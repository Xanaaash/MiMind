# Tasks: Model Invocation Observability

**Branch**: `[012-model-observability]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Data Model And Store

- [x] **T1.1** Add model invocation record schema - `backend/src/modules/observability/models.py`
- [x] **T1.2** Extend in-memory store with invocation persistence and listing - `backend/src/modules/storage/in_memory.py`

### Phase 2: Gateway And Runtime Integration

- [x] **T2.1** Add audit recording in model gateway for success/failure paths - `backend/src/modules/model_gateway/service.py`
- [x] **T2.2** Wire coach and safety runtime to store-backed gateway auditing - `backend/src/modules/coach/session_service.py`, `backend/src/modules/safety/detector_service.py`
- [x] **T2.3** Add cost estimation helper for observability records - `backend/src/modules/model_gateway/service.py`

### Phase 3: API And Validation

- [x] **T3.1** Add observability API endpoint to list invocations with filters - `backend/src/modules/api/observability_endpoints.py`, `backend/src/app.py`
- [x] **T3.2** Add unit and contract tests for observability behavior - `backend/tests/unit/model_gateway/`, `backend/tests/contract/observability/`
- [x] **T3.3** Run full regression suite - `scripts/run-backend-tests.sh`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
