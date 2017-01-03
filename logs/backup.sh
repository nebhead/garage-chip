#!/bin/sh

NOW=$(date +"%Y-%m-%d")
LOGFILE="/home/pi/garage-chip/logs/backuplog-$NOW.log"

mv /home/pi/garage-pi/events.log $LOGFILE
cp /home/pi/garage-pi/events.log.template /home/pi/garage-pi/events.log
