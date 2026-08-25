# Rocky Linux Deployment

This repo can run on Rocky Linux in a CPU-only mode with:

- Sarvam API as the primary answer provider
- Ollama as the fallback provider
- OpenVINO forced onto CPU for embedder/reranker
- Node/Express serving the frontend and proxying to Flask

## Expected layout

Clone or copy the repo to:

```bash
/opt/eproc-chatbot
```

## 1. Install system packages

```bash
sudo dnf install -y \
  git \
  nodejs \
  npm \
  python3.11 \
  python3.11-pip \
  python3.11-devel \
  tesseract \
  tesseract-langpack-hin \
  poppler-utils
```

Notes:

- If your Rocky host ships a different supported Python version for this repo, adjust accordingly.
- `tesseract` and `poppler-utils` are needed for OCR/PDF workflows.

## 2. Create the Python environment

```bash
cd /opt/eproc-chatbot
python3.11 -m venv .venv
source .venv/bin/activate
# Avoid a host-level pip configuration redirecting installs to ~/.local.
unset PIP_USER PIP_TARGET PIP_PREFIX PYTHONUSERBASE
python -m pip install --upgrade pip
python -m pip install --no-user -r requirements.txt
python -c 'import requests; print("Python dependencies are installed in", __import__("sys").prefix)'
```

## 3. Install Node dependencies

```bash
cd /opt/eproc-chatbot/05_webui/nodejs
npm install
```

## 4. Configure environment

Create `/opt/eproc-chatbot/.env` and ensure it includes at least:

```env
SARVAM_API_KEY=your_real_key
SARVAM_MODEL=sarvam-105b
ANSWER_PROVIDER=sarvam
ENABLE_MODEL_FALLBACK=true

OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3:4b
OLLAMA_FALLBACK_MODEL=gemma3:4b

RERANKER_BACKEND=openvino
RERANKER_DEVICE=CPU
EMBEDDER_BACKEND=openvino
EMBEDDER_DEVICE=CPU

CUDA_VISIBLE_DEVICES=-1
USE_WAITRESS=true
PORT=3000
FLASK_URL=http://127.0.0.1:5050
```

## 5. Start manually

```bash
cd /opt/eproc-chatbot
chmod +x start_cpu.sh
./start_cpu.sh
```

If startup reports `No module named requests`, the packages were installed into
the wrong Python environment. Recreate the environment and install with the
commands in step 2; use `python -m pip`, not `pip`.

Expected startup lines include:

- `Embedder backend: OpenVINO on CPU`
- `Reranker backend: OpenVINO on CPU`

The UI should be available at:

```bash
http://your-server:3000
```

## 6. Install as a systemd service

Copy the included unit:

```bash
sudo cp deploy/rocky-linux/eproc-chatbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now eproc-chatbot
sudo systemctl status eproc-chatbot
```

Logs:

```bash
journalctl -u eproc-chatbot -f
```

## Notes

- `server.js` starts Flask automatically, so a separate Flask service is not required.
- If Ollama is used as fallback, install and run Ollama separately on the Rocky host.
- If OpenVINO CPU wheels fail on your exact Rocky/Python combination, switch to:

```env
RERANKER_BACKEND=flag
EMBEDDER_BACKEND=flag
```

That keeps the app CPU-only without OpenVINO acceleration.
