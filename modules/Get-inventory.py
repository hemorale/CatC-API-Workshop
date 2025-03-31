import requests
import json
import rich
import warnings
from getpass import getpass
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

#loading dotenv file
load_dotenv()


class MyError(Exception):
    """Custom base class for exceptions"""
    pass

class AuthenticationError(MyError):
    """To be raised when authentication failure occurs"""
    pass

def get_token_for_dnac(ip_address, username, password):
    """ function to get a valid token for DNAC API
    access. Input needed is DNAC IP address, username
    and password
    """

    # build complete URL first
    token_url = "https://" + ip_address + "/dna/system/api/v1/auth/token"

    # use a POST call to get token
    warnings.filterwarnings("ignore")
    token_call = requests.post(token_url, auth=HTTPBasicAuth(username, password), headers={"Content-Type": "application/json"}, verify=False)

    # return actual token
    return(token_call.json()['Token'])

def get_network_devices_from_dnac(ip_address, token):
    """ function to get complete list of network
    devices from DNAC using DNAC's IP address and 
    the authentication token as input
    """

    # build complete URL first
    network_device_url = "https://" + ip_address + "/dna/intent/api/v1/network-device/"

    # use a GET call to return this data
    network_device_call = requests.get(network_device_url, headers={"Content-Type":"application/json", "X-Auth-Token": token}, verify=False)
    
    # return network device list
    return(network_device_call.json()['response'])

def main():
    # Use these commands to replace your own
    dnac_ip_address = {Your own "DNAC_IP"}
    dnac_username = {Your own "DNAC_USERNAME"}
    dnac_password = {Your own "DNAC_PASSWORD"}
    
    # Use this commands if you define as OS env variables
    #dnac_ip_address = os.getenv("DNAC_IP")
    #dnac_username = os.getenv("DNAC_USERNAME")
    #dnac_password = os.getenv("DNAC_PASSWORD")

    # try to get valid token for DNAC now
    try:
        token = get_token_for_dnac(dnac_ip_address, dnac_username, dnac_password)
        rich.print("[green]Retrieved token from DNAC for subsequent API calls")
    except:
        raise AuthenticationError("Error getting token for DNAC. Please try again with correct credentials\n")

    # get the list of network devices from DNAC
    dnac_device_list = get_network_devices_from_dnac(dnac_ip_address, token)

    # device list could be empty if no devices are present in DNAC
    if dnac_device_list:
        rich.print("[green]Retrieved device list from DNAC")
        rich.print(dnac_device_list)
    else:
        rich.print("[red]No devices found in DNAC inventory")

if __name__ == "__main__":
    main()