import subprocess
import sys
import shutil
import os
from pathlib import Path

doc_name = 'Vigilance Manual (Updated 2021) English'
stage1_dir = Path('01_preprocessing/stage1_output') / doc_name
stage2_dir = Path('01_preprocessing/stage2_output') / doc_name
chunk_dir = Path('03_chunking/output') / doc_name

print('Running Stage 2 OCR...')
res = subprocess.run([sys.executable, '01_preprocessing/run_stage2.py', str(stage1_dir)])
if res.returncode != 0:
    print('Stage 2 failed')
    sys.exit(1)

print('Clearing old chunks...')
if chunk_dir.exists():
    shutil.rmtree(chunk_dir)
# Also remove flat files
for f in Path('03_chunking/output').glob(f'{doc_name}_chunk_*.txt'):
    f.unlink()

print('Chunking structured.md...')
res2 = subprocess.run([sys.executable, '03_chunking/docling_chunker.py', '--input', str(stage2_dir / 'structured.md'), '--output', str(chunk_dir)])
if res2.returncode != 0:
    print('Chunking failed')
    sys.exit(1)

print('Running embeddings...')
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
subprocess.run([sys.executable, '04_embeddings_and_kg/scripts/embeddings_production.py'], env=env)

print('Done!')
