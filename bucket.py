"""
Create
Retrieve
Update
Destroy
"""
from .status import check_status
from .status import CREATE_STATUS, RETRIEVE_STATUS, DELETE_STATUS


def create_bucket(s3, bucket_name):
    """CREATE a bucket"""
    success = 200
    return check_status(s3.create_bucket(Bucket=bucket_name), CREATE_STATUS)

def get_bucket_list(s3):
    """GET all bucketnames of s3"""
    response = check_status(s3.list_buckets(), RETRIEVE_STAUS)
    print(response)
    buckets = []
    for bucket in response.get('Buckets', []):
        buckets.append(bucket.get('Name'))
    return buckets

def delete_bucket(s3, bucket_name):
    """DELETE a bucket"""
    return check_status(s3.delete_bucket(Bucket=bucket_name), DELETE_STAUS)