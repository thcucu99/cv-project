from utils.rendering.session import SessionSpecification
from utils.trials.trial_models import *
import os

if __name__ == '__main__':

    trials = [
        HTMLContent(
            purpose='consent',
        ),
        # ImabeBlock(
        #     image_url='https://visualaffect.s3.amazonaws.com/stimuli/2023-11-18/0e81182de129299953a09c3e9b628410ef75bd72513f851b48960600b23de5b9.jpg'
        # ),
        ImabeBlock(
            # image_url='https://raw.githubusercontent.com/thcucu99/cv-project/main/images/all_images/image_95/image_95_1234.png'
            image_url='https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_95.png',

        ),
        ImabeBlock(
            image_url='https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_95.png',
            unlock_order=[4,3,2,1]
        ),
        ImabeBlock(
            image_url='https://raw.githubusercontent.com/thcucu99/cv-project/main/images/original/image_95.png',
            unlock_order=[3, 4, 1, 2]
        ),
        # ImageClassification(
        #     image_url='https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
        #     choices_strings=['Box', 'Baby'],
        #     i_correct_response=0,
        # ),
        # ImageValenceClassification(
        #     image_url='https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
        #     choices_order='happy_to_sad',
        # ),
        # ImageValenceClassification(
        #     image_url='https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
        #     choices_order='sad_to_happy',
        # ),
        # ImageClassification(
        #     image_url='https://visualaffect.s3.amazonaws.com/images/050a87f791653513834d10e38bde2dcf7f17ce9098cdc49d65fa9101a3006d19.png',
        #     choices_strings=['Box', 'Baby'],
        #     i_correct_response=0,
        #     keep_stimulus_image_on=False
        # ),
        # ValenceProbe(
        #     prompt='Select the image that looks the happiest:',
        #     choices_order='sad_to_happy'
        # ),
        # HTMLContent(
        #     purpose='outro'
        # ),

    ]

    session = SessionSpecification(trial_sequence=trials)
    html_string = session.render_html(filename='dev')
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example_rendering.html')
    with open(example_path, 'w') as f:
        f.write(html_string)
    print(example_path)

