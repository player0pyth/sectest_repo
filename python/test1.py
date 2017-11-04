import boto3
import json
from botocore.exceptions import ClientError
from pprint import pprint as pp

ec2 = boto3.client('ec2')

with open('sg.json', 'r') as f:
 file1=json.load(f)

sg=file1['SecurityGroups']
for i in range(len(sg)):
 print sg[i]['GroupName']

   
#except Client.Error as e:
 #   print(e)
