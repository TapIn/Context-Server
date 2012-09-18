import pycurl
import os
import socket
from StringIO import StringIO

response_buffer = StringIO()
curl = pycurl.Curl()

curl.setopt(curl.URL, "http://" + socket.gethostbyname(socket.gethostname()) + "/status")

curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
curl.setopt(pycurl.CONNECTTIMEOUT, 1)

curl.perform()
curl.close()

response_value = response_buffer.getvalue()

if(response_value and response_value=="cats"):
        print "Up"
else:
        print "Down"
        os.system("bash /var/www/runserver.sh")