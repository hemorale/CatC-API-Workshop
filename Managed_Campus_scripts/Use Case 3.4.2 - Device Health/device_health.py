import requests
import csv
import urllib3
from requests.auth import HTTPBasicAuth
from datetime import datetime
import getpass

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

def send_api_request(ip_address,tk):
	output_filename = 'device_details_'+str(ip_address)+'.csv'
	url_devices = f"https://{ip_address}/dna/intent/api/v1/network-device"
	
	headers = {
		'X-Auth-Token': tk
	}
	response = requests.get(url_devices, headers=headers, verify=False)
	if response.status_code == 200:
		data = response.json()
		device_info = {}
		for item in data['response']:
			device_info[item['macAddress']] = item['id']
	else:
		print(f"Failed to retrieve device data, status code: {response.status_code}")
	
	url = f"https://{ip_address}/dna/intent/api/v1/device-detail"
	csvfile = open(output_filename, 'w', newline='')
	
	fields = ['managementIpAddr', 'nwDeviceName', 'platformId', 'nwDeviceId','softwareVersion', 'overallHealth', 'memoryScore', 'cpuScore', 'memory', 'cpu','location']
	csvwriter = csv.DictWriter(csvfile, fieldnames=fields)
	csvwriter.writeheader()
	write = csv.writer(csvfile)
	
	for key in device_info:
		parameters = {
			'searchBy':device_info[key],
			'identifier':'uuid'
		}
		
		response = requests.get(url, headers=headers, params=parameters, verify=False)
		data = response.json()
		temp = []
		for key in fields:
			if key in data['response']:
				temp.append(data['response'][key])
			else:
				temp.append('')
		write.writerow(temp)
	print(f'Output stored in "{output_filename}"')

requests.packages.urllib3.disable_warnings()

with open('input.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)
        send_api_request(dnac_ip,token)