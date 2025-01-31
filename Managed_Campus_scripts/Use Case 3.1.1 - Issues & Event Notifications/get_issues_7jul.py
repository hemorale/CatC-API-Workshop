#from flask import Flask, request
import json
from urllib.parse import urlparse
import csv
import requests
from requests.auth import HTTPBasicAuth
import warnings
import urllib3
import time
from prettytable import PrettyTable

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

def get_device_detail(dnac,token,devId):
	headers = {
		'X-Auth-Token': token
	}
	url = 'https://'+dnac+'/dna/intent/api/v1/network-device/'+devId
	response = requests.get(url, headers=headers, verify=False)
	details = response.json()['response']
	return details

current_time_seconds = time.time()
current_time_milliseconds = int(current_time_seconds * 1000)
relative_window_minutes = int(input("Enter the duration for which you need to pull data in minutes(like for last 10 min data, enter 10): "))
window_start_milliseconds = current_time_milliseconds - (relative_window_minutes * 60 * 1000)
endTime = current_time_milliseconds
startTime = window_start_milliseconds

output_filename = 'output.txt'
dnac_filename = 'input.csv'
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)
commands_filename = 'commands_to_run.csv'
header_values = ['Issue No.','SuggestedAction','Device Name','Device ID','Command','Description']
csvfile = open(commands_filename, 'w',newline='')
writer = csv.writer(csvfile)
writer.writerow(header_values)
output_file = open(output_filename, 'w')


with open(dnac_filename, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)

        url = 'https://'+dnac_ip+'/dna/intent/api/v1/issues'
        
        headers = {
            'X-Auth-Token': token
        }
        
        parameters = {
            'startTime' : startTime,
            'endTime' : endTime,
            'issueStatus' : 'ACTIVE'    ### ACTIVE, IGNORED, RESOLVED
            }
        
        # Send the POST request
        response = requests.get(url, headers=headers, params = parameters, verify=False)
        output = response.json()['response']
        
        url2 = 'https://'+dnac_ip+'/dna/intent/api/v1/issue-enrichment-details'
        
        count = 1
        time.sleep(5)
        
        for i in output:
            dnac_issues = PrettyTable(['issueId', 'issuePriority', 'issueName', 'issueSummary', 'device_name', 'device_mgmtip', 'issueDescription'])
            dnac_issues.padding_width = 1
            dnac_issues.align = "l"
            data_list = []
            headers2 = {
                'X-Auth-Token': token,
                'entity_type': "issue_id",
                'entity_value': i['issueId']
                }
            
            deviceId = i['deviceId']
            device_details = get_device_detail(dnac_ip,token,deviceId)
            
            issue_response = requests.get(url2, headers=headers2, verify=False)
            issue_output = issue_response.json()
            issue_d = get_value(issue_output, 'issue')
            if issue_d is None:
                continue
            
            issue_details = issue_d[0]
            issueId = issue_details['issueId']
            issueName = issue_details['issueName']
            issueDescription = issue_details['issueDescription']
            issuePriority = issue_details['issuePriority']
            issueSummary = issue_details['issueSummary']
            suggestedActions = issue_details['suggestedActions']
            device_name = device_details['hostname']
            device_mgmtip = device_details['managementIpAddress']
            
            data_list = [issueId, issuePriority, issueName, issueSummary, device_name, device_mgmtip, issueDescription]
            dnac_issues.add_row(data_list)
            output_file.write('++++++++++++++ ISSUE '+str(count)+' ++++++++++++++\n')
            output_file.write(str(dnac_issues)+'\n')
        
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
                        values = ['Issue '+str(count),str(action+1)+int_to_alpha(x+1),step_device_name,step_deviceId,step_command,step_desc]
                        writer.writerow(values)
                output_file.write('\n\n')
            count += 1
output_file.close()
print(f'\nCheck the files : "{output_filename}" & "{commands_filename}"')