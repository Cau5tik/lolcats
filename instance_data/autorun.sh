#!/bin/bash

cd /home/lolcats/lolcats
virtualenv cat_env
source cat_env/bin/activate
pip install flask gunicorn

cat /home/lolcats/lolcats/instance_data/nginx_server.conf >> /etc/nginx/conf.d/virtual.conf
chown -R lolcats:lolcats /home/lolcats
/home/lolcats/lolcats/instance_data/start.sh


