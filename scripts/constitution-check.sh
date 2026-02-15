#!/usr/bin/env bash
set -euo pipefail

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
else
  SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

CONSTITUTION="$REPO_ROOT/.specify/memory/constitution.md"
ROADMAP="$REPO_ROOT/roadmap.md"
SPECS_DIR="$REPO_ROOT/specs"

failures=0

require_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "[FAIL] Missing required file: $file"
    failures=$((failures + 1))
  else
    echo "[PASS] File exists: $file"
  fi
}

require_text() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if rg -q "$pattern" "$file"; then
    echo "[PASS] $label"
  else
    echo "[FAIL] $label (pattern: $pattern)"
    failures=$((failures + 1))
  fi
}

echo "== Base files =="
require_file "$CONSTITUTION"
require_file "$ROADMAP"

if [[ -f "$CONSTITUTION" ]]; then
  echo
  echo "== Constitution redline checks =="
  require_text "$CONSTITUTION" "非医疗产品" "Product boundary present"
  require_text "$CONSTITUTION" "禁止做出临床诊断|禁止做临床诊断" "No diagnosis redline present"
  require_text "$CONSTITUTION" "禁止建议药物" "No medication advice redline present"
  require_text "$CONSTITUTION" "实时双层检测" "Dual-layer detection requirement present"
  require_text "$CONSTITUTION" "四级响应" "Four-level crisis response requirement present"
  require_text "$CONSTITUTION" "对话优先于量表" "Conversation-over-scale rule present"
fi

if [[ ! -d "$SPECS_DIR" ]]; then
  echo "[FAIL] specs/ directory missing"
  failures=$((failures + 1))
else
  echo
  echo "== Feature doc and test-gate checks =="
  feature_count=0
  for feature_dir in "$SPECS_DIR"/[0-9][0-9][0-9]-*; do
    [[ -d "$feature_dir" ]] || continue
    feature_count=$((feature_count + 1))

    spec_file="$feature_dir/spec.md"
    plan_file="$feature_dir/plan.md"
    tasks_file="$feature_dir/tasks.md"

    for f in "$spec_file" "$plan_file" "$tasks_file"; do
      if [[ -f "$f" ]]; then
        echo "[PASS] $(basename "$feature_dir") has $(basename "$f")"
      else
        echo "[FAIL] $(basename "$feature_dir") missing $(basename "$f")"
        failures=$((failures + 1))
      fi
    done

    if [[ -f "$tasks_file" ]]; then
      require_text "$tasks_file" "Unit tests|单元测试" "$(basename "$feature_dir"): unit-test task exists"
      require_text "$tasks_file" "contract tests|契约测试|API contract" "$(basename "$feature_dir"): contract-test task exists"
      require_text "$tasks_file" "Safety|安全" "$(basename "$feature_dir"): safety-test task exists"
    fi
  done

  if [[ $feature_count -eq 0 ]]; then
    echo "[FAIL] No feature directories found under specs/"
    failures=$((failures + 1))
  fi
fi

echo
if [[ $failures -gt 0 ]]; then
  echo "Constitution check failed with $failures issue(s)."
  exit 1
fi

echo "Constitution check passed."
