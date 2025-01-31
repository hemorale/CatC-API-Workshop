import json
from urllib.parse import urlparse
import csv
import requests
from requests.auth import HTTPBasicAuth
import warnings
import urllib3
import time

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
        
def find_id_by_hierarchy(data, hierarchy):
    hierarchy_lower = hierarchy.lower()
    for site in data['response']:
        if site['siteNameHierarchy'].lower() == hierarchy_lower:
            return site['id']
    print("\nSite hierarchy not found, kindly check\n")
    sys.exit()

def site_select(ip_address,tk):
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
    
    #print(site_id)
    
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
                    dev[device['instanceUuid']] = [device['hostname'],device['managementIpAddress']]
    else:
        print("Unable to fetch device details")
        sys.exit()
    return dev

output_file = open('device_list.txt','w')

warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)
with open('input.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)

        devices = site_select(dnac_ip,token)
        #print(devices)
        print(f'\nDevices in site as follows. Output also written to file "device_list.txt".')
        for key in devices:
            output_file.write(str(key)+','+str(devices[key][0])+','+str(devices[key][1])+'\n')
            print(devices[key][0])