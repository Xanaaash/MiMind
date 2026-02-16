# Implementation Plan: Model Gateway And Safety Evals

**Branch**: `codex/008-model-gateway-and-evals` | **Date**: 2026-02-16 | **Spec**: `specs/008-model-gateway-and-evals/spec.md`

## Summary

Introduce a `ModelGateway` layer and migrate safety detector routing to it while keeping behavior unchanged from current constitutional safety baseline.

## Scope (This Iteration)

1. Create typed gateway models and provider interface.
2. Implement default local heuristic provider for safety tasks.
3. Refactor `SafetyDetectorService` to route through gateway.
4. Add gateway unit tests and safety regression checks.

## Out Of Scope (Deferred)

- External paid model provider integrations.
- Relational persistence migration for model telemetry.
- Prompt registry rollout controls.

## Technical Context

- Runtime: Python 3.9+, FastAPI
- Existing safety stack: `modules/safety/{nlu,semantic,policy}`
- Test strategy: `unittest`, contract + safety + benchmark suites

## Constitution Check

- Safety fail-closed behavior remains mandatory.
- Dialogue risk override and joke-disclaimer handling remain mandatory.
- No diagnostic or treatment output behavior changes.

## Design Notes

- Gateway returns normalized payload for all task types:
  - `risk_level`, `reasons`, `latency_ms`, `provider`, `trace_id`, `raw`
- Safety detector maps gateway output into existing `SafetyDetectionResult`.
- Provider selection is task-based; current default provider is local heuristic provider.

## Testing Strategy

- New unit tests for gateway router.
- Updated detector tests to validate unchanged behavior.
- Existing benchmarks remain the initial eval baseline.
- Full regression via `scripts/run-backend-tests.sh`.

## Risks

- Refactor could accidentally alter reason/source formatting expected by tests.
- Gateway abstraction might hide provider exceptions if error mapping is too broad.

## Mitigations

- Keep response mapping explicit and narrow.
- Preserve existing default behavior semantics in detector service.
