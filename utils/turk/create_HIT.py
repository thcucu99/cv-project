import numpy as np
from typing import Union, List
from vat.utils.turk import connection


def external_question_template(url, frame_height):
    s = f'<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">' \
        f'<ExternalURL>{url}</ExternalURL>' \
        f'<FrameHeight>{frame_height}</FrameHeight></ExternalQuestion>'
    return s


def publish_external_questions(
        url_list: list,
        HIT_group_title: str,
        HIT_group_description: str,
        Keywords: str,
        num_assignments_per_hit: Union[int, List[int]],
        sandbox: bool,
        duration_sec: int,
        completion_reward_usd: float,
        auto_approval_days=0,
        qualification_requirements: list = None,
        force_publish=False
) -> [str]:
    # Check inputs
    assert isinstance(url_list, list)
    assert isinstance(HIT_group_title, str)
    assert isinstance(HIT_group_description, str)
    assert isinstance(Keywords, str)
    assert isinstance(num_assignments_per_hit, (int, list))
    assert isinstance(duration_sec, int)
    assert isinstance(completion_reward_usd, (int, float))
    assert isinstance(sandbox, bool)

    if isinstance(num_assignments_per_hit, int):
        num_assignments_per_hit = [num_assignments_per_hit for _ in range(len(url_list))]

    assert np.all(np.array(num_assignments_per_hit) > 0), 'Gave an invalid number of HITs; must be positive %s' % (
        str(num_assignments_per_hit))

    safety_value = 5
    if completion_reward_usd >= safety_value:
        confirm = input('Specified a reward of $%0.2f per HIT. Type "i am sure" to continue:' % completion_reward_usd)
        if confirm == 'i am sure':
            pass
        else:
            raise Exception('Aborting publish')

    client = connection.get_client(sandbox=sandbox)

    # Estimate approval cost
    total_num_assignments = np.sum(num_assignments_per_hit)
    total_approval_cost = completion_reward_usd * total_num_assignments
    print('Total # assignments = %d' % (total_num_assignments))
    print('Approval cost (not including bonuses) = $%0.2f' % (total_approval_cost))

    # Check remaining balance
    if sandbox:
        print('Publishing HITs to sandbox.')
    else:
        print('\nBalance remaining: $', client.get_account_balance()['AvailableBalance'], '\n')
        if not force_publish:
            confirm = input('Publishing HITs to real workers. Continue? (y/n)')
            if confirm == 'y':
                pass
            else:
                raise RuntimeError('Aborting publish')

    # Reasonable defaults
    HIT_FRAME_HEIGHT = 0  # 768 "If you set the value to 0, your HIT will automatically resize to fit within the Worker's browser window."
    LifetimeInSeconds = 1209600

    if qualification_requirements is None:
        qualification_requirements = []

    hit_type_response = client.create_hit_type(
        AutoApprovalDelayInSeconds=auto_approval_days * 24 * 60 * 60,
        AssignmentDurationInSeconds=duration_sec,
        Reward=str(completion_reward_usd),
        Title=HIT_group_title,
        Keywords=Keywords,
        Description=HIT_group_description,
        QualificationRequirements=qualification_requirements)

    hit_ids = []
    for n_hits, url in zip(num_assignments_per_hit, url_list):
        q = external_question_template(url, HIT_FRAME_HEIGHT)

        _hit = client.create_hit_with_hit_type(
            HITTypeId=hit_type_response['HITTypeId'],
            Question=q,
            MaxAssignments=n_hits,
            LifetimeInSeconds=LifetimeInSeconds,
        )

        print('Created %d assignments of HIT %s at %s' % (n_hits, _hit['HIT']['HITId'], url))
        hit_ids.append(_hit['HIT']['HITId'])

    return hit_ids
