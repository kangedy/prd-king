# 📝 原型导向 PRD · 产品需求文档标准

**一套PRD标准，两种输出形态。从需求到高保真原型，一次写对。**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRD Chapters](https://img.shields.io/badge/PRD-10%20Chapters%20%7C%20P0%2FP1%2FP2-blueviolet)](SKILL.md)
[![Design System](https://img.shields.io/badge/Design-Ant%20Design%205.x%20%7C%20Element%20Plus%20%7C%20TDesign%20%7C%20Arco%20%7C%20Semi%20%7C%20NutUI-orange)](references/design-system-options.md)

---

## 🌟 这是什么

这是一个 **面向原型生成的PRD标准**——不同于市面上任何PRD模板，它的每一章都是可以直接翻译为HTML/CSS/JS的指令。由实战项目锤炼而成，已交付多个企业级系统PRD。

### 核心理念

> **PRD不是文档，是原型生成指令。** 每一条需求必须能直接翻译成DOM元素+交互逻辑+Mock数据。

### 与传统PRD的区别

| 维度 | 传统PRD | 本PRD标准 |
|------|--------|-----------|
| 定位 | 读给开发听的说明书 | 可直接生成原型的指令集 |
| 设计规范 | 通常不提或一笔带过 | Ant Design默认+6大国产体系可选，Token直接映射CSS |
| 颗粒度 | 功能模块级 | 按钮/弹窗/操作级 |
| 数据模型 | 有时有，有时没有 | P0硬依赖，逐字段含类型/校验/控件 |
| Mock数据 | 不要求 | 正常/空/极限三组 |
| 验收标准 | "开发自测" | 10条自动化门禁 |
| 输出 | 一份文档 | VERSION A(甲方交付) + VERSION B(AI原型) |

---

## 📂 目录结构

```
prd-skill/
├── SKILL.md                              ← Hermes Agent 技能主文件（10章标准）
├── templates/
│   ├── commercial-prd-template.md        ← VERSION A · 商用交付版（甲方/合同/开发排期）
│   └── ai-prototype-prd-template.md      ← VERSION B · AI原型生成版（直接出HTML原型）
├── references/
│   └── design-system-options.md          ← 8大设计体系Token完整参考
├── README.md                             ← 本文件
├── LICENSE                               ← MIT
├── CONTRIBUTING.md                       ← 贡献指南
└── CHANGELOG.md                          ← 版本记录
```

---

## 🚀 快速开始

### 如果你是产品经理（不需要Hermes）

直接打开模板开始写：

| 用途 | 打开 |
|------|------|
| 给甲方交付/合同附件 | `templates/commercial-prd-template.md` |
| 交给AI生成原型 | `templates/ai-prototype-prd-template.md` |

### 如果你是 Hermes Agent 用户

```bash
# 安装技能
mkdir -p ~/.hermes/skills/product/prd/ && cp -r * ~/.hermes/skills/product/prd/

# 使用
load skill_view(name='prd')
→ 说「帮我写个PRD」
→ 自动走 Phase 0c 结构化访谈 → 输出10章PRD
```

---

## 📐 10章结构速览

| 章 | 标题 | 优先级 | 一句话说明 |
|----|------|--------|-----------|
| Ch1 | 设计规范 | 🔴 P0 | Ant Design/Element Plus/TDesign... Token即CSS |
| Ch2 | 信息架构 | 🔴 P0 | 导航树 + 角色-菜单映射 |
| Ch3 | 业务流程 | 🟡 P1 | 页面间跳转，标注[从XX页→弹窗XX→到XX页] |
| Ch4 | 系统架构上下文 | 🟢 P2 | 只写影响原型设计的部分（权限/数据流向） |
| Ch5 | 页面清单 | 🔴 P0 | 每页有唯一 data-page + 布局类型 |
| Ch6 | 功能点清单 | 🔴 P0 | 逐按钮/逐操作，操作类型+触发方式+结果 |
| Ch7 | 数据模型 | 🔴 P0 | 逐字段含类型/必填/选项值/控件/校验 |
| Ch8 | Mock数据 | 🔴 P0 | 正常(≥5条)+空态+极限三组 |
| Ch9 | 边界条件 | 🟡 P1 | 权限/校验/网络/精度/溢出处理 |
| Ch10 | 验收标准 | 🔴 P0 | 每模块List/Detail/Action三问 |

---

## 🎨 设计体系选择

| 选 | 体系 | 厂商 | 主色 | 框架 | 适用场景 |
|----|------|------|------|------|---------|
| ⭐ | **Ant Design 5.x** | 阿里 | #1677FF | React | B端/通用（默认） |
| ② | **Element Plus** | 饿了么 | #409EFF | Vue 3 | Vue3 B端后台 |
| ③ | **TDesign** | 腾讯 | #0052D9 | 全端 | Web+小程序统一 |
| ④ | **Arco Design** | 字节 | #165DFF | React/Vue3 | 现代年轻化B端 |
| ⑤ | **Semi Design** | 抖音 | #0077FA | React | 数据密集型后台 |
| ⑥ | **NutUI** | 京东 | #FA2C19 | Vue 3 | 移动端电商H5 |
| ⑦ | 微信WeUI | 微信 | #07C160 | 原生 | 小程序 |
| ⑧ | Apple HIG | Apple | #0066CC | iOS | iOS原生App |

> 每个体系的完整Token/CSS变量/组件数/场景优缺点 → `references/design-system-options.md`

---

## 🏗 工作流

```
用户说「写个PRD」
  ↓
Phase 0 · 自动查背景（已有会话/文件/记忆）
  ↓
Phase 0c · 只问未知的 → 最多11问，一次性抛出
  ├── 组A：项目名/核心流程/技术栈/用户角色
  ├── 组B：设计体系/模块清单/输出用途(A/B/C)
  └── 组C：异常场景/核心操作/时间线/竞品
  ↓
用户一次性回答
  ↓
Phase 2 · 按P0/P1/P2组织输出
  ↓
Phase 3 · 输出10章PRD（自动套用VERSION A或B）
  ↓
PRD质量自检表 → ✅ 全部通过 → 交付
```

---

## 📋 PRD质量自检表

提交前逐项检查：

```
□ [P0] Ch1 设计Token已定义（主色/背景/侧栏/字号/圆角）
□ [P0] Ch2 树形导航 + 角色-菜单映射 + 默认落地页
□ [P1] Ch3 P0核心流程已标注页面跳转关系
□ [P2] Ch4 仅写影响原型的部分（权限/数据流向/接口格式）
□ [P0] Ch5 每页有唯一 data-page + 布局类型 + 依赖实体
□ [P0] Ch6 功能点细化到按钮级，无「多种」「各类」模糊词
□ [P0] Ch7 字段含类型/必填/选项值/展示控件/校验规则
□ [P0] Ch8 正常(≥5条) + 空态 + 极限三组Mock数据
□ [P1] Ch9 边界条件覆盖权限/校验/网络/精度/溢出
□ [P0] Ch10 每模块List/Detail/Action三问已答
□ 所有枚举值已列全
□ 搜索条件已逐字段列出控件类型+options
□ 状态有色值映射
□ 关联实体跨页面数据一致
```

---

## 🧑‍💻 贡献

欢迎 PR、Issue、讨论。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 主要贡献方向

- 增加设计体系（如华为OpenTiny、字节Semi已加）
- 更多实际项目PRD样例（`examples/` 目录待建）
- 非功能需求SLA参考值扩展
- 对接更多AI原型生成工具

---

## 📜 开源协议

MIT License。可自由使用、修改、商用。

---

## 🙏 致谢

- **Nous Research** — Hermes Agent 技能系统
- **Ant Design / Element Plus / TDesign / Arco Design / Semi Design / NutUI** — 优秀的设计体系
- **天机阁团队** — 小乔/貂蝉/大乔/孔明，实战反馈持续迭代
