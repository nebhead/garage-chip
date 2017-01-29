from flask import Flask, request, render_template, make_response
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
	# Read Switch States from File
	# *****************************************

	# Read all lines of states.json into an list(array)
	try:
		json_data_file = open("settings.json", "r")
		json_data_string = json_data_file.read()
		settings = json.loads(json_data_string)
		json_data_file.close()
	except(IOError, OSError):
		# Issue with reading states JSON, so create one/write new one
		settings = {}

		settings['email'] = {
			'ToEmail': 'your_to_email', # E-mail address to send notification to
			'FromEmail': 'your_from_email', # E-mail address to log into system
			'Password' : 'your_password', # Password
			'SMTPServer' : 'smtp.gmail.com', # SMTP Server Name
			'SMTPPort' : 587 # SMTP Port
			}

		settings['notification'] = {
			'minutes': 0 # Magnetic Switch
		}
		WriteSettings(settings)

	return(settings)

def WriteSettings(settings):
	# *****************************************
	# Write all control states to JSON file
	# *****************************************
	json_data_string = json.dumps(settings)
	with open("settings.json", 'w') as settings_file:
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


@app.route('/admin/<action>', methods=['POST','GET'])
@app.route('/admin', methods=['POST','GET'])
def admin(action=None):
	states = ReadStates()
	settings = ReadSettings()

	if action == 'reboot':
		# event = "Admin_Reboot"
		# WriteLog(event)
		os.system("sleep 3 && sudo reboot &")

		#Show Reboot Splash
		return render_template('shutdown.html', action=action)

	if action == 'shutdown':
		# event = "Admin_Shutdown"
		# WriteLog(event)
		os.system("sleep 3 && sudo shutdown -h now &")

		#Show Shutdown Splash
		return render_template('shutdown.html', action=action)

	if (request.method == 'POST') and (action == 'settings'):
		response = request.form

		if('from_email' in response):
			if(response['from_email']!=''):
				print("from_email: " + response['from_email'])
				settings['email']['FromEmail'] = response['from_email']

		if('to_email' in response):
			if(response['to_email']!=''):
				print("to_email: " + response['to_email'])
				settings['email']['ToEmail'] = response['to_email']

		if('server' in response):
			if(response['server']!=''):
				print("Server: " + response['server'])
				settings['email']['SMTPServer'] = response['server']

		if('port' in response):
			if(response['port']!=''):
				print("Port: " + response['port'])
				settings['email']['SMTPPort'] = int(response['port'])

		if('password' in response):
			if(response['password']!=''):
				print("password: " + response['password'])
				settings['email']['Password'] = response['password']

		if('timeout' in response):
			if(response['timeout']!=''):
				print("Timeout: " + response['timeout'])
				settings['notification']['minutes'] = int(response['timeout'])

		WriteSettings(settings)

	uptime = os.popen('uptime').readline()

	cpuinfo = os.popen('cat /proc/cpuinfo').readlines()

	return render_template('admin.html', action=action, uptime=uptime, cpuinfo=cpuinfo, settings=settings)

@app.route('/manifest')
def manifest():
    res = make_response(render_template('manifest.json'), 200)
    res.headers["Content-Type"] = "text/cache-manifest"
    return res

if __name__ == '__main__':
    app.run(host='0.0.0.0') # use ,debug=True for debug mode
