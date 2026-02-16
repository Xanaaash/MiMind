# Feature Specification: Prompt Registry And Rollback Controls

**Feature Branch**: `[010-prompt-registry-rollout]`
**Created**: 2026-02-16
**Status**: In Progress (Prototype)
**Input**: docs/model-integration-next-step-v1.md + specs/009-provider-routing-coach

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Versioned Prompt Packs (Priority: P0)

As an operator, I can manage versioned prompt packs (system/style) and query active version.

**Why this priority**: Prompt changes are high-risk and must be auditable + reversible.

**Independent Test**: Query prompt packs and verify active version metadata is returned.

**Acceptance Scenarios**:

1. **Given** prompt pack catalog request, **When** API responds, **Then** available versions and compatibility metadata are returned.
2. **Given** coach session start, **When** prompt stack is built, **Then** active prompt pack version is included.

---

### User Story 2 - Runtime Rollback (Priority: P0)

As an operator, I can activate a previous prompt version to rollback safely.

**Why this priority**: Rapid rollback is mandatory for safety and quality incidents.

**Independent Test**: Activate an older version and verify subsequent prompt reads use that version.

**Acceptance Scenarios**:

1. **Given** valid version id, **When** activate endpoint is called, **Then** active version updates.
2. **Given** invalid version id, **When** activate endpoint is called, **Then** request fails with clear validation error.

### Edge Cases

- Environment default points to unknown version.
- Unsupported style id in a selected pack.
- Rollback during active traffic (must be atomic at service level).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST define prompt pack registry with versioned `system` and `styles` assets.
- **FR-002**: System MUST provide active-version query and pack listing interfaces.
- **FR-003**: System MUST support runtime activation (rollback) to any registered prompt version.
- **FR-004**: Existing `get_system_prompt` and `get_style_prompt` calls MUST resolve through active registry version.
- **FR-005**: Coach session start response MUST expose active prompt pack version.
- **FR-006**: System MUST include unit + contract tests for prompt registry and rollback behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Prompt registry unit tests cover list/get/activate/error paths.
- **SC-002**: Coach and prompt API contract tests pass after registry integration.
- **SC-003**: Full regression suite remains green.

## Clarifications

- This phase uses in-memory active-version state (process-local) for prototype speed.
- Persistent rollout targeting (percentage/segment) is deferred.
