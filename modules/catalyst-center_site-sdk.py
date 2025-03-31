import os
from dnacentersdk import DNACenterAPI
import json
from rich.console import Console
from time import sleep
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize console for rich printing
console = Console()

# Function to create a new site (area, building, floor) based on the provided JSON structure
def create_new_site(site):
    try:
        # Debug: Print the site JSON to check its structure
        console.print(f"[bold blue] Site JSON Structure: {json.dumps(site, indent=4)}")

        # Check the type and create the site accordingly
        if site['type'] == 'area' and 'area' in site['site']:
            site_name = site['site']['area']['name']
        elif site['type'] == 'building' and 'building' in site['site']:
            site_name = site['site']['building']['name']
        elif site['type'] == 'floor' and 'floor' in site['site']:
            site_name = site['site']['floor']['name']
        else:
            console.print(f"[bold red] Error: 'name' field missing or invalid structure in site: {json.dumps(site, indent=4)}")
            return

        # Create the site in DNAC
        resp = dnac.sites.create_site(payload=site)
        console.print(f"[bold green] {site_name} Created Successfully!")
        sleep(2)  # Give time for DNAC to process the creation
        
    except Exception as e:
        console.print(f"[bold red] Error: {str(e)}")

# Function to render site information and create sites
def render_site_info():
    console.print("[bold red] Building New Site...")
    
    # Load and create area
    with open('sites/area.json', 'r') as outfile:
        area = json.load(outfile)
        create_new_site(area)
    
    # Load and create building
    with open('sites/bldg.json', 'r') as outfile:
        building = json.load(outfile)
        create_new_site(building)
    
    # Load and create floor
    with open('sites/floor.json', 'r') as outfile:
        floor = json.load(outfile)
        create_new_site(floor)

# Main entry point for the script
if __name__ == '__main__':
    """
    Fetching credentials from environment variables
    """
    # Fetch DNAC credentials from environment variables
    dnac_ip = os.getenv("DNAC_IP")  # IP address of your DNAC
    dnac_username = os.getenv("DNAC_USERNAME")  # Username for DNAC
    dnac_password = os.getenv("DNAC_PASSWORD")  # Password for DNAC
    
    # Validate if the environment variables are set
    if not dnac_ip or not dnac_username or not dnac_password:
        console.print("[bold red]Error: Missing one or more environment variables (DNAC_IP, DNAC_USERNAME, DNAC_PASSWORD).")
        exit(1)

    # Initialize DNAC API with credentials from environment variables
    try:
        dnac = DNACenterAPI(
            username=dnac_username,
            password=dnac_password,
            base_url=f"https://{dnac_ip}:443",
            verify=False  # Set to True if using proper certificates in production
        )
        console.print("[bold green] DNAC API initialized successfully!")
    except Exception as e:
        console.print(f"[bold red] Error initializing DNAC API: {str(e)}")
        exit(1)

    # Render site info and create the sites
    render_site_info()