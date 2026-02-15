---
description: 根据需求描述创建功能规格，创建新分支与 spec 文件
---

# Create Feature Specification

根据用户描述创建功能规格并初始化功能分支。

## 用户输入

```
$ARGUMENTS
```

## 执行步骤

1. 运行 `.specify/scripts/create-new-feature.sh` 并传入用户描述，或根据描述手动：
   - 确定下一个可用的功能编号（001, 002, ...）
   - 创建 Git 分支 `00x-feature-name`
   - 在 `specs/00x-feature-name/` 创建 `spec.md`
2. 根据用户描述填充 spec.md，使用 `.specify/templates/spec-template.md` 结构
3. 确保 User Stories、Functional Requirements、Success Criteria 完整
4. 遵守 `.specify/memory/constitution.md` 中的所有原则

## 输出

- 新分支名称
- spec.md 路径
- 规格概要
