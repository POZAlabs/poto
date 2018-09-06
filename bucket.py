"""
Create
Retrieve
Update
Destroy
"""

def create_bucket(s3, bucket_name):
    """CREATE a bucket"""
    return s3.create_bucket(Bucket=bucket_name)

def get_bucket_list(s3):
    """GET all bucketnames of s3"""
    response = s3.list_buckets()
    buckets = []
    for bucket in response.get('Buckets', []):
        buckets.append(bucket.get('Name'))
    return buckets

def delete_bucket(s3, bucket_name):
    """DELETE a bucket"""
    return s3.delete_bucket(Bucket=bucket_name)