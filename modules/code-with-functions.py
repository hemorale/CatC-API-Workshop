import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import json
import urllib3

# Disable SSL warnings (if you're using self-signed certificates or for testing purposes)
urllib3.disable_warnings()

# Load environment variables from a .env file
load_dotenv()

# Set the base URL for DNAC API
BASE_URL = 'https://' + os.getenv("DNAC_IP")
AUTH_URL = '/dna/system/api/v1/auth/token'

# Fetch the credentials from environment variables
USERNAME = os.getenv("DNAC_USERNAME")
PASSWORD = os.getenv("DNAC_PASSWORD")

# Function to get an authentication token
def get_auth_token():
    response = requests.post(
        BASE_URL + AUTH_URL, 
        auth=HTTPBasicAuth(USERNAME, PASSWORD), 
        verify=False
    )
    if response.status_code == 200:
        token = response.json()['Token']
        print("Token from Catalyst Center\n\n", token, "\n\n")
        return token
    else:
        print(f"Error fetching auth token: {response.status_code} - {response.text}")
        return None

# Function to get the count of devices
def get_device_count(token):
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    DEVICES_COUNT_URL = '/dna/intent/api/v1/network-device/count'
    response = requests.get(
        BASE_URL + DEVICES_COUNT_URL, 
        headers=headers, 
        verify=False
    )
    if response.status_code == 200:
        count = response.json()['response']
        print("\n\nNumber of Devices in Catalyst Center Inventory:", count, "\n\n")
        return count
    else:
        print(f"Error fetching device count: {response.status_code} - {response.text}")
        return None

# Function to get the list of devices
def list_devices(token):
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    DEVICES_URL = '/dna/intent/api/v1/network-device'
    response = requests.get(BASE_URL + DEVICES_URL, headers=headers, verify=False)
    
    if response.status_code == 200:
        devices = response.json()['response']
        print("===============LIST OF DEVICES===========================")
        for item in devices:
            print("", item['id'], item['hostname'], item['managementIpAddress'])
    else:
        print(f"Error fetching devices: {response.status_code} - {response.text}")

# Function to filter and list details of Catalyst 9300 devices
def list_c9300_devices(token):
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    DEVICES_URL = '/dna/intent/api/v1/network-device'
    response = requests.get(BASE_URL + DEVICES_URL, headers=headers, verify=False)

    if response.status_code == 200:
        devices = response.json()['response']
        found_c9300 = False
        print("======================Devices Details==========================")
        for device in devices:
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
        print(f"Error fetching device details: {response.status_code} - {response.text}")

# Function to get the details of a specific device by ID
def get_device_details_by_id(token, device_id):
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    DEVICES_BY_ID_URL = f'/dna/intent/api/v1/network-device/{device_id}'
    
    response = requests.get(BASE_URL + DEVICES_BY_ID_URL, headers=headers, verify=False)
    
    if response.status_code == 200:
        print("Name of the device:", response.json()['response']['hostname'])
        print(json.dumps(response.json()['response'], indent=4))
    else:
        print(f"Error fetching device details: {response.status_code} - {response.text}")

# Main function to orchestrate the process
def main():
    token = get_auth_token()
    
    if token:
        # Get device count
        get_device_count(token)

        # List all devices
        list_devices(token)

        # List Catalyst 9300 devices
        list_c9300_devices(token)

        # Get details of a specific device (using an example device ID)
        device_id = "d5da1d6f-0afd-4e09-a916-58cad716bc03"
        get_device_details_by_id(token, device_id)

if __name__ == '__main__':
    main()