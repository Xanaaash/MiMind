#!/usr/bin/env bash
set -euo pipefail

echo "=== MiMind dev setup ==="

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install uv first: https://docs.astral.sh/uv/"
  exit 1
fi

uv venv
uv sync --extra dev

echo ""
echo "Done. Use these commands:"
echo "  uv run python -m unittest discover -s backend/tests -p 'test_*.py' -v"
echo "  uv run pytest"
echo "  uv run ruff check ."
echo "  uv run mypy"
