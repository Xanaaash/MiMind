# Feature Specification: Healing Tools

**Feature Branch**: `[004-healing-tools]`
**Created**: 2026-02-15
**Status**: Implemented (Prototype)
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
