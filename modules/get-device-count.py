import requests
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings()
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = 'https://' + os.getenv("DNAC_IP")
AUTH_URL = '/dna/system/api/v1/auth/token'
USERNAME = os.getenv("DNAC_USERNAME")
PASSWORD = os.getenv("DNAC_PASSWORD")

response = requests.post(BASE_URL + AUTH_URL, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
token = response.json()['Token']
headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}

DEVICES_COUNT_URL = '/dna/intent/api/v1/network-device/count'
response = requests.get(BASE_URL + DEVICES_COUNT_URL, headers = headers, verify=False)
print(response.json())