# MiMind - Agent 指引

## 关于本项目

MiMind 是专业心理教练平台，非医疗产品。面向无/轻度心理困扰用户，提供量表、测试、疗愈工具及 AI 心理教练服务。支持中英文。

## Spec Kit 工作流

本项目使用 Spec-Driven Development，核心命令：

| 命令 | 用途 |
|------|------|
| `/speckit.constitution` | 创建/更新项目宪法 |
| `/speckit.specify` | 创建功能规格与分支 |
| `/speckit.clarify` | 澄清需求歧义 |
| `/speckit.plan` | 生成技术实现计划 |
| `/speckit.tasks` | 拆解可执行任务 |
| `/speckit.implement` | 执行实现 |
| `/autodev` | 自动推进：读宪法 → 确定下一项 → 新分支实现 → 直接 merge main |

## 关键文件

- **宪法**: `.specify/memory/constitution.md` — 治理原则、红线、安全机制、技术标准
- **产品路线图**: `roadmap.md` — MVP 优先级与阶段规划（P0/P1/Phase2+）
- **功能规格**: `specs/00x-feature-name/spec.md`
- **实现计划**: `specs/00x-feature-name/plan.md`
- **任务列表**: `specs/00x-feature-name/tasks.md`

## Git 分支策略

- `main`: 稳定主分支
- `00x-feature-name`: 功能分支（001、002、003...）
- 完成实现后**直接 merge 到 main**，不创建 PR
- 所有新开发在 feature 分支上进行

## 脚本

- `.specify/scripts/create-new-feature.sh` — 创建新功能分支与 spec
- `.specify/scripts/check-prerequisites.sh` — 检查 plan、tasks 等是否就绪
- `.specify/scripts/setup-plan.sh` — 初始化 plan.md
- `scripts/init-roadmap-tasks.sh` — 按 roadmap 初始化 001~006 的 spec/plan/tasks
- `scripts/spec-status.sh` — 查看 specs 完整度状态（spec/plan/tasks）
- `scripts/constitution-check.sh` — 宪法红线与任务测试门禁检查
- `scripts/dev-setup.sh` — 使用 uv 初始化本地开发环境（依赖 + 工具）
- `scripts/run-backend-tests.sh` — 运行后端全量测试（支持 uv run）
- `scripts/run-api.sh` — 启动 FastAPI 原型服务入口

## 环境变量

- `SPECIFY_FEATURE`: 指定当前功能目录（如 `001-user-registration-assessment`），在非 Git 或特殊场景使用

## Git 提交

- **每完成一个任务即 git commit** — 多 commit、粒度细，保证改动可溯源
- 不使用笼统的 commit message，需说明具体改动
