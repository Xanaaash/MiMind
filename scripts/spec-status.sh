#!/usr/bin/env bash
set -euo pipefail

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
else
  SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

SPECS_DIR="$REPO_ROOT/specs"
if [[ ! -d "$SPECS_DIR" ]]; then
  echo "specs/ not found"
  exit 1
fi

found=false
printf "%-34s %-5s %-5s %-5s %-8s\n" "FEATURE" "SPEC" "PLAN" "TASK" "STATUS"
printf "%-34s %-5s %-5s %-5s %-8s\n" "----------------------------------" "-----" "-----" "-----" "--------"

for feature_dir in "$SPECS_DIR"/[0-9][0-9][0-9]-*; do
  [[ -d "$feature_dir" ]] || continue
  found=true

  feature_name="$(basename "$feature_dir")"
  spec_mark="N"
  plan_mark="N"
  task_mark="N"

  [[ -f "$feature_dir/spec.md" ]] && spec_mark="Y"
  [[ -f "$feature_dir/plan.md" ]] && plan_mark="Y"
  [[ -f "$feature_dir/tasks.md" ]] && task_mark="Y"

  status="todo"
  if [[ "$spec_mark" == "Y" && "$plan_mark" == "Y" && "$task_mark" == "Y" ]]; then
    status="ready"
  elif [[ "$spec_mark" == "Y" || "$plan_mark" == "Y" || "$task_mark" == "Y" ]]; then
    status="partial"
  fi

  printf "%-34s %-5s %-5s %-5s %-8s\n" "$feature_name" "$spec_mark" "$plan_mark" "$task_mark" "$status"
done

if [[ "$found" != "true" ]]; then
  echo "No feature directories found under specs/."
fi
