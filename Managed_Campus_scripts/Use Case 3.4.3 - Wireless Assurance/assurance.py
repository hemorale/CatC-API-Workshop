from flask import Flask, request
import json
from urllib.parse import urlparse
import csv
import requests
from requests.auth import HTTPBasicAuth
import warnings
import urllib3
import time
from prettytable import PrettyTable
from datetime import datetime
from gevent import pywsgi

warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

username = "admin"			#username for the DNAC
password = "C1sco12345"		#password for the DNAC

def get_value(nested_dict, target_key):
    for key, value in nested_dict.items():
        if key == target_key:
            return value
        elif isinstance(value, dict):
            result = get_value(value, target_key)
            if result is not None:
                return result
    return None
	
def int_to_alpha(input):
    alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return alpha[input - 1]
	
def get_device_detail(dnac,token,devId):
	headers = {
		'X-Auth-Token': token
	}
	url = 'https://'+dnac+'/dna/intent/api/v1/network-device/'+devId
	response = requests.get(url, headers=headers, verify=False)
	details = response.json()['response']
	return details

def get_X_auth_token(ip, uname, pword):
    post_url = f"https://{ip}/api/system/v1/auth/token"
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(post_url, auth=HTTPBasicAuth(username=uname, password=pword), headers=headers,verify=False)
        r.raise_for_status()
        return r.json()["Token"]
    except requests.exceptions.ConnectionError as e:
        # Something wrong, cannot get service token
        print ("Error: %s" % e)
        sys.exit ()

def parse_nested_dict(nested_dict, selected_keys):
	parsed = {}
	for key, value in nested_dict.items():
		if key in selected_keys:
			parsed[key]=value
		if isinstance(value, dict):
			parse_nested_dict(value, selected_keys)
	return parsed

app = Flask(__name__)
@app.route('/webhook', methods=['POST'])

def respond():
	data_list = []
	dnac_issues = PrettyTable(['issueId', 'issuePriority', 'issueName', 'issueSummary', 'device_name', 'device_mgmtip', 'issueDescription'])
	dnac_issues.padding_width = 1
	dnac_issues.align = "l"
	
	data = request.json
	#print(data,'\n')
	selected_keys = ['instanceId', 'ciscoDnaEventLink']
	result = parse_nested_dict(data, selected_keys)
	
	issueId = result['instanceId']
	parsed_url = urlparse(result['ciscoDnaEventLink'])
	dnac_ip = parsed_url.netloc
	
	print(f'Issue id : {issueId}')
	token = get_X_auth_token(dnac_ip,username,password)
	url = 'https://'+dnac_ip+'/dna/intent/api/v1/issue-enrichment-details'
	
	headers = {
	'X-Auth-Token': token,
	'entity_type': "issue_id",
	'entity_value': issueId
	}

	time.sleep(5)
	response = requests.get(url, headers=headers, verify=False)
	time.sleep(5)
	issue_output = response.json()
	issue_data = issue_output['issueDetails']['issue'][0]
	issue_d = get_value(issue_output, 'issue')
	deviceId = issue_data['deviceId']
	device_details = get_device_detail(dnac_ip,token,deviceId)
	
	issue_details = issue_d[0]
	issueId = issue_details['issueId']

	prev_issue = issueId
	issueName = issue_details['issueName']
	issueDescription = issue_details['issueDescription']
	issuePriority = issue_details['issuePriority']
	issueSummary = issue_details['issueSummary']
	suggestedActions = issue_details['suggestedActions']
	device_name = device_details['hostname']
	device_mgmtip = device_details['managementIpAddress']
	
	now = datetime.now()
	current_time = now.strftime("%H_%M_%S")
	
	data_list = [issueId, issuePriority, issueName, issueSummary, device_name, device_mgmtip, issueDescription]
	dnac_issues.add_row(data_list)
	output_filename = 'output_'+device_name+'_'+issueId+'_'+current_time+'.txt'
	output_file = open(output_filename, 'w')
	output_file.write(str(dnac_issues)+'\n')
	
	commands_filename = 'commands_'+device_name+'_'+issueId+'_'+current_time+'.csv'
	header_values = ['Issue No.','SuggestedAction','Device Name','Device ID','Command','Description']
	csvfile = open(commands_filename, 'w',newline='')
	writer = csv.writer(csvfile)
	writer.writerow(header_values)
	
	for action in range(0,len(suggestedActions)):
		output_file.write(str(action+1)+')'+suggestedActions[action]['message'])
		if get_value(suggestedActions[action],'steps'):
			len_of_steps = len(suggestedActions[action]['steps'])
			for x in range(0,len_of_steps):
				step_deviceId = suggestedActions[action]['steps'][x]['entityId']
				step_device_details = get_device_detail(dnac_ip,token,step_deviceId)
				step_device_name = step_device_details['hostname']
				step_desc = suggestedActions[action]['steps'][x]['description']
				step_command = suggestedActions[action]['steps'][x]['command']
				
				output_file.write('\n  '+int_to_alpha(x+1)+') '+step_device_name+' | '+step_desc+' | '+step_command)
				values = ['Issue:'+str(issueId),str(action+1)+int_to_alpha(x+1),step_device_name,step_deviceId,step_command,step_desc]
				writer.writerow(values)
		output_file.write('\n\n')
	print(f'\nCheck the files :\n "{output_filename}" \n "{commands_filename}"\n')
	return {'status': 'success'}, 200

if __name__ == '__main__':
	ip = '198.18.133.36'	#input('Enter IP address for listening on : ')
	port = '5000'			#input('Enter port number to listen on : ')
	print(f'Listening on {ip}:{port}')
	http_server = pywsgi.WSGIServer((ip, int(port)), app, keyfile='server.key', certfile='server.crt')
	http_server.serve_forever()