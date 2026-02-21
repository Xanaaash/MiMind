# Tasks: Memory Retrieval Upgrade (Embedding + Reranker)

**Branch**: `[011-memory-retrieval-upgrade]` | **From**: plan.md | **Roadmap Priority**: P0

## Task Breakdown

### Phase 1: Memory Provider Foundation

- [x] **T1.1** Add memory retrieval models and vector record schema - `backend/src/modules/memory/models.py`
- [x] **T1.2** Add embedder/reranker provider interfaces and local implementations - `backend/src/modules/memory/providers/`
- [x] **T1.3** Add memory provider config loader with optional external embedder adapter - `backend/src/modules/memory/config.py`, `backend/src/modules/memory/providers/openai_embedding.py`

### Phase 2: Service And Store Integration

- [x] **T2.1** Extend in-memory store to persist vector memory records - `backend/src/modules/storage/in_memory.py`
- [x] **T2.2** Upgrade memory service to index embeddings and retrieve reranked relevant summaries - `backend/src/modules/memory/service.py`
- [x] **T2.3** Inject relevant memory snippets into coach generation metadata - `backend/src/modules/coach/session_service.py`

### Phase 3: Validation

- [x] **T3.1** Add unit tests for memory indexing/retrieval/reranking - `backend/tests/unit/memory/`
- [x] **T3.2** Extend coach integration tests for memory metadata usage - `backend/tests/unit/coach/`
- [x] **T3.3** Run full regression suite - `scripts/run-backend-tests.sh`

## Dependencies

- T2.x depends on T1.x
- T3.x depends on T2.x

## Test Gate Alignment
- Unit tests: covered by corresponding backend/frontend unit suites
- contract tests: covered by API contract suites
- Safety: covered by safety regression suites
