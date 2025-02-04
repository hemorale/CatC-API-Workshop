### **Exposing Your Flask Webhook to the Internet Using `ngrok`**  

If you want to expose your Flask server to the internet and receive `POST` requests from external services, you can use `ngrok`, a tunneling tool that provides a public URL for your local server.

---

## **Step-by-Step Guide to Using `ngrok` with Flask**

### **1. Install `ngrok`**
- **On macOS (using Homebrew):**  
  ```bash
  brew install ngrok/ngrok/ngrok
  ```
- **On Linux:**  
  ```bash
  wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
  unzip ngrok-stable-linux-amd64.zip
  sudo mv ngrok /usr/local/bin
  ```
- **On Windows:**  
  - Download `ngrok` from [https://ngrok.com/download](https://ngrok.com/download).  
  - Extract and add it to your system’s `PATH`.

---

### **2. Authenticate Your `ngrok` Account**
Before using `ngrok`, you need to authenticate it with an API token (only required once).

1. Sign up at [https://ngrok.com/signup](https://ngrok.com/signup) (free plan available).
2. Copy your authentication token from your ngrok dashboard.
3. Run the following command (replace `YOUR_AUTH_TOKEN` with your actual token):
   ```bash
   ngrok authtoken YOUR_AUTH_TOKEN
   ```

---

### **3. Start Your Flask Server Locally**
Run your Flask webhook server in one terminal:
```bash
python Webhook_server.py
```
Make sure Flask is running on port **5000**.

---

### **4. Start `ngrok` to Expose Your Local Server**
In a **new terminal**, run:
```bash
ngrok http 5000
```
This will create a secure public URL that looks like:
```
https://random-name.ngrok.io
```
Your Flask server is now accessible from the internet!

---

### **5. Test Your Public Webhook URL**
Now, you can send a `POST` request to your `ngrok` URL:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"eventId": "123", "type": "alert"}' https://random-name.ngrok.io/webhook
```
Or, configure your external service to send requests to this public URL.

---

### **6. Keep `ngrok` Running**
As long as `ngrok` is running in your terminal, your Flask server will remain accessible. If you close the terminal, the tunnel will stop, and you’ll need to restart `ngrok` to get a new public URL.

---
