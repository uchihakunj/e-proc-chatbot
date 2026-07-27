import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import requests
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "03_chunking" / "output"
sys.path.insert(0, str(ROOT / "04_embeddings_and_kg" / "scripts"))

from ov_embedder import OVEmbedder
from ov_reranker import OVReranker


QUERY = "How do I register as a vendor and what documents are required on the e-Procurement portal?"
CHUNK_LIMIT = 40
TOPK_FINAL = 3

MPNET_VARIANTS = [
    {
        "label": "mpnet_top5_plain",
        "query_text": QUERY,
        "topk_retrieve": 5,
    },
    {
        "label": "mpnet_top10_plain",
        "query_text": QUERY,
        "topk_retrieve": 10,
    },
    {
        "label": "mpnet_top10_expanded",
        "query_text": (
            QUERY
            + " vendor registration supplier registration PAN CRN "
              "bank details authorized signatory contact information registration fee"
        ),
        "topk_retrieve": 10,
    },
]


def load_env(env_path):
    for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()


def normalize(arr):
    arr = np.asarray(arr, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return arr / norms


def load_chunks(limit):
    chunks = []
    for path in sorted(CHUNK_DIR.rglob("*_chunk_*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        chunks.append(
            {
                "path": str(path.relative_to(CHUNK_DIR)),
                "text": text[:2400],
            }
        )
        if len(chunks) >= limit:
            break
    return chunks


def build_prompt(query, chunks):
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"Source {i}: {chunk['path']}\n{chunk['text']}")
    context = "\n\n".join(context_parts)
    system = (
        "You are a procurement assistant. Answer only from the provided context. "
        "If the context does not contain the answer, say so clearly. "
        "Be concise and factual. End with a line starting with 'Source:' followed by the most relevant source file names."
    )
    user = f"Question: {query}\n\nContext:\n{context}"
    return system, user


def call_sarvam(system, user):
    payload = {
        "model": os.environ.get("SARVAM_MODEL", "sarvam-105b").strip(),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "stream": False,
        "max_tokens": 512,
        "reasoning_effort": None,
    }
    headers = {
        "api-subscription-key": os.environ.get("SARVAM_API_KEY", "").strip(),
        "Content-Type": "application/json",
    }
    start = time.perf_counter()
    resp = requests.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=180,
    )
    elapsed = time.perf_counter() - start
    resp.raise_for_status()
    data = resp.json()
    content = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
    return content, elapsed


def encode_bge(query, texts):
    model = OVEmbedder("BAAI/bge-m3", device="CPU")
    model.return_sparse = False
    _ = model.encode([query], batch_size=1, max_length=512)
    start = time.perf_counter()
    qvec = model.encode([query], batch_size=1, max_length=512)["dense_vecs"]
    cvecs = model.encode(texts, batch_size=8, max_length=512)["dense_vecs"]
    return qvec, cvecs, time.perf_counter() - start


def encode_mpnet(model, query, texts):
    _ = model.encode([query], normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
    start = time.perf_counter()
    qvec = model.encode([query], normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
    cvecs = model.encode(texts, batch_size=8, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
    return qvec, cvecs, time.perf_counter() - start


def run_bge_baseline(chunks, reranker):
    texts = [c["text"] for c in chunks]
    qvec, cvecs, retrieval_s = encode_bge(QUERY, texts)
    sims = normalize(cvecs) @ normalize(qvec)[0]
    top_idx = np.argsort(-sims)[:5]
    retrieved = [chunks[i] for i in top_idx]
    pairs = [[QUERY, chunk["text"][:1500]] for chunk in retrieved]
    start = time.perf_counter()
    rr_scores = reranker.compute_score(pairs, normalize=True, max_length=256)
    rerank_s = time.perf_counter() - start
    order = sorted(range(len(retrieved)), key=lambda i: rr_scores[i], reverse=True)
    final_chunks = [retrieved[i] for i in order[:TOPK_FINAL]]
    system, user = build_prompt(QUERY, final_chunks)
    answer, sarvam_s = call_sarvam(system, user)
    return {
        "pipeline": "bge_baseline_top5",
        "retrieval_seconds": round(retrieval_s, 3),
        "rerank_seconds": round(rerank_s, 3),
        "sarvam_seconds": round(sarvam_s, 3),
        "total_seconds": round(retrieval_s + rerank_s + sarvam_s, 3),
        "top_chunks_after_rerank": [c["path"] for c in final_chunks],
        "answer": answer,
    }


def run_mpnet_variant(model, variant, chunks, reranker):
    texts = [c["text"] for c in chunks]
    qvec, cvecs, retrieval_s = encode_mpnet(model, variant["query_text"], texts)
    sims = normalize(cvecs) @ normalize(qvec)[0]
    top_idx = np.argsort(-sims)[: variant["topk_retrieve"]]
    retrieved = [chunks[i] for i in top_idx]
    pairs = [[QUERY, chunk["text"][:1500]] for chunk in retrieved]
    start = time.perf_counter()
    rr_scores = reranker.compute_score(pairs, normalize=True, max_length=256)
    rerank_s = time.perf_counter() - start
    order = sorted(range(len(retrieved)), key=lambda i: rr_scores[i], reverse=True)
    final_chunks = [retrieved[i] for i in order[:TOPK_FINAL]]
    system, user = build_prompt(QUERY, final_chunks)
    answer, sarvam_s = call_sarvam(system, user)
    return {
        "pipeline": variant["label"],
        "retrieval_query_used": variant["query_text"],
        "retrieval_topk": variant["topk_retrieve"],
        "retrieval_seconds": round(retrieval_s, 3),
        "rerank_seconds": round(rerank_s, 3),
        "sarvam_seconds": round(sarvam_s, 3),
        "total_seconds": round(retrieval_s + rerank_s + sarvam_s, 3),
        "top_chunks_after_rerank": [c["path"] for c in final_chunks],
        "answer": answer,
    }


def main():
    load_env(ROOT / ".env")
    chunks = load_chunks(CHUNK_LIMIT)
    reranker = OVReranker("BAAI/bge-reranker-v2-m3", device="CPU")
    mpnet_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    report = {
        "query": QUERY,
        "corpus_sample_size": len(chunks),
        "results": [run_bge_baseline(chunks, reranker)],
    }
    for variant in MPNET_VARIANTS:
        report["results"].append(run_mpnet_variant(mpnet_model, variant, chunks, reranker))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
