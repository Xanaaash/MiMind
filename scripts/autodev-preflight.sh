#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/autodev-preflight.sh [--require-main] [--require-clean] [--expect-branch BRANCH]

Checks repository state before running multi-agent autodev flow.
EOF
}

require_main=false
require_clean=false
expect_branch=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --require-main)
      require_main=true
      shift
      ;;
    --require-clean)
      require_clean=true
      shift
      ;;
    --expect-branch)
      if [[ $# -lt 2 ]]; then
        echo "[FAIL] --expect-branch requires a value" >&2
        exit 1
      fi
      expect_branch="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[FAIL] Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "[FAIL] Not inside a git repository" >&2
  exit 1
fi

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[FAIL] Detached HEAD is not supported in autodev flow" >&2
  exit 1
fi

echo "[INFO] branch=$branch"

if [[ -n "$expect_branch" && "$branch" != "$expect_branch" ]]; then
  echo "[FAIL] Expected branch '$expect_branch' but found '$branch'" >&2
  exit 1
fi

if [[ "$require_main" == true && "$branch" != "main" ]]; then
  echo "[FAIL] Current branch must be 'main' for this step (found '$branch')" >&2
  exit 1
fi

if [[ "$require_clean" == true ]]; then
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "[FAIL] Working tree is not clean" >&2
    git status --short
    exit 1
  fi
fi

upstream="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
if [[ -n "$upstream" ]]; then
  ahead_behind="$(git rev-list --left-right --count "${upstream}...HEAD" 2>/dev/null || echo "0 0")"
  behind="$(echo "$ahead_behind" | awk '{print $1}')"
  ahead="$(echo "$ahead_behind" | awk '{print $2}')"
  echo "[INFO] upstream=$upstream ahead=$ahead behind=$behind"
else
  echo "[WARN] No upstream configured for branch '$branch'"
fi

if [[ -f "todo.md" ]]; then
  open_count="$(rg -c "^- \\[ \\] \\*\\*T-[0-9]{3}\\*\\*" todo.md || true)"
  lock_count="$(rg -c "^- \\[🔒 [^]]+\\] \\*\\*T-[0-9]{3}\\*\\*" todo.md || true)"
  done_count="$(rg -c "^- \\[✅\\] \\*\\*T-[0-9]{3}\\*\\*" todo.md || true)"
  echo "[INFO] todo: open=${open_count:-0} locked=${lock_count:-0} done=${done_count:-0}"
fi

echo "[PASS] autodev preflight checks passed"
