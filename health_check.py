"""
health_check.py
==============
For every kept document, verify the full pipeline:
  1. structured.md exists with real (non-garbled) text
  2. chunk files exist on disk
  3. points exist in Qdrant
Flags anything broken: missing OCR, Krutidev garbage, no chunks, or not embedded.
"""

import re
from pathlib import Path
from collections import Counter
from qdrant_client import QdrantClient

ROOT        = Path(__file__).resolve().parent
STAGE2_OUT  = ROOT / '01_preprocessing' / 'stage2_output'
CHUNK_OUT   = ROOT / '03_chunking' / 'output'
QDRANT_PATH = ROOT / '04_embeddings_and_kg' / 'db' / 'qdrant_local'
COLLECTION  = 'db3'

KRUTI_PAT  = re.compile(r'NRrhlx|jkT;|fyfeVsM|Hk\.Mkj|Ã˜|\bfu;e\b')
DEVANAGARI = re.compile(r'[ऀ-ॿ]')


def assess_text(md_path: Path) -> str:
    if not md_path.exists():
        return 'NO structured.md'
    txt = md_path.read_text(encoding='utf-8', errors='replace')
    body = re.sub(r'<!--.*?-->', '', txt).strip()
    if len(body) < 100:
        return 'EMPTY/too short'
    if '[OCR failed' in txt:
        return 'OCR FAILED markers'
    if KRUTI_PAT.search(txt) and not DEVANAGARI.search(txt):
        return 'KRUTIDEV garbage'
    deva = len(DEVANAGARI.findall(txt))
    if deva > 200:
        return f'OK (Hindi, {len(body):,} chars)'
    return f'OK (English, {len(body):,} chars)'


def main():
    # Qdrant source counts
    client = QdrantClient(path=str(QDRANT_PATH))
    qsrc = Counter()
    offset = None
    while True:
        pts, offset = client.scroll(COLLECTION, limit=500, offset=offset, with_payload=['source'])
        for p in pts:
            qsrc[p.payload.get('source', '?')] += 1
        if offset is None:
            break
    total_pts = sum(qsrc.values())
    client.close()

    # All docs that have a chunk folder
    chunk_folders = sorted(d.name for d in CHUNK_OUT.iterdir() if d.is_dir())

    print(f'{"DOCUMENT":<46} {"MD/OCR":<26} {"CHUNKS":>6} {"QDRANT":>7}  STATUS')
    print('-' * 108)

    problems = []
    for doc in chunk_folders:
        md_status   = assess_text(STAGE2_OUT / doc / 'structured.md')
        disk_chunks = len(list((CHUNK_OUT / doc).rglob('*_chunk_*.txt')))
        q_pts       = qsrc.get(doc, 0)

        ok = ('OK' in md_status) and disk_chunks > 0 and q_pts > 0
        # Some docs were chunked directly from PDF (no structured.md) — still valid if embedded
        if md_status == 'NO structured.md' and disk_chunks > 0 and q_pts > 0:
            md_status = 'direct (no OCR step)'
            ok = True

        flag = 'OK' if ok else '*** CHECK ***'
        if not ok:
            problems.append(doc)
        print(f'{doc[:44]:<46} {md_status[:25]:<26} {disk_chunks:>6} {q_pts:>7}  {flag}')

    # Docs in Qdrant but with no chunk folder (orphans)
    orphans = [s for s in qsrc if s not in chunk_folders and s != '?']
    print('-' * 108)
    print(f'Total Qdrant points: {total_pts}  |  Documents: {len(chunk_folders)}')
    if orphans:
        print(f'\nOrphan sources in Qdrant (no chunk folder): {len(orphans)}')
        for o in orphans:
            print(f'  {o}  ({qsrc[o]} pts)')
    if problems:
        print(f'\nDocuments needing attention: {len(problems)}')
        for p in problems:
            print(f'  - {p}')
    else:
        print('\nAll documents healthy.')


if __name__ == '__main__':
    main()
