# Feature Specification: Observability Summary Metrics

**Feature Branch**: `[014-observability-summary]`
**Created**: 2026-02-16
**Status**: In Progress (Prototype)
**Input**: specs/012-model-observability

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Aggregated Model Health Metrics (Priority: P0)

As an operator, I need aggregated model invocation health metrics from recent records.

**Why this priority**: Raw traces are hard to scan quickly; ops needs a summary view.

**Independent Test**: Generate mixed success/failure calls and verify aggregate summary fields.

**Acceptance Scenarios**:

1. **Given** invocation records exist, **When** summary API is called, **Then** totals include success/failure counts, success_rate, avg/p95 latency, and estimated cost.
2. **Given** mixed tasks/providers, **When** summary API is called, **Then** grouped aggregates by task and provider are returned.

---

### User Story 2 - Filtered Summary Scope (Priority: P1)

As an operator, I can request summary over filtered task/provider slices.

**Why this priority**: Supports troubleshooting specific model paths quickly.

**Independent Test**: Filter by task_type and verify summary only reflects that slice.

**Acceptance Scenarios**:

1. **Given** task filter, **When** summary API is called, **Then** totals and groups reflect filtered records.
2. **Given** no records match filter, **When** summary API is called, **Then** summary returns zero-safe metrics.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Observability service MUST compute totals: `total`, `success`, `failure`, `success_rate`, `avg_latency_ms`, `p95_latency_ms`, `estimated_cost_usd`.
- **FR-002**: Observability service MUST compute grouped summaries by `task_type` and `provider`.
- **FR-003**: Observability API MUST expose `/api/observability/model-invocations/summary`.
- **FR-004**: Summary API MUST support `limit`, `task_type`, and `provider` filters.
- **FR-005**: Summary API MUST return zero-safe values when no records match.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Unit tests validate aggregate math, p95 calculation, and zero-safe behavior.
- **SC-002**: Contract tests validate API schema and filtering.
- **SC-003**: Full regression suite remains green.
