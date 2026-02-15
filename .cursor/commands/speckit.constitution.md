---
description: 创建或更新项目宪法，确保治理原则与模板同步
---

# Constitution Update

你正在更新项目宪法文件 `.specify/memory/constitution.md`。

## 用户输入

```
$ARGUMENTS
```

如有用户输入，必须优先考虑。

## 执行步骤

1. 读取现有 `.specify/memory/constitution.md`
2. 根据用户输入或项目上下文，更新治理原则
3. 确保每条原则清晰、可执行，使用 MUST/MUST NOT 等明确措辞
4. 更新版本号：MAJOR=原则不兼容变更，MINOR=新增原则，PATCH=措辞澄清
5. 更新 LAST_AMENDED_DATE 为当前日期
6. 将结果写回 `.specify/memory/constitution.md`

## 输出

- 更新后的宪法内容
- 版本变更说明
- 建议的 commit message
