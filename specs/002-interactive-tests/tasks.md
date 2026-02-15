# Tasks: Interactive Psychological Tests

**Branch**: `[002-interactive-tests]` | **From**: plan.md | **Roadmap Priority**: P0/P1

## Task Breakdown

### Phase 1: Catalog And Scoring Core

- [ ] **T1.1** Build test catalog schema with theory references and versioning - `backend/src/modules/tests/catalog/`
- [ ] **T1.2** Implement MVP tests: MBTI, 16P, Big Five, Attachment, Love Language - `backend/src/modules/tests/definitions/`
- [ ] **T1.3** Implement answer ingestion and scoring pipelines - `backend/src/modules/tests/scoring/`

### Phase 2: Reports, Entitlements, Growth Hooks

- [ ] **T2.1** Implement report endpoints with subscription paywall checks - `backend/src/modules/tests/report/`
- [ ] **T2.2** Implement share-card generation (mobile vertical format) - `backend/src/modules/cards/`
- [ ] **T2.3** Implement friend pairing flow and compatibility summary - `backend/src/modules/tests/pairing/`

### Phase 3: Testing And Validation

- [ ] **T3.1** Unit tests for scoring dimensions and normalization - `backend/tests/unit/tests/`
- [ ] **T3.2** API contract tests for submit/report/share/pairing endpoints - `backend/tests/contract/tests/`
- [ ] **T3.3** Safety tests to block diagnostic language in generated reports - `backend/tests/safety/tests/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
