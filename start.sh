#!/bin/bash

service nginx start
/home/lolcats/lolcats/gunicorn_start &
