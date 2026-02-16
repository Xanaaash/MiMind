# Tasks: Scale And Test Foundation Expansion

**Branch**: `[007-scale-test-foundation]` | **From**: plan.md | **Roadmap Priority**: P0/P1

## Task Breakdown

### Phase 1: Clinical Scale Foundation

- [x] **T1.1** Add SCL-90 constants and cadence to clinical scale catalog - `backend/src/modules/assessment/catalog/scales.py`
- [x] **T1.2** Implement SCL-90 scoring (list/dimension inputs) and optional submission integration - `backend/src/modules/assessment/scoring_service.py`
- [x] **T1.3** Add SCL-90 yellow-channel modifier in triage - `backend/src/modules/triage/triage_service.py`
- [x] **T1.4** Expose `/api/scales/catalog` and `/api/scales/score` endpoints - `backend/src/modules/api/scales_endpoints.py`, `backend/src/app.py`

### Phase 2: Interactive Test Matrix Expansion

- [x] **T2.1** Add P1 test definitions (stress coping / EQ / inner child / boundary / psych age) - `backend/src/modules/tests/definitions/catalog.py`
- [x] **T2.2** Implement deterministic scoring for all new test types - `backend/src/modules/tests/scoring/service.py`
- [x] **T2.3** Extend interactive catalog metadata for frontend schema rendering - `backend/src/modules/tests/models.py`, `backend/src/modules/tests/service.py`
- [x] **T2.4** Add per-test schema endpoint `/api/tests/catalog/{test_id}` - `backend/src/modules/api/tests_endpoints.py`, `backend/src/app.py`

### Phase 3: Verification And Governance

- [x] **T3.1** Add product/system design baseline docs - `docs/system-design-v1.md`, `docs/scale-test-design-v1.md`
- [x] **T3.2** Add/extend unit + contract + platform tests for scale/test expansion - `backend/tests/unit/`, `backend/tests/contract/`
- [x] **T3.3** Run full regression suite after each major milestone - `scripts/run-backend-tests.sh`
- [x] **T3.4** Add bilingual question-bank assets for all scales/tests - `backend/src/modules/*/catalog/`
- [ ] **T3.5** Migrate in-memory scale/test storage to persistent relational schema (deferred)

## Dependencies

- T2.x depends on T1.x catalog/scoring contracts being stable.
- T3.x depends on T1.x + T2.x implementation completeness.
