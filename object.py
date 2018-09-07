"""
Create
Retrieve
Update
Destroy
"""
import os
from .status import check_status
from .status import CREATE_STATUS, RETRIEVE_STATUS, DELETE_STATUS


def walk_dir(dir_path):
    """Generates each path of file by retreiving inside of dir"""
    for root, dirs, files in os.walk(dir_path):
        if files == []:
            continue
        for file in files:
            yield os.path.join(root, file)

def create_dir(s3, bucket_name, dir_name):
    """CREATE empty directory"""
    return check_status(s3.put_object(Bucket=bucket_name, Key=dir_name), CREATE_STATUS)

def upload_file(s3, local_file_path, bucket_name, object_name=None):
    """CREATE or UPDATE an object via uploading local file."""
    # It returns nothing
    if not object_name:
        object_name = local_file_path
    s3.upload_file(local_file_path, bucket_name, object_name)

def download_file(s3, bucket_name, object_name, local_file_path=None):
    """RETREIVE a file from S3 object"""
    # It returns nothing
    if not local_file_path:
        local_file_path = object_name
    s3.download_file(bucket_name, object_name, local_file_path)

def delete_file(s3, bucket_name, object_name):
    """DELETE an object"""
    s3.delete_object(Bucket=bucket_name, Key=object_name)

def upload_dir(s3, bucket_name, local_dir_path):
    for file in walk_dir(local_dir_path):
        upload_file(s3, file, bucket_name)

def download_dir(s3, bucket_name, dir_object):
    pass

# developing
def upload_skip_existing(s3):
    raise NotImplementedError
    try:
        s3.head_object(Bucket = bucket, Key = s3_path)
        print("Path found on S3! Skipping %s..." % s3_path)

    except:
        print("Uploading %s..." % s3_path)
        s3.upload_file(local_path, bucket, s3_path)
