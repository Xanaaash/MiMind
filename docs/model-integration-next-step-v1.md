# Model Integration Next Step (v1)

## Purpose

Build the next architecture layer after 001-007 by introducing production-grade model adapters while keeping constitution safety boundaries immutable.

## Current Baseline

- Prototype backend APIs and business flows are implemented.
- Safety dual-layer pipeline and crisis policy are implemented.
- Clinical scales + interactive tests are implemented with deterministic scoring.
- AI coach prompt stack and session flow are implemented.

## Design Upgrades (Next)

### 1) Model Gateway Layer

Create a dedicated `ModelGateway` abstraction to decouple product logic from providers.

- Input: `task_type`, locale, risk context, user tier, timeout budget.
- Output: normalized response schema with latency, confidence, and provider trace id.
- Failure mode: fail-closed for safety tasks.

Suggested module target:
- `backend/src/modules/model_gateway/`

### 2) Provider Routing Policy

Use policy-based routing by task criticality:

- `safety_nlu_fast`: small bilingual classifier model, strict p95 latency guard.
- `safety_semantic_judge`: stronger reasoning model, high recall priority.
- `coach_generation`: high quality dialog model, style-conditioned prompting.
- `memory_embedding`: bilingual embedding model for cross-session retrieval.
- `memory_rerank`: cross-encoder reranker for top-k context precision.

### 3) Data and Memory Reliability

Replace in-memory session/test/assessment persistence with relational storage + vector index.

- Relational DB: users, assessments, test_results, coach_sessions, safety_events, billing_events.
- Vector index: session summaries, journal summaries, preference snippets.

### 4) Safety Evaluation Harness

Add offline evaluation sets and online canary metrics:

- High-risk recall, false-negative rate, interruption correctness.
- Prompt redline compliance rate.
- Latency SLO: NLU <100ms p95, semantic judge <2s p95.

### 5) Prompt Governance Registry

Version prompts as immutable assets:

- `system`, `style`, `context` each with semantic version.
- Rollout by percentage and user segment.
- One-click rollback to previous prompt pack.

## Recommended Models To Integrate Next (Priority Order)

| Priority | Model Role | Recommended Capability | Why Now | Integration Target | Acceptance Gate |
|---|---|---|---|---|---|
| P0 | Safety Fast Classifier | Lightweight bilingual text classification model | Needed for stable <100ms risk pre-filter in production | `modules/safety/nlu` | p95 latency <100ms, high-risk miss rate near 0 |
| P0 | Safety Semantic Judge | High-recall reasoning LLM with strict safety prompt | Critical to reduce false negatives in crisis paths | `modules/safety/semantic` + `modules/safety/policy` | High-risk recall >= 99% on eval set |
| P0 | Coach Generation LLM | High-quality bilingual conversational model with long context | Core product value and session quality | `modules/coach` + `modules/prompt/*` | Session quality rubric + redline compliance |
| P1 | Embedding Model | Bilingual embedding model (short + long text robust) | Needed for cross-session memory relevance | `modules/memory` | Retrieval hit-rate/precision uplift vs baseline |
| P1 | Reranker Model | Cross-encoder reranker | Reduces irrelevant memory injection before generation | `modules/memory` | Top-k precision improvement and lower hallucination risk |
| P2 | Voice Stack (ASR/TTS) | High-accuracy multilingual ASR and natural TTS | Enables voice-first coaching and accessibility | new `modules/voice` | WER threshold + safety transcription parity |

## Rollout Plan (Execution-Ready)

### Phase A - Safety-First Modelization (1 sprint)

- Introduce `ModelGateway` interface and provider adapter stubs.
- Migrate `safety/nlu` and `safety/semantic` to gateway-based invocation.
- Add evaluation dataset runner and CI safety gate.

### Phase B - Coach + Memory Upgrade (1-2 sprints)

- Connect coach generation to gateway routing.
- Introduce embedding indexing and reranker in context assembly.
- Add prompt versioning and A/B canary controls.

### Phase C - Persistence + Observability (1 sprint)

- Move core entities from `InMemoryStore` to relational storage.
- Add model call audit logs and per-feature cost dashboards.

## Non-Negotiable Constitution Constraints

- Never output clinical diagnosis language.
- Never suggest medication/prescription.
- Halt normal coaching on high-risk detection.
- Ignore joke disclaimers for safety response routing.
- Keep hotline fallback available even when model calls fail.

## Deliverable For Next Spec

Create `008-model-gateway-and-evals` with scope:

1. Gateway interface + provider adapters.
2. Safety model routing and eval harness.
3. Prompt registry and rollback.
4. Basic persistence migration for safety/model audit events.

## Implemented Feature Matrix (As Of 2026-02-16)

| Domain | Implemented Scope | Key API / Module |
|---|---|---|
| Onboarding + Consent | Registration, consent capture, policy version persistence, assessment submission | `/api/register`, `/api/assessment/{user_id}` |
| Clinical Scales | PHQ-9, GAD-7, PSS-10, C-SSRS, SCL-90 scoring and catalog | `/api/scales/catalog`, `/api/scales/score` |
| Triage + Entitlements | Green/yellow/red routing, AI access guard for non-green | `modules/triage`, `modules/entitlement` |
| Interactive Tests | MBTI, 16P, Big5, Attachment, Love Language, Stress Coping, EQ, Inner Child, Boundary, Psych Age | `/api/tests/catalog`, `/api/tests/catalog/{test_id}`, `/api/tests/{user_id}/submit` |
| Reports + Growth Hooks | Subscription paywall report, share card, friend pairing | `/api/tests/{user_id}/report/{result_id}`, `/api/tests/{user_id}/share/{result_id}`, `/api/tests/pairing` |
| AI Coach Core | 3-layer prompt stack, style module, start/chat/end session flow, summary and memory adapter | `/api/coach/{user_id}/start`, `/api/coach/{session_id}/chat`, `/api/coach/{session_id}/end` |
| Healing Tools | Audio library, breathing completion, meditation library/start, mood journal + trend | `/api/tools/audio/*`, `/api/tools/breathing/*`, `/api/tools/meditation/*`, `/api/tools/journal/*` |
| Billing | Plans, trial, checkout, webhook idempotency, quota consume/reset, entitlement checks | `/api/billing/*` |
| Safety + Crisis | Dual-layer risk detection, 4-level policy, hotline cache fallback, ops alert hooks | `/api/safety/{user_id}/assess`, `/api/safety/hotline-cache` |
| Quality Gates | Unit, contract, safety, benchmark suites with full pass | `scripts/run-backend-tests.sh` (70 tests passing) |
