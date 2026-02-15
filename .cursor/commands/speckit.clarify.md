---
description: 澄清功能规格中的歧义与未定义项
---

# Clarify Specification

对当前功能的 spec.md 进行澄清，识别并填充 underspecified 区域。

## 执行步骤

1. 读取 `specs/[current-branch]/spec.md`（根据当前分支或 SPECIFY_FEATURE 确定）
2. 识别标记为 [NEEDS CLARIFICATION] 或模糊的需求
3. 提出澄清问题或基于合理假设补充
4. 将澄清结果写入 spec.md 的 **Clarifications** 部分
5. 更新受影响的需求描述

## 输出

- 澄清问题列表及解答
- 更新后的 spec.md 相关章节
