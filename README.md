CHiPS RAG — Minimal Run Guide

Stage 01 — Preprocessing
- Run `python 01_preprocessing/run_stage1.py`
  - default input: `01_preprocessing\input_pdfs`
  - default output: `01_preprocessing\stage1_output`
- Run `python 01_preprocessing/run_stage2.py
  - default input: `01_preprocessing\stage1_output` 
  - default output: `01_preprocessing\stage2_output`

Stage 02 — Optimization
- Run `python 02_optimization/optimize.py`

Stage 03 — Chunking
- Run `python 03_chunking/docling_chunker.py`

Stage 04 — Embeddings & Vector DB
- Run `python 04_embeddings_and_kg/scripts/embeddings_production.py` to generate or manage the vector DB

Stage 05 — Web UI & Flask RAG Backend
- Start Flask RAG backend: `python 05_webui/app.py`
  - Requires Ollama running locally with gemma3-q3km:12b model
  - Serves streaming endpoint at http://localhost:5000/api/stream
  - Set environment vars: `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` to avoid network timeouts
- Run the Node server: `node 05_webui/nodejs/server.js`
  - Auth Username: `admin`
  - Auth Password: `StrongPass123`
  - Accesses Flask backend at http://localhost:5000
