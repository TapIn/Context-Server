#!/bin/bash

echo "--> Installing server"
git clone git@github.com:FS-Stack/TapIn-Context-Server.git /tmp/bootstrap/context
cp -r /tmp/bootstrap/context/www /var

echo "--> Installing nginx"
apt-get install -y nginx spawn-fcgi python-flup
echo 'server {
        server_name context.tapin.tv;

        location / {
        fastcgi_param REQUEST_METHOD $request_method;
        fastcgi_param QUERY_STRING $query_string;
        fastcgi_param CONTENT_TYPE $content_type;
        fastcgi_param CONTENT_LENGTH $content_length;
        fastcgi_param GATEWAY_INTERFACE CGI/1.1;
        fastcgi_param SERVER_SOFTWARE nginx/$nginx_version;
        fastcgi_param REMOTE_ADDR $remote_addr;
        fastcgi_param REMOTE_PORT $remote_port;
        fastcgi_param SERVER_ADDR $server_addr;
        fastcgi_param SERVER_PORT $server_port;
        fastcgi_param SERVER_NAME $server_name;
        fastcgi_param SERVER_PROTOCOL $server_protocol;
        fastcgi_param SCRIPT_FILENAME $fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_script_name;
        fastcgi_pass 127.0.0.1:9002;
        }
}' > /etc/nginx/sites-available/default
service nginx restart

echo "--> Installing crontab"
crontab -l > mycron
echo '* * * * * python /var/www/checkserver.py
* * * * * ( sleep 30 ; python /var/www/checkserver.py )' >> mycron
crontab mycron
rm mycron
