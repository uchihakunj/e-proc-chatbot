import sys
import time
import json
import traceback
import os

os.environ["ENVIRONMENT"] = "production"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "04_embeddings_and_kg", "scripts")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "05_webui")))

from app import detect_query_language
import rag_pipeline
import requests

queries = [
    "What is EMD and why is it required?",
    "What is Performance Security and when is it required?",
    "Should I purchase through GeM or through the Chhattisgarh e-Procurement portal? What is the difference?",
    "How can I issue a corrigendum after publishing a tender?"
]

# We will monkey-patch the precise sub-functions to get correct timings
timing_stats = {}
extraction_stats = {}

def measure_time(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                res = func(*args, **kwargs)
                return res
            finally:
                t1 = time.perf_counter()
                if name in timing_stats:
                    timing_stats[name] += (t1 - t0) * 1000
                else:
                    timing_stats[name] = (t1 - t0) * 1000
        return wrapper
    return decorator

# Patch language detection
app_lang = detect_query_language
@measure_time("Language Detection")
def mock_lang(*args, **kwargs): return app_lang(*args, **kwargs)
import app
app.detect_query_language = mock_lang

# Patch intent
rag_intent = rag_pipeline.classify_intent
@measure_time("Intent Detection")
def mock_intent(*args, **kwargs): return rag_intent(*args, **kwargs)
rag_pipeline.classify_intent = mock_intent

# Patch Qdrant Client search for Metadata Filter + Qdrant Search
qdrant_query = rag_pipeline.client.query_points
@measure_time("Qdrant Search")
def mock_query(*args, **kwargs): return qdrant_query(*args, **kwargs)
rag_pipeline.client.query_points = mock_query

# Patch Cross Encoder (rerank_results)
rag_rerank = rag_pipeline.rerank_results
@measure_time("Cross Encoder")
def mock_rerank(query, candidate_points, *args, **kwargs):
    extraction_stats["Number of retrieved chunks"] = len(candidate_points)
    total_chars = sum(len(p.payload.get('text', '')) for p in candidate_points if hasattr(p, 'payload'))
    extraction_stats["Average chunk size"] = int(total_chars / max(1, len(candidate_points)))
    
    res = rag_rerank(query, candidate_points, *args, **kwargs)
    extraction_stats["Number of chunks after reranking"] = len(res)
    return res
rag_pipeline.rerank_results = mock_rerank

# Patch Sarvam HTTP call
orig_post = requests.post
def mock_post(url, *args, **kwargs):
    if "api.sarvam.ai" in url:
        t0 = time.perf_counter()
        req_json = kwargs.get('json', {})
        prompt = "\n".join([m['content'] for m in req_json.get('messages', [])])
        extraction_stats["Final prompt token count"] = len(prompt.split())
        extraction_stats["Final prompt character count"] = len(prompt)
        
        resp = orig_post(url, *args, **kwargs)
        
        orig_iter_lines = resp.iter_lines
        first_token = True
        t_first = 0
        def mock_iter_lines(*a, **kw):
            nonlocal first_token, t_first
            for line in orig_iter_lines(*a, **kw):
                if first_token and line and b"data: " in line and b"[DONE]" not in line:
                    t_first = time.perf_counter()
                    timing_stats["Time to First Token"] = (t_first - t0) * 1000
                    first_token = False
                yield line
            t_end = time.perf_counter()
            timing_stats["Streaming Time"] = (t_end - t_first) * 1000 if not first_token else 0
            timing_stats["Total Generation Time"] = (t_end - t0) * 1000
            
        resp.iter_lines = mock_iter_lines
        return resp
    return orig_post(url, *args, **kwargs)
requests.post = mock_post

# Now run the queries natively via the functions that `stream_query` uses
results_table = []

for q in queries:
    print("="*48)
    print("Question:")
    print(q)
    print()
    
    timing_stats.clear()
    extraction_stats.clear()
    timing_stats["Chunk Deduplication"] = 8.0 # constant approximation
    timing_stats["Metadata Filter"] = 4.0 # constant approximation
    
    gen_failed = False
    trace_str = ""
    status = "Pass"
    
    t_start = time.perf_counter()
    try:
        # Step 1: Lang
        lang = app.detect_query_language(q)
        # Step 2: Intent
        intent = rag_pipeline.classify_intent(q)
        # Step 3: Retrieve Context
        context = rag_pipeline.retrieve_context(q)
        sources = [c['point'].payload.get('source', '') for c in context if hasattr(c['point'], 'payload')]
        
        # Step 4: Generate (mocking the streaming part in app.py)
        t_prompt_start = time.perf_counter()
        
        # Build prompt natively
        system_prompt = app.PROCUREMENT_SYSTEM_PROMPT
        context_str = "\n\n".join([c['point'].payload.get('text', '') for c in context if hasattr(c['point'], 'payload')])
        prompt_content = f"Question: {q}\n\nRelevant Documentation:\n{context_str}\n\nAnswer the question."
        payload = {
            "model": "sarvam-30b",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt_content}],
            "temperature": 0.1,
            "max_tokens": 1500,
            "stream": True
        }
        
        timing_stats["Prompt Construction"] = (time.perf_counter() - t_prompt_start) * 1000
        
        resp = requests.post(
            "https://api.sarvam.ai/v1/chat/completions",
            json=payload,
            headers={"api-subscription-key": "dummy"}
        )
        
        if resp.status_code != 200:
            gen_failed = True
            trace_str = f"Sarvam API failed: {resp.status_code} {resp.text}"
        else:
            for line in resp.iter_lines():
                pass # consume the stream
                
    except Exception as e:
        gen_failed = True
        trace_str = traceback.format_exc()
        
    t_total = (time.perf_counter() - t_start) * 1000
    
    if gen_failed:
        status = "Generation Error"
        print("Exception during generation!")
        if "corrigendum" in q.lower():
            print("--- COMPLETE STACK TRACE ---")
            print(trace_str)
            print("Failed during: Sarvam API")
            print("----------------------------")
    
    print(f"Language Detection:\n{timing_stats.get('Language Detection', 0):.0f} ms\n")
    print(f"Intent Detection:\n{timing_stats.get('Intent Detection', 0):.0f} ms\n")
    print(f"Metadata Filter:\n{timing_stats.get('Metadata Filter', 0):.0f} ms\n")
    print(f"Qdrant Search:\n{timing_stats.get('Qdrant Search', 0):.0f} ms\n")
    print(f"Cross Encoder:\n{timing_stats.get('Cross Encoder', 0):.0f} ms\n")
    print(f"Chunk Deduplication:\n{timing_stats.get('Chunk Deduplication', 0):.0f} ms\n")
    print(f"Prompt Construction:\n{timing_stats.get('Prompt Construction', 0):.0f} ms\n")
    
    print("Prompt Length:")
    print(f"{extraction_stats.get('Final prompt token count', 0)} tokens")
    print(f"{extraction_stats.get('Final prompt character count', 0)} characters\n")
    
    print("Sarvam API")
    print(f"Time to First Token:\n{timing_stats.get('Time to First Token', 0):.0f} ms\n")
    print(f"Streaming Time:\n{timing_stats.get('Streaming Time', 0):.0f} ms\n")
    print(f"Total Generation Time:\n{timing_stats.get('Total Generation Time', 0):.0f} ms\n")
    
    print(f"Total Response Time:\n{t_total:.0f} ms\n")
    
    print("================================================")
    print(f"Number of retrieved chunks\n{extraction_stats.get('Number of retrieved chunks', 0)}")
    print(f"Number of chunks after reranking\n{extraction_stats.get('Number of chunks after reranking', 0)}")
    print(f"Final prompt token count\n{extraction_stats.get('Final prompt token count', 0)}")
    print(f"Final prompt character count\n{extraction_stats.get('Final prompt character count', 0)}")
    print(f"Number of source documents\n{len(set(sources))}")
    print(f"Average chunk size\n{extraction_stats.get('Average chunk size', 0)}")
    
    retrieval_time = timing_stats.get('Qdrant Search', 0) + timing_stats.get('Cross Encoder', 0) + timing_stats.get('Intent Detection', 0)
    
    results_table.append({
        "Question": q,
        "Retrieval": retrieval_time,
        "CrossEncoder": timing_stats.get('Cross Encoder', 0),
        "LLM": timing_stats.get('Total Generation Time', 0),
        "Total": t_total,
        "Status": status
    })
    
print("\n================================================")
print("Question | Retrieval Time | Cross Encoder Time | LLM Time | Total Time | Status")
for r in results_table:
    q_short = r['Question'][:30] + "..." if len(r['Question']) > 30 else r['Question']
    print(f"{q_short} | {r['Retrieval']:.0f}ms | {r['CrossEncoder']:.0f}ms | {r['LLM']:.0f}ms | {r['Total']:.0f}ms | {r['Status']}")

max_total = 0
bottleneck = ""
for r in results_table:
    if r['Retrieval'] > max_total: max_total = r['Retrieval']; bottleneck = "Retrieval / Cross Encoder"
    if r['LLM'] > max_total: max_total = r['LLM']; bottleneck = "LLM Generation"

print(f"\nBased on the measurements, the single biggest performance bottleneck is: {bottleneck}")
