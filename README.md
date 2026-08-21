# 📝 原型导向 PRD · 产品需求文档标准

**写PRD不再是为了交差，而是为了直接生成原型。** 10章结构化标准，P0/P1/P2 分级，按钮级颗粒度，AI 拿到就能出可点击原型。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRD Chapters](https://img.shields.io/badge/PRD-10%20Chapters%20%7C%20P0%2FP1%2FP2-blueviolet)](SKILL.md)
[![Design System](https://img.shields.io/badge/Design-Ant%20Design%205.x%20%7C%20Element%20Plus%20%7C%20TDesign%20%7C%20Arco%20%7C%20Semi%20%7C%20NutUI-orange)](references/design-system-options.md)
[![Validation](https://img.shields.io/badge/Validation-validate--prd.py%20%7C%20%3E%3D80%25%20P0-green)](scripts/validate-prd.py)

---

## 🔥 你在经历的痛点

写 PRD 的人都知道这些场景：

| # | 痛点 | 后果 |
|---|------|------|
| 1 | **PRD 写了 50 页，开发/设计只看目录** | 需求全靠口头补充，实现跑偏 |
| 2 | **「多种查询方式」「各类入库」这种模糊词** | AI 和开发全靠猜，枚举不全直接返工 |
| 3 | **PRD 和原型是两份文档，对不上** | 原型缺页缺字段，评审才发现，改一次 2 天 |
| 4 | **设计规范写「现代化、大气」** | 每个页面一个风格，Token 全靠心情 |
| 5 | **Mock 数据用「测试数据」** | 原型评审通过率差 5 倍，演示效果劝退甲方 |
| 6 | **需求改一版，PRD 重写一遍** | 丢失 50%+ 内容，字段表格全没了 |

**根因：PRD 写成了「给人读的说明书」，而不是「可执行的指令」。**

---

## 💡 这个仓库怎么解决

> ### PRD 不是文档，是原型生成指令。
> 每一条需求必须能直接翻译成 **DOM 元素 + 交互逻辑 + Mock 数据**。抽象描述和模糊需求会被跳过或脑补——本标准的每一章都在强制消灭模糊。

**一句话：写一份 PRD = 顺手把原型的关键决策也定了，AI 拿到就能出活。**

---

## ✨ 核心亮点

### 1️⃣ 10 章标准，P0/P1/P2 分级，缺失即不可交付

| 章 | 标题 | 优先级 | AI 读作 |
|----|------|--------|---------|
| Ch1 | 设计规范 | 🔴 P0 | → design-tokens.css |
| Ch2 | 信息架构 | 🔴 P0 | → 导航菜单 + 路由表 |
| Ch3 | 业务流程 | 🟡 P1 | → 页面跳转逻辑 + 状态机 |
| Ch4 | 系统架构上下文 | 🟢 P2 | → 权限按钮显隐规则 |
| Ch5 | 页面清单 | 🔴 P0 | → N 个 HTML 页面骨架 |
| Ch6 | 功能点清单 | 🔴 P0 | → 每个按钮/弹窗/搜索的 handler |
| Ch7 | 数据模型 | 🔴 P0 | → 表单字段 + 表格列 + 详情 |
| Ch8 | Mock 数据 | 🔴 P0 | → 正常/空/极限三组数据池 |
| Ch9 | 边界条件 | 🟡 P1 | → 空态/加载态/报错态变体 |
| Ch10 | 验收标准 | 🔴 P0 | → 自动化验收脚本 checklist |
| Ch11 | 运营指标与看板 | 🟡 P1 | → 看板页 + 指标口径（可运营性铁律） |

> **缺一条 P0 = 原型缺一项。** 不像传统 PRD 缺了也能交付，本标准让「遗漏」在文档阶段就现形。

### 2️⃣ 按钮级颗粒度，消灭「多种」「各类」

传统 PRD：「仓储管理 - 完成」❌
本标准：

```
| # | 操作类型 | 动作名称 | 触发方式 | 结果 | 数据来源 |
|---|---------|---------|---------|------|---------|
| 1 | Modal | 按车辆入库 | 点击入库按钮 | 弹出入库弹窗 | vehicleData |
| 2 | Modal | 零散入库 | 点击零散入库 | 弹出零散弹窗 | scatteredData |
| 3 | Batch | 批量审核 | 勾选+点击批量审核 | 弹出审核弹窗 | selectedIds |
```

「多种入库方式」这种写法直接不合格——**必须列全所有枚举值**（按车/OE/VIN/品类/批量/退货/调拨 = 7 种）。

### 3️⃣ 一套标准，两种输出形态

| 版本 | 模板文件 | 适用 | 特点 |
|------|---------|------|------|
| **VERSION A** 商用交付版 | `templates/commercial-prd-template.md` | 甲方交付/合同附件/开发排期 | 9章+附录，项目概述/SLA/风险路线图/竞品对标，MoSCoW 分级 |
| **VERSION B** AI原型生成版 | `templates/ai-prototype-prd-template.md` | 直接生成高保真原型 | 10章 P0/P1/P2，Mock 数据/边界条件/验收门禁直接翻译为 HTML |

> 不再需要「先写商用版，再转 AI 版」——双生成工作流一步到位，省一半成本。

### 4️⃣ 8 大设计体系，Token 即 CSS，零转换

Ant Design 5.x（默认）/ Element Plus / TDesign / Arco Design / Semi Design / NutUI / 微信 WeUI / Apple HIG。

选好体系，从 `references/design-system-options.md` 复制 CSS 变量块到 PRD Ch1 即可。**PRD 里写组件名，原型直接生成**——Ant Design 72 个组件覆盖原型 90% 场景。

### 5️⃣ 自动化校验，交付前先过机器

```bash
python3 scripts/validate-prd.py my-prd.md
# 通过标准：≥80% P0 门禁通过率
```

- 检查 Ch1/2/5/6/7/8/10 完整性（P0 硬依赖）
- P1/P2 章节给「建议补充」提示
- 自动识别模糊词、枚举不全、缺控件类型

### 6️⃣ 增量修订，绝不重写

需求变更时用 python-docx 对原文件做**精准修订**（段落/表格/插入），保留全部格式和内容——「更新 PRD」不是「重写 PRD」，50%+ 的原始内容（功能点表、验收标准、流程图）不会再丢。

### 7️⃣ 实战锤炼：反向工程也能写 PRD

没有文档？只有部署好的系统？支持：
- **SPA 反向工程** — 扒 JS bundle 提取路由/组件/数据模型 → 生成 PRD
- **RuoYi/若依 SSR 反向工程** — 登录 + 菜单树 + 表格列 + /add 表单字段三 Pass 提取（列表页只能看到 ~20% 字段，/add 表单才有 100%）

---

## 🚀 使用引导

### 10 秒开始（最快路径）

```bash
# 克隆仓库
git clone https://github.com/kangedy/prd-king.git
cd prd-king

# 打开 AI 原型版模板直接写
open templates/ai-prototype-prd-template.md
```

### 按身份使用

| 你的身份 | 怎么做 |
|---------|--------|
| **AI Agent 用户**（Hermes/OpenClaw/Codex） | 安装 skill → 说「帮我写个PRD」→ 自动走结构化访谈 → 出 10 章 PRD |
| **产品经理**（人肉写 PRD） | 打开 VERSION A 商用模板，按 10 章填空，交付前跑 validate-prd.py |
| **甲方/老板**（评审） | 只看 Ch1 设计规范 + Ch5 页面清单 + Ch8 Mock 数据，就能判断系统长什么样 |
| **开发**（拿需求开工） | Ch6 功能点 + Ch7 数据模型 + Ch10 验收标准，就是你的实现清单和测试用例 |
| **项目经理**（排期） | Ch11 运营指标 + 附录风险路线图，确定分期交付范围 |

### AI Agent 安装

```bash
# Hermes Agent
mkdir -p ~/.hermes/skills/product/prd/ && cp -r * ~/.hermes/skills/product/prd/
→ 说「帮我写个PRD」，自动走 Phase 0c 结构化访谈（只问未知的，最多11问一次抛完）

# Codex CLI
codex skills install kangedy/prd-king

# OpenClaw
cp SKILL.md ~/.openclaw/skills/prd-skill.md
```

### 完整使用链路

```
prd-king 写PRD → prototype-king 转原型 → verify-prototype.py 交付验收
      ↓                ↓                        ↓
  10章标准          8 Phase 流水线            ≥95% 门禁
```

### 快速自检（交付前 1 分钟）

```
□ 所有 P0 章节完整（Ch1/2/5/6/7/8/10）
□ 所有枚举值已列全（没有被「多种」「各类」模糊带过的）
□ 每个功能点有明确操作类型+触发方式+结果
□ 每个字段有类型+必填+选项值+校验规则
□ Mock 数据有正常/空/极限三组
□ 状态有对应的色值映射
□ 跑过 validate-prd.py，P0 通过率 ≥80%
```

---

## 📂 目录结构

```
prd-king/
├── SKILL.md                              ← 主文件（10章标准 + 完整工作流）
├── scripts/validate-prd.py               ← PRD结构校验脚本（P0门禁 ≥80%）
├── templates/
│   ├── commercial-prd-template.md        ← VERSION A · 商用交付版
│   └── ai-prototype-prd-template.md      ← VERSION B · AI原型生成版
├── references/                           ← 29个参考文件
│   ├── design-system-options.md          ← 8大设计体系Token完整参考
│   ├── checklist-to-prd-batch-generation.md  ← 验收清单→PRD批量生成
│   ├── enterprise-to-ai-prototype-conversion.md ← 企业PRD→AI原型版转换
│   ├── spa-reverse-engineering-prd.md    ← SPA反向工程→PRD
│   ├── ruoyi-ssr-reverse-engineering.md  ← RuoYi SSR反向工程→PRD
│   └── ...（详见 SKILL.md 参考文件表）
├── examples/super-todo-list/PRD.md       ← 完整10章PRD示例
├── posts/                                ← 推广帖草稿
└── CHANGELOG.md
```

## 🔗 配套项目

| 项目 | 链接 | 功能 |
|------|------|------|
| **prd-king**（本仓库） | https://github.com/kangedy/prd-king | **PRD写作标准** — 10章模板+设计体系+校验脚本 |
| **prototype-king** | https://github.com/kangedy/prototype-king | **PRD→原型工作流** — 8 Phase + 自动化验收 |

---

## 🧑‍💻 贡献

欢迎 PR、Issue、讨论。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 主要贡献方向

- 增加设计体系（华为 OpenTiny、字节 Semi 已加）
- 更多实际项目 PRD 样例（`examples/` 目录）
- 非功能需求 SLA 参考值扩展
- 对接更多 AI 原型生成工具

---

## 📜 开源协议

MIT License。可自由使用、修改、商用。

---

## 🙏 致谢

- **Nous Research** — Hermes Agent 技能系统
- **Ant Design / Element Plus / TDesign / Arco Design / Semi Design / NutUI** — 优秀的设计体系
