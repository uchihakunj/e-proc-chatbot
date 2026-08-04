# 🤖 CHiPS e-Procurement RAG Chatbot

An AI-powered e-Procurement assistant designed to answer queries based on Chhattisgarh e-Procurement Store Rules and procurement guidelines using Retrieval-Augmented Generation (RAG) powered by **Gemma 3 (4B)**.

---

## ⚡ 1-Click Automated Setup & Launch (Windows)

If you are on Windows, simply open PowerShell in the project folder and run:

```powershell
.\setup_and_run.ps1
```

> **What this script does automatically:**
> 1. Verifies your system has Python 3.10+, Node.js, and Ollama installed.
> 2. Copies `.env.template` to `.env` if not present.
> 3. Creates the Python virtual environment (`.venv`) and installs all dependencies from `requirements.txt`.
> 4. Installs Node.js frontend dependencies in `05_webui/nodejs`.
> 5. Starts Ollama and downloads the `gemma3:4b` model.
> 6. Launches the application stack and opens `http://localhost:3000` in your web browser.

---

## 📋 Manual Setup Guide

If you prefer to set up manually or are running on Linux/macOS, follow the steps below:

### 💻 Prerequisites

| Software | Required Version | Download Link |
| :--- | :--- | :--- |
| **Python** | 3.10 or higher | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | v18 or higher | [nodejs.org](https://nodejs.org/) |
| **Ollama** | Latest | [ollama.com](https://ollama.com/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |

> 💡 **Important (Windows Users):**  
> During Python installation, make sure you enable **"Add Python to PATH"**.

---

## 🚀 Step-by-Step Manual Setup

### Step 1: Clone the Repository

Open PowerShell, Command Prompt, Git Bash, or Terminal and run:

```bash
git clone https://github.com/CMITF/eProcurement-Project.git
cd E-PROC-CHATBOT_ANTI_GRAVITY
```

---

### Step 2: Create Configuration File

Create the active configuration file from the template:

* **Windows (PowerShell):** `Copy-Item .env.template .env`
* **Windows (CMD):** `copy .env.template .env`
* **Linux / macOS:** `cp .env.template .env`

---

### Step 3: Set Up Python Virtual Environment

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Install Node.js UI Dependencies

Navigate to the frontend directory and install all required packages:

```bash
cd 05_webui/nodejs
npm install
cd ../..
```

---

### Step 5: Setup & Download Gemma 3 (4B)

Ensure Ollama is installed and running:

```bash
# Start Ollama service (if not running)
ollama serve

# Download Gemma 3 (4B) model
ollama pull gemma3:4b
```

---

## 🚀 Launching the Application

* **Windows (Automated 1-Click):** `.\setup_and_run.ps1` or `start_cpu.bat`
* **Linux / macOS:** 
  ```bash
  chmod +x start_cpu.sh
  ./start_cpu.sh
  ```
* **Manual Launch:**
  ```bash
  cd 05_webui/nodejs
  npm start
  ```

---

## 🌐 Accessing the Web UI

Once the application has started successfully, open your web browser and go to:

👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🛑 How to Stop the Application

### Method 1: Stop from Terminal
Press `Ctrl + C` in the running terminal.

---

### Method 2: Force Stop All Services
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

## ❓ Troubleshooting

### 1. 'python' or 'pip' is not recognized
- Reinstall Python and make sure **"Add Python to PATH"** is enabled.
- Restart your terminal.

### 2. PowerShell Script Execution Policy Error
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. "RAG backend is unreachable"
- Verify Ollama is active (`ollama serve`) and model is pulled (`ollama pull gemma3:4b`).
- Check that `pip install -r requirements.txt` completed without errors.
- Ensure ports **3000**, **5000**, or **8080** are not blocked by a firewall.

### 4. Port 3000 Is Already in Use
Terminate existing Node processes using the Stop command above, then restart the app.
