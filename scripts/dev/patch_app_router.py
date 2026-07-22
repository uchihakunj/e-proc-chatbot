import os
import re

app_path = r'05_webui\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the _stream_model function and the logic around it
old_stream_code = '''            def _stream_model(model, state):
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
                        "stream": True,
                        "max_tokens": 4096
                    }
                    
                    with httpx.stream("POST", url, headers=headers, json=data, timeout=60) as r:
                        if r.status_code != 200:
                            print(f"[SARVAM ERROR] {r.status_code}: {r.read().decode()}", flush=True)
                            state['failed_before_output'] = True
                            return
                            
                        for chunk in r.iter_lines():
                            if not chunk: continue
                            print(f"[SARVAM CHUNK] {chunk}", flush=True)
                            if chunk.startswith("data: ") and chunk != "data: [DONE]":
                                try:
                                    parsed = json.loads(chunk[6:])
                                    if "choices" in parsed and len(parsed["choices"]) > 0:
                                        delta = parsed["choices"][0].get("delta", {})
                                        content = delta.get("content")
                                        reasoning = delta.get("reasoning_content")
                                        text_to_yield = ""
                                        if content: text_to_yield += content
                                        if reasoning: text_to_yield += reasoning
                                        if text_to_yield:
                                            state['content_streamed'] = True
                                            yield f"data: {json.dumps({'type':'token','content':text_to_yield})}\\n\\n"
                                except Exception as json_err:
                                    print(f"[JSON PARSE ERROR] {json_err}", flush=True)
                except Exception as e:
                    if not state.get('content_streamed'):
                        state['failed_before_output'] = True
                        print(f'[SARVAM EXCEPTION] {e}', flush=True)
                        state['error'] = str(e)
                    else:
                        yield f"data: {json.dumps({'type':'error','message':f'Sarvam error: {e}'})}\\n\\n"'''

new_stream_code = '''            def _stream_model(model, state):
                """Run streaming attempt (Sarvam if model='sarvam-30b', else Ollama)."""
                if model == "sarvam-30b":
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
                            "stream": True,
                            "max_tokens": 4096
                        }
                        
                        with httpx.stream("POST", url, headers=headers, json=data, timeout=60) as r:
                            if r.status_code != 200:
                                print(f"[SARVAM ERROR] {r.status_code}: {r.read().decode()}", flush=True)
                                state['failed_before_output'] = True
                                return
                                
                            for chunk in r.iter_lines():
                                if not chunk: continue
                                print(f"[SARVAM CHUNK] {chunk}", flush=True)
                                if chunk.startswith("data: ") and chunk != "data: [DONE]":
                                    try:
                                        parsed = json.loads(chunk[6:])
                                        if "choices" in parsed and len(parsed["choices"]) > 0:
                                            delta = parsed["choices"][0].get("delta", {})
                                            content = delta.get("content")
                                            reasoning = delta.get("reasoning_content")
                                            text_to_yield = ""
                                            if content: text_to_yield += content
                                            if reasoning: text_to_yield += reasoning
                                            if text_to_yield:
                                                state['content_streamed'] = True
                                                yield f"data: {json.dumps({'type':'token','content':text_to_yield})}\\n\\n"
                                    except Exception as json_err:
                                        print(f"[JSON PARSE ERROR] {json_err}", flush=True)
                    except Exception as e:
                        if not state.get('content_streamed'):
                            state['failed_before_output'] = True
                            print(f'[SARVAM EXCEPTION] {e}', flush=True)
                            state['error'] = str(e)
                        else:
                            yield f"data: {json.dumps({'type':'error','message':f'Sarvam error: {e}'})}\\n\\n"
                else:
                    # OLLAMA FALLBACK
                    try:
                        resp = requests.post(
                            f"{OLLAMA_URL}/api/chat",
                            json={'model': model,
                                  'messages': [{'role':'system','content':ollama_system},
                                               {'role':'user','content':ollama_user}],
                                  'stream': True,
                                  'keep_alive': os.getenv('OLLAMA_KEEP_ALIVE', '30m'),
                                  'think': False,
                                  'options': {
                                      'temperature': 0,
                                      'seed':        42,
                                      'num_predict': int(os.getenv('OLLAMA_NUM_PREDICT', '1536')),
                                      'num_ctx':     int(os.getenv('OLLAMA_NUM_CTX', '6144')),
                                  }
                            },
                            stream=True, timeout=60
                        )
                        if resp.status_code != 200:
                            state['failed_before_output'] = True
                            print(f"Ollama returned {resp.status_code}: {resp.text}", flush=True)
                            return
                        for line in resp.iter_lines():
                            if line:
                                j = json.loads(line)
                                msg = j.get('message', {})
                                chunk = msg.get('content', '')
                                if chunk:
                                    state['content_streamed'] = True
                                    state['answer_buf'].append(chunk)
                                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\\n\\n"
                    except Exception as e:
                        if not state.get('content_streamed'):
                            state['failed_before_output'] = True
                        else:
                            yield f"data: {json.dumps({'type':'error','message':f'Model error: {e}'})}\\n\\n"'''

code = code.replace(old_stream_code, new_stream_code)

old_primary_call = '''            state = {'content_streamed': False, 'failed_before_output': False}
            for sse in _stream_model(OLLAMA_MODEL, state):
                yield sse'''

new_primary_call = '''            state = {'content_streamed': False, 'failed_before_output': False, 'answer_buf': []}
            PRIMARY_MODEL = "sarvam-30b"
            for sse in _stream_model(PRIMARY_MODEL, state):
                yield sse'''

code = code.replace(old_primary_call, new_primary_call)

old_fallback_call = '''            if ((state['failed_before_output'] or not state['content_streamed'])
                    and FALLBACK_MODEL and FALLBACK_MODEL != OLLAMA_MODEL):'''

new_fallback_call = '''            if ((state['failed_before_output'] or not state['content_streamed'])
                    and FALLBACK_MODEL):'''

code = code.replace(old_fallback_call, new_fallback_call)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.py logic")
