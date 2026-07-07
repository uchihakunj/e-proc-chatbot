@echo off
echo ========================================================
echo   CHiPS e-Procurement Chatbot - CPU ONLY (Windows)
echo ========================================================

:: 1. Force Ollama to ignore Intel and NVIDIA GPUs
set OLLAMA_INTEL_GPU=false
set OLLAMA_LLM_LIBRARY=cpu

:: 2. Force Python (PyTorch/OpenVINO) to ignore GPUs
set CUDA_VISIBLE_DEVICES=-1

:: 3. Restart Ollama in this terminal so it picks up the CPU flags
echo Stopping any running Ollama instance...
powershell -Command "Stop-Process -Name 'ollama*' -Force -ErrorAction SilentlyContinue"
timeout /t 2 >nul

echo Starting Ollama in CPU-only mode (background)...
start /B ollama serve >nul 2>&1
timeout /t 3 >nul

:: 4. Start the Application Stack
echo Starting Node.js UI and Flask Backend...
cd 05_webui\nodejs
node server.js
