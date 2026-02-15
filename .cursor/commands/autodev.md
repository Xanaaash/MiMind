---
description: 自动推进开发：阅读宪法 → 确定下一项工作 → 新分支实现 → 直接 merge 回 main
---

# Autodev - 自动推进工作流

执行自动推进开发流程：阅读宪法、确定下一个待完成功能、在新分支上实现、直接 merge 回 main（无 PR）。

## 用户输入（可选）

```
$ARGUMENTS
```

用户可指定要推进的功能名称或编号；若为空，由 Agent 根据项目状态自主判断。

## 执行流程

### 1. 阅读宪法与项目状态

- 读取 `.specify/memory/constitution.md` 全部内容
- 列出 `specs/` 下所有功能目录及状态（是否有 spec.md、plan.md、tasks.md、是否已实现）
- 读取计划中的功能拆分建议：
  - 001-user-registration-assessment
  - 002-interactive-tests
  - 003-ai-coach-core
  - 004-healing-tools
  - 005-subscription-billing
  - 006-safety-nlu-crisis

### 2. 确定下一项工作

- 按编号顺序，找出首个「有 spec 但未完成实现」或「无 spec 需新建」的功能
- 若用户输入了具体功能，则按用户指定执行
- 输出：下一项工作 = `00x-feature-name`

### 3. 切换到新分支并落实

- 若当前不在 main，先 `git checkout main` 并 `git pull`（如有）
- 若该功能尚无分支/目录：运行 `.specify/scripts/create-new-feature.sh "功能描述"` 或手动创建
- 若已有分支：`git checkout 00x-feature-name`
- 按 Spec Kit 流程执行：
  - 无 spec → 使用 `/speckit.specify` 创建
  - 无 plan → 使用 `/speckit.plan` 创建
  - 无 tasks → 使用 `/speckit.tasks` 创建
  - 执行 `/speckit.implement` 完成实现
- 本地验证通过后，**按任务粒度多次 commit**：每完成一个可独立计数的任务即 `git add` + `git commit`，保证改动可溯源

### 4. Merge 回 main（无 PR，直接合并）

- `git checkout main`
- `git merge 00x-feature-name` 或 `git cherry-pick <latest-commit>`（若更倾向 cherry-pick）
- 不创建 Pull Request，直接合并
- 推送 main：`git push origin main`

### 5. 后续开发

- 所有新开发均在新的 feature 分支上进行
- 完成一个功能 → 直接 merge 到 main → 再开下一个 feature 分支

## 约束

- 所有实现必须遵守 `.specify/memory/constitution.md` 中的红线与技术标准
- 安全相关功能（如 006-safety-nlu-crisis）须通过 Constitution Check
- 不提交 Pull Request，采用直接 merge 模式

## 输出

- 已选择的功能
- 分支与实现摘要
- Merge 结果
- 建议的下一项工作
