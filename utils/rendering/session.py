import json
import os

from vat.trials.trial_models import Trial


class SessionSpecification(object):
    def __init__(
            self,
            trial_sequence: [Trial],
    ):
        for t in trial_sequence:
            assert isinstance(t, Trial)

        self.trial_sequence = trial_sequence

    def render_html(self, filename) -> str:

        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')

        with open(template_path, 'r') as file:
            html_template = file.read()

        data_sequence = [t.data for t in self.trial_sequence]

        json_data = json.dumps(data_sequence)

        html_string = html_template.replace('\'__INJECT TRIAL INFORMATION HERE__\'', json_data)
        html_string = html_string.replace('__INJECT_CONDITION_HERE__', filename)

        return html_string
