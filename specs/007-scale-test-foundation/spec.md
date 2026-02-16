# Feature Specification: Scale And Test Foundation Expansion

**Feature Branch**: `[007-scale-test-foundation]`
**Created**: 2026-02-16
**Status**: In Progress (Prototype)
**Input**: roadmap.md v2.0 + constitution.md + docs/scale-test-design-v1.md

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Expand Clinical Scale Baseline (Priority: P0)

As a user, I can access a complete clinical scale catalog and submit single-scale scoring for onboarding/retest workflows.

**Why this priority**: Clinical screening is the safety baseline for downstream AI coaching access.

**Independent Test**: Query scale catalog and score PHQ-9/GAD-7/PSS-10/C-SSRS/SCL-90 through API.

**Acceptance Scenarios**:

1. **Given** scale catalog request, **When** API returns definitions, **Then** all required scales include cadence and input contract metadata.
2. **Given** SCL-90 answers, **When** scoring runs, **Then** global index and yellow-channel modifier are produced.

---

### User Story 2 - Expand Interactive Test Coverage (Priority: P0/P1)

As a user, I can complete both core and growth-oriented tests and receive non-diagnostic summaries.

**Why this priority**: Test coverage is a core growth loop and profile enrichment source for coaching context.

**Independent Test**: Submit MBTI/16P/Big5/Attachment/Love Language plus Stress Coping/EQ/Inner Child/Boundary/Psych Age and verify summaries.

**Acceptance Scenarios**:

1. **Given** catalog request, **When** user inspects one test schema, **Then** required answer keys and value range are discoverable.
2. **Given** test submission, **When** report is generated, **Then** output remains non-diagnostic and subscription-aware.

### Edge Cases

- Unsupported scale/test id submitted by client.
- Missing required keys or out-of-range values in scoring payload.
- SCL-90 present in submission while mandatory scales are incomplete.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a clinical scale catalog including PHQ-9, GAD-7, PSS-10, C-SSRS, and SCL-90.
- **FR-002**: System MUST support single-scale scoring API for each supported clinical scale.
- **FR-003**: System MUST include SCL-90 scoring in onboarding submission as an optional yellow-risk modifier.
- **FR-004**: System MUST extend interactive tests to include Stress Coping, EQ, Inner Child, Boundary, and Psychological Age.
- **FR-005**: System MUST expose interactive test catalog metadata including required answer keys and input range.
- **FR-006**: System MUST expose per-test catalog item endpoint for frontend dynamic form rendering.
- **FR-007**: Interactive reports MUST remain non-diagnostic and constitution-aligned.
- **FR-008**: New scale/test logic MUST include unit tests and API contract tests.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of supported clinical scales are discoverable in catalog APIs.
- **SC-002**: New interactive tests return deterministic summaries in contract tests.
- **SC-003**: Test suite passes with no regression in existing safety constraints.

## Clarifications

- This phase focuses on deterministic MVP scoring; psychometric calibration and norm-based interpretation are deferred.
