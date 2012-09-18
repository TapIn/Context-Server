#!/bin/sh
nohup spawn-fcgi -d /var/www -f /var/www/main.py -a 127.0.0.1 -p 9002 &