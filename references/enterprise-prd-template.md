# Enterprise Multi-Subsystem PRD Template

> Reference template for large-scale Chinese enterprise projects with 3~4 subsystems.
> Adapted from the 湖南高速客户中心项目 PRD — replace content with actual project details.

---

## Document Header

```markdown
# {Project Name} — {Subsystem Count}子系统详细需求PRD

**版本：** V1.0
**日期：** {Date}
**编制：** 产品团队
**状态：** 初稿（待甲方确认）
```

## Document Structure

```markdown
## 文档说明

### 文档目的
{1 paragraph on what this doc drives — dev handoff, RFP, vendor bid, etc.}

### 子系统全景
Architecture diagram with:
- Entry points (小程序/APP/公众号)
- API Gateway layer
- Subsystem boxes (3~6, each with key modules listed inside)
- Third-party integration layer (ETC, POS, payment, tax, etc.)

### 角色定义
Table: Role | Description | Core needs
```

## Pre-PRD: Organizational Context Mapping

Before writing the PRD for an enterprise multi-department project, **first map the client's organizational structure**. This determines subsystem boundaries, data ownership, and the autonomy vs. unification balance.

| Step | Action | Output |
|:-----|:-------|:-------|
| 1 | Identify all business departments/divisions | Department list with core business scope |
| 2 | Map each department's existing systems | Legacy system inventory (name, users, tech stack) |
| 3 | Determine autonomy boundaries | Which decisions are centralized vs. departmental |
| 4 | Identify existing membership/积分 systems | Critical: these determine the migration scope |
| 5 | Map departments to PRD subsystems | Which department owns/uses which module |

**Common pattern (from 湖南高速):**
- Multiple departments with independent operational authority → 积分互通 must balance unification (统一价值折现率) vs. autonomy (各事业部自定发行规则)
- Existing legacy systems (美美哒会员系统, 50万+ users) → PRD needs a dedicated migration module
- Each department has distinct use cases → role definitions must cover all departments

## Subsystem Architecture Alignment

When writing a PRD based on an existing client design document (设计提纲), compare your proposed architecture against theirs:

```markdown
### 架构对齐说明

**甲方设计提纲定义：** {X}个子系统
- {Subsystem A}: {scope}
- {Subsystem B}: {scope}

**我方PRD划分：** {Y}个子系统
- 差异1: {我方多了一个子系统} → 原因：{定位为平台能力中心，赋能各子公司}
- 差异2: {子系统范围不同} → 原因：{按客户需求调整}
```

## Data Volume Planning

When the client provides data volume estimates, embed them directly:

```markdown
### 数据量级规划（依据甲方设计提纲）

| 数据类型 | 估算数据量 | 存储周期 | 说明 |
|:--------|:---------|:--------|:----|
| 会员数据 | ~{N}TB | 5年 | {basis} |
| 客户数据 | ~{N}TB | 5年 | {basis} |
| 画像数据 | ~{N}TB | 5年 | {basis} |
| **总数据量** | **~{N}TB** | **5年** | 按{N}TB级别规划架构 |
```

## Tag Taxonomy Integration

When the client has a pre-defined tag taxonomy, embed it as a reference table:

```markdown
**六大类标签体系（甲方定义，直接复用）：**

| 大类 | 说明 | 典型标签示例 | 标签数量 |
|:----|:-----|:------------|:-------:|
| **客户基础属性** | 自然属性、联系信息、车辆属性 | 性别、年龄、新能源车标签 | ~30个 |
| **客户服务画像** | 诉求特征、服务敏感度、服务渠道偏好 | 15天高频投诉、退费客户 | ~35个 |
| **客户渠道偏好** | 各渠道使用频次与偏好 | 热线低频/高频、公众号活跃/沉默 | ~25个 |
| **客户信用画像** | 黑名单、欠费、稽核风险 | ETC卡黑名单、追缴名单 | ~20个 |
| **客户行为习惯** | 通行行为、消费能力、拓展应用、驻留 | 高频通行、月消费能力分层 | ~100个 |
| **客户业务属性** | ETC发行、生命周期、车辆运营 | ETC新用户、多车客户、集装箱车 | ~50个 |
```

## Legacy System Migration Module

Include this when the client has an existing membership/积分 system:

```markdown
### {N}.{M}.{X} {Legacy System}存量对接

**功能ID：** {SS}-M{NN}
**优先级：** P0 (Phase 1 — must ship with core systems)
**依赖：** 客户管理、会员等级体系

**功能点：**

| 编号 | 功能点 | 详细说明 |
|:---|:------|:---------|
| {SS}-M{NN}-01 | 存量数据摸底 | 盘点存量数据：用户数、等级分布、积分余额、优惠券 |
| {SS}-M{NN}-02 | 客户ID映射 | 旧系统ID → 统一UCID，手机号+身份证匹配 |
| {SS}-M{NN}-03 | 存量积分迁移 | 1:1等值转入，原发行方承担负债，30天通知 |
| {SS}-M{NN}-04 | 会员等级对接 | 旧{N}级 → 统一等级映射规则 |
| {SS}-M{NN}-05 | 双轨运行期 | 30天新老并行，双向同步 |
| {SS}-M{NN}-06 | 一致性校验 | 全量校验，差异率 < 0.01% |
| {SS}-M{NN}-07 | 回滚预案 | 30分钟内切回旧系统 |

## Role Definitions (Multi-Department)

Each department with independent operational authority should get its own row:

```markdown
| 角色 | 描述 | 核心诉求 |
|:----|:-----|:---------|
| **{Dept A}** | {What they do} | {What they need} |
| **{Dept B}** | {What they do} | {What they need} |
```

## Subsystem PRD Sections

Each subsystem follows this structure:

```markdown
# {N}、{Subsystem Name}({English Name})

## {N}.1 概述
{1-2 paragraphs: purpose, what it owns, module count, priority}

## {N}.2 功能模块详情

### {N}.{M}.1 {Module Name}

**功能ID：** {SS}-M{NN}
**优先级：** P0/P1/P2
**依赖：** {dependent module IDs or "无"}

**需求描述：**
{Summary}

**功能点：**

| 编号 | 功能点 | 详细说明 |
|:---|:------|:---------|
| {SS}-M{NN}-01 | {Feature} | {Detail} |

**验收标准：**
- Measurable criteria
```
