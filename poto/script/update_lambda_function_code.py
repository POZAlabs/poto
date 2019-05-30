import os
import argparse
import json
import shutil

import boto3

from poto.access import get_client
from poto.lambda_func import create_lambda_function_zip
from poto.utils import set_home

def get_parser():
    parser = argparse.ArgumentParser('lambda')
    parser.add_argument('--aws_config_path', type=str, help='config path containing aws access key and secret key')
    parser.add_argument('--zappa_stage', type=str, help='zappa_settings_key')
    parser.add_argument('--output_path', type=str, default=os.path.expanduser("~"), help='output path')
    parser.add_argument('--repo_path', type=str, help='zipped repo_path')
    parser.add_argument('--is_non_editible_packages', action="store_true")
    parser.add_argument('--func_name', type=str, help='lambda function name')
    parser.add_argument('--delete_local_zip', action="store_true")
    
    return parser

if __name__  == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    args.repo_path = set_home(args.repo_path)
    os.chdir(args.repo_path)

    func_zip_path = create_lambda_function_zip(args.repo_path, 
                                               args.output_path, 
                                               args.is_non_editible_packages, 
                                               args.zappa_stage)

    os.chdir(args.repo_path)
    settings = json.load(open("zappa_settings.json"))
    config = json.load(open(args.aws_config_path))
    lambda_client = get_client('lambda', config)

    # update function
    response = lambda_client.update_function_code(FunctionName=args.func_name,
                                                  ZipFile=open(func_zip_path, 'rb').read(),
                                                  Publish=True)
    print(response)

    if args.delete_local_zip:
        os.remove(func_zip_path)
    
