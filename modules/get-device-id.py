import requests
from requests.auth import HTTPBasicAuth
import urllib3
import json  # Import json module to format output

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

device_id = "d5da1d6f-0afd-4e09-a916-58cad716bc03"
DEVICES_BY_ID_URL = f'/dna/intent/api/v1/network-device/{device_id}'

response = requests.get(BASE_URL + DEVICES_BY_ID_URL, headers=headers, verify=False)

# Check if the response is valid and print the formatted JSON output
if response.status_code == 200:
    # Output the JSON data in a pretty printed format
    print(json.dumps(response.json()['response'], indent=4))
else:
    print(f"Error fetching device details: {response.status_code} - {response.text}")