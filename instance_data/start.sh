#!/bin/bash

service nginx start
/home/lolcats/lolcats/instance_data/gunicorn_start &
