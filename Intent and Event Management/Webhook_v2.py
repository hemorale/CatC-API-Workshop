from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import json

app = Flask(__name__)
auth = HTTPBasicAuth()

# Define valid credentials for Basic Authentication
users = {
    "admin": "CiscoLive100%"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

@app.route('/dna/events/', methods=['POST'])
@auth.login_required
def receive_events():
    data = request.json
    print("Received POST request with data:", json.dumps(data, indent=4))
    return jsonify({"message": "Data received successfully"}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
