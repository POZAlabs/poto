"""
Create
Retrieve
Update
Destroy
"""
import os
from poto.status import check_status
from poto.status import CREATE_STATUS, RETRIEVE_STATUS, DELETE_STATUS


def _walk_dir(dir_path):
    """Generates each path of file by retreiving inside of dir"""
    for root, dirs, files in os.walk(dir_path):
        if files == []:
            continue
        for file in files:
            yield os.path.join(root, file)

def list_object_detail(s3, bucket_name, max_keys=1000):
    """Retrieve all object in bucket and more detail informations are come.
    
    Return: each object has keys like `Key`, `LastModified`, `Size`.
        Key: path of object
        LastModified: uploaded or downloaded time
        Size: file size
    """
    response = check_status(s3.list_objects(Bucket=bucket_name, MaxKeys=max_keys), RETRIEVE_STATUS)
    details = []
    for obj in response['Contents']:
        obj.pop('ETag')
        obj.pop('Owner')
        obj.pop('StorageClass')
        details.append(obj)
    return details

def list_object(s3, bucket_name, max_keys=1000):
    """Returns path of each objects"""
    response = check_status(s3.list_objects(Bucket=bucket_name, MaxKeys=max_keys), RETRIEVE_STATUS)
    return [obj['Key'] for obj in response['Contents']]

def list_object_specific(s3, bucket_name, prefix, max_keys=1000):
    """Returns path of each objects"""
    response = check_status(s3.list_objects(Bucket=bucket_name, Prefix=prefix, Delimiter='/', MaxKeys=max_keys), RETRIEVE_STATUS)
    return [obj['Key'] for obj in response['Contents']]

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

def delete_file(s3, bucket_name, object_name, warn=True):
    """DELETE an object"""
    if warn:
        print('Warning!!! 여기서 지우면 복구할 수 없어욧! 자칫 for문이라도 잘못 돌린 날에는..!!')
    s3.delete_object(Bucket=bucket_name, Key=object_name)

def upload_dir(s3, bucket_name, local_dir_path):
    for file in _walk_dir(local_dir_path):
        upload_file(s3, file, bucket_name)

def download_dir_withlocal(s3, bucket_name, dir_object, local_dir_path=None):
    if dir_object[-1] != '/':
        dir_object += '/'
        
    result = check_status(s3.list_objects(Bucket=bucket_name, Prefix=dir_object, Delimiter='/'), RETRIEVE_STATUS)
    if result.get('CommonPrefixes'):
        raise AssertionError("dir_object is not the end of directory.", [obj.get('Prefix') for obj in result.get('CommonPrefixes')])
    else:
        try:
            if local_dir_path:
                os.mkdir(local_dir_path)
            else:
                pass
        except OSError:
            pass
        # download each obejcts
        for obj in result['Contents']:
            path = obj['Key']
            if local_dir_path:
                filename = path.split('/')[-1]
                local_path = os.path.join(local_dir_path, filename)
            else:
                local_path = path
            download_file(s3, bucket_name, path, local_path)
            print("{} downloaded".format(path))

def download_dir(s3, bucket_name, dir_object):
    """Download dir from bucket. Directory must have only one level. 
    If wrong dir name is passed or more than one directory level is passed, raise AssertionError.

    Args:
        bucket_name: :)
        dir_object: directory that contains files.
    
    Return:
        nothing.:)
    """
    if dir_object[-1] != '/':
        dir_object += '/'

    result = s3.list_objects(Bucket=bucket_name, Prefix=dir_object, Delimiter='/')
    result = check_status(result, RETRIEVE_STATUS)

    if result.get('CommonPrefixes'):
        msg = "dir_object is not the end of directory."
        raise AssertionError(msg, [obj.get('Prefix') for obj in result.get('CommonPrefixes')])
    else:
        # download each obejcts
        for obj in result['Contents']:
            path = obj['Key']
            download_file(s3, bucket_name, path, path)
            print("{} downloaded".format(path))

# developing
def upload_skip_existing(s3):
    raise NotImplementedError
    try:
        s3.head_object(Bucket = bucket, Key = s3_path)
        print("Path found on S3! Skipping %s..." % s3_path)

    except:
        print("Uploading %s..." % s3_path)
        s3.upload_file(local_path, bucket, s3_path)
