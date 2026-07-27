import json
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY")
CHUNK_DIR = ROOT / "03_chunking" / "output"
sys.path.insert(0, str(ROOT / "04_embeddings_and_kg" / "scripts"))

from ov_reranker import OVReranker
from FlagEmbedding import FlagReranker

query = "How can a bidder submit the technical bid and price bid on the e-Procurement portal?"
chunks = []
for path in sorted(CHUNK_DIR.rglob("*_chunk_*.txt")):
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        continue
    chunks.append({"path": str(path.relative_to(CHUNK_DIR)), "text": text[:1500]})
    if len(chunks) >= 5:
        break
pairs = [[query, c["text"]] for c in chunks]

report = {"query": query, "candidates": [c["path"] for c in chunks], "results": []}

for label, model in [
    ("openvino_cpu", OVReranker("BAAI/bge-reranker-v2-m3", device="CPU")),
    ("flag_cpu", FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)),
]:
    model.compute_score(pairs, normalize=True, max_length=256)
    start = time.perf_counter()
    scores = model.compute_score(pairs, normalize=True, max_length=256)
    elapsed = time.perf_counter() - start
    report["results"].append({
        "model": label,
        "seconds": round(elapsed, 3),
        "scores": [round(float(s), 4) for s in scores],
        "best_candidate": chunks[max(range(len(scores)), key=lambda i: scores[i])]["path"],
    })

print(json.dumps(report, ensure_ascii=False, indent=2))
