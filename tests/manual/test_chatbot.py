import sys
import os
import codecs
from pathlib import Path

# Force Windows console to support Hindi characters
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Speed up CPU testing
os.environ["RERANK_TOPK"] = "10"
os.environ["RERANK_MAX_CANDS"] = "10"

SCRIPT_DIR = Path(r"c:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY\05_webui")
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / '04_embeddings_and_kg' / 'scripts'))

from rag_pipeline import retrieve_context
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SARVAM_API_KEY')

def ask_sarvam(query, contexts):
    context_text = "\n\n".join([f"Source: {c['point'].payload.get('source', 'Unknown')}\n{c['point'].payload.get('text', '')}" for c in contexts])
    
    url = "https://api.sarvam.ai/v1/chat/completions"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    
    system_msg = "You are a procurement assistant. Answer strictly based on the provided context."
    user_msg = f"Context:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"

    data = {
        "model": "sarvam-30b",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0,
        "stream": True
    }
    
    with httpx.stream("POST", url, headers=headers, json=data, timeout=60) as r:
        if r.status_code != 200:
            print(f"\nAPI Error: {r.status_code}")
            print(r.read().decode())
            return
            
        for chunk in r.iter_lines():
            if not chunk: continue
            if chunk.startswith("data: ") and chunk != "data: [DONE]":
                raw_json = chunk[6:]
                try:
                    import json
                    parsed = json.loads(raw_json)
                    if "choices" in parsed and len(parsed["choices"]) > 0:
                        delta = parsed["choices"][0].get("delta", {})
                        content = delta.get("content")
                        if content is not None and content != "":
                            print(content, end="", flush=True)
                except Exception as e:
                    pass
            elif not chunk.startswith("data: "):
                print(f"\n[Raw API]: {chunk}")

def main():
    print("\n✅ Terminal Chatbot Ready! (Powered by Sarvam AI)")
    print("Type 'exit' to stop.")
    
    while True:
        query = input("\n📝 You: ")
        
        if query.lower() in ['exit', 'quit']:
            break
        if not query.strip():
            continue
            
        print("\n🤖 Chatbot is thinking...\n")
        try:
            contexts = retrieve_context(query, num_context=5)
            if not contexts:
                print("No context found in database.")
                continue
            
            ask_sarvam(query, contexts)
            print("\n")
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
