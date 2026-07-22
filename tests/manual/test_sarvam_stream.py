import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SARVAM_API_KEY')
model = os.getenv('SARVAM_MODEL', 'sarvam-30b')

try:
    from sarvamai import SarvamAI
    client = SarvamAI(api_subscription_key=api_key)
    
    print("Testing stream=True...")
    response = client.chat.completions(
        model=model,
        messages=[{"role": "user", "content": "Count from 1 to 5"}],
        temperature=0,
        stream=True
    )
    
    print(f"Response type: {type(response)}")
    for chunk in response:
        print(chunk)
except Exception as e:
    print(f"Exception: {e}")
