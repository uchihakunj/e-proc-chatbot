import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SARVAM_API_KEY')
model = os.getenv('SARVAM_MODEL', 'sarvam-30b')

state = {'content_streamed': False, 'failed_before_output': False}

def _stream_sarvam(model, state):
    try:
        from sarvamai import SarvamAI
        client = SarvamAI(api_subscription_key=api_key)
        
        response = client.chat.completions(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ],
            temperature=0
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response dir: {dir(response)}")
        
        # This is exactly what app.py does:
        content = response.choices[0].message.content if hasattr(response, 'choices') else str(response)
        
        print(f"Extracted content: {repr(content)}")
        
        if content:
            state['content_streamed'] = True
            yield f"data: {content}\n\n"
            
    except Exception as e:
        print(f"Exception: {repr(e)}")
        if not state.get('content_streamed'):
            state['failed_before_output'] = True

for sse in _stream_sarvam(model, state):
    print("Yielded:", sse)

print("Final state:", state)
