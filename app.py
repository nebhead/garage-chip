from flask import Flask, render_template, make_response
import time
import datetime
import os
import pickle

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

    # Start with an empty states list
	states = []

	# Read all lines of states.dat into an list(array)
	try:
		with open('states.dat', 'rb') as statesfile:
			states = pickle.load(statesfile)
			statesfile.close()
	# If file not found error, then create states.dat file
	except(IOError, OSError):
		states = ['off', 'off']
		WriteStates(states)

	return(states)

def WriteStates(states):
	# *****************************************
	# Write Switch State Values to File
	# *****************************************
	with open('states.dat', 'wb') as statesfile:
		pickle.dump(states, statesfile, protocol=2)
		statesfile.close()

@app.route('/')
def index():

	door_history = []
	events = 0
	readeventhistory(door_history, events)

	states = ReadStates()

	if(states[1] == 'on'):
		door_state = True
	else:
		door_state = False

	return render_template('index.html', state=door_state, events=events, door_history=door_history)

@app.route('/button')
def button():

	states = ReadStates()
	states[0] = 'on'  		# Button pressed - Set state to 'on'
	WriteStates(states)		# Write button press to file

	door_history = []
	events = 0
	readeventhistory(door_history, events)

	if(states[1] == 'on'):
		door_state = True
	else:
		door_state = False

	return render_template('index.html', state=door_state, events=events, door_history=door_history)

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
	if action == 'reboot':
		#Show Reboot Splash
		return render_template('shutdown.html', action=action)

	if action == 'reboot-now':
		os.system("sudo reboot")
		return 'See you tomorrow!'

	if action == 'shutdown':
		#Show Shutdown Splash
		return render_template('shutdown.html', action=action)
		#return 'Shutting Down...'

	if action == 'shutdown-now':
		os.system("sudo shutdown -h now")
		return 'Peace.'

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
