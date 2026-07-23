import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import httpx, json, time

key = 'sk_fw0t2lcb_pKKcB5MpH17E52wHq8irTrnm'
headers = {'api-subscription-key': key, 'Content-Type': 'application/json'}

# Try with budget_tokens to cap reasoning + big max_tokens for final answer
t0 = time.monotonic()
r = httpx.post('https://api.sarvam.ai/v1/chat/completions', headers=headers,
    json={
        'model': 'sarvam-105b',
        'messages': [{'role': 'user', 'content': 'In one sentence: what is GFR Rule 154?'}],
        'max_tokens': 2000,
        'temperature': 0,
        'budget_tokens': 200,   # cap reasoning chain
    },
    timeout=120)
elapsed = round(time.monotonic() - t0, 2)
print(f'HTTP {r.status_code} | {elapsed}s')
d = r.json()
choice = d['choices'][0]['message']
content = choice.get('content') or ''
reasoning = choice.get('reasoning_content') or ''
print(f'content ({len(content)} chars): {repr(content[:600])}')
print(f'reasoning ({len(reasoning)} chars): first 200: {repr(reasoning[:200])}')
print(f'finish_reason: {d["choices"][0]["finish_reason"]}')
print(f'usage: {d.get("usage")}')
