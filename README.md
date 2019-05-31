# poto
boto3 wrapper by Pozalabs, so called P(ozalabs)(b)oto

# install
`pip install git+https://github.com/POZAlabs/poto`

# covers
- s3
- ecs
- elb
- lambda

# how to get client
```
import json
from poto.access import get_client

# Config must have 'access_key', 'secret_key', 'region_name' keys.
# If you need endpoint_url for s3 client, use get_s3_client and 
# add 'service_name' and 'endpoint_url'.
config = json.load(open('{your config.json path}'))
client = get_client('{service_name}', config)
```
