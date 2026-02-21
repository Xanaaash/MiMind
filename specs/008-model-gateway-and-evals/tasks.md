# Tasks: Model Gateway And Safety Evals

**Branch**: `[008-model-gateway-and-evals]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Gateway Foundation

- [x] **T1.1** Add model gateway request/response models and task types - `backend/src/modules/model_gateway/models.py`
- [x] **T1.2** Add provider interface and default local safety provider - `backend/src/modules/model_gateway/providers/`
- [x] **T1.3** Add gateway service router with task-based dispatch - `backend/src/modules/model_gateway/service.py`

### Phase 2: Safety Integration

- [x] **T2.1** Refactor safety detector to use model gateway for NLU + semantic calls - `backend/src/modules/safety/detector_service.py`
- [x] **T2.2** Preserve fail-closed and override/joke rules after gateway migration - `backend/src/modules/safety/detector_service.py`

### Phase 3: Evals And Regression

- [x] **T3.1** Add gateway unit tests (success, unsupported task, provider error) - `backend/tests/unit/model_gateway/`
- [x] **T3.2** Update safety detector tests for gateway-backed behavior - `backend/tests/unit/safety/`
- [x] **T3.3** Run benchmark + safety + full regression suites - `backend/tests/benchmark/safety/`, `scripts/run-backend-tests.sh`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x

## Test Gate Alignment
- Unit tests: covered by corresponding backend/frontend unit suites
- contract tests: covered by API contract suites
- Safety: covered by safety regression suites
