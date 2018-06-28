#!/bin/sh

/bin/echo "off" > /tmp/state

echo ff 00 00 > /sys/devices/platform/hzpro-mcu/rgb
sleep 0.5
echo 00 00 00 > /sys/devices/platform/hzpro-mcu/rgb
sleep 0.5
echo ff 00 00 > /sys/devices/platform/hzpro-mcu/rgb
sleep 0.5
echo 00 00 00 > /sys/devices/platform/hzpro-mcu/rgb

