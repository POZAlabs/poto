import boto3
import json

CKPT_BUCKET = "checkpoints"
DATA_BUCKET = "data"

def get_s3client(config):
    """access s3 client
    Args:
        config: dictionary, import from json config
    Return:
        authorized s3 client
    """
    s3 = boto3.client(config['service_name'],
                      endpoint_url=config['endpoint_url'],
                      aws_access_key_id=config['access_key'],
                      aws_secret_access_key=config['secret_key'])
    return s3