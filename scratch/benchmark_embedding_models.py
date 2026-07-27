import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "03_chunking" / "output"
sys.path.insert(0, str(ROOT / "04_embeddings_and_kg" / "scripts"))

from ov_embedder import OVEmbedder

QUERIES = [
    {
        "query": "What is e-Procurement?",
        "expected_terms": ["faq", "chips", "procurement"],
    },
    {
        "query": "Vendor registration kaise karein?",
        "expected_terms": ["vendor", "registration"],
    },
    {
        "query": "What is EMD and when is it refunded?",
        "expected_terms": ["emd", "refund"],
    },
    {
        "query": "Tender eligibility criteria kaise check karun?",
        "expected_terms": ["eligibility", "bid", "tender"],
    },
    {
        "query": "How do I submit my technical and price bid online?",
        "expected_terms": ["bid", "submission", "price", "technical"],
    },
]


def normalize(vecs):
    arr = np.asarray(vecs, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return arr / norms


def load_chunks(limit=40):
    chunks = []
    for path in sorted(CHUNK_DIR.rglob("*_chunk_*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        chunks.append(
            {
                "path": str(path.relative_to(CHUNK_DIR)),
                "source": path.parent.name if path.parent != CHUNK_DIR else path.stem,
                "text": text[:2400],
            }
        )
        if len(chunks) >= limit:
            break
    return chunks


def encode_current_model(model, texts):
    model.return_sparse = False
    times = []
    for text in texts:
        start = time.perf_counter()
        model.encode([text], batch_size=1, max_length=512)
        times.append(time.perf_counter() - start)
    batch_start = time.perf_counter()
    batch = model.encode(texts, batch_size=8, max_length=512)["dense_vecs"]
    batch_time = time.perf_counter() - batch_start
    return batch, times, batch_time


def encode_mpnet_model(model, texts):
    times = []
    for text in texts:
        start = time.perf_counter()
        model.encode([text], normalize_embeddings=True, show_progress_bar=False)
        times.append(time.perf_counter() - start)
    batch_start = time.perf_counter()
    batch = model.encode(
        texts,
        batch_size=8,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    batch_time = time.perf_counter() - batch_start
    return batch, times, batch_time


def retrieval_probe(corpus_chunks, corpus_emb, query_embs):
    corpus = normalize(corpus_emb)
    queries = normalize(query_embs)
    rows = []
    for meta, qvec in zip(QUERIES, queries):
        sims = corpus @ qvec
        top_idx = np.argsort(-sims)[:3]
        top_sources = [corpus_chunks[i]["source"] for i in top_idx]
        top_paths = [corpus_chunks[i]["path"] for i in top_idx]
        expected_hit = any(
            any(term in source.lower() or term in path.lower() for term in meta["expected_terms"])
            for source, path in zip(top_sources, top_paths)
        )
        rows.append(
            {
                "query": meta["query"],
                "expected_hit_top3": expected_hit,
                "top3_sources": top_sources,
                "top3_scores": [round(float(sims[i]), 4) for i in top_idx],
            }
        )
    return rows


def summarize(name, corpus_time, query_times, query_batch_time, retrieval_rows):
    return {
        "model": name,
        "corpus_encode_seconds": round(corpus_time, 3),
        "query_single_avg_seconds": round(statistics.mean(query_times), 3),
        "query_single_p95_seconds": round(max(query_times), 3),
        "query_batch_seconds_for_5": round(query_batch_time, 3),
        "expected_hits_top3": sum(1 for row in retrieval_rows if row["expected_hit_top3"]),
        "retrieval_probe": retrieval_rows,
    }


def main():
    chunks = load_chunks()
    texts = [c["text"] for c in chunks]
    queries = [q["query"] for q in QUERIES]

    print("Loading current BGE-M3 OpenVINO model on CPU...", flush=True)
    current_model = OVEmbedder("BAAI/bge-m3", device="CPU")
    current_model.return_sparse = False
    start = time.perf_counter()
    current_query_embs, current_query_times, current_query_batch = encode_current_model(current_model, queries)
    current_total_query = time.perf_counter() - start

    print(f"Encoding {len(chunks)} corpus chunks with BGE-M3...", flush=True)
    start = time.perf_counter()
    current_corpus_batch = current_model.encode(texts, batch_size=8, max_length=512)["dense_vecs"]
    current_corpus_time = time.perf_counter() - start

    current_probe = retrieval_probe(chunks, current_corpus_batch, current_query_embs)

    print("Loading paraphrase-multilingual-mpnet-base-v2 on CPU...", flush=True)
    mpnet_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    start = time.perf_counter()
    mpnet_query_embs, mpnet_query_times, mpnet_query_batch = encode_mpnet_model(mpnet_model, queries)
    mpnet_query_total = time.perf_counter() - start

    print(f"Encoding {len(chunks)} corpus chunks with MPNet...", flush=True)
    start = time.perf_counter()
    mpnet_corpus_embs = mpnet_model.encode(
        texts,
        batch_size=8,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    mpnet_corpus_time = time.perf_counter() - start
    mpnet_probe = retrieval_probe(chunks, mpnet_corpus_embs, mpnet_query_embs)

    report = {
        "corpus_sample_size": len(chunks),
        "notes": [
            "This benchmark measures dense embedding CPU speed and a small retrieval proxy only.",
            "It does not include reranker latency, Qdrant I/O, prompt building, or Sarvam generation time.",
            "The current production stack also uses BGE-M3 sparse signals; this comparison is dense-only.",
        ],
        "results": [
            summarize("bge-m3-openvino-cpu", current_corpus_time, current_query_times, current_query_batch, current_probe),
            summarize("paraphrase-multilingual-mpnet-base-v2", mpnet_corpus_time, mpnet_query_times, mpnet_query_batch, mpnet_probe),
        ],
        "raw_query_timing_seconds": {
            "bge_m3_total_query_stage": round(current_total_query, 3),
            "mpnet_total_query_stage": round(mpnet_query_total, 3),
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
