#!/usr/bin/env python3
"""Add retrieval metadata to existing Qdrant points without re-embedding.

Stop the local chatbot/backend before running with ``--apply`` because embedded
Qdrant permits a single process to open its storage directory.
"""

import argparse
import os
from pathlib import Path

from qdrant_client import QdrantClient

from index_metadata import derive_retrieval_metadata


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "04_embeddings_and_kg" / "db" / "qdrant_local"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write metadata; default is dry-run")
    parser.add_argument("--force", action="store_true", help="replace existing metadata version")
    parser.add_argument("--collection", default=os.getenv("CHIPPY_QDRANT_COLLECTION", "db3"))
    parser.add_argument("--path", default=os.getenv("CHIPPY_QDRANT_LOCAL_PATH", str(DEFAULT_PATH)))
    args = parser.parse_args()

    client = QdrantClient(path=args.path)
    offset = None
    scanned = updated = 0
    while True:
        points, offset = client.scroll(
            collection_name=args.collection, offset=offset, limit=100,
            with_payload=True, with_vectors=False,
        )
        for point in points:
            payload = point.payload or {}
            if payload.get("metadata_version") == 1 and not args.force:
                continue
            metadata = derive_retrieval_metadata(payload.get("source", ""), payload.get("text", ""))
            scanned += 1
            if args.apply:
                client.set_payload(
                    collection_name=args.collection, payload=metadata, points=[point.id]
                )
            updated += 1
        if offset is None:
            break

    mode = "updated" if args.apply else "would update"
    print(f"Scanned {scanned} eligible point(s); {mode} {updated} point(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
