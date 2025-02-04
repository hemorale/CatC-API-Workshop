from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
import uvicorn

app = FastAPI()
security = HTTPBasic()

# Define valid credentials for Basic Authentication
users = {
    "admin": "CiscoLive100%"
}

def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if username in users and users[username] == password:
        return credentials.username
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.post('/dna/events/')
async def receive_events(request: Request, username: str = Depends(verify_password)):
    data = await request.json()
    print("Received POST request with data:", json.dumps(data, indent=4))
    return {"message": "Data received successfully"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5001)
