import base64
import os
import json
import sys

version = sys.version_info.major

if version == 3:
    raw_input = input

def Recover(rep_label=''):
	password = None
	use = None
	label = None

	app = 'Maya'

	appdata_path = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),'MatLib')
	config_path = os.path.join(appdata_path, 'config.json')

	with open(config_path, 'r') as f:
		file_data = json.load(f)

	try:
		rep_index = file_data[app]['Redshift']['repository'].index(rep_label)
		rep_path = file_data[app]['Redshift']['dirs'][rep_index]

		if os.path.exists(rep_path):
			with open(os.path.join(rep_path, app, 'options.json'), 'r') as f:
				file_data = json.load(f)

			use = file_data.get('pass_use')
			label = file_data.get('label')

			if use == 'True':
				password = base64.b64decode(file_data.get('password')).decode('utf-8')
			else:
				password = 'no password'

	except ValueError:
		password = None
	

	return password

def password_recover(name=''):
	if name is None:
		print ('Enter the repository label to recover password.')
	elif name == 'no password':
		print ('This repository is not password protected.')
	else:
		value = Recover(rep_label=name)
		if value is None:
			print ('Repository label is wrong.')
		else:
			print ('##################')
			print ('%s password:' %name, value)
			print ('##################')






