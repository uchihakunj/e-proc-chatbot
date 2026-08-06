@echo off
echo ========================================================
echo   CHiPS e-Procurement Chatbot - CPU ONLY (Windows)
echo ========================================================

:: 1. Force Ollama to ignore Intel and NVIDIA GPUs
set OLLAMA_INTEL_GPU=false
set OLLAMA_LLM_LIBRARY=cpu

:: 2. Allow GPU acceleration for ONNX/OpenVINO
:: set CUDA_VISIBLE_DEVICES=-1

:: 3. Restart Ollama in this terminal so it picks up the CPU flags
echo Stopping any running Ollama instance...
powershell -Command "Stop-Process -Name 'ollama*' -Force -ErrorAction SilentlyContinue"
ping 127.0.0.1 -n 3 >nul

echo Starting Ollama in CPU-only mode (background)...
start /B ollama serve >nul 2>&1
ping 127.0.0.1 -n 4 >nul

:: 4. Start Voice Server (background)
set PYTHON=%~dp0.venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

echo Starting Voice Server on port 5050 (background)...
if not exist "%~dp0logs" mkdir "%~dp0logs"
start /B "" "%PYTHON%" "%~dp006_voice\voice_server.py" > "%~dp0logs\voice_server.log" 2>&1
ping 127.0.0.1 -n 3 >nul

:: 5. Start the Application Stack
echo Starting Node.js UI and Flask Backend...
set NODE_ENV=production
set ENVIRONMENT=production
set USE_WAITRESS=true
if "%FLASK_PORT%"=="" set FLASK_PORT=5000
if "%FLASK_URL%"=="" set FLASK_URL=http://127.0.0.1:%FLASK_PORT%
if "%FLASK_TIMEOUT_MS%"=="" set FLASK_TIMEOUT_MS=300000
if "%WAITRESS_THREADS%"=="" set WAITRESS_THREADS=8
if "%MAX_CONCURRENT_RAG_REQUESTS%"=="" set MAX_CONCURRENT_RAG_REQUESTS=8
if "%RAG_REQUEST_QUEUE_TIMEOUT_SECONDS%"=="" set RAG_REQUEST_QUEUE_TIMEOUT_SECONDS=2.0
cd "%~dp005_webui\nodejs"
node server.js

