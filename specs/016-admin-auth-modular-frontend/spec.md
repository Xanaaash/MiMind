# Feature Specification: Admin Auth + Modular Frontend

**Feature Branch**: `[016-admin-auth-modular-frontend]`
**Created**: 2026-02-16
**Status**: Implemented (Prototype)
**Input**: User description: "admin 登录管理 + 模块化导航 + 完整量表/测试入口"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin Session Gate (Priority: P0)

As an operator, I can log in with admin credentials and access protected admin interfaces via persistent session.

**Why this priority**: Frontend management experience must be gated and aligned with authentication baseline.

**Independent Test**: Login success/failure and session restore via cookie.

**Acceptance Scenarios**:

1. **Given** wrong credentials, **When** admin login is submitted, **Then** request is rejected with 401 and UI stays on login view.
2. **Given** valid credentials, **When** admin login succeeds, **Then** backend sets HttpOnly cookie and UI enters admin shell.

---

### User Story 2 - Modular Admin Shell (Priority: P0)

As an operator, I can access platform capabilities through type-based navigation rather than long stacked blocks.

**Why this priority**: Improves clarity and maintainability as modules scale.

**Independent Test**: Desktop sidebar + mobile top tab navigation can switch modules.

**Acceptance Scenarios**:

1. **Given** authenticated admin, **When** switching module tabs, **Then** only selected module content is active.
2. **Given** homepage, **When** view loads, **Then** clinical scales center and interactive tests center entry cards are both visible.

---

### User Story 3 - Full Scale/Test Entry (Priority: P0)

As an operator, I can launch every implemented clinical scale and interactive test from frontend and submit scoring.

**Why this priority**: Current frontend lacks explicit scale/test entry and dynamic questionnaire rendering.

**Independent Test**: Catalog fetch, question render, submit, and result view for all available scale/test IDs.

**Acceptance Scenarios**:

1. **Given** scales catalog is loaded, **When** one scale is selected, **Then** question bank renders and score submit works.
2. **Given** interactive tests catalog is loaded, **When** one test is selected, **Then** questions render and submit response returns summary.

### Edge Cases

- Session cookie expires during module usage.
- API unavailable while maintaining shell layout.
- Large SCL-90 questionnaire requires pagination and local unsent state retention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide admin login/logout/session APIs with HttpOnly cookie session.
- **FR-002**: System MUST gate admin shell by authenticated session state.
- **FR-003**: System MUST provide modular navigation for all platform feature types.
- **FR-004**: System MUST provide dynamic frontend entry for all clinical scales in catalog.
- **FR-005**: System MUST provide dynamic frontend entry for all interactive tests in catalog.
- **FR-006**: System MUST expose reserved user-management API endpoint and return not-implemented contract for this phase.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admin login endpoint sets HttpOnly cookie and supports session recovery.
- **SC-002**: Frontend login-gated shell renders sidebar/tabs and module switching without page reload.
- **SC-003**: Scale/test entry list matches backend catalogs and supports successful submit flow.

## Clarifications

- Admin username is fixed to `admin`.
- Password source is `ADMIN_PASSWORD` with dev fallback for local use.
- Full user-management UI is deferred; API interface is reserved in this phase.
