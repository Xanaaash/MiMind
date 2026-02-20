#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/autodev-worktree.sh --agent-id <agent-id> --task-id T-xxx

Create an isolated worktree and branch for one claimed task.
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

if [[ -z "$agent_id" || -z "$task_id" ]]; then
  echo "[FAIL] --agent-id and --task-id are required" >&2
  exit 1
fi

if ! [[ "$task_id" =~ ^T-[0-9]{3}$ ]]; then
  echo "[FAIL] Task id must be T-xxx, got '$task_id'" >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ "$(git branch --show-current)" != "main" ]]; then
  echo "[FAIL] Run from main branch to avoid accidental drift" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "[FAIL] Working tree must be clean before creating worktree" >&2
  git status --short
  exit 1
fi

if ! rg -q "^- \\[🔒 ${agent_id}\\] \\*\\*${task_id}\\*\\*" todo.md; then
  echo "[FAIL] Task ${task_id} is not claimed by ${agent_id} in todo.md" >&2
  exit 1
fi

git pull origin main --rebase

branch="agent/${agent_id}/${task_id}"
worktree_path="${repo_root}/.worktrees/${agent_id}-${task_id}"

mkdir -p "${repo_root}/.worktrees" "${repo_root}/.autodev/sessions"

if [[ -d "$worktree_path" ]]; then
  echo "[FAIL] Worktree already exists: $worktree_path" >&2
  exit 1
fi

if git show-ref --verify --quiet "refs/heads/${branch}"; then
  git worktree add "$worktree_path" "$branch"
else
  git worktree add -b "$branch" "$worktree_path" main
fi

session_file="${repo_root}/.autodev/sessions/${agent_id}-${task_id}.env"
cat > "$session_file" <<EOF
AUTODEV_AGENT_ID=${agent_id}
AUTODEV_TASK_ID=${task_id}
AUTODEV_BRANCH=${branch}
AUTODEV_WORKTREE=${worktree_path}
EOF

cat <<EOF
[PASS] worktree ready
branch:   ${branch}
path:     ${worktree_path}
session:  ${session_file}

Next:
  cd ${worktree_path}
  bash ${repo_root}/scripts/autodev-guard.sh --session ${session_file}
EOF
