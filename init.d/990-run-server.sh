#!/bin/bash

pushd /var/www
nohup spawn-fcgi -a 127.0.0.1 -p 9002 -f /var/www/main.py -d /var/www &