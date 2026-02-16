# Tasks: Warm Frontend Experience

**Branch**: `[013-warm-frontend-experience]` | **From**: plan.md | **Roadmap Priority**: P0 UX enablement

## Task Breakdown

### Phase 1: Frontend Shell And Visual Design

- [x] **T1.1** Build warm bilingual landing shell with responsive layout - `frontend/index.html`, `frontend/styles.css`
- [x] **T1.2** Add meaningful motion and atmosphere styling tokens - `frontend/styles.css`

### Phase 2: API Flow Integration

- [x] **T2.1** Implement register + baseline assessment + healing tools interactions - `frontend/app.js`
- [x] **T2.2** Implement journal + coach interaction panel and activity log - `frontend/app.js`
- [x] **T2.3** Provide crisis resource panel and constitution-safe UX copy - `frontend/index.html`, `frontend/app.js`

### Phase 3: Validation And Guardrails

- [x] **T3.1** Unit tests for frontend shell rendering and baseline copy - `backend/tests/unit/frontend/test_frontend_shell.py`
- [x] **T3.2** API contract tests for root frontend delivery and key form hooks - `backend/tests/contract/platform/test_frontend_web_contract.py`
- [x] **T3.3** Safety tests for non-medical boundary copy and prohibited claim absence - `backend/tests/safety/frontend/test_frontend_safety_copy.py`
- [x] **T3.4** Add static hosting entrypoint and run script - `backend/src/web_app.py`, `scripts/run-web-app.sh`
- [x] **T3.5** Add usage notes for local run - `frontend/README.md`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
