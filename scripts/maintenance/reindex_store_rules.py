"""Remove only the retired CG Store Rules vectors, then index the promoted set."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue


ROOT = Path(__file__).resolve().parents[2]
QDRANT = ROOT / "04_embeddings_and_kg" / "db" / "qdrant_local"
MANIFEST = ROOT / "04_embeddings_and_kg" / ".embeddings_manifest.json"
COLLECTION = "db3"
SOURCE = "store purchase rule cg"
EMBEDDER = ROOT / "04_embeddings_and_kg" / "scripts" / "embeddings_production.py"


def main() -> None:
    client = QdrantClient(path=str(QDRANT))
    try:
        before = client.count(COLLECTION, count_filter=Filter(must=[
            FieldCondition(key="source", match=MatchValue(value=SOURCE))
        ])).count
        if before:
            client.delete(COLLECTION, points_selector=Filter(must=[
                FieldCondition(key="source", match=MatchValue(value=SOURCE))
            ]))
        after = client.count(COLLECTION, count_filter=Filter(must=[
            FieldCondition(key="source", match=MatchValue(value=SOURCE))
        ])).count
    finally:
        client.close()
    if after:
        raise RuntimeError(f"Expected no retired Store Rules vectors, found {after}")

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    old_keys = [key for key in data["indexed_chunks"] if "store purchase rule cg" in key.casefold()]
    for key in old_keys:
        del data["indexed_chunks"][key]
    data["total_indexed"] = len(data["indexed_chunks"])
    MANIFEST.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"retired_qdrant_vectors={before}")
    print(f"retired_manifest_entries={len(old_keys)}")

    completed = subprocess.run([sys.executable, str(EMBEDDER)], cwd=ROOT)
    if completed.returncode:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
