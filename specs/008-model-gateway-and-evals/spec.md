# Feature Specification: Model Gateway And Safety Evals

**Feature Branch**: `[008-model-gateway-and-evals]`
**Created**: 2026-02-16
**Status**: In Progress (Prototype)
**Input**: docs/model-integration-next-step-v1.md + constitution.md

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unified Model Gateway For Safety Tasks (Priority: P0)

As a platform engineer, I can invoke safety model tasks through one gateway interface instead of hard-coding provider logic in service layers.

**Why this priority**: Enables provider swapping, unified telemetry, and consistent fail-closed controls.

**Independent Test**: Route `safety_nlu_fast` and `safety_semantic_judge` requests through gateway and verify normalized outputs.

**Acceptance Scenarios**:

1. **Given** NLU task request, **When** gateway executes, **Then** response contains normalized level/reasons/latency/provider trace.
2. **Given** semantic task request, **When** provider fails, **Then** caller can trigger fail-closed safety behavior.

---

### User Story 2 - Safety Detector Uses Gateway Routing (Priority: P0)

As a safety runtime, I use gateway-routed NLU + semantic results while preserving constitutional safety behavior.

**Why this priority**: Introduces model abstraction without regressing crisis protection.

**Independent Test**: Existing safety unit/contract suites pass with detector refactored to gateway.

**Acceptance Scenarios**:

1. **Given** high-risk utterance, **When** detector runs, **Then** high/extreme routing still short-circuits to crisis path.
2. **Given** detector internal failure, **When** detection runs, **Then** system fail-closes to high risk.

### Edge Cases

- Unsupported gateway task type.
- Provider timeout / exception.
- Missing response fields from provider adapter.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST define a model gateway abstraction with typed request/response contracts.
- **FR-002**: System MUST provide default provider adapters for safety NLU and semantic tasks.
- **FR-003**: Safety detector MUST consume NLU and semantic outputs via the gateway.
- **FR-004**: Safety detector MUST preserve fail-closed and joke-disclaimer constitutional rules.
- **FR-005**: Gateway responses MUST include basic telemetry fields (`provider`, `latency_ms`, `trace_id`).
- **FR-006**: System MUST include tests for gateway routing and safety detector regression.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Existing safety contract and regression suites continue to pass.
- **SC-002**: NLU p95 and semantic p95 benchmarks remain within existing thresholds.
- **SC-003**: Gateway unit tests cover success + unsupported task + provider error paths.

## Clarifications

- This phase introduces abstraction and routing only; production external model providers are deferred.
- Evaluation harness in this phase is baseline-oriented (latency + deterministic regression), not full offline dataset scoring.
