# *****************************************
# Garage Door Control Python script
# *****************************************
#
# Description: This script will read the states.txt file and set relays/LEDs
# upon any changes to that file.  This script also accepts input from the IR
# sensor and will write the states.txt file and set the relays appropriately.
#
# This script runs as a separate process from the Flask / Gunicorn
# implementation which handles the web interface.
#
# *****************************************

# Imports
import time
import datetime
import os
import json
import CHIP_IO.GPIO as GPIO
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

GPIO.setup("CSID0", GPIO.OUT) # Setup Relay IN1 on GPIO0
GPIO.output("CSID0", GPIO.LOW) # Set Relay IN1 on GPIO0 to 0 (LOW)
GPIO.setup("CSID2", GPIO.OUT) # Setup Relay IN2 on GPIO2
GPIO.output("CSID2", GPIO.LOW) # Set Relay IN2 on GPIO2 to 0 (LOW)

GPIO.setup("CSID1", GPIO.IN) # Setup Magnetic Switch on GPIO1  (set pull down)

timer_start = 0 # Initialize timer_start variable, set to 0

def SendNotification(settings):

	try:
	    fromaddr = settings['email']['FromEmail']
	    toaddr = settings['email']['ToEmail']

	    msg = MIMEMultipart()
	    msg['From'] = fromaddr
	    msg['To'] = toaddr
	    msg['Subject'] = "GarageCHIP: Door Open for " + str(settings['notification']['minutes']) + " Minutes"
	    now = datetime.datetime.now()
	    body = "GarageCHIP wants you to know that your garage door has been open for " + str(settings['notification']['minutes']) + " minutes at " + str(now)

	    msg.attach(MIMEText(body, 'plain'))

	    server = smtplib.SMTP(settings['email']['SMTPServer'], settings['email']['SMTPPort'])
	    server.starttls()
	    server.login(fromaddr, settings['email']['Password'])
	    text = msg.as_string()
	    server.sendmail(fromaddr, toaddr, text)
	    server.quit()
	except():
	    print("Failed.")

    	return()

def ToggleRelay():
	# *****************************************
	# Function to Toggle Relay (and open/close the garage door)
	# *****************************************
	# Insert code to push button here
	GPIO.output("CSID0", GPIO.HIGH) 	#Turn on Relay
	time.sleep(0.5)			#Wait for 0.5s
	GPIO.output("CSID0", GPIO.LOW)	#Turn off Relay

def ReadStates():
	# *****************************************
	# Read Switch States from File
	# *****************************************

	# Read all lines of states.json into an list(array)
	try:
		json_data_file = open("states.json", "r")
		json_data_string = json_data_file.read()
		states = json.loads(json_data_string)
		json_data_file.close()
	except(IOError, OSError):
		# Issue with reading states JSON, so create one/write new one
		states = {}

		states['inputs'] = {
			'switch': False # Magnetic Switch
		}

		states['outputs'] = {
			'button': False # Relay Button
		}
		WriteStates(states)

	return(states)

def WriteStates(states):
	# *****************************************
	# Write all control states to JSON file
	# *****************************************
	json_data_string = json.dumps(states)
	with open("states.json", 'w') as settings_file:
	    settings_file.write(json_data_string)

def ReadSettings():
	# *****************************************
	# Read Settings from File
	# *****************************************

	# Read all lines of settings.json into an list(array)
	try:
		json_data_file = open("settings.json", "r")
		json_data_string = json_data_file.read()
		settings = json.loads(json_data_string)
		json_data_file.close()
	except(IOError, OSError):
		# Issue with reading settings JSON, so create one/write new one
		settings = {}

		settings['email'] = {
			'ToEmail': 'your_to_email', # E-mail address to send notification to
			'FromEmail': 'your_from_email', # E-mail address to log into system
			'Password' : 'your_password', # Password
			'SMTPServer' : 'smtp.gmail.com', # SMTP Server Name
			'SMTPPort' : 587 # SMTP Port
			}

		settings['notification'] = {
			'minutes': 0 # Minutes
		}
		WriteSettings(settings)

	return(settings)

def WriteSettings(settings):
	# *****************************************
	# Write all settings to JSON file
	# *****************************************
	json_data_string = json.dumps(settings)
	with open("settings.json", 'w') as settings_file:
	    settings_file.write(json_data_string)

def CheckDoorState(states, settings):
	# *****************************************
	# Check switch state Open / Closed
	# Function run from Readstates()
	# *****************************************
	global timer_start

	if (GPIO.input("CSID1") == True and states['inputs']['switch'] != True):
		states['inputs']['switch'] = True
		WriteStates(states)
		now = str(datetime.datetime.now())
		doorhistory = open("events.log", "a")
		doorhistory.write(now + " Door_Opened\n")
		doorhistory.close()
		if(settings['notification']['minutes'] > 0):
			timer_start = time.time() # Set start time for timer
		time.sleep(1)
	if (GPIO.input("CSID1") == False and states['inputs']['switch'] != False):
		states['inputs']['switch'] = False
		WriteStates(states)
		now = str(datetime.datetime.now())
		doorhistory = open("events.log", "a")
		doorhistory.write(now + " Door_Closed\n")
		doorhistory.close()
		timer_start = 0
		time.sleep(1)
	return(states)

# *****************************************
# Main Program Loop
# *****************************************

# First Init List Switch States

while True:
	settings = ReadSettings()
	states = CheckDoorState(ReadStates(),settings)

	if (timer_start > 0):
		if(time.time() > (timer_start + settings['notification']['minutes'])):
			SendNotification(settings)
			timer_start = 0 # Stop the timer, stop from sending another notification

	if (states['outputs']['button'] == True):

		now = str(datetime.datetime.now())
		doorhistory = open("events.log", "a")
		doorhistory.write(now + " Button_Pressed\n")
		doorhistory.close()

		ToggleRelay()

		states['outputs']['button'] = False
		WriteStates(states)

	time.sleep(0.25)

exit()
