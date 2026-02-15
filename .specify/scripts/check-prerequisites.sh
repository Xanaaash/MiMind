#!/usr/bin/env bash
set -e

JSON_MODE=false
REQUIRE_TASKS=false
INCLUDE_TASKS=false
PATHS_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --require-tasks) REQUIRE_TASKS=true ;;
        --include-tasks) INCLUDE_TASKS=true ;;
        --paths-only) PATHS_ONLY=true ;;
        --help|-h)
            echo "Usage: check-prerequisites.sh [--json] [--require-tasks] [--include-tasks] [--paths-only]"
            exit 0
            ;;
        *) echo "ERROR: Unknown option '$arg'" >&2; exit 1 ;;
    esac
done

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

eval $(get_feature_paths)
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

if $PATHS_ONLY; then
    if $JSON_MODE; then
        printf '{"REPO_ROOT":"%s","BRANCH":"%s","FEATURE_DIR":"%s"}\n' "$REPO_ROOT" "$CURRENT_BRANCH" "$FEATURE_DIR"
    else
        echo "REPO_ROOT: $REPO_ROOT"
        echo "BRANCH: $CURRENT_BRANCH"
        echo "FEATURE_DIR: $FEATURE_DIR"
    fi
    exit 0
fi

[[ ! -d "$FEATURE_DIR" ]] && { echo "ERROR: Feature directory not found: $FEATURE_DIR" >&2; exit 1; }
[[ ! -f "$IMPL_PLAN" ]] && { echo "ERROR: plan.md not found. Run /speckit.plan first." >&2; exit 1; }
[[ $REQUIRE_TASKS == true && ! -f "$TASKS" ]] && { echo "ERROR: tasks.md not found. Run /speckit.tasks first." >&2; exit 1; }

docs=()
[[ -f "$RESEARCH" ]] && docs+=("research.md")
[[ -f "$DATA_MODEL" ]] && docs+=("data-model.md")
[[ -d "$CONTRACTS_DIR" && -n "$(ls -A "$CONTRACTS_DIR" 2>/dev/null)" ]] && docs+=("contracts/")
[[ -f "$QUICKSTART" ]] && docs+=("quickstart.md")
[[ $INCLUDE_TASKS == true && -f "$TASKS" ]] && docs+=("tasks.md")

if $JSON_MODE; then
    json_docs=$(printf '"%s",' "${docs[@]}")
    printf '{"FEATURE_DIR":"%s","AVAILABLE_DOCS":[%s]}\n' "$FEATURE_DIR" "${json_docs%,}"
else
    echo "FEATURE_DIR:$FEATURE_DIR"
    echo "AVAILABLE_DOCS:"
    check_file "$RESEARCH" "research.md"
    check_file "$DATA_MODEL" "data-model.md"
    check_dir "$CONTRACTS_DIR" "contracts/"
    check_file "$QUICKSTART" "quickstart.md"
    $INCLUDE_TASKS && check_file "$TASKS" "tasks.md"
fi
