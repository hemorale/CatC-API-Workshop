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
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%d-%b-%Y %H:%M')

    url = f'https://{ip_address}/dna/intent/api/v1/diagnostics/system/performance'
    headers = {
        'X-Auth-Token': tk
        }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        
        with open('system_performance_'+str(ip_address)+'.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date/Time','HostName', 'CPU Utilization', 'Memory Utilization', 'Network TX Rate', 'Network RX Rate'])
            writer.writerow([
                formatted_datetime,
                data['hostName'],
                data['kpis']['cpu']['utilization'],
                data['kpis']['memory']['utilization'],
                data['kpis']['network tx_rate']['utilization'],
                data['kpis']['network rx_rate']['utilization']
            ])
        
        print("Data has been saved to system_performance_"+str(ip_address)+".csv")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

requests.packages.urllib3.disable_warnings()

with open('input.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        dnac_ip, username, password = row
        token = get_X_auth_token(dnac_ip,username,password)
        send_api_request(dnac_ip,token)