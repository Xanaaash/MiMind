# Scale And Test Design (Initial Development)

## 1. Clinical Scale Matrix

| Scale | Purpose | MVP State | Re-test Cadence | Notes |
|---|---|---|---|---|
| PHQ-9 | Depression screening | Implemented | 30 days | Core triage input |
| GAD-7 | Anxiety screening | Implemented | 30 days | Core triage input |
| PSS-10 | Stress perception | Implemented | 30 days | Context enrichment |
| C-SSRS (Screener) | Self-harm/suicide risk | Implemented | trigger / 30 days | Any positive -> red |
| SCL-90-R (initial) | Broad symptom screening | Initial engine in this phase | 90 days | Used as yellow risk modifier |

## 2. Interactive Test Matrix

### 2.1 Implemented before this phase

- MBTI
- 16Personalities-style profile
- Big Five (OCEAN)
- Attachment style
- Love language

### 2.2 Added in this phase (initial scoring)

- Stress coping style
- Emotional intelligence (EQ)
- Inner child profile
- Interpersonal boundary profile
- Psychological age

## 3. Scoring Strategy

Initial stage scoring follows deterministic rule-based methods:

- Numeric normalization and category aggregation
- Primary trait/profile extraction
- Non-diagnostic interpretation only

This keeps behavior auditable and constitution-aligned.

## 4. Safety Constraints For Test Reports

- Reports must avoid diagnosis language
- Reports must avoid medication suggestions
- Reports are reflective/growth-oriented and non-clinical

## 5. Next Step

- Add psychometric validation datasets and score reliability checks
- Add submission mode that aggregates question-level answers into scoring dimensions
- Introduce migration/backup tooling for SQLite to managed Postgres in production
