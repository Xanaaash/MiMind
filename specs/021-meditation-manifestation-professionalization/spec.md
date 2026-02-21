# Feature Specification: 冥想显化内容升级与专业化增强（021）

**Feature Branch**: `021-meditation-manifestation-professionalization`  
**Created**: 2026-02-21  
**Status**: Draft  
**Input**: User description: "通过网络资源升级冥想与显化内容、优化番茄钟可见性、扩展权威量表并提升 AI Coach 专业答疑能力"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 高质量冥想与显化体验 (Priority: P1)

用户进入心灵空间后可以使用质量更高、结构更成熟的冥想与显化内容，而不是低质量占位素材。

**Why this priority**: 当前内容质量直接影响留存和专业感，是本轮最核心问题。

**Independent Test**: 从 `/mindfulness` 进入冥想和显化流程，验证可播放资源与内容结构完整可用。

**Acceptance Scenarios**:

1. **Given** 用户打开冥想页，**When** 选择任意轨道，**Then** 音频可播放且展示来源/授权信息。
2. **Given** 用户打开显化页，**When** 选择快速练习或深度练习，**Then** 均可完整走通。

---

### User Story 2 - 番茄钟轻量悬浮可见 (Priority: P1)

用户开启番茄钟后，右侧工具栏附近出现不占空间的小计时交互，跨页面持续可见。

**Why this priority**: 需要兼顾“随时可见”与“不干扰页面阅读”，属于高频核心交互。

**Independent Test**: 开启番茄钟后在 `/home -> /coach -> /relief` 切换，验证悬浮计时器持续显示且倒计时准确。

**Acceptance Scenarios**:

1. **Given** 番茄钟运行中，**When** 用户切换路由，**Then** 悬浮计时器持续显示并更新时间。
2. **Given** 用户停止番茄钟，**When** 计时归零或手动停止，**Then** 悬浮计时器自动隐藏。

---

### User Story 3 - 量表专业化与 AI 专家答疑 (Priority: P2)

用户在量表/测试中心看到通俗用途说明，并可通过 AI Coach 获取学术范围内的专业解答。

**Why this priority**: 目标是提升专业信任和可解释性，同时保持安全分流与非医疗边界。

**Independent Test**: 新增权威量表可提交并产出解释；专业问答样例集回归通过且无红线违规。

**Acceptance Scenarios**:

1. **Given** 用户浏览测试或量表列表，**When** 阅读简介，**Then** 能用简单语言理解“用途/作用/适用场景”。
2. **Given** 用户在 Coach 提问心理学理论问题，**When** 系统回复，**Then** 回答专业且包含边界声明，不给诊断或药物建议。

### Edge Cases

- 网络资源许可不明时必须降级为“候选未纳入”，不得直接上线使用。
- 冥想音频不可访问时应展示可读错误并提供备用轨道。
- 番茄钟浮窗在移动端窄屏下不得遮挡底部主要导航与输入区。
- 专业问答遇到风险词时必须优先走安全响应，不得继续普通学术对话。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 建立冥想/显化外部资源清单，包含来源 URL、授权类型、用途建议、质量评分。
- **FR-002**: 系统 MUST 只接入可商用或许可明确的音频资源，并保留可追溯元数据。
- **FR-003**: 系统 MUST 升级冥想播放列表，提供更高质量音频与结构化信息（时长、主题、来源、版权）。
- **FR-004**: 系统 MUST 升级心灵空间信息架构，显化模块支持“快速开始 + 深度练习”双模式。
- **FR-005**: 系统 MUST 为番茄钟提供轻量悬浮计时器，跨路由可见且可最小化。
- **FR-006**: 系统 MUST 新增一批权威量表并记录文献来源、计分依据和适用边界。
- **FR-007**: 系统 MUST 在 tests/scales 页面加入简单语言用途说明，支持中英文。
- **FR-008**: 系统 MUST 提升 AI Coach 专业问答能力，支持学术解释、理论比较和术语答疑。
- **FR-009**: 系统 MUST 保持非医疗边界，禁止诊断、药物建议和处方相关输出。
- **FR-010**: 系统 MUST 提供统一回归验收报告，覆盖前端、E2E、安全与文案完整性。

### Key Entities *(include if feature involves data)*

- **ContentSourceRecord**: 外部内容来源记录（URL、license、provider、quality_score、status）。
- **MeditationTrackMeta**: 冥想轨道元数据（title、duration、theme、source_url、license_label）。
- **PomodoroMiniWidgetState**: 浮窗状态（visible、collapsed、remainingSec、anchorPosition）。
- **ScaleCatalogExtension**: 新增量表定义（来源文献、评分规则、免责声明）。
- **CoachExpertQAProfile**: 专业答疑配置（知识范围、回答模板、边界声明）。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 完成不少于 20 条外部资源调研记录，且每条具备授权字段。
- **SC-002**: 冥想播放列表不少于 12 条高质量轨道，可播放可切换，坏链率 0。
- **SC-003**: 番茄钟浮窗在跨页面场景持续可见并通过自动化回归。
- **SC-004**: 新增不少于 6 个权威量表定义，并至少 1 个具备完整提交流程验证。
- **SC-005**: AI Coach 20 条专业问答样例回归通过，红线违规率 0。
- **SC-006**: `vitest`、关键 `playwright`、`constitution-check`、`spec-status` 全部通过。

## Clarifications

- 内容资源优先选择可商用、版权清晰、可公开追溯来源；不可验证授权的资源仅做调研不接入。
- 专业问答增强仅在学术与心理教育范围内，不改变现有分流与安全机制。
