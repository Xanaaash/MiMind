# Feature Specification: User Auth With JWT Cookie Session

**Feature Branch**: `[018-user-auth-jwt-session]`  
**Created**: 2026-02-20  
**Status**: In Progress  
**Input**: todo.md T-101 + roadmap.md + constitution.md

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Password Registration And Login (Priority: P0)

As a user, I can create an account with email+password and log in with real credentials.

**Why this priority**: T-101 is a P0 launch gate for identity and account safety baseline.

**Independent Test**: Call `/api/auth/register` and `/api/auth/login` with valid/invalid payloads and verify responses and cookie behavior.

**Acceptance Scenarios**:

1. **Given** a new email, **When** user submits valid email/password, **Then** account is created and auth cookies are issued.
2. **Given** an existing email with wrong password, **When** user logs in, **Then** request fails with 401 and no authenticated session.

---

### User Story 2 - Session Restore And Logout (Priority: P0)

As an authenticated user, I stay logged in after refresh and can safely log out.

**Why this priority**: Real-world usability requires persistent auth state and deterministic logout.

**Independent Test**: Log in, request `/api/auth/session`, then `/api/auth/logout`, and confirm session transitions from authenticated to unauthenticated.

**Acceptance Scenarios**:

1. **Given** valid auth cookies, **When** frontend refreshes and checks session, **Then** authenticated user profile is returned.
2. **Given** authenticated user, **When** logout is called, **Then** cookies are cleared and subsequent session check returns 401.

### Edge Cases

- Duplicate email registration must fail with 409.
- Weak passwords must be rejected with 400.
- Expired or malformed JWT must be rejected and treated as unauthenticated.
- Legacy users without password hash must not be allowed to password-login until they complete a password registration/reset flow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide `/api/auth/register`, `/api/auth/login`, `/api/auth/session`, `/api/auth/refresh`, and `/api/auth/logout`.
- **FR-002**: System MUST hash and verify passwords server-side; plaintext password storage is forbidden.
- **FR-003**: System MUST issue access/refresh JWT via HttpOnly cookies (SameSite=Lax).
- **FR-004**: Frontend user auth page MUST use real register/login API instead of local temporary identity generation.
- **FR-005**: Existing onboarding endpoint `/api/register` MUST remain compatible for current assessment flow tests.

### Key Entities *(include if feature involves data)*

- **User**: Adds `password_hash` and `auth_provider` fields; identifies password-capable account records.
- **AuthTokenPayload**: JWT claims for `sub`, `token_type`, `iat`, `exp`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of contract tests for auth endpoints pass.
- **SC-002**: Authenticated browser refresh restores session without manual re-login.
- **SC-003**: Backend tests show wrong-password and invalid-token paths are denied with expected status codes.

## Clarifications

- Token transport uses cookie (not localStorage bearer token).
- Cookie mode follows current local dev defaults (`secure=False`) with env-based override.
- Password rule for MVP: length >= 8 and must contain letters and digits.
