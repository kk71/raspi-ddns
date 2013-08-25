#!/bin/bash
#coding=utf-8

#raspberry pi watchdog script
#author:kK

s=`ps -ef|egrep "bash\s.*raspdog.sh"`;
if [[ $s == "" ]];then
    echo "no dog is running."
    exit
fi
s_array=($s);
kill ${s_array[1]};
if [ $? -eq 0 ];then
    echo "raspi watchdog has been stopped."
else
    echo "can't fetch the pid to the dog,please try to figure out its pid manually."
fi
