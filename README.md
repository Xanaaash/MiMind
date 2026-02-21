# MiMind

专业心理教练平台。面向希望更好了解自己的你，提供量表测评、互动测试、疗愈工具与 AI 心理教练对话服务。

**这不是医疗产品**，不做诊断和治疗。我们陪伴你探索内心，支持日常情绪调节与自我成长。

---

## 你可以做什么

- **量表测评** — 抑郁、焦虑、压力、风险筛查等专业量表，帮助了解当前状态
- **互动测试** — MBTI、依恋类型、爱情语言、EQ 等，认识自己的性格与模式
- **疗愈工具** — 正念冥想、呼吸练习、情绪日记、白噪音，随时为自己按下暂停键
- **AI 心理教练** — 基于专业咨询流派的 AI 对话，支持中英文（需完成测评并符合使用条件）

---

## 收费说明

- **免费**：量表填写、测试参与、有限试听
- **基础订阅**：量表报告、疗愈工具、测试结果（所有用户可订阅）
- **教练订阅**：基础全部 + AI 咨询（符合绿色通道的用户）
- 新用户可享 7 天免费体验基础订阅

---

## 安全与隐私

我们重视你的安全与隐私。平台设有风险检测与分级响应机制，必要时会提供专业求助资源。你的数据将加密存储，仅用于为你提供服务。

---

*MiMind — 陪伴你更好地了解自己*

---

## 开发工作流（Spec Kit + Roadmap）

- `roadmap.md` 定义产品优先级（P0/P1/Phase2+）
- 初始化任务骨架：`scripts/init-roadmap-tasks.sh`
- 查看功能文档完整度：`scripts/spec-status.sh`
- 运行治理门禁检查：`scripts/constitution-check.sh`
- 运行后端测试（001 原型）：`scripts/run-backend-tests.sh`

## 本地开发环境

- 依赖管理：`uv + pyproject.toml`
- 一键初始化：`scripts/dev-setup.sh`
- 执行数据库迁移：`scripts/run-db-migrations.sh`
- 启动 API 服务：`scripts/run-api.sh`（默认 `http://127.0.0.1:8000`）
- 常用命令：
  - `uv run pytest`
  - `uv run ruff check .`
  - `uv run mypy`
  - `scripts/run-db-migrations.sh`
  - `scripts/run-backend-tests.sh`

## Docker（T-401）

- 构建镜像：`docker build -t mimind:latest .`
- 运行容器：`docker run --rm -p 8080:8080 mimind:latest`
- 访问地址：
  - 前端（Nginx 静态服务）：`http://127.0.0.1:8080`
  - 后端健康检查（经 Nginx 反代）：`http://127.0.0.1:8080/healthz`

## Docker Compose（T-402）

- 一键启动：`docker compose up -d --build`
- 查看状态：`docker compose ps`
- 停止并清理：`docker compose down`
- 服务说明：
  - `app`：运行 `FastAPI + Nginx`（前端静态托管 + `/api` 反代）
  - `db`：PostgreSQL 16（为后续数据库迁移任务预留）
- 生产部署细节：见 `docs/deployment.md`

## 环境变量（T-404）

- 示例文件：`.env.example`
- 使用方式：`cp .env.example .env` 后按环境修改
- 生产环境至少应配置：
  - `ADMIN_PASSWORD`
  - `AUTH_JWT_SECRET`
  - `MIMIND_DATA_ENCRYPTION_KEY`
- 当模型 provider 使用 `openai` 时，还需配置：
  - `OPENAI_API_KEY`
- 音频资源托管可选配置：
  - `MEDIA_ASSET_BASE_URL`（默认 `/audio`，可替换为 CDN / 对象存储前缀）
