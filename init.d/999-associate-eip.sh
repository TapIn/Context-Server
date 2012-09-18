#!/bin/bash

if [ $USERDATA == "prod" ]
then
    echo "--> Registering EIP"
    ec2-associate-address -i $AMI_ID 184.169.132.52
fi
