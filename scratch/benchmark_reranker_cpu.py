import json
import statistics
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "03_chunking" / "output"
sys.path.insert(0, str(ROOT / "04_embeddings_and_kg" / "scripts"))

from ov_reranker import OVReranker

try:
    from FlagEmbedding import FlagReranker
except Exception:
    FlagReranker = None


QUERIES = [
    "What is e-Procurement?",
    "Vendor registration kaise karein?",
    "What is EMD and when is it refunded?",
    "Tender eligibility criteria kaise check karun?",
    "How do I submit my technical and price bid online?",
]


REPEATS = 5


def load_chunks(limit=20):
    chunks = []
    for path in sorted(CHUNK_DIR.rglob("*_chunk_*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        chunks.append(
            {
                "path": str(path.relative_to(CHUNK_DIR)),
                "text": text[:1500],
            }
        )
        if len(chunks) >= limit:
            break
    return chunks


def build_pair_batches(chunks):
    docs = [chunk["text"] for chunk in chunks]
    per_query_pairs = []
    for idx, query in enumerate(QUERIES):
        start = idx % max(1, len(docs) - 4)
        selected = docs[start : start + 5]
        if len(selected) < 5:
            selected = (selected + docs)[:5]
        per_query_pairs.append([[query, doc] for doc in selected])
    return per_query_pairs


def benchmark_model(label, model, per_query_pairs):
    warm_pairs = per_query_pairs[0]
    model.compute_score(warm_pairs, normalize=True, max_length=256)

    single_query_runs = []
    for _ in range(REPEATS):
        for pairs in per_query_pairs:
            start = time.perf_counter()
            scores = model.compute_score(pairs, normalize=True, max_length=256)
            elapsed = time.perf_counter() - start
            single_query_runs.append(elapsed)
            if not scores:
                raise RuntimeError(f"{label} returned no scores")

    all_pairs = [pair for pairs in per_query_pairs for pair in pairs]
    start = time.perf_counter()
    batch_scores = model.compute_score(all_pairs, normalize=True, max_length=256)
    batch_time = time.perf_counter() - start
    if len(batch_scores) != len(all_pairs):
        raise RuntimeError(
            f"{label} returned {len(batch_scores)} scores for {len(all_pairs)} pairs"
        )

    return {
        "model": label,
        "pairs_per_query": len(per_query_pairs[0]),
        "query_count": len(per_query_pairs),
        "single_query_repeats": REPEATS,
        "total_pairs_batch": len(all_pairs),
        "query_single_avg_seconds": round(statistics.mean(single_query_runs), 3),
        "query_single_median_seconds": round(statistics.median(single_query_runs), 3),
        "query_single_min_seconds": round(min(single_query_runs), 3),
        "query_single_p95_seconds": round(max(single_query_runs), 3),
        "batch_seconds_for_all_pairs": round(batch_time, 3),
        "pairs_per_second_batch": round(len(all_pairs) / batch_time, 2),
        "raw_single_query_seconds": [round(x, 3) for x in single_query_runs],
    }


def main():
    chunks = load_chunks()
    if len(chunks) < 5:
        raise RuntimeError("Need at least 5 chunks to benchmark reranker")

    per_query_pairs = build_pair_batches(chunks)
    results = []

    print("Loading current reranker: OpenVINO bge-reranker-v2-m3 on CPU...", flush=True)
    ov_model = OVReranker("BAAI/bge-reranker-v2-m3", device="CPU")
    results.append(benchmark_model("bge-reranker-v2-m3-openvino-cpu", ov_model, per_query_pairs))

    if FlagReranker is not None:
        print("Loading comparison reranker: CPU FlagReranker...", flush=True)
        flag_model = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)
        results.append(benchmark_model("bge-reranker-v2-m3-flag-cpu", flag_model, per_query_pairs))

    report = {
        "notes": [
            "Measures isolated reranker latency only, using 5 candidate documents per query.",
            "This mirrors the current .env tuning where RERANK_MAX_CANDS=5.",
            "It excludes embedding, Qdrant, prompt assembly, and Sarvam generation.",
        ],
        "results": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
