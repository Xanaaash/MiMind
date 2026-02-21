# Feature Specification: 疗愈工具体系重构（急救舱 + 心灵空间 + 全局伴随工具栏）

**Feature Branch**: `020-tools-rearchitecture`  
**Created**: 2026-02-21  
**Status**: Draft  
**Input**: User description: "将工具能力重组为急救舱、心灵空间与跨路由常驻工具栏，并完成旧工具页收口与回归验收"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 跨页面不中断的伴随工具体验 (Priority: P1)

用户在任意页面都可以打开右侧工具栏，启动番茄钟或环境音后继续浏览其他页面，不需要重新配置或重启播放。

**Why this priority**: 这是重构的核心价值，直接决定工具是否从单页功能升级为全局陪伴能力。

**Independent Test**: 启动一条环境音后在 `/home -> /coach -> /relief` 切换，验证声音状态与工具栏状态保持。

**Acceptance Scenarios**:

1. **Given** 用户在 `/home` 打开工具栏并开启环境音，**When** 切换到 `/coach`，**Then** 环境音持续播放且工具栏状态保持。
2. **Given** 用户在任意页面设置番茄钟，**When** 页面切换，**Then** 倒计时继续且完成次数正常累计。

---

### User Story 2 - 急救舱 1 次点击可启动 (Priority: P1)

用户进入急救舱后，应在最少认知负担下立即获得可执行的平复动作（呼吸或感官急救）。

**Why this priority**: 急救场景强调时效与低负担，交互复杂会直接降低安全可用性。

**Independent Test**: 打开 `/relief`，首屏点击一次即可触发呼吸流程或粉红噪音播放。

**Acceptance Scenarios**:

1. **Given** 用户进入 `/relief`，**When** 点击主入口按钮，**Then** 系统立即进入呼吸或感官急救流程。
2. **Given** 用户处于过载状态，**When** 选择低刺激入口，**Then** 页面提供低刺激视觉和快速噪音启动能力。

---

### User Story 3 - 心灵空间与旧路由收口 (Priority: P2)

用户通过 `/mindfulness` 访问冥想与显化能力，旧 `/tools` 路由逐步收口，不影响过渡期可达性和多语言文案完整性。

**Why this priority**: 这是重构收尾阶段，关系到信息架构一致性和后续维护成本。

**Independent Test**: 校验 `/mindfulness` 功能可达，旧 `/tools` 过渡可用，i18n 新键无缺失，关键冒烟回归通过。

**Acceptance Scenarios**:

1. **Given** 用户访问 `/mindfulness`，**When** 切换播放列表与模块，**Then** 内容与文案完整可用。
2. **Given** 系统处于收口阶段，**When** 访问 `/tools`，**Then** 页面行为符合过渡策略且不会出现死链。

### Edge Cases

- 当用户在无活动音轨时设置定时器，系统应仅更新状态，不触发播放引擎计时器。
- 当最后一个音轨被关闭时，系统应清理 `timer` 与 `startedAt`，避免残留状态。
- 当语言切换时，新增导航键与工具键不得出现 missing key。
- 当移动端屏幕较小且键盘弹出时，工具栏不应遮挡关键交互入口。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 提供全局常驻右侧工具栏，支持番茄钟与环境音混音能力。
- **FR-002**: 系统 MUST 使用统一 `useToolStore` 管理番茄钟、环境音和工具栏 UI 状态。
- **FR-003**: 系统 MUST 保证环境音在路由切换时不中断，除非用户主动停止。
- **FR-004**: 系统 MUST 提供急救舱路由 `/relief`，并支持 1 次点击启动急救动作。
- **FR-005**: 系统 MUST 提供心灵空间路由 `/mindfulness`，承接冥想与显化能力。
- **FR-006**: 系统 MUST 支持可配置冥想播放列表与沉浸式播放背景。
- **FR-007**: 系统 MUST 在过渡期处理 `/tools` 路由收口并避免无效引用。
- **FR-008**: 系统 MUST 为新增导航与模块补齐 `zh-CN`/`en-US` 文案键值。
- **FR-009**: 系统 MUST 提供回归验证，覆盖跨页面音频、工具栏状态持久化与关键路由可达性。
- **FR-010**: 系统 MUST 保持非医疗边界，不新增任何诊断/药物建议相关能力。

### Key Entities *(include if feature involves data)*

- **ToolStoreState**: 全局工具状态，包含 `pomodoro`、`ambient`、`ui` 三个子域。
- **AmbientPlaybackSession**: 当前环境音播放上下文，包含活动音轨、音量、定时器、启动时间。
- **ToolRouteMap**: 工具域路由映射（`/relief`、`/mindfulness`、`/tools` 过渡入口）。
- **ToolI18nKeys**: 工具重构新增文案键集合，用于多语言完整性校验。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 用户在至少 3 次路由切换后，环境音持续播放成功率达到 100%（回归用例通过）。
- **SC-002**: 右侧工具栏开合状态在跨页面场景保持一致（对应测试全部通过）。
- **SC-003**: `/relief` 首屏 1 次点击启动急救动作成功率达到 100%（冒烟回归通过）。
- **SC-004**: `zh-CN` 与 `en-US` 对新增 `tools.*` 与 `nav.*` 键无 missing key。
- **SC-005**: `vitest` 与关键路由冒烟回归通过，且无宪法红线违规项。

## Clarifications

- `/tools` 在 1 个迭代内保留兼容入口，完成 `T-715` 后再移除或重定向到新信息架构。
- 本特性不引入后端新接口，音频播放列表先由前端配置管理。
