#!/bin/python

import os
import sys
import json
import base64
import boto.ec2
import boto.ec2.elb
import boto.ec2.autoscale
from boto.ec2.autoscale import launchconfig
from boto.ec2.elb import HealthCheck
from boto.ec2.securitygroup import SecurityGroup 
import boto.route53
import boto.vpc

CONFIG_FILE="amazon_configs.json"

def write_log(message):
    print message

def load_config():
    try:
        write_log("Loading configurations from %s" % CONFIG_FILE)
        with open(CONFIG_FILE) as configs:
            try:
                configs=json.load(configs)
            except ValueError:
                raise Exception("CONFIG_FILE does not point to a valid JSON document")
    except IOError:
        raise Exception("Could not read file %s" % CONFIG_FILE)
    return configs

def connect_to_aws(region):
    
    aws=dict()
    write_log("Connecting to AWS")
    aws['ec2']=boto.ec2.connect_to_region(region)
    aws['elb']=boto.ec2.elb.connect_to_region(region)
    aws['asg']=boto.ec2.autoscale.connect_to_region(region)
    aws['r53']=boto.route53.connect_to_region(region)
    aws['vpc']=boto.vpc.VPCConnection()

    for key, value in aws.iteritems():
        if str(value) == 'None':
            raise Exception("Could not connect to all AWS services")

    write_log("Connected to all AWS services")
    return aws

def create_network(vpc_connection):
    
    new_vpc=vpc_connection.create_vpc('192.168.0.0/16', instance_tenancy='default')
    new_vpc.add_tag('Name',value='lolcats_vpc')
    new_gw=vpc_connection.create_internet_gateway()
    new_gw.add_tag('Name', value='lolcats_gateway')
    vpc_connection.attach_internet_gateway(new_gw.id,new_vpc.id)
    new_subnet=vpc_connection.create_subnet(new_vpc.id, '192.168.5.0/24')
    new_subnet.add_tag('Name',value='lolcats_subnet')
    
    route_tables=vpc_connection.get_all_route_tables()
    for route_table in route_tables:
        if route_table.vpc_id == new_vpc.id:
            my_route_table=route_table

    vpc_connection.create_route(my_route_table.id, '0.0.0.0/0', gateway_id=new_gw.id)
    vpc_connection.associate_route_table(my_route_table.id, new_subnet.id)

    write_log("New VPC and subnet created.")
    return new_vpc, new_subnet


def create_security_groups(ec2_connection, vpc_id, sg_configs):
    security_groups=[]
    for security_group in ec2_connection.get_all_security_groups():
        if security_group.vpc_id == vpc_id:
            security_groups.append(security_group)
            break

    write_log("Creating security groups...")
    for sg in sg_configs:
        lolcats_sg=ec2_connnection.create_security_group(
            sg['name'], ('Security group for %s' % sg['name'], vpc_id=vpc_id)
        lolcats_sg.add_tag('Name',value=sg['name'])
        lolcats_sg.authorize(
            ip_protocol=sg['ip_protocol'], from_port=sg['from_port'],
            to_port=sg['to_port'], cidr_ip=sg['cidr_ip'])
        security_groups.append(lolcats_sg)
 
    return security_groups

def destroy_existing_deployment(aws_conn):

    write_log("Destroying existing deployment..")
    for vpc in aws_conn['vpc'].get_all_vpcs():
        try:
            if vpc.tags['Name'] == 'lolcats_vpc':
                write_log("Found existing lolcats_vpc. Removing...")
                aws_conn['vpc'].delete_vpc(vpc.id)
        except KeyError:
            pass
    write_log("Existing deployment removed")
    return

def create_load_balancer(elb_connection, elb_config, hc_config, subnet_id, security_groups):

    write_log("Creating new elastic load balancer")
    listeners=[]
    for listener in elb_config['listeners']:
        listeners.append(tuple(listener))

    sec_groups=[]
    for security_group in security_groups:
        sec_groups.append(security_group.id)

    elb_hc= HealthCheck(
        interval=hc_config['interval'],
        healthy_threshold=hc_config['healthy_threshold'],
        unhealthy_threshold=hc_config['unhealthy_threshold'],
        target=hc_config['target'])    
    
    lolcats_elb=elb_connection.create_load_balancer(
        name=elb_config['name'], zones=elb_config['zones'],
        listeners=listeners, subnets=[subnet_id],
        security_groups=sec_groups)

    lolcats_elb.configure_health_check(elb_hc)

    return lolcats_elb

def create_autoscaling_group(as_connection, asg_config, security_groups, elb):
    write_log("Creating ASG launch configuration")

    launch_config=asg_config['launch_config']
    lc=launchconfig.LaunchConfiguration(
        name=launch_config['name'],image_id=launch_config['image_id'], \
        key_name=launch_config['key_name'],security_groups=launch_config['security_groups'], \
        user_data=base64.b64encode(open("user_data.sh").read()), \
        instance_type=launch_config['instance_type'])
    lolcats_lc=autoscale_connection.create_launch_configuration(lc)


       
def deploy_cats():

    lolcats=dict()
    aws_configs=load_config()

    aws_conn=connect_to_aws(aws_configs['region'])
    destroy_existing_deployment(aws_conn)

    lolcats['vpc'], lolcats['subnet']=create_network(aws_conn['vpc'])
    lolcats['sg']=create_security_groups(aws_conn['ec2'], lolcats['vpc'].id, aws_configs['security'])
    lolcats['elb']=create_load_balancer(
        aws_conn['elb'], aws_configs['elb_config'], 
        aws_config['elb_config']['healthcheck'],
        lolcats['subnet'].id, lolcats['sg'])
    lolcats['asg']=create_auto_scaling_group(
        aws_conn['asg'], aws_config['asg_config'],
        lolcats['sg'],lolcats['elb']) 

    
if __name__ == '__main__':
    try:
        deploy_cats()
    except Exception, e:
        print e
