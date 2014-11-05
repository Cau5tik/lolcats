#!/bin/bash

cd /home/lolcats/lolcats
virtualenv cat_env
source cat_env/bin/activate
pip install flask gunicorn

cat nginx_server.conf >> /etc/nginx/conf.d/virtual.conf


