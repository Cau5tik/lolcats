#!/bin/bash

yum update -y
cd /home/lolcats
git clone https://github.com/Cau5tik/lolcats.git
/home/lolcats/lolcats/autorun.sh
