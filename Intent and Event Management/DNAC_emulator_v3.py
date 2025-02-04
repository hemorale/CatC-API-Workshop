from flask import Flask, request, jsonify
import secrets
import time
import json
import threading
import requests
from requests.auth import HTTPBasicAuth
import base64


app = Flask(__name__)

# Variables for periodic POST requests
send_events_flag = 0 # 1 - turns on the POST messages to be sent out from the event collection
post_interval = 10  # Default interval (in seconds)

# Define valid credentials
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'CiscoLive100%'

# Store the token and its expiry time
token_info = {
    "token": None,
    "expiry": None
}

def send_periodic_events():
    global send_events_flag, post_interval
    while True:
        if send_events_flag:
            try:
                with open('events_collection_verified.json', 'r') as file:
                    events_data = json.load(file)

                # Encode the credentials
                credentials = f"{VALID_USERNAME}:{VALID_PASSWORD}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()

                # Set up headers with Basic Authentication
                headers = {
                    'Authorization': f'Basic {encoded_credentials}',
                    'content-type': 'application/json'
                }

                # Sending POST request
                post_url = 'http://127.0.0.1:5001/dna/events/'  # Update to your target server's URL
                response = requests.post(post_url, json=events_data, headers=headers, verify=True)
                print("POST request sent. Status Code:", response.status_code)
            except Exception as e:
                print("Error sending POST request:", str(e))
        time.sleep(post_interval)

# Start the thread for sending events
threading.Thread(target=send_periodic_events, daemon=True).start()


@app.route('/dna/system/api/v1/auth/token', methods=['POST'])
def generate_token():
    username = request.json.get('username')
    password = request.json.get('password')

    # Check if the provided credentials match the valid credentials
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        # Generate a random token
        token = secrets.token_urlsafe(64)
        token_info["token"] = token
        token_info["expiry"] = time.time() + 3600  # Token expires after 60 minutes
        return jsonify({"Token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401  # Unauthorized

@app.route('/dna/intent/api/v1/issues', methods=['GET'])
def get_issues():
    token = request.headers.get('x-auth-token')
    if token != token_info["token"] or time.time() > token_info["expiry"]:
        return jsonify({"error": "Invalid or expired token"}), 401

    try:
        # Load issues from the JSON file
        with open('issues_collection_verified.json', 'r') as file:
            issues_data = json.load(file)
        return jsonify(issues_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/control/events', methods=['POST'])
def control_events():
    global send_events_flag, post_interval
    send_events_flag = request.json.get('send_events_flag', 0)
    post_interval = request.json.get('interval', 10)
    return jsonify({"message": "Event control updated"}), 200

@app.route('/dna/intent/api/v1/issue-enrichment-details', methods=['GET'])
def issue_enrichment_details():
    token = request.headers.get('x-auth-token')
    if token != token_info["token"] or time.time() > token_info["expiry"]:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    entity_type = request.headers.get('entity-type')
    entity_value = request.headers.get('entity-value')
    print("entity_type: ", entity_type)
    print("entity_value:", entity_value)

    try:
        with open('Issues_enrichment_verified.json', 'r') as file:
            issues_data = json.load(file)

            if not entity_type or not entity_value:
                return jsonify({"error": "Required headers missing (entity-type and entity-value)"}), 400
            
            if entity_type != "issue_id":
                return jsonify({"error": "Invalid entity_type. It must be 'issue_id'"}), 400
            
            for item in issues_data:
                issue_details = item.get('issueDetails', {})
                issues_list = issue_details.get('issue', [])
                for issue in issues_list:
                    if issue["issueId"] == entity_value:
                        print(issue["issueId"])
                        return jsonify(issue), 200
                    else: 
                        return jsonify({"error": "Issue not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
