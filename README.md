# 🤖 CHiPS e-Procurement RAG Chatbot

An AI-powered e-Procurement assistant designed to answer queries based on Chhattisgarh e-Procurement store rules and procurement guidelines using Retrieval-Augmented Generation (RAG) powered by **Gemma 3 (4B)**.

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

> 💡 **Important for Windows Users during installation:**  
> When installing Python, make sure to check the box **"Add Python to PATH"**.

---

## 🚀 Step-by-Step Manual Setup

### Step 1: Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/YOUR_USERNAME/E-PROC-CHATBOT_ANTI_GRAVITY.git
cd E-PROC-CHATBOT_ANTI_GRAVITY
```

---

### Step 2: Create Configuration File

Copy `.env.template` to create your configuration file `.env`:

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

```bash
cd 05_webui/nodejs
npm install
cd ../..
```

---

### Step 5: Setup & Download Gemma 3 (4B)

```bash
# Start Ollama service (if not running)
ollama serve

# Pull Gemma 3 4B model
ollama pull gemma3:4b
```

---

## 🚀 Launching the Application

* **Windows (Automated):** `.\setup_and_run.ps1` or `start_cpu.bat`
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

Open your browser and navigate to:  
👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🛑 How to Stop the Application

- **In Terminal:** Press `Ctrl + C`
- **Force Stop via Command:**
  * **Windows (PowerShell):** `Stop-Process -Name "node","python","ollama*" -Force -ErrorAction SilentlyContinue`
  * **Windows (CMD):** `taskkill /F /IM node.exe /IM python.exe /IM ollama.exe`
  * **Linux / macOS:** `pkill -f "node|python|ollama"`

---

## ❓ Troubleshooting

### 1. 'python' or 'pip' is not recognized
Ensure Python was added to system PATH during installation, then restart your terminal.

### 2. PowerShell execution policy error (.ps1 script blocked)
Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. "RAG backend is unreachable"
Ensure `ollama pull gemma3:4b` has completed and `ollama serve` is active.
