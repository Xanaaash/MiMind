---
description: 自动推进开发（强约束版）：原子认领 + 强制 worktree + 漂移守卫 + 自动整合 main
---

# Autodev（强约束版）

目标：解决多 Agent 并行时最常见的三类问题。

1. 分支串线（开发中被切到别的分支）
2. 工作区污染（主目录遗留未提交改动）
3. 认领竞争（`todo.md` 被并发写入）

---

## 唯一规则

1. **认领只能在 `main` + 干净工作区执行**
2. **开发只能在独立 worktree 执行**
3. **每个任务开工前必须通过 guard**
4. **一个 agent 同时只持有一个 `[🔒 <agent-id>]`**

---

## 标准流程（必须按顺序）

### 0) 预检（主目录）

```bash
bash scripts/autodev-preflight.sh --require-main --require-clean
git pull origin main --rebase
```

---

### 1) 阅读上下文

- `.specify/memory/constitution.md`
- `roadmap.md`
- `todo.md`

---

### 2) 原子认领（主目录）

推荐命令：

```bash
bash scripts/autodev-claim.sh --agent-id <agent-id> --task-id T-xxx
```

不传 `--task-id` 时，会自动认领 `todo.md` 第一个 `[ ]`。

---

### 3) 创建隔离 worktree（主目录）

```bash
bash scripts/autodev-worktree.sh --agent-id <agent-id> --task-id T-xxx
```

该步骤会创建：

- 分支：`agent/<agent-id>/T-xxx`
- 目录：`.worktrees/<agent-id>-T-xxx`
- 会话文件：`.autodev/sessions/<agent-id>-T-xxx.env`

---

### 4) 进入 worktree 开发（禁止在主目录开发）

```bash
cd .worktrees/<agent-id>-T-xxx
bash ../../scripts/autodev-guard.sh --session ../../.autodev/sessions/<agent-id>-T-xxx.env
```

在每次以下动作前都跑一次 guard：

- 大规模编辑前
- 提交前
- rebase 前
- 合并回 main 前

---

### 5) 开发与验证

- 遵守宪法红线
- 子步骤级 commit（细粒度）
- 后端改动执行：`scripts/run-backend-tests.sh`
- 前端改动执行：`npm run build`（`frontend/user/`）

---

### 6) 整合回 main

在 worktree 分支：

```bash
git fetch origin
git rebase origin/main
```

回主目录：

```bash
cd <repo-root>
git checkout main
git pull origin main --rebase
git merge agent/<agent-id>/T-xxx --no-ff -m "merge: T-xxx <简述> by <agent-id>"
```

将 `todo.md` 状态从 `[🔒 <agent-id>]` 改为 `[✅]` 后提交并推送。

---

### 7) 清理

```bash
git worktree remove .worktrees/<agent-id>-T-xxx
git branch -d agent/<agent-id>/T-xxx
```

---

## 漂移处理（重点）

如果你看到自己突然在别的分支：

```bash
bash scripts/autodev-guard.sh --session .autodev/sessions/<agent-id>-T-xxx.env
```

- 通过：继续
- 失败：**立即停止编辑**，切回对应 worktree 再继续

---

## 输出模板

完成每个任务后输出：

1. 任务 ID 与标题
2. 改动文件
3. 关键实现说明（1-3 句）
4. 测试结果
5. 下一个建议任务
