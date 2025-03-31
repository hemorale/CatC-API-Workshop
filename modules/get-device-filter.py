import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings()
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Define base URL and authentication endpoint
BASE_URL = 'https://' + os.getenv("DNAC_IP")
AUTH_URL = '/dna/system/api/v1/auth/token'
USERNAME = os.getenv("DNAC_USERNAME")
PASSWORD = os.getenv("DNAC_PASSWORD")

# Obtain the authentication token from Cisco DNA Center
response = requests.post(BASE_URL + AUTH_URL, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)

# Check if the token was retrieved successfully
if response.status_code == 200:
    token = response.json()['Token']
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
else:
    print(f"Error obtaining token: {response.status_code} - {response.text}")
    exit()

# Endpoint to get all network devices
DEVICES_URL = '/dna/intent/api/v1/network-device'

# Make the GET request to get all network devices
response = requests.get(BASE_URL + DEVICES_URL, headers=headers, verify=False)

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