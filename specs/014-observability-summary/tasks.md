# Tasks: Observability Summary Metrics

**Branch**: `[014-observability-summary]` | **From**: plan.md | **Roadmap Priority**: P0/P1

## Task Breakdown

### Phase 1: Aggregation Core

- [x] **T1.1** Add summary aggregation in observability service - `backend/src/modules/observability/service.py`
- [x] **T1.2** Add p95 and zero-safe helpers - `backend/src/modules/observability/service.py`

### Phase 2: API Exposure

- [x] **T2.1** Add summary method in observability API - `backend/src/modules/api/observability_endpoints.py`
- [x] **T2.2** Add FastAPI summary route - `backend/src/app.py`

### Phase 3: Validation

- [x] **T3.1** Add unit tests for summary metrics - `backend/tests/unit/observability/`
- [x] **T3.2** Add contract/platform tests for summary endpoint - `backend/tests/contract/observability/`, `backend/tests/contract/platform/`
- [x] **T3.3** Run full regression suite - `scripts/run-backend-tests.sh`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x

## Test Gate Alignment
- Unit tests: covered by corresponding backend/frontend unit suites
- contract tests: covered by API contract suites
- Safety: covered by safety regression suites
