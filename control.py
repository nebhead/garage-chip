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

GPIO.setup("CSID0", GPIO.OUT) # Setup Relay IN1 on GPIO0
GPIO.output("CSID0", GPIO.LOW) # Set Relay IN1 on GPIO0 to 0 (LOW)
GPIO.setup("CSID2", GPIO.OUT) # Setup Relay IN2 on GPIO2
GPIO.output("CSID2", GPIO.LOW) # Set Relay IN2 on GPIO2 to 0 (LOW)

GPIO.setup("CSID1", GPIO.IN) # Setup Magnetic Switch on GPIO1  (set pull down)

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

		states['controls'] = {
			'shutdown': False, # Shutdown the system
			'reboot': False # Reboot the system
		}

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

def CheckDoorState(states):
	# *****************************************
	# Check switch state Open / Closed
	# Function run from Readstates()
	# *****************************************

	if (GPIO.input("CSID1") == True and states['inputs']['switch'] != True):
		states['inputs']['switch'] = True
		WriteStates(states)
		now = str(datetime.datetime.now())
		doorhistory = open("events.log", "a")
		doorhistory.write(now + " Door_Opened\n")
		doorhistory.close()
		time.sleep(1)
	if (GPIO.input("CSID1") == False and states['inputs']['switch'] != False):
		states['inputs']['switch'] = False
		WriteStates(states)
		now = str(datetime.datetime.now())
		doorhistory = open("events.log", "a")
		doorhistory.write(now + " Door_Closed\n")
		doorhistory.close()
		time.sleep(1)
	return(states)

# *****************************************
# Main Program Loop
# *****************************************

# First Init List Switch States

while True:
	states = CheckDoorState(ReadStates())
	if (states['controls']['reboot'] == True):
		# Set State Controls to False
		states['controls']['reboot'] = False
		# Write State Back to JSON
		WriteStates(states)
		# Delay 5 Seconds
		time.sleep(3)
		# Send Reboot Command
		os.system("sudo reboot")

	elif (states['controls']['shutdown'] == True):
		# Set State Controls to False
		states['controls']['shutdown'] = False
		# Write State Back to JSON
		WriteStates(states)
		# Delay 5 Seconds
		time.sleep(3)
		# Send Shutdown Halt Command
		os.system("sudo shutdown -h now")

	elif (states['outputs']['button'] == True):

		now = str(datetime.datetime.now())
		doorhistory = open("events.log", "a")
		doorhistory.write(now + " Button_Pressed\n")
		doorhistory.close()

		ToggleRelay()

		states['outputs']['button'] = False
		WriteStates(states)

	time.sleep(0.25)
#except:
#	print("Exception.  Exiting.")
#	GPIO.cleanup()
#	exit()
