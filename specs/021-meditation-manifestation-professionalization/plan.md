# Implementation Plan: 冥想显化内容升级与专业化增强（021）

**Branch**: `021-meditation-manifestation-professionalization` | **Date**: 2026-02-21 | **Spec**: `specs/021-meditation-manifestation-professionalization/spec.md`  
**Input**: Feature specification from `specs/021-meditation-manifestation-professionalization/spec.md`

## Summary

围绕“内容成熟度 + 专业可信度”推进五条主线：外部资源调研与授权筛选、冥想显化内容升级、番茄钟轻量悬浮交互、权威量表扩展与用途解释、AI Coach 专业问答增强，并以统一回归门禁收敛。

## Technical Context

**Language/Version**: TypeScript 5.x, React 19.x, Python 3.11  
**Primary Dependencies**: React Router, Zustand, Vitest, Playwright, FastAPI  
**Storage**: Browser `localStorage` + existing backend storage  
**Testing**: Vitest, Playwright, backend unittest/contract, constitution gate scripts  
**Target Platform**: Web (desktop + mobile)  
**Project Type**: Full-stack feature extension with frontend-first delivery  
**Constraints**:
- 内容接入必须满足“可商用或授权明确”
- 不可突破非医疗边界和安全机制
- 多 Agent 并行下按任务原子提交，避免大范围冲突

## Constitution Check

*GATE: Must pass before implementation. Align with `.specify/memory/constitution.md`*

- [x] Product boundary: Non-medical, no diagnosis language
- [x] Safety redlines: No medication/prescription guidance
- [x] Safety mechanism: Keep existing crisis intercept and hotline behavior
- [x] Technical standards: Ensure Unit tests + contract tests + Safety regression tasks

## Project Structure

```text
specs/021-meditation-manifestation-professionalization/
├── spec.md
├── plan.md
└── tasks.md

docs/content/
└── meditation-manifestation-sources.md

frontend/user/src/
├── config/meditationPlaylist.ts
├── pages/Mindfulness/*
├── components/FloatingToolbar/*
├── pages/Scales/*
├── pages/Tests/*
└── __tests__/*

backend/src/modules/
├── assessment/*
└── prompt/*
```

## Implementation Phases

1. **Phase A - Spec & Research Gate（T-801, T-802）**  
   完成规格文档与资源调研清单，明确版权许可与接入策略。

2. **Phase B - Mindfulness Content Upgrade（T-803, T-804）**  
   升级冥想播放列表与显化/冥想信息架构，补齐沉浸式体验与来源展示。

3. **Phase C - Mini Pomodoro Widget（T-805）**  
   在右侧工具栏附近增加轻量悬浮计时器，确保跨路由可见与低占用。

4. **Phase D - Professional Scale & Explanation（T-806, T-807）**  
   扩充权威量表，并在测试/量表页面增加通俗用途说明模块。

5. **Phase E - Expert Coach Upgrade & Regression（T-808, T-809）**  
   完成专业问答增强与全链路验收，输出统一回归报告。
