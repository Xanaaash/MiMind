#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH="backend/src:${PYTHONPATH:-}" python3 -m unittest discover -s backend/tests -p 'test_*.py' -v
