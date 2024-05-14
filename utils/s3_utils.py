from typing import Union, List
import os
import numpy as np
from tqdm import tqdm
import boto3
import requests

def check_if_url_exists(
        url: str,
):

    r = requests.head(url)
    return r.status_code == requests.codes.ok

def upload_file(
        dryrun: bool,
        filepath,
        bucket_name,
        object_name,
        make_public: bool,
        s3_client=None,
) -> str:
    """

    Upload a file to a _location in an S3 bucket.
    If making public, and the file endswith .png or .jpeg, sets the content type.

    :param filepath: File to upload
    :param bucket_name: Bucket to upload to
    :param object_name: S3 object qual_name.
    :return: url
    """

    assert os.path.exists(filepath)
    if not dryrun:
        # Upload the file
        if s3_client is None:
            s3_client = boto3.client(
                's3',
                # os.environ.get('AWS_ACCESS_KEY_ID'),
                # os.environ.get('AWS_SECRET_ACCESS_KEY')
            )

        ExtraArgs = {}
        if make_public == True:

            ExtraArgs['ACL'] = 'public-read'

            if filepath.endswith('.png'):
                ExtraArgs['ContentType'] = 'image/png'
            elif filepath.endswith('.jpeg'):
                ExtraArgs['ContentType'] = 'image/jpeg'
            elif filepath.endswith('.html'):
                ExtraArgs['ContentType'] = 'text/html'


        s3_client.upload_file(
            filepath,
            bucket_name,
            object_name,
            ExtraArgs=ExtraArgs
        )

    url = os.path.join('https://s3.amazonaws.com/', bucket_name, object_name)

    return url

def upload_imageset(
        dryrun: bool,
        imageset_name: str,
        image_locations: [str],
        bucket_name: str = 'mildatasets',
        make_public: bool = True,
        add_images_prefix=True,
) -> [str]:
    s3_client = boto3.client(
        's3',
        # os.environ.get('AWS_ACCESS_KEY_ID'),
        # os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

    for loc in image_locations:
        assert os.path.exists(loc), loc

    common_path = os.path.commonpath(image_locations)

    object_root = os.path.join('imagesets', imageset_name)
    pbar = tqdm(total=len(image_locations))

    image_urls = []
    for image_loc in (image_locations):
        image_relpath = os.path.relpath(image_loc, common_path)
        if add_images_prefix:
            object_name = os.path.join(object_root, 'images', image_relpath)
        else:
            object_name = os.path.join(object_root, image_relpath)

        image_url = upload_file(
            dryrun=dryrun,
            filepath=image_loc,
            bucket_name=bucket_name,
            object_name=object_name,
            make_public=make_public,
            s3_client=s3_client)

        image_urls.append(image_url)
        pbar.update(1)
    pbar.close()

    return image_urls
