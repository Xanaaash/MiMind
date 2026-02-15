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
