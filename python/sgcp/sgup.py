import boto3
import json
import time
from botocore.exceptions import ClientError
from pprint import pprint as pp
import sys


def checkregions(region,awsregions): #check if provided region is part of available regions
 response='no'
 for i in range(len(awsregions)):
  if region==awsregions[i]['RegionName']:
   response='yes'
 return response



def callaws():
 try:
    response = ec2.describe_security_groups() #Making a call to AWS
 except:
    print "Can't access AWS"
 return response


def regionid(region):
 try:
  ec2 = boto3.client('ec2', region_name=region)
 except ClientError as e:
  print(e)
 return ec2

def regionid(region):
 try:
  ec2 = boto3.client('ec2', region_name=region)
 except ClientError as e:
  print(e)
 return ec2



def queryaws(ec2,arg):
 try:
    response = ec2.describe_security_groups(GroupIds=[arg]) #Making a call to AWS
 except:   # Checking for access
    response='nogroup'
    print "The groupID {} doesn't exist".format(arg)
 return response

def removehttp(response):
 secdata=response['SecurityGroups']
 return secdata



def printrule(rules):
 for i,a in enumerate(rules):
   if rules[i]['IpProtocol'] == '-1':
    ipproto='ALL'
    from_port='N/A'
    to_port='N/A'
   else:
    from_port=rules[i]['FromPort']
    to_port=rules[i]['ToPort']
    ipproto=rules[i]['IpProtocol']
   if not rules[i]['IpRanges']:
      cidrip=rules[i]['UserIdGroupPairs'][0]['GroupId']
   if rules[i]['IpRanges'] and rules[i]['UserIdGroupPairs']:
        cidrip=str(rules[i]['IpRanges'][0]['CidrIp'])+' +'+str(rules[i]['UserIdGroupPairs'][0]['GroupId'])
   elif not rules[i]['IpRanges'] or not rules[i]['IpRanges'][0]['CidrIp']:
    cidrip='N/A'
   else:
    cidrip=rules[i]['IpRanges'][0]['CidrIp']
   if to_port==from_port:
    print "\n{:20} {:<30} {:<20}".format(ipproto, to_port, cidrip)
   else:
    print "\n{:20} {}-{:<30} {:<20}".format(ipproto,from_port, to_port, cidrip)

def main():
 check='y'
 ec2 = boto3.client('ec2') # Select ec2
 response=ec2.describe_regions()
 print"Available Regions:\n"
 awsregions=regions=response['Regions']
 for i,a in enumerate(awsregions):
  region=awsregions[i]['RegionName']
  sys.stdout.write(region)
  sys.stdout.write(',')
  sys.stdout.write(' ')
 ### WE ARE GOING TO SELECT THE REGION
 print "\nSelect the region:"
 region=raw_input()
 checkregion=checkregions(region,awsregions) # checking if the region is within available regions
 if checkregion=='yes':  
  ec2 = regionid(region)
 else:
  print "Can't find the region, try again"
  sys.exit(1)
 response=ec2.describe_security_groups() # describe security groups
 secdata=removehttp(response) # stripping data to Sec groups only
 print "\nAvailable security groups:"
 print "\n{:20} {:<30} {:<20} {:<20}".format("Security Group Name:", "Group ID:", "VpcID:", "Description:")
 for i in range(len(secdata)):
  print "{:20} {:<30} {:<20} {:<20}".format(secdata[i]['GroupName'], secdata[i]['GroupId'], secdata[i]['VpcId'], secdata[i]['Description'])
 while ( check=='y'):
  
  response = ec2.describe_vpcs()
  vpc_data = response.get('Vpcs', [{}])
  print "\nAvailable VPCs:\n"
  for i in range(len(vpc_data)):
       vpc_id = response.get('Vpcs', [{}])[i].get('VpcId', '')
       print vpc_id
  print "Would you like to add another security group?y/n"
  check=raw_input().strip()
  if check!='y': break 
  
  print "\n Provide the file name for upload"
  filename=raw_input().strip()
  try: 
   with open(filename, 'r') as f:
     data=json.load( f)  
  except:
   print "can't find the file"
   continue
  sg_data = data.get('SecurityGroups', [{}])[0]
  #pp(sg_data) #Check the file
  
  print"\nThe Security Group Name: {} Description: {} OLD_VPC_ID: {} OLD_GROUP_ID: {}".format(sg_data['GroupName'], sg_data['Description'], sg_data['VpcId'],sg_data['GroupId'])
 
  print "\n Would you like to change the name of the  SG? y/n"
  sgname_check=raw_input().strip()
  if sgname_check!='y':
   sgname= sg_data['GroupName']
  else:
   print "\nProvide new value:"
   sgname=raw_input().strip()
  print "\n Would you like to change  description of the  SG? y/n"
  sgdesc_check=raw_input().strip()
  if sgdesc_check!='y':
   sgdesc= sg_data['Description']
  else:
   print "\nProvide new value:"
   sgdesc=raw_input().strip()     
  print "\n Please provide the VPC ID for the new group?"
  nvpc_id=raw_input().strip()
  try:
    response = ec2.create_security_group(GroupName=sgname,
                                         Description=sgdesc,
                                         VpcId=nvpc_id)
    security_group_id = response['GroupId']
    print('Security Group Successfully Created %s in vpc %s.' % (security_group_id, vpc_id))
  except ClientError as e:
    print(e)
    print "\nWould you like to try again? y/n"
    check=raw_input()
    if check=='y':
       continue
    else:
       break

  for i in range(len(sg_data['IpPermissionsEgress'])): # check if permit ip any any exists in the outband rule in the file
   if sg_data['IpPermissionsEgress'][i]['IpProtocol']=='-1' and sg_data['IpPermissionsEgress'][i]['IpRanges'][0]['CidrIp']=='0.0.0.0/0':
    del sg_data['IpPermissionsEgress'][i]
   else:
    ec2.revoke_security_group_egress(GroupId=security_group_id,IpPermissions=[{u'IpProtocol': u'-1',
                                                u'IpRanges': [{u'CidrIp': u'0.0.0.0/0'}],
                                                u'Ipv6Ranges': [],
                                                u'PrefixListIds': [],
                                                u'UserIdGroupPairs': []}])
  try:

   data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=sg_data['IpPermissions'])
   print('Ingress rules Successfully Set HTTPStatusCode  %s' % data['ResponseMetadata']['HTTPStatusCode'])
   
   if sg_data['IpPermissionsEgress']:
    data = ec2.authorize_security_group_egress(
        GroupId=security_group_id,
        IpPermissions=sg_data['IpPermissionsEgress'])
    print('Egress rules Successfully Set HTTPStatusCode %s' % data['ResponseMetadata']['HTTPStatusCode'])
  except ClientError as e:
   print(e)
  
  print "\nWould you like to try again? y/n"
  check=raw_input()


if __name__ == "__main__":
  main()








