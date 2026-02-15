# Tasks: Safety NLU And Crisis Intervention

**Branch**: `[006-safety-nlu-crisis]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Risk Detection Pipeline

- [ ] **T1.1** Implement NLU fast classifier API and rule lexicon - `backend/src/modules/safety/nlu/`
- [ ] **T1.2** Implement LLM semantic risk evaluator and confidence calibration - `backend/src/modules/safety/semantic/`
- [ ] **T1.3** Implement detector orchestrator with fail-closed policy - `backend/src/modules/safety/detector.service.ts`

### Phase 2: Four-Level Crisis Response

- [ ] **T2.1** Implement response policy engine for levels 1-4 - `backend/src/modules/safety/policy/`
- [ ] **T2.2** Implement counseling interruption + crisis script routing - `backend/src/modules/safety/interruption.service.ts`
- [ ] **T2.3** Implement hotline resource resolver (locale aware) and client fallback package - `client/src/safety/hotline-cache/`
- [ ] **T2.4** Implement operations alerting and case audit trail - `backend/src/modules/safety/ops-alert/`
- [ ] **T2.5** Implement emergency-contact and legal-policy gating hooks - `backend/src/modules/safety/emergency/`

### Phase 3: Safety Validation And Performance Gates

- [ ] **T3.1** Unit tests for level mapping, policy transitions, and fail-closed behavior - `backend/tests/unit/safety/`
- [ ] **T3.2** API contract tests for detection and crisis response endpoints - `backend/tests/contract/safety/`
- [ ] **T3.3** Safety regression suite for high-risk recall, joke-disclaimer handling, and dialogue-priority rules - `backend/tests/safety/crisis/`
- [ ] **T3.4** Benchmark tests enforcing NLU <100ms and semantic judge <2s - `backend/tests/benchmark/safety/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
