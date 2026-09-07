# Micro:bit v2 Multi-User Generative AI Bridge Options

Connecting multiple physical **BBC micro:bit v2** units to a centralized generative AI endpoint requires shifting from a simple local serial bridge to a **multi-user web architecture**. Because a USB cable creates a **1:1 hardware connection**, your hosted code must function as a web server that aggregates requests from remote users.

---

## Architecture Overview

Instead of talking directly to your USB port, your hosted server exposes a secure API endpoint. Users relay their micro:bit commands across the internet to your server, which safely handles the Claude (Anthropic) API credentials.

```
[User 1 micro:bit] 🔌 USB ➡️ [User 1 Browser/Script] 🌐 Internet \
                                                               ➡️ [Your Hosted Flask Server] ➡️ [Claude API]
[User 2 micro:bit] 🔌 USB ➡️ [User 2 Browser/Script] 🌐 Internet /
```

---

## Option A: The "No-Local-Python" Web Browser Method (Recommended)

This method provides the friction-free user experience. Users plug their micro:bits into their computers, open a web browser (Chrome or Edge), and click connect. The browser leverages the native **Web Serial API** to bridge the micro:bit to your hosted cloud server.

### 1. Centralized Cloud Server (`app.py`)
Deploy this backend script to a cloud hosting platform (like Render, Railway, or AWS). Set your `ANTHROPIC_API_KEY` as a secure environment variable on the platform.

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from anthropic import Anthropic
import os

app = Flask(__name__)
CORS(app) # Permissive CORS allows user browsers to hit your hosted server

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.json
    prompt = data.get("prompt", "")
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": f"{prompt} Keep your answer extremely short (under 60 characters)."}
            ]
        )
        return jsonify({"response": message.content.text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2. User Frontend Webpage (`index.html`)
Host this HTML file on your web server or via GitHub Pages. When users navigate here, their browser communicates locally with the micro:bit and relays prompts to your cloud endpoint.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Multi-User Micro:bit AI Hub</title>
</head>
<body>
    <button id="connect">Connect Micro:bit</button>
    <p id="status">Status: Disconnected</p>

    <script>
    let port;
    document.getElementById('connect').addEventListener('click', async () => {
        try {
            // Requesting hardware access via browser Web Serial API
            port = await navigator.serial.requestPort();
            await port.open({ baudRate: 115200 });
            document.getElementById('status').innerText = "Status: Connected!";
            
            const decoder = new TextDecoderStream();
            port.readable.pipeTo(decoder.writable);
            const reader = decoder.readable.getReader();

            while (true) {
                const { value, done } = await reader.read();
                if (value && value.includes("GEN_AI_REQUEST:")) {
                    let prompt = value.replace("GEN_AI_REQUEST:", "").trim();
                    document.getElementById('status').innerText = "Sending prompt to cloud AI...";
                    
                    // Route to your deployed Flask application URL
                    let res = await fetch('https://your-hosted-server.com/ask-ai', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: prompt })
                    });
                    let data = await res.json();
                    
                    // Respond back down the local serial port
                    const encoder = new TextEncoder();
                    const writer = port.writable.getWriter();
                    await writer.write(encoder.encode(data.response + "\n"));
                    writer.releaseLock();
                    document.getElementById('status').innerText = "Response sent to Micro:bit!";
                }
            }
        } catch (err) {
            document.getElementById('status').innerText = "Error: " + err;
        }
    });
    </script>
</body>
</html>
```

---

## Option B: The "Multi-Tenant" Local Client Method

If you prefer to avoid web pages, users keep a micro-sized Python runner file locally on their computers. This file listens to their USB port and proxies data to your centralized server.

### 1. Centralized Cloud Server
The server structure remains **identical to Option A**.

### 2. User Local Script (`client.py`)
Each user runs this script on their local system. They only change the `MICROBIT_PORT` value to match their specific system assignment (`COM3`, `/dev/tty.usbmodem101`, etc.).

```python
import serial
import requests
import time

# User configures their personal hardware port mapping
MICROBIT_PORT = 'COM3' 
SERVER_URL = "https://your-hosted-server.com/ask-ai"

try:
    ser = serial.Serial(MICROBIT_PORT, 115200, timeout=1)
    print(f"Listening to Micro:bit on {MICROBIT_PORT}...")
except Exception as e:
    print(f"Connection failure: {e}")
    exit()

while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("GEN_AI_REQUEST:"):
                prompt = line.replace("GEN_AI_REQUEST:", "").strip()
                print(f"Forwarding prompt to Hosted Bridge: {prompt}")
                
                # Make HTTP POST request to your managed server
                response = requests.post(SERVER_URL, json={"prompt": prompt})
                ai_response = response.json().get("response", "Error retrieving AI text")
                
                # Push answer back to physical device
                ser.write((ai_response + "\n").encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(0.1)
```

---

## Important Operational Notes

* **API Budgeting & Guardrails:** Your centralized Anthropic account pays for all user interactions. Ensure you configure tight usage limits inside your Anthropic console to prevent run-away classroom costs.
* **Rate-Limit Mitigation:** If 20–30 micro:bits push requests at the exact same moment, Claude might reply with a `429 Too Many Requests` error. Implementing basic exponential backoff in your Flask server can gracefully queue bursts.
