#!/bin/sh

NOW=$(date +"%Y-%m-%d")
LOGFILE="/home/chip/garage-chip/logs/backuplog-$NOW.log"

mv /home/chip/garage-chip/events.log $LOGFILE
cp /home/chip/garage-chip/events.log.template /home/chip/garage-chip/events.log
