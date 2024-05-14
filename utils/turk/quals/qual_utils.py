from tqdm import tqdm
import datetime


def create_qualification(
        client,
        qual_name: str,
        description: str,
        verbose=True,
):
    # Check if qualification already exists; return if it does
    current_quals = get_all_qualifications(client)

    if qual_name in current_quals:
        if verbose:
            print('Found requested qual %s in existing qualifications as: %s' % (qual_name, str(current_quals[qual_name])))
        return current_quals[qual_name]['qualification_type_id']

    # Create
    response = client.create_qualification_type(
        Name=qual_name,
        Description=description,
        QualificationTypeStatus='Active'
    )
    qualification_type_id = response['QualificationType']['QualificationTypeId']
    return qualification_type_id


def check_if_worker_has_qual(
        client,
        worker_id,
        qualification_type_id
) -> (bool, datetime.datetime):
    """
    Check if a worker has a qualification
    """
    try:
        response = client.get_qualification_score(
            QualificationTypeId=qualification_type_id,
            WorkerId=worker_id
        )



        #current_value = response['Qualification']['IntegerValue']
        status = response['Qualification']['Status']
        if status == 'Granted':
            grant_datetime = response['Qualification']['GrantTime']
            return True, grant_datetime
        elif status == 'Revoked':
            return False, None
        else:
            raise ValueError('Unknown qualification status %s' % status)
    except Exception as e:
        if 'botocore.errorfactory.RequestError' in str(type(e)):
            assert 'You requested a Qualification that does not exist.' in str(e), 'Unknown error: %s' % str(e)
            return False, None
        else:
            raise e


def get_current_qual_value(
        client,
        worker_id,
        qualification_type_id,
        verbose=True,
):
    try:
        response = client.get_qualification_score(
            QualificationTypeId=qualification_type_id,
            WorkerId=worker_id
        )
        current_value = response['Qualification']['IntegerValue']
    except Exception as e:
        if 'botocore.errorfactory.RequestError' in str(type(e)):
            if verbose:
                print(f'Worker {worker_id} does not have qual {qualification_type_id}')
            current_value = None
        else:
            raise e

    """
    {
    'Qualification': {
        'QualificationTypeId': 'string',
        'WorkerId': 'string',
        'GrantTime': datetime(2015, 1, 1),
        'IntegerValue': 123,
        'LocaleValue': {
            'Country': 'string',
            'Subdivision': 'string'
        },
        'Status': 'Granted'|'Revoked'
    }
    }
    """
    return current_value


def set_qual_value(
        client,
        worker_id,
        qualification_type_id,
        value: int,
):
    assert isinstance(value, int)
    grant_qualification(
        client=client,
        worker_id=worker_id,
        qualification_type_id=qualification_type_id,
        value=value,
        send_notification=False,
    )
    return


def grant_qualification(
        client,
        worker_id: str,
        qualification_type_id: str,
        send_notification=False,
        value=1
):
    assert isinstance(value, int)

    client.associate_qualification_with_worker(
        QualificationTypeId=qualification_type_id,
        WorkerId=worker_id,
        IntegerValue=value,
        SendNotification=send_notification)


def revoke_qualification(
        client,
        worker_id: str,
        qualification_type_id: str,
):
    assert isinstance(worker_id, str)
    try:
        client.disassociate_qualification_from_worker(
            QualificationTypeId=qualification_type_id,
            WorkerId=worker_id,
            Reason='',
        )

        print('Revoked qualification %s from worker %s' % (qualification_type_id, worker_id))

    except Exception as e:
        message = str(e)
        if 'RequestError' in message:
            print(message)
        else:
            raise e

def delete_qualification(
        client,
        qualification_type_id: str,
        force=False
):
    worker_dict = list_workers_with_qual(
        client,
        qualification_type_id=qualification_type_id
    )

    print('Found %d workers with qual %s' % (len(worker_dict.keys()), qualification_type_id))

    if not force:
        confirm = input('Confirm that you would like to delete this qualification by typing "delete"')

        if confirm != 'delete':
            raise Exception

    client.delete_qualification_type(QualificationTypeId=qualification_type_id)
    print('Deleted qualification %s' % qualification_type_id)


def get_all_qualifications(client):
    """
    Get all qualifications associated with the client's AWS account
    Returns a dictionary: qualification_name:{'qualification_type_id':str, 'description':str}
    """

    qualification_dict = {}

    NextToken = ''

    call_kwargs = {}
    while NextToken is not None:

        res = client.list_qualification_types(
            MustBeRequestable=False,
            MustBeOwnedByCaller=True,
            MaxResults=100,
            **call_kwargs)

        """
        {
            'NumResults': 123,
            'NextToken': 'string',
            'QualificationTypes': [
                {
                    'QualificationTypeId': 'string',
                    'CreationTime': datetime(2015, 1, 1),
                    'Name': 'string',
                    'Description': 'string',
                    'Keywords': 'string',
                    'QualificationTypeStatus': 'Active'|'Inactive',
                    'Test': 'string',
                    'TestDurationInSeconds': 123,
                    'AnswerKey': 'string',
                    'RetryDelayInSeconds': 123,
                    'IsRequestable': True|False,
                    'AutoGranted': True|False,
                    'AutoGrantedValue': 123
                },
            ]
        }
        """

        if 'NextToken' in res:
            NextToken = res['NextToken']
        else:
            NextToken = None

        call_kwargs['NextToken'] = NextToken

        qreturn = res['QualificationTypes']
        for q in qreturn:
            qualification_type_id = q['QualificationTypeId']
            name = q['Name']
            description = q['Description']

            if name in qualification_dict:
                print('Found replicated qualification names; qual_name %s' % (name))
                assert qualification_type_id == qualification_dict[name]['qualification_type_id']


            qualification_dict[name] = {
                'qualification_type_id': qualification_type_id,
                'description': description,
            }

    return qualification_dict


def list_workers_with_qual(
        client,
        qualification_type_id: str,
        verbose=True,
) -> dict:
    """
    Return a dictionary of
        {
            workerId:{
                'GrantTime':datetime,
                'Status': 'Granted' | 'Revoked',
                'Value':int
                }
        }

    """

    qualified_workers = {}

    NextToken = ''

    call_kwargs = {}

    pbar = tqdm(desc='Paginating list_workers_with_qualification_type', disable=not verbose)
    i_calls = 0
    while NextToken is not None:
        res = client.list_workers_with_qualification_type(
            QualificationTypeId=qualification_type_id,
            Status='Granted',
            MaxResults=100,
            **call_kwargs
        )

        i_calls += 1
        pbar.update(1)

        """
            [{
                'NextToken': 'string',
                'NumResults': 123,
                'Qualifications': [
                    {
                        'QualificationTypeId': 'string',
                        'WorkerId': 'string',
                        'GrantTime': datetime(2015, 1, 1),
                        'IntegerValue': 123,
                        'LocaleValue': {
                            'Country': 'string',
                            'Subdivision': 'string'
                        },
                        'Status': 'Granted'|'Revoked'
                    },
                ]
            }]
        """
        if 'NextToken' in res:
            NextToken = res['NextToken']
            call_kwargs['NextToken'] = NextToken
        else:
            NextToken = None

        quals = res['Qualifications']

        for r in quals:
            worker_id = r['WorkerId']
            value = r['IntegerValue']
            grant_time = r['GrantTime']
            status = r['Status']
            if status == 'Revoked':
                print('Found worker %s with a revoked qualification, not returning' % (worker_id))
                continue

            assert worker_id not in qualified_workers
            qualified_workers[worker_id] = {
                'value': value,
                'grant_time': grant_time
            }

    return qualified_workers

