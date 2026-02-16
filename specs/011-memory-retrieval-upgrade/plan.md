# Implementation Plan: Memory Retrieval Upgrade (Embedding + Reranker)

**Branch**: `codex/011-memory-retrieval-upgrade` | **Date**: 2026-02-16 | **Spec**: `specs/011-memory-retrieval-upgrade/spec.md`

## Summary

Upgrade memory from recency-only retrieval to semantic retrieval using embedding + reranker providers, then wire relevant memory snippets into coach model generation metadata.

## Scope

1. Add memory provider abstractions and local implementations.
2. Add optional external embedding adapter (env-gated).
3. Extend in-memory store for vector records.
4. Upgrade memory service indexing + semantic retrieval.
5. Integrate coach generation metadata with relevant memories.
6. Add tests and full regression run.

## Out Of Scope

- Persistent vector database integration.
- Multi-tenant memory sharding.
- Retrieval metrics dashboard.

## Constitution Check

- Retrieval content is reflective support context only; no diagnostic output logic is introduced.
- Safety interruption order remains unchanged and has higher priority than coaching generation.

## Testing Strategy

- Unit tests for local embedder, local reranker, memory service retrieval.
- Coach integration test to ensure memory snippets are passed.
- Full regression with `scripts/run-backend-tests.sh`.
