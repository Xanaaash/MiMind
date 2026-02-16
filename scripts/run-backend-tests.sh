#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1 && [[ -f "pyproject.toml" ]]; then
  PYTHONPATH="backend/src:${PYTHONPATH:-}" uv run -- python -m unittest discover -s backend/tests -p 'test_*.py' -v
else
  PYTHONPATH="backend/src:${PYTHONPATH:-}" python3 -m unittest discover -s backend/tests -p 'test_*.py' -v
fi
