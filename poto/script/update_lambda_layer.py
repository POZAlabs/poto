import os
import argparse
import json
import shutil

import boto3

from poto.access import get_client
from poto.lambda_func import create_lambda_layer
from poto.utils import set_home

def get_parser():
    parser = argparse.ArgumentParser('lambda')
    parser.add_argument('--config_path', type=str, help='config path containing aws access key and secret key')
    parser.add_argument('--zappa_stage', type=str, help='zappa_settings_key')
    parser.add_argument('--output_path', type=str, default=os.path.expanduser("~"), help='output path')
    parser.add_argument('--zappa_settings_path', type=str, help='zappa_settings_path')
    parser.add_argument('--is_non_editible_packages', action="store_true")
    parser.add_argument('--layer_name', type=str, help='lambda layer name')
    parser.add_argument('--delete_local_zip', action="store_true")
    
    return parser

if __name__  == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    args.zappa_settings_path = set_home(args.zappa_settings_path)
    os.chdir(os.path.dirname(args.zappa_settings_path))
    
    #layer_zip_path = create_lambda_layer(args.zappa_stage, args.output_path) 
    layer_zip_path = "/Users/poza/layer_201905291411.zip"

    settings = json.load(open("zappa_settings.json"))
    config = json.load(open(args.config_path))
    config['service_name'] = 'lambda'
    lambda_client = get_client(config)

    # publish layer
    response = lambda_client.publish_layer_version(LayerName=args.layer_name,
                                                Content={'ZipFile': open(layer_zip_path, 'rb').read()},
                                                CompatibleRuntimes=['python3.6'])
    print(response)

    if args.delete_local_zip:
        os.remove(layer_zip_path)
    
