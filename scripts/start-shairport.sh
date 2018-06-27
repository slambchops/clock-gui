#!/bin/sh

cd /root/gui/scripts

TMP=/tmp/shair
HOSTNAME="$(cat /etc/hostname)"
STATE=/tmp/state
ON=./stream-on.sh
OFF=./stream-off.sh

rm $TMP
touch $TMP

rm $STATE
touch $STATE

echo "Hostname is " $HOSTNAME

shairport-sync --name=$HOSTNAME --metadata-pipename=$TMP --on-start=$ON --on-stop=$OFF

