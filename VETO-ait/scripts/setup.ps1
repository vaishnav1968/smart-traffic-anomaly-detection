# VETO Setup Script for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  VETO: Zero-Trust Runtime Security Environment Setup" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# 1. Create Virtual Environment
if (-not (Test-Path ".venv")) {
    Write-Host "[1/3] Creating Python virtual environment in .venv..." -ForegroundColor Cyan
    python -m venv .venv
} else {
    Write-Host "[1/3] Virtual environment already exists." -ForegroundColor Gray
}

# 2. Install Backend Dependencies
Write-Host "[2/3] Installing backend dependencies..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r backend\requirements.txt

# 3. Build Frontend
Write-Host "[3/3] Installing frontend packages and building bundle..." -ForegroundColor Cyan
Push-Location frontend
npm install
npm run build
Pop-Location

Write-Host "`nSetup complete! Run '.\scripts\run.ps1' to start VETO." -ForegroundColor Green
