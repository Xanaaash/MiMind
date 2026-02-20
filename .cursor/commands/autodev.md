---
description: 自动推进开发（v2）：宪法对齐 + 原子认领 + worktree 隔离 + 自动整合 main
---

# Autodev - 多 Agent 稳定并行工作流（v2）

目标：在多 Agent 并发下，避免分支串线、脏工作区污染、任务重复认领。

## 用户输入（可选）

```text
$ARGUMENTS
```

可指定任务 ID（如 `T-101`）；为空则认领 `todo.md` 中第一个 `[ ]`。

---

## 强制规则（必须满足）

1. `todo.md` 是唯一任务来源。
2. 认领动作只能在 `main` 且干净工作区执行。
3. 开发动作必须在独立 `worktree` 执行，禁止在共享根目录来回切分支。
4. 每个 Agent 同时仅持有 1 个 `[🔒 <agent-id>]` 任务。
5. 不得改动 `constitution.md`、`roadmap.md`（除非任务明确要求）。

---

## 0) 预检（每轮必做）

```bash
bash scripts/autodev-preflight.sh --require-main --require-clean
git pull origin main --rebase
```

若失败，先修复本地状态再继续。

---

## 1) 阅读上下文

- `.specify/memory/constitution.md`
- `roadmap.md`
- `todo.md`

---

## 2) 原子认领任务（在 main）

1. 选择任务：
   - 若指定了 `$ARGUMENTS` 且是 `T-xxx`，优先认领该任务
   - 否则认领 `todo.md` 第一个 `[ ]`
2. 将目标行从 `[ ]` 改为 `[🔒 <agent-id>]`
   - 推荐 `<agent-id>`：`平台-MMDD-序号`，如 `codex-0220a`
3. 立即提交并推送：

```bash
git add todo.md
git commit -m "claim: T-xxx by <agent-id>"
git push origin main
```

4. 若 push 失败（被抢占）：

```bash
git pull origin main --rebase
```

重新检查目标任务是否仍为 `[ ]`；若已被认领，改认领下一项。

---

## 3) 创建隔离工作区（worktree）

认领成功后，创建隔离分支与目录：

```bash
bash scripts/autodev-worktree.sh --agent-id <agent-id> --task-id T-xxx
```

输出示例：
- branch: `agent/<agent-id>/T-xxx`
- worktree: `.worktrees/<agent-id>-T-xxx`

进入该目录开发：

```bash
cd .worktrees/<agent-id>-T-xxx
git branch --show-current
```

---

## 4) 在 worktree 开发

开发规范：

- 遵守宪法红线与安全机制
- 每完成一个子步骤就 commit（细粒度）
- commit 格式：`type(scope): description`
- 后端改动后运行 `scripts/run-backend-tests.sh`
- 前端改动后运行 `npm run build`（`frontend/user/`）

---

## 5) 完成后整合回 main

在 worktree 分支：

```bash
git fetch origin
git rebase origin/main
```

冲突处理原则：保留双方有效改动，不删除他人已完成功能。

然后回到仓库根目录：

```bash
cd <repo-root>
git checkout main
git pull origin main --rebase
git merge agent/<agent-id>/T-xxx --no-ff -m "merge: T-xxx <简述> by <agent-id>"
```

标记任务完成：

```bash
# todo.md: [🔒 <agent-id>] -> [✅]
git add todo.md
git commit -m "done: T-xxx by <agent-id>"
git push origin main
```

若 push 失败：`git pull origin main --rebase` 后解决冲突再 push。

---

## 6) 清理

```bash
git worktree remove .worktrees/<agent-id>-T-xxx
git branch -d agent/<agent-id>/T-xxx
```

回到步骤 0 继续下一项。

---

## 故障恢复（v2 新增）

### A. 发现“分支漂移”（跑到别的任务分支）

```bash
git branch --show-current
bash scripts/autodev-preflight.sh --expect-branch agent/<agent-id>/T-xxx
```

若校验失败，立刻停止编码，切回正确分支或 worktree 后再继续。

### B. 共享根目录出现脏改动

不要继续认领新任务。先将改动归位到对应任务分支/worktree，再执行预检。

### C. 多 Agent 同时改 `todo.md` 冲突

仅合并状态标记，不删除任何任务行。

---

## 配套脚本（v2）

- `scripts/autodev-preflight.sh`：预检分支、工作区、上游状态、todo 摘要
- `scripts/autodev-worktree.sh`：为单任务创建隔离 worktree（避免串线）

---

## 输出模板（每任务完成后）

1. 任务 ID 与标题
2. 改动文件列表（新增/修改）
3. 关键实现说明（1-3 句）
4. 测试验证结果（构建/测试）
5. 下一个建议认领任务 ID
