import json

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

json_data_string = json.dumps(states)
with open("states.json", 'w') as settings_file:
    settings_file.write(json_data_string)

print ("Done.")
