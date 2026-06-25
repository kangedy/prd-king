# 贡献指南

欢迎贡献！这个项目的目标是成为中文互联网最好用的PRD标准。

## 如何贡献

### 提交 Issue
- 报告模板BUG、遗漏的场景
- 建议增加新的设计体系
- 分享使用案例
- 原型工作流改进建议

### 提交 Pull Request
1. Fork 本仓库
2. 创建特性分支: `git checkout -b feat/my-improvement`
3. 提交改动
4. 发起 PR

## 目录规范

```
prd-king/
├── SKILL.md               ← Hermes Agent技能主文件
├── templates/             ← PRD模板（写需求）
│   ├── commercial-prd-template.md
│   └── ai-prototype-prd-template.md
├── prototype/             ← 原型工作流（做原型）
│   ├── WORKFLOW.md        ← 主工作流文档
│   ├── references/        ← 设计体系Token参考
│   └── scripts/           ← 自动化脚本
└── references/            ← 公共参考
    └── design-system-options.md
```

## 代码规范

- `SKILL.md` 修改后需跑一遍自查清单
- `prototype/` 新增文件需在 `WORKFLOW.md` 更新Phase说明
- 新增设计体系需包含：主色/框架/组件数/Token CSS块/场景说明
- 新增模板版本需在 README 的「10章结构速览」中更新入口
- `scripts/verify-prototype.py` 修改后需用 Python3 验证无语法错误

## 发布流程

版本号格式：v{大版本}.{小版本}.{修订}
- 大版本：10章结构变更 / 原型流程重构
- 小版本：新增设计体系/模板/工作流Phase
- 修订：内容修正/优化

## 行为准则

- 保持专业和友善
- PRD质量优先
- 所有枚举值必须列全，不用「多种」「各类」模糊词
- 原型验收 ≥90% 才允许交付
