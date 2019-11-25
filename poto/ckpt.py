import numpy as np
import os
import re
from poto.object import list_object_specific, download_file

MODEL_FILENAME = 'model_ckpt'
CKPT_START = MODEL_FILENAME+'-'
CKPT_EXTENSIONS = ['data-00000-of-00001', 'index', 'meta']


def download_ckpt(s3, ckpt_dir, training=False):
    """Download latest ckpt from S3

    Args:
        s3: Verified s3 client object from boto
        ckpt_dir: checkpoints dir that starts with `checkpoints`, ends with `/`
        training: using this function as training mode or inference mode
    
    Returns:
        None
    """
    if ckpt_dir[-1] != '/':
        ckpt_dir += '/'
    assert ckpt_dir[:12] == 'checkpoints/'

    try:
        objects = list_object_specific(s3, 'checkpoints', ckpt_dir)
    except KeyError as e:
        if training:
            return None
        else:
            raise KeyError(e)
    else:
        try:
            os.mkdir(ckpt_dir)
        except OSError:
            print('Dir already exists.')
        latest_step = max(get_ckpt_steps(objects))
        download_file(s3, 'checkpoints', os.path.join(ckpt_dir, 'checkpoint'))
        for extension in CKPT_EXTENSIONS:
            download_file(s3=s3,
                        bucket_name='checkpoints',
                        object_name=os.path.join(ckpt_dir, "{}-{}.{}".format(MODEL_FILENAME, latest_step, extension)))

def download_ckpt_v2(s3, ckpt_dir, training=False):
    """Download latest ckpt from S3. 
       You don't have to pass ckpt_dir as `checkpoints/`
       That is different with `download_ckpt`

    Args:
        s3: Verified s3 client object from boto
        ckpt_dir: checkpoints dir contains `checkpoints`
        training: using this function as training mode or inference mode
    
    Returns:
        None
    """
    if ckpt_dir[-1] != '/':
        ckpt_dir += '/'
    
    splited = ckpt_dir.split('/')
    start_idx = -1
    for i, path in enumerate(splited):
        if path == 'checkpoints':
            start_idx = i

    assert start_idx != -1 , f"{ckpt_dir} doesn't contain `checkpoints`"

    prefix = "/".join(splited[start_idx:])
    
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
        for extension in CKPT_EXTENSIONS:
            file_ = f"{MODEL_FILENAME}-{latest_step}.{extension}"
            download_file(s3=s3,
                        bucket_name='checkpoints',
                        object_name=os.path.join(prefix, file_),
                        local_file_path=os.path.join(ckpt_dir, file_))

def get_ckpt_steps(objects):
    return np.unique([int(obj.split(CKPT_START)[-1].split('.')[0])
                      for obj in objects if re.search(CKPT_START, obj)])
