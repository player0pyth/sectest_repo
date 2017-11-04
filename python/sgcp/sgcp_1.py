import boto3
import json
from botocore.exceptions import ClientError
from pprint import pprint as pp


ec2 = boto3.client('ec2') # Select ec2



def callaws():
 try:
    response = ec2.describe_security_groups(DryRun=True|False) #Making a call to AWS
 except:
    print "Can't access AWS"
 return response


def queryaws(arg):
 try:
    response = ec2.describe_security_groups() #Making a call to AWS
 except Client.Error as e:   # Checking for access
    print(e)

 return response




def removehttp(response):
 secdata=response['SecurityGroups']
 return secdata



def main():
 response=callaws()
 secdata=removehttp(response) # stripping data to Sec groups only

 print "\n{:20} {:<30} {:<20} {:<20}".format("Security Group Name:", "Group ID:", "VpcID:", "Description:")
 for i in range(len(secdata)):
  print "{:20} {:<30} {:<20} {:<20}".format(secdata[i]['GroupName'], secdata[i]['GroupId'], secdata[i]['VpcId'], secdata[i]['Description'])

 print "\nProvide a group ID to check the rulset \n"
 groupid=raw_input()
 groupid=groupid.strip()
 print "\n\n"

 try:
    response = ec2.describe_security_groups(GroupIds=[groupid]) #Making a call to AWS for the specific group
    secdata=response['SecurityGroups']
 except Client.Error as e:   # Checking for access
    print "Can't find {} groupid".format(groupid)

 print "\n{:20} {:<30} {:<20} {:<20}".format("Security Group Name:", "Group ID:", "VpcID:", "Description:")

 inboundrules=secdata[0]['IpPermissions']

 pp(inboundrules)

 print "\nInbound rules\n"

 print "\n{:20} {:<30} {:<20}".format("Protocol:", "Port Range:", "Source:")

 a=range(len(inboundrules))
 print a



 for i in range(len(inboundrules)):
   if inboundrules[i]['IpProtocol'] == '-1':
    to_port='N/A'
   else: 
    to_port=inboundrules[i]['ToPort']
   if inboundrules[i]['IpRanges'][0]['CidrIp'] == None:
    cidrip='N/A' 
   else:
    cidrip=inboundrules[i]['IpRanges'][0]['CidrIp']
   print "\n{:20} {:<30} {:<20}".format(inboundrules[i]['IpProtocol'], to_port, cidrip)



if __name__ == "__main__":
  main()








