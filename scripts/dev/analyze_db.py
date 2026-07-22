import os
import json
from qdrant_client import QdrantClient
from collections import Counter
import statistics

# Connect to local Qdrant
db_path = r"C:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY\04_embeddings_and_kg\db\qdrant_local"
client = QdrantClient(path=db_path)
COLLECTION_NAME = "chips_procurement"

def analyze_db():
    print(f"--- QDRANT DATABASE ANALYSIS ---")
    
    # 1. Basic Stats
    info = client.get_collection(COLLECTION_NAME)
    num_points = info.vectors_count
    print(f"Total points (chunks) in DB: {num_points}")
    
    # Scroll through all points to gather stats
    points = []
    offset = None
    while True:
        res = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )
        batch, next_offset = res
        points.extend(batch)
        if next_offset is None:
            break
        offset = next_offset

    if not points:
        print("No points found!")
        return

    # Analyze metadata & chunks
    chunk_lengths = []
    sources = Counter()
    files = Counter()
    exact_texts = Counter()
    has_store_purchase = False
    metadata_fields = set()
    
    for p in points:
        payload = p.payload or {}
        metadata_fields.update(payload.keys())
        
        text = payload.get("text", "")
        chunk_lengths.append(len(text))
        exact_texts[text] += 1
        
        source = payload.get("source", "UNKNOWN")
        file_name = payload.get("file", "UNKNOWN")
        
        sources[source] += 1
        files[file_name] += 1
        
        if "store" in text.lower() and "purchase" in text.lower() and "rule" in text.lower():
            has_store_purchase = True
            
        if "store" in file_name.lower() or "purchase" in file_name.lower():
            has_store_purchase = True

    # 1. Chunk Sizes
    print("\n1. Chunk Size Analysis:")
    print(f"   Max chunk size: {max(chunk_lengths)} characters")
    print(f"   Min chunk size: {min(chunk_lengths)} characters")
    print(f"   Avg chunk size: {statistics.mean(chunk_lengths):.2f} characters")
    print(f"   Median chunk size: {statistics.median(chunk_lengths):.2f} characters")
    
    # 2. Document Dominance (FAQ check)
    print("\n2. Document Distribution (Top 10):")
    for f, count in files.most_common(10):
        print(f"   - {f}: {count} chunks ({(count/num_points)*100:.1f}%)")
        
    # 3. Store Purchase Rule Indexed
    print("\n3. Store Purchase Rule:")
    print(f"   Found references to Store Purchase Rules: {has_store_purchase}")
    
    # 4. Metadata Check
    print("\n4. Metadata Fields Present:")
    print(f"   {list(metadata_fields)}")
    
    # 5. Duplicates
    duplicates = {text: count for text, count in exact_texts.items() if count > 1}
    print("\n5. Duplicate Analysis:")
    print(f"   Total unique chunks: {len(exact_texts)}")
    print(f"   Exact duplicate text chunks: {len(duplicates)}")
    if duplicates:
        print(f"   Top duplicate repeated {max(duplicates.values())} times.")

if __name__ == "__main__":
    analyze_db()
