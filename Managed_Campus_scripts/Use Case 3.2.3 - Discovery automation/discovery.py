import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
import json
import time
import csv

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
        
def get_credentials(ip,tk):
    url = f'https://{ip}/dna/intent/api/v1/global-credential'
    hdr = {'x-auth-token': tk, 'content-type' : 'application/json'}
    
    cred_type = ['CLI','SNMPV2_READ_COMMUNITY','SNMPV2_WRITE_COMMUNITY']
    
    creds = {}
    
    for i in range(0,3):
        parameters = {
            "credentialSubType" : cred_type[i]
        }
        response = requests.get(url, headers=hdr, params = parameters, verify=False)
    
        if response.status_code > 200:
            print ("Credentials could not be fetched.\n")
            quit()
        for items in response.json()['response']:
            creds[items['description']] = items['id']
            #print(f"\nName : {items['description']}\n Id : {items['id']}")
    return creds        

def creds_to_id(ip,tk,creds,file):
    x = open(file,'r')
    read = csv.reader(x)
    
    count = 0
    skip = []
    parameters = {}
    
    for i,row in enumerate(read, start=0):
        cli = snmpr = snmpw = True
        if i != 0:
            for key in cred_ids:
                if row[3] == key:
                    cli = False
                    row[3] = cred_ids[key]
                if row[4] == key:
                    snmpr = False
                    row[4] = cred_ids[key]
                if row[5] == key:
                    snmpw = False
                    row[5] = cred_ids[key]
            if (cli or snmpr or snmpw):
                skip.append(count)
                print(f'One of Crendentials specified for discovery named "{row[0]}" not found. Kindly Check.\n')
                continue
            parameters[count] = row
        count +=1
        
    return parameters

def discover(ip,tk,payload):
    headers = {
        'X-Auth-Token': tk,
        'content-type': 'application/json'
    }
    url_discover = f'https://{ip}/dna/intent/api/v1/discovery'
    response = requests.post(url_discover, headers=headers, data=payload, verify=False)
    data = response.json()
    #print(data)
    return data['response']

def get_task(host, token, taskid):
    url = f'https://{host}/api/v1/task/{taskid}'
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    task_result = requests.get(url, headers=hdr, verify=False)
    data = task_result.json()['response']
    #print(data)
    return data

def get_discovery_status(ip,tk,disc_id):
    url = f'https://{ip}/dna/intent/api/v1/discovery/{disc_id}'
    hdr = {'x-auth-token': tk, 'content-type' : 'application/json'}
    result = requests.get(url, headers=hdr, verify=False)
    data = result.json()['response']
    if data['discoveryCondition'] == 'Complete':
        y = data
    else:
        print('Discovery in progress...')
        time.sleep(25)
        x = get_discovery_status(ip,tk,disc_id)
    return data
    
def get_devices(ip,tk,disc_id):
    url = f'https://{ip}/dna/intent/api/v1/discovery/{disc_id}/network-device'
    hdr = {'x-auth-token': tk, 'content-type' : 'application/json'}
    result = requests.get(url, headers=hdr, verify=False)
    data = result.json()['response']
    return data

requests.packages.urllib3.disable_warnings()

with open('input.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)
        
        cred_ids = get_credentials(dnac_ip,token)
        p = creds_to_id(dnac_ip,token,cred_ids,'discover.csv')

        #print(p)
        
        for key in p:
            print(f'Starting discovery with name {p[key][0]}\n')
            payload = {
                "name": p[key][0],
                "discoveryType": p[key][1],
                "enablePasswordList": [p[key][2]],
                "globalCredentialIdList": [p[key][3], p[key][4],p[key][5]],
                "ipAddressList": p[key][6],
                "protocolOrder": p[key][7],
                "netconfPort": "830"
            }
                        
            result = discover(dnac_ip,token,json.dumps(payload))
            #print(result)
            taskId = result['taskId']
            print(f"Task Id : {taskId}")
            
            time.sleep(15)
            
            data = get_task(dnac_ip,token,taskId)
            discovery_id = data['progress']
            
            if data['isError'] == True:
                print(f'Failure : {data['failureReason']}')
                continue
            
            print(f'Discovery Id : {discovery_id}')
            time.sleep(20)
            d_status = get_discovery_status(dnac_ip,token,discovery_id)
            #time.sleep(20)
            #print(d_status)
            #if d_status['discoveryCondition'] == 'Complete':
            #    print(f"Discovery completed with status {d_status['discoveryCondition']}")
            #else:
            #    print(f"Discovery status {d_status['discoveryCondition']}")
            
            time.sleep(20)
            
            discovered_devices = get_devices(dnac_ip,token,discovery_id)
            print('Discovered Devices :-\n')
            #print(discovered_devices)
            for items in discovered_devices:
                print(f"Hostname : {items['hostname']}, Management IP Address : {items['managementIpAddress']}\n")