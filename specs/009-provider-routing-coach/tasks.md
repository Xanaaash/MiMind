# Tasks: Provider Routing And Coach Gateway Integration

**Branch**: `[009-provider-routing-coach]` | **From**: plan.md | **Roadmap Priority**: P0/P1

## Task Breakdown

### Phase 1: Gateway Provider Routing

- [x] **T1.1** Add `coach_generation` gateway task type and response mapping - `backend/src/modules/model_gateway/models.py`
- [x] **T1.2** Add local coach provider adapter - `backend/src/modules/model_gateway/providers/local_coach.py`
- [x] **T1.3** Add env-driven provider routing config loader - `backend/src/modules/model_gateway/config.py`
- [x] **T1.4** Add optional external provider adapter (env-gated) - `backend/src/modules/model_gateway/providers/openai_chat.py`

### Phase 2: Coach Integration

- [x] **T2.1** Refactor coach reply generation to use gateway `coach_generation` task - `backend/src/modules/coach/session_service.py`
- [x] **T2.2** Add fail-safe fallback when provider errors occur without breaking safety path - `backend/src/modules/coach/session_service.py`

### Phase 3: Testing And Regression

- [x] **T3.1** Add/extend gateway unit tests for coach routing and external-config errors - `backend/tests/unit/model_gateway/`
- [x] **T3.2** Add coach integration unit/contract checks for gateway-generated replies - `backend/tests/unit/coach/`, `backend/tests/contract/coach/`
- [x] **T3.3** Run coach safety + full regression suite - `backend/tests/safety/coach/`, `scripts/run-backend-tests.sh`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
