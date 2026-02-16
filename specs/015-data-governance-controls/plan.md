# Implementation Plan: Data Governance Controls

**Branch**: `[015-data-governance-controls]` | **Date**: 2026-02-16 | **Spec**: `/specs/015-data-governance-controls/spec.md`
**Input**: Feature specification from `/specs/015-data-governance-controls/spec.md`

## Summary

Add export/erase compliance APIs backed by storage-layer primitives, covering both SQLite-persisted assessment/test data and in-memory runtime records.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, unittest
**Storage**: Hybrid store (`SQLiteStore` + in-memory maps)
**Testing**: Unit + contract + platform HTTP tests
**Target Platform**: Backend API
**Project Type**: web backend
**Constraints**: Must remain constitution-aligned (non-medical language, privacy-first handling)

## Constitution Check

- [x] Product boundary: Non-medical, no diagnosis semantics in compliance payloads
- [x] Safety redlines: No forbidden guidance changes introduced
- [x] Safety mechanism: Existing safety flow untouched
- [x] Technical standards: Unit/API tests added for new behavior

## Project Structure

```
specs/015-data-governance-controls/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/compliance/
backend/src/modules/api/
backend/src/modules/storage/
backend/tests/contract/
backend/tests/unit/
```

## Implementation Phases

1. Storage primitives for export/delete
2. Compliance service + API endpoints
3. Contract/platform coverage and regression validation
