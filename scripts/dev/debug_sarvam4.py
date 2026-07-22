import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SARVAM_API_KEY')

url = "https://api.sarvam.ai/v1/chat/completions"
headers = {
    "api-subscription-key": api_key,
    "Content-Type": "application/json"
}

# Simulate the exact prompt with a lot of dummy context
context_text = "Dummy context " * 500
system_msg = "You are a procurement assistant.\n\n=== LANGUAGE LOCK ===\nThe user's question is in ENGLISH. You MUST write the ENTIRE response in ENGLISH ONLY. ABSOLUTELY NO HINDI. Do not use Hindi words or scripts. Use ONLY the English headings: 💡 Answer, 📋 Process, Rule/Provision:, Explanation:, 📘 Source:."
user_msg = f"Context:\n{context_text}\n\nQuestion: In chhatisgarh ,what are different ways of govt. procurement\n\n>>> CRITICAL INSTRUCTION: You MUST write the ENTIRE response in ENGLISH ONLY. ABSOLUTELY NO HINDI ALLOWED. Do not write in Hindi even if the prompt contains Indian names. Use the English headings (💡 Answer / 📋 Process / 📘 Source).\n\nAnswer:"

data = {
    "model": "sarvam-30b",
    "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    "temperature": 0,
    "stream": True
}

print("Making raw POST request...")
with httpx.stream("POST", url, headers=headers, json=data, timeout=60) as r:
    print(f"Status: {r.status_code}")
    print(f"Headers: {r.headers}")
    print("Content:")
    for chunk in r.iter_text():
        print(chunk, end="")
print("\nDone.")
