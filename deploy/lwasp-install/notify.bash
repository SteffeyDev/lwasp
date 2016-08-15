#!/bin/bash
. /home/template/.lwasp_dbus
XAUTHORITY=/home/template/.Xauthority
export XAUTHORITY
DISPLAY=:0
export DISPLAY

notify-send $1 $2
