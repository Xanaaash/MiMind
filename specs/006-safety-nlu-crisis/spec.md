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
