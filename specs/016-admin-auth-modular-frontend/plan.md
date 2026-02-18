# Implementation Plan: Admin Auth + Modular Frontend

**Branch**: `[016-admin-auth-modular-frontend]` | **Date**: 2026-02-16 | **Spec**: `specs/016-admin-auth-modular-frontend/spec.md`
**Input**: Feature specification from `/specs/016-admin-auth-modular-frontend/spec.md`

## Summary

Implement backend admin cookie session auth and rebuild frontend into a login-gated modular shell with full clinical scale and interactive test centers.

## Technical Context

**Language/Version**: Python 3.9, HTML/CSS/Vanilla JavaScript
**Primary Dependencies**: FastAPI, uvicorn, pytest
**Storage**: InMemoryStore + SQLiteStore
**Testing**: pytest + existing contract/unit structure
**Target Platform**: Web (desktop/mobile web)
**Project Type**: web
**Constraints**: Maintain constitution safety boundary copy and existing API compatibility

## Constitution Check

*GATE: Must pass before implementation. Align with .specify/memory/constitution.md*

- [x] Product boundary: Non-medical, no diagnosis
- [x] Safety redlines: No forbidden statements in UI copy
- [x] Safety mechanism: Crisis resource copy remains visible
- [x] Technical standards: Unit/contract/safety/frontend coverage added

## Project Structure

```
specs/016-admin-auth-modular-frontend/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/admin/
backend/src/modules/api/admin_endpoints.py
backend/src/modules/storage/in_memory.py
backend/src/modules/storage/sqlite_store.py
backend/src/app.py

frontend/index.html
frontend/styles.css
frontend/app.js
frontend/README.md

backend/tests/unit/admin/
backend/tests/unit/storage/
backend/tests/contract/admin/
backend/tests/unit/frontend/
backend/tests/contract/platform/
backend/tests/safety/frontend/
```

## Implementation Phases

1. Admin auth module + storage persistence + API wiring
2. Frontend modular shell and dynamic scale/test centers
3. Contract/unit/safety/frontend validation and deferred task marking
