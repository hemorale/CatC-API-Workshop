import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
import json
import time
from prettytable import PrettyTable
import datetime
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
        
def get_backups(ip,tk):
    url = f'https://{ip}/api/system/v1/maglev/backup'
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    response = requests.get(url,headers=hdr,verify=False)
    
    if response.status_code > 200:
        print ("Backup information could not be fetched.\n")
        quit()
    print('\nFetching Backup details...\n')
    return response.json()
    
requests.packages.urllib3.disable_warnings()

with open('input.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)

backup_details = PrettyTable(['Backup ID','Description','Status','Compatible','Backup Time','Backup Size (GB)','Age (days)'])
backup_details.padding_width = 1
backup_details.align = 'l'

backup = get_backups(dnac_ip,token)

for backup in backup['response']:
    details_list = []
    details_list.append(backup['backup_id'])
    details_list.append(backup['description'])
    details_list.append(backup['status'])
    details_list.append(backup['compatible'])
        
    convert_time = datetime.datetime.fromtimestamp(backup['start_timestamp'])
    backup_time = convert_time.strftime('%Y-%m-%d %H:%M:%S')
    details_list.append(backup_time)
    
    backup_size_gb = round(backup['backup_size'] / 1000000000,2)
    details_list.append(backup_size_gb)
    
    backup_age = round((time.time() - backup['start_timestamp']) / 86400,0)
    backup_age = int(backup_age)
    details_list.append(backup_age)    
    backup_details.add_row(details_list)
    
print(backup_details)

x = open('backup_status.txt','w')
x.write(str(backup_details))
x.close()