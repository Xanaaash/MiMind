# Tasks: Prompt Registry And Rollback Controls

**Branch**: `[010-prompt-registry-rollout]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Prompt Registry Foundation

- [x] **T1.1** Add prompt pack models and catalog versions - `backend/src/modules/prompt/registry/`
- [x] **T1.2** Add registry service with list/get/activate operations - `backend/src/modules/prompt/registry/service.py`
- [x] **T1.3** Add runtime singleton accessor for active prompt registry - `backend/src/modules/prompt/registry/runtime.py`

### Phase 2: Integration

- [x] **T2.1** Route `get_system_prompt` and `get_style_prompt` through registry active version - `backend/src/modules/prompt/system/prompt.py`, `backend/src/modules/prompt/styles/registry.py`
- [x] **T2.2** Expose prompt registry APIs (`list/active/activate`) - `backend/src/modules/api/prompt_endpoints.py`, `backend/src/app.py`
- [x] **T2.3** Include prompt pack version in coach start-session payload - `backend/src/modules/coach/session_service.py`

### Phase 3: Validation

- [x] **T3.1** Add unit tests for registry activation and invalid versions - `backend/tests/unit/prompt/`
- [x] **T3.2** Add contract tests for prompt APIs and coach prompt metadata - `backend/tests/contract/prompt/`, `backend/tests/contract/coach/`
- [x] **T3.3** Run full regression suite - `scripts/run-backend-tests.sh`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
