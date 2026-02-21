# Tasks: 冥想显化内容升级与专业化增强（021）

**Branch**: `021-meditation-manifestation-professionalization` | **From**: `specs/021-meditation-manifestation-professionalization/plan.md`

## Task Breakdown

### Phase 0: Spec Gate

- [x] **T0.1 / T-801** 新建 `specs/021-meditation-manifestation-professionalization/spec.md`，定义需求、边界与验收标准 - `specs/021-meditation-manifestation-professionalization/spec.md`
- [x] **T0.2 / T-801** 新建 `plan.md`，明确实施阶段、技术上下文与宪法门禁 - `specs/021-meditation-manifestation-professionalization/plan.md`
- [x] **T0.3 / T-801** 新建 `tasks.md`，映射 `T-802~T-809` 执行项与依赖 - `specs/021-meditation-manifestation-professionalization/tasks.md`

### Phase 1: Research & Content Intake

- [ ] **T1.1 / T-802** 产出冥想/显化资源调研清单（来源、授权、质量评分、接入建议） - `docs/content/meditation-manifestation-sources.md`
- [x] **T1.2 / T-803** 替换冥想播放列表并增加来源/版权元数据展示 - `frontend/user/src/config/meditationPlaylist.ts`, `frontend/user/src/pages/Tools/MeditationPlayer.tsx`
- [x] **T1.3 / T-804** 升级心灵空间信息架构与显化双层交互（快速/深度） - `frontend/user/src/pages/Mindfulness/*`

### Phase 2: Widget & Scale Professionalization

- [x] **T2.1 / T-805** 实现番茄钟轻量悬浮计时器（跨路由可见、可最小化） - `frontend/user/src/components/FloatingToolbar/*`, `frontend/user/src/stores/useToolStore.ts`
- [x] **T2.2 / T-806** 扩充权威量表定义与来源文献映射 - `backend/src/modules/assessment/*`, `frontend/user/src/pages/Scales/*`
- [ ] **T2.3 / T-807** 为 tests/scales 列表补充通俗用途说明区块（中英文） - `frontend/user/src/pages/Tests/*`, `frontend/user/src/pages/Scales/*`, `frontend/user/public/locales/*.json`

### Phase 3: Coach Expert Upgrade

- [x] **T3.1 / T-808** 增强 AI Coach 专业问答 Prompt Pack 与术语解释能力 - `backend/src/modules/prompt/*`, `backend/src/modules/coach/*`
- [x] **T3.2 / T-808** 增加专业问答样例集与边界守卫策略 - `backend/tests/*`, `docs/qa/*`

### Phase 4: Testing & Validation

- [x] **T4.1 / T-809** Unit tests：补齐前端状态/组件与后端服务单元覆盖
- [x] **T4.2 / T-809** contract tests：补齐 API contract 与关键路由 E2E 冒烟
- [x] **T4.3 / T-809** Safety：验证专业问答与内容升级不突破安全红线
- [x] **T4.4 / T-809** 执行 `scripts/constitution-check.sh` 与 `scripts/spec-status.sh` 并输出回归报告 - `docs/qa/t809-regression-report.md`

## Dependencies

- `T-803/T-804` 依赖 `T-802`
- `T-807` 依赖 `T-806`（保证说明文案与量表定义一致）
- `T-808` 与 `T-806/T-807` 可并行，但统一在 `T-809` 汇总验收
- 测试门禁任务依赖功能任务收敛后执行
