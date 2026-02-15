# Feature Specification: User Registration And Assessment

**Feature Branch**: `[001-user-registration-assessment]`
**Created**: 2026-02-15
**Status**: Implemented (Prototype)
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
