---
description: 自动推进开发：读取 roadmap 与宪法 → 自动选取下一项任务 → 实现并合并 main
---

# Autodev - 多 Agent 自动推进工作流

执行自动推进开发流程：支持多 Agent（Cursor / Codex / Gemini 等）并行认领任务、独立开发、自动整合。

## 用户输入（可选）

```
$ARGUMENTS
```

用户可指定要推进的功能名称或任务 ID（如 `T-101`）；若为空，由 Agent 自主认领。

---

## 核心执行流程

### 0. 同步最新 — 每次操作前必做

```bash
git checkout main
git pull origin main --rebase
```

若 pull 失败（冲突），先解决冲突后再继续。

### 1. 阅读上下文

- 读取 `.specify/memory/constitution.md` — 安全红线与技术标准
- 读取 `roadmap.md` — 产品需求与优先级
- 读取 `todo.md` — 唯一任务来源

### 2. 认领任务（原子操作）

从 `todo.md` 中找到第一个 `[ ]`（未认领）的任务，优先选择 P0 批次：

1. 再次 `git pull origin main --rebase`（确保看到最新认领状态）
2. 将目标任务的 `[ ]` 改为 `[🔒 <agent-id>]`
   - `<agent-id>` 格式：`平台-时间戳` 如 `cursor-0220a`、`codex-0220b`、`gemini-0220c`
3. **立即 commit + push 完成认领**：
   ```bash
   git add todo.md
   git commit -m "claim: T-xxx by <agent-id>"
   git push origin main
   ```
4. **若 push 失败**（其他 Agent 先推了）：
   ```bash
   git pull origin main --rebase
   ```
   - 检查目标任务是否仍为 `[ ]`
   - 若已被他人认领 → 放弃，重新选择下一个 `[ ]` 任务
   - 若仍可用 → 重新标记并 push

> **关键原则**：认领靠 push 竞争。push 成功 = 认领成功。失败 = 被抢，换一个。

### 3. 创建特性分支并开发

```bash
git checkout -b agent/<agent-id>/T-xxx
```

**开发规范**：

- 遵守 `.specify/memory/constitution.md` 中的全部红线
- 每完成一个子步骤即 commit（细粒度 commit）
- Commit 格式：`类型(范围): 描述`（如 `feat(auth): 添加 JWT 登录 API`）
- 安全相关变更须有对应测试
- 前端改动后执行 `npm run build`（在 `frontend/user/` 下）确认构建通过
- 后端改动后执行 `scripts/run-backend-tests.sh` 确认测试通过

### 4. 完成 → 整合 → 合并

开发完成后执行以下步骤（顺序不可乱）：

```bash
# 4a. 切回 main 并拉取最新
git checkout main
git pull origin main --rebase

# 4b. 将特性分支 rebase 到最新 main
git checkout agent/<agent-id>/T-xxx
git rebase main

# 4c. 若 rebase 有冲突 → 解决冲突
#   原则：保留双方改动，不删除他人代码
#   若无法自动判断 → 保守策略：保留两边，人工后续处理

# 4d. 合并回 main
git checkout main
git merge agent/<agent-id>/T-xxx --no-ff -m "merge: T-xxx <简述> by <agent-id>"

# 4e. 标记任务完成
#   在 todo.md 中将 [🔒 <agent-id>] 改为 [✅]
git add -A
git commit -m "done: T-xxx by <agent-id>"

# 4f. 推送
git push origin main
```

**若 push 失败（他人已推新提交）**：

```bash
git pull origin main --rebase
# 解决冲突（保留双方）后再次 push
git push origin main
```

### 5. 清理 & 继续

```bash
git branch -d agent/<agent-id>/T-xxx
```

回到 **步骤 0**，继续认领下一个任务。循环直到 `todo.md` 中无 `[ ]` 任务。

---

## 冲突解决策略

多 Agent 并行时**必然**产生冲突。遵循以下原则：

### 文件级策略

| 文件 | 策略 |
|------|------|
| `todo.md` | 合并双方认领/完成标记，不删除任何行 |
| 同一文件不同区域 | Git 自动合并 |
| 同一文件同一区域 | 保留双方代码，用注释标注后提交，交人工审查 |
| 新增文件（不冲突） | 直接接受 |

### 代码整合原则

- **不删除**他人已完成的功能代码
- **不覆盖**他人对 `todo.md` 的状态标记
- 若两个 Agent 修改了同一组件的不同部分 → 合并保留
- 若两个 Agent 对同一逻辑有不同实现 → 保留先合并者的版本，后者适配

---

## 各平台适配指南

### Cursor Agent

- 直接使用 `/autodev` 指令触发
- Agent ID 格式：`cursor-MMDD-序号`（如 `cursor-0220a`）
- 可在 IDE 终端直接执行所有 git 命令

### Codex

- 在 codex 会话中粘贴本工作流或引用本文件
- Agent ID 格式：`codex-MMDD-序号`
- 注意：codex 的 sandbox 需配置 git push 权限
- 建议每次只认领 1 个任务，完成后再触发下一轮

### Gemini / Claude / 其他

- 将本文件内容作为 system prompt 或首条消息
- Agent ID 格式：`<平台名>-MMDD-序号`
- 若平台不支持直接 git push，则输出所有代码改动 + git 命令序列，由人工执行 push

---

## 约束

- 所有实现必须遵守 `.specify/memory/constitution.md` 中的红线与技术标准
- 安全相关任务（含 `T-304`、涉及安全检测的改动）须通过 `scripts/constitution-check.sh`
- `todo.md` 是唯一任务来源 — 不存在于 `todo.md` 中的工作不要做
- 不要修改 `roadmap.md`、`constitution.md`、其他 Agent 已完成的功能代码（除非修 bug）
- 每个 Agent 同时只持有 **1 个** 认领中的任务

## 输出

完成每个任务后，Agent 应输出：

1. **任务 ID 与标题**
2. **改动文件列表**（新增/修改）
3. **关键实现说明**（1-3 句）
4. **测试验证结果**（构建是否通过、测试是否通过）
5. **下一个建议认领的任务 ID**
