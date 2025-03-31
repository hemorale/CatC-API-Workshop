import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os 
import urllib3
urllib3.disable_warnings()
import json

load_dotenv()

BASE_URL = 'https://' + os.getenv("DNAC_IP")
AUTH_URL = '/dna/system/api/v1/auth/token'
USERNAME = os.getenv("DNAC_USERNAME")
PASSWORD = os.getenv("DNAC_PASSWORD")
response = requests.post(BASE_URL + AUTH_URL , auth=HTTPBasicAuth(USERNAME, PASSWORD), verify= False)
token = response.json()['Token']

print("Token from Catalyst Center\n\n")
print(token)
print("\n\n")

# Get count of devices
headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
DEVICES_COUNT_URL = '/dna/intent/api/v1/network-device/count'
response = requests.get(BASE_URL + DEVICES_COUNT_URL,
                        headers=headers, verify=False)
# Print device count
print("\n\nNumber of Devices in Catalyst Center Inventoy:",response.json()['response'],"\n\n")


DEVICES_URL = '/dna/intent/api/v1/network-device'
response = requests.get(BASE_URL + DEVICES_URL, headers = headers, verify=False)


print("===============LIST OF DEVICES===========================")
for item in response.json()['response']:
    print("",item['id'], item['hostname'], item['managementIpAddress'])


DEVICES_URL = '/dna/intent/api/v1/network-device'

# Make the GET request to get all network devices
response = requests.get(BASE_URL + DEVICES_URL, headers=headers, verify=False)


print("======================Devices Details==========================")
# Check if the response is successful
if response.status_code == 200:
    devices = response.json()['response']

    # Filter and print only Catalyst 9300 devices
    found_c9300 = False
    for device in devices:
        # Check if the platformId matches Catalyst 9300 (C9300)
        if 'C9300' in device.get('platformId', ''):  # Adjust key according to your device data
            found_c9300 = True
            print(f"Device ID: {device['id']}")
            print(f"Hostname: {device['hostname']}")
            print(f"Management IP: {device['managementIpAddress']}")
            print(f"Platform ID: {device['platformId']}")
            print('-' * 50)

    if not found_c9300:
        print("No Catalyst 9300 devices found in the inventory.")
else:
    print(f"Error fetching devices: {response.status_code} - {response.text}")


print("=====================================================================")
device_id = "d5da1d6f-0afd-4e09-a916-58cad716bc03"
DEVICES_BY_ID_URL = f'/dna/intent/api/v1/network-device/{device_id}'

response = requests.get(BASE_URL + DEVICES_BY_ID_URL, headers=headers, verify=False)

# Check if the response is valid and print the formatted JSON output
if response.status_code == 200:
    # Output the JSON data in a pretty printed format
    print("Name of the device:",response.json()['response']['hostname'])
    print(json.dumps(response.json()['response'], indent=4))
else:
    print(f"Error fetching device details: {response.status_code} - {response.text}")
