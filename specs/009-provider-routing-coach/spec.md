# Feature Specification: Provider Routing And Coach Gateway Integration

**Feature Branch**: `[009-provider-routing-coach]`
**Created**: 2026-02-16
**Status**: In Progress (Prototype)
**Input**: specs/008-model-gateway-and-evals + docs/model-integration-next-step-v1.md

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Coach Generation Through Model Gateway (Priority: P0)

As a platform engineer, coach responses should be generated through `ModelGateway` instead of direct hard-coded logic.

**Why this priority**: Aligns core value path (coach dialog) with provider abstraction introduced in 008.

**Independent Test**: Start a coaching session and verify chat path returns normal coaching response while safety behavior remains unchanged.

**Acceptance Scenarios**:

1. **Given** low-risk user input, **When** chat runs, **Then** reply is produced via gateway task `coach_generation`.
2. **Given** medium/high risk, **When** safety path triggers, **Then** existing pause/stop behavior remains unchanged.

---

### User Story 2 - Configurable Provider Routing (Priority: P1)

As an operator, I can switch provider selection by task type using env configuration with safe local fallback.

**Why this priority**: Enables phased rollout of external model providers without blocking local reliability.

**Independent Test**: Instantiate gateway with default config and verify tasks route to local providers; verify unsupported provider config fails clearly.

**Acceptance Scenarios**:

1. **Given** default env config, **When** gateway starts, **Then** safety and coach tasks route to local providers.
2. **Given** external provider selected without credentials, **When** coach task runs, **Then** explicit error is returned and caller can fallback.

### Edge Cases

- Unknown provider id in env config.
- External provider timeout/network failure.
- Missing prompt metadata for coach generation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Gateway MUST support `coach_generation` task type.
- **FR-002**: Gateway MUST support provider routing config per task with local fallback defaults.
- **FR-003**: Coach session service MUST call gateway for low-risk reply generation.
- **FR-004**: Coach service MUST keep constitutional safety interception unchanged.
- **FR-005**: System MUST include unit tests for provider routing and coach gateway path.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Existing coach contract and safety tests pass unchanged.
- **SC-002**: New routing tests cover local default and external-config error path.
- **SC-003**: Full regression suite remains green.

## Clarifications

- External provider integration in this phase is adapter-level and optional-by-env.
- This phase does not yet introduce prompt A/B rollout or persistence for model traces.
