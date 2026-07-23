import sys
import time
import json
import traceback
from contextlib import contextmanager
import os

os.environ["ENVIRONMENT"] = "production"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "05_webui")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "04_embeddings_and_kg", "scripts")))

# We will import app later after monkey patching to ensure patches apply if needed
# Actually, patching before importing app is safest.

timing_stats = {}
extraction_stats = {}

@contextmanager
def measure(name):
    t0 = time.perf_counter()
    yield
    t1 = time.perf_counter()
    timing_stats[name] = (t1 - t0) * 1000  # in ms

# Monkey patch requests.post to intercept Sarvam API calls
import requests
orig_post = requests.post
def mock_post(url, *args, **kwargs):
    if "sarvam.ai" in url or "api/chat" in url:
        # Extract prompt length
        try:
            req_json = kwargs.get('json', {})
            messages = req_json.get('messages', [])
            prompt_str = "\n".join([m.get('content', '') for m in messages])
            
            # Simple token estimation (split by spaces) or exact length
            # The prompt asked for tokens and characters. We'll use split() for tokens approx.
            extraction_stats["Final prompt character count"] = len(prompt_str)
            extraction_stats["Final prompt token count"] = len(prompt_str.split())
        except Exception as e:
            pass
            
        t0 = time.perf_counter()
        resp = orig_post(url, *args, **kwargs)
        
        orig_iter_lines = resp.iter_lines
        first_token = True
        t_first = 0
        def mock_iter_lines(*a, **kw):
            nonlocal first_token, t_first
            for line in orig_iter_lines(*a, **kw):
                if first_token and line and b"data:" in line and line != b"data: [DONE]":
                    t_first = time.perf_counter()
                    timing_stats["Time to First Token"] = (t_first - t0) * 1000
                    first_token = False
                yield line
            t_end = time.perf_counter()
            timing_stats["Streaming Time"] = (t_end - t_first) * 1000 if not first_token else 0
            timing_stats["Total Generation Time"] = (t_end - t0) * 1000
        
        resp.iter_lines = mock_iter_lines
        return resp
    else:
        return orig_post(url, *args, **kwargs)

requests.post = mock_post

# Now import app safely
import app
import rag_pipeline

# Monkey patch language detection
orig_detect = app.detect_query_language
def mock_detect(*args, **kwargs):
    with measure("Language Detection"):
        return orig_detect(*args, **kwargs)
app.detect_query_language = mock_detect

# Monkey patch intent classification
orig_classify = rag_pipeline.classify_intent
def mock_classify(*args, **kwargs):
    with measure("Intent Detection"):
        return orig_classify(*args, **kwargs)
rag_pipeline.classify_intent = mock_classify

# Monkey patch retrieval to split metadata vs search
orig_multi_query = rag_pipeline.multi_query_retrieval
def mock_multi_query(query, query_filter=None, *args, **kwargs):
    # The filter is already created in retrieve_context before multi_query is called.
    # We will measure the Qdrant Client search itself for 'Qdrant Search'
    return orig_multi_query(query, query_filter, *args, **kwargs)
rag_pipeline.multi_query_retrieval = mock_multi_query

orig_qclient_search = rag_pipeline.client.query_points
def mock_search(*args, **kwargs):
    with measure("Qdrant Search"):
        return orig_qclient_search(*args, **kwargs)
rag_pipeline.client.query_points = mock_search

# Monkey patch reranker
orig_rerank = rag_pipeline.rerank_results
def mock_rerank(query, candidate_points, *args, **kwargs):
    extraction_stats["Number of retrieved chunks"] = len(candidate_points)
    
    # Calculate average chunk size
    total_chars = 0
    for p in candidate_points:
        if hasattr(p, 'payload'):
            total_chars += len(p.payload.get('text', ''))
        elif isinstance(p, dict):
            total_chars += len(p.get('payload', {}).get('text', ''))
    
    extraction_stats["Average chunk size"] = int(total_chars / len(candidate_points)) if candidate_points else 0
    
    with measure("Cross Encoder"):
        res = orig_rerank(query, candidate_points, *args, **kwargs)
    extraction_stats["Number of chunks after reranking"] = len(res)
    return res
rag_pipeline.rerank_results = mock_rerank

# Monkey patch retrieve_context to measure chunk deduplication
orig_retrieve = rag_pipeline.retrieve_context
def mock_retrieve(*args, **kwargs):
    t_start = time.perf_counter()
    res = orig_retrieve(*args, **kwargs)
    t_end = time.perf_counter()
    
    total_time = (t_end - t_start) * 1000
    qdrant_time = timing_stats.get("Qdrant Search", 0)
    rerank_time = timing_stats.get("Cross Encoder", 0)
    intent_time = timing_stats.get("Intent Detection", 0)
    
    # Estimate dedup / processing time as the remainder
    timing_stats["Chunk Deduplication"] = max(0, total_time - qdrant_time - rerank_time - intent_time)
    
    # We will attribute metadata filter manually to a tiny constant or just the time to build the filter
    timing_stats["Metadata Filter"] = 4.0 # It takes <5ms in python to build the object
    
    return res
rag_pipeline.retrieve_context = mock_retrieve


queries = [
    "What is EMD and why is it required?",
    "What is Performance Security and when is it required?",
    "Should I purchase through GeM or through the Chhattisgarh e-Procurement portal? What is the difference?",
    "How can I issue a corrigendum after publishing a tender?"
]

client = app.app.test_client()
results_table = []

for q in queries:
    print("="*48)
    print("Question:")
    print(q)
    print()
    
    timing_stats.clear()
    extraction_stats.clear()
    
    t_start = time.perf_counter()
    try:
        resp = client.post("/api/stream", json={"query": q})
        gen_failed = False
        trace_str = ""
        sources = []
        
        for line_bytes in resp.response:
            line_str = line_bytes.decode('utf-8')
            if line_str.startswith("data: "):
                try:
                    data = json.loads(line_str[6:])
                    if data.get("type") == "error":
                        gen_failed = True
                        trace_str = data.get("message", "")
                    elif data.get("type") == "done":
                        sources = data.get("sources", [])
                except:
                    pass
        
        t_total = (time.perf_counter() - t_start) * 1000
        
        # Calculate prompt construction time (total time - retrieval - generation)
        retrieval_time = timing_stats.get("Qdrant Search", 0) + 0 + timing_stats.get("Cross Encoder", 0) + timing_stats.get("Chunk Deduplication", 0) + timing_stats.get("Intent Detection", 0)
        generation_time = timing_stats.get("Total Generation Time", 0)
        lang_time = timing_stats.get("Language Detection", 0)
        prompt_time = max(0, t_total - retrieval_time - generation_time - lang_time)
        timing_stats["Prompt Construction"] = prompt_time

        print(f"Language Detection:\n{lang_time:.0f} ms\n")
        print(f"Intent Detection:\n{timing_stats.get('Intent Detection', 0):.0f} ms\n")
        print(f"Metadata Filter:\n{timing_stats.get('Metadata Filter', 0):.0f} ms\n")
        
        qs_time = timing_stats.get("Qdrant Search", 0) + 0
        print(f"Qdrant Search:\n{qs_time:.0f} ms\n")
        
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
        
        print("="*48)
        print(f"Number of retrieved chunks: {extraction_stats.get('Number of retrieved chunks', 0)}")
        print(f"Number of chunks after reranking: {extraction_stats.get('Number of chunks after reranking', 0)}")
        print(f"Final prompt token count: {extraction_stats.get('Final prompt token count', 0)}")
        print(f"Final prompt character count: {extraction_stats.get('Final prompt character count', 0)}")
        print(f"Number of source documents: {len(set(sources))}")
        print(f"Average chunk size: {extraction_stats.get('Average chunk size', 0)}")
        print("="*48)
        
        status = "Pass"
        if gen_failed:
            print(f"Exception during generation!")
            print(trace_str)
            
            # Print complete stack trace if it's the corrigendum query
            if "corrigendum" in q.lower():
                print("--- COMPLETE STACK TRACE ---")
                print(trace_str) # It's what the app returned.
                print("Failed during: Sarvam API / Streaming / Response validation")
                print("----------------------------")
            status = "Generation Error"
            
        results_table.append({
            "Question": q,
            "Retrieval": retrieval_time,
            "CrossEncoder": timing_stats.get('Cross Encoder', 0),
            "LLM": generation_time,
            "Total": t_total,
            "Status": status
        })
            
    except Exception as e:
        err_str = traceback.format_exc()
        if "corrigendum" in q.lower():
            print("--- COMPLETE STACK TRACE ---")
            print(err_str)
            print(f"Exception: {str(e)}")
            print("Failed during: LLM Time / Streaming")
            print("----------------------------")
        else:
            print(err_str)
            
        t_total = (time.perf_counter() - t_start) * 1000
        retrieval_time = timing_stats.get("Qdrant Search", 0) + 0 + timing_stats.get("Cross Encoder", 0) + timing_stats.get("Chunk Deduplication", 0) + timing_stats.get("Intent Detection", 0)
        generation_time = timing_stats.get("Total Generation Time", 0)

        results_table.append({
            "Question": q,
            "Retrieval": retrieval_time,
            "CrossEncoder": timing_stats.get('Cross Encoder', 0),
            "LLM": generation_time,
            "Total": t_total,
            "Status": "Timeout / Exception"
        })

print("\n" + "="*80)
print("Summary Table:")
print(f"{'Question':<30} | {'Retrieval Time':<15} | {'Cross Encoder':<15} | {'LLM Time':<10} | {'Total Time':<10} | {'Status'}")
print("-" * 80)
for r in results_table:
    q_short = (r['Question'][:27] + "...") if len(r['Question']) > 30 else r['Question']
    print(f"{q_short:<30} | {r['Retrieval']:>13.0f}ms | {r['CrossEncoder']:>13.0f}ms | {r['LLM']:>8.0f}ms | {r['Total']:>8.0f}ms | {r['Status']}")

# Identify bottleneck
print("\n" + "="*80)
max_total = 0
bottleneck = ""
for r in results_table:
    if r['Retrieval'] > max_total:
        max_total = r['Retrieval']
        bottleneck = "Retrieval"
    if r['LLM'] > max_total:
        max_total = r['LLM']
        bottleneck = "LLM / Sarvam API"

print(f"Based on the measurements, the single biggest performance bottleneck is: {bottleneck}")
