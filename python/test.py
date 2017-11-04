import boto3
import json
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

try:
    response = ec2.describe_security_groups()
    with open('sg.json', 'w') as f:
     json.dump(response, f)
except Client.Error as e:
    print(e)
