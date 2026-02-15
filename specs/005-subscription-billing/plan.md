# Implementation Plan: Subscription And Billing

**Branch**: `[005-subscription-billing]` | **Date**: 2026-02-15 | **Spec**: `/specs/005-subscription-billing/spec.md`
**Input**: Feature specification from `/specs/005-subscription-billing/spec.md`

## Summary

Implement billing engine, entitlement service, trial lifecycle, and quota enforcement with payment webhook reliability.

## Technical Context

**Language/Version**: TypeScript 5.x
**Primary Dependencies**: Payment provider SDK (TBD), scheduler, entitlement cache
**Storage**: PostgreSQL
**Testing**: unit + contract + safety tests
**Target Platform**: Web backend
**Project Type**: web
**Constraints**: Coach plan usable only for green-channel users

## Constitution Check

- [ ] Product boundary: Billing copy avoids medical claims
- [ ] Safety redlines: Access controls enforce non-green restrictions
- [ ] Safety mechanism: Entitlement checks integrated before AI use
- [ ] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/005-subscription-billing/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/billing/
backend/src/modules/entitlement/
```

## Implementation Phases

1. Product and plan model
2. Payment + webhook + trial lifecycle
3. Entitlement and quota validation
