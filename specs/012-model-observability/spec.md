# Feature Specification: Model Invocation Observability

**Feature Branch**: `[012-model-observability]`
**Created**: 2026-02-16
**Status**: In Progress (Prototype)
**Input**: specs/008-model-gateway-and-evals + specs/009-provider-routing-coach

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persist Model Invocation Audit Records (Priority: P0)

As an operator, I need traceable records for every model gateway invocation (success and failure).

**Why this priority**: Required for safety auditability, troubleshooting, and cost control.

**Independent Test**: Trigger coach and safety model calls and verify invocation records are stored.

**Acceptance Scenarios**:

1. **Given** successful gateway call, **When** invocation completes, **Then** trace id, provider, latency, and cost estimate are persisted.
2. **Given** failed gateway call, **When** invocation errors, **Then** failure record is still persisted with error reason.

---

### User Story 2 - Query Observability Data (Priority: P0)

As an operator, I can query recent model invocation records via API.

**Why this priority**: Needed for day-to-day monitoring without direct store access.

**Independent Test**: Call observability API and validate records schema and filter behavior.

**Acceptance Scenarios**:

1. **Given** invocation history exists, **When** listing API is called, **Then** records return in newest-first order.
2. **Given** filters are provided, **When** listing API is called, **Then** only matching task/provider records are returned.

### Edge Cases

- Invocation fails before provider returns response.
- Unsupported task type errors.
- Empty observability store response.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Model gateway MUST persist invocation records for both success and failure outcomes.
- **FR-002**: Invocation record MUST include `trace_id`, `task_type`, `provider`, `latency_ms`, `success`, `estimated_cost_usd`, and timestamp.
- **FR-003**: System MUST provide observability API to list invocation records with limit and optional filters.
- **FR-004**: Safety runtime and coach runtime MUST instantiate gateway with shared store-backed auditing enabled.
- **FR-005**: System MUST include unit and contract tests for observability behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Unit tests validate success/failure record persistence from gateway.
- **SC-002**: Contract tests validate observability endpoint schema and filtering.
- **SC-003**: Full regression suite remains green.

## Clarifications

- Cost values are estimated for monitoring and not billing-grade.
- This phase stores records in in-memory prototype store.
