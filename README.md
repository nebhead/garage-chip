# Garage-CHIP

## CHIP based Garage Door Control / Status via Web Based Interface using Flask / Gunicorn / nginx
##### Also uses Bootstrap (http://getbootstrap.com/)

This project was inspired by Chris Driscoll's "Idiot's Guide to a Raspberry Pi Garage Door Opener" (http://www.driscocity.com/idiots-guide-to-a-raspberry-pi-garage-door-opener/).  I've replicated Chris' hardware setup almost exactly, save for the NTC CHIP (instead of the Raspberry Pi Model B).  

Instead of using the WebIO libraries that Chris uses, I decided to implement things a bit differently, providing a dynamic webUI with bootstrap and Flask.  

Initially this project used Flask's native WSGI services without Gunicorn or nginx as a proxy.  However, I noticed that after some time, the app would become unresponsive.  After a little research, it appears that Flask's built in web server is for testing purposes only and shouldn't really be used in production.  With that said, I'm using Gunicorn and nginx to proxy web resquests.  This is simple enough to configure and setup, however I had to redesign the application without the threading libraries, due to conflicts with Gunicorn.  Instead, I am using two processes running concurrently (control.py and app.py).  Control handles all of the RasPi GPIO interfaces, while App handles the web routes.  They communicate through a .dat file (using pickle to simplify the format).  

## Hardware Configuration
See the parts list, hardware setup instructions here: (http://www.driscocity.com/idiots-guide-to-a-raspberry-pi-garage-door-opener/)

### GPIO Mapping
GPIO0 - Output Relay Control (Open / Close Garage Door)
GPIO1 - Input for Magnetic Switch (Current State of Garage Door)

## Software Installation:
###NOTE: The install.sh script doesn't work properly.  Please follow the below instructions to install instead.

### Install Python PIP, Flask, Gunicorn, nginx
>sudo apt-get update

>sudo apt-get install python-pip nginx git gunicorn -y

>cd ~

>git clone https://github.com/nebhead/garage-chip

>sudo pip install flask

### Setup nginx to proxy to gunicorn
>sudo rm /etc/nginx/sites-enabled/default # Delete default configuration

>sudo cp garage-chip.nginx /etc/nginx/sites-available/garage-chip # Copy configuration file to nginx

>sudo ln -s /etc/nginx/sites-available/garage-chip /etc/nginx/sites-enabled # Create link in sites-enabled

>sudo service nginx restart # Restart nginx

### Configure Crontab for boot
>sudo crontab -l > mycron

>echo "@reboot cd /home/chip/garage-chip && sudo sh boot.sh &" >> mycron

>echo "0 0 1 * * cd /home/chip/garage-chip/logs && sh backup.sh" >> mycron

>sudo crontab mycron

>rm mycron
