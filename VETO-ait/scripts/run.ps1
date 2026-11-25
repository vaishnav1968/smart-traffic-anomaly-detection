# VETO Run Script for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Starting VETO Runtime Security Platform" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

if (-not (Test-Path ".venv")) {
    Write-Host "Virtual environment not found! Running setup..." -ForegroundColor Yellow
    .\scripts\setup.ps1
}

$env:PYTHONPATH = "."
Write-Host "Starting FastAPI backend server on http://localhost:8000..." -ForegroundColor Cyan
Start-Process "http://localhost:8000"
.\.venv\Scripts\uvicorn.exe backend.app.main:app --host 0.0.0.0 --port 8000 --reload
