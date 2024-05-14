import numpy as np
from typing import Union, List
import vat.utils.turk.quals.qual_utils as qual_utils
import collections

from tqdm import tqdm


def make_qual_exists_requirement(
        client,
        exists: bool,
        qualification_type_id: str,
        nonqualified_cannot_discover=True,
        nonqualified_cannot_preview=True,
):
    """
    Assembles a dictionary in the format of a QualificationRequirement.

    The requirement checks that the user has (exists=True) or does not have (exists=False) the qualification.
    Otherwise, blocks the user from discovering, previewing, and accepting the HIT.
    """
    if exists:
        comparator = 'Exists'
    else:
        comparator = 'DoesNotExist'

    requirement = _make_qual_requirement_core(
        client=client,
        qualification_type_id=qualification_type_id,
        comparator=comparator,
        comparator_values=[],
        country=None,
        country_subdivision=None,
        nonqualified_cannot_discover=nonqualified_cannot_discover,
        nonqualified_cannot_preview=nonqualified_cannot_preview,
    )
    return requirement


def make_qual_comparator_requirements(
        client,
        lower_bound: Union[int, type(None)],
        upper_bound: Union[int, type(None)],
        qualification_type_id: str,
):
    """
    Returns a list of requirements which allows workers with the qualification with a value between lower_bound and upper_bound, inclusive
    """

    if lower_bound is None:
        assert isinstance(upper_bound, int)

    if upper_bound is None:
        assert isinstance(lower_bound, int)

    requirement_list = []
    if lower_bound is not None:
        assert isinstance(lower_bound, int)
        lower_bound_requirement = _make_qual_requirement_core(
            client=client,
            qualification_type_id=qualification_type_id,
            comparator='GreaterThanOrEqualTo',
            comparator_values=[lower_bound],
            country=None,
            country_subdivision=None,
            nonqualified_cannot_discover=True,
            nonqualified_cannot_preview=True,
        )
        requirement_list.append(lower_bound_requirement)

    if upper_bound is not None:
        assert isinstance(upper_bound, int)
        upper_bound_requirement = _make_qual_requirement_core(
            client=client,
            qualification_type_id=qualification_type_id,
            comparator='LessThanOrEqualTo',
            comparator_values=[upper_bound],
            country=None,
            country_subdivision=None,
            nonqualified_cannot_discover=True,
            nonqualified_cannot_preview=True,
        )
        requirement_list.append(upper_bound_requirement)

    return requirement_list


def _make_qual_requirement_core(
        client,
        qualification_type_id: str,
        comparator: str,
        comparator_values: [int],
        country: Union[str, type(None)],
        country_subdivision: Union[str, type(None)],
        nonqualified_cannot_preview: bool,
        nonqualified_cannot_discover: bool,
):
    # Check that qualification is valid
    assert isinstance(qualification_type_id, str)
    client.get_qualification_type(QualificationTypeId=qualification_type_id)

    assert isinstance(comparator, str)
    assert isinstance(comparator_values, list)
    valid_comparators = ['LessThan', 'LessThanOrEqualTo', 'GreaterThan', 'GreaterThanOrEqualTo', 'EqualTo',
                         'NotEqualTo', 'Exists', 'DoesNotExist', 'In', 'NotIn', ]
    assert comparator in valid_comparators, 'Comparator must be one of %s; gave %s' % (valid_comparators, comparator)

    if comparator not in ['Exists', 'DoesNotExist']:
        assert len(comparator_values) > 0
        assert np.all([isinstance(v, int) for v in comparator_values]), 'Expected integers in list comparator_values, but found: %s' % (str([type(v) for v in comparator_values]))
    else:
        assert len(comparator_values) == 0

    if country is not None:
        if country_subdivision is not None:
            raise NotImplementedError
        raise NotImplementedError
    else:
        locale_values = []

    assert isinstance(nonqualified_cannot_preview, bool)
    assert isinstance(nonqualified_cannot_discover, bool)

    actions_guarded = 'Accept'

    if nonqualified_cannot_preview:
        actions_guarded = 'PreviewAndAccept'

    if nonqualified_cannot_discover:
        assert nonqualified_cannot_preview
        actions_guarded = 'DiscoverPreviewAndAccept'

    """
    [
            {
                'QualificationTypeId': 'string',
                'Comparator': 'LessThan'|'LessThanOrEqualTo'|'GreaterThan'|'GreaterThanOrEqualTo'|'EqualTo'|'NotEqualTo'|'Exists'|'DoesNotExist'|'In'|'NotIn',
                'IntegerValues': [
                    123,
                ],
                'LocaleValues': [
                    {
                        'Country': 'string',
                        'Subdivision': 'string'
                    },
                ],
                'RequiredToPreview': True|False,
                'ActionsGuarded': 'Accept'|'PreviewAndAccept'|'DiscoverPreviewAndAccept'
            },
        ],
    """
    requirement = {
        'QualificationTypeId': qualification_type_id,
        'Comparator': comparator,
        # 'IntegerValues': comparator_values,
        # 'LocaleValues': locale_values,
        'ActionsGuarded': actions_guarded
    }

    if comparator not in ['Exists', 'DoesNotExist']:
        requirement['IntegerValues'] = comparator_values

    return requirement


def get_valid_workers(
        client,
        requirements_list: List,
        verbose=False,
) -> dict:
    for req in requirements_list:
        assert isinstance(req, dict), 'Requirement must be a dict, not %s' % type(req)

    worker_id_to_requirement_evaluations = collections.defaultdict(dict)
    mandatory_qualification_ids = set()
    worker_pool = set()

    for req in tqdm(requirements_list, desc='Getting valid workers for these requirements'):
        comparator = req['Comparator']
        qualification_type_id = req['QualificationTypeId']

        # Retrieve all workers associated with this qualification
        worker_id_to_vals = qual_utils.list_workers_with_qual(
            client=client,
            qualification_type_id=qualification_type_id,
            verbose=False,
        )

        if verbose:
            print('Found %d workers with qualification %s' % (len(worker_id_to_vals), qualification_type_id))

        # Iterate over workers
        for worker_id in worker_id_to_vals:
            worker_pool.add(worker_id)

            value = worker_id_to_vals[worker_id]['value']
            if comparator == 'Exists':
                mandatory_qualification_ids.add(qualification_type_id)
                worker_id_to_requirement_evaluations[worker_id][qualification_type_id] = True
            elif comparator == 'LessThanOrEqualTo':
                mandatory_qualification_ids.add(qualification_type_id)

                assert isinstance(req['IntegerValues'], list)

                compare_int = int(req['IntegerValues'][0])
                if value <= compare_int:
                    worker_id_to_requirement_evaluations[worker_id][qualification_type_id] = True
                else:
                    worker_id_to_requirement_evaluations[worker_id][qualification_type_id] = False
            elif comparator == 'GreaterThanOrEqualTo':
                mandatory_qualification_ids.add(qualification_type_id)
                assert isinstance(req['IntegerValues'], list)
                compare_int = int(req['IntegerValues'][0])
                if value >= compare_int:
                    worker_id_to_requirement_evaluations[worker_id][qualification_type_id] = True
                else:
                    worker_id_to_requirement_evaluations[worker_id][qualification_type_id] = False
            elif comparator == 'DoesNotExist':
                worker_id_to_requirement_evaluations[worker_id][qualification_type_id] = False
            else:
                raise Exception(f'The requirement comparator {comparator} not supported')

    accepted_workers = []
    explicitly_rejected_workers = []
    for worker_id in worker_id_to_requirement_evaluations:

        # Reject if any qualifications failed
        passed = True
        for req_id in worker_id_to_requirement_evaluations[worker_id]:
            if not worker_id_to_requirement_evaluations[worker_id][req_id]:
                passed = False
                break

        # Reject if not all mandatory qualifications are present
        if not mandatory_qualification_ids.issubset(set(worker_id_to_requirement_evaluations[worker_id].keys())):
            passed = False

        for qual in mandatory_qualification_ids:
            if qual not in worker_id_to_requirement_evaluations[worker_id]:
                passed = False
                continue
            if not worker_id_to_requirement_evaluations[worker_id][qual]:
                passed = False

        if passed:
            accepted_workers.append(worker_id)
        else:
            explicitly_rejected_workers.append(worker_id)

    return {
        'accepted': accepted_workers,
        'rejected': explicitly_rejected_workers,
    }

