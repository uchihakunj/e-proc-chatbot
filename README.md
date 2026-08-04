# 🤖 CHiPS e-Procurement RAG Chatbot

An AI-powered e-Procurement assistant designed to answer queries based on Chhattisgarh e-Procurement Store Rules and procurement guidelines using Retrieval-Augmented Generation (RAG).

---

# 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Quick Start Guide](#-quick-start-guide)
   - [Step 1: Clone the Repository](#step-1-clone-the-repository)
   - [Step 2: Create Configuration File](#step-2-create-configuration-file)
   - [Step 3: Set Up Python Virtual Environment](#step-3-set-up-python-virtual-environment)
   - [Step 4: Install Node.js UI Dependencies](#step-4-install-nodejs-ui-dependencies)
   - [Step 5: Setup & Start Ollama (AI Engine)](#step-5-setup--start-ollama-ai-engine)
3. [Launching the Application](#-launching-the-application)
4. [Accessing the Web UI](#-accessing-the-web-ui)
5. [How to Stop the Application](#-how-to-stop-the-application)
6. [Troubleshooting](#-troubleshooting)

---

# 💻 Prerequisites

Before running the application, ensure the following software is installed:

| Software | Required Version | Download |
| :--- | :--- | :--- |
| **Python** | 3.10 or higher | https://www.python.org/downloads/ |
| **Node.js** | v18 or higher | https://nodejs.org/ |
| **Ollama** | Latest | https://ollama.com/ |
| **Git** | Latest | https://git-scm.com/ |

> **Important (Windows Users):**
>
> During Python installation, ensure that **"Add Python to PATH"** is checked.

---

# 🚀 Quick Start Guide

## Step 1: Clone the Repository

Open PowerShell, Command Prompt, Git Bash, or Terminal and run:

```bash
git clone https://github.com/YOUR_USERNAME/E-PROC-CHATBOT_ANTI_GRAVITY.git
cd E-PROC-CHATBOT_ANTI_GRAVITY
```

---

## Step 2: Create Configuration File

Create your active `.env` file from the provided template.

### Windows (PowerShell)

```powershell
Copy-Item .env.template .env
```

### Windows (Command Prompt)

```cmd
copy .env.template .env
```

### Linux / macOS

```bash
cp .env.template .env
```

---

## Step 3: Set Up Python Virtual Environment

### Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate the Virtual Environment

#### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt)

```cmd
.\.venv\Scripts\activate.bat
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4: Install Node.js UI Dependencies

Navigate to the frontend directory and install the required packages.

```bash
cd 05_webui/nodejs
npm install
cd ../..
```

---

## Step 5: Setup & Start Ollama (AI Engine)

Ensure the Ollama service is running.

If not, start it:

```bash
ollama serve
```

Download the required model:

```bash
ollama pull llama3.2
```

---

# 🚀 Launching the Application

## Option A: Automated Startup (Recommended)

Run the startup script from the project root.

### Windows

```cmd
start_cpu.bat
```

### Linux / macOS

```bash
chmod +x start_cpu.sh
./start_cpu.sh
```

---

## Option B: Manual Startup

1. Open a terminal inside the project folder.
2. Activate the virtual environment.
3. Start the application.

```bash
cd 05_webui/nodejs
npm start
```

---

# 🌐 Accessing the Web UI

Once the application has started successfully, open your browser and visit:

```
http://localhost:3000
```

You can now begin interacting with the CHiPS e-Procurement Assistant.

---

# 🛑 How to Stop the Application

## Method 1: Stop from the Terminal

Press:

```
Ctrl + C
```

---

## Method 2: Force Stop All Services

### Windows (PowerShell)

```powershell
Stop-Process -Name "node","python","ollama*" -Force -ErrorAction SilentlyContinue
```

### Windows (Command Prompt)

```cmd
taskkill /F /IM node.exe /IM python.exe /IM ollama.exe
```

### Linux / macOS

```bash
pkill -f "node|python|ollama"
```

---

# ❓ Troubleshooting

## 1. `'python'` or `'pip'` is not recognized

**Solution**

- Reinstall Python.
- During installation, enable **"Add Python to PATH"**.
- Restart your terminal (or computer).

---

## 2. PowerShell Execution Policy Error

If you receive:

```
... cannot be loaded because running scripts is disabled ...
```

Run PowerShell as **Administrator** and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the virtual environment again.

---

## 3. "RAG backend is unreachable"

Possible causes:

- Ollama is not running.
- Required model is missing.
- Python dependencies are not installed.
- Backend service failed to start.

Verify:

```bash
ollama serve
```

Ensure the model exists:

```bash
ollama pull llama3.2
```

Reinstall dependencies if needed:

```bash
pip install -r requirements.txt
```

Also ensure that ports such as **3000**, **5000**, or **8080** are not blocked by your firewall.

---

## 4. Port 3000 Is Already in Use

Stop all existing Node.js processes using the commands shown in **How to Stop the Application**, then restart the application.

---

# 📁 Project Structure

```text
E-PROC-CHATBOT_ANTI_GRAVITY/
│
├── 05_webui/
│   ├── app.py
│   ├── nodejs/
│   └── ...
│
├── requirements.txt
├── .env.template
├── .env
├── start_cpu.bat
├── start_cpu.sh
└── README.md
```

---

# 📄 License

This project is intended for research and development purposes related to the CHiPS e-Procurement chatbot.

---

# 🤝 Support

If you encounter any issues during setup or execution, please verify:

- Python installation
- Node.js installation
- Ollama installation
- Environment configuration (`.env`)
- Installed Python dependencies
- Running Ollama service
- Required AI model availability

Once all prerequisites are met, launch the application again using the recommended startup script.
