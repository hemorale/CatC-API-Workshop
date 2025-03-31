import requests
import json
import warnings
from requests.auth import HTTPBasicAuth
from getpass import getpass
from dotenv import load_dotenv
import os

# Disable insecure request warnings
warnings.filterwarnings("ignore")

#loading dotenv file
load_dotenv()

# Function to get the authentication token
def get_dnac_token(dnac_ip, username, password):
    token_url = f"https://{dnac_ip}/dna/system/api/v1/auth/token"
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(token_url, auth=HTTPBasicAuth(username, password), headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()["Token"]
    else:
        raise Exception(f"Failed to get token: {response.text}")

# Function to get site information from DNAC
def get_dnac_sites(dnac_ip, token):
    url = f"https://{dnac_ip}/dna/intent/api/v1/site"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": token
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve site info: {response.text}")

# Main function to execute the script
def main():
    # Use these commands to replace your own
    dnac_ip_address = {Your own "DNAC_IP"}
    dnac_username = {Your own "DNAC_USERNAME"}
    dnac_password = {Your own "DNAC_PASSWORD"}
    
    # Use this commands if you define as OS env variables
    #dnac_ip_address = os.getenv("DNAC_IP")
    #dnac_username = os.getenv("DNAC_USERNAME")
    #dnac_password = os.getenv("DNAC_PASSWORD")

    try:
        # Get token from DNAC
        token = get_dnac_token(dnac_ip, dnac_username, dnac_password)
        print("Successfully retrieved token.")

        # Get site information
        site_info = get_dnac_sites(dnac_ip, token)
        print("Successfully retrieved site information:")
        print(json.dumps(site_info, indent=4))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
