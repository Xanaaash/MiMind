# Implementation Plan: Scale And Test Foundation Expansion

**Branch**: `codex/007-scale-test-foundation` | **Date**: 2026-02-16 | **Spec**: `specs/007-scale-test-foundation/spec.md`

## Summary

Deliver initial-stage expansion for all required scale/test capabilities from roadmap v2:

1. Extend clinical scale matrix with SCL-90 support and catalog/score APIs.
2. Extend interactive test matrix with five P1 tests and deterministic scoring.
3. Expose frontend-consumable input contracts via enriched catalog metadata and per-test schema endpoint.
4. Maintain constitution safety boundaries with non-diagnostic report language and channel gating.

## Technical Context

- Runtime: Python 3.9+, FastAPI
- Data layer: in-memory store for prototype
- Test framework: unittest
- Existing baseline: 001-006 features already integrated in single app service

## Constitution Check

- Product boundary: no diagnosis/treatment/medication suggestions.
- Safety redlines: report text and coaching restrictions remain intact.
- Technical standard: unit + contract + safety regression coverage required.

## Design Decisions

- Keep scoring deterministic and auditable for MVP.
- Add metadata contracts (`required_answer_keys`, `answer_range`, `category`) to avoid frontend hardcoded schemas.
- Keep SCL-90 optional in onboarding submission while allowing triage yellow modifier.

## Work Breakdown

1. Clinical scale expansion
2. Interactive scoring expansion
3. Catalog schema endpoint and metadata enrichment
4. Contract/unit regression coverage
5. Documentation/spec alignment

## Testing Strategy

- Unit tests: scoring functions and guardrails for new test types.
- Contract tests: API-level submit/report/share/pairing and catalog contracts.
- Platform tests: FastAPI HTTP route coverage for new catalog item endpoint.
- Full regression: `scripts/run-backend-tests.sh`

## Risks

- Simplified scoring may diverge from future psychometric standards.
- In-memory persistence limits production-readiness and historical analytics.

## Deferred

- Localized question banks (`zh-CN` / `en-US`) and item-level questionnaire assets.
- Persistent relational storage for result history.
- Psychometric calibration and reliability validation datasets.
