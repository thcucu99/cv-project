function get_jspsych_trial(trial_json_spec) {
    /*
    Create a jsPsych trial from trial_json_spec.
    */

    const trial_type = trial_json_spec['trial_type'];
    console.log(trial_type);
    let trial = null;
    if (trial_type === 'nway_classification') {
        trial = create_classification_trial(
            trial_json_spec['stimulus_image_url'],
            trial_json_spec['stimulus_image_height'],
            trial_json_spec['stimulus_string'],
            trial_json_spec['choice_strings'],
            trial_json_spec['choice_image_urls'],
            trial_json_spec['i_correct_choice'],
            trial_json_spec['deliver_reinforcement'],
            trial_json_spec['trial_tag'],
            trial_json_spec['background'],
            trial_json_spec['pre_choice_stimulus_duration'],
            trial_json_spec['keep_stimulus_image_on'],
            trial_json_spec['pre_choice_stimulus_string_duration'],
            trial_json_spec['during_choice_stimulus_string'],
            trial_json_spec['catch_trial'],
            trial_json_spec['cover_task'],
        )
    }
    if (trial_type === 'message') {
        trial = create_message_trial(trial_json_spec['html_content'], trial_json_spec['choices'])
    }
    return trial
}


function create_message_trial(html_content, choices) {
    const message_html = {
        type: jsPsychHtmlButtonResponse,
        stimulus: html_content,
        choices: choices,
    }
    return message_html
}


function create_fixation_trial() {
    let jspsych_trial = {
        // The fixation phase.
        type: jsPsychHtmlButtonResponse,
        button_html: `<button class="fixation-button-element">%choice%</button>`,
        stimulus: ``,
        choices: ['+'],
        on_finish: function (data) {
            delete data['response'];
            delete data['stimulus'];
            data['trial_type'] = 'fixation';
            data['trial_tag'] = 'fixation';
        }
    }
    return jspsych_trial
}


function create_classification_trial(
    stimulus_image_url,
    stimulus_image_height, // As CSS string, e.g. '20em' or "256px"
    stimulus_string,
    choice_strings,
    choice_image_urls,
    i_correct_choice,
    deliver_reinforcement,
    trial_tag,
    background,
    pre_choice_stimulus_duration,
    keep_stimulus_image_on,
    pre_choice_stimulus_string_duration,
    during_choice_stimulus_string,
    catch_trial,
    cover_task,
) {


    let if_correct_node = {
        timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            stimulus: "Correct",
            css_classes: ['correct', 'cursor_off'],
            trial_duration: 200
        }],
        conditional_function: function () {
            if (!deliver_reinforcement) {
                return false
            }

            const data = jsPsych.data.get().last(1).values()[0];
            let deliver_positive_reinforcement = false;

            if (data['i_choice'] === data['i_correct_choice']) {
                deliver_positive_reinforcement = true;
            }

            return deliver_positive_reinforcement;
        }
    }


    let if_incorrect_node = {
        timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            stimulus: "Incorrect",
            css_classes: ['incorrect', 'cursor_off'],
            trial_duration: 1000
        }],
        conditional_function: function () {
            if (!deliver_reinforcement) {
                return false
            }

            const data = jsPsych.data.get().last(1).values()[0];
            let deliver_negative_reinforcement = false;

            if (data['i_choice'] !== data['i_correct_choice']) {
                deliver_negative_reinforcement = true;
            }

            return deliver_negative_reinforcement;
        }
    }

    function  show_stimulus(keep_stimulus_image_on, during_choice_stimulus_string){
        let stimulus_string_during_choice = stimulus_string;
        if (during_choice_stimulus_string === false) {stimulus_string_during_choice = ''};
        if (keep_stimulus_image_on === true){
            return assemble_stimulus_html(stimulus_image_url, stimulus_image_height, stimulus_string_during_choice)
        } else {
            // return ''
            return assemble_stimulus_html(stimulus_image_url, '0em', stimulus_string_during_choice)
        }
    }

    function assemble_stimulus_html(stimulus_image_url, stimulus_image_height, query_string) {
        let html_string = '';

        // Add query string
        if (query_string && query_string.length > 0) {
            html_string += `<div class="stimulus-string-element">
                $query_string$
            </div>`
        }
        // Add stimulus image
        if (stimulus_image_url && stimulus_image_url.length > 0) {
            EXTERNAL_IMAGE_REFERENCES.push(stimulus_image_url);
            html_string += `
            <div id='stimulus_image' class="stimulus-image-element" style="height: $stimulus_image_height$;">
                <img  src="$stimulus_image_url$" style="height:100%; width:auto; max-width:none; ">
            </div>
            `
        }

        html_string = html_string.replace('$query_string$', query_string)
        html_string = html_string.replace('$stimulus_image_url$', stimulus_image_url)
        html_string = html_string.replace('$stimulus_image_height$', stimulus_image_height)
        return html_string
    }

    function assemble_nway_trial_html() {
        // Wrap the stimulus elements
        let stimulus_element = document.getElementById("jspsych-html-button-response-stimulus")
        stimulus_element.className = 'stimulus-wrapper';

        // If there is an image element, dynamically shift the stimulus wrapper so its y midpoint is the midpoint of the image; continue to maintain the horizontal centering of the stimulus wrapper
        let stimulus_image_element = document.getElementById("stimulus_image");
        if (stimulus_image_element) {
            let y_offset = stimulus_image_element.offsetHeight / 2;
            stimulus_element.style['transform'] = `translate(-50%, ${y_offset}px)`;
        }

        // Assign the custom choices-wrapper div class
        let button_group_element = document.getElementById("jspsych-html-button-response-btngroup")
        button_group_element.className = 'choices-wrapper';
        if (background){
            button_group_element.style['background-color'] = 'darkgray';
        }
        // Dynamically shift the choices wrapper so it does not overlap with the stimulus wrapper, if it was dynamically moved.
        if (stimulus_image_element) {
            let y_offset = stimulus_image_element.offsetHeight / 2;
            // Dynamically translate the button wrapper by y_offset downward
            button_group_element.style['transform'] = `translate(-50%, ${y_offset}px)`;
        }

        // Assign the custom button div classes
        let button_widths = [];
        for (let i_button = 0; i_button < choice_strings.length; i_button++) {
            let button_element = button_group_element.children[i_button];
            button_element.style = '';
            button_element.className = 'choice-element-wrapper';
            button_widths.push(button_element.offsetWidth);
        }
    }

    function assemble_choices_html(choice_strings, choice_image_urls){

        // Set default value of choice_strings and choiec_image_urls to [] if they are not defined
        choice_strings = choice_strings || [];
        choice_image_urls = choice_image_urls || [];

        //
        const nchoices = Math.max(choice_strings.length, choice_image_urls.length);
        let choice_html_strings = []
        for (let i_choice = 0; i_choice < nchoices; i_choice++) {

            const choice_string_cur = choice_strings[i_choice] || '';
            const choice_image_url_cur = choice_image_urls[i_choice] || '';

            let html_string = '';
            // If there is an image url, add it first
            if(choice_image_url_cur.length > 0){
                EXTERNAL_IMAGE_REFERENCES.push(choice_image_url_cur);
                let image_element_string = `
                    <img class="choice-image" src="$choice_image_url$" >
                `
                image_element_string = image_element_string.replace('$choice_image_url$', choice_image_url_cur)
                html_string += image_element_string;
            }

            // If there is a choice string, add it second
            if(choice_string_cur.length > 0){
                let choice_string_html = `
                    <div class="choice-string">
                        $choice_string$
                    </div>
                `
                choice_string_html = choice_string_html.replace('$choice_string$', choice_string_cur)
                html_string += choice_string_html
            }


            choice_html_strings.push(html_string);
        }

        return choice_html_strings
    }
    let pre_choice_stimulus_string = stimulus_string;
    if (pre_choice_stimulus_string_duration === 0) {pre_choice_stimulus_string = ''};

    let timeline = [];
        // The fixation trial

    if (!cover_task) {
        timeline.push(create_fixation_trial())
    }
    if (!catch_trial && !cover_task) {
        console.log('HERE', trial_tag, catch_trial, cover_task);
        // Add this part to the timeline only if catch_trial is not true
        timeline.push({
            // Just the image
            type: jsPsychHtmlButtonResponse,
            stimulus: assemble_stimulus_html(stimulus_image_url, stimulus_image_height, pre_choice_stimulus_string),
            choices: [],
            trial_duration: pre_choice_stimulus_duration,
            button_html: '%choice%',
            on_load: assemble_nway_trial_html
        });
    }
    if (cover_task){ // Add a 100ms delay if cover task
        timeline.push(
            {
              type: jsPsychHtmlButtonResponse,
              stimulus: '',
              choices: [],
              prompt: "",
              trial_duration: 100,
            }
        );
    }

    // Add remaining parts of the timeline
    timeline.push({
            // The images and choices phase.
            type: jsPsychHtmlButtonResponse,
                stimulus: show_stimulus(keep_stimulus_image_on, during_choice_stimulus_string),
                choices: assemble_choices_html(choice_strings, choice_image_urls),
                button_html: '%choice%',
                on_load: assemble_nway_trial_html,
                on_finish: function (data) {

                    data['trial_type'] = 'nway_classification';
                    data['stimulus_image_url'] = stimulus_image_url;
                    data['stimulus_string'] = stimulus_string;
                    data['choice_strings'] = choice_strings;
                    data['choice_image_urls'] = choice_image_urls;
                    data['trial_tag'] = trial_tag;
                    data['i_choice'] = data['response'];
                    data['i_correct_choice'] = i_correct_choice;
                    data['deliver_reinforcement'] = deliver_reinforcement;
                    data['background'] = background;
                    data['pre_choice_stimulus_duration'] = pre_choice_stimulus_duration;
                    data['keep_stimulus_image_on'] = keep_stimulus_image_on;
                    data['pre_choice_stimulus_string_duration'] = pre_choice_stimulus_string_duration;
                    data['during_choice_stimulus_string'] = during_choice_stimulus_string;

                    delete data['response'];
                    delete data['stimulus'];
                }
        },
        if_correct_node, if_incorrect_node,
    );

    return {
        'timeline': timeline
    }

    // return {
    //     'timeline': [
    //         //The fixation trial
    //         create_fixation_trial(),
    //         {
    //             // Just the image
    //             type: jsPsychHtmlButtonResponse,
    //             stimulus: assemble_stimulus_html(stimulus_image_url, stimulus_image_height, pre_choice_stimulus_string),
    //             choices: [],
    //             trial_duration: pre_choice_stimulus_duration,
    //             button_html: '%choice%',
    //             on_load: assemble_nway_trial_html
    //         },
    //         {
    //             // The images and choices phase.
    //             type: jsPsychHtmlButtonResponse,
    //             stimulus: show_stimulus(keep_stimulus_image_on, during_choice_stimulus_string),
    //             choices: assemble_choices_html(choice_strings, choice_image_urls),
    //             button_html: '%choice%',
    //             on_load: assemble_nway_trial_html,
    //             on_finish: function (data) {
    //
    //                 data['trial_type'] = 'nway_classification';
    //                 data['stimulus_image_url'] = stimulus_image_url;
    //                 data['stimulus_string'] = stimulus_string;
    //                 data['choice_strings'] = choice_strings;
    //                 data['choice_image_urls'] = choice_image_urls;
    //                 data['trial_tag'] = trial_tag;
    //                 data['i_choice'] = data['response'];
    //                 data['i_correct_choice'] = i_correct_choice;
    //                 data['deliver_reinforcement'] = deliver_reinforcement;
    //                 data['background'] = background;
    //                 data['pre_choice_stimulus_duration'] = pre_choice_stimulus_duration;
    //                 data['keep_stimulus_image_on'] = keep_stimulus_image_on;
    //                 data['pre_choice_stimulus_string_duration'] = pre_choice_stimulus_string_duration;
    //                 data['during_choice_stimulus_string'] = during_choice_stimulus_string;
    //
    //                 delete data['response'];
    //                 delete data['stimulus'];
    //             }
    //         },
    //         if_correct_node, if_incorrect_node,
    //     ]
    // }
}