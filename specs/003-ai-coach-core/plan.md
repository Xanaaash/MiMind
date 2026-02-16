# Implementation Plan: AI Coach Core

**Branch**: `[003-ai-coach-core]` | **Date**: 2026-02-15 | **Spec**: `/specs/003-ai-coach-core/spec.md`
**Input**: Feature specification from `/specs/003-ai-coach-core/spec.md`

## Summary

Deliver MVP coaching engine with layered prompts, style modules, session lifecycle, and memory integration.

## Technical Context

**Language/Version**: TypeScript 5.x + LLM provider SDK
**Primary Dependencies**: Prompt builder, vector store adapter, moderation gateway
**Storage**: PostgreSQL + vector database
**Testing**: unit + contract + safety + prompt regression tests
**Target Platform**: Web backend
**Project Type**: web
**Constraints**: Must integrate with feature 006 safety system

## Constitution Check

- [x] Product boundary: Coaching language only, no diagnosis/treatment
- [x] Safety redlines: Forbidden advice and promises blocked
- [x] Safety mechanism: Every turn goes through risk detection gateway
- [x] Technical standards: Unit/API/Safety tests included

## Project Structure

```
specs/003-ai-coach-core/
├── spec.md
├── plan.md
└── tasks.md

backend/src/modules/coach/
backend/src/modules/prompt/
backend/src/modules/memory/
```

## Implementation Phases

1. Prompt stack and style modules
2. Session orchestration and summaries
3. Memory retrieval and safety integration
