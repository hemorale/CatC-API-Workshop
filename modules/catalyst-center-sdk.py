from dnacentersdk import api
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the DNACenterAPI client with the correct parameters
dnac = api.DNACenterAPI(
    base_url=f"https://{os.getenv('DNAC_IP')}:443",  # Correctly format the URL
    username=os.getenv("DNAC_USERNAME"),            # Fetch the username from environment variables
    password=os.getenv("DNAC_PASSWORD"),verify=False             # Fetch the password from environment variables
)
print("Auth token:",dnac.access_token)

print("\n\n =======List of the devices in inventory=========")
devices = dnac.devices.get_device_list()
for device in devices.response:
    print(device.managementIpAddress)