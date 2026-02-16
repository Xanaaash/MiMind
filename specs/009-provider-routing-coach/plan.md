# Implementation Plan: Provider Routing And Coach Gateway Integration

**Branch**: `codex/009-provider-routing-coach` | **Date**: 2026-02-16 | **Spec**: `specs/009-provider-routing-coach/spec.md`

## Summary

Extend the model gateway from safety-only routing to coach generation, then add configurable provider routing (default local, optional external adapter) with safe behavior under missing credentials or provider errors.

## Scope

1. Add `coach_generation` task type and local coach provider.
2. Add gateway configuration resolver for task->provider mapping.
3. Add optional external coach provider adapter (env-gated).
4. Refactor coach session reply generation to use gateway.
5. Add unit/contract regression tests.

## Out Of Scope

- Prompt registry/versioning controls.
- Embedding and reranker integration.
- Persistent model trace store.

## Constitution Check

- Safety interception remains highest priority and unchanged.
- No diagnostic or treatment language may be introduced.
- Fail-safe behavior remains required for any provider exceptions.

## Testing Strategy

- Unit tests for gateway routing and provider error paths.
- Coach contract tests for start/chat/end flow.
- Coach safety tests for pause/crisis interception.
- Full regression suite via `scripts/run-backend-tests.sh`.
