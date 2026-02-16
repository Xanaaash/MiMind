# Implementation Plan: Warm Frontend Experience

**Branch**: `[013-warm-frontend-experience]` | **Date**: 2026-02-16 | **Spec**: `specs/013-warm-frontend-experience/spec.md`
**Input**: Feature specification from `/specs/013-warm-frontend-experience/spec.md`

## Summary

Build a cozy, bilingual, constitution-aligned web frontend that exposes core prototype user journeys and safety messaging without changing existing in-flight backend files.

## Technical Context

**Language/Version**: HTML5, CSS3, Vanilla JavaScript (ES2020), Python 3.9+
**Primary Dependencies**: FastAPI static hosting via existing backend dependency
**Storage**: N/A (client-only state)
**Testing**: pytest (frontend smoke test via FastAPI TestClient)
**Target Platform**: Web (desktop + mobile web)
**Project Type**: web
**Constraints**: Must preserve non-medical boundary and crisis guidance in visible UI

## Constitution Check

*GATE: Must pass before implementation. Align with .specify/memory/constitution.md*

- [x] Product boundary: Non-medical, no diagnosis
- [x] Safety redlines: No forbidden statements
- [x] Safety mechanism: Crisis resources surfaced in UI
- [x] Technical standards: Include test coverage for frontend shell

## Project Structure

```
specs/013-warm-frontend-experience/
├── spec.md
├── plan.md
└── tasks.md

frontend/
├── index.html
├── styles.css
├── app.js
└── README.md

backend/src/
└── web_app.py

backend/tests/unit/frontend/
└── test_frontend_shell.py

scripts/
└── run-web-app.sh
```

## Implementation Phases

1. Frontend shell and visual system
2. API interaction flows and safety UX
3. Runtime entrypoint and smoke validation
