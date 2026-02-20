# Implementation Plan: 神经多样性与认知特质探索模块

## 技术上下文

### 现有架构（复用点）

| 组件 | 路径 | 复用方式 |
|------|------|----------|
| 量表定义注册 | `backend/src/modules/assessment/catalog/registry.py` | 新增 `ExplorationScaleDefinition`，与 `ClinicalScaleDefinition` 并行 |
| 量表 ID 常量 | `backend/src/modules/assessment/catalog/scales.py` | 新增 ASRS/AQ10/HSP/CATQ 常量 |
| 计分服务 | `backend/src/modules/assessment/scoring_service.py` | 扩展计分分支 |
| 题库 | `backend/src/modules/assessment/catalog/question_bank.py` | 新增题目 JSON |
| Context Builder | `backend/src/modules/prompt/context/builder.py` | 注入神经多样性评估结果 |
| 咨询风格 | `backend/src/modules/prompt/styles/registry.py` | 新增谱系适配风格 |
| Web Audio 引擎 | `frontend/user/src/utils/ambientAudio.ts` | 复用噪音生成，新增粉红/棕色噪音 |
| 分享卡片 | `frontend/user/src/utils/shareCard.ts` | 扩展"大脑说明书"模板 |
| i18n | `frontend/user/public/locales/{zh-CN,en-US}.json` | 新增命名空间 `neuro.*` |

### 新增架构

```
backend/src/modules/assessment/
├── catalog/
│   ├── scales.py              # += ASRS, AQ10, HSP, CATQ 常量
│   ├── registry.py            # += ExplorationScaleDefinition
│   ├── question_bank.py       # += 四套量表题目
│   └── neurodiversity/        # 新增
│       ├── __init__.py
│       ├── asrs_scoring.py    # ASRS v1.1 计分逻辑
│       ├── aq10_scoring.py    # AQ-10 计分逻辑
│       ├── hsp_scoring.py     # HSP 计分逻辑
│       └── catq_scoring.py    # CAT-Q 计分逻辑
├── models.py                  # += NeurodiversityScoreSet
└── scoring_service.py         # += 调用 neurodiversity scorers

backend/src/modules/prompt/
├── context/
│   └── builder.py             # += neurodiversity_scores 字段
└── styles/
    └── neurodiversity.py      # 新增：ADHD/ASD/HSP 适配 prompt 片段

frontend/user/src/
├── pages/Tests/
│   ├── NeuroExplorer.tsx       # 新增：探索测试入口（量表选择卡片）
│   └── NeuroResult.tsx         # 新增：探索测试结果页（雷达/柱状图）
├── components/
│   ├── Disclaimer/
│   │   └── NeuroDisclaimer.tsx # 新增：免责声明弹窗/提示条
│   └── Charts/
│       ├── RadarChart.tsx      # 新增：雷达图组件（Recharts）
│       └── BarChart.tsx        # 新增：柱状图组件（Recharts）
├── pages/Tools/
│   ├── SensoryRelief.tsx       # 新增：感官急救包
│   └── FocusTimer.tsx          # 新增：番茄钟
└── utils/
    └── ambientAudio.ts         # += buildPinkNoise, buildBrownNoise
```

---

## 实现阶段

### Phase 1: 后端量表基础（T-601 ~ T-604 后端部分）

**目标**: 四套量表的数据定义、题库、计分逻辑、API 端点

1. **scales.py 扩展**
   - 新增常量: `ASRS = "asrs"`, `AQ10 = "aq10"`, `HSP = "hsp"`, `CATQ = "catq"`
   - 新增 `EXPLORATION_SCALES = [ASRS, AQ10, HSP, CATQ]`
   - 关键: 这些量表 **不进入** `MANDATORY_SCALES` 或 `SUPPORTED_CLINICAL_SCALES`

2. **registry.py 扩展**
   - 新增 `ExplorationScaleDefinition` dataclass
   - 与 `ClinicalScaleDefinition` 区分: 无 `required_for_triage` 字段，新增 `category: str = "neurodiversity"`
   - 注册 ASRS/AQ10/HSP/CATQ 定义

3. **neurodiversity/ 计分模块**
   - 每个量表独立文件，函数签名: `def score(responses: List[int]) -> dict`
   - ASRS: Part A 6 题筛查 + Part B 12 题完整，返回 `{screener_positive: bool, total_score: int, dimensions: {inattention: int, hyperactivity: int}}`
   - AQ-10: 10 题，返回 `{total_score: int, high_trait: bool, dimensions: {detail_focus, social_intuition, systematic_thinking, sensory_load}}`
   - HSP: 27 题 Likert 7，返回 `{mean_score: float, high_sensitivity: bool, dimensions: {depth_processing, overstimulation, emotional_reactivity, subtle_awareness}}`
   - CAT-Q: 25 题 Likert 7，返回 `{total_score: int, dimensions: {compensation, masking, assimilation}}`

4. **models.py 扩展**
   - `NeurodiversityScoreSet` dataclass

5. **API 端点**
   - `POST /api/assessment/exploration/{scale_id}/submit` — 提交答案 + 返回计分结果
   - `GET /api/assessment/exploration/{scale_id}/questions` — 获取题目列表
   - `GET /api/assessment/exploration/results/{user_id}` — 获取用户所有探索测试结果

### Phase 2: 前端量表 UI（T-601 ~ T-604 前端部分）

**目标**: 答题界面 + 结果可视化

1. **NeuroExplorer.tsx** — 探索测试入口
   - 四张卡片：注意力模式、社交风格、高敏感、社交面具
   - 每张卡片显示预估时长、核心维度、免责声明入口

2. **答题组件** — 复用现有量表答题 UI，适配 Likert 5/7 级
   - 进度条 + 当前题号
   - 提交后 loading + 结果页跳转

3. **NeuroResult.tsx** — 结果可视化
   - Recharts RadarChart（雷达图）— ASRS 注意力/冲动两维度，CAT-Q 三维度
   - Recharts BarChart（柱状图）— AQ-10 四维度，HSP 四维度
   - 下方：个性化文字解读 + 策略建议
   - 底部：免责声明提示条

4. **路由注册** — `/tests/explore` 入口，`/tests/explore/:scaleId/result` 结果页

### Phase 3: 合规层（T-611, T-612）

1. **NeuroDisclaimer.tsx**
   - 弹窗模式（测试前）: 勾选确认 → 才能开始答题
   - 提示条模式（报告页）: 固定在报告顶部，不可关闭
   - 中英双语，读取 i18n key

2. **AI 教练开场插入**
   - 当 `context.neurodiversity_scores` 存在时，系统 prompt 自动附加免责声明段落

### Phase 4: AI 教练适配（T-621 ~ T-624）

1. **neurodiversity.py prompt 片段**
   ```python
   ADHD_HIGH_CONTEXT = """
   用户表现出较高的 ADHD 特质。请：
   - 使用简短分块的信息
   - 偏向行动教练风格，提供具体执行步骤
   - 在给出建议前先肯定用户的努力
   - 注意识别拒绝敏感性（RSD）
   """
   ```

2. **context/builder.py 扩展**
   - `build_context_prompt` 返回新增 `neurodiversity_scores` 字段
   - 当分数达到阈值时附加对应 prompt 片段

3. **分流逻辑补丁**
   - 明确：神经多样性高分 → 不改变通道颜色
   - 但如果同时 PHQ-9/GAD-7 达中度以上 → AI 主动建议进行情绪量表

### Phase 5: 疗愈工具（T-631, T-632）

1. **ambientAudio.ts 扩展**
   - `buildPinkNoise()`: 对白噪音施加 -3dB/octave 滤波
   - `buildBrownNoise()`: 对白噪音施加 -6dB/octave 滤波
   - 新增到 `AMBIENT_SOUNDS` 数组

2. **SensoryRelief.tsx**
   - 暗色背景 + 极简 UI
   - 噪音选择（粉红/棕色/白）
   - 暗色呼吸动画（复用 BreathingExercise 核心逻辑，暗色主题变体）
   - 渐进式恢复引导（分步文字提示 + 定时器）

3. **FocusTimer.tsx**
   - 环形进度条计时器
   - 可设置专注时长（默认 25 分钟）和休息时长（默认 5 分钟）
   - 任务拆解输入框：用户输入大任务 → 自动分 3-5 个小步骤
   - 完成后微奖励动画（confetti + 正向文案）

### Phase 6: 社交裂变（T-641, T-642）

1. **shareCard.ts 扩展**
   - 「你的大脑说明书」模板
   - 风格标签映射：ADHD 高→"猎人型大脑"，ASD 高→"系统化思维者"，HSP 高→"感知放大器"
   - Canvas 绘制：特质可视化图 + 标签 + MiMind logo

2. **平台尺寸适配**
   - 小红书 3:4 (1080×1440)
   - Instagram 1:1 (1080×1080)
   - TikTok 9:16 (1080×1920)

### Phase 7: 国际化（T-651, T-652）

1. 所有量表题目双语 JSON
2. 报告文案、建议文案双语
3. 免责声明双语（标记法律审核占位符 `[LEGAL_REVIEW_PENDING]`）

---

## Constitution Check

| 宪法原则 | 合规措施 |
|----------|----------|
| 不做临床诊断 | 所有量表结果使用"特质探索"话语，三处强制免责声明 |
| 安全红线 | 谱系高分不触发危机通道，仅当并发 PHQ-9/GAD-7/C-SSRS 达阈值时由原有逻辑处理 |
| 分流逻辑 | 神经多样性评估独立于四级响应体系，不改变通道颜色 |
| 数据合规 | 评估结果加密存储，遵循现有隐私政策 |
| 技术标准 | 计分逻辑须有单元测试覆盖，API 须有契约测试 |

✅ Constitution Check 通过
