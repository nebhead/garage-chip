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
import pickle
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

    # Start with an empty states list
	states = []

	# Read all lines of states.dat into an list(array)
	try:
		with open('states.dat', 'rb') as statesfile:
			states = pickle.load(statesfile)
			statesfile.close()
			states = CheckDoorState(states)
	# If file not found error, then create states.dat file
	except(IOError, OSError):
		states = ['off', 'off']
		states = CheckDoorState(states)
		WriteStates(states)

	return(states)

def WriteStates(states):
	# *****************************************
	# Write Switch State Values to File
	# *****************************************
	with open('states.dat', 'wb') as statesfile:
		pickle.dump(states, statesfile, protocol=2)
		statesfile.close()

def CheckDoorState(states):
	# *****************************************
	# Check switch state Open / Closed
	# Function run from Readstates()
	# *****************************************

	if (GPIO.input("CSID1") == True and states[1] != 'on'):
		states[1] = 'on'
		now = str(datetime.datetime.now())
		doorhistory = open("events.log", "a")
		doorhistory.write(now + " Door_Opened\n")
		doorhistory.close()
		time.sleep(1)
	if (GPIO.input("CSID1") == False and states[1] != 'off'):
		states[1] = 'off'
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
states = ['off','off']
tempstates = ['off', 'off']

while True:
	tempstates = ReadStates()
	if (states != tempstates):
		states = tempstates
		if (states[0] == 'on'):
			ToggleRelay()

			now = str(datetime.datetime.now())
			doorhistory = open("events.log", "a")
			doorhistory.write(now + " Button_Pressed\n")
			doorhistory.close()

			states[0] = 'off'
		WriteStates(states)
	time.sleep(0.25)
#except:
#	print("Exception.  Exiting.")
#	GPIO.cleanup()
#	exit()
