import boto3
import json
import time
from botocore.exceptions import ClientError
from pprint import pprint as pp
import sys


def regionid(region):
 try:
  ec2 = boto3.client('ec2', region_name=region)
 except ClientError as e:
  print(e)
 return ec2

def checkregions(region,awsregions): #check if provided region is part of available regions
 response='no'
 for i in range(len(awsregions)):
  if region==awsregions[i]['RegionName']:
   response='yes'
 return response

def queryaws(ec2,arg):
 try:
  response = ec2.describe_security_groups(GroupIds=[arg]) #Making a call to AWS
 except:   # Checking for access
  response='nogroup'
  print "The groupID {} doesn't exist".format(arg)
  print "To exit press x, to try again press enything else"
  x=raw_input()
  if x=='x':
   sys.exit(1)
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
 n=0;
 try:
  ec2 = boto3.client('ec2') # Select ec2
  response=ec2.describe_regions()
  awsregions=regions=response['Regions']
  for i in range(len(awsregions)):
   if n==5:
    print "Press any key to continue.."
    aaa=raw_input()
    n=0
   region=awsregions[i]['RegionName']
   print "\nRegion {:5}".format(region)
   ec2 = regionid(region)
   response=ec2.describe_security_groups() # describe security groups
   secdata=removehttp(response) # stripping data to Sec groups only

   print "\n{:20} {:<30} {:<20} {:<20}".format("Security Group Name:", "Group ID:", "VpcID:", "Description:")
   for i in range(len(secdata)):
    print "{:20} {:<30} {:<20} {:<20}".format(secdata[i]['GroupName'], secdata[i]['GroupId'], secdata[i]['VpcId'], secdata[i]['Description'])
    n=n+1
 except ClientError as e:
   print(e)
 check='y'
  ### WE ARE GOING TO SELECT THE REGION
 print "\nSelect the region:"
 region=raw_input()
 checkregion=checkregions(region,awsregions) # checking if the region is within available regions
 if checkregion=='yes':  
  ec2 = regionid(region)
 else:
  print "Can't find the region, try again"
  sys.exit(1)
 while ( check=='y'):
  print "\nProvide a group ID to check the rulset"
  groupid=raw_input()
  groupid=groupid.strip()
  response=queryaws(ec2,groupid)
  if response=='nogroup':
   continue 
  secdata=removehttp(response) 
  #pp(secdata)
  print "\n{:20} {:<30} {:<20} {:<20}".format("Security Group Name:", "Group ID:", "VpcID:", "Description:")
  print "{:20} {:<30} {:<20} {:<20}".format(secdata[0]['GroupName'], secdata[0]['GroupId'], secdata[0]['VpcId'], secdata[0]['Description']) 
  inboundrules=secdata[0]['IpPermissions']
  outboundrules=secdata[0]['IpPermissionsEgress']
  print "\nInbound Rules:\n"
  print "\n{:20} {:<30} {:<20}".format("Protocol:", "Port Range:", "Source:")
 
 
  printrule(inboundrules)

  print "\nOutbound Rules:\n"
  print "\n{:20} {:<30} {:<20}".format("Protocol:", "Port Range:", "Source:")
 
  printrule(outboundrules)
 
  print "Save to the file? y/n"
  answer=raw_input()
  if answer =='y':
   timestr = time.strftime("%Y%m%d-%H%M%S")
   filename='{}_{}'.format(groupid,timestr) 
   with open(filename, 'w') as f:
     json.dump(response, f)
   print "The configuration for {} groupID  was saved to the {} file.\n".format(groupid,filename)
  print "\nCheck another group? y/n"
  check=raw_input()
 

if __name__ == "__main__":
  main()


