import requests
import csv
import urllib3
from requests.auth import HTTPBasicAuth
from datetime import datetime
import getpass
from prettytable import PrettyTable
import sys
import json
import time

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

def list_images(ip,tk):
	url_images = f'https://{ip}/dna/intent/api/v1/image/importation'
	headers = {
		'X-Auth-Token': tk
	}
	response = requests.get(url_images, headers=headers, verify=False)
	data = response.json()
	img_list = PrettyTable(['Serial','Name','Version','Family','isTaggedGolden','imageUuid'])
	img_list.padding_width = 1
	img_list.align = "l"
	counter = 1
	img = {}
	for image in data['response']:
		img[counter] = [image['imageUuid'],image['name']]
		img_list.add_row([str(counter),image['name'],image['version'],image['family'],image['isTaggedGolden'],image['imageUuid']])
		counter +=1
	print(img_list)
	return img

def distribute(ip, tk, imageUuid, deviceId):
    payload = json.dumps([
		{
			"deviceUuid": deviceId,
			"imageUuid": imageUuid
		}
	])
    
    headers = {
		'X-Auth-Token': tk,
		"Content-Type": "application/json"
		}
        
    url_distribute = f'https://{ip}/dna/intent/api/v1/image/distribution'
    response = requests.post(url_distribute, headers=headers, data=payload, verify=False)
    data = response.json()
    return data['response']['taskId']

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

def get_task(taskid, token, host,counter):
    url = f'https://{host}/api/v1/task/{taskid}'
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    task_result = requests.get(url, headers=hdr, verify=False)
    progress = task_result.json()['response']['progress']
    if "Distribution" in progress:
        print('Distributing...')
    if 'activation' in progress:
        print('Activating...')
    if "completed successfully" in progress:
        print("Successfully pushed Image\n")
    else:
        if "Failure = 1" in progress:
            print("Failure\n")
            return None
        time.sleep(40)
        if counter == 25:
            print("Unable to push Image\n")
            return None
        get_task(taskid, token, host,counter+1)

def activate(ip, tk, imageUuid, deviceId):
	payload = json.dumps([
	{
		"activateLowerImageVersion": True,
		"deviceUpgradeMode": "currentlyExists",
		"deviceUuid": deviceId,
		"distributeIfNeeded": False,
		"imageUuidList": [imageUuid],
		"smuImageUuidList": []
	}
	])
    
	headers = {
		'X-Auth-Token': tk,
		"Content-Type": "application/json"
	}    
	url_activate = f'https://{ip}/dna/intent/api/v1/image/activation/device'
	response = requests.post(url_activate, headers=headers, data=payload, verify=False)
	data = response.json()
	return data['response']['taskId']

requests.packages.urllib3.disable_warnings()

with open('input.csv', newline='') as csvfile:
	csvreader = csv.reader(csvfile)
	for row in csvreader:
		dnac_ip, username, password = row
		token = get_X_auth_token(dnac_ip,username,password)

option = '0'
imageuuid = ''
deviceuuid = ''
imagename = ''

while option != '4':
    option = input('\nOptions\n1. List images\n2. Distribute image\n3. Activate image\n4. Exit\nSelect option(1,2,3 or 4):')
    if option == '1':
        img_list = list_images(dnac_ip,token)
        image = input("Enter serial no. for the image that needs to be pushed : ")
        for key in img_list:
            if int(image) == key:
                imageuuid = img_list[key][0]
                imagename = img_list[key][1]
    
    if option == '2':
        device_mgmt_ip = input("Enter IP of device to upgrade: ")	
        deviceuuid = get_deviceId(dnac_ip,token,device_mgmt_ip)
        print(f'Pushing image {imagename} to device with ip {device_mgmt_ip}.... Please wait')
        taskid = distribute(dnac_ip,token,imageuuid,deviceuuid)
        print(f'Distribution task id {taskid}\n')
        get_task(taskid,token,dnac_ip,0)
        
    if option == '3':
        print(f'Activating pushed image {imagename} on device {device_mgmt_ip}\n')
        task2 = activate(dnac_ip,token,imageuuid,deviceuuid)
        print(f'Activation task id {task2}\n')
        get_task(task2,token,dnac_ip,0)