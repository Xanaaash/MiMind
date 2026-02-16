# Implementation Plan: Model Invocation Observability

**Branch**: `codex/012-model-observability` | **Date**: 2026-02-16 | **Spec**: `specs/012-model-observability/spec.md`

## Summary

Add gateway-level invocation audit persistence and expose read APIs for operational monitoring.

## Scope

1. Add observability record models.
2. Extend in-memory store for model invocation records.
3. Add gateway persistence hooks for success/failure.
4. Wire coach and safety gateway instances to store-backed auditing.
5. Add observability endpoint with limit/filter options.
6. Add unit + contract tests and run full regression.

## Out Of Scope

- Persistent database sink.
- Real-time dashboards/alerts.
- Billing reconciliation from model costs.

## Constitution Check

- Observability records must not weaken safety flow control.
- Failure in audit persistence must not crash safety critical runtime.

## Testing Strategy

- Unit tests for gateway audit persistence and cost estimate shape.
- Contract tests for observability API listing and filters.
- Existing safety/coach tests to verify no behavior regressions.
