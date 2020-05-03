#!/usr/bin/env python3
"""
Created on Sun Apr 19 21:00:14 2020

@author: Gopi Narayanaswamy
"""

import sys, paramiko
import json 
import boto3
from checkGGgroup import checkGroup,checkPolicy


def remote_connect(hostname,username,command):
    try:
       client = paramiko.SSHClient()
       client.load_system_host_keys()
       client.set_missing_host_key_policy(paramiko.WarningPolicy)
       client.connect(hostname,username=username)
       stdin, stdout, stderr = client.exec_command(command, get_pty=True)
       #for line in iter(stdout.readline, ""):
       #    print(line, end="")
       output = [line.strip() for line in stdout.readlines()]
       #print(stdout.read().decode('ascii').strip("\n"))
       for line in output:
           print(line)
       #print(output)
       print(stderr.readlines())
    finally:
       client.close()

def remote_ftp(hostname,username,localpath,remotepath):
      try:
         client = paramiko.SSHClient()
         client.load_system_host_keys()
         client.set_missing_host_key_policy(paramiko.WarningPolicy)
         client.connect(hostname,username=username)
         sftp = client.open_sftp()
         #sftp.chdir("~/aws_gg")
         sftp.put(localpath,remotepath)
         if sftp.stat(remotepath):
            print("File uploaded")
         else:
            print("file didn`t upload")
      finally:
         client.close() 
 
exists = os.path.isfile("./ggconfig.json")        
if exists:
    with open('ggconfig.json') as f:
        custConfig = json.load(f)
    region_name = custConfig['region']
    hostname = custConfig['host_name']
    print ("Creating remote directory  ....")
    command = "mkdir -p ~/aws_gg"
    remote_connect(hostname,username,command)
    print("creating Greengrass User and Group ....")
    command = "sudo adduser --system ggc_user"
    remote_connect(hostname,username,command)
    command = "sudo groupadd --system ggc_group"
    remote_connect(hostname,username,command)
    localpath="./Pre_task_validation.sh"
    remotepath="/home/{0}/aws_gg/Pre_task_validation.sh".format(username)
    remote_ftp(hostname,username,localpath,remotepath)
    print("validating the user and directory ...")
    command = "sudo bash ~/aws_gg/Pre_task_validation.sh"
    remote_connect(hostname,username,command)
    print("installing core software in remote device ...")
    localpath="./remote_device_install_task_001.sh"
    remotepath="/home/{0}/aws_gg/remote_device_install_task_001.sh".format(username)
    remote_ftp(hostname,username,localpath,remotepath)
    command = "sudo bash ~/aws_gg/remote_device_install_task_001.sh"
    remote_connect(hostname,username,command)
    # Sets AWS Services that will be used
    gg = boto3.client('greengrass', region_name=region_name)
    iot = boto3.client('iot', region_name=region_name)
    #clientLambda = boto3.client('lambda', region_name=region_name)
    #gglambda = checkLambda(custConfig)
    # print("gglambda", gglambda)
    #if gglambda != 'error':    
    group = checkGroup(custConfig['groupName'])
    keys_cert = iot.create_keys_and_certificate(setAsActive=True)
    core_thing = iot.create_thing(thingName="{0}_core".format(group['Name']))
    iot.attach_thing_principal(
        thingName=core_thing['thingName'],
        principal=keys_cert['certificateArn'])
    policy = checkPolicy(custConfig['policyName'], region_name)
    print("policy", policy)
    iot.attach_principal_policy(
    policyName=policy['policyName'],
    principal=keys_cert['certificateArn'])
    initial_version = {'Cores': [
            {
                'Id': core_thing['thingName'], # Quite intuitive, eh?
                'CertificateArn': keys_cert['certificateArn'],
                'SyncShadow': False, # Up to you, True|False
                'ThingArn': core_thing['thingArn']
            }
    ]}
    core_definition = gg.create_core_definition(
    Name="{0}_core_def".format(group['Name']),
    InitialVersion=initial_version)
    updateconfig = gg.update_group_certificate_configuration(
            CertificateExpiryInMilliseconds='2592000000',
            GroupId=group['Id']
    )
  


    tempIoTHost = 'demo.iot.' + region_name + '.amazonaws.com'
    tempGGHost = 'greengrass.iot.' + region_name + '.amazonaws.com'
    with open('./iot-pem-crt', 'w') as f:
         f.write(keys_cert['certificatePem'])
    with open('./iot-pem-key', 'w') as f:
         f.write(keys_cert['keyPair']['PrivateKey'])
    config = {
          "coreThing": {
                "caPath": "root.ca.pem",
                "certPath": "iot-pem-crt",
                "keyPath": "iot-pem-key",
                "thingArn": core_thing['thingArn'],
                "iotHost": tempIoTHost,
                "ggHost": tempGGHost,
                "keepAlive" : 600
    },
          "runtime": {
                "cgroup": {
                    "useSystemd": "yes"
                }
            },
            "managedRespawn": False
    }
    with open('./config.json', 'w') as f:
            json.dump(config, f, indent=4)
    
else:
    print ("We do not have a greengrass config file")
      

