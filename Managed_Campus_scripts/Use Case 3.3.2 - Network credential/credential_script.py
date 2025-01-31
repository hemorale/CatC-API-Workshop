import requests
import csv
import urllib3
from requests.auth import HTTPBasicAuth
import json
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


def create_cred(ip,tk,inputfile):
    create_cli_cred_url = f'https://{ip}/dna/intent/api/v1/global-credential/cli'
    create_snmp_read_url = f'https://{ip}/dna/intent/api/v1/global-credential/snmpv2-read-community'
    create_snmp_write_url = f'https://{ip}/dna/intent/api/v1/global-credential/snmpv2-write-community'
    headers = {
        'X-Auth-Token': token,
        'content-type': 'application/json'
    }
    
    with open(inputfile,'r') as file:
        lines = file.readlines()
        counter = 0
        for line in lines:
            elements = line.split(',')
            if elements[0] == 'cli_credential':
                cli_description = elements[1]
                cli_username = elements[2]
                cli_password = elements[3]
                cli_enablePassword = elements[4]
            if elements[0] == 'snmpV2cRead':
                snmpV2cRead_description = elements[1]
                snmpV2cRead_readCommunity = elements[2]
            if elements[0] == 'snmpV2cWrite':
                snmpV2cWrite_description = elements[1]
                snmpV2cWrite_writeCommunity = elements[2]
            
        cli_payload = [
                {
                    "description": cli_description,
                    "username": cli_username,
                    "password": cli_password,
                    "enablePassword": cli_enablePassword
                }
            ]
        
        snmp_read_payload = [
                {
                    "description": snmpV2cRead_description,
                    "readCommunity": snmpV2cRead_readCommunity
                }
            ]
        
        snmp_write_payload = [
                {
                    "description": snmpV2cWrite_description,
                    "writeCommunity": snmpV2cWrite_writeCommunity
                }
            ]
        
        print('Creating CLI credentials\n')
        cli_response = requests.post(create_cli_cred_url, headers=headers, data=json.dumps(cli_payload), verify=False)
        print('Creating SNMP Read credentials\n')
        snmp_read_response = requests.post(create_snmp_read_url, headers=headers, data=json.dumps(snmp_read_payload), verify=False)
        print('Creating SNMP Write credentials\n')
        snmp_write_response = requests.post(create_snmp_write_url, headers=headers, data=json.dumps(snmp_write_payload), verify=False)
        
        cli_res = cli_response.json()['response']
        snmp_read_res = snmp_read_response.json()['response']
        snmp_write_res = snmp_write_response.json()['response']
        
        cli_taskid = cli_res['taskId']
        snmp_read_taskid = snmp_read_res['taskId']
        snmp_write_taskid = snmp_write_res['taskId']
        
    return cli_taskid,snmp_read_taskid,snmp_write_taskid        

def get_task(taskid, host, tk):
    url = f'https://{host}/dna/intent/api/v1/task/{taskid}'
    hdr = {'x-auth-token': tk}
    task_result = requests.get(url, headers=hdr, verify=False)
    progress = task_result.json()['response']['progress']
    return progress

def find_id_by_hierarchy(data, hierarchy):
    hierarchy_lower = hierarchy.lower()
    for site in data['response']:
        if site['siteNameHierarchy'].lower() == hierarchy_lower:
            return site['id']
    print("\nSite hierarchy not found, kindly check\n")
    sys.exit()

def get_site(ip_address,tk):
    url_sites = f"https://{ip_address}/dna/intent/api/v1/site"
    headers = {
    'X-Auth-Token': tk
    }
    response = requests.get(url_sites, headers=headers, verify=False)
    
    if response.status_code == 200:
        data = response.json()
        user_input = input("Please enter the Site Name Hierarchy(like Global/Area/Building/Floor) where credentials need to be applied: ").strip()
        site_id = find_id_by_hierarchy(data, user_input)
    else:
        print("Unable to fetch site details")
        sys.exit()
    
    return site_id

def push_creds(ip,tk,site,cli,snmpr,snmpw):
    url_push_creds = f"https://{ip}/dna/intent/api/v1/credential-to-site/{site}"
    headers = {
    'X-Auth-Token': tk
    }
    
    payload = {
        "cliId": cli,
        "snmpV2ReadId": snmpr,
        "snmpV2WriteId": snmpw
    }
       
    response = requests.post(url_push_creds, headers=headers, data=json.dumps(payload), verify=False)
    data = response.json()
    return data

def get_execution_status(execid,ip,tk):
    url_exec = f"https://{ip}/dna/platform/management/business-api/v1/execution-status/{execid}"
    headers = {
        'X-Auth-Token': tk
    }
    response = requests.get(url_exec, headers=headers, verify=False)
    data = response.json()
    return data
    
requests.packages.urllib3.disable_warnings()

with open('input.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)
        cli,snmpR,snmpW = create_cred(dnac_ip,token,'cred_input.csv')
        
        cli_progress = get_task(cli,dnac_ip,token)
        snmpR_progress = get_task(snmpR,dnac_ip,token)
        snmpW_progress = get_task(snmpW,dnac_ip,token)
        counter = 0  
        if 'failed' in cli_progress:
            print('Failed to create CLI credentials.')
        else:
            print(f'CLI credential created, Id : {cli_progress}')
            counter +=1
            
        if 'failed' in snmpR_progress:
            print('Failed to create SNMP Read credentials.')
        else:
            print(f'SNMP Read credential created, Id : {snmpR_progress}')
            counter +=1
        
        if 'failed' in snmpW_progress:
            print('Failed to create SNMP Write credentials.')
        else:
            print(f'SNMP Write credential created, Id : {snmpW_progress}')
            counter +=1
        
        if counter == 3:
            siteId = get_site(dnac_ip,token)
            push_task = push_creds(dnac_ip,token,siteId,cli_progress,snmpR_progress,snmpW_progress)
            execution_id = push_task['executionId']
            
            exec_status = get_execution_status(execution_id,dnac_ip,token)
            print(f"Status : {exec_status['status']}\nSync Response : {exec_status['bapiSyncResponse']}\n")
            
        else:
            print('One of the credentials didn''t get created')         