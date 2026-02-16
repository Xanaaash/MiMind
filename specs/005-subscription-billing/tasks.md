# Tasks: Subscription And Billing

**Branch**: `[005-subscription-billing]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Plans And Entitlement Core

- [x] **T1.1** Define plan catalog (Free/Base/Coach/Trial) and entitlement matrix - `backend/src/modules/billing/catalog/`
- [x] **T1.2** Implement entitlement service shared by all feature guards - `backend/src/modules/entitlement/entitlement.service.ts`
- [x] **T1.3** Implement green-channel guard for coach plan purchase and usage - `backend/src/modules/billing/coach.guard.ts`

### Phase 2: Payment And Lifecycle

- [x] **T2.1** Implement checkout session API and order persistence - `backend/src/modules/billing/checkout/`
- [x] **T2.2** Implement idempotent webhook processor (dedupe + ordering) - `backend/src/modules/billing/webhook/`
- [x] **T2.3** Implement 7-day trial activation and expiry jobs - `backend/src/modules/billing/trial/`
- [x] **T2.4** Implement monthly AI session quota tracking and reset jobs - `backend/src/modules/billing/quota/`

### Phase 3: Validation And Compliance

- [x] **T3.1** Unit tests for entitlement matrix, quota math, and webhook idempotency - `backend/tests/unit/billing/`
- [x] **T3.2** API contract tests for checkout/webhook/entitlement endpoints - `backend/tests/contract/billing/`
- [x] **T3.3** Safety tests for blocked coach access in yellow/red channels - `backend/tests/safety/billing/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
