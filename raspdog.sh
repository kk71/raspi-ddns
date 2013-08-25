#!/bin/bash
#coding=utf-8

#raspberry pi watchdog script
#author:kK

#change dir to
#cd ""

#dog logfile
logfile="dog.log";

#interval
interval=30s;


function put()
{
    echo $* >> $logfile;
}

function check_net_connection()
{
    baidu_header=`curl -I -s http://www.baidu.com`;
    if [ $? -ne 0 ];then
        return 1;
    fi
    headers=($baidu_header);
    if [ ${headers[1]} -eq 200 ];then
        return 0;
    else
        return 1;
    fi
}

put "raspi watchdog is working";
put `date`;
internet_connection=0;
while :; do
    if check_net_connection;then
        if [ $internet_connection -eq 0 ];then
            put "internet connection established.$`date`"
            internet_connection=1;
        fi
        put `python3 ddns.py`;
        if [ $? -ne 0 ];then
            put "ddns tool error.";
        fi
    else
        if [ $internet_connection -ne 0 ];then
            put "no internet connection. $`date`"
            internet_connection=0;
        fi
    fi
    sleep $interval;
done;

