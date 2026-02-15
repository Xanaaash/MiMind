# Tasks: AI Coach Core

**Branch**: `[003-ai-coach-core]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Prompt Stack And Style Modules

- [ ] **T1.1** Build immutable system prompt module with constitutional redline guards - `backend/src/modules/prompt/system/`
- [ ] **T1.2** Implement style prompt modules (Warm Guide, Rational Analysis) - `backend/src/modules/prompt/styles/`
- [ ] **T1.3** Implement context prompt builder (profile + scales + journal + summary) - `backend/src/modules/prompt/context/`

### Phase 2: Session Lifecycle

- [ ] **T2.1** Implement coaching session orchestration and turn pipeline - `backend/src/modules/coach/session.service.ts`
- [ ] **T2.2** Add post-session summary generation and timeline storage - `backend/src/modules/coach/summary.service.ts`
- [ ] **T2.3** Integrate green-channel entitlement checks before each session - `backend/src/modules/coach/access.guard.ts`

### Phase 3: Memory + Safety Integration + Validation

- [ ] **T3.1** Implement vector memory indexing and retrieval adapters - `backend/src/modules/memory/`
- [ ] **T3.2** Unit tests for prompt composition and style selection - `backend/tests/unit/coach/`
- [ ] **T3.3** API contract tests for start/chat/end session APIs - `backend/tests/contract/coach/`
- [ ] **T3.4** Safety tests for forbidden outputs and crisis escalation handoff - `backend/tests/safety/coach/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x and feature 006 interfaces
