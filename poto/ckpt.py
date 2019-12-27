import numpy as np
import os
import re
from poto.object import list_object_specific, download_file
from botocore.client import ClientError

MODEL_FILENAME = 'model_ckpt'
CKPT_START = MODEL_FILENAME+'-'
CKPT_EXTENSIONS = ['data-00000-of-00001', 'index', 'meta']
CONFIG_FORMAT = '{}_config.json'


def download_ckpt(s3, ckpt_dir, training=False):
    """Download latest ckpt from S3. 

    Args:
        s3: Verified s3 client object from boto
        ckpt_dir: checkpoints dir contains `checkpoints`
        training: using this function as training mode or inference mode
    
    Returns:
        None
    """
    prefix = get_prefix(ckpt_dir)
    try:
        objects = list_object_specific(s3, 'checkpoints', prefix)
    except KeyError as e:
        if training:
            return None
        else:
            raise KeyError(e)
    else:
        try:
            os.makedirs(ckpt_dir)
        except OSError:
            print('Dir already exists.')
        latest_step = max(get_ckpt_steps(objects))
        ckpt_prefix = os.path.join(prefix, 'checkpoint')
        local_file_path = os.path.join(ckpt_dir, 'checkpoint')
        
        download_file(s3, 'checkpoints', object_name=ckpt_prefix, local_file_path=local_file_path)
        # TODO: config.json까지 download
        for extension in CKPT_EXTENSIONS:
            file_ = f"{MODEL_FILENAME}-{latest_step}.{extension}"
            download_file(s3=s3,
                        bucket_name='checkpoints',
                        object_name=os.path.join(prefix, file_),
                        local_file_path=os.path.join(ckpt_dir, file_))
        

def download_model_config(s3, ckpt_dir):
    """Download model config

    Args:
        s3: Verified s3 client object from boto
        ckpt_dir: checkpoints dir contains `checkpoints`
    
    Returns:
        config path: str
    """
    prefix = get_prefix(ckpt_dir)
    # prefix format: checkpoints/some/
    project_name = os.path.basename(os.path.dirname(prefix))
    config_file = CONFIG_FORMAT.format(project_name)
    
    try:
        download_file(
            s3=s3,
            bucket_name='checkpoints',
            object_name=os.path.join(prefix, config_file),
            local_file_path=os.path.join(ckpt_dir, config_file)
        )
    except ClientError:
        print(f"{project_name} doesn't have model config.json")

    return os.path.join(ckpt_dir, config_file)


def get_prefix(ckpt_dir):
    if ckpt_dir[-1] != '/':
        ckpt_dir += '/'

    splited = ckpt_dir.split('/')
    start_idx = -1
    for i, path in enumerate(splited):
        if path == 'checkpoints':
            start_idx = i
    assert start_idx != -1 , f"{ckpt_dir} doesn't contain `checkpoints`"
    prefix = "/".join(splited[start_idx:])

    return prefix


def get_ckpt_steps(objects):
    return np.unique([int(obj.split(CKPT_START)[-1].split('.')[0])
                      for obj in objects if re.search(CKPT_START, obj)])
