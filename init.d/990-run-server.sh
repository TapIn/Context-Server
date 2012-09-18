#!/bin/bash

pushd /var/www
chmod +x /var/www/main.py
chmod +x /var/www/checkserver.py
chmod +x /var/www/runserver.py
chmod +x /var/www/stopserver.py
nohup spawn-fcgi -a 127.0.0.1 -p 9002 -f /var/www/main.py -d /var/www &
