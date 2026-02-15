---
description: 按 tasks.md 执行实现，完成功能开发
---

# Implement Tasks

按 tasks.md 顺序执行实现任务。

## 执行步骤

1. 运行 `.specify/scripts/check-prerequisites.sh --require-tasks --include-tasks` 验证 plan.md 与 tasks.md 存在
2. 读取 `specs/[current-branch]/tasks.md`
3. 按顺序执行每个任务，更新代码
4. **每完成一个任务即 `git commit`** — 多 commit、粒度细，保证改动可溯源
5. 每个 User Story 完成后进行 checkpoint 验证
6. 遵循 `.specify/memory/constitution.md` 中的技术标准：
   - 编写单元测试
   - API 契约测试
   - 安全逻辑专项测试
7. 执行本地测试，修复运行时错误
8. 最终确认所有变更已 commit，无未提交的改动

## 输出

- 实现的代码变更
- 测试结果
- 未完成任务或遗留问题
