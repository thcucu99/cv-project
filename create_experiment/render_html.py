from vat.rendering.session import SessionSpecification
from vat.trials.trial_models import *
import os

if __name__ == '__main__':

    trials = [
        HTMLContent(
            purpose='consent',
        ),
        # HTMLContent(
        #     purpose='instructions',
        # ),
        # HTMLContent(
        #     purpose='intro',
        # )
        # ,
        ImageClassification(
            image_url='https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
            choices_strings=['Box', 'Baby'],
            i_correct_response=0,
        ),
        ImageValenceClassification(
            image_url='https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
            choices_order='happy_to_sad',
        ),
        ImageValenceClassification(
            image_url='https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
            choices_order='sad_to_happy',
        ),
        ImageClassification(
            image_url='https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
            choices_strings=['Box', 'Baby'],
            i_correct_response=0,
            keep_stimulus_image_on=False
        ),
        ValenceProbe(
            prompt='Select the image that looks the happiest:',
            choices_order='sad_to_happy'
        ),
        HTMLContent(
            purpose='outro'
        ),
        # EmotionalProbe(
        #     choices_order='sad_to_happy',
        # ),
        # EmotionalProbe(
        #     choices_order='happy_to_sad',
        # ),
        # EmotionalProbe(
        #     prompt='Select an image at random:',
        #     choices_order='sad_to_happy',
        # ),
    ]

    session = SessionSpecification(trial_sequence=trials)
    html_string = session.render_html(filename='dev')
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example_rendering.html')
    with open(example_path, 'w') as f:
        f.write(html_string)

