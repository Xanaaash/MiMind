#!/usr/bin/env bash
set -euo pipefail

FORCE=false
if [[ "${1:-}" == "--force" ]]; then
  FORCE=true
fi

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
else
  SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

SPECS_DIR="$REPO_ROOT/specs"
mkdir -p "$SPECS_DIR"

write_if_missing() {
  local file="$1"
  if [[ -f "$file" && "$FORCE" != "true" ]]; then
    echo "[skip] $file"
    return
  fi

  mkdir -p "$(dirname "$file")"
  cat > "$file"
  echo "[write] $file"
}

write_if_missing "$SPECS_DIR/001-user-registration-assessment/spec.md" <<'EOF_SPEC_001'
# Feature Specification: User Registration And Assessment

**Feature Branch**: `[001-user-registration-assessment]`
**Created**: 2026-02-15
**Status**: Draft
**Input**: roadmap.md v2.0 + constitution.md

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registration + Mandatory Clinical Scales (Priority: P0)

As a new user, I must complete registration and mandatory clinical scales before using core functions.

**Why this priority**: It is the entry gate for risk control and all later product capabilities.

**Independent Test**: Register a new account, finish PHQ-9/GAD-7/PSS-10/C-SSRS, and verify triage is generated.

**Acceptance Scenarios**:

1. **Given** a new user, **When** registration completes, **Then** profile and consent records are stored.
2. **Given** required scales are completed, **When** scoring runs, **Then** the system stores raw answers and structured scores.

---

### User Story 2 - Triage-Based Feature Access (Priority: P0)

As a user, I should only see features allowed by my triage channel.

**Why this priority**: Prevents unsafe access to AI coaching for non-green users.

**Independent Test**: Simulate green/yellow/red scale results and verify entitlements.

**Acceptance Scenarios**:

1. **Given** green channel, **When** user opens AI coaching, **Then** access is granted.
2. **Given** yellow or red channel, **When** user opens AI coaching, **Then** access is blocked and guidance is shown.

### Edge Cases

- User closes app during assessment and resumes later.
- Scale responses change from green to red during periodic retest.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support registration, login, and consent capture.
- **FR-002**: System MUST require PHQ-9, GAD-7, PSS-10, and C-SSRS before core feature unlock.
- **FR-003**: System MUST compute triage channel by constitutional thresholds.
- **FR-004**: System MUST enforce channel-based entitlements.
- **FR-005**: System MUST support periodic reassessment schedules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of new users receive a triage result after mandatory scales.
- **SC-002**: AI coaching access denial accuracy for non-green users is 100% in test suite.
- **SC-003**: Reassessment scheduler creates next due dates for >99% users.

## Clarifications

- C-SSRS uses screener version for MVP.
- SCL-90 is optional in MVP and can be introduced in Phase 2.
EOF_SPEC_001

write_if_missing "$SPECS_DIR/001-user-registration-assessment/plan.md" <<'EOF_PLAN_001'
# Implementation Plan: User Registration And Assessment

**Branch**: `[001-user-registration-assessment]` | **Date**: 2026-02-15 | **Spec**: `/specs/001-user-registration-assessment/spec.md`
**Input**: Feature specification from `/specs/001-user-registration-assessment/spec.md`

## Summary

Build onboarding, mandatory scale workflow, triage service, and channel-based access guard.

## Technical Context

**Language/Version**: TypeScript 5.x (target)
**Primary Dependencies**: Node.js web framework (TBD), validation library, scheduler
**Storage**: PostgreSQL (target)
**Testing**: vitest/jest + API contract tests
**Target Platform**: Web backend + web app
**Project Type**: web
**Constraints**: Must follow constitution redlines and triage thresholds

## Constitution Check

*GATE: Must pass before implementation. Align with .specify/memory/constitution.md*

- [ ] Product boundary: Non-medical, no diagnosis
- [ ] Safety redlines: No forbidden statements
- [ ] Safety mechanism: Triage + risk guard integrated
- [ ] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/001-user-registration-assessment/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/auth/
backend/src/modules/assessment/
backend/src/modules/triage/
```

## Implementation Phases

1. Identity, consent, and profile baseline
2. Scale engine and triage rule implementation
3. Access control and full test coverage
EOF_PLAN_001

write_if_missing "$SPECS_DIR/001-user-registration-assessment/tasks.md" <<'EOF_TASK_001'
# Tasks: User Registration And Assessment

**Branch**: `[001-user-registration-assessment]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Identity And Consent Baseline

- [ ] **T1.1** Create user/profile/consent data model and migrations - `backend/src/modules/user/`
- [ ] **T1.2** Implement registration/login/session APIs - `backend/src/modules/auth/`
- [ ] **T1.3** Add consent capture and policy version persistence - `backend/src/modules/compliance/`

### Phase 2: Mandatory Scale Workflow + Triage

- [ ] **T2.1** Implement PHQ-9/GAD-7/PSS-10/C-SSRS questionnaire schemas - `backend/src/modules/assessment/catalog/`
- [ ] **T2.2** Implement scoring service and normalized result storage - `backend/src/modules/assessment/scoring.service.ts`
- [ ] **T2.3** Implement triage rules (green/yellow/red) and audit log - `backend/src/modules/triage/triage.service.ts`
- [ ] **T2.4** Enforce AI coaching access only for green channel - `backend/src/modules/entitlement/`
- [ ] **T2.5** Create reassessment scheduler (30/90 day cadence) - `backend/src/modules/assessment/schedule.service.ts`

### Phase 3: Testing And Validation

- [ ] **T3.1** Unit tests for scoring and triage thresholds - `backend/tests/unit/assessment/`
- [ ] **T3.2** API contract tests for onboarding and assessment endpoints - `backend/tests/contract/assessment/`
- [ ] **T3.3** Safety tests for conversation-priority-over-scale and "joke" handling - `backend/tests/safety/triage/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
EOF_TASK_001

write_if_missing "$SPECS_DIR/002-interactive-tests/spec.md" <<'EOF_SPEC_002'
# Feature Specification: Interactive Psychological Tests

**Feature Branch**: `[002-interactive-tests]`
**Created**: 2026-02-15
**Status**: Draft
**Input**: roadmap.md v2.0 growth section

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete Core Personality Tests (Priority: P0)

As a user, I can complete core non-clinical tests and receive structured results after subscription.

**Why this priority**: Growth engine and profile enrichment for coaching context.

**Independent Test**: Finish MBTI/Big Five/Attachment/Love Language and verify result generation.

**Acceptance Scenarios**:

1. **Given** test answers submitted, **When** scoring completes, **Then** result profile is stored.
2. **Given** no active subscription, **When** user opens detailed report, **Then** paywall is shown.

---

### User Story 2 - Shareable Result Cards + Pairing (Priority: P1)

As a user, I can share test cards and optionally pair with a friend.

**Why this priority**: Supports social distribution and acquisition.

**Independent Test**: Generate share card and run friend pairing report.

**Acceptance Scenarios**:

1. **Given** completed test, **When** user taps share, **Then** a vertical card is generated.
2. **Given** two users complete pairing tests, **When** pairing report runs, **Then** compatibility summary is available.

### Edge Cases

- User submits incomplete questionnaire.
- Test catalog updates while old answers exist.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a configurable test catalog with theory metadata.
- **FR-002**: System MUST support MBTI/16P/Big Five/Attachment/Love Language in MVP.
- **FR-003**: System MUST store raw answers and scored dimensions.
- **FR-004**: System MUST apply subscription gating for full reports.
- **FR-005**: System MUST provide share card and optional pairing flows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Core test completion flow success rate >95% in QA.
- **SC-002**: Report gating behaves correctly in 100% entitlement tests.
- **SC-003**: Share-card generation succeeds for >99% completed tests.

## Clarifications

- Only theory-backed tests are allowed.
EOF_SPEC_002

write_if_missing "$SPECS_DIR/002-interactive-tests/plan.md" <<'EOF_PLAN_002'
# Implementation Plan: Interactive Psychological Tests

**Branch**: `[002-interactive-tests]` | **Date**: 2026-02-15 | **Spec**: `/specs/002-interactive-tests/spec.md`
**Input**: Feature specification from `/specs/002-interactive-tests/spec.md`

## Summary

Build an extensible interactive test system with scoring, report paywall, share cards, and pairing.

## Technical Context

**Language/Version**: TypeScript 5.x (target)
**Primary Dependencies**: Schema engine, scoring service, media generation
**Storage**: PostgreSQL + object storage for cards
**Testing**: unit + contract + safety suites
**Target Platform**: Web
**Project Type**: web
**Constraints**: Tests must have psychological theory references

## Constitution Check

- [ ] Product boundary: Non-medical test language only
- [ ] Safety redlines: No diagnosis or medication advice in reports
- [ ] Safety mechanism: Risk signals forwarded to safety module
- [ ] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/002-interactive-tests/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/tests/
backend/src/modules/cards/
```

## Implementation Phases

1. Catalog + scoring engine
2. Report/paywall + card generation
3. Pairing flow + validation coverage
EOF_PLAN_002

write_if_missing "$SPECS_DIR/002-interactive-tests/tasks.md" <<'EOF_TASK_002'
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
EOF_TASK_002

write_if_missing "$SPECS_DIR/003-ai-coach-core/spec.md" <<'EOF_SPEC_003'
# Feature Specification: AI Coach Core

**Feature Branch**: `[003-ai-coach-core]`
**Created**: 2026-02-15
**Status**: Draft
**Input**: roadmap.md AI coach module + constitution redlines

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Safe AI Coaching For Green Users (Priority: P0)

As a green-channel user, I can start a coaching conversation with a selected style.

**Why this priority**: Core differentiating value of MindCoach AI.

**Independent Test**: Create a green user, choose style, complete one session and get summary.

**Acceptance Scenarios**:

1. **Given** green channel user, **When** session starts, **Then** AI coaching is available.
2. **Given** non-green user, **When** session starts, **Then** coaching is denied with guidance.

---

### User Story 2 - Prompt Layering + Session Memory (Priority: P0)

As a system, I should combine system/style/context prompts and keep cross-session summaries.

**Why this priority**: Ensures quality, consistency, and continuity.

**Independent Test**: Run two sessions and confirm second session loads prior summary.

**Acceptance Scenarios**:

1. **Given** style selected, **When** request is built, **Then** system+style+context layers are all present.
2. **Given** session ends, **When** post-processing runs, **Then** summary is generated and indexed.

### Edge Cases

- Session interrupted by safety trigger.
- User switches style between sessions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST enforce green-channel-only AI coaching access.
- **FR-002**: System MUST implement immutable system prompt layer with redline rules.
- **FR-003**: System MUST implement style prompt modules (at least 2 in MVP).
- **FR-004**: System MUST ingest profile/assessment/journal context.
- **FR-005**: System MUST generate session summaries and cross-session memory indexes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Prompt layer integrity checks pass for 100% sampled sessions.
- **SC-002**: Session summary generation success rate >99%.
- **SC-003**: Safety intercept integration blocks prohibited response paths in tests.

## Clarifications

- MVP styles: Warm Guide (humanistic) + Rational Analysis (CBT).
EOF_SPEC_003

write_if_missing "$SPECS_DIR/003-ai-coach-core/plan.md" <<'EOF_PLAN_003'
# Implementation Plan: AI Coach Core

**Branch**: `[003-ai-coach-core]` | **Date**: 2026-02-15 | **Spec**: `/specs/003-ai-coach-core/spec.md`
**Input**: Feature specification from `/specs/003-ai-coach-core/spec.md`

## Summary

Deliver MVP coaching engine with layered prompts, style modules, session lifecycle, and memory integration.

## Technical Context

**Language/Version**: TypeScript 5.x + LLM provider SDK
**Primary Dependencies**: Prompt builder, vector store adapter, moderation gateway
**Storage**: PostgreSQL + vector database
**Testing**: unit + contract + safety + prompt regression tests
**Target Platform**: Web backend
**Project Type**: web
**Constraints**: Must integrate with feature 006 safety system

## Constitution Check

- [ ] Product boundary: Coaching language only, no diagnosis/treatment
- [ ] Safety redlines: Forbidden advice and promises blocked
- [ ] Safety mechanism: Every turn goes through risk detection gateway
- [ ] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/003-ai-coach-core/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/coach/
backend/src/modules/prompt/
backend/src/modules/memory/
```

## Implementation Phases

1. Prompt stack and style modules
2. Session orchestration and summaries
3. Memory retrieval and safety integration
EOF_PLAN_003

write_if_missing "$SPECS_DIR/003-ai-coach-core/tasks.md" <<'EOF_TASK_003'
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
EOF_TASK_003

write_if_missing "$SPECS_DIR/004-healing-tools/spec.md" <<'EOF_SPEC_004'
# Feature Specification: Healing Tools

**Feature Branch**: `[004-healing-tools]`
**Created**: 2026-02-15
**Status**: Draft
**Input**: roadmap.md healing tools + P1 journal scope

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Core Healing Toolkit (Priority: P0)

As a subscribed user, I can use white noise, breathing exercises, and guided meditation.

**Why this priority**: Provides broad value across channels and supports retention.

**Independent Test**: Start each tool and complete one full usage flow.

**Acceptance Scenarios**:

1. **Given** base subscription active, **When** user starts white noise, **Then** audio plays with timer control.
2. **Given** user starts breathing tool, **When** exercise completes, **Then** completion event is stored.

---

### User Story 2 - Mood Journal Integration (Priority: P1)

As a user, I can log moods and have it available to AI context.

**Why this priority**: Adds longitudinal emotional data and coaching personalization.

**Independent Test**: Log 7 days of mood entries and verify trend + AI context availability.

**Acceptance Scenarios**:

1. **Given** mood entry submitted, **When** timeline is queried, **Then** trend view is generated.
2. **Given** coaching session starts, **When** context is built, **Then** recent journal summary is included.

### Edge Cases

- Offline usage and delayed sync.
- Missing audio source fallback.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide white noise/ambient audio tool.
- **FR-002**: System MUST provide guided breathing exercise with visual pacing.
- **FR-003**: System MUST provide guided meditation playback.
- **FR-004**: System MUST provide mood journal with trend view.
- **FR-005**: System MUST expose journal summary for AI context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Tool startup success rate >99% in QA.
- **SC-002**: Journal entry API success rate >99%.
- **SC-003**: Context pipeline includes journal summary in 100% eligible sessions.

## Clarifications

- All channels can access healing tools with base subscription.
EOF_SPEC_004

write_if_missing "$SPECS_DIR/004-healing-tools/plan.md" <<'EOF_PLAN_004'
# Implementation Plan: Healing Tools

**Branch**: `[004-healing-tools]` | **Date**: 2026-02-15 | **Spec**: `/specs/004-healing-tools/spec.md`
**Input**: Feature specification from `/specs/004-healing-tools/spec.md`

## Summary

Build MVP healing tools and mood journal with backend APIs and AI context integration hooks.

## Technical Context

**Language/Version**: TypeScript 5.x
**Primary Dependencies**: Media delivery, journaling service, analytics events
**Storage**: PostgreSQL + object storage
**Testing**: unit + contract + safety tests
**Target Platform**: Web/mobile web
**Project Type**: web
**Constraints**: Tools available by subscription entitlement across channels

## Constitution Check

- [ ] Product boundary: No treatment claims in tool copy
- [ ] Safety redlines: Emotional language remains non-diagnostic
- [ ] Safety mechanism: Journal risk signals forwarded to feature 006
- [ ] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/004-healing-tools/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/tools/
backend/src/modules/journal/
frontend/src/features/tools/
```

## Implementation Phases

1. Tools baseline (audio/breathing/meditation)
2. Journal + trend analytics
3. Entitlement and context integration
EOF_PLAN_004

write_if_missing "$SPECS_DIR/004-healing-tools/tasks.md" <<'EOF_TASK_004'
# Tasks: Healing Tools

**Branch**: `[004-healing-tools]` | **From**: plan.md | **Roadmap Priority**: P0/P1

## Task Breakdown

### Phase 1: Core Tools (P0)

- [ ] **T1.1** Implement white-noise audio library, timer, and playback APIs - `backend/src/modules/tools/audio/`
- [ ] **T1.2** Implement 4-7-8 breathing exercise state machine - `frontend/src/features/tools/breathing/`
- [ ] **T1.3** Implement guided meditation content APIs and playback metadata - `backend/src/modules/tools/meditation/`

### Phase 2: Mood Journal (P1)

- [ ] **T2.1** Implement mood journal entry/create/update/list APIs - `backend/src/modules/journal/`
- [ ] **T2.2** Implement 7/30-day trend calculation service - `backend/src/modules/journal/trend.service.ts`
- [ ] **T2.3** Implement journal-to-context summary adapter for coach module - `backend/src/modules/journal/context.adapter.ts`

### Phase 3: Validation And Guardrails

- [ ] **T3.1** Unit tests for breathing timer, trend calculations, and adapters - `backend/tests/unit/tools/`
- [ ] **T3.2** API contract tests for tools and journal endpoints - `backend/tests/contract/tools/`
- [ ] **T3.3** Safety tests for risk-signal forwarding from journal entries - `backend/tests/safety/journal/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
EOF_TASK_004

write_if_missing "$SPECS_DIR/005-subscription-billing/spec.md" <<'EOF_SPEC_005'
# Feature Specification: Subscription And Billing

**Feature Branch**: `[005-subscription-billing]`
**Created**: 2026-02-15
**Status**: Draft
**Input**: roadmap.md pricing model and entitlement rules

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tiered Subscription Purchase (Priority: P0)

As a user, I can purchase base plan or coach plan with correct entitlement outcomes.

**Why this priority**: Monetization and feature unlock depend on this module.

**Independent Test**: Purchase base and coach plans and verify access differences.

**Acceptance Scenarios**:

1. **Given** free user, **When** base plan purchase succeeds, **Then** reports/tools unlock.
2. **Given** green user with base plan, **When** coach plan purchase succeeds, **Then** AI session quota unlocks.

---

### User Story 2 - Trial + Quota Enforcement (Priority: P0)

As a user, I can receive 7-day base trial; as system, monthly AI quota is enforced.

**Why this priority**: Required by pricing policy and cost control.

**Independent Test**: Activate trial, simulate expiry, and validate quota deductions.

**Acceptance Scenarios**:

1. **Given** new user, **When** registration completes, **Then** base trial starts automatically.
2. **Given** coach subscriber, **When** session quota consumed, **Then** next session is denied with renewal prompt.

### Edge Cases

- Payment webhook retries/out-of-order events.
- Trial abuse attempts with repeated account creation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support Free/Base/Coach tiers and trial.
- **FR-002**: System MUST enforce coach plan only for green channel users.
- **FR-003**: System MUST enforce monthly AI session quota.
- **FR-004**: System MUST process payment webhooks idempotently.
- **FR-005**: System MUST expose entitlement API used by all modules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Entitlement correctness reaches 100% on billing regression suite.
- **SC-002**: Webhook idempotency tests pass for duplicates/out-of-order payloads.
- **SC-003**: Trial start and expiry jobs execute successfully for >99% users.

## Clarifications

- Exact pricing amounts remain configurable via admin settings.
EOF_SPEC_005

write_if_missing "$SPECS_DIR/005-subscription-billing/plan.md" <<'EOF_PLAN_005'
# Implementation Plan: Subscription And Billing

**Branch**: `[005-subscription-billing]` | **Date**: 2026-02-15 | **Spec**: `/specs/005-subscription-billing/spec.md`
**Input**: Feature specification from `/specs/005-subscription-billing/spec.md`

## Summary

Implement billing engine, entitlement service, trial lifecycle, and quota enforcement with payment webhook reliability.

## Technical Context

**Language/Version**: TypeScript 5.x
**Primary Dependencies**: Payment provider SDK (TBD), scheduler, entitlement cache
**Storage**: PostgreSQL
**Testing**: unit + contract + safety tests
**Target Platform**: Web backend
**Project Type**: web
**Constraints**: Coach plan usable only for green-channel users

## Constitution Check

- [ ] Product boundary: Billing copy avoids medical claims
- [ ] Safety redlines: Access controls enforce non-green restrictions
- [ ] Safety mechanism: Entitlement checks integrated before AI use
- [ ] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/005-subscription-billing/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/billing/
backend/src/modules/entitlement/
```

## Implementation Phases

1. Product and plan model
2. Payment + webhook + trial lifecycle
3. Entitlement and quota validation
EOF_PLAN_005

write_if_missing "$SPECS_DIR/005-subscription-billing/tasks.md" <<'EOF_TASK_005'
# Tasks: Subscription And Billing

**Branch**: `[005-subscription-billing]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Plans And Entitlement Core

- [ ] **T1.1** Define plan catalog (Free/Base/Coach/Trial) and entitlement matrix - `backend/src/modules/billing/catalog/`
- [ ] **T1.2** Implement entitlement service shared by all feature guards - `backend/src/modules/entitlement/entitlement.service.ts`
- [ ] **T1.3** Implement green-channel guard for coach plan purchase and usage - `backend/src/modules/billing/coach.guard.ts`

### Phase 2: Payment And Lifecycle

- [ ] **T2.1** Implement checkout session API and order persistence - `backend/src/modules/billing/checkout/`
- [ ] **T2.2** Implement idempotent webhook processor (dedupe + ordering) - `backend/src/modules/billing/webhook/`
- [ ] **T2.3** Implement 7-day trial activation and expiry jobs - `backend/src/modules/billing/trial/`
- [ ] **T2.4** Implement monthly AI session quota tracking and reset jobs - `backend/src/modules/billing/quota/`

### Phase 3: Validation And Compliance

- [ ] **T3.1** Unit tests for entitlement matrix, quota math, and webhook idempotency - `backend/tests/unit/billing/`
- [ ] **T3.2** API contract tests for checkout/webhook/entitlement endpoints - `backend/tests/contract/billing/`
- [ ] **T3.3** Safety tests for blocked coach access in yellow/red channels - `backend/tests/safety/billing/`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x
EOF_TASK_005

write_if_missing "$SPECS_DIR/006-safety-nlu-crisis/spec.md" <<'EOF_SPEC_006'
# Feature Specification: Safety NLU And Crisis Intervention

**Feature Branch**: `[006-safety-nlu-crisis]`
**Created**: 2026-02-15
**Status**: Draft
**Input**: constitution redlines + roadmap safety chapter

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real-Time Dual-Layer Risk Detection (Priority: P0)

As a user, every message should be screened by safety detection before normal conversation continues.

**Why this priority**: This is the primary safety baseline and redline defense.

**Independent Test**: Send low/medium/high/extreme risk utterances and verify proper level assignment.

**Acceptance Scenarios**:

1. **Given** any message, **When** it enters pipeline, **Then** NLU fast classifier runs first.
2. **Given** non-high-risk signal, **When** fast layer returns, **Then** LLM semantic judge runs within latency budget.

---

### User Story 2 - Crisis Response Orchestration (Priority: P0)

As a system, I must stop normal counseling and trigger graded crisis responses.

**Why this priority**: Prevents unsafe continuation during risk situations.

**Independent Test**: Simulate each risk level and verify actions (pause/stop/resources/alerts).

**Acceptance Scenarios**:

1. **Given** level 2 risk, **When** detected, **Then** topic pauses and resources are shown.
2. **Given** level 3/4 risk, **When** detected, **Then** counseling is stopped and crisis protocol runs.

### Edge Cases

- User says risk statement is "just joking".
- Model failure or timeout during risk response.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST run dual-layer detection for every user message.
- **FR-002**: System MUST implement four-level response policy.
- **FR-003**: System MUST treat dialogue risk signal as higher priority than previous scale state.
- **FR-004**: System MUST ignore "joke" disclaimers and still run full safety response.
- **FR-005**: System MUST expose local hotline fallback data for client offline/error states.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: NLU classifier p95 latency <100ms in benchmark suite.
- **SC-002**: Semantic judge p95 latency <2s in benchmark suite.
- **SC-003**: High-risk recall target >=99% on safety evaluation set.
- **SC-004**: Crisis response policy assertions pass for all four levels.

## Clarifications

- Extreme-level emergency actions depend on legal/compliance region policy flags.
EOF_SPEC_006

write_if_missing "$SPECS_DIR/006-safety-nlu-crisis/plan.md" <<'EOF_PLAN_006'
# Implementation Plan: Safety NLU And Crisis Intervention

**Branch**: `[006-safety-nlu-crisis]` | **Date**: 2026-02-15 | **Spec**: `/specs/006-safety-nlu-crisis/spec.md`
**Input**: Feature specification from `/specs/006-safety-nlu-crisis/spec.md`

## Summary

Implement dual-layer risk detection, four-level crisis orchestration, and fail-safe hotline fallback.

## Technical Context

**Language/Version**: TypeScript 5.x + model inference services
**Primary Dependencies**: NLU classifier, LLM moderation endpoint, policy engine
**Storage**: PostgreSQL + secure audit log
**Testing**: unit + contract + safety + benchmark tests
**Target Platform**: Web backend + client fallback package
**Project Type**: web
**Constraints**: Safety has strict fail-closed behavior; false positives preferred over false negatives

## Constitution Check

- [ ] Product boundary: Safety language remains non-diagnostic
- [ ] Safety redlines: No continuation of normal counseling after high risk
- [ ] Safety mechanism: Dual-layer + four-level response fully implemented
- [ ] Technical standards: Unit/API/Safety tests and latency benchmarks

## Project Structure

```
specs/006-safety-nlu-crisis/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/safety/
client/src/safety/
```

## Implementation Phases

1. Risk detection engines and policy model
2. Crisis orchestration and alerting
3. Benchmarking, regression hardening, and fallback delivery
EOF_PLAN_006

write_if_missing "$SPECS_DIR/006-safety-nlu-crisis/tasks.md" <<'EOF_TASK_006'
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
EOF_TASK_006

echo "Initialization complete."
