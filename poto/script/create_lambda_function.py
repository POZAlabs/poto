import os
import argparse
import json
import re
import sys
import base64
import shutil

import boto3

from poto.access import get_client
from poto.lambda_func import create_lambda_layer, create_lambda_function_zip
from poto.utils import set_home

def get_parser():
    parser = argparse.ArgumentParser('lambda')
    parser.add_argument('--aws_config_path', type=str, help='config path containing aws access key and secret key')
    parser.add_argument('--zappa_stage', type=str, help='zappa_settings_key')
    parser.add_argument('--output_path', type=str, default=os.path.expanduser("~"), help='output path')
    parser.add_argument('--repo_path', type=str, help='zipped repo_path')
    parser.add_argument('--is_non_editible_packages', action="store_true")
    parser.add_argument('--layer_name', type=str, help='lambda layer name')
    parser.add_argument('--func_name', type=str, help='lambda function name')
    parser.add_argument('--handler', type=str, help='lambda handler')
    parser.add_argument('--Timeout', type=int, default=600)
    parser.add_argument('--delete_local_zip', action="store_true")
    
    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    args.repo_path = set_home(args.repo_path)
    os.chdir(args.repo_path)
    
    layer_zip_path = create_lambda_layer(args.zappa_stage, args.output_path)
    func_zip_path = create_lambda_function_zip(args.repo_path, 
                                               args.output_path, 
                                               args.is_non_editible_packages,
                                               args.zappa_stage)  

    settings = json.load(open(os.path.join(args.repo_path, "zappa_settings.json")))
    config = json.load(open(args.aws_config_path))
    lambda_client = get_client('lambda', config)
    
    # create layer
    response = lambda_client.publish_layer_version(LayerName=args.layer_name,
                                                Content={'ZipFile': open(layer_zip_path, 'rb').read()},
                                                CompatibleRuntimes=['python3.6'])

    print('='*30, 'layer', '='*30)
    print(response)

    # get layer arn
    layer_version_response = lambda_client.get_layer_version(LayerName=args.layer_name,
                                               VersionNumber=1)
    # create function
    response = lambda_client.create_function(FunctionName=args.func_name,
                                             Runtime='python3.6',
                                             Role=settings[args.zappa_stage]['role_arn'],
                                             Handler=args.handler,
                                             Code={'ZipFile': open(func_zip_path, 'rb').read()},
                                             Environment={'Variables':
                                                            settings[args.zappa_stage].get('aws_environment_variables')},
                                             Layers=[layer_version_response['LayerVersionArn']])    
    print('='*30, 'function', '='*30)
    print(response)

    if args.delete_local_zip:
        os.remove(layer_zip_path)
        os.remove(func_zip_path)
