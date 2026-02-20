#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/autodev-claim.sh --agent-id <agent-id> [--task-id T-xxx]

Claim one task in todo.md from main branch and push immediately.
EOF
}

agent_id=""
task_id=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent-id)
      if [[ $# -lt 2 ]]; then
        echo "[FAIL] --agent-id requires a value" >&2
        exit 1
      fi
      agent_id="$2"
      shift 2
      ;;
    --task-id)
      if [[ $# -lt 2 ]]; then
        echo "[FAIL] --task-id requires a value" >&2
        exit 1
      fi
      task_id="$2"
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

if [[ -z "$agent_id" ]]; then
  echo "[FAIL] --agent-id is required" >&2
  exit 1
fi

if ! [[ "$agent_id" =~ ^[a-z0-9._-]+$ ]]; then
  echo "[FAIL] Invalid agent-id format: $agent_id" >&2
  exit 1
fi

if [[ "$(git branch --show-current)" != "main" ]]; then
  echo "[FAIL] Must run on 'main' branch" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "[FAIL] Working tree must be clean before claiming" >&2
  git status --short
  exit 1
fi

if [[ ! -f "todo.md" ]]; then
  echo "[FAIL] todo.md not found" >&2
  exit 1
fi

git pull origin main --rebase

if [[ -z "$task_id" ]]; then
  line="$(rg -n "^- \\[ \\] \\*\\*T-[0-9]{3}\\*\\*" todo.md | head -n 1 || true)"
  if [[ -z "$line" ]]; then
    echo "[FAIL] No unclaimed task found" >&2
    exit 1
  fi
  task_id="$(echo "$line" | sed -E 's/.*(T-[0-9]{3}).*/\1/')"
fi

if ! [[ "$task_id" =~ ^T-[0-9]{3}$ ]]; then
  echo "[FAIL] Task id must be T-xxx, got '$task_id'" >&2
  exit 1
fi

if ! rg -q "^- \\[ \\] \\*\\*${task_id}\\*\\*" todo.md; then
  echo "[FAIL] Task $task_id is not unclaimed" >&2
  exit 1
fi

tmp="$(mktemp)"
perl -0pe "s/^- \\[ \\] \\*\\*${task_id}\\*\\*/- [🔒 ${agent_id}] **${task_id}**/m" todo.md > "$tmp"
mv "$tmp" todo.md

git add todo.md
git commit -m "claim: ${task_id} by ${agent_id}"
git push origin main

echo "[PASS] Claimed ${task_id} by ${agent_id}"
