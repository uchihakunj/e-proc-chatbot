# eproc-chatbot

This repository is now organized so that runtime code stays near the top level,
while reports, diagnostics, ad-hoc scripts, and request documents live in
dedicated folders.

## Top-Level Layout

- `01_preprocessing` to `06_voice`: primary pipeline and application modules
- `docs/reports`: evaluation reports, benchmarks, and sample-answer documents
- `docs/requests`: Word documents and request artifacts
- `diagnostics`: JSON and text outputs from audits, traces, and debugging runs
- `scripts/dev`: one-off debugging and patch helper scripts
- `scripts/maintenance`: repository maintenance utilities
- `scripts/pipeline`: non-primary pipeline helper runners
- `tests/manual`: root-level manual and exploratory test scripts
- `utils`: shared utility modules, including configuration helpers
- `eval`, `reports`, `scratch`, `tmp`, `output`, `outputs`: existing analysis and experiment areas

## Main Runtime Entry Points

- Flask RAG backend: `python 05_webui/app.py`
- Node UI proxy: `cd 05_webui/nodejs && npm install && npm start`
- Voice server: `python 06_voice/voice_server.py`
- CPU stack bootstrap: `./start_cpu.bat` on Windows or `./start_cpu.sh` on Unix-like shells
- Health check: `python scripts/maintenance/health_check.py`
- Manifest rebuild: `python scripts/maintenance/rebuild_manifest.py`

## Pipeline

### Stage 01 - Preprocessing

- Run `python 01_preprocessing/run_stage1.py`
  - default input: `01_preprocessing/input_pdfs`
  - default output: `01_preprocessing/stage1_output`
- Run `python 01_preprocessing/run_stage2.py`
  - default input: `01_preprocessing/stage1_output`
  - default output: `01_preprocessing/stage2_output`

### Stage 02 - Optimization

- Run `python 02_optimization/optimize.py`

### Stage 03 - Chunking

- Run `python 03_chunking/docling_chunker.py`

### Stage 04 - Embeddings and Vector DB

- Run `python 04_embeddings_and_kg/scripts/embeddings_production.py`

### Stage 05 - Web UI and Flask Backend

- Start Flask: `python 05_webui/app.py`
- Start UI: `cd 05_webui/nodejs && npm install && npm start`
- Open `http://localhost:3000`

## Notes

- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` are still useful when running fully local model flows.
- Voice STT and TTS live in `06_voice`.
- Sarvam and Ollama startup choices depend on environment variables set before starting the UI/backend processes.
