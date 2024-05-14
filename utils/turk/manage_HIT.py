import numpy as np
from tqdm import tqdm


def print_account_balance(sandbox) -> float:
    client = vat.utils.turk.connection.get_client(sandbox)
    balance_usd = client.get_account_balance()['AvailableBalance']
    if sandbox:
        string = '(Sandbox):'
    else:
        string = 'Production:'
    print(string + ' $'+balance_usd)

    return balance_usd


def retrieve_hit_id_to_hits(hit_ids: list, client, disable_pbar=False) -> dict:
    if isinstance(hit_ids, str):
        hit_ids = [hit_ids]
    assert isinstance(hit_ids, list)
    n_hits = len(hit_ids)

    hit_ids_to_hits = {}

    if n_hits <= 10:
        # Do it on demand
        for hit_id in tqdm(hit_ids, disable=disable_pbar):
            hit_info = client.get_hit(HITId=hit_id)["HIT"]
            hit_ids_to_hits[hit_id] = hit_info
        return hit_ids_to_hits

    """
    Otherwise, do it in batch mode 
    """

    remaining_hits = list(hit_ids)

    kwargs = dict(
        MaxResults=100
    )

    h = client.list_hits(**kwargs)
    for hit in h["HITs"]:
        hit_id = hit['HITId']
        if hit_id in remaining_hits:
            remaining_hits.remove(hit_id)
            hit_ids_to_hits[hit_id] = hit

    if 'NextToken' in h:
        NextToken = h['NextToken']
    else:
        NextToken = None

    pbar = tqdm(total=n_hits, desc='pinging HIT statuses')

    nremaining_hits_to_download = len(remaining_hits)
    while (nremaining_hits_to_download > 0) and NextToken is not None:
        if NextToken is not None:
            cur_kwargs = {k: kwargs[k] for k in kwargs}
            cur_kwargs['NextToken'] = NextToken
        else:
            cur_kwargs = kwargs

        h = client.list_hits(**cur_kwargs)
        hits = h['HITs']
        for hit in hits:
            hit_id = hit['HITId']
            if hit_id in remaining_hits:
                remaining_hits.remove(hit_id)
                hit_ids_to_hits[hit_id] = hit
                pbar.update(1)

        if 'NextToken' in h:
            NextToken = h['NextToken']
        else:
            NextToken = None

        nremaining_hits_to_download = len(remaining_hits)

    pbar.refresh()
    pbar.close()

    return hit_ids_to_hits


def download_assignments_for_hit(client, hit_id: str) -> list:
    """
    Download all assignments, regardless of status, associated with this HITId.
    Returns the assignments as a list.
    """
    all_assignments = []

    nextToken = ''
    AssignmentStatuses = ['Submitted', 'Approved', 'Rejected']
    request_kwargs = dict(HITId=hit_id, MaxResults=100, AssignmentStatuses=AssignmentStatuses, )


    while nextToken is not None:

        if nextToken != '':
            request_kwargs['NextToken'] = nextToken
        else:
            if 'NextToken' in request_kwargs:
                del request_kwargs['NextToken']

        call_return = client.list_assignments_for_hit(**request_kwargs)
        """
        call_return = {
            'NextToken': 'string',
            'NumResults': 123,
            'Assignments': [
                {
                    'AssignmentId': 'string',
                    'WorkerId': 'string',
                    'HITId': 'string',
                    'AssignmentStatus': 'Submitted'|'Approved'|'Rejected',
                    'AutoApprovalTime': datetime(2015, 1, 1),
                    'AcceptTime': datetime(2015, 1, 1),
                    'SubmitTime': datetime(2015, 1, 1),
                    'ApprovalTime': datetime(2015, 1, 1),
                    'RejectionTime': datetime(2015, 1, 1),
                    'Deadline': datetime(2015, 1, 1),
                    'Answer': 'string',
                    'RequesterFeedback': 'string'
                },
            ]
        }
        """
        assignments = call_return['Assignments']


        if 'NextToken' in call_return:
            nextToken = call_return['NextToken']
        else:
            # Will break
            nextToken = None

        all_assignments.extend(assignments)
    return all_assignments


def add_more_assignments(
        hit_id: str,
        nmore: int,
        client,
        request_confirmation=True,
):
    if request_confirmation or nmore > 20:
        response = input('Add %d more assignments to %s? (y/n)' % (nmore, hit_id))
        if response != 'y':
            raise RuntimeError

    # request_token = str(io.zhash(obj = hit_id + str(nmore)))
    client.create_additional_assignments_for_hit(
        HITId=hit_id,
        NumberOfAdditionalAssignments=nmore,
        # UniqueRequestToken = request_token,
    )


def list_account_hits(client):
    nextToken = ''
    request_kwargs = dict(MaxResults=100)

    all_hits = []
    while nextToken is not None:

        if nextToken != '':
            request_kwargs['NextToken'] = nextToken
        else:
            if 'NextToken' in request_kwargs:
                del request_kwargs['NextToken']

        call_return = client.list_hits(
            **request_kwargs)



        if 'NextToken' in call_return:
            nextToken = call_return['NextToken']
        else:
            # Will break
            nextToken = None

        if 'HITs' in call_return:
            all_hits.extend(call_return["HITs"])
    return all_hits


def delete_hit(hit_id: str, client):
    try:
        client.delete_hit(
            HITId=hit_id
        )
        print(f'Hit {hit_id} was deleted.')
    except Exception as e:
        print(f'Failed to delete Hit {hit_id}.')
        raise e


def approve_assignment(assignment_id: str, client):
    response = client.approve_assignment(
        AssignmentId=assignment_id,
        RequesterFeedback='Thank you for your work!',
        OverrideRejection=True,
    )
    return response


def grant_qualification(qualification_type_id: str,
                        worker_id: str,
                        client):
    # Grant them qualification
    client.associate_qualification_with_worker(
        QualificationTypeId=qualification_type_id,
        WorkerId=worker_id,
        IntegerValue=1,
        SendNotification=False)


def grant_bonus(worker_id: str,
                assignment_id: str,
                bonus_usd: float,
                client,
                verbose=True
                ):
    bonus_amount = float(bonus_usd)
    bonus_amount = np.round(bonus_amount, decimals=2)

    MAX_BONUS_SAFETY = 2
    if bonus_amount >= MAX_BONUS_SAFETY:
        raise RuntimeWarning(
            f'About to grant %f to worker %s for assignment %s.' % (bonus_amount, worker_id, assignment_id))

    try:
        client.send_bonus(
            WorkerId=worker_id,
            BonusAmount=str(bonus_amount),
            AssignmentId=assignment_id,
            Reason='Behavior based bonus.',
            UniqueRequestToken='bonus_token_' + str(worker_id) + '_' + str(assignment_id))
        print(f'$%0.2f paid (worker {worker_id}, Assignment {assignment_id})' %bonus_amount)
        return True
    except Exception as e:
        if 'idempotency' in str(e):
            if verbose:
                print(f'Already paid bonus ($%0.2f; worker {worker_id}, Assignment {assignment_id})' % (bonus_amount))
        else:
            print(f'(workerId:{worker_id}, assignmentId:{assignment_id}: Bonus granting failed with exception: {e}')

        return False
