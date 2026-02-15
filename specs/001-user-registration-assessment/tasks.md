# Tasks: User Registration And Assessment

**Branch**: `[001-user-registration-assessment]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Identity And Consent Baseline

- [x] **T1.1** Create user/profile/consent data model and migrations - `backend/src/modules/user/`
- [x] **T1.2** Implement registration/login/session APIs - `backend/src/modules/auth/`
- [x] **T1.3** Add consent capture and policy version persistence - `backend/src/modules/compliance/`

### Phase 2: Mandatory Scale Workflow + Triage

- [x] **T2.1** Implement PHQ-9/GAD-7/PSS-10/C-SSRS questionnaire schemas - `backend/src/modules/assessment/catalog/`
- [x] **T2.2** Implement scoring service and normalized result storage - `backend/src/modules/assessment/scoring.service.ts`
- [x] **T2.3** Implement triage rules (green/yellow/red) and audit log - `backend/src/modules/triage/triage.service.ts`
- [x] **T2.4** Enforce AI coaching access only for green channel - `backend/src/modules/entitlement/`
- [x] **T2.5** Create reassessment scheduler (30/90 day cadence) - `backend/src/modules/assessment/schedule.service.ts`

### Phase 3: Testing And Validation

- [x] **T3.1** Unit tests for scoring and triage thresholds - `backend/tests/unit/assessment/`
- [x] **T3.2** API contract tests for onboarding and assessment endpoints - `backend/tests/contract/assessment/`
- [x] **T3.3** Safety tests for conversation-priority-over-scale and "joke" handling - `backend/tests/safety/triage/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
