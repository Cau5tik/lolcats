#!/bin/python

import os
import sys
import boto.ec2
import boto.ec2.elb
import boto.ec2.autoscale
import boto.route53
import boto.vpc

ec2_conn=boto.ec2.connect_to_region('us-east-1')
elb_conn=boto.ec2.elb.connect_to_region('us-east-1')
asc_conn=boto.ec2.autoscale.connect_to_region('us-east-1')
r53_conn=boto.route53.connect_to_region('us-east-1')
vpc_conn=boto.vpc.VPCConnection()

VPC_IDS={'lolcats':'vpc-fac71e9f'}
SUBNET_IDS={'lolcats':'subnet-d703fda0'}
