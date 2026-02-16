# Feature Specification: Memory Retrieval Upgrade (Embedding + Reranker)

**Feature Branch**: `[011-memory-retrieval-upgrade]`
**Created**: 2026-02-16
**Status**: In Progress (Prototype)
**Input**: docs/model-integration-next-step-v1.md + specs/009-provider-routing-coach

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Semantic Memory Indexing (Priority: P0)

As a system, session summaries should be indexed with embeddings for semantic retrieval, not only recency.

**Why this priority**: Improves cross-session continuity for coaching quality.

**Independent Test**: Index multiple summaries and verify semantic query returns relevant memories.

**Acceptance Scenarios**:

1. **Given** memory summaries are stored, **When** indexing runs, **Then** embedding vectors are persisted in memory store.
2. **Given** a query message, **When** retrieval runs, **Then** top relevant summaries are returned.

---

### User Story 2 - Reranked Memory Context In Coach Generation (Priority: P0)

As a coach runtime, model generation should receive reranked memory snippets related to current user message.

**Why this priority**: Reduces irrelevant context injection into model prompt.

**Independent Test**: Chat path includes gateway metadata with relevant memory snippets for low-risk coaching mode.

**Acceptance Scenarios**:

1. **Given** user asks about recurring work anxiety, **When** coach reply is generated, **Then** relevant historical memory is included in model context metadata.
2. **Given** retrieval providers fail, **When** chat runs, **Then** system falls back safely without breaking session flow.

### Edge Cases

- Query with no lexical overlap to stored memories.
- Provider set to external embedder without credentials.
- Empty or whitespace-only memory summary.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Memory module MUST provide embedding provider abstraction with local default implementation.
- **FR-002**: Memory module MUST provide reranker abstraction with local default implementation.
- **FR-003**: Memory summaries MUST be indexed into vector records in addition to plain text storage.
- **FR-004**: Memory service MUST expose semantic retrieval API with reranking.
- **FR-005**: Coach generation path MUST include relevant memory snippets from semantic retrieval.
- **FR-006**: System MUST include unit tests for indexing/retrieval/reranking and fallback behaviors.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Memory retrieval unit tests verify relevance ranking and edge cases.
- **SC-002**: Coach integration tests pass with memory-retrieval-enhanced metadata.
- **SC-003**: Full regression suite remains green.

## Clarifications

- This phase uses deterministic local embedding/reranking by default.
- External embedding provider is adapter-only and optional by env.
