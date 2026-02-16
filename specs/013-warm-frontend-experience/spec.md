# Feature Specification: Warm Frontend Experience

**Feature Branch**: `[013-warm-frontend-experience]`
**Created**: 2026-02-16
**Status**: Implemented (Prototype)
**Input**: User description: "按照核心宪法实现一个漂亮温馨前端"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Safe Warm Welcome (Priority: P0)

As a first-time user, I can open a warm and clear landing page that states product boundaries and safety principles.

**Why this priority**: Product boundary and safety redlines are constitutional gates and must be visible before interaction.

**Independent Test**: Open the web app root page and verify non-medical statement, crisis resources, and bilingual toggle.

**Acceptance Scenarios**:

1. **Given** user opens the page, **When** hero content renders, **Then** non-medical boundary and safety promise are clearly shown.
2. **Given** user needs help urgently, **When** crisis area is visible, **Then** hotline resources are immediately accessible.

---

### User Story 2 - Guided Prototype Journey (Priority: P0)

As a prototype user, I can complete register -> baseline assessment -> healing tools/journal -> coach flow from one interface.

**Why this priority**: It validates MVP journey and makes backend modules observable without API-only operation.

**Independent Test**: Use one page to complete all actions and check activity log responses.

**Acceptance Scenarios**:

1. **Given** API is running, **When** user executes each module action, **Then** interface shows success/failure feedback and structured logs.
2. **Given** coach session enters risk mode, **When** API returns crisis/safety action, **Then** UI highlights pause/halt state and resource guidance.

### Edge Cases

- API endpoint unavailable or network blocked.
- User triggers tool/coach action before registration.
- Cross-language copy consistency across all labels.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a warm bilingual (ZH/EN) frontend shell.
- **FR-002**: System MUST prominently show non-medical boundary and safety redline reminders.
- **FR-003**: Users MUST be able to trigger key prototype APIs from UI controls.
- **FR-004**: System MUST surface crisis resources and cache-like local hotline references in UI.
- **FR-005**: System MUST support responsive mobile/desktop layouts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Root page loads without JS errors and renders all core sections.
- **SC-002**: Main flows (register/assessment/tools/journal/coach) can be triggered via UI controls.
- **SC-003**: Safety boundary and crisis resource area is visible within first viewport on desktop.

## Clarifications

- Frontend is a prototype shell with direct API calls and a local activity log.
