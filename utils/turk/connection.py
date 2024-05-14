import boto3

def get_client(sandbox: bool):
    assert isinstance(sandbox, bool)
    if sandbox:
        endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    else:
        endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
    conn = boto3.client('mturk', endpoint_url=endpoint_url)
    return conn
