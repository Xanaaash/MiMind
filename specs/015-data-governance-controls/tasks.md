# Tasks: Data Governance Controls

**Branch**: `[015-data-governance-controls]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Storage Foundation

- [x] **T1.1** Add storage export/delete primitives for user assessment/test runtime data - `backend/src/modules/storage/`
- [x] **T1.2** Ensure SQLite persistence layer supports compliant retrieval/deletion paths - `backend/src/modules/storage/sqlite_store.py`

### Phase 2: Compliance API

- [x] **T2.1** Implement data governance service (export bundle + erase summary) - `backend/src/modules/compliance/`
- [x] **T2.2** Expose `/api/compliance/{user_id}/export` and `/api/compliance/{user_id}/erase` endpoints - `backend/src/modules/api/`, `backend/src/app.py`

### Phase 3: Verification

- [x] **T3.1** Add unit tests for governance service and store behaviors - `backend/tests/unit/`
- [x] **T3.2** Add API contract + FastAPI platform tests for export/erase flows - `backend/tests/contract/`
- [x] **T3.3** Run full backend regression suite - `scripts/run-backend-tests.sh`

## Dependencies

- T2.x depends on T1.x storage support.
- T3.x depends on T1.x + T2.x completion.
