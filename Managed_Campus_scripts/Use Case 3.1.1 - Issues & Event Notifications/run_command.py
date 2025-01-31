import json
from urllib.parse import urlparse
import csv
import requests
from requests.auth import HTTPBasicAuth
import warnings
import urllib3
import time
from prettytable import PrettyTable

output_filename = 'command_output.txt'

def get_X_auth_token(ip, uname, pword):
    post_url = "https://"+ip+"/api/system/v1/auth/token"
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(post_url, auth=HTTPBasicAuth(username=uname, password=pword), headers=headers,verify=False)
        r.raise_for_status()
        return r.json()["Token"]
    except requests.exceptions.ConnectionError as e:
        print ("Error: %s" % e)
        sys.exit ()

def cmd_runner(token, host, device_id, ios_cmd):
	param = {
		"name": "Show Command",
		"commands": [ios_cmd],
		"deviceUuids": [device_id]
	}
	url_cmd = f'https://{host}/api/v1/network-device-poller/cli/read-request'
	header = {'content-type': 'application/json', 'x-auth-token': token}
	response = requests.post(url_cmd, data=json.dumps(param), headers=header, verify=False)
	task_id = response.json()['response']['taskId']
	return task_id

def get_task(taskid, token, host,counter):
	out = open('temp.txt','w')
	url = f'https://{host}/api/v1/task/{taskid}'
	hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
	task_result = requests.get(url, headers=hdr, verify=False)
	fileid = task_result.json()['response']['progress']
	if "fileId" in fileid:
		unwanted_chars = '{"}'
		for char in unwanted_chars:
			fileid = fileid.replace(char, '')
		fileid = fileid.split(':')
		fileid = fileid[1]
		url_o = f'https://{host}/api/v1/file/{fileid}'
		cmd_result = requests.get(url_o, headers=hdr, verify=False)
		x = cmd_result.json()[0]['commandResponses']
		if x['SUCCESS']:
			out.write(json.dumps(x['SUCCESS']))
		elif x['FAILURE']:
			out.write(json.dumps(x['FAILURE']))
		out.close()
		return out
	else:
		time.sleep(5)
		print(taskid)
		if counter == 10:
			out.write('{"Unable to run command":"Unable to run command"}')
			out.close()
			return out
		get_task(taskid, token, host,counter+1)

warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

commands_filename = 'commands_to_run.csv'
dnac_filename = 'input.csv'

issues = PrettyTable(['Issue No.','SuggestedAction','Device Name','Device ID','Command','Description','Output'])
issues.padding_width = 1
issues.align = "l"

with open(dnac_filename, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)

        # Open the CSV file
        with open(commands_filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                data = row
                task = cmd_runner(token, dnac_ip, row[3], row[4])
                cmd_result = get_task(task,token, dnac_ip,0)
                with open('temp.txt','r') as tmp:
                    out1 = json.load(tmp)
                for key in out1:
                    data.append(out1[key])
        
                issues.add_row(data)
                issues.add_row(['-----','------','-------','--------','----------------','------------------','------------------'])

with open(output_filename,'w') as t:
	t.write(str(issues)+'\n')
    
print(f'\nOutput stored in file "{output_filename}"')