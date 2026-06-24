---
name: ai-prototype-prd-template
description: 'VERSION B — AI生成原型版PRD模板。面向AI Agent（Hermes/my self）的PRD，结构化数据优先，可直接翻译为HTML/CSS/JS原型。'
---

# PRD Template · AI原型生成版 (VERSION B)

> 适用场景：直接给AI生成高保真交互原型
> 核心原则：**结构化数据优先**，P0章节缺一条 = 原型缺一项
> 
> 优先级标注：🔴[P0]=原型硬依赖 / 🟡[P1]=强烈建议 / 🟢[P2]=锦上添花
> 
> ⚡ AI读取说明：本PRD的每一行都是原型生成指令。不要写散文，不要写「多种」「各类」，选项值全部列全。

---

## Ch1 · Design Spec / 设计规范 [🔴P0]

### 1.1 设计系统选择

```
┌─ 默认: Ant Design 5.x（React B端）
├─ Vue 3 B端 → Element Plus (主色:#409EFF)
├─ 全端统一 → TDesign (主色:#0052D9)
├─ 现代B端   → Arco Design (主色:#165DFF)
├─ 数据密集型 → Semi Design (主色:#0077FA)
├─ 移动电商   → NutUI (主色:#FA2C19, 375px)
├─ 小程序    → 微信WeUI (主色:#07C160, 375px)
└─ iOS App  → Apple HIG (44pt, SF字体)
```

### 1.2 Token（以Ant Design 5.x为例）

```
框架: Ant Design 5.x  /  Element Plus  /  TDesign  /  Arco Design  /  Semi  /  NutUI

```
侧栏宽度: 240px
内容区最大: 1440px
栅格列: 24
栅格间距: 16px
```

---

## Ch2 · Information Architecture / 信息架构 [🔴P0]

### 2.1 导航菜单

```
├── 首页 (/dashboard)
├── 交易管理 (/trade)
│   ├── 订单列表 (/trade/order)       data-page="order-list"
│   │   ├── 全部订单                   filter=all
│   │   ├── 待审核                     filter=pending_review
│   │   └── 已完成                     filter=completed
│   └── 退款管理 (/trade/refund)      data-page="refund-list"
├── 商品管理 (/product)
│   ├── 商品列表 (/product/list)      data-page="product-list"
│   └── 分类管理 (/product/category)  data-page="category-list"
├── 报表中心 (/report)
│   └── 销售报表 (/report/sales)      data-page="sales-report"
└── 系统设置 (/system)
    ├── 用户管理 (/system/user)        data-page="user-list"
    └── 角色管理 (/system/role)        data-page="role-list"
```

### 2.2 角色-菜单映射

```
超级管理员: 全部菜单
运营: 交易管理 + 报表中心
商家: 商品管理(仅自己) + 订单管理(仅自己)
财务: 交易管理(只读) + 报表中心
```

### 2.3 默认落地页

```
默认: /dashboard (数据概览)
角色无权限时: /trade/order
```

---

## Ch3 · Business Process / 业务流程 [🟡P1]

### 3.1 核心流程

```
下单流程 [P0]:
  product-list → [点击购买] → product-detail
  → [选择规格+加入购物车] → cart-page
  → [结算] → order-confirm (收货地址/优惠券/备注)
  → [提交订单] → order-detail (status=待支付)
  → [支付] → payment-page (微信/支付宝)
  → [支付成功] → order-detail (status=待审核) → Toast+3s倒计时跳回

审核流程 [P0]:
  order-list → [勾选1-N条] → [点击批量审核]
  → modal-review (选择通过/驳回+填写备注)
  → [提交] → 列表刷新 (status变更)
  单条审核: order-detail → [审核按钮] → modal-review

退款流程 [P1]:
  order-detail → [申请退款]
  → modal-refund (选择原因+上传凭证+提交)
  → 列表刷新 (status=退款中)
  → [商家审核] → modal-refund-review (同意/拒绝)
  → [确认] → 退款到账 (status=已退款)
```

### 3.2 异常流程

```
支付超时:
  order-detail (status=待支付) → [30分钟未支付]
  → 自动取消 (status=已取消) → 系统通知用户

审核驳回:
  order-detail → [审核驳回+填写原因]
  → order-detail (status=退款中) → 退款到账

支付失败:
  payment-page → [支付失败]
  → Toast「支付异常，请重试」→ 保留待支付状态
  → 30分钟内可重新支付
```

### 3.3 状态机

```
Order状态机(枚举string非数字):
  pending_payment ──[支付成功]──→ pending_review
  pending_payment ──[超时取消]──→ cancelled
  pending_review ──[审核通过]──→ pending_delivery
  pending_review ──[审核驳回]──→ refunding
  pending_delivery ──[商家发货]──→ shipped
  shipped ──[确认收货]──→ completed
  completed ──[申请退款]──→ refunding
  refunding ──[退款完成]──→ completed

状态-颜色映射:
  pending_payment: #FAAD14 (黄)
  pending_review: #1890FF (蓝)
  pending_delivery: #722ED1 (紫)
  shipped: #52C41A (绿)
  completed: #8C8C8C (灰)
  cancelled: #FF4D4F (红)
  refunding: #FF7A45 (橙)
```

---

## Ch4 · System Context / 系统架构上下文 [🟢P2]

### 4.1 权限规则 (影响按钮显隐)

```
角色 === 超级管理员 → 全部按钮可见
角色 === 运营 → 可见: 审核/导出/查看  隐藏: 删除/编辑系统设置
角色 === 商家 → 可见: 商品管理/订单管理(仅自己)  隐藏: 系统设置/报表/审核
角色 === 财务 → 可见: 订单列表(只读)/报表  隐藏: 审核/编辑/删除
```

### 4.2 数据流向 (影响Mock数据结构)

```
订单数据: 外部ERP → 每日同步 → 本地Order表 → API → 前端展示
商品图片: OSS/CDN → https://img.xxx.com/{bucket}/{key}
缓存: 订单列表 5min / 商品列表 30min
```

### 4.3 接口格式 (影响Mock数据)

```
统一返回: {code:0, msg:"success", data:{}}
分页: page/pageSize (从1开始)
状态: string枚举 (非数字)
时间: ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)
```

---

## Ch5 · Page Inventory / 页面清单 [🔴P0]

| data-page | 标题 | 模块 | 布局 | 依赖实体 |
|-----------|------|------|------|---------|
| dashboard | 数据概览 | 首页 | cards | OrderStat |
| order-list | 订单列表 | 交易 | table+search | Order |
| order-detail | 订单详情 | 交易 | detail | Order/OrderItem |
| modal-review | 审核弹窗 | 交易 | modal+form | Review |
| order-refund | 退款弹窗 | 交易 | modal+form | Refund |
| product-list | 商品列表 | 商品 | table+search | Product |
| product-form | 商品上架 | 商品 | form+steps | Product/Category |
| cart-page | 购物车 | 交易 | cards+calc | Cart |
| user-list | 用户管理 | 系统 | table+search | User |
| role-list | 角色管理 | 系统 | table+search | Role |

---

## Ch6 · Feature Inventory / 功能点清单 [🔴P0]

### 6.1 功能点表（每页独立）

> 操作类型枚举: Search / Navigation / Modal / Submit / Download / Delete / Batch / Switch / Refresh

#### order-list (订单列表)

| # | 类型 | 动作 | 触发 | 结果 | 数据源 |
|---|------|------|------|------|--------|
| 1 | Search | 查询订单 | 点击搜索按钮 | table刷新 | API:/order/list |
| 2 | Navigation | 查看详情 | 点击行 | 跳转order-detail | id |
| 3 | Modal | 审核订单 | 点击审核按钮 | 弹出modal-review | mockReview |
| 4 | Download | 导出 | 点击导出 | 下载Excel | API:/order/export |
| 5 | Modal+Batch | 批量审核 | 勾选+批量审核 | 弹出modal-review | selectedIds |
| 6 | Switch | Tab切换 | 点击全部/待审核/已完成 | table刷新 | filter参数 |
| 7 | Refresh | 刷新列表 | 点击刷新按钮 | table刷新 | 当前查询条件 |

#### product-list (商品列表)

| # | 类型 | 动作 | 触发 | 结果 | 数据源 |
|---|------|------|------|------|--------|
| 1 | Search | 查询商品 | 点击搜索 | table刷新 | API:/product/list |
| 2 | Navigation | 查看详情 | 点击行 | 跳转product-detail | id |
| 3 | Navigation | 新增商品 | 点击新增 | 跳转product-form | — |
| 4 | Modal | 删除商品 | 点击删除 | 确认弹窗→删除 | id |
| 5 | Switch | 上架/下架 | 点击开关 | 状态变更Toast | id/status |

### 6.2 搜索条件清单

#### order-list 搜索条件

```
字段: order_no (文本框, placeholder="输入订单号")
字段: customer_phone (文本框, placeholder="输入买家手机号")
字段: status (下拉选择, options=[全部/待支付/待审核/待发货/已发货/已完成/已取消/退款中])
字段: date_range (日期范围选择器, 格式YYYY-MM-DD)
按钮: 查询 (type=primary)
按钮: 重置 (清空所有条件)
```

#### product-list 搜索条件

```
字段: product_name (文本框, placeholder="输入商品名称")
字段: category_id (下拉选择, options=动获取)
字段: status (下拉选择, options=[全部/上架/下架])
按钮: 查询
按钮: 重置
```

### 6.3 弹窗清单

| modal-id | 触发 | 字段 | 按钮 |
|----------|------|------|------|
| modal-review | 审核按钮 | 审核结果(通过/驳回radio)+备注(textarea) | 提交/取消 |
| modal-refund | 申请退款 | 退款原因(dropdown)+金额(number)+凭证(upload) | 提交/取消 |
| modal-delete | 删除按钮 | 确认文案(text)+输入密码(password) | 确认删除/取消 |

---

## Ch7 · Data Model / 数据模型 [🔴P0]

### 7.1 实体字段表

#### Order (订单)

| 字段 | 类型 | 必填 | 选项/范围 | 控件 | 校验 |
|------|------|------|----------|------|------|
| order_no | string | Y | — | Input | 格式:ORD+14位时间+6位随机数 |
| customer_name | string | Y | ≤32字 | Input | — |
| customer_phone | string | Y | 11位 | Input | regex:/^1[3-9]\d{9}$/ |
| status | enum | Y | pending_payment/pending_review/pending_delivery/shipped/completed/cancelled/refunding | Tag+颜色 | 见状态机 |
| total_amount | number | Y | ≥0.01 | 金额¥格式化 | 保留2位小数 |
| payment_method | enum | Y | wechat/alipay/transfer | RadioGroup | — |
| paid_at | datetime | N | — | DatePicker | YYYY-MM-DD HH:mm |
| remark | string | N | ≤500字 | TextArea | — |
| created_at | datetime | Y | — | DatePicker | YYYY-MM-DD HH:mm |

#### OrderItem (订单项)

| 字段 | 类型 | 必填 | 选项/范围 | 控件 |
|------|------|------|----------|------|
| product_name | string | Y | — | Text |
| product_image | string | Y | — | Image(src) |
| quantity | number | Y | ≥1 | Text |
| unit_price | number | Y | ≥0.01 | ¥格式化 |
| subtotal | number | Y | =quantity*unit_price | ¥格式化(计算) |

#### Review (审核记录)

| 字段 | 类型 | 必填 | 选项/范围 | 控件 |
|------|------|------|----------|------|
| action | enum | Y | approve/reject | RadioGroup |
| reason | string | N(驳回时Y) | ≤200字 | TextArea(reject时显示) |
| created_at | datetime | Y | — | Text(只读) |

#### User (用户)

| 字段 | 类型 | 必填 | 选项/范围 | 控件 |
|------|------|------|----------|------|
| username | string | Y | ≤32字 | Input |
| role | enum | Y | super_admin/operator/merchant/finance | Select |
| phone | string | Y | 11位 | Input |
| email | string | N | — | Input |
| status | enum | Y | active/disabled | Switch |
| created_at | datetime | Y | — | Text(只读) |

---

## Ch8 · Mock Data / 模拟数据 [🔴P0]

### 8.1 正常数据

```javascript
var MOCK_ORDERS = [
  { id: 1, order_no: "ORD202601010001", customer_name: "张三",
    customer_phone: "13800138001", status: "pending_review",
    total_amount: 3842.50, payment_method: "wechat",
    paid_at: "2026-01-01 10:30", remark: "麻烦尽快发货", created_at: "2026-01-01 10:28" },
  { id: 2, order_no: "ORD202601010002", customer_name: "李四汽车服务",
    customer_phone: "13912345678", status: "pending_review",
    total_amount: 15680.00, payment_method: "transfer", created_at: "2026-01-01 14:15" },
  { id: 3, order_no: "ORD202601010003", customer_name: "王五汽配",
    customer_phone: "13698765432", status: "pending_delivery",
    total_amount: 238.00, payment_method: "alipay",
    paid_at: "2026-01-01 09:00", created_at: "2026-01-01 08:55" },
  { id: 4, order_no: "ORD202512310004", customer_name: "赵六",
    customer_phone: "13755556666", status: "shipped",
    total_amount: 8999.00, payment_method: "wechat",
    paid_at: "2025-12-31 20:00", remark: "送到南门保安室", created_at: "2025-12-31 19:50" },
  { id: 5, order_no: "ORD202512300005", customer_name: "孙七汽修",
    customer_phone: "15800001111", status: "completed",
    total_amount: 520.00, payment_method: "wechat",
    paid_at: "2025-12-30 15:00", created_at: "2025-12-30 14:55" },
];
```

### 8.2 空数据

```javascript
var MOCK_ORDERS_EMPTY = [];  // 显示空态: 「暂无订单数据」+ 插画
var MOCK_SEARCH_EMPTY = [];  // 显示: 「未找到相关订单」+ 建议调整搜索条件
```

### 8.3 极限数据

```javascript
var MOCK_ORDERS_LONG = [
  { id: 999, order_no: "ORD202601010999", customer_name: "这是一个超级长的客户名字有限公司华南分公司",
    customer_phone: "13800138001", status: "pending_review",
    total_amount: 9999999.99, payment_method: "transfer",
    remark: "请送到广东省广州市天河区珠江新城华夏路16号富力盈凯广场45楼4508室前台转交采购部张经理收，联系电话13800138001，工作时间周一到周五9:00-18:00，到货前请提前2小时电话通知",
    created_at: "2026-01-01 10:28" },
];
// 1000条分页: 使用同一模板生成，分页page=1/2/3...50
// 日期极值: created_at = "1970-01-01 00:00" / "2099-12-31 23:59"
```

---

## Ch9 · Boundary Conditions / 边界条件 [🟡P1]

| 场景 | 原型处理 |
|------|---------|
| 无权限操作 | 按钮灰显 + tooltip「联系管理员开通权限」 |
| 表单必填项校验失败 | 边框变红 + 字段下方红色提示文字 |
| 网络错误 | Toast「网络异常，请稍后重试」+ 重试按钮 |
| 并发审核 | Toast「该订单正在被XXX审核」+ 按钮灰显 |
| 跨页选中 | 仅本页选中（不跨页全选）|
| 超长文本 | CSS截断... + title属性tooltip全文 |
| 金额格式 | ¥1,234.00（千分位+2位小数）|
| 手机号展示 | 中间4位掩码：138****8001 |
| 空态 | 插画+「暂无数据」+ 引导操作按钮 |
| 加载态 | Skeleton骨架屏（表格/卡片） |
| 分页边界 | page=1 时上一页禁用 / page=max 时下一页禁用 |
| 日期极值 | 输入框限制不可选超过当前日期 |

---

## Ch10 · Acceptance Criteria / 验收标准 [🔴P0]

### 10.1 模块验收三问

| data-page | List在哪 | Detail在哪 | Action有哪些 |
|-----------|---------|-----------|------------|
| order-list | Ant Design Table + Pagination | 点击行→order-detail页 | search/view/review/export/batch-review |
| product-list | Ant Design Table + Pagination | 点击行→product-detail页 | search/view/add/delete/toggle-status |
| user-list | Ant Design Table + Pagination | 点击行→user-edit弹窗 | search/add/edit/disable |

### 10.2 自动化验收门禁

```
G1 功能完整性: 每个功能点有handler
G2 页面完整性: 所有data-page存在且可渲染
G3 字段完整性: 所有字段在原型中出现
G4 数据一致性: 同一实体跨页面数据一致
G5 状态覆盖: 每个列表页有空态+加载态
G6 字号合规: 正文≥14px / 表格≥13px / 标签≥12px
G7 JS语法: node --check 无语法错误
G8 按钮无遗漏: 每个button有handler
G9 弹窗完整性: 每个showModal有对应id元素
G10 路由完整性: 每个data-page在菜单树中存在
```

---

## 附录：10章优先级速查

```
Ch#  | 章节 | 优先级 | AI读作
-----|------|--------|--------
Ch1  | 设计规范 | 🔴P0 | → design-tokens.css
Ch2  | 信息架构 | 🔴P0 | → 导航菜单+路由表
Ch3  | 业务流程 | 🟡P1 | → 页面跳转逻辑
Ch4  | 系统架构 | 🟢P2 | → 权限按钮显隐规则
Ch5  | 页面清单 | 🔴P0 | → N个HTML页面骨架
Ch6  | 功能点清单 | 🔴P0 | → 按钮+弹窗+搜索的handler
Ch7  | 数据模型 | 🔴P0 | → 表单字段+表格列+详情
Ch8  | Mock数据 | 🔴P0 | → mock-data.js
Ch9  | 边界条件 | 🟡P1 | → 空态/加载态/报错态变体
Ch10 | 验收标准 | 🔴P0 | → verify-prototype.py checklist
```

## PRD质量自检表

> 交付前逐项检查，全部 ✅ 方可提交。

```
□ [P0] Ch1 设计Token已定义（主色/背景/侧栏/字号/圆角）
□ [P0] Ch2 导航+角色映射完成
□ [P1] Ch3 P0核心流程已标注页面跳转关系
□ [P2] Ch4 仅写影响原型的部分
□ [P0] Ch5 每页有唯一 data-page
□ [P0] Ch6 功能点细化到按钮级，无模糊词
□ [P0] Ch7 字段含类型/必填/选项/控件/校验
□ [P0] Ch8 有正常/空/极限三组Mock数据
□ [P1] Ch9 边界条件覆盖权限/校验/网络/精度
□ [P0] Ch10 每模块List/Detail/Action已答
□ 所有枚举值已列全
□ 搜索条件已列出控件类型
□ 状态有色值映射
```
