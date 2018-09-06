"""
Create
Retrieve
Update
Destroy
"""

def create_dir(s3, bucket_name, dir_name):
    """CREATE empty directory"""
    return s3.put_object(Bucket=bucket_name, Key=dir_name)

def upload_file(s3, local_file_path, bucket_name, object_name):
    """CREATE or UPDATE a file via uploading local file."""
    return s3.upload_file(local_file_path, bucket_name, object_name)






##########################################################################################
import boto3
import os

bucket_name = 'models'

# create folder
s3object_name = 'S2S/'

s3.put_object(Bucket=bucket_name, Key=s3object_name)

# upload file
object_name = 'S2S_multiconditions_block6_targetsmask'
for root, dirs, files in os.walk('checkpoints/{}/'.format(object_name)):
    for file in files:
        fp = os.path.join(root, file)
        s3_path = os.path.join(s3object_name, object_name, file)
        s3.upload_file(fp, bucket_name, s3_path)


S2S_kor_dir_path = 'data/preprocessed_inputs/S2S/wordmin50_min6max10_conditions_20180501_2659033lines/'
K2L_kor_dir_path = 'data/preprocessed_inputs/K2L/wordmin50_k1_min6max10_condition_tag_20180501_2299250lines/'

# create folder
bucket_name = 'data'
s3object_name = 'K2L/'

s3.put_object(Bucket=bucket_name, Key=s3object_name)

# upload file
object_name = 'wordmin50_k1_min6max10_condition_tag_20180501_2299250lines/'
for root, dirs, files in os.walk('data/preprocessed_inputs/{}/{}/'.format(s3object_name, object_name)):
    for file in files:
        fp = os.path.join(root, file)
        s3_path = os.path.join(s3object_name, object_name, file)
        s3.upload_file(fp, bucket_name, s3_path)

# upload mp3
song_dir = '/home/ubuntu/lyricker-page/MP3/'

bucket_name = 'data'
s3object_name = 'demo_mp3'

s3.put_object(Bucket=bucket_name, Key=s3object_name)

# upload file
for root, dirs, files in os.walk(song_dir):
    for file in files:
        fp = os.path.join(root, file)
        s3_path = os.path.join(s3object_name, file)
        s3.upload_file(fp, bucket_name, s3_path)


bucket_name = 'sample-bucket'

object_name = 'sample-object'
local_file_path = '/tmp/test.txt'

s3.download_file(bucket_name, object_name, local_file_path)
