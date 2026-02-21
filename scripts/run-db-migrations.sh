#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1 && [[ -f "pyproject.toml" ]]; then
  PYTHONPATH="backend/src:${PYTHONPATH:-}" uv run -- python -m modules.storage.migration_cli "$@"
else
  PYTHONPATH="backend/src:${PYTHONPATH:-}" python3 -m modules.storage.migration_cli "$@"
fi
