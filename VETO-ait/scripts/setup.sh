#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  VETO: Zero-Trust Runtime Security Environment Setup"
echo "=========================================================="

# 1. Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[1/3] Creating Python virtual environment in .venv..."
    python3 -m venv .venv
else
    echo "[1/3] Virtual environment already exists."
fi

# 2. Install Backend Dependencies
echo "[2/3] Installing backend dependencies..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r backend/requirements.txt

# 3. Build Frontend
echo "[3/3] Installing frontend packages and building bundle..."
cd frontend
npm install
npm run build
cd ..

echo -e "\nSetup complete! Run './scripts/run.sh' to start VETO."
