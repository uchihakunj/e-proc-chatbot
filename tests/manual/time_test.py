import requests, time

print('Starting timing test...')
start_time = time.time()
payload = {'query': 'ई-प्रोक्योरमेंट के क्या फायदे हैं?'}

try:
    with requests.post('http://localhost:5000/api/stream', json=payload, stream=True) as r:
        first_token_time = None
        for line in r.iter_lines():
            if line:
                if not first_token_time and b'"type": "token"' in line:
                    first_token_time = time.time()
                    print(f'\n[RAG + API Latency] Time to first token: {first_token_time - start_time:.2f}s')
                
        end_time = time.time()
        print(f'\n[Total Time] Full response completed in: {end_time - start_time:.2f}s')
        if first_token_time:
            print(f'[Generation Time] Sarvam streaming took: {end_time - first_token_time:.2f}s')
except Exception as e:
    print('Request failed:', e)
