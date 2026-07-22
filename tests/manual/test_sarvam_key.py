import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('SARVAM_API_KEY')

print(f"Testing Sarvam API Key: {api_key[:5]}...{api_key[-5:]}" if api_key else "No key found")

try:
    response = requests.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers={
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        },
        json={
            "model": os.getenv('SARVAM_MODEL', 'sarvam-105b'),
            "messages": [{"role": "user", "content": "Hello!"}],
            "temperature": 0.1,
            "max_tokens": 10
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        print("Success! The API key is working.")
    else:
        print("Failed! The API key might be invalid or there is an issue with the API.")
        
except Exception as e:
    print(f"Error connecting to Sarvam API: {e}")
