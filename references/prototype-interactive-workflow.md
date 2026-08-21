# 从静态原型到全交互Demo — 执行工作流

当PRD和页面骨架就绪后，需要将静态HTML原型升级为数据驱动的全交互Demo。本工作流用于91+页、700+按钮的大规模SPA原型。

## 核心原则

**Toast模拟永不通过验收。** 用户说"完善交互"、"补充完整"、"全部完成"时，意味着：
- 搜索按钮必须真正过滤数据，不只是弹Toast
- 新增/编辑按钮必须打开表单弹窗，提交后数据真正写入数组
- 删除按钮必须confirm确认后真正从数组移除
- 导出按钮必须真实下载CSV
- 分页必须真正切换数据页

## 四波执行模型（有顺序依赖）

```
第1波：数据层 ──→ 第2波：弹窗体系 ──→ 第3波：CRUD逻辑 ──→ 第4波：业务流
  550条/20实体      动态生成表单         增删改查+分页+导出     审批/上下架/冻结
```

### 第1波：Mock数据层（2子Agent并行，~3min）

生成业务Mock数据，直接注入HTML `<script>` 标签。

| 子系统 | 实体 | 条数 | 数据规范 |
|--------|------|:----:|---------|
| KHZX客户中心 | customers/users/accounts/tags/rules | 各30 | 真实中文名、湘牌、1xx手机 |
| HYZX会员中心 | members/levels/pointsRecords/partners/activities | 各30 | 等级/积分/消费关联 |
| YXZX营销中心 | products/merchants/coupons/orders/strategies | 各30 | 真实品类/企业名/金额 |
| KHSJ数据服务 | dataSources/idMappings/dataPackages/tasks/systemLogs | 各20 | ETC门架等真实数据源 |
| **合计** | **20实体** | **550条** | |

**输出格式：**
```javascript
var DATA = { "customers": [...], "members": [...], ... };
```

### 第2波：弹窗体系（1子Agent，~5min）

替换所有data-action="add/edit/view"的Toast模拟为真实弹窗。

**新增弹窗**：动态生成表单，字段从数据模型推断：
```javascript
function openFormModal(title, fields, data, onSave) {
  // fields: [{key, label, type:'text'|'select'|'number', options, required}]
  // 生成modal DOM → append到body → 显示
}
```

**编辑弹窗**：同新增弹窗，预填现有数据。
**详情弹窗**：只读表格展示所有字段。

**关闭方式**：遮罩点击 / Escape键 / 取消按钮。

### 第3波：CRUD逻辑（1子Agent，~7min）

实现7个核心模块，全部操作真实修改DATA数组：

| # | 模块 | 函数 | 行为 |
|:-:|------|------|------|
| 1 | 表格渲染 | `renderTable()` | 数据→HTML行，含操作按钮 |
| 2 | 搜索筛选 | `doSearch()` | filter模糊匹配→重绘 |
| 3 | 新增 | `DATA[entity].push()` | 生成ID→追加→重绘 |
| 4 | 编辑 | `findIndex()`→splice | 预填→更新→重绘 |
| 5 | 删除 | `splice(idx,1)` | confirm→移除→重绘 |
| 6 | 分页 | `paginateData()` | slice切片→页码导航 |
| 7 | 导出CSV | `exportCSV()` | Blob→a.click下载(UTF-8 BOM) |

**页面-实体映射表（19个关键映射）：**
```javascript
var PAGE_ENTITY_MAP = {
  'khzx-customer-list': 'customers',
  'khzx-user-list': 'users',
  'hyzx-member-list': 'members',
  'yxzx-product-list': 'products',
  'yxzx-coupon-list': 'coupons',
  'khsj-collect': 'dataSources',
  // ...共19页
};
```

### 第4波：业务流闭环（与第3波合并执行）

| 功能 | 实现 |
|------|------|
| 审批流转 | `transitionStatus()` + STATUS_TRANSITIONS白名单 |
| 上下架 | 状态切换 + 表格重绘 |
| 冻结/解冻 | 状态切换 + 行样式变更 |

## 常见陷阱

### 🔴 Toast-only mockup（最常被纠正）
不要在任何按钮处理函数中只写 `showToast()`。用户会立即发现并说"不要模拟的"。
正确的做法：要么不做（保持按钮无功能），要么做真的（操作数据+重绘）。

### 🔴 字段名不匹配
数据字段名与CRUD代码中引用的字段名必须完全一致。
```javascript
// ❌ DATA中有"customerLevel"，代码写"level"
// ✅ 保持一致性
```
**预防**：写CRUD前先 `JSON.stringify(DATA[entity][0])` 打印一条记录确认字段名。

### 🟡 搜索后不分页
搜索过滤后数据量可能变化，必须重置到第1页并重新计算总页数。

### 🟡 分页后搜索条件丢失
翻页时必须保持filter条件不变。用闭包或全局变量保存当前搜索条件。

### 🟡 弹窗ID冲突
91页共用一套弹窗系统，弹窗ID必须用 `'modal-' + currentPage` 确保唯一。

### 🟢 状态流转校验
不允许非法流转（如"草稿"→"已通过"），用白名单控制：
```javascript
var STATUS_TRANSITIONS = {
  '待审批': ['已通过', '已驳回'],
  '草稿': ['已上架'],
  '已上架': ['已下架'],
};
```

## 验证检查清单（27项）

完成后逐项检查：
```
[ ] DATA对象含20个实体，550条数据
[ ] renderTable() 渲染正常
[ ] doSearch() 过滤后重绘
[ ] openFormModal() 动态生成表单
[ ] openDetailModal() 只读展示
[ ] 新增：push后表格增加行
[ ] 编辑：修改后表格更新行
[ ] 删除：confirm + splice移除
[ ] 批量：勾选校验 + 批量操作
[ ] 分页：slice分页 + 页码切换
[ ] 导出CSV：真实下载
[ ] 审批：状态机流转
[ ] 上下架/冻结：状态切换
[ ] 遮罩点击关闭弹窗
[ ] Escape键关闭弹窗
[ ] 取消按钮关闭弹窗
[ ] 搜索后重置到第1页
[ ] 翻页后筛选条件保持
[ ] 所有data-action绑定成功
[ ] 无Toast-only mockup
```
