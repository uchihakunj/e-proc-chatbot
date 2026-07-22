import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('SARVAM_API_KEY')
model = os.getenv('SARVAM_MODEL', 'sarvam-30b')

print(f"Testing Sarvam SDK with model: {model}")
print(f"API Key: {api_key[:5]}...{api_key[-5:]}" if api_key else "No key found")

try:
    from sarvamai import SarvamAI
    client = SarvamAI(api_subscription_key=api_key)
    
    response = client.chat.completions(
        model=model,
        messages=[
            {"role": "user", "content": "What is the capital of India?"}
        ],
        temperature=0
    )
    
    content = response.choices[0].message.content if hasattr(response, 'choices') else str(response)
    print("Success! SDK works.")
    print("Response:")
    print(content)
except Exception as e:
    print(f"Error testing Sarvam SDK: {e}")
