import re

with open(r'05_webui\app.py', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = re.compile(r'            def _stream_model\(model, state\):.*?state\[\'content_streamed\'\] = True\n.*?yield f"data: \{json.dumps\(\{\'type\':\'token\',\'content\':out\}\)\}\\n\\n"\n\s*break\n\s*except Exception:\n\s*pass\n.*?\n\s*yield f"data: \{json.dumps\(\{\'type\':\'error\',\'message\':f\'Ollama error: \{e\}\'\}\)\}\\n\\n"', re.DOTALL)

match = pattern.search(code)
if match:
    new_func = '''            def _stream_model(model, state):
                """Run Sarvam API streaming attempt."""
                try:
                    import httpx
                    url = "https://api.sarvam.ai/v1/chat/completions"
                    headers = {
                        "api-subscription-key": os.getenv('SARVAM_API_KEY'),
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
                                    parsed = json.loads(chunk[6:])
                                    if "choices" in parsed and len(parsed["choices"]) > 0:
                                        delta = parsed["choices"][0].get("delta", {})
                                        content = delta.get("content")
                                        if content is not None and content != "":
                                            state['content_streamed'] = True
                                            yield f"data: {json.dumps({'type':'token','content':content})}\\n\\n"
                                except Exception:
                                    pass
                except Exception as e:
                    if not state.get('content_streamed'):
                        state['failed_before_output'] = True
                        state['error'] = str(e)
                    else:
                        yield f"data: {json.dumps({'type':'error','message':f'Sarvam error: {e}'})}\\n\\n"'''
    
    new_code = code[:match.start()] + new_func + code[match.end():]
    with open(r'05_webui\app.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("Patched app.py successfully!")
else:
    print("Could not find _stream_model")
