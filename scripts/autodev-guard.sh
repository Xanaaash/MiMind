#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/autodev-guard.sh --session <session.env> [--require-clean]
  scripts/autodev-guard.sh --agent-id <agent-id> --task-id <T-xxx> [--require-clean]

Fail fast when branch/cwd drift is detected.
EOF
}

session_file=""
agent_id=""
task_id=""
require_clean=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session)
      if [[ $# -lt 2 ]]; then
        echo "[FAIL] --session requires a value" >&2
        exit 1
      fi
      session_file="$2"
      shift 2
      ;;
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
    --require-clean)
      require_clean=true
      shift
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

if [[ -n "$session_file" ]]; then
  if [[ ! -f "$session_file" ]]; then
    echo "[FAIL] session file not found: $session_file" >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  source "$session_file"
  agent_id="${AUTODEV_AGENT_ID:-}"
  task_id="${AUTODEV_TASK_ID:-}"
  expected_branch="${AUTODEV_BRANCH:-}"
  expected_worktree="${AUTODEV_WORKTREE:-}"
else
  if [[ -z "$agent_id" || -z "$task_id" ]]; then
    echo "[FAIL] Provide --session or both --agent-id and --task-id" >&2
    exit 1
  fi
  repo_root="$(git rev-parse --show-toplevel)"
  expected_branch="agent/${agent_id}/${task_id}"
  expected_worktree="${repo_root}/.worktrees/${agent_id}-${task_id}"
fi

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$expected_branch" ]]; then
  echo "[FAIL] Branch drift detected: expected '$expected_branch', got '$current_branch'" >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
if [[ "$repo_root" != "$expected_worktree" ]]; then
  echo "[FAIL] Worktree drift detected: expected '$expected_worktree', got '$repo_root'" >&2
  exit 1
fi

if [[ "$require_clean" == true ]] && [[ -n "$(git status --porcelain)" ]]; then
  echo "[FAIL] Working tree is not clean" >&2
  git status --short
  exit 1
fi

echo "[PASS] guard ok for ${expected_branch}"
