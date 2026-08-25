<#
.SYNOPSIS
    Automated Setup & Launcher for CHiPS e-Procurement Chatbot (Windows PowerShell)

.DESCRIPTION
    This script automates the complete first-time setup and subsequent runs of the chatbot:
    1. Checks system prerequisites (Python, Node.js, Ollama)
    2. Sets up configuration (.env) from template
    3. Creates Python virtual environment (.venv) & installs requirements
    4. Installs Node.js UI dependencies
    5. Verifies Ollama is running and pulls the gemma3:4b model
    6. Launches the application stack and opens the web browser
#>

# Enable Stop on error for critical steps
$ErrorActionPreference = "Stop"

# Helper output functions
function Write-Header ($text) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step ($text) {
    Write-Host "[+] $text" -ForegroundColor Green
}

function Write-Info ($text) {
    Write-Host "[i] $text" -ForegroundColor Yellow
}

function Write-ErrorMsg ($text) {
    Write-Host "[!] ERROR: $text" -ForegroundColor Red
}

$ProjectRoot = $PSScriptRoot
Set-Location -Path $ProjectRoot

Write-Header "CHiPS e-Procurement Chatbot - Automated Setup & Launcher"

# ---------------------------------------------------------------------------
# 1. Check Prerequisites
# ---------------------------------------------------------------------------
Write-Step "Checking prerequisites..."

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Info "Found Python: $pythonVersion"
} catch {
    Write-ErrorMsg "Python is not installed or not added to PATH. Please install Python 3.10+ from https://www.python.org/downloads/ and check 'Add Python to PATH'."
    exit 1
}

# Check Node.js & npm
try {
    $nodeVersion = node -v 2>&1
    Write-Info "Found Node.js: $nodeVersion"
} catch {
    Write-ErrorMsg "Node.js is not installed or not added to PATH. Please install Node.js (v18+) from https://nodejs.org/."
    exit 1
}

# Check Ollama
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Info "Found Ollama: $ollamaVersion"
} catch {
    Write-ErrorMsg "Ollama is not installed or not added to PATH. Please install Ollama from https://ollama.com/."
    exit 1
}

# ---------------------------------------------------------------------------
# 2. Environment File Setup (.env)
# ---------------------------------------------------------------------------
$envPath = Join-Path $ProjectRoot ".env"
$envTemplatePath = Join-Path $ProjectRoot ".env.template"

if (-not (Test-Path $envPath)) {
    if (Test-Path $envTemplatePath) {
        Write-Step "Creating .env configuration file from template..."
        Copy-Item -Path $envTemplatePath -Destination $envPath
    } else {
        Write-ErrorMsg ".env.template file not found in project root!"
        exit 1
    }
} else {
    Write-Info ".env configuration file already exists."
}

# ---------------------------------------------------------------------------
# 3. Python Virtual Environment (.venv) Setup
# ---------------------------------------------------------------------------
$venvPath = Join-Path $ProjectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip = Join-Path $venvPath "Scripts\pip.exe"

if (-not (Test-Path $venvPath)) {
    Write-Step "Creating Python virtual environment (.venv)..."
    python -m venv $venvPath
}

Write-Step "Upgrading pip and installing Python dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPip install -r (Join-Path $ProjectRoot "requirements.txt") --no-cache-dir

# ---------------------------------------------------------------------------
# 4. Node.js UI Setup
# ---------------------------------------------------------------------------
$nodeUiDir = Join-Path $ProjectRoot "05_webui\nodejs"
$nodeModulesDir = Join-Path $nodeUiDir "node_modules"

if (-not (Test-Path $nodeModulesDir)) {
    Write-Step "Installing Node.js dependencies in 05_webui\nodejs..."
    Set-Location -Path $nodeUiDir
    npm install
    Set-Location -Path $ProjectRoot
} else {
    Write-Info "Node.js dependencies already installed."
}

# ---------------------------------------------------------------------------
# 5. Ollama Startup & Model Pull (gemma3:4b)
# ---------------------------------------------------------------------------
Write-Step "Checking Ollama status & model (gemma3:4b)..."

# Set CPU flags for Ollama
$env:OLLAMA_INTEL_GPU = "false"
$env:OLLAMA_LLM_LIBRARY = "cpu"

# Check if Ollama service is listening on port 11434
$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $ollamaRunning = $true
    }
} catch {
    $ollamaRunning = $false
}

if (-not $ollamaRunning) {
    Write-Info "Starting Ollama service in background..."
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

Write-Step "Ensuring model 'gemma3:4b' is downloaded in Ollama..."
ollama pull gemma3:4b

# ---------------------------------------------------------------------------
# 6. Launch Application Stack
# ---------------------------------------------------------------------------
Write-Header "Launching Application Stack"

$env:NODE_ENV = "production"
$env:ENVIRONMENT = "production"
$env:USE_WAITRESS = "true"
if (-not $env:FLASK_PORT) { $env:FLASK_PORT = "5000" }
if (-not $env:FLASK_URL) { $env:FLASK_URL = "http://127.0.0.1:$($env:FLASK_PORT)" }
if (-not $env:FLASK_TIMEOUT_MS) { $env:FLASK_TIMEOUT_MS = "300000" }
if (-not $env:WAITRESS_THREADS) { $env:WAITRESS_THREADS = "8" }
if (-not $env:MAX_CONCURRENT_RAG_REQUESTS) { $env:MAX_CONCURRENT_RAG_REQUESTS = "8" }
if (-not $env:RAG_REQUEST_QUEUE_TIMEOUT_SECONDS) { $env:RAG_REQUEST_QUEUE_TIMEOUT_SECONDS = "2.0" }

# Add .venv\Scripts to PATH so node server.js finds the virtual environment python
$env:PATH = "$(Join-Path $venvPath 'Scripts');" + $env:PATH
$env:PYTHON = $venvPython

# Start Voice Server in background
$voiceServerScript = Join-Path $ProjectRoot "06_voice\voice_server.py"
if (Test-Path $voiceServerScript) {
    $logsDir = Join-Path $ProjectRoot "logs"
    if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir -Force | Out-Null }
    $voiceLog = Join-Path $logsDir "voice_server.log"
    $voiceErrLog = Join-Path $logsDir "voice_server_err.log"
    Write-Step "Starting Voice Server on port 5050 (background)..."
    Start-Process -FilePath $venvPython -ArgumentList "`"$voiceServerScript`"" -RedirectStandardOutput $voiceLog -RedirectStandardError $voiceErrLog -WindowStyle Hidden
}

Write-Info "Waiting for UI to become ready at http://localhost:3000 before opening browser..."
Start-Job -ScriptBlock {
    for ($i = 0; $i -lt 150; $i++) {
        Start-Sleep -Seconds 2
        try {
            $resp = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue
            if ($resp.StatusCode -eq 200) {
                break
            }
        } catch {
            # Express UI not listening yet
        }
    }
    Start-Process "http://localhost:3000"
} | Out-Null

Write-Step "Starting Express UI & Flask RAG backend..."
Set-Location -Path $nodeUiDir
node server.js
