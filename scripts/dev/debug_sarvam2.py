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
        messages=[{"role": "user", "content": "In chhatisgarh ,what are different ways of govt. procurement"}],
        temperature=0,
        stream=True
    )
    
    app_has_output = False
    for chunk in response:
        if not hasattr(chunk, 'choices') or not chunk.choices:
            continue
        
        delta = chunk.choices[0].delta
        if getattr(delta, 'reasoning_content', None):
            print(f"Reasoning: {delta.reasoning_content}", end='', flush=True)
            
        if delta.content:
            app_has_output = True
            print(f"Content: {delta.content}", end='', flush=True)
            
    print(f"\nFinal app_has_output: {app_has_output}")
except Exception as e:
    print(f"Exception: {e}")
