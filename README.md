# 🤖 CHiPS e-Procurement RAG Chatbot

An AI-powered e-Procurement assistant designed to answer queries based on Chhattisgarh e-Procurement Store Rules and procurement guidelines using Retrieval-Augmented Generation (RAG) powered by **Gemma 3 (4B)**.

---

# 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Quick Start Guide](#-quick-start-guide)
   - [Step 1: Clone the Repository](#step-1-clone-the-repository)
   - [Step 2: Create Configuration File](#step-2-create-configuration-file)
   - [Step 3: Set Up Python Virtual Environment](#step-3-set-up-python-virtual-environment)
   - [Step 4: Install Node.js UI Dependencies](#step-4-install-nodejs-ui-dependencies)
   - [Step 5: Setup & Download Gemma 3 (4B)](#step-5-setup--download-gemma-3-4b)
3. [Launching the Application](#-launching-the-application)
4. [Accessing the Web UI](#-accessing-the-web-ui)
5. [How to Stop the Application](#-how-to-stop-the-application)
6. [Troubleshooting](#-troubleshooting)

---

# 💻 Prerequisites

Before running the application, make sure the following software is installed on your system.

| Software | Required Version | Download |
| :--- | :--- | :--- |
| **Python** | 3.10 or higher | https://www.python.org/downloads/ |
| **Node.js** | v18 or higher | https://nodejs.org/ |
| **Ollama** | Latest | https://ollama.com/ |
| **Git** | Latest | https://git-scm.com/ |

> **Important (Windows Users):**
>
> During Python installation, make sure you enable **"Add Python to PATH"**.

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

Create the active configuration file from the template.

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

### Create the Virtual Environment

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

Navigate to the frontend directory and install all required packages.

```bash
cd 05_webui/nodejs
npm install
cd ../..
```

---

## Step 5: Setup & Download Gemma 3 (4B)

Ensure Ollama is installed and running.

If Ollama is not already running, start it:

```bash
ollama serve
```

Download the required AI model:

```bash
ollama pull gemma3:4b
```

> **Note:** The first download may take several minutes depending on your internet connection.

---

# 🚀 Launching the Application

## Option A: Automated Startup (Recommended)

Run the startup script from the project root directory.

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

If you prefer starting the application manually:

1. Open a terminal in the project root.
2. Activate the Python virtual environment.
3. Start the Node.js server.

```bash
cd 05_webui/nodejs
npm start
```

The backend service will start automatically.

---

# 🌐 Accessing the Web UI

Once the application has started successfully, open your preferred web browser and navigate to:

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
- Restart your terminal or computer.

---

## 2. PowerShell Script Execution Policy Error

If you receive an error similar to:

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

Verify the following:

- Ollama is running.

```bash
ollama serve
```

- The Gemma 3 (4B) model has been downloaded.

```bash
ollama pull gemma3:4b
```

- Python dependencies are installed.

```bash
pip install -r requirements.txt
```

Also ensure that ports **3000**, **5000**, or **8080** are not blocked by your firewall or another application.

---

## 4. Port 3000 Is Already in Use

Terminate all existing Node.js processes using the commands listed in **How to Stop the Application**, then restart the application.

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

This project is intended for research, development, and demonstration purposes related to the CHiPS e-Procurement RAG Chatbot.

---

# 🤝 Support

Before reporting an issue, verify that:

- Python is installed correctly.
- Node.js is installed.
- Ollama is installed and running.
- The **Gemma 3 (4B)** model has been downloaded.
- The `.env` file is configured.
- Python dependencies are installed successfully.
- No required ports are blocked.

If all prerequisites are satisfied, restart the application using the recommended startup script.
