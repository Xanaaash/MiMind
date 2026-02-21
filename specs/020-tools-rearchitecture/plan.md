# Implementation Plan: 疗愈工具体系重构（020）

**Branch**: `020-tools-rearchitecture` | **Date**: 2026-02-21 | **Spec**: `specs/020-tools-rearchitecture/spec.md`  
**Input**: Feature specification from `specs/020-tools-rearchitecture/spec.md`

## Summary

将工具能力从单页入口重构为三层结构：全局伴随工具栏（状态层 + 播放层）、急救舱（低负担快速启动）、心灵空间（冥想与显化承接），并完成旧 `/tools` 收口与回归验收。

## Technical Context

**Language/Version**: TypeScript 5.x, React 19.x, Python 3.11  
**Primary Dependencies**: React Router, Zustand, Vitest, Playwright, FastAPI  
**Storage**: Browser `localStorage`（工具状态持久化）  
**Testing**: Vitest（store/components/utils）, Playwright（关键路由冒烟）, backend unittest（保持无回归）  
**Target Platform**: Web（Desktop + Mobile）  
**Project Type**: Frontend-heavy web feature with existing backend reuse  
**Constraints**:
- 必须保持非医疗产品边界，不新增诊断/药物建议能力
- 不新增后端 API，优先复用现有工具能力
- 多 Agent 并行开发下，变更应尽量原子且低冲突

## Constitution Check

*GATE: Must pass before implementation. Align with `.specify/memory/constitution.md`*

- [x] Product boundary: Non-medical, no diagnosis
- [x] Safety redlines: No forbidden statements
- [x] Safety mechanism: Existing crisis and hotline flow remains intact
- [x] Technical standards: Unit tests + contract tests + Safety regression requirements included

## Project Structure

```text
specs/020-tools-rearchitecture/
├── spec.md
├── plan.md
└── tasks.md

frontend/user/src/
├── stores/useToolStore.ts
├── utils/ambientAudio.ts
├── utils/ambientAudioService.ts
├── components/FloatingToolbar/FloatingToolbar.tsx
├── components/Layout/AppLayout.tsx
├── pages/Relief/*
├── pages/Mindfulness/*
├── pages/Tools/*
└── __tests__/*
```

## Implementation Phases

1. **Phase A - 状态层与播放层基础（T-701, T-704）**  
   建立 `useToolStore` 契约并将音频引擎能力抽象为服务层，保证跨路由不中断。

2. **Phase B - 全局 UI 挂载（T-702, T-703）**  
   实现 `FloatingToolbar` 并挂载到 `AppLayout` 的 `Outlet` 外层，形成伴随式交互。

3. **Phase C - 急救舱上线（T-705, T-706, T-707）**  
   新增 `/relief` 信息架构，完成呼吸/感官急救迁移与低刺激快速启动体验。

4. **Phase D - 心灵空间升级（T-711, T-712, T-713, T-714）**  
   新增 `/mindfulness` 入口，完成播放列表升级、沉浸式背景和显化工具。

5. **Phase E - 收口与验收（T-715, T-716, T-717）**  
   处理旧路由收口、多语言键值补齐，并通过前端回归验收标准。
