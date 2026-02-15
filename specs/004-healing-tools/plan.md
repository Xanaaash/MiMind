# Implementation Plan: Healing Tools

**Branch**: `[004-healing-tools]` | **Date**: 2026-02-15 | **Spec**: `/specs/004-healing-tools/spec.md`
**Input**: Feature specification from `/specs/004-healing-tools/spec.md`

## Summary

Build MVP healing tools and mood journal with backend APIs and AI context integration hooks.

## Technical Context

**Language/Version**: TypeScript 5.x
**Primary Dependencies**: Media delivery, journaling service, analytics events
**Storage**: PostgreSQL + object storage
**Testing**: unit + contract + safety tests
**Target Platform**: Web/mobile web
**Project Type**: web
**Constraints**: Tools available by subscription entitlement across channels

## Constitution Check

- [ ] Product boundary: No treatment claims in tool copy
- [ ] Safety redlines: Emotional language remains non-diagnostic
- [ ] Safety mechanism: Journal risk signals forwarded to feature 006
- [ ] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/004-healing-tools/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/tools/
backend/src/modules/journal/
frontend/src/features/tools/
```

## Implementation Phases

1. Tools baseline (audio/breathing/meditation)
2. Journal + trend analytics
3. Entitlement and context integration
