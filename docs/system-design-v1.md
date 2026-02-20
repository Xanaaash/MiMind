# MiMind System Design (V1)

## 1. Product Boundary

MiMind is a psychological coaching platform, not a medical diagnosis or treatment system.
All runtime outputs must comply with constitutional redlines:

- No diagnosis claims
- No medication/prescription advice
- No confidentiality guarantees
- No normal coaching continuation after high/extreme risk detection

## 2. Core Runtime Layers

### 2.1 Access and Triage Layer

- User registration and consent
- Clinical scale scoring and channel assignment
- Entitlement derivation from triage + subscription state

### 2.2 Coaching Layer

- Immutable `System` prompt (redline guard)
- Pluggable `Style` prompt (Warm Guide / Rational Analysis)
- Dynamic `Context` prompt (profile + scores + journal + memory)

### 2.3 Safety Layer

- Dual-layer detection:
  - Fast NLU classifier (`<100ms target`)
  - Semantic evaluator (`<2s target`)
- Four-level policy response (monitor / pause / crisis stop / emergency)
- Hotline fallback cache for client-side failover

### 2.4 Tools and Growth Layer

- Healing tools: audio, breathing, meditation, mood journal
- Interactive tests: personality and relationship exploration tests
- Share cards and pairing reports

### 2.5 Billing Layer

- Free / Base / Coach / Trial plans
- Webhook idempotency
- Monthly AI quota accounting and reset

## 3. Data Design (Prototype)

Current implementation uses in-memory storage for rapid iteration:

- `users`, `consents`
- `submissions`, `scores`, `triage_decisions`, `schedules`
- `test_results`, `coach_sessions`, `memory_summaries`
- `journal_entries`, `tool_events`
- `subscriptions`, `processed_webhooks`

Next iteration should migrate to PostgreSQL with audit trails for safety-critical operations.

## 4. API Surface (Current)

- Onboarding and assessment
- Tests, reports, share, pairing
- Coach session lifecycle
- Healing tools and journal
- Billing and entitlement
- Safety runtime assessment and hotline cache

Entry point: `backend/src/app.py`

## 5. Development Gates

Required before merge:

- `scripts/constitution-check.sh`
- `scripts/run-backend-tests.sh`
- CI governance workflow pass

## 6. Roadmap Alignment

Current implemented baseline covers `001` to `006` in prototype depth.
This iteration extends the clinical scale and interactive test foundation for wider catalog support.
