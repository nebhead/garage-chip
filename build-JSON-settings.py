import json

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

json_data_string = json.dumps(settings)
with open("settings.json", 'w') as settings_file:
    settings_file.write(json_data_string)

print ("Done.")
