import json
import urllib.parse
import collections
import xarray as xr
from typing import List, Dict
import os
import datetime
import numpy as np


def parse_data(json_path: str) -> xr.Dataset:
    assert isinstance(json_path, str), 'json_path must be a string!'
    assert os.path.exists(json_path), f'json_path {json_path} does not exist!'

    # Load assignment json
    with open(json_path, 'r') as f:
        assignment_json = json.load(f)

    answer_text = assignment_json['Answer']

    # Get metadata
    session_start_time = extract_freetext_answer(
        answer_text=answer_text,
        question_identifier='session_start_time'
    )

    task_url = extract_freetext_answer(
        answer_text=answer_text,
        question_identifier='task_url'
    )

    experimental_condition = extract_freetext_answer(
        answer_text=answer_text,
        question_identifier='experimental_condition'
    )

    # Extract answer string
    trial_answer_text_decoded = extract_freetext_answer(
        answer_text=answer_text,
        question_identifier='trial_datastring'
    )

    trial_sequence = json.loads(json.loads(trial_answer_text_decoded))  # Not sure why this is double-encoded, but it is what it is.

    ds_data = parse_nway_classification_trials(trial_sequence=trial_sequence)

    ds_data = ds_data.assign_coords(
        worker_id=assignment_json['WorkerId'],
        assignment_id=assignment_json['AssignmentId'],
        hit_id=assignment_json['HITId'],
        submit_time=assignment_json['SubmitTime'],
        task_url=task_url,
        session_start_time=session_start_time,
        experimental_condition=experimental_condition
    )

    # Assign time coord

    datetime_session_start = iso_timestamp_string_to_datetime(iso_timestamp_string=session_start_time)
    time_deltas = [datetime.timedelta(milliseconds=int(v)) for v in ds_data['time_elapsed'].values]

    print(datetime_session_start)
    ds_data = ds_data.assign_coords(
        timestamp=(['trial'], [datetime_session_start + v for v in time_deltas]),
        timestamp_session_start=datetime_session_start,
    )
    ds_data = ds_data.rename(
        {'time_elapsed': 'time_elapsed_msec'}
    )
    return ds_data


def iso_timestamp_string_to_datetime(iso_timestamp_string: str) -> datetime.datetime:
    """

    :param iso_timestamp_string: Example: '2024-01-31T23:36:06.398Z'
    :return:
    """
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    parsed_datetime = datetime.datetime.strptime(iso_timestamp_string, date_format)
    return parsed_datetime


def extract_freetext_answer(answer_text: str, question_identifier: str) -> str:
    assert isinstance(answer_text, str)
    assert isinstance(question_identifier, str)

    search_tag = f'<QuestionIdentifier>{question_identifier}</QuestionIdentifier>'
    assert search_tag in answer_text, f'Question identifier {question_identifier} not found in answer text!'
    answer_text = answer_text.split(search_tag + '<FreeText>')[1].split('</FreeText>')[0]
    answer_text_decoded = urllib.parse.unquote(answer_text)  # Added after encodeURIComponent was added to jspsych
    return answer_text_decoded


def parse_nway_classification_trials(trial_sequence: list) -> xr.Dataset:
    datavars_nway_classification = collections.defaultdict(lambda: (['trial'], []))
    coords_nway_classification = collections.defaultdict(lambda: (['trial'], []))
    datavars_nway_classification['choice_image_urls'] = (['trial', 'choice'], [])
    # datavars_nway_classification['choice_image_urls'] = (lambda: (['trial', 'choice'], []))

    for trial in trial_sequence:
        if trial['trial_type'] == 'nway_classification':
            """
                        Example trial data:
                        {
                            'rt': 971,
                            'trial_type': 'nway_classification',
                            'trial_index': 6,
                            'time_elapsed': 8783,
                            'internal_node_id': '0.0-4.0-2.0',
                            'stimulus_image_url': '',
                            'stimulus_string': 'Select the face that looks the most neutral:',
                            'choice_image_urls': ['https://visualaffect.s3.amazonaws.com/emotional_probe_images/c-4.png', 'https://visualaffect.s3.amazonaws.com/emotional_probe_images/c-3.png',
                                                  'https://visualaffect.s3.amazonaws.com/emotional_probe_images/c-2.png', 'https://visualaffect.s3.amazonaws.com/emotional_probe_images/c-1.png',
                                                  'https://visualaffect.s3.amazonaws.com/emotional_probe_images/c0.png', 'https://visualaffect.s3.amazonaws.com/emotional_probe_images/c1.png',
                                                  'https://visualaffect.s3.amazonaws.com/emotional_probe_images/c2.png', 'https://visualaffect.s3.amazonaws.com/emotional_probe_images/c3.png',
                                                  'https://visualaffect.s3.amazonaws.com/emotional_probe_images/c4.png'],
                            'trial_tag': 'attention_trial',
                            'i_choice': 4,
                            'i_correct_choice': None,
                            'deliver_reinforcement': False,
                            'background': True,
                            'pre_choice_stimulus_duration': 500,
                            'keep_stimulus_image_on': True
                        }
            """
            datavar_names = {
                'rt',
                'i_choice',
                'stimulus_image_url',
                'stimulus_string',
                'choice_image_urls',
                'i_correct_choice',
                'deliver_reinforcement',
            }
            coord_names = {
                'trial_tag',
                'background',
                'pre_choice_stimulus_duration',
                'keep_stimulus_image_on',
                'time_elapsed',
            }

            for k in trial:  # Add all fields to the dataset
                if k in datavar_names:
                    datavars_nway_classification[k][1].append(trial[k])
                if k in coord_names:
                    coords_nway_classification[k][1].append(trial[k])
        else:
            continue

    # choice_image_urls_data = np.array(datavars_nway_classification['choice_image_urls'][1], dtype=object)
    #
    # # Update the dictionary to use this array of objects instead of the original nested lists
    # datavars_nway_classification['choice_image_urls'] = (
    #     datavars_nway_classification['choice_image_urls'][0], choice_image_urls_data
    # )

    for i in range(len(datavars_nway_classification['choice_image_urls'][1])):
        temp = datavars_nway_classification['choice_image_urls'][1][i]
        if len(temp) < 9:
            datavars_nway_classification['choice_image_urls'][1][i] = ['']*9


    print(datavars_nway_classification)
    ds_nway_classification = xr.Dataset(
        data_vars=datavars_nway_classification,
        coords=coords_nway_classification
    )
    ds_nway_classification = ds_nway_classification.assign_coords(
        trial=range(len(ds_nway_classification.trial)),
        choice=range(len(ds_nway_classification.choice)),
    )
    ds_nway_classification = ds_nway_classification.rename({'rt': 'reaction_time_msec'})

    return ds_nway_classification

