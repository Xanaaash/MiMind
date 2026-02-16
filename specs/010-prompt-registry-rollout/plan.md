# Implementation Plan: Prompt Registry And Rollback Controls

**Branch**: `codex/010-prompt-registry-rollout` | **Date**: 2026-02-16 | **Spec**: `specs/010-prompt-registry-rollout/spec.md`

## Summary

Introduce a versioned prompt registry with runtime activation/rollback and integrate existing prompt accessors + coach session metadata to use the active prompt pack.

## Scope

1. Add prompt pack models and static catalog.
2. Add prompt registry service with list/get/activate operations.
3. Rewire system/style prompt accessors to registry runtime.
4. Add API endpoints for packs and activation.
5. Add tests and regression coverage.

## Out Of Scope

- Database-backed prompt release history.
- Percentage rollout / segment targeting.
- Approval workflow and RBAC.

## Constitution Check

- Every prompt pack must preserve non-negotiable safety redlines.
- Rollback cannot bypass safety requirements in system prompt.

## Testing Strategy

- Unit tests for prompt registry activation and validation.
- Contract tests for prompt APIs and coach prompt pack exposure.
- Full regression via `scripts/run-backend-tests.sh`.
