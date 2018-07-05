#!/bin/sh

GUI_DIR=/usr/share/gui
SHAIR_DIR=/tmp/shair
STATE_DIR=/tmp/state

touch $SHAIR_DIR
touch $STATE_DIR

cd $GUI_DIR
python gui.py
