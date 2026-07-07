# -*- coding: utf-8 -*-
"""Standalone de-risk probe for the OpenVINO/Arc reranker backend.

Exports BAAI/bge-reranker-v2-m3 to OpenVINO IR, runs it on the Arc iGPU, and
compares its scores + latency against the current CPU FlagReranker on the same
query/doc pairs. Run once before wiring the backend into rag_pipeline.py.
"""
import sys, time, math
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL = "BAAI/bge-reranker-v2-m3"
DEVICE = "GPU"  # the Arc iGPU

pairs = [
    ["What is EMD refund process?", "The earnest money deposit is refunded to the bidder after the tender process concludes, via the online refund module."],
    ["What is EMD refund process?", "The auction engine asks bidders to change the default password before quoting a bid."],
    ["How to register as a vendor on CHiPS?", "Visit eproc.cgstate.gov.in, click New User, enter PAN card details and a preferred login code."],
    ["How to register as a vendor on CHiPS?", "General Financial Rules 2017 apply to all Central Government Ministries and Departments."],
    ["What is the procedure for DSC?", "A Digital Signature Certificate (Class II or III) is required; obtain it from a licensed Certifying Authority."],
]

def sigmoid(x): return 1.0 / (1.0 + math.exp(-x))

print("=== CPU FlagReranker (baseline) ===", flush=True)
from FlagEmbedding import FlagReranker
fr = FlagReranker(MODEL, use_fp16=True)
t = time.time()
cpu = fr.compute_score([[q, d[:512]] for q, d in pairs], normalize=True, max_length=256)
cpu_t = time.time() - t
cpu = cpu if isinstance(cpu, list) else [cpu]
print(f"  scores: {[round(s,3) for s in cpu]}")
print(f"  warm latency: {cpu_t*1000:.0f} ms for {len(pairs)} pairs", flush=True)

print("\n=== OpenVINO on Arc GPU ===", flush=True)
from optimum.intel import OVModelForSequenceClassification
from transformers import AutoTokenizer
import numpy as np

t = time.time()
tok = AutoTokenizer.from_pretrained(MODEL)
ov = OVModelForSequenceClassification.from_pretrained(MODEL, export=True, device=DEVICE)
print(f"  export+compile on {DEVICE}: {time.time()-t:.1f}s", flush=True)

def ov_score(pairs, max_length=256):
    q = [a for a, _ in pairs]; d = [b[:512] for _, b in pairs]
    enc = tok(q, d, padding=True, truncation=True, max_length=max_length, return_tensors="np")
    logits = ov(**{k: enc[k] for k in enc}).logits
    logits = np.asarray(logits).reshape(-1)
    return [sigmoid(float(x)) for x in logits]

_ = ov_score(pairs)  # warmup
t = time.time()
gpu = ov_score(pairs)
gpu_t = time.time() - t
print(f"  scores: {[round(s,3) for s in gpu]}")
print(f"  warm latency: {gpu_t*1000:.0f} ms for {len(pairs)} pairs", flush=True)

print("\n=== COMPARISON ===")
maxdiff = max(abs(a - b) for a, b in zip(cpu, gpu))
order_cpu = sorted(range(len(pairs)), key=lambda i: -cpu[i])
order_gpu = sorted(range(len(pairs)), key=lambda i: -gpu[i])
print(f"  max |score diff|: {maxdiff:.4f}")
print(f"  ranking order CPU: {order_cpu}")
print(f"  ranking order GPU: {order_gpu}")
print(f"  ranking identical: {order_cpu == order_gpu}")
print(f"  speedup: {cpu_t/gpu_t:.2f}x  (CPU {cpu_t*1000:.0f}ms -> GPU {gpu_t*1000:.0f}ms)")
