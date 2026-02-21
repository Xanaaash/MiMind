---
description: 自动推进开发（协作强化版）：主目录零开发 + 原子认领 + 强制 worktree + 漂移守卫 + 同步闸门
---

# Autodev（协作强化版）

目标：解决多 Agent 并行时最常见的五类问题。

1. 分支串线（开发中被切到别的分支）
2. 工作区污染（主目录遗留未提交改动）
3. 认领竞争（`todo.md` 被并发写入）
4. 外来改动闯入（当前任务外文件突然变脏）
5. 推送抢跑（`non-fast-forward` / rebase 阻塞）

---

## 唯一规则

1. **主目录只做编排，不做开发**  
   允许动作仅限：`preflight / claim / worktree / merge / todo状态更新 / cleanup`
2. **认领只能在 `main` + 干净工作区执行**
3. **开发只能在独立 worktree 执行**
4. **每个任务开工前必须通过 guard**
5. **一个 agent 同时只持有一个 `[🔒 <agent-id>]`**
6. **发现未知来源改动时，立即停手，不得混入当前任务提交**
7. **每次 push 前必须先同步远端（`pull --rebase`）**

---

## 标准流程（必须按顺序）

### 0) 预检（主目录）

```bash
bash scripts/autodev-preflight.sh --require-main --require-clean
git pull origin main --rebase
```

若预检失败（工作区不干净），执行下方「脏区决策树」。

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
bash ../../scripts/autodev-guard.sh --session ../../.autodev/sessions/<agent-id>-T-xxx.env
git fetch origin
git rebase origin/main
```

回主目录：

```bash
cd <repo-root>
bash scripts/autodev-preflight.sh --require-main --require-clean
git checkout main
git pull origin main --rebase
git merge agent/<agent-id>/T-xxx --no-ff -m "merge: T-xxx <简述> by <agent-id>"
```

将 `todo.md` 状态从 `[🔒 <agent-id>]` 改为 `[✅]` 后提交并推送：

```bash
git add todo.md
git commit -m "done: T-xxx <简述>"
git pull origin main --rebase
git push origin main
```

---

### 7) 清理

```bash
git worktree remove .worktrees/<agent-id>-T-xxx
git branch -d agent/<agent-id>/T-xxx
```

---

## 脏区决策树（必须执行）

当任一步骤提示 `Working tree is not clean`：

1. **先识别来源**
   - 当前任务相关且需要保留：`commit` 或 `stash`
   - 来源不明/非当前任务：**立即停止并通知负责人**
2. **禁止混提**
   - 不得把“当前任务改动 + 外来改动”放进同一 commit
3. **推荐优先级**
   - 优先 `commit`（可追溯）
   - 次选 `stash`（需命名）

标准 stash 命名：

```bash
git stash push -u -m "autodev-temp-<agent-id>-<task-id>-<yyyymmdd-HHMMSS>"
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

## 推送与同步闸门（新增）

为避免 `non-fast-forward`：

```bash
git pull origin main --rebase
git push origin main
```

若 push 失败且出现本地脏区：

1. 先执行 `git status --short` 定位文件  
2. 按「脏区决策树」处理  
3. 再执行 `pull --rebase` 与 `push`

---

## 外来改动处置协议（新增）

若主目录或 worktree 出现“你未触碰文件”的变更：

1. 立即停止当前实现动作
2. 输出变更文件列表（`git status --short`）
3. 请求人工决策：`stash / commit checkpoint / 放弃本轮`
4. 未获确认前不得继续合并或推送

---

## 输出模板

完成每个任务后输出：

1. 任务 ID 与标题
2. 改动文件
3. 关键实现说明（1-3 句）
4. 测试结果
5. 下一个建议任务
