# Tasks: Healing Tools

**Branch**: `[004-healing-tools]` | **From**: plan.md | **Roadmap Priority**: P0/P1

## Task Breakdown

### Phase 1: Core Tools (P0)

- [x] **T1.1** Implement white-noise audio library, timer, and playback APIs - `backend/src/modules/tools/audio/`
- [x] **T1.2** Implement 4-7-8 breathing exercise state machine - `frontend/src/features/tools/breathing/`
- [x] **T1.3** Implement guided meditation content APIs and playback metadata - `backend/src/modules/tools/meditation/`

### Phase 2: Mood Journal (P1)

- [x] **T2.1** Implement mood journal entry/create/update/list APIs - `backend/src/modules/journal/`
- [x] **T2.2** Implement 7/30-day trend calculation service - `backend/src/modules/journal/trend.service.ts`
- [x] **T2.3** Implement journal-to-context summary adapter for coach module - `backend/src/modules/journal/context.adapter.ts`

### Phase 3: Validation And Guardrails

- [x] **T3.1** Unit tests for breathing timer, trend calculations, and adapters - `backend/tests/unit/tools/`
- [x] **T3.2** API contract tests for tools and journal endpoints - `backend/tests/contract/tools/`
- [x] **T3.3** Safety tests for risk-signal forwarding from journal entries - `backend/tests/safety/journal/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
