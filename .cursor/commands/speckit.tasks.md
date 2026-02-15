---
description: 将实现计划拆解为可执行任务
---

# Generate Tasks

将 plan.md 拆解为可执行任务列表。

## 执行步骤

1. 读取 `specs/[current-branch]/plan.md` 及相关实现细节
2. 按 User Story 或实现阶段拆分任务
3. 为每个任务指定：
   - 描述
   - 目标文件路径
   - 依赖关系
   - 可并行标记 [P]（如适用）
4. 写入 `specs/[current-branch]/tasks.md`
5. 确保任务顺序尊重依赖（如 model → service → endpoint）

## 输出

- tasks.md 完整内容
- 任务依赖关系说明
