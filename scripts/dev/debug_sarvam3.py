import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SARVAM_API_KEY')
model = os.getenv('SARVAM_MODEL', 'sarvam-30b')

from sarvamai import SarvamAI
client = SarvamAI(api_subscription_key=api_key)

system_msg = "You are a procurement assistant.\n\n=== LANGUAGE LOCK ===\nThe user's question is in ENGLISH. You MUST write the ENTIRE response in ENGLISH ONLY. ABSOLUTELY NO HINDI. Do not use Hindi words or scripts. Use ONLY the English headings: 💡 Answer, 📋 Process, Rule/Provision:, Explanation:, 📘 Source:."
user_msg = "Context: [some context]\n\nQuestion: In chhatisgarh ,what are different ways of govt. procurement\n\n>>> CRITICAL INSTRUCTION: You MUST write the ENTIRE response in ENGLISH ONLY. ABSOLUTELY NO HINDI ALLOWED. Do not write in Hindi even if the prompt contains Indian names. Use the English headings (💡 Answer / 📋 Process / 📘 Source).\n\nAnswer:"

print("Testing exact prompt stream=True...")
response = client.chat.completions(
    model=model,
    messages=[
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    temperature=0,
    stream=True
)

app_has_output = False
for chunk in response:
    if not hasattr(chunk, 'choices') or not chunk.choices:
        continue
    
    delta = chunk.choices[0].delta
    if getattr(delta, 'reasoning_content', None):
        pass # print("R", end='', flush=True)
    if delta.content:
        app_has_output = True
        print(delta.content, end='', flush=True)
        
print(f"\nFinal app_has_output: {app_has_output}")
