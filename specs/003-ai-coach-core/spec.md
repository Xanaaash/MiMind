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
