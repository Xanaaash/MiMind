# Tasks: Admin Auth + Modular Frontend

**Branch**: `[016-admin-auth-modular-frontend]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Backend Admin Auth

- [ ] **T1.1** Implement admin config/session models/service - `backend/src/modules/admin/`
- [ ] **T1.2** Add admin session storage methods for in-memory and sqlite persistence - `backend/src/modules/storage/in_memory.py`, `backend/src/modules/storage/sqlite_store.py`
- [ ] **T1.3** Add admin auth API adapter and `/api/admin/*` routes - `backend/src/modules/api/admin_endpoints.py`, `backend/src/app.py`

### Phase 2: Frontend Modular Shell

- [ ] **T2.1** Rebuild frontend into login-gated app shell with left sidebar + mobile top tabs - `frontend/index.html`, `frontend/styles.css`, `frontend/app.js`
- [ ] **T2.2** Implement clinical scales center with dynamic question render and SCL-90 pagination - `frontend/app.js`
- [ ] **T2.3** Implement interactive tests center with dynamic question render and submission flow - `frontend/app.js`
- [ ] **T2.4** Keep existing tool/journal/coach/safety flows under modular navigation - `frontend/app.js`, `frontend/index.html`

### Phase 3: Validation And Deferred Marker

- [ ] **T3.1** Unit tests for admin service and session lifecycle - `backend/tests/unit/admin/`
- [ ] **T3.2** Contract tests for `/api/admin/login|session|logout|users` - `backend/tests/contract/admin/`
- [ ] **T3.3** Extend sqlite store tests for admin session persistence - `backend/tests/unit/storage/test_sqlite_store.py`
- [ ] **T3.4** Update frontend shell/contract/safety tests to new structure - `backend/tests/unit/frontend/`, `backend/tests/contract/platform/`, `backend/tests/safety/frontend/`
- [ ] **T3.5** Document admin password env and module usage - `frontend/README.md`
- [ ] **T3.6 (deferred)** Full user-management UI (list/filter/detail actions) - `frontend/*`, `backend/src/modules/admin/*`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x

## Test Gate Alignment
- Unit tests: covered by corresponding backend/frontend unit suites
- contract tests: covered by API contract suites
- Safety: covered by safety regression suites
