class Trial(object):
    def __init__(self):
        pass

    @property
    def data(self):
        return None


class SwedishBivalentAdjectiveEmotionalProbe(Trial):
    def __init__(self, option_left: str, option_right: str):
        super().__init__()
        assert isinstance(option_left, str)
        assert isinstance(option_right, str)

        self.option_left = option_left
        self.option_right = option_right

    @property
    def data(self):
        """
        {"trial_type": "emotion_probe", "opt1": "pessimistic", "opt2": "optimistic"},
        :return:
        """

        data = {
            'trial_type': 'emotion_probe',
            'opt1': self.option_left,
            'opt2': self.option_right,
        }
        return data


class EarlyExit(Trial):
    def __init__(self):
        super().__init__()

    @property
    def data(self):
        """
        {"trial_type": "early_exit"},
        :return:
        """

        data = {
            'trial_type': 'early_exit'
        }
        return data


class HTMLContent(Trial):
    def __init__(self, purpose: str, task='image_classification'):
        super().__init__()
        assert purpose in ('intro', 'outro', 'consent', 'instructions')
        self.message = ''
        self.choices = ['Continue']

        if purpose == 'intro':
            self.message = 'We will begin with a warm-up. Select CONTINUE to start the warm-up.'
        if purpose == 'outro':
            self.message = 'The warm-up is over. Select CONTINUE to start the experiment.'
        if purpose == 'consent':
            self.message = (
                """
            <div style="text-align:left; background-color:white; margin:1% auto; padding:2%; border-radius:8px; border-color:black; border-width:2px; max-width: 80%">\n
            <h1 style="text-align:center">Welcome!</h1>    \n
            This is a scientific study being conducted by researchers at MIT to help understand the visual system. It will involve viewing images and making responses. \n
            <ul>\n
            <li>There are neither risks nor benefits associated with performing this study.</li>\n
            <li><b><text style="color:red;">Some of the images might contain nudity, violence, or graphic content.</text></b></li>\n
            <li>If you feel uncomfortable at any point during the study, you may leave at any time with no penalty.</li>\n
            <li>You will remain anonymous. We may ask for nonidentifying demographic information, such as your gender identity and approximate age, to help us understand how our results relate to the population at large.</li>\n
            <li>The information you provide will only be available to MIT and collaborating research institutions. Your data will be retained throughout the lifecycle of the research project and secured through personnel authorized by MIT information services. </li>\n
            \n
            </ul>\n
            \n
            Clicking on the <b>\'Accept\'</b> button below indicates that you are at least 18 years of age, and that you agree to complete this study voluntarily.\n
            </div>
             """)
            self.choices = ['Accept', 'Reject']
        if purpose == 'instructions':
            if task == 'image_classification':
                self.message = ("""
                <div style="text-align:left; background-color:white; margin:1% auto; padding:2%; border-radius:8px; border-color:black; border-width:2px; max-width:80%;">\n
                <h1 style="text-align:center">Instructions</h1>    \n
                Pictures communicate. They depict people, objects, and scenes. In this study, we are interested in how people perceive various pictures. \n
                <b>We will be asking you questions about positive feelings and negative feelings. </b> Positive feelings include feeling happy, satisfied, competent, proud, contented, delighted, and so on. \n
                Negative feelings include feeling unhappy, upset, irritated, angry, sad, depressed, and so on. \n
                <b><text style="color:red;">Again, some of the images might contain nudity, violence, or graphic content.
                """)
            if task == 'image_valence_a':
                self.message = ("""
                <div style="text-align:left; background-color:white; margin:1% auto; padding:2%; border-radius:8px; border-color:black; border-width:2px; max-width:80%;">\n
                <h1 style="text-align:center">Instructions</h1>    \n
                Pictures communicate. They depict people, objects, and scenes. In this study, we are interested in how various pictures make people feel. \n
                As you answer, please remember:
                There are no right or wrong answers. We are interested in your individual opinion. Please do not take too long over any picture. Your first
                response is as good as any. \n </div>
                """)
            if task == 'image_valence_b':
                self.message = ("""
                <div style="text-align:left; background-color:white; margin:1% auto; padding:2%; border-radius:8px; border-color:black; border-width:2px; max-width:80%;">\n
                <h1 style="text-align:center">Instructions</h1>    \n
                   For example, positive feelings include feeling happy, satisfied, competent, proud, contented, delighted, and so on. \n 
                   Negative feelings include feeling unhappy, upset, irritated, angry, sad, depressed, and so on. \n
                   <b><text style="color:red;">Again, some of the images might contain nudity, violence, or graphic content. </text></b> </div>
                   """)

    @property
    def data(self):

        """
        {"trial_type": "practice"},
        :return:
        """

        data = {
            'trial_type': 'message',
            'html_content': self.message,
            'choices': self.choices
        }
        return data

#TODO: add keep_stimulus_image_on
#


class ImageClassification(Trial):
    def __init__(
            self,
            image_url: str,
            choices_strings: list,
            i_correct_response: int,
            image_height_css='18em',
            pre_choice_stimulus_duration=0,
            keep_stimulus_image_on=True,
            pre_choice_stimulus_string_duration=500,
            during_choice_stimulus_string: bool = True,
            catch_trial: bool = False,
            trial_tag: str = 'image_classification',
            cover_task: bool = False,
    ):
        super().__init__()
        assert isinstance(image_url, str)
        assert isinstance(image_height_css, str)
        assert isinstance(choices_strings, list)
        assert isinstance(pre_choice_stimulus_duration, int)
        assert i_correct_response in {0, 1}

        self.image_url = image_url
        self.choices_strings = choices_strings
        self.i_correct_response = i_correct_response
        self.image_height_css = image_height_css
        self.pre_choice_stimulus_duration = pre_choice_stimulus_duration
        self.keep_stimulus_image_on = keep_stimulus_image_on
        self.pre_choice_stimulus_string_duration = pre_choice_stimulus_string_duration
        self.during_choice_stimulus_string = during_choice_stimulus_string
        self.catch_trial = catch_trial


    @property
    def data(self):

        """
            {
            'stimulus_image_url': 'https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
            'stimulus_image_height': '20em',
            'stimulus_string': '',
            'choice_strings': ['Box', 'Baby'],
            'choice_image_urls': [],
            'i_correct_choice': 0,
            'trial_type': 'nway_classification',
            'trial_tag': 'image_classification',
            'deliver_reinforcement': true,
            },
        """
        data = {
            'stimulus_image_url': self.image_url,
            'stimulus_image_height': self.image_height_css,
            'stimulus_string': 'Select the option that describes what the image is.',
            'choice_strings': self.choices_strings,
            'choice_image_urls': [],
            'i_correct_choice': self.i_correct_response,
            'trial_type': 'nway_classification',
            'trial_tag': 'image_classification',
            'deliver_reinforcement': False,
            'background': False,
            'pre_choice_stimulus_duration': self.pre_choice_stimulus_duration,
            'keep_stimulus_image_on': self.keep_stimulus_image_on,
            'pre_choice_stimulus_string_duration': self.pre_choice_stimulus_string_duration,
            'during_choice_stimulus_string': self.during_choice_stimulus_string,
            'catch_trial': self.catch_trial,
            'cover_task': False,
            }
        return data


class EmotionalProbe(Trial):
    def __init__(
            self,
            prompt: str,
            urls: list,
            tag: str,
            pre_choice_stimulus_duration=500,
    ):
        super().__init__()
        assert isinstance(prompt, str)
        assert isinstance(urls, list)
        assert isinstance(tag, str)
        assert isinstance(pre_choice_stimulus_duration, int)
        self.stimulus_str = prompt
        self.choice_images_urls = urls
        self.trial_tag = tag
        self.pre_choice_stimulus_duration = pre_choice_stimulus_duration

    @property
    def data(self):

        """
            'stimulus_image_url': '',
            'stimulus_image_height': '',
            'stimulus_string': 'Choose the image that best reflects how you currently feel',
            'choice_image_urls': [
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/-4.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/-3.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/-2.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/-1.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/0.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/1.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/2.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/3.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/4.png',
                ],
            'i_correct_choice': null,
            'deliver_reinforcement': false,
            'trial_type': 'nway_classification',
            'trial_tag': 'emotional_probe',
        """
        data = {
            'stimulus_image_url': '',
            'stimulus_image_height': '',
            'stimulus_string': self.stimulus_str,
            'choice_image_urls': self.choice_images_urls,
            'i_correct_choice': None,
            'deliver_reinforcement': False,
            'trial_type': 'nway_classification',
            'trial_tag': self.trial_tag,
            'background': True,
            'pre_choice_stimulus_duration': self.pre_choice_stimulus_duration,
            'keep_stimulus_image_on': True
            }
        return data


class ValenceProbe(EmotionalProbe):
    def __init__(
            self,
            choices_order: str,
            prompt='',
            color=True,
    ):
        assert choices_order in ['sad_to_happy', 'happy_to_sad']

        if prompt:
            self.stimulus_str = prompt
            self.trial_tag = 'attention_trial'
        else:
            self.stimulus_str = 'Select the image that best matches your current emotional state:'
            self.trial_tag = 'emotional_probe'

        if color:
            temp = 'https://visualaffect.s3.amazonaws.com/emotional_probe_images/cREPLACE.png'
        else:
            temp = 'https://visualaffect.s3.amazonaws.com/emotional_probe_images/REPLACE.png'
        if choices_order == 'sad_to_happy':
            self.choices_idx = range(-4, 5)
        else:
            self.choices_idx = range(4, -5, -1)
        self.choice_images_urls = [temp.replace('REPLACE', str(i)) for i in self.choices_idx]
        super().__init__(prompt=self.stimulus_str, urls=self.choice_images_urls, tag=self.trial_tag)


##TODO: implement tuple for stimulus_string_behavior: (how many milliseconds before stimulus is displayed, boolean for whether it's on during and/or after)
class ImageEmotionalClassification(Trial):
    def __init__(
            self,
            image_url: str,
            choices_urls: list,
            stimulus_string: str,
            trial_tag: str,
            image_height_css='18em',
            background=True,
            pre_choice_stimulus_duration=500,
            keep_stimulus_image_on=True,
            pre_choice_stimulus_string_duration=500,
            during_choice_stimulus_string: bool = True,
            catch_trial: bool = False,
            cover_task: bool = False,
    ):
        super().__init__()
        assert isinstance(image_url, str)
        assert isinstance(image_height_css, str)
        assert isinstance(choices_urls, list)
        assert isinstance(stimulus_string, str)
        assert isinstance(trial_tag, str)
        assert isinstance(background, bool)
        assert isinstance(pre_choice_stimulus_duration, int)
        assert isinstance(keep_stimulus_image_on, bool)

        self.image_url = image_url
        self.image_height_css = image_height_css

        self.stimulus_str = stimulus_string
        self.trial_tag = trial_tag

        self.choice_images_urls = choices_urls

        self.background = background
        self.pre_choice_stimulus_duration = pre_choice_stimulus_duration
        self.keep_stimulus_image_on = keep_stimulus_image_on
        self.pre_choice_stimulus_string_duration = pre_choice_stimulus_string_duration
        self.during_choice_stimulus_string = during_choice_stimulus_string
        self.catch_trial = catch_trial
        self.cover_task = cover_task

    @property
    def data(self):

        """
            'stimulus_image_url': 'https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
            'stimulus_image_height': '20em',
            'stimulus_string': 'Choose the image that best reflects how you currently feel',
            'choice_image_urls': [
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/-4.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/-3.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/-2.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/-1.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/0.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/1.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/2.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/3.png',
                'https://visualaffect.s3.amazonaws.com/emotional_probe_images/4.png',
                ],
            'i_correct_choice': null,
            'deliver_reinforcement': false,
            'trial_type': 'nway_classification',
            'trial_tag': 'emotional_probe',
        """
        data = {
            'stimulus_image_url': self.image_url,
            'stimulus_image_height': self.image_height_css,
            'stimulus_string': self.stimulus_str,
            'choice_image_urls': self.choice_images_urls,
            'i_correct_choice': None,
            'deliver_reinforcement': False,
            'trial_type': 'nway_classification',
            'trial_tag': self.trial_tag,
            'background': self.background,
            'pre_choice_stimulus_duration': self.pre_choice_stimulus_duration,
            'keep_stimulus_image_on': self.keep_stimulus_image_on,
            'pre_choice_stimulus_string_duration': self.pre_choice_stimulus_string_duration,
            'during_choice_stimulus_string': self.during_choice_stimulus_string,
            'catch_trial': self.catch_trial,
            'cover_task': self.cover_task,
            }
        return data


class ImageValenceClassification(ImageEmotionalClassification):
    def __init__(
            self,
            image_url: str,
            choices_order: str,
            stimulus_string: str = 'Select the face that best matches how this image makes you feel:',
            image_height_css='18em',
            color=True,
            background=True,
            keep_stimulus_image_on=True,
            pre_choice_stimulus_duration=500,
            pre_choice_stimulus_string_duration=500,
            during_choice_stimulus_string: bool = True,
            trial_tag: str = 'valence_image_classification',
            catch_trial: bool = False,
            cover_task: bool = False,
    ):
        assert choices_order in ['sad_to_happy', 'happy_to_sad']
        self.trial_tag = trial_tag
        self.prompt = stimulus_string
        if color:
            temp = 'https://visualaffect.s3.amazonaws.com/emotional_probe_images/cREPLACE.png'
        else:
            temp = 'https://visualaffect.s3.amazonaws.com/emotional_probe_images/REPLACE.png'
        if choices_order == 'sad_to_happy':
            self.choices_idx = range(-4, 5)
        else:
            self.choices_idx = range(4, -5, -1)
        self.choice_images_urls = [temp.replace('REPLACE', str(i)) for i in self.choices_idx]

        super().__init__(
            image_url=image_url,
            image_height_css=image_height_css,
            choices_urls=self.choice_images_urls,
            stimulus_string=self.prompt,
            trial_tag=self.trial_tag,
            background=background,
            keep_stimulus_image_on=keep_stimulus_image_on,
            pre_choice_stimulus_duration=pre_choice_stimulus_duration,
            pre_choice_stimulus_string_duration=pre_choice_stimulus_string_duration,
            during_choice_stimulus_string=during_choice_stimulus_string,
            catch_trial=catch_trial,
            cover_task=cover_task
        )


if __name__ == '__main__':

    trial = ImageClassification(
        image_url='https://visualaffect.s3.amazonaws.com/emotional_probe_images/0.png',
        choices_strings=['Box', 'Baby'],
        i_correct_response=0,
        image_height_css='18em',
        pre_choice_stimulus_duration_msec=500,
        keep_stimulus_image_on=True
    )