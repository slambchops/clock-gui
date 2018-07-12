#!/bin/sh

echo ff 00 00 > /sys/devices/platform/hzpro-mcu/rgb
wpa_passphrase $1 $2 > /etc/wpa_supplicant.conf
echo 00 ff 00  > /sys/devices/platform/hzpro-mcu/rgb
ifdown wlan0
echo 00 00 ff > /sys/devices/platform/hzpro-mcu/rgb
ifup wlan0
echo 00 00 00 > /sys/devices/platform/hzpro-mcu/rgb
reboot
