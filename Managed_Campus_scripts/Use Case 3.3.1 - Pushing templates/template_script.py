import requests
import csv
import urllib3
from requests.auth import HTTPBasicAuth
from datetime import datetime
import getpass
import json
import time

def get_deviceId(ip,tk,mgmtip):
	headers = {
		'X-Auth-Token': token
	}
	
	parameters = {
		"managementIpAddress": mgmtip
    }
	
	url_device = f'https://{ip}/dna/intent/api/v1/network-device'
	response = requests.get(url_device, headers=headers, params=parameters, verify=False)
	details = response.json()['response']
	return details[0]['id']

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

def show_templates(ip,tk):
    headers = {
        'X-Auth-Token': tk
    }
    print("Available Templates:")
    url_show_template = f'https://{ip}/dna/intent/api/v1/template-programmer/template'
    response = requests.get(url_show_template, headers=headers, verify=False)
    data = response.json()
    #print(data)
    print ('\n'.join(sorted([ '  {0}/{1}'.format(project['projectName'], project['name']) for project in data])))


def get_template_id(ip,tk,temp_name):
    headers = {
        'X-Auth-Token': tk
    }
    
    parts = temp_name.split("/")
    projectName = parts[0]
    templateName = parts[1]
    print ('Template: {0}/{1}'.format(projectName, templateName))
    url_search_template = f'https://{ip}/dna/intent/api/v1/template-programmer/template'
    response = requests.get(url_search_template, headers=headers, verify=False)
    data = response.json()
    
    max = 0
    id = 0
    for project in data:
        if project['projectName'] == projectName and project['name'] == templateName:
            x = project
            for v in project['versionsInfo']:
                if int(v['version']) > max:
                    max = int(v['version'])
                    id = v['id']
    return id,max,project

def print_template(ip,tk,templateId):
    headers = {
        'X-Auth-Token': tk
    }
    url_template = f'https://{ip}/dna/intent/api/v1/template-programmer/template/{templateId}'
    response = requests.get(url_template, headers=headers, verify=False)
    data = response.json()
    
    name = data['name']
    #product = data['deviceTypes'][0]['productSeries']
    content = data['templateContent']
    project = data['projectName']
    
    print(f'\nTemplate Name : {name}\nContent : {content}\nProject Name : {project}')
    #for p in data['templateParams']:
    #    print(p['parameterName'])

def deploy(ip, tk, tmp_id, device):
    print (f'\nDeploying template on {device}')

    payload = {
    "templateId": tmp_id,
    "forcePushTemplate" : 'True',
    "targetInfo": [
     {
        "id": device,
        "type": "MANAGED_DEVICE_IP"
        }
     ]
    }
    
    headers = {
        'X-Auth-Token': tk,
        'Content-Type': 'application/json'
    }
    
    url_template_apply = f'https://{ip}/dna/intent/api/v2/template-programmer/template/deploy'
    response = requests.post(url_template_apply, headers=headers, data=json.dumps(payload), verify=False)
    data = response.json()
    return data['response']

t = ''

def get_task(taskid, token, host):
	url = f'https://{host}/api/v1/task/{taskid}'
	hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
	task_result = requests.get(url, headers=hdr, verify=False)
	progress = task_result.json()['response']['progress']
	return progress

def status_template(host,tk,deploymentId):
	url = f'https://{host}/dna/intent/api/v1/template-programmer/template/deploy/status/{deploymentId}'
	hdr = {'x-auth-token': tk}
	response = requests.get(url, headers=hdr, verify=False)
	status = response.json()['status']
	detail_msg = response.json()['devices'][0]['detailedStatusMessage']
	return status,detail_msg
	
requests.packages.urllib3.disable_warnings()

with open('input.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)
        show_templates(dnac_ip,token)
    
    template_name = input('Enter project name/template name from the above list : ')
    id_template, ver, template = get_template_id(dnac_ip,token,template_name)
    if id_template == 0:
            raise ValueError('Cannot find template:{0}'.format(template_name))
    
    print_template(dnac_ip,token,id_template)
    
    ip_list = []
    dev = open('devices.txt','r')
    for line in dev:
        ip_list.append(line.strip())
        
    for ip in ip_list:
        print(f'\n+++++++{ip}++++++++\n')
        device_mgmt_ip = ip
        device = get_deviceId(dnac_ip,token,device_mgmt_ip)
        
        #apply template
        task_id = deploy(dnac_ip,token,id_template,device_mgmt_ip)
        print(f"Task Id : {task_id['taskId']}")
        
        time.sleep(10)
        
        count = 0
        while count < 50:
            x = get_task(task_id['taskId'],token,dnac_ip)
            if 'Id:' in x:
                deploymentId = x.split('Id: ')[1]
                break
            time.sleep(15)
            count += 1
        
        print(f'Deployment id : {deploymentId}')
        
        count = 0
        while count < 50:
            status,msg = status_template(dnac_ip,token,deploymentId)
            if 'SUCCESS' in status:
                print(f'Status : {status},\nMessage : {msg}')
                break
            time.sleep(15)
            count += 1