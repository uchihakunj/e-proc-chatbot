import sys
import os
from pathlib import Path

# Speed up CPU testing by only reranking top 10 instead of 50
os.environ["RERANK_TOPK"] = "10"
os.environ["RERANK_MAX_CANDS"] = "10"

# Add required paths
SCRIPT_DIR = Path(r"c:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY\05_webui")
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / '04_embeddings_and_kg' / 'scripts'))

from rag_pipeline import retrieve_context

def main():
    print("\n✅ Pipeline ready! You can now test the database.")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        query = input("\n📝 Ask a question: ")
        
        if query.lower() in ['exit', 'quit']:
            break
            
        if not query.strip():
            continue
            
        print(f"\n🔍 Retrieving top 5 chunks for: '{query}'...\n")
        
        try:
            contexts = retrieve_context(query, num_context=5)
            
            if not contexts:
                print("⚠️ No chunks found.")
                continue
                
            for i, ctx in enumerate(contexts):
                point = ctx.get('point')
                if not point:
                    continue
                payload = getattr(point, 'payload', {}) or {}
                
                print(f"--- Chunk {i+1} ---")
                print(f"Source: {payload.get('source', 'Unknown')}")
                print(f"Content:\n{payload.get('text', 'No text found')}\n")
        except Exception as e:
            print(f"Error during retrieval: {e}")

if __name__ == "__main__":
    main()
