#!/bin/sh

sed -i "s/$HOSTNAME/$1/g" /etc/hosts
echo $1 > /etc/hostname
hostname $1
