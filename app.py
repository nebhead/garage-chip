from flask import Flask, render_template, make_response
import time
import datetime
import os
import json

app = Flask(__name__)

def readeventhistory(door_history, events):
	# Read all lines of events.log into an list(array)
	try:
		with open('events.log') as event_log:
			event_lines = event_log.readlines()
	# If file not found error, then create events.log file
	except(IOError, OSError):
		event_log = open('events.log', "w")
		event_log.close()
		event_lines = []

	# Get number of events
	events = len(event_lines)

	# Explode/Split lines into separate elements
	for x in range(events):
		door_history.append(event_lines[x].split(" "))

	# Error handling if number of events is less than 10, fill array with empty
	if (events < 10):
		for line in range((10-events)):
			door_history.append(["empty","empty","empty"])
		events = 10

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


@app.route('/')
def index():

	door_history = []
	events = 0
	readeventhistory(door_history, events)

	states = ReadStates()

	if(states['inputs']['switch'] == True):
		door_state = True
	else:
		door_state = False

	return render_template('index.html', state=door_state, events=events, door_history=door_history)

@app.route('/button')
def button():

	door_history = []
	events = 0
	readeventhistory(door_history, events)

	states = ReadStates()
	states['outputs']['button'] = True  		# Button pressed - Set state to 'on'
	WriteStates(states)		# Write button press to file

	return render_template('button.html')

@app.route('/history')
def history():
	# Read all lines of events.log into an list(array)
	try:
		with open('events.log') as event_log:
			event_lines = event_log.readlines()
	# If file not found error, then create events.log file
	except(IOError, OSError):
		event_log = open('events.log', "w")
		event_log.close()
		event_lines = []

	# Initialize/Clear the array for event data
	door_history = []
	events = len(event_lines)

	# Explode/Split lines into separate elements
	if (events == 0):
		empty_list = ["empty","empty","empty"]
		door_history.append(empty_list)
		events = 1
	else:
		for x in range(events):
			door_history.append(event_lines[x].split(" "))

	return render_template('door-log.html', door_history=door_history, events=events)

@app.route('/admin/<action>')
@app.route('/admin')
def admin(action=None):
	states = ReadStates()

	if action == 'reboot':
		states['controls']['reboot'] = True
		WriteStates(states)
		#Show Reboot Splash
		return render_template('shutdown.html', action=action)

	if action == 'shutdown':
		states['controls']['shutdown'] = True
		WriteStates(states)
		#Show Shutdown Splash
		return render_template('shutdown.html', action=action)

	uptime = os.popen('uptime').readline()

	cpuinfo = os.popen('cat /proc/cpuinfo').readlines()

	return render_template('admin.html', action=action, uptime=uptime, cpuinfo=cpuinfo)

@app.route('/manifest')
def manifest():
    res = make_response(render_template('manifest.json'), 200)
    res.headers["Content-Type"] = "text/cache-manifest"
    return res

if __name__ == '__main__':
    app.run(host='0.0.0.0')
