#!/usr/bin/env bash
# ==========================================================
# Optik Platform Backend - Dev/Prod Launcher
# Usage: ./start.sh [dev|prod]
# ==========================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${ROOT_DIR}/venv"
PYTHON="${VENV}/bin/python"
UVICORN="${VENV}/bin/uvicorn"

MODE="${1:-dev}"

if [ ! -f "${UVICORN}" ]; then
    echo "❌ venv not found. Run: python3 -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

echo "🚀 Starting Optik Backend in ${MODE} mode..."
cd "${ROOT_DIR}"

if [ "$MODE" = "prod" ]; then
    exec "${UVICORN}" api.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --log-level info
else
    exec "${UVICORN}" api.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level debug
fi
