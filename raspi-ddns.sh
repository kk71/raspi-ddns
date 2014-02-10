#!/bin/bash
#coding=utf-8

#raspberry pi watchdog script
#author:kK
#
# environment:
# arch linux raspberry pi with netctl network manager

#show info in green font
function put {
    echo -e "\033[032m$@\033[m";
}

if [[ $1 == "install-service" ]];then

    put "install ddns with interval=$2 and interface=$3 ..."
    sed "s/time_interval/$2/g;s/net_interface/$3/g" ddns.service > /etc/systemd/system/ddns.service;
    systemctl enable ddns.service
    systemctl start ddns.service
    if [ $? -eq 0 ];then
        put "successfully installed ddns service to systemd."
    fi
    exit

elif [[ $1 == "delete-service" ]];then

    systemctl disable ddns.service
    systemctl stop ddns.service
    if [ $? -eq 0 ];then
        put "successfully delete ddns service to systemd."
    fi
    rm /etc/systemd/system/ddns.service
    exit

elif [[ $1 == "daemon" ]];then

    interval=$2
    net_interface=$3

    #change to cuurent dir
    cd `dirname $0`;

    function check_internet_connection()
    #return: 
    #0:connection established. 
    #1:network interface not configured or ip not in public internet
    {
        #get public ip
        ifconfigs=(`ifconfig $net_interface|grep inet`);
        #for some archlinux net-tools are not installed by default.
        if [ $? == 127 ];then
            put "ifconfig is not installed, installing..."
            pacman -S --noconfirm net-tools
            ifconfigs=(`ifconfig $net_interface|grep inet`);
        fi
        inet=${ifconfigs[1]};
        if [[ inet == "" || inet == "127.0.0.1" ]];then
            put "public ip not found through interface $net_interface"
            return 1
        fi
        #check route table if the ip is the default route
        route_table_first_item=(`route | sed -n "3p"`);
        let route_table_first_item_length=${#route_table_first_item[@]};
        if [[ ${route_table_first_item[$route_table_first_item_length - 1]} != $net_interface ]];then
            put "default route interface is not $net_interface."
            route add default gw $inet $net_interface
            if [ $? -ne 0 ];then
                put "ERROR! failed when changing default route..."
                put "this could cause your ddns tool sync your raspi through another gateway!"
                return 1
            fi
            put "default route changed successfully."
        fi
    }

    echo "Raspi ddns started.";
    internet_connection=0; #0 stand for no Internet access
    while :; do
        check_internet_connection;
        if [ $? -eq 0 ]; then
            if [ $internet_connection -eq 0 ];then
                echo "Internet connection established. $`date`"
                internet_connection=1;
            fi
            if [[ $1 == "daemon" ]]; then
                echo `python3 ddns.py`;
            fi
            if [ $? -ne 0 ];then
                echo "ddns tool error. reinstall it from git.";
            fi
        else
            if [ $internet_connection -eq 1 ];then
                echo "No internet connection. $`date`" >> /dev/stderr
                internet_connection=0;
            fi
        fi
        sleep $interval;
    done;
fi
