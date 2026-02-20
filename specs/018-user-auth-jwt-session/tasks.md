# Tasks: User Auth With JWT Cookie Session

**Branch**: `[018-user-auth-jwt-session]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Backend Auth Foundation

- [ ] **T1.1** Extend `User` model and storage adapters for password hash/auth provider + email lookup - `backend/src/modules/user/models.py`, `backend/src/modules/storage/`
- [ ] **T1.2** Implement password hashing and JWT sign/verify utilities - `backend/src/modules/auth/`
- [ ] **T1.3** Implement auth service register/login/session/refresh flow - `backend/src/modules/auth/service.py`
- [ ] **T1.4** Add `/api/auth/*` endpoint adapter and route wiring with HttpOnly cookie management - `backend/src/modules/api/auth_endpoints.py`, `backend/src/app.py`

### Phase 2: Frontend User Auth Migration

- [ ] **T2.1** Replace temporary auth flow with real register/login UI and API calls - `frontend/user/src/pages/Auth/Auth.tsx`, `frontend/user/src/api/auth.ts`
- [ ] **T2.2** Update auth store to support backend session restore and deterministic logout - `frontend/user/src/stores/auth.ts`, `frontend/user/src/components/Layout/AppLayout.tsx`
- [ ] **T2.3** Add/adjust i18n labels for auth flow and session error states - `frontend/user/public/locales/*.json`

### Phase 3: Validation And Gates

- [ ] **T3.1** Unit tests for auth service (password validation, login, token verify) - `backend/tests/unit/auth/`
- [ ] **T3.2** API contract tests for `/api/auth/register|login|session|refresh|logout` - `backend/tests/contract/auth/`
- [ ] **T3.3** Compatibility tests ensuring onboarding `/api/register` flow remains valid - `backend/tests/contract/platform/`
- [ ] **T3.4** Safety/quality gate validation: `scripts/constitution-check.sh`, backend tests, and frontend build - `scripts/`

## Dependencies

- T1.x before T2.x
- T2.x before T3.x
