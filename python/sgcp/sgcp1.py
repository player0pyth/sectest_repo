import boto3
import json
import time
from botocore.exceptions import ClientError
from pprint import pprint as pp


ec2 = boto3.client('ec2') # Select ec2

def callaws():
 try:
    response = ec2.describe_security_groups() #Making a call to AWS
 except:
    print "Can't access AWS"
 return response


def queryaws(arg):
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
  for i in range(len(rules)):
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
   elif not rules[i]['IpRanges'][0]['CidrIp']:
     cidrip='N/A'
   else:
    cidrip=rules[i]['IpRanges'][0]['CidrIp']
   if to_port==from_port:
    print "\n{:20} {:<30} {:<20}".format(ipproto, to_port, cidrip)
   else:
    print "\n{:20} {}-{:<30} {:<20}".format(ipproto,from_port, to_port, cidrip)

def main():
 check='y'
 response=callaws()
 secdata=removehttp(response) # stripping data to Sec groups only

 print "\n{:20} {:<30} {:<20} {:<20}".format("Security Group Name:", "Group ID:", "VpcID:", "Description:")
 for i in range(len(secdata)):
  print "{:20} {:<30} {:<20} {:<20}".format(secdata[i]['GroupName'], secdata[i]['GroupId'], secdata[i]['VpcId'], secdata[i]['Description'])
 while ( check=='y'):
  print "\nProvide a group ID to check the rulset \n"
  groupid=raw_input()
  groupid=groupid.strip()

  response=queryaws(groupid)
  if response=='nogroup':
   continue 
  secdata=removehttp(response) 
  pp(secdata)
  print "\n{:20} {:<30} {:<20} {:<20}".format("Security Group Name:", "Group ID:", "VpcID:", "Description:")
  
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








