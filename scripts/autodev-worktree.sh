#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/autodev-worktree.sh --agent-id <agent-id> [--task-id T-xxx]

Create an isolated worktree for one claimed task to avoid cross-agent branch switching.
This script does not claim tasks. Claim on main first, then run this script.
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

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "[FAIL] Not inside a git repository" >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "[FAIL] Working tree must be clean before creating worktree" >&2
  git status --short
  exit 1
fi

if [[ -z "$task_id" ]]; then
  if [[ ! -f "todo.md" ]]; then
    echo "[FAIL] todo.md not found and --task-id not provided" >&2
    exit 1
  fi
  task_line="$(rg -n "^- \\[🔒 ${agent_id}\\] \\*\\*T-[0-9]{3}\\*\\*" todo.md | head -n 1 || true)"
  if [[ -z "$task_line" ]]; then
    task_line="$(rg -n "^- \\[ \\] \\*\\*T-[0-9]{3}\\*\\*" todo.md | head -n 1 || true)"
  fi
  if [[ -z "$task_line" ]]; then
    echo "[FAIL] Could not infer task id from todo.md" >&2
    exit 1
  fi
  task_id="$(echo "$task_line" | sed -E 's/.*(T-[0-9]{3}).*/\1/')"
fi

if ! [[ "$task_id" =~ ^T-[0-9]{3}$ ]]; then
  echo "[FAIL] task id format must be T-xxx (got '$task_id')" >&2
  exit 1
fi

feature_branch="agent/${agent_id}/${task_id}"
worktree_dir="${repo_root}/.worktrees/${agent_id}-${task_id}"

git checkout main
git pull origin main --rebase

mkdir -p "${repo_root}/.worktrees"

if git show-ref --verify --quiet "refs/heads/${feature_branch}"; then
  git worktree add "${worktree_dir}" "${feature_branch}"
else
  git worktree add -b "${feature_branch}" "${worktree_dir}" main
fi

cat <<EOF
[PASS] Created isolated worktree
agent_id:      ${agent_id}
task_id:       ${task_id}
branch:        ${feature_branch}
worktree_path: ${worktree_dir}

Next:
  cd ${worktree_dir}
  git branch --show-current
EOF
