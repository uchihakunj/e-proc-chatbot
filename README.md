#  e-Procurement RAG Chatbot

An AI-powered e-Procurement assistant designed to answer queries based on Chhattisgarh e-Procurement Store Rules and procurement guidelines using Retrieval-Augmented Generation (RAG) powered by **Ollama (Gemma 3 4B / LLaMA 3.2)**, hybrid Qdrant vector retrieval, and OpenVINO acceleration.

---

## 📐 System Architecture

```
   ┌─────────────────────────────────────────────────────────┐
   │                     User Browser                        │
   │               http://localhost:3000                     │
   └──────────────────────────┬──────────────────────────────┘
                              │
                              ▼
   ┌─────────────────────────────────────────────────────────┐
   │        Node.js / Express Web UI (Port 3000)             │
   │            [05_webui/nodejs/server.js]                  │
   └──────────────────────────┬──────────────────────────────┘
                              │ Proxies RAG Requests
                              ▼
   ┌─────────────────────────────────────────────────────────┐
   │        Flask / Waitress RAG Backend (Port 5000)         │
   │                [05_webui/app.py]                        │
   └──────────────┬───────────────────────────┬──────────────┘
                  │                           │
                  ▼                           ▼
   ┌──────────────────────────────┐ ┌────────────────────────┐
   │  Qdrant Hybrid Vector DB     │ │     Ollama LLM Engine  │
   │  (Dense BGE-M3 + BM25)       │ │  (gemma3:4b / 11434)   │
   │  [04_embeddings_and_kg]      │ └────────────────────────┘
   └──────────────────────────────┘
```

---

## 📑 Table of Contents

- [💻 Prerequisites](#-prerequisites)
- [⚡ Quick Start Launch Options](#-quick-start-launch-options)
  - [Option A: Windows 1-Click Automated Setup](#option-a-windows-1-click-automated-setup)
  - [Option B: CPU-Optimized Launch Scripts](#option-b-cpu-optimized-launch-scripts)
- [📋 Manual Step-by-Step Setup Guide](#-manual-step-by-step-setup-guide)
  - [Step 1: Clone Repository](#step-1-clone-repository)
  - [Step 2: Environment Configuration](#step-2-environment-configuration)
  - [Step 3: Setup Python Virtual Environment](#step-3-setup-python-virtual-environment)
  - [Step 4: Install Node.js Frontend Dependencies](#step-4-install-nodejs-frontend-dependencies)
  - [Step 5: Setup Ollama & Download Model](#step-5-setup-ollama--download-model)
  - [Step 6: Launch Application Stack](#step-6-launch-application-stack)
- [📄 Ingesting New Documents & Running Pipeline](#-ingesting-new-documents--running-pipeline)
- [🎙️ Optional Voice Assistant Server](#️-optional-voice-assistant-server)
- [⚙️ Environment Configuration Reference](#️-environment-configuration-reference)
- [🛑 How to Stop the Application](#-how-to-stop-the-application)
- [❓ Troubleshooting & FAQ](#-troubleshooting--faq)

---

## 💻 Prerequisites

Ensure the following tools are installed on your machine before starting:

| Software | Required Version | Download Link | Notes |
| :--- | :--- | :--- | :--- |
| **Python** | `3.10` or higher | [python.org/downloads](https://www.python.org/downloads/) | **Windows users:** Ensure **"Add Python to PATH"** is checked during installation |
| **Node.js** | `v18` or higher | [nodejs.org](https://nodejs.org/) | Includes `npm` package manager |
| **Ollama** | Latest | [ollama.com](https://ollama.com/) | Local LLM execution engine |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) | Version control |

---

## ⚡ Quick Start Launch Options

### Option A: Windows 1-Click Automated Setup

If you are on Windows, you can perform full environment verification, dependency installation, model setup, and application launch using PowerShell:

1. Open PowerShell in the project directory.
2. Execute the launcher script:

```powershell
.\setup_and_run.ps1
```

> **What [setup_and_run.ps1](file:///c:/Users/HP/Desktop/eProcurement-Project/setup_and_run.ps1) automates:**
> 1. Verifies Python 3.10+, Node.js, and Ollama installation.
> 2. Copies [.env.template](file:///c:/Users/HP/Desktop/eProcurement-Project/.env.template) to `.env` if missing.
> 3. Creates the `.venv` virtual environment and installs all Python requirements from [requirements.txt](file:///c:/Users/HP/Desktop/eProcurement-Project/requirements.txt).
> 4. Installs Node.js UI dependencies in `05_webui/nodejs`.
> 5. Starts Ollama in background (if not running) and pulls `gemma3:4b`.
> 6. Launches the application stack and automatically opens `http://localhost:3000` in your web browser.

---

### Option B: CPU-Optimized Launch Scripts

If your environment is already set up and you wish to run with CPU optimization flags:

#### On Windows (CMD / Batch):

```cmd
start_cpu.bat
```
*(Runs [start_cpu.bat](file:///c:/Users/HP/Desktop/eProcurement-Project/start_cpu.bat))*

#### On Linux / macOS (Bash):

```bash
chmod +x start_cpu.sh
./start_cpu.sh
```
*(Runs [start_cpu.sh](file:///c:/Users/HP/Desktop/eProcurement-Project/start_cpu.sh))*

---

## 📋 Manual Step-by-Step Setup Guide

Follow these steps for a manual setup on any OS (Windows, Linux, macOS):

### Step 1: Clone Repository

Open your terminal / PowerShell and clone the repository:

```bash
git clone https://github.com/CMITF/eProcurement-Project.git
cd eProcurement-Project

```

---

### Step 2: Environment Configuration

Create your local `.env` configuration file from the provided template:

* **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.template .env
  ```
* **Windows (CMD):**
  ```cmd
  copy .env.template .env
  ```
* **Linux / macOS:**
  ```bash
  cp .env.template .env
  ```

---

### Step 3: Setup Python Virtual Environment

Create and activate a virtual environment, then install required packages from [requirements.txt](file:///c:/Users/HP/Desktop/eProcurement-Project/requirements.txt):

#### 1. Create Virtual Environment:
```bash
python -m venv .venv
```

#### 2. Activate Virtual Environment:
* **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
* **Windows (CMD):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
* **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

#### 3. Install Python Dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Install Node.js Frontend Dependencies

Navigate into `05_webui/nodejs` and install npm packages:

```bash
cd 05_webui/nodejs
npm install
cd ../..
```

---

### Step 5: Setup Ollama & Download Model

Make sure Ollama service is running, then pull the target LLM model (`gemma3:4b`):

```bash
# 1. Start Ollama service (if not already running as a system service)
ollama serve

# 2. In a new terminal window, pull the required model
ollama pull gemma3:4b
```

---

### Step 6: Launch Application Stack

Navigate to the Node.js frontend directory and start the server:

```bash
cd 05_webui/nodejs
node server.js
```

> ℹ️ **How it works:** [server.js](file:///c:/Users/HP/Desktop/eProcurement-Project/05_webui/nodejs/server.js) starts the Express UI server on port `3000` and automatically spawns the Flask RAG backend ([05_webui/app.py](file:///c:/Users/HP/Desktop/eProcurement-Project/05_webui/app.py)) on port `5000` if it is not already running.

Open your browser and visit:

👉 **[http://localhost:3000](http://localhost:3000)**

---

## 📄 Ingesting New Documents & Running Pipeline

If you add new procurement store rules or PDF guidelines and want to re-process and re-index them into the Qdrant vector database:

1. Place your input PDF documents into `01_preprocessing/input_pdfs/`.
2. Activate your Python virtual environment.
3. Run the master pipeline script [run_full_pipeline.py](file:///c:/Users/HP/Desktop/eProcurement-Project/run_full_pipeline.py):

```bash
python run_full_pipeline.py
```

### Pipeline Sequence:
1. **Stage 1 & 2 (OCR & Structure):** Runs PDF image conversion & Docling OCR structure extraction to generate markdown/JSON outputs in `01_preprocessing/stage2_output/`.
2. **Stage 3 (Semantic Chunking):** Runs [docling_chunker.py](file:///c:/Users/HP/Desktop/eProcurement-Project/03_chunking/docling_chunker.py) to split markdown into chunk files in `03_chunking/output/`.
3. **Stage 4 (Vector Embeddings):** Runs [embeddings_production.py](file:///c:/Users/HP/Desktop/eProcurement-Project/04_embeddings_and_kg/scripts/embeddings_production.py) to compute `BAAI/bge-m3` dense + BM25 sparse hybrid embeddings and store them in Qdrant (`04_embeddings_and_kg/db/qdrant_local`).

### Useful Pipeline CLI Flags:
* Skip embeddings step (chunking only):
  ```bash
  python run_full_pipeline.py --no-embed
  ```
* Dry run (inspect steps without modifying files):
  ```bash
  python run_full_pipeline.py --dry-run
  ```

---

## 🎙️ Optional Voice Assistant Server

The application includes an optional real-time voice interface powered by Speech-to-Text and Text-to-Speech endpoints.

### To start the Voice Server manually:
```bash
python 06_voice/voice_server.py
```
*(Listening on port `5050`)*

### To start with voice support on Linux/macOS:
```bash
./start_cpu.sh --voice
```

---

## ⚙️ Environment Configuration Reference

The [.env](file:///c:/Users/HP/Desktop/eProcurement-Project/.env.template) file allows you to customize ports, models, and retrieval parameters:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `FLASK_PORT` | `5000` | Port for Flask RAG backend |
| `PORT` | `3000` | Port for Express Web UI frontend |
| `OLLAMA_MODEL` | `gemma3:4b` | Default LLM model running in Ollama |
| `ANSWER_PROVIDER` | `ollama` | Primary answer synthesis provider (`ollama` / `sarvam`) |
| `CHIPPY_QDRANT_COLLECTION` | `db3` | Qdrant vector database collection name |
| `TOP_K_RETRIEVAL` | `20` | Candidate passages retrieved before reranking |
| `USE_WAITRESS` | `true` | Enables high-performance Waitress WSGI server |
| `WAITRESS_THREADS` | `8` | Worker thread count for Flask Waitress server |

---

## 🛑 How to Stop the Application

### Method 1: Terminal Interrupt
Press `Ctrl + C` in the active terminal window running `node server.js` or launcher scripts.

### Method 2: Terminate All Processes

* **Windows (PowerShell):**
  ```powershell
  Stop-Process -Name "node","python","ollama*" -Force -ErrorAction SilentlyContinue
  ```
* **Windows (CMD):**
  ```cmd
  taskkill /F /IM node.exe /IM python.exe /IM ollama.exe
  ```
* **Linux / macOS:**
  ```bash
  pkill -f "node|python|ollama"
  ```

---

## ❓ Troubleshooting & FAQ

### 1. `python` or `pip` is not recognized (Windows)
* Ensure Python 3.10+ is installed and **"Add Python to PATH"** was checked during installation.
* Close and re-open PowerShell/CMD.

### 2. PowerShell Script Execution Policy Error
If running `.\setup_and_run.ps1` gives a script execution policy restriction error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Backend Unreachable / Connection Error
* Ensure Ollama is running (`ollama serve`) and model is pulled (`ollama pull gemma3:4b`).
* Verify Python dependencies are installed in `.venv`:
  ```bash
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  ```
* Ensure ports `3000` and `5000` are free and not blocked by firewall.

### 4. Port 3000 or 5000 is Already in Use
Use the process kill commands in the [Stopping the Application](#-how-to-stop-the-application) section, then restart the application.

---
