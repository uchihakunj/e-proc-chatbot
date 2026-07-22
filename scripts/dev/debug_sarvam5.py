import os
import sys
import json
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SARVAM_API_KEY')

# Add 05_webui to path so we can import from app.py
sys.path.insert(0, os.path.abspath('05_webui'))
from app import retrieve_context, detect_query_language, language_directive, PROCUREMENT_SYSTEM_PROMPT, expand_query_for_retrieval, prepend_lexical_rule_hits

query_text = "In chhatisgarh ,what are different ways of govt. procurement"
effective_query = query_text

print("Retrieving context...")
context_results = retrieve_context(expand_query_for_retrieval(effective_query), num_context=5, rerank_query=effective_query)
context_results = prepend_lexical_rule_hits(effective_query, context_results)

CTX_CHAR_BUDGET = 7000
PER_CHUNK_CAP   = 1600
context_parts = []
source_refs   = []
used = 0
for i, r in enumerate(context_results, 1):
    point = r.get('point', {})
    src  = point.payload.get('source','') if hasattr(point,'payload') else ''
    txt  = point.payload.get('text','')   if hasattr(point,'payload') else ''
    body = txt[:PER_CHUNK_CAP]
    if context_parts and used + len(body) > CTX_CHAR_BUDGET:
        break
    source_refs.append(src)
    context_parts.append(f"[Source {i}: {src}]\n{body}")
    used += len(body)

context_text = "\n\n".join(context_parts)
sources_str  = ", ".join(source_refs)

_lang = detect_query_language(query_text)
ollama_system = PROCUREMENT_SYSTEM_PROMPT.strip() + language_directive(_lang)
_final = ("\n\n>>> CRITICAL INSTRUCTION: You MUST write the ENTIRE response in ENGLISH ONLY. "
          "ABSOLUTELY NO HINDI ALLOWED. Do not write in Hindi even if the prompt contains Indian names. "
          "Use the English headings (💡 Answer / 📋 Process / 📘 Source).")
ollama_user = f"Context:\n{context_text}\n\nQuestion: {query_text}{_final}\n\nAnswer:"

print("Context length:", len(context_text))
print("User prompt length:", len(ollama_user))

data = {
    "model": "sarvam-30b",
    "messages": [
        {"role": "system", "content": ollama_system},
        {"role": "user", "content": ollama_user}
    ],
    "temperature": 0,
    "stream": True
}

url = "https://api.sarvam.ai/v1/chat/completions"
headers = {
    "api-subscription-key": api_key,
    "Content-Type": "application/json"
}

print("Making raw POST request...")
with httpx.stream("POST", url, headers=headers, json=data, timeout=60) as r:
    print(f"Status: {r.status_code}")
    for chunk in r.iter_text():
        print(chunk, end="")
print("\nDone.")
