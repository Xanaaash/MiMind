# Implementation Plan: User Auth With JWT Cookie Session

**Branch**: `[018-user-auth-jwt-session]` | **Date**: 2026-02-20 | **Spec**: `/specs/018-user-auth-jwt-session/spec.md`  
**Input**: Feature specification from `/specs/018-user-auth-jwt-session/spec.md`

## Summary

Implement production-oriented user password auth for web user frontend:
- Add backend user auth APIs (`/api/auth/*`) with JWT access/refresh cookies.
- Persist password hash and auth provider in store layers.
- Replace frontend temporary identity flow with real register/login/session restore/logout.
- Preserve existing onboarding `/api/register` compatibility and existing risk/triage contracts.

## Technical Context

**Language/Version**: Python 3.11, TypeScript 5.x  
**Primary Dependencies**: FastAPI, React, Zustand, i18next  
**Storage**: SQLiteStore + InMemoryStore abstraction  
**Testing**: unittest contract/unit tests, frontend build check  
**Target Platform**: Web (backend + frontend/user)  
**Project Type**: web  
**Constraints**: Non-medical boundary, no safety regression, backward compatibility for current onboarding tests

## Constitution Check

*GATE: Must pass before implementation. Align with .specify/memory/constitution.md*

- [x] Product boundary: Non-medical, no diagnosis
- [x] Safety redlines: No forbidden statements
- [x] Safety mechanism: Existing safety flow untouched; auth change must not bypass triage guard
- [x] Technical standards: Unit tests + API contract tests + frontend build

## Project Structure

```
specs/018-user-auth-jwt-session/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/auth/
backend/src/modules/api/auth_endpoints.py
backend/src/app.py
backend/src/modules/storage/{in_memory.py,sqlite_store.py}
backend/src/modules/user/models.py
backend/tests/unit/auth/
backend/tests/contract/auth/
frontend/user/src/pages/Auth/Auth.tsx
frontend/user/src/api/auth.ts
frontend/user/src/stores/auth.ts
```

## Implementation Phases

1. Backend auth primitives and storage model extension (password hash + JWT + cookies)
2. API integration and frontend auth flow migration
3. Contract/unit tests, compatibility verification, and build/test validation
