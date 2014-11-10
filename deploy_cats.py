#!/bin/python

import os
import sys
import json
import base64
import boto.ec2
import boto.ec2.elb
import boto.ec2.autoscale
from boto.ec2.autoscale import launchconfig
from boto.ec2.autoscale import group as asg
import boto.route53
import boto.vpc

CONFIG_FILE="amazon_configs"


def load_config():
    my_config=dict()
    try:
        with open(CONFIG_FILE) as configs:
            try:
                configs=json.load(configs)
            except ValueError:
                raise Exception("CONFIG_FILE does not point to a valid JSON document")
    except IOError:
        raise Exception("Could not read file %s" % CONFIG_FILE)
    try:
        my_config['elb_config']=configs['elb_config']
    except KeyError:
        raise Exception("Could not load ELB config from %s" % CONFIG_FILE)
    try:
        my_config['launch_config']=configs['launch_config']
    except KeyError:
        raise Exception("Could not load launch config from %s" % CONFIG_FILE)
    try:
        my_config['region']=configs['region']
    except KeyError:
        raise Exception("Could not load region config from %s" % CONFIG_FILE)
    return my_config

def connect_to_aws(region):
    aws=dict()
    aws['ec2']=boto.ec2.connect_to_region(region)
    aws['elb']=boto.ec2.elb.connect_to_region(region)
    aws['as']=boto.ec2.autoscale.connect_to_region(region)
    aws['r53']=boto.route53.connect_to_region(region)
    aws['vpc']=boto.vpc.VPCConnection()
    return aws

def get_vpc(connection):
    lolcats_vpc=False
    for vpc in connection.get_all_vpcs():
        try:
            if vpc.tags['Name'] == 'lolcats_vpc':
                return vpc
        except KeyError:
            pass
    if lolcats_vpc == False:
        #make one?
        raise Exception ("VPC not found")

def get_subnet(connection):
    lolcats_subnet=False
    for subnet in connection.get_all_subnets():
        try:
            if subnet.tags['Name'] == 'lolcats_subnet':
                return subnet
        except KeyError:
            pass
    if lolcats_subnet == False:
        #make one?
        raise Exception("VPC subnet not found")

def get_security_groups(connection):
    security_groups=[]
    for security_group in connection.get_all_security_groups():
        try:
            if security_group.tags['Name'].startswith("lolcats"):
                security_groups.append(security_group)
        except KeyError:
            pass
    if len(security_groups) < 2:
        #make one/them
        raise Exception("Security groups not found")
    return security_groups
    

       
def deploy_cats():

    aws_configs=load_config()
    aws_services=connect_to_aws(aws_configs['region'])
    lolcats_vpc=get_vpc(aws_services['vpc'])
    lolcats_subnet=get_subnet(aws_services['vpc'])
    lolcats_sg=get_security_groups(aws_services['vpc'])

    launch_config=aws_configs['launch_config']
    launch_config=launchconfig.LaunchConfiguration(
        name=launch_config['name'],image_id=launch_config['image_id'], \
        key_name=launch_config['key_name'],security_groups=launch_config['security_groups'], \
        user_data=base64.b64encode(open("user_data.sh").read()), \
        instance_type=launch_config['instance_type'])
    
    
if __name__ == '__main__':
    try:
        deploy_cats()
    except Exception, e:
        print e
