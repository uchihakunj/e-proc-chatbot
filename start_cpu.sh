#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${ROOT_DIR}/.venv/bin/python"

ENABLE_VOICE="${ENABLE_VOICE:-false}"
for arg in "$@"; do
  if [[ "$arg" == "--voice" ]]; then
    ENABLE_VOICE="true"
  fi
done

echo "========================================================"
echo "  CHiPS e-Procurement Chatbot - CPU ONLY (Rocky Linux)"
echo "========================================================"

cd "${ROOT_DIR}"

# Force Python/OpenVINO/PyTorch paths to stay on CPU.
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:--1}"
export EMBEDDER_BACKEND="${EMBEDDER_BACKEND:-openvino}"
export EMBEDDER_DEVICE="${EMBEDDER_DEVICE:-CPU}"
export RERANKER_BACKEND="${RERANKER_BACKEND:-openvino}"
export RERANKER_DEVICE="${RERANKER_DEVICE:-CPU}"
export FLASK_URL="${FLASK_URL:-http://127.0.0.1:5000}"
export PORT="${PORT:-3000}"
export NODE_ENV="${NODE_ENV:-production}"
export USE_WAITRESS="${USE_WAITRESS:-true}"
export PYTHON="${PYTHON:-$VENV_PYTHON}"

if [[ ! -x "${PYTHON}" ]]; then
  echo "ERROR: Python executable not found at ${PYTHON}"
  echo "Create the virtualenv first, or export PYTHON=/path/to/python"
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: node is not installed or not on PATH"
  exit 1
fi

echo "Using Python: ${PYTHON}"
echo "Using Node: $(command -v node)"
echo "Frontend URL: http://0.0.0.0:${PORT}"
echo "Backend URL: ${FLASK_URL}"
echo "Embedder: ${EMBEDDER_BACKEND} on ${EMBEDDER_DEVICE}"
echo "Reranker: ${RERANKER_BACKEND} on ${RERANKER_DEVICE}"

if [[ "${ENABLE_VOICE}" == "true" ]]; then
  mkdir -p "${ROOT_DIR}/logs"
  echo "Starting Voice Server on port 5050..."
  "${PYTHON}" "${ROOT_DIR}/06_voice/voice_server.py" > "${ROOT_DIR}/logs/voice_server.log" 2>&1 &
  echo "Voice Server launched in background (Log: logs/voice_server.log)"
fi

cd "${ROOT_DIR}/05_webui/nodejs"
exec node server.js
