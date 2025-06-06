import json
from urllib.parse import urlparse
import csv
import requests
from requests.auth import HTTPBasicAuth
import warnings
import urllib3
import time
from prettytable import PrettyTable

output_filename = 'final_output.txt'
dnac_filename ='input.csv'
device_filename = 'device_list.txt'


def get_X_auth_token(ip, uname, pword):
    post_url = "https://"+ip+"/api/system/v1/auth/token"
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(post_url, auth=HTTPBasicAuth(username=uname, password=pword), headers=headers,verify=False)
        #print (r.text)
        r.raise_for_status()
        # return service token
        return r.json()["Token"]
    except requests.exceptions.ConnectionError as e:
        # Something wrong, cannot get service token
        print ("Error: %s" % e)
        sys.exit ()

def cmd_runner(token, host, device_id, ios_cmd):
    param = {
        "name": "Commands",
        "commands": [ios_cmd.strip()],
        "deviceUuids": [device_id]
    }
    url_cmd = f'https://{host}/api/v1/network-device-poller/cli/read-request'
    header = {'content-type': 'application/json', 'x-auth-token': token}
    response = requests.post(url_cmd, data=json.dumps(param), headers=header, verify=False)
    task_id = response.json()['response']
    return task_id

def get_task(taskid, token, host,counter):
    out = open('temp.txt','w')
    url = f'https://{host}/api/v1/task/{taskid}'
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    task_result = requests.get(url, headers=hdr, verify=False)
    time.sleep(5)
    if 'progress' in task_result.json()['response']:
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
            if counter == 10:
                out.write('{"Unable to run command":"Unable to run command"}')
                out.close()
                return out
            get_task(taskid, token, host,counter+1)
    else:
        print('Error in running command')
        return None

warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

issues = PrettyTable(['Device Name','IP Address','Command','Output'])
issues.padding_width = 1
issues.align = "l"

commands_filename = 'commands_to_run.txt'

with open(device_filename,'r') as dev:
    lines = dev.readlines()

with open(dnac_filename, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)

        for line in lines:
            print(f'\n+++++ Running commands on {line.split(",")[1]} +++++')
            deviceid = line.split(",")[0]
            with open(commands_filename, 'r') as file:
                commands = file.readlines()
                for comm in commands:
                    print('\n'+comm.strip())
                    task = cmd_runner(token, dnac_ip, deviceid, comm)
                    #print(task)
                    if 'errorCode' in task:
                        print(f"Error in running command. Detail : {task['detail']}")
                    else:
                        print(f"Task id : {task['taskId']}")
                        cmd_result = get_task(task['taskId'],token, dnac_ip,0)
                        with open('temp.txt','r') as tmp:
                            out1 = json.load(tmp)
                        for key1 in out1:
                            device_detail = line.split(",")
                            issues.add_row([device_detail[1],device_detail[2],comm.strip(),out1[key1]])
                
                        issues.add_row(['-----','------','-------','--------'])
        issues.add_row(['++++++++','+++++++++','++++++++++','+++++++++++'])

print(f'\nOutput has been stored in file : "{output_filename}"')
with open(output_filename,'w') as t:
	t.write(str(issues)+'\n')