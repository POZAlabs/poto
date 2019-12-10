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


def _walk_dir_v2(dir_path):
    """Generates each path of file by retreiving inside of dir"""
    for root, dirs, files in os.walk(dir_path):
        if files == []:
            continue
        for file in files:
            yield root, file

def _mkdir_loop(s3_path, local_target_path='/tmp'):
    local_target_path = '/tmp'
    # 마지막 값은 파일 이름
    dirs = s3_path.split('/')[:-1]
    for unit_path in dirs:
        local_target_path = os.path.join(local_target_path, unit_path)
        try:
            os.mkdir(local_target_path)
        except OSError:
            pass

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
    """CREATE or UPDATE an object via uploading local file.
    Upload file in path same as local_file_path if you don't specify object_name.
    """
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

# TODO: version 붙이기
def download_file_not_in_local(s3, local_dir_path, bucket_name, s3_dir, max_keys=1000, save_dir=None):
    """ local directory내에 있는 file과 s3 bucket에 있는 file을 비교해, 
        local directory에 없는 file을 download 합니다.
    
    Args:
        s3: boto s3 client
        local_dir_path: str, local path compared to s3
        bucket_name: str, s3 bucket name
        s3_dir: str, s3 dir if it's more than one depth, depth delimiter is '/'
        max_keys: int, max number of files and directories you can get from s3
        save_dir: str, directory that saves files. default is same with local_dir_path
    """
    local_files = [f for f in os.listdir(local_dir_path) if f[0] != '.']
    objs = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_dir, MaxKeys=max_keys)

    if not save_dir:
        save_dir = local_dir_path

    s3_files = []
    for content in objs['Contents']:
        if content['Key'] == f'{s3_dir}/':
            continue
        file_name = os.path.basename(content['Key'])
        if file_name not in local_files:
            print(f"{file_name}이 local에 없으므로 다운로드합니다.")
            save_path = os.path.join(save_dir, file_name)
            download_file(s3, bucket_name, content['Key'], save_path)
        s3_files.append(file_name)
    
    diff = set(local_files).difference(s3_files)

    if diff:
        print(f'다음과 같은 파일들은 로컬에만 존재합니다.\n {diff}')

def delete_file(s3, bucket_name, object_name, warn=True):
    """DELETE an object"""
    if warn:
        print('Warning!!! 여기서 지우면 복구할 수 없어욧! 자칫 for문이라도 잘못 돌린 날에는..!!')
    s3.delete_object(Bucket=bucket_name, Key=object_name)

def upload_dir(s3, bucket_name, local_dir_path):
    for file in _walk_dir(local_dir_path):
        upload_file(s3, file, bucket_name)

# TODO: 버그 덩어리! 한 뎊쓰 밖에 못만듦ㅋㅋ
def upload_dir_depth(s3, bucket_name, local_dir_path, depth=1):
    """depth=1 makes one directory"""
    for root, file in _walk_dir_v2(local_dir_path):
        local_file_path = os.path.join(root, file)
        dirs = root.split('/')[-depth-1]
        object_name = os.path.join(dirs, file)
        upload_file(s3, local_file_path, bucket_name, object_name)

def upload_last_dir(s3, bucket_name, local_dir_path):
    """가장 마지막에 있는 dir과 해당 dir에 있는 모든 dir과 file을 업로드합니다."""
    dir_path_leng_without_last = _get_dir_path_length_without_last(local_dir_path)
    for root, file in _walk_dir_v2(local_dir_path):
        local_file_path = os.path.join(root, file)
        upload_path = local_file_path[dir_path_leng_without_last:]
        upload_file(s3, local_file_path, bucket_name, upload_path)

def upload_last_dir_v2(s3, bucket_name, local_dir_path, upload_dir=None):
    """ 경로 가장 마지막에 있는 directory에 있는 모든 file을 upload 합니다.

    Args:
        s3: boto s3 client
        bucket_name: str, s3 bucket name
        local_dir_path: str, every files in local_dir_path'll be uploaded to s3
        upload_dir: str, directory name uploaded in s3, default is same with last path of local_dir_path
    """
    # Upload only files not dir if you append '/' to dir
    msg = 'Don\'t append `/` to dir {}'
    assert local_dir_path[-1] != '/', msg.format(local_dir_path)
    if upload_dir is not None:
        assert upload_dir[-1] != '/', msg.format(upload_dir)

    if not upload_dir:
        upload_dir = os.path.basename(local_dir_path)
    for root, file in _walk_dir_v2(local_dir_path):
        if file[0] == '.':
            continue
        local_file_path = os.path.join(root, file)
        upload_path = os.path.join(upload_dir, file)
        upload_file(s3, local_file_path, bucket_name, upload_path)

def _get_dir_path_length_without_last(dir_path):
    splited_path = dir_path.split('/')
    dir_path_without_last = (lambda splited: splited[:-1] if splited[-1] else splited[:-2])(splited_path)
    dir_path_without_last = '/'.join(dir_path_without_last) + '/'
    
    return len(dir_path_without_last)

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
        print(f"download {dir_object}")
        for obj in result['Contents']:
            path = obj['Key']
            if local_dir_path:
                filename = path.split('/')[-1]
                local_path = os.path.join(local_dir_path, filename)
            else:
                local_path = path
            download_file(s3, bucket_name, path, local_path)
        print("download done")

def download_dir(s3, bucket_name, dir_object, save_tmp=True, force_update=False):
    """Download dir from bucket. Directory must have only one level. 
    If wrong dir name is passed or more than one directory level is passed, raise AssertionError.

    Args:
        bucket_name: str, Name of bucket
        dir_object: str, Directory that contains files.
        save_tmp: bool, Save into /tmp or not
        force_update: bool, Update even if object exists in local path
    
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
        for i, obj in enumerate(result['Contents']):
            path = obj['Key']
            
            # 첫 번째 시도에서 디렉토리를 만듭니다.
            if i == 0:
                _mkdir_loop(path, '/tmp')

            # 혹시나 문장을 찾을 때는 pass 합니다.
            if path[-1] == '/':
                continue

            if save_tmp:
                local_file_path = os.path.join('/tmp', path)
            else:
                local_file_path = path
            if not force_update:
                if os.path.exists(local_file_path):
                    continue
            download_file(s3, bucket_name, path, local_file_path)
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
