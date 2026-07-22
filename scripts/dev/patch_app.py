import re
with open(r'05_webui\app.py', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = re.compile(r'            def _stream_sarvam\(model, state\):.*?state\[\'content_streamed\'\] = True', re.DOTALL)
match = pattern.search(code)
if match:
    new_func = '''            def _stream_sarvam(model, state):
                """Run one Sarvam API streaming attempt using httpx directly."""
                api_key = os.getenv('SARVAM_API_KEY')
                if not api_key:
                    state['failed_before_output'] = True
                    return
                try:
                    import httpx
                    import json as m_json
                    
                    yield f"data: {m_json.dumps({'type':'status','message':'🚀 Generating answer (Sarvam API)...'})}\\n\\n"
                    
                    url = "https://api.sarvam.ai/v1/chat/completions"
                    headers = {
                        "api-subscription-key": api_key,
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": "sarvam-30b",
                        "messages": [
                            {"role": "system", "content": ollama_system},
                            {"role": "user", "content": ollama_user}
                        ],
                        "temperature": 0,
                        "stream": True
                    }
                    
                    with httpx.stream("POST", url, headers=headers, json=data, timeout=60) as r:
                        if r.status_code != 200:
                            state['failed_before_output'] = True
                            return
                            
                        for chunk in r.iter_lines():
                            if not chunk: continue
                            if chunk.startswith("data: ") and chunk != "data: [DONE]":
                                try:
                                    parsed = m_json.loads(chunk[6:])
                                    if "choices" in parsed and len(parsed["choices"]) > 0:
                                        delta = parsed["choices"][0].get("delta", {})
                                        content = delta.get("content")
                                        if content is not None and content != "":
                                            state['content_streamed'] = True
                                            yield f"data: {m_json.dumps({'type':'token','content':content})}\\n\\n"
                                except Exception:
                                    pass
                except Exception:
                    state['failed_before_output'] = True
                    pass
                state['content_streamed'] = state.get('content_streamed', False)'''
    new_code = code[:match.start()] + new_func + code[match.end():]
    with open(r'05_webui\app.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print('Patched app.py successfully.')
else:
    print('Failed to find _stream_sarvam.')
