#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Run scripts/dev-setup.sh first."
  exit 1
fi

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

PYTHONPATH="backend/src:${PYTHONPATH:-}" uv run uvicorn app:app --host "$HOST" --port "$PORT" --reload
