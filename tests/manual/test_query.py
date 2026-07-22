import requests
import json

url = "http://localhost:3000/api/stream"
data = {
    "query": "mujhe laptop kharidne ka process batao?",
    "session_id": "test-1234",
    "advanced_mode": False
}

print(f"Sending query to {url}...")
try:
    response = requests.post(url, json=data, stream=True, timeout=60)
    print(f"Status Code: {response.status_code}")
    
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
