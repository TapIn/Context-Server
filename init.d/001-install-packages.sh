#!/bin/bash

# Install webpy
echo "--> Installing webpy"
git clone https://github.com/webpy/webpy /tmp/webpy
pushd /tmp/webpy/
python setup.py install
popd

# Apt-get update first because EC2 messed something up recently
apt-get update
sleep 2

# Install PIP
echo "--> Installing pip"
apt-get install python-pip python-dev build-essential -y
sleep 2

echo "--> Installing Requests"
pip install requests
