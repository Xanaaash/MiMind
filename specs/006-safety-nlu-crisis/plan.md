# Implementation Plan: Safety NLU And Crisis Intervention

**Branch**: `[006-safety-nlu-crisis]` | **Date**: 2026-02-15 | **Spec**: `/specs/006-safety-nlu-crisis/spec.md`
**Input**: Feature specification from `/specs/006-safety-nlu-crisis/spec.md`

## Summary

Implement dual-layer risk detection, four-level crisis orchestration, and fail-safe hotline fallback.

## Technical Context

**Language/Version**: TypeScript 5.x + model inference services
**Primary Dependencies**: NLU classifier, LLM moderation endpoint, policy engine
**Storage**: PostgreSQL + secure audit log
**Testing**: unit + contract + safety + benchmark tests
**Target Platform**: Web backend + client fallback package
**Project Type**: web
**Constraints**: Safety has strict fail-closed behavior; false positives preferred over false negatives

## Constitution Check

- [ ] Product boundary: Safety language remains non-diagnostic
- [ ] Safety redlines: No continuation of normal counseling after high risk
- [ ] Safety mechanism: Dual-layer + four-level response fully implemented
- [ ] Technical standards: Unit/API/Safety tests and latency benchmarks

## Project Structure

```
specs/006-safety-nlu-crisis/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/safety/
client/src/safety/
```

## Implementation Phases

1. Risk detection engines and policy model
2. Crisis orchestration and alerting
3. Benchmarking, regression hardening, and fallback delivery
