"""
rebuild_manifest.py
==================
Rebuilds .embeddings_manifest.json to match the CURRENT state:
  - Every chunk file currently on disk is marked as indexed
  - IDs are offset high (100000+) so future uploads never collide with the
    existing Qdrant point IDs

Run this after bulk edits (deletions, re-chunking) to stop the incremental
embedder from re-embedding already-indexed chunks (which creates duplicates).
"""

import json
from datetime import datetime
from pathlib import Path

ROOT      = Path(__file__).resolve().parent
CHUNK_DIR = ROOT / '03_chunking' / 'output'
MANIFEST  = ROOT / '04_embeddings_and_kg' / '.embeddings_manifest.json'

# Start IDs well above any existing Qdrant point ID to guarantee no collision
ID_BASE = 100_000


def main():
    disk_files = sorted(str(f.relative_to(CHUNK_DIR))
                        for f in CHUNK_DIR.rglob('*_chunk_*.txt'))
    print(f'Chunk files on disk: {len(disk_files)}')

    indexed = {}
    for i, rel in enumerate(disk_files):
        indexed[rel] = {'id': ID_BASE + i, 'indexed_at': datetime.now().isoformat()}

    data = {
        'version': '1.0',
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
        'indexed_chunks': indexed,
        'total_indexed': len(indexed),
        'collection': 'db3',
    }
    MANIFEST.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f'Manifest rebuilt: {len(indexed)} entries, IDs {ID_BASE}–{ID_BASE+len(indexed)-1}')
    print('Future uploads will only embed genuinely new chunks.')


if __name__ == '__main__':
    main()
