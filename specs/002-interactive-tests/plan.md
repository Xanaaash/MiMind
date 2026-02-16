# Implementation Plan: Interactive Psychological Tests

**Branch**: `[002-interactive-tests]` | **Date**: 2026-02-15 | **Spec**: `/specs/002-interactive-tests/spec.md`
**Input**: Feature specification from `/specs/002-interactive-tests/spec.md`

## Summary

Build an extensible interactive test system with scoring, report paywall, share cards, and pairing.

## Technical Context

**Language/Version**: TypeScript 5.x (target)
**Primary Dependencies**: Schema engine, scoring service, media generation
**Storage**: PostgreSQL + object storage for cards
**Testing**: unit + contract + safety suites
**Target Platform**: Web
**Project Type**: web
**Constraints**: Tests must have psychological theory references

## Constitution Check

- [x] Product boundary: Non-medical test language only
- [x] Safety redlines: No diagnosis or medication advice in reports
- [x] Safety mechanism: Risk signals forwarded to safety module
- [x] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/002-interactive-tests/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/tests/
backend/src/modules/cards/
```

## Implementation Phases

1. Catalog + scoring engine
2. Report/paywall + card generation
3. Pairing flow + validation coverage
