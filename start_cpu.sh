#!/bin/bash
echo "========================================================"
echo "  CHiPS e-Procurement Chatbot - CPU ONLY (Rocky Linux)"
echo "========================================================"

# Force Python (PyTorch/OpenVINO) to ignore GPUs
export CUDA_VISIBLE_DEVICES="-1"

echo "Starting Application Stack (Node.js + Flask)..."
cd 05_webui/nodejs
node server.js
