# Iframe SPA 多Agent并行原型生成工作流

当PRD规模很大（50+页面、4+模块），需要产出高保真交互原型HTML时，用此工作流。

## 架构

```
母版壳 (master.html)
├── 左侧：侧栏导航（所有模块菜单）
├── 顶部：面包屑
├── 中央：iframe 内容区
└── JS：路由切换 + Toast + Modal/Confirm

模块HTML (agent-a.html / agent-b.html / ...)
├── 每个模块独立HTML文件
├── 内嵌 <style>（无外部CSS依赖）
├── 使用 hash 路由切换子页面 (#page-name)
└── data-action 全局交互委托
```

## 执行流程

### Phase 1: 母版壳（主Agent）
- Ant Design CSS变量
- 侧栏导航（完整菜单树）
- PAGE_MODULE映射表：菜单key → `模块文件.html#默认子页面`
- iframe路由切换函数
- Toast / Modal / Confirm 全局组件

### Phase 2: 并行生成模块HTML（3 Agent，max_concurrent=3）
每个Agent负责15-25页，生成自包含HTML：
- 完整CSS（与母版壳共享变量）
- hash路由切换（window.onhashchange → showPage）
- data-action交互委托（search/reset/add/edit/delete/view/export/approve/reject/submit）
- Mock数据（真实业务场景命名）
- 每页标配：KPI卡片+筛选栏+数据表格+分页+操作按钮

### Phase 3: 补充模块（1 Agent，如有剩余模块）

### Phase 4: 集成验证
- 母版壳内点击各菜单，验证iframe加载正确
- 验证每个子页面的hash路由
- 验证交互反馈

## PAGE_MODULE 映射表（关键）

```javascript
var PAGE_MODULE = {
  'dashboard': 'prototype_settlement.html#dashboard',
  'campaign': 'prototype_campaign.html#campaign-list',
  'coupon': 'prototype_campaign.html#coupon-list',
  'rules': 'prototype_ai.html#rules-config',
  'merchant': 'prototype_merchant.html#merchant-list',
  // ... 每个菜单项 → 文件名 + 默认子页面hash
};
```

### 映射表要点
1. 每个菜单key映射到「模块文件 + #子页面hash」，一次到位，不做二次拼接
2. 导航函数直接使用映射值：`iframe.src = PAGE_MODULE[page]`
3. 初始 `currentPage = null`（不是 `'dashboard'`），确保首次加载触发导航

## 常见Pitfalls

### 1. 导航下拉失效（overflow-x:auto裁切）
`.nav-bar` 中的 `overflow-x:auto` 会导致 `overflow-y` 也被强制为 `auto`，裁切内部 `position:absolute` 的下拉菜单。
**修复**：移除 `overflow-x:auto`，或用 `overflow-y:visible` 显式覆盖。

### 2. 首次导航被跳过
`var currentPage = 'dashboard'; navigate('dashboard', ...)` → `if (page === currentPage) return;` 跳过。
**修复**：`var currentPage = null;`

### 3. iframe内hash路由与母版壳hash冲突
母版壳向iframe传hash时，应直接拼在 iframe.src 中：`prototype_campaign.html#coupon-list`，而非依赖iframe的onhashchange二次路由。

### 4. Agent生成的模块HTML自带导航与母版壳侧栏重复
模块HTML内部可以有子模块快速导航（如tabs），但不应有与母版壳重复的侧栏。模块内导航使用 `href="#sub-page"` + `onhashchange`。

### 5. 优惠券管理链接到了活动页面
PAGE_MODULE中同文件不同hash未区分 → `'coupon': 'prototype_campaign.html'` 加载后默认显示活动页。
**修复**：`'coupon': 'prototype_campaign.html#coupon-list'`

## 每个Agent的输出规范

委托给子Agent的context必须包含：
- 完整的CSS变量块（粘贴到context，不让子Agent读文件）
- 页面清单（data-page名称列表）
- Mock数据规范（真实场景命名）
- 输出文件路径
- 交互行为（data-action枚举+响应方式）
