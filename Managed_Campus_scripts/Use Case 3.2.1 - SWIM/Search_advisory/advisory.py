import requests
import csv
import urllib3
from requests.auth import HTTPBasicAuth
from datetime import datetime
import getpass
from prettytable import PrettyTable
import sys

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

def find_id_by_hierarchy(data, hierarchy):
    hierarchy_lower = hierarchy.lower()
    for site in data['response']:
        if site['siteNameHierarchy'].lower() == hierarchy_lower:
            return site['id']
    print("\nSite hierarchy not found, kindly check\n")
    sys.exit()

def send_api_request(ip_address,tk):
    url_sites = f"https://{ip_address}/dna/intent/api/v1/site"
    headers = {
    'X-Auth-Token': tk
    }
    response = requests.get(url_sites, headers=headers, verify=False)
	
    if response.status_code == 200:
        data = response.json()
        user_input = input("Please enter the Site Name Hierarchy(like Global/Area/Building/Floor) : ").strip()
        site_id = find_id_by_hierarchy(data, user_input)
    else:
        print("Unable to fetch site details")
        sys.exit()
    
    url_membership = f"https://{ip_address}/dna/intent/api/v1/membership/{site_id}"
    response2 = requests.get(url_membership, headers=headers, verify=False)
    dev = {}
    if response2.status_code == 200:
        data2 = response2.json()
        if len(data2['device'][0]['response']) == 0:
            print('No device found under this site')
            sys.exit()
        else:
            for device in data2['device'][0]['response']:
                if device['instanceUuid']:
                    dev[device['instanceUuid']] = [device['managementIpAddress'],device['softwareVersion']]
    else:
        print("Unable to fetch device details")
        sys.exit()
        
    output = []
    output.append(['Device Mgmt IP', 'Advisory', 'CVE(s)', 'Fixed Version(s)', 'Publication URL'])
    
    for key in dev:
        counter = 0
        url_advisory = f'https://{ip_address}/dna/intent/api/v1/security-advisory/device/{key}/advisory'
        response3 = requests.get(url_advisory, headers=headers, verify=False)
        if response3.status_code == 200:
            data3 = response3.json()
            for item in data3['response']:
                advid = item['advisoryId']
                cves = ', '.join(item['cves'])
                fixedVersions = item['fixedVersions']
                publicationUrl = item['publicationUrl']
                for i in fixedVersions:
                    if i == dev[key][1]:
                        fixedVersions = ', '.join(fixedVersions[i])
                if counter == 0:
                    output.append([str(dev[key][0]),str(advid),str(cves),str(fixedVersions),str(publicationUrl)])
                    counter = 1
                else:
                    output.append([' ',str(advid),str(cves),str(fixedVersions),str(publicationUrl)])
        else:
            print(f"Unable to fetch advisory details for device : {key}")

    csv_file_name = 'Advisory_output.csv'
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in output:
            writer.writerow(row)
        print(f'Output stored in {csv_file_name}')
requests.packages.urllib3.disable_warnings()

with open('input.csv', newline='') as csvfile:
	csvreader = csv.reader(csvfile)
	for row in csvreader:
		dnac_ip, username, password = row
		token = get_X_auth_token(dnac_ip,username,password)
		send_api_request(dnac_ip,token)