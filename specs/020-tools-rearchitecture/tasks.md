# Tasks: 疗愈工具体系重构（020）

**Branch**: `020-tools-rearchitecture` | **From**: `specs/020-tools-rearchitecture/plan.md`

## Task Breakdown

### Phase 0: Spec Gate

- [x] **T0.1** 建立 `specs/020-tools-rearchitecture/spec.md`（目标、场景、FR、SC） - `specs/020-tools-rearchitecture/spec.md`
- [x] **T0.2** 建立实现计划 `plan.md` 并完成宪法门禁自检 - `specs/020-tools-rearchitecture/plan.md`
- [x] **T0.3** 生成任务清单 `tasks.md`，映射 `T-701~T-717` - `specs/020-tools-rearchitecture/tasks.md`

### Phase 1: P0 Foundation (Batch A+B)

- [x] **T1.1 / T-701** 新建 `useToolStore` 并固化状态契约字段 - `frontend/user/src/stores/useToolStore.ts`
- [x] **T1.2 / T-704** 抽象全局音频服务并接入 store，保障跨路由播放不中断 - `frontend/user/src/utils/ambientAudioService.ts`
- [x] **T1.3 / T-702** 实现右侧 `FloatingToolbar`（迷你番茄钟 + 混音器） - `frontend/user/src/components/FloatingToolbar/FloatingToolbar.tsx`
- [x] **T1.4 / T-703** 将工具栏挂载到 `AppLayout` 常驻层 - `frontend/user/src/components/Layout/AppLayout.tsx`

### Phase 2: P0 Relief Hub (Batch C)

- [x] **T2.1 / T-705** 新建急救舱 `/relief` 路由与入口导航 - `frontend/user/src/pages/Relief/ReliefHub.tsx`, `frontend/user/src/router.tsx`
- [x] **T2.2 / T-706** 迁移呼吸与感官急救页面到 Relief 模块 - `frontend/user/src/pages/Relief/BreathingExercise.tsx`, `frontend/user/src/pages/Relief/SensoryRelief.tsx`
- [x] **T2.3 / T-707** 完成低刺激快速启动 UX（1 次点击启动） - `frontend/user/src/pages/Relief/*`

### Phase 3: P1 Mindfulness (Batch D)

- [x] **T3.1 / T-711** 新建心灵空间 `/mindfulness` 信息架构入口 - `frontend/user/src/pages/Mindfulness/MindfulnessHub.tsx`, `frontend/user/src/router.tsx`
- [x] **T3.2 / T-712** 冥想播放列表改为前端可配置资源 - `frontend/user/src/pages/Tools/MeditationPlayer.tsx`, `frontend/user/public/audio/meditation/*`
- [x] **T3.3 / T-713** 冥想播放器沉浸式背景升级 - `frontend/user/src/pages/Tools/MeditationPlayer.tsx`
- [x] **T3.4 / T-714** 实现 Manifestation v1（肯定语 + 愿景卡片） - `frontend/user/src/pages/Mindfulness/*`

### Phase 4: P1 Closure (Batch E)

- [ ] **T4.1 / T-715** 删除旧 `ToolsHub.tsx` 及无效引用，完成 `/tools` 路由收口 - `frontend/user/src/pages/Tools/ToolsHub.tsx`, `frontend/user/src/router.tsx`
- [ ] **T4.2 / T-716** 补齐 `zh-CN` 与 `en-US` 新键（`nav.rescue/nav.mindfulness/tools.rescue.*` 等） - `frontend/user/public/locales/zh-CN.json`, `frontend/user/public/locales/en-US.json`
- [ ] **T4.3 / T-717** 前端回归验收（路由切换音频连续、工具栏状态持久、关键路由冒烟） - `frontend/user/src/__tests__/*`, `frontend/user/e2e/*`

### Phase 5: Testing & Validation

- [x] **T5.1** Unit tests：补充 `useToolStore`、`ambientAudio`、`ambientAudioService`、`FloatingToolbar` 的单元/组件覆盖
- [ ] **T5.2** contract tests：补充或确认关键路由/API contract 冒烟覆盖（必要时扩展 Playwright / HTTP contract）
- [ ] **T5.3** Safety：验证急救路径与非医疗文案边界，确保不存在诊断化输出
- [ ] **T5.4** 执行 `scripts/constitution-check.sh` 与 `scripts/spec-status.sh`，确认 spec 与红线门禁通过

## Dependencies

- `T-702/T-703` 依赖 `T-701/T-704`
- `T-706/T-707` 依赖 `T-705`
- `T-712/T-713/T-714` 依赖 `T-711`
- `T-717` 依赖 `T-715/T-716`
- 测试与门禁任务依赖全部功能任务收敛
