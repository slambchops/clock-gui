#!/bin/sh

/bin/echo "on" > /tmp/state

echo 00 00 ff > /sys/devices/platform/hzpro-mcu/rgb
sleep 0.5
echo 00 00 00 > /sys/devices/platform/hzpro-mcu/rgb
sleep 0.5
echo 00 00 ff > /sys/devices/platform/hzpro-mcu/rgb
