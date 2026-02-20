---
description: 根据功能规格生成技术实现计划
---

# Create Implementation Plan

根据 spec.md 生成技术实现计划。

## 用户输入（技术栈等）

```
$ARGUMENTS
```

## 执行步骤

1. 运行 `.specify/scripts/setup-plan.sh` 初始化 plan.md
2. 读取 `specs/[current-branch]/spec.md`
3. 根据用户输入的技术栈（或默认选择）填充：
   - `plan.md` - 实现计划概要、技术上下文、项目结构
   - `research.md` - 技术调研（如需要）
   - `data-model.md` - 数据模型
   - `contracts/` - API 契约（如适用）
4. 执行 **Constitution Check**：对照 `.specify/memory/constitution.md` 验证计划合规
5. 确保 MiMind 红线与安全机制在架构中体现

## 输出

- plan.md 完整内容
- 相关 research、data-model、contracts 文件
- Constitution Check 通过确认
