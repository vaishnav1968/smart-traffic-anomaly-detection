#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  Starting VETO Runtime Security Platform"
echo "=========================================================="

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found! Running setup..."
    ./scripts/setup.sh
fi

export PYTHONPATH="."
echo "Starting FastAPI backend server on http://localhost:8000..."
./.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
