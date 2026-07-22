import json
import re

with open(r'05_webui\app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add max_tokens
code = re.sub(
    r'\"stream\": True\s*\}',
    '\"stream\": True,\n                        \"max_tokens\": 4096\n                    }',
    code
)

# Replace content extraction
old_extract = '''                                        content = delta.get("content")
                                        if content is not None and content != "":
                                            state['content_streamed'] = True
                                            yield f"data: {json.dumps({'type':'token','content':content})}\\n\\n"'''

new_extract = '''                                        content = delta.get("content")
                                        reasoning = delta.get("reasoning_content")
                                        text_to_yield = ""
                                        if content: text_to_yield += content
                                        if reasoning: text_to_yield += reasoning
                                        if text_to_yield:
                                            state['content_streamed'] = True
                                            yield f"data: {json.dumps({'type':'token','content':text_to_yield})}\\n\\n"'''

code = code.replace(old_extract, new_extract)

with open(r'05_webui\app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Patched app.py with max_tokens and reasoning_content')
