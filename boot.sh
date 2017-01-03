#!/bin/sh
cd /home/chip/garage-chip
# Run via Gunicorn / nginx
sudo gunicorn app:app &
# Run via Python
sudo python control.py &
