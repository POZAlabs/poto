import os
import shutil
from datetime import datetime
import json
import zipfile
import sys
import re

from poto.utils import set_home

ZIP_LIMIT_SIZE = 52400000
PACKAGE_ROOT_PATH = 'python'
PACKAGE_PATH = 'python/lib/python3.6/site-packages'
LIB_PATH = 'python/lib'
ZAPPA_OUTPUT_ZIP = 'output.zip'
DEFAULT_EXCLUDE_PACKS = ['boto3', 'botocore', 'zappa', 'kappa', 'ipython', 'IPython', 'lambda_packages', 'tqdm']


def create_lambda_layer(zappa_stage, output_path):
    # django 2.2부터는 mysqlclient 1.3.13을 쓰는데 
    # amazon linux 2017.03.1에 있는 lib~와 호환이 안 됨.
    output_path = set_home(output_path)
    _check_django_mysql_version()

    postfix = datetime.now().strftime("%Y%m%d%H%M")
    temp_dir_path = _make_temp_dir(postfix)

    _copy_and_edit_settings(temp_dir_path, zappa_stage)

    output_zip_path = os.path.join(temp_dir_path, ZAPPA_OUTPUT_ZIP)
    _make_package_dir(zappa_stage, temp_dir_path, output_zip_path)

    if os.path.getsize(output_zip_path) > ZIP_LIMIT_SIZE:
        raise AssertionError(f'package zip 용량이 {os.path.getsize(output_zip_path)}라서 {ZIP_LIMIT_SIZE}를 넘어가요')

    layer_zip = f"layer_{postfix}.zip"
    _make_dir_archi(temp_dir_path, layer_zip)

    shutil.move(layer_zip, output_path)
    shutil.rmtree(temp_dir_path)
    zip_dest_path = os.path.join(output_path, layer_zip)

    print(f'layer {zip_dest_path} created')
    
    return zip_dest_path

def create_lambda_function_zip(dir_, output_zip_path, is_non_editible_packages, zappa_stage):
    os.chdir(dir_)
    
    postfix = datetime.now().strftime("%Y%m%d%H%M")
    temp_dir_path =_make_temp_dir(postfix)
    temp_dir = os.path.basename(temp_dir_path)

    if not is_non_editible_packages:
        # default exclude에 포함 안 되는 거 제외
        editible_packages_pattern = _get_editible_packages_pattern(is_non_editible_packages, zappa_stage)
        _copy_editible_packages(temp_dir_path, editible_packages_pattern)
    
    dir_ = (lambda dir_: dir_ if dir_[-1] != '/' else dir_[:-1])(dir_)
    output_zip = f"{os.path.basename(dir_)}_{postfix}.zip"
    os.system(f'cp -r `ls -A | grep -vE "{temp_dir}"` {temp_dir}')

    os.chdir(temp_dir_path)
    os.system(f"zip -r9 {output_zip} *" )
    os.system(f"chmod 755 {output_zip}")

    zip_dest_path = os.path.join(output_zip_path, output_zip)
    os.rename(output_zip, zip_dest_path)
    shutil.rmtree(temp_dir_path)

    print(f'fuction zip {zip_dest_path} created')
    
    return zip_dest_path    

def _get_editible_packages_pattern(is_non_editible_packages, zappa_stage):
    settings = json.load(open("zappa_settings.json"))
    if not is_non_editible_packages:    
        if not settings[zappa_stage].get('exclude'):
            raise AssertionError('editible package pattern을 zappa_settings exclude에 추가해주세요. ex) "exclude": [your_packs*]')
        editible_packages_pattern = [p for p in settings[zappa_stage]['exclude'] if not re.search("|".join(DEFAULT_EXCLUDE_PACKS), p)]
        print('editible_packages_pattern', editible_packages_pattern)    
    else:
        editible_packages_pattern = None
    
    return editible_packages_pattern

def _check_django_mysql_version():
    try:
        import django
        if int(django.__version__) >= 2.2:
            try:
                import MySQLdb
                raise AssertionError('mysqlclient 1.3.13은 lambda에서 쓸 수 없어요...')
            except:
                pass
    except:
        pass

def _copy_and_edit_settings(temp_dir_path, zappa_stage):
    settings_path = os.path.join(os.getcwd(), "zappa_settings.json")
    
    if not os.path.isfile(settings_path):
        raise FileNotFoundError(f'{os.getcwd()}에 zappa_settings.json이 없어요')
    
    shutil.copy(settings_path, temp_dir_path)

    temp_settings_path = os.path.join(temp_dir_path, "zappa_settings.json")
    settings = json.load(open(temp_settings_path))
    
    if settings[zappa_stage].get('exclude'): 
        settings[zappa_stage]['exclude'] += [f"{name}*" for name in DEFAULT_EXCLUDE_PACKS]
    else:
        settings[zappa_stage]['exclude'] = [f"{name}*" for name in DEFAULT_EXCLUDE_PACKS]    
    
    with open(temp_settings_path, 'w') as out:
        json.dump(settings, out)

def _make_package_dir(zappa_stage, temp_dir_path, output_zip_path):
    os.chdir(temp_dir_path)
    os.system(f"zappa package {zappa_stage} -o {output_zip_path}")

    output = zipfile.ZipFile(output_zip_path)
    output.extractall()

def _split_dir(output_zip_path):
    raise NotImplementedError('아직 다 구현 안 됨')
    output_zip_path = output_path[:-4]
    files = os.listdir(output_path)
    package_names = []
    for file_ in files:
        if not re.search('egg-info|dist-info', file_):
            if file_[-3:] == '.py':
                file_ = file_[-3:]
            package_names.append(file_.lower())

    groups = []
    for name in package_names:
        group = []
        for file_ in files:
            if name in file_.lower():
                group.append(file_)
        groups.append(group)

    n_layer = os.path.getsize(output_path) // MAX_SIZE + (lambda: 1 if os.path.getsize(output_path) % MAX_SIZE != 0 else 0)() 
    for i in range(n_layer):
        layer_dir = f'layer_{i+1}'
        os.mkdir(layer_dir)

def _make_dir_archi(temp_dir_path, layer_zip):
    os.makedirs(PACKAGE_PATH)

    for file_ in os.listdir(temp_dir_path):
        if re.search(f'zappa_settings|{ZAPPA_OUTPUT_ZIP}|{PACKAGE_ROOT_PATH}', file_):
            continue
        elif re.search('[a-z]*\.so', file_):
            shutil.move(file_, LIB_PATH)
        else:
            shutil.move(file_, PACKAGE_PATH)
        
    os.system(f"zip -r9 {layer_zip} {PACKAGE_ROOT_PATH}")
    os.system(f"chmod 755 {layer_zip}")

def _make_temp_dir(postfix):
    temp_dir = f"temp{postfix}"
    cwd = os.getcwd()
    temp_dir_path = os.path.join(cwd, temp_dir)
    os.mkdir(temp_dir_path)

    return temp_dir_path

def _copy_editible_packages(temp_dir_path, editible_packages_pattern):
    venv = sys.prefix
    site_package_path = os.path.join(venv, 'lib/python3.6/site-packages')
    
    joined = ', '.join(os.listdir(site_package_path))
    
    for pattern in editible_packages_pattern:
        pattern = re.sub('\*', '[-.0-9a-zA-Z]*', pattern)
        targets = re.findall(pattern, joined)
        for target in targets:
            target_path = os.path.join(site_package_path, target)
            os.system(f'cp -r {target_path} {temp_dir_path}')