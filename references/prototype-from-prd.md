# HTML Prototype Generation from PRD

When the user asks to "制作产品原型" or "输出产品原型设计" after a PRD is complete, generate a self-contained clickable HTML prototype.

## When to Use

- User says "做原型", "出原型", "产品原型设计" after PRD delivery
- User wants interactive demo before development begins

## Architecture

Single-directory deployable prototype:
```
prototype/
  index.html          — Entry, layout shell
  css/
    design-system.css — All styles (CSS variables, components)
  js/
    app.js            — Navigation, routing, modal, helpers
    pages.js          — All page templates (PAGE_LOADERS map)
```

## Design System Requirements

### CSS Variables
```css
:root {
  --primary: #2563eb;
  --success/warning/danger/info
  --gray-50..900
  --sidebar-width: 240px;
  --radius: 8px;
  --shadow-sm/md/lg
}
```

### Required Components
- **Sidebar**: Dark bg, collapsible submenus, section headers, active state
- **Header**: Sticky, breadcrumb, user avatar
- **Stats cards**: Icon + value + label + change indicator
- **Search bar**: Label + input/select rows, search + export buttons
- **Data table**: Striped, hover, status badges, action buttons
- **Modal**: Overlay, header/body/footer sections, form grids
- **Pagination**: Page info + page buttons
- **Process steps**: Horizontal step indicators with done/active states
- **Badges**: Color-coded status indicators

### Form Patterns
- `form-grid`: 2-column grid layout
- `form-grid.col-3`: 3-column for compact fields
- `form-section-title`: Section dividers in long forms
- `.required` marker for mandatory fields

## Page Structure Pattern

Each page is a function in `PAGE_LOADERS[pageName]`:

```javascript
PAGE_LOADERS['order-list'] = function() {
  const data = [[...], [...]];
  const rows = data.map(r => '<tr>...</tr>').join('');
  return '<div class="page-content">...table + modal...</div>';
};
```

### Modal Pattern — 从PRD Ch5+Ch6读取字段

**弹窗字段必须从PRD Ch5"弹窗清单"列和Ch6"弹窗清单"节提取，不要自己脑补。**

```javascript
// 从PRD弹窗清单读取字段定义后，生成对应的弹窗HTML
// 字段行格式：字段名(控件类型, 必填/选填, 选项值/范围, 校验规则)
// 示例: 任务名称(text, 必填, ≤50字) | 执行策略(select, 必填, 选项: cron/间隔/一次性)

function generateFormFields(fieldDefs) {
  // fieldDefs: "任务名称(text,必填,≤50字)|执行策略(select,必填,选项:cron/间隔/一次性)"
  // 解析后生成对应的表单HTML
}
```

**对于每个page，如果PRD Ch5的"弹窗清单"列标注了add/edit/detail，就必须创建对应的弹窗HTML。不可遗漏。**

Standard modal with form-grid inside:
```html
<div class="modal-overlay" id="xxx-modal">
  <div class="modal">
    <div class="modal-header">...</div>
    <div class="modal-body">
      <div class="form-section-title">分区标题</div>
      <div class="form-grid">...</div>
    </div>
    <div class="modal-footer">...</div>
  </div>
</div>
```

## Coverage Target

For a system PRD:
- **Dashboard**: Stats overview + process flow visualization
- **All CRUD pages**: List + search + add/edit modal (all PRD form fields)
- **Status-based pages**: Reuse pattern with different status filters
- **Settings pages**: Simpler layout (list + inline edit)
- **Report pages**: Date range + filter + data table + export button
- **Calculation nodes**: Show formula preview

## Reuse Patterns

Factory functions for status pages:
```javascript
function makeStatusPage(title, statusCode, columns, data) {
  return function() { /* generate with provided params */ };
}
PAGE_LOADERS['status-302'] = makeStatusPage('待派车', '302', cols, data);
```

Linked pages (one implementation serving multiple menu items):
```javascript
PAGE_LOADERS['vehicle-list-sales'] = PAGE_LOADERS['vehicle-list'];
```

## 基于PRD Ch5页面清单批量生成SPA原型（单文件模式）

当PRD已完成（含Ch5页面清单和Ch6功能点清单），需要从零生成完整原型时，用此模式。

### 工作流

1. **读取PRD Ch5页面清单**：提取所有 data-page、标题、布局类型、依赖实体
2. **读取PRD Ch6功能点清单**：了解每个模块的功能点范围
3. **建立内容映射**：如有现有原型内容，建立PRD data-page → 现有页面内容的映射
4. **生成SPA骨架**：4子系统树形导航 + 页面容器 + CSS设计系统 + JS导航引擎
5. **注入页面内容**：现有内容直接复用，新增页面生成含KPI+筛选+表格的完整占位页
6. **添加交互层**：data-action全局委托系统（见下文）

### 页面生成策略

| 内容来源 | 处理方式 |
|---------|---------|
| 已有原型内容 | 直接提取HTML注入对应data-page |
| PRD有但无内容 | 生成标准占位页：面包屑+KPI卡片(4个)+筛选栏(3-5字段)+数据表格(5行Mock数据)+分页+操作按钮 |
| 非本期范围 | 标注【非本期范围·待确认】但保留页面入口 |

### Mock数据规范

```
客户总量: ~2,156,389（百万级真实感）
月新增: ~58,236（日均约1,900）
会员总量: ~862,350
积分总量: ~7.85亿
所有表格5行真实Mock数据（含真实地名、人名、业务状态标签）
```

## data-action 全局交互委托系统

无需逐个按钮绑定事件的交互方案。所有按钮通过 `data-action` 属性声明行为，一个全局事件监听器处理全部交互。

### 架构

```javascript
// 唯一全局监听
document.addEventListener('click', function(e) {
  var btn = e.target.closest('[data-action]');
  if (!btn) return;
  var action = btn.dataset.action;

  if (action === 'search' || action === 'query') {
    showToast('✅ 查询完成，共返回 N 条结果');
  }
  else if (action === 'add' || action === 'create') {
    openModal(modal || 'modal-' + currentPage);
  }
  // ... 更多action处理
});
```

### data-action 枚举

| data-action | 触发操作 | 交互行为 |
|------------|---------|---------|
| search/query | 搜索/查询 | Toast显示结果数 |
| reset | 重置 | 清空筛选表单字段 |
| add/create | 新增/创建 | 打开弹窗 |
| edit | 编辑 | 打开编辑弹窗 |
| view | 查看详情 | 打开详情弹窗 |
| delete | 删除 | confirm对话框 → 行淡化 → Toast |
| submit/save | 提交/保存 | Toast成功 → 关闭弹窗 |
| export/download | 导出/下载 | Toast进度模拟 |
| approve | 审批通过 | confirm → Toast |
| reject | 驳回 | confirm → Toast |
| batch | 批量操作 | 校验勾选 → Toast |
| import | 导入 | Toast任务提交 |
| config | 配置 | 打开配置弹窗 |
| close/cancel | 关闭/取消 | 关闭弹窗 |
| deactivate/freeze/unpublish | 停用/冻结/下架 | confirm → Toast |
| activate/unfreeze/publish | 启用/解冻/上架 | Toast成功 |

### 配套Modal系统

```javascript
function openModal(id) { /* display:flex + overflow:hidden */ }
function closeModal(id) { /* display:none + overflow:auto */ }
// 遮罩点击关闭 + Escape键关闭
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal-overlay')) closeModal(e.target.id);
});
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { /* close all open modals */ }
});
```

### 批量添加data-action到按钮

**⚠️ 警告：不要依赖简单的文本匹配来批量赋值。** `+ 新建` 按钮中的"新"字可能被 `search` 规则先匹配，导致新建按钮变成搜索按钮。

正确的做法：先统计所有按钮文本分布，手动确认映射关系，用 patch 逐个精确替换。

```python
# 1. 先统计所有按钮文本
import re
buttons = re.findall(r'<button[^>]*>([^<]*)</button>', html)
from collections import Counter
print(Counter(b.strip() for b in buttons if len(b.strip()) < 20))

# 2. 逐条确认映射，用patch替换
# 不要用全局字符串替换！会误伤其他相似结构
```

操作前必须先备份：`cp file.html file.html.bak`

## 并行委派生成 iframe SPA 原型（60+页面大规模系统）

当原型超过50页，单Agent无法在超时前完成时，采用此模式。

### 适用规模
- 50-100页面、10+模块的系统原型
- 每个模块有独立子导航
- 需要多Agent并行生成

### 架构

```
母版壳 (13KB)                模块HTML (各70-94KB)
┌─────────────────┐          ┌──────────────────────┐
│ 侧栏导航(12菜单) │  iframe→ │ campaign.html (25页)  │
│ 面包屑           │          │ ai.html (17页)        │
│ Toast/Modal      │  iframe→ │ merchant.html (24页)  │
│ 全局交互委托     │          │ settlement.html (18页)│
└─────────────────┘          └──────────────────────┘
```

### 工作流

1. **Phase 1: 母版壳** — 由主Agent生成，包含设计系统CSS + 完整侧栏菜单树 + `PAGE_MODULE`映射 + `navigate()`函数 + Toast/Modal/Confirm全局组件
2. **Phase 2: 并行生成模块HTML** — 3个Agent按场景分组，每个生成一个独立HTML文件。context中预嵌入CSS、功能点数据、页面清单（避免Agent读大文件超时）
3. **Phase 3: 补充模块** — 1个Agent处理剩余模块（总Agent数=4，分2批）
4. **Phase 4: 验证修复** — 检查所有`PAGE_MODULE`映射的hash是否与iframe内`id="page-xxx"`匹配，修复nav CSS问题

### 母版壳核心代码

```javascript
var PAGE_MODULE = {
  'dashboard': 'module_settlement.html#dashboard',
  'campaign': 'module_campaign.html#campaign-list',
  // 每个映射包含 文件名 + #子页面hash
};
var currentPage = null; // 必须null，不能是已有值
function navigate(page, label) {
  if (page === currentPage) return;
  currentPage = page;
  document.getElementById('contentFrame').src = PAGE_MODULE[page];
}
```

### 每个子Agent的context必须包含
- 完整CSS（已压缩的一行版，~2KB）
- 功能点数据（预提取的模块-子模块-类型分布，避免Agent读Excel超时）
- 页面清单（data-page名、标题、KPI指标、表格列）
- Mock数据规范
- 交互模式（data-action枚举 + postMessage Toast）
- 输出文件名

### JS Code Generation Pitfalls (tripped multiple times)

### ❌ `msg='...'` instead of `msg:'...'` in object literals
When generating `postMessage({type:'toast',msg:'text'},'*')`, agents occasionally write `msg='text'` (equals) instead of `msg:'text'` (colon). This produces "Invalid shorthand property initializer" and silently kills the entire script block. ALL functions defined after the error are unreachable.
**Fix:** Always verify JS syntax with `node --check` after any patch to `<script>` content.

### ❌ `showPage` undefined because of earlier JS error
When the `<script>` block has ANY syntax error, `showPage` becomes undefined even though it's defined later in the same block. All `onclick="showPage('...')"` buttons silently fail.
**Fix:** Fix the root JS error first. Don't patch individual onclick attributes.

## CSS Pitfalls

### ❌ `overflow-x:auto` on nav bars clips absolute dropdowns
CSS spec: setting one overflow axis to non-visible forces the other axis to auto too. A `.nav-bar{overflow-x:auto}` will clip `position:absolute` dropdowns.
**Fix:** Remove `overflow-x:auto` from nav bars.

### ❌ `display:flex` on dropdown container makes links horizontal
`nav .nav-group:hover .nav-dropdown{display:flex}` makes child elements layout in a row. Links must be `display:block`.
**Fix:** Use `display:block` for dropdown containers.

## Patch Tool Quirks

### ❌ `patch` double-escapes backslash-quote sequences
When using `patch` with strings containing `\"`, the tool writes `\\\"`. Breaks JS inside `<script>` tags.
**Fix:** Use `String.fromCharCode(34)` instead of `\"` in patch strings.

## Interactive Pattern Preference

### ✅ Real modals > Toast notifications
User rejects Toast-only button handlers. Every button must open a modal, navigate, or confirm — not just `showToast()`.

## Pitfalls
- **context中不要要求Agent读大文件**（PRD/Excel），会导致超时。预提取数据嵌入context
- **子Agent生成的HTML如果自带导航栏，CSS中不要有 `overflow-x:auto`**（裁切下拉菜单）
- **母版壳的 `navigate()` 直接用 `PAGE_MODULE[page]` 做 `iframe.src`**，不要拼接hash
- **首次加载 `currentPage` 必须 `null`**，否则初始导航被跳过

当原型有40+占位页需要填充时，按子系统拆分为3个并行子Agent，每Agent处理约20-30页。

每个子Agent的context需包含：
- 原型文件路径
- 需填充的data-page列表
- 页面HTML模板规范（面包屑+KPI+筛选+表格+分页+按钮）
- Mock数据规范
- 操作方式：直接patch原型HTML文件（禁止curl/HTTP请求）

### 页面模板规范（每页必备）

```
✅ 面包屑导航（子系统 > 模块 > 页面）
✅ 页面标题 + 业务描述（1-2句）
✅ KPI卡片（4个，含业务相关数字和趋势）
✅ 筛选条件栏（3-5个筛选字段）
✅ 数据表格（5-8列，5行真实Mock数据）
✅ 操作按钮（查询/重置/新增/导出，带data-action属性）
✅ 分页组件
```

## 数据驱动CRUD交互层（从Toast模拟到真实操作）

当原型从静态展示升级为可交互Demo时，需要将Toast模拟替换为真实的数据操作。此模式适用于91+页、700+按钮的大规模SPA原型。

### 架构：三层分离

```
数据层 (DATA) → 逻辑层 (CRUD Functions) → 渲染层 (Table/Modal/Form)
```

### 第1层：Mock数据注入

```javascript
// 550条数据，20个实体，直接注入HTML <script> 标签
var DATA = {
  customers: [ /* 30条：姓名/电话/车牌/等级/来源 */ ],
  // ...
};
```

**数据规范：**
- 真实中文名（百家姓含复姓）
- 湖南车牌（湘A-N/U 14个前缀）
- 1xx手机号段（30+号段）
- 时间在近6个月内
- 金额/数量有业务真实感

### 🔴 枚举字段options提取（从PRD Ch7到ENTITY_COLUMNS）

**这是PRD→原型生成中最常断的链路。** PRD Ch7数据模型为每个enum字段列出了选项值（如 `silver/gold/diamond`），但生成ENTITY_COLUMNS时经常丢失。

**正确流程：**

```javascript
// PRD Ch7 原文：
// | member_level | enum | Y | silver/gold/diamond | Tag | — |
// | status | enum | Y | potential/normal/active/dormant/cancelled | Tag | — |

// ENTITY_COLUMNS 必须包含options（中文，用户可见）：
var ENTITY_COLUMNS = {
  members: [
    {key:'member_level', label:'会员等级', format:levelTag, 
     options:['普通','银卡','金卡','钻石']},  // ← 必须有options
    {key:'status', label:'状态', format:statusTag,
     options:['正常','冻结','注销']},         // ← 必须有options
  ],
};
```

**提取规则：**
1. PRD Ch7的"选项/范围"列列出了所有enum可选值 → 提取为options数组
2. **值必须用中文**（PRD可能用英文代码，原型中必须转中文）
3. 对应关系：
   - `silver/gold/diamond` → `['普通','银卡','金卡','钻石']`
   - `potential/normal/active/dormant/cancelled` → `['准客户','正式客户','活跃','休眠','注销']`
   - `draft/pending_approval/approved/enabled/disabled/ended` → `['草稿','待审批','已审批','已启用','已停用','已结束']`
4. `getEntityFields` 函数自动检测 `options` 字段，将type设为`'select'`并渲染为下拉菜单

**getEntityFields的正确实现：**

```javascript
function getEntityFields(entity) {
  var cols = ENTITY_COLUMNS[entity] || [];
  return cols.map(function(c) {
    var f = { key: c.key, label: c.label, type: 'text', required: false };
    // 如果有选项列表，设为select
    if (c.options && c.options.length > 0) {
      f.type = 'select';
      f.options = c.options;
    }
    // 数字类型
    else if (/* 数字字段名匹配 */) {
      f.type = 'number';
    }
    // 长文本
    else if (/* 文本字段名匹配 */) {
      f.type = 'textarea';
    }
    f.required = (c.key === 'name');
    return f;
  });
}
```

**检查清单（生成完成后必须验证）：**
- [ ] ENTITY_COLUMNS 中每个enum字段都有options数组
- [ ] options值用中文（用户可见）
- [ ] getEntityFields能正确检测options并设type='select'
- [ ] openFormModal能渲染select下拉菜单

### 第2层：CRUD函数（7个模块）

```javascript
// 1. 表格渲染器
function renderTable(tableSelector, data, columns) {
  // tableSelector: 目标表格的CSS选择器
  // data: 数据数组（已分页）
  // columns: [{key, label, format: fn}] 列定义
  // 清空tbody → 遍历data生成tr → 添加操作按钮列
}

// 2. 搜索/筛选
function doSearch(entity, filterSelector, tableSelector, columns) {
  // 从filterSelector区的input/select取值
  // 对DATA[entity]做模糊匹配过滤
  // 调用renderTable渲染
}

// 3. 弹窗系统（动态生成）
function openFormModal(title, fields, data, onSave) {
  // fields: [{key, label, type, options, required}]
  // data: 编辑时预填，新增时null
  // 生成modal DOM → append到body → 显示
}
function openDetailModal(title, data, fields) {
  // 只读表格展示所有字段
}

// 4. CRUD操作
// 新增：DATA[entity].push(newRecord) → renderTable
// 编辑：DATA[entity].findIndex() → splice更新 → renderTable
// 删除：confirm → DATA[entity].splice(idx,1) → renderTable
// 批量：confirm → 遍历checked → filter排除 → renderTable

// 5. 分页
function paginateData(data, page, pageSize) {
  // slice((page-1)*pageSize, page*pageSize)
  // 返回 {items, total, totalPages, page}
}

// 6. 导出CSV
function exportCSV(data, columns, filename) {
  // 生成CSV字符串（UTF-8 BOM）
  // Blob → a.click() 触发下载
}

// 7. 状态流转
var STATUS_TRANSITIONS = {
  '待审批': ['已通过', '已驳回'],
  '草稿': ['已上架'],
  '已上架': ['已下架'],
  '已下架': ['已上架'],
  '正常': ['观察期', '暂停合作'],
  '暂停合作': ['正常', '已退出'],
};
function transitionStatus(entity, id, newStatus) {
  // 校验流转合法性
  // 更新状态字段
  // renderTable
}
```

### 第3层：页面-实体映射

建立19+个关键页面的实体映射关系，使表格渲染器能自动匹配：

```javascript
var PAGE_ENTITY_MAP = {
  'khzx-customer-list': 'customers',
  'khzx-user-list': 'users',
  'hyzx-member-list': 'members',
  'yxzx-product-list': 'products',
  'yxzx-coupon-list': 'coupons',
  'khsj-collect': 'dataSources',
  // ... 共19个映射
};
```

### 部署流程

```
Step 1: 生成Mock数据（2子Agent并行，各300+条）→ 550条
Step 2: 注入数据到HTML <script>（文件增大120KB+）
Step 3: 追加CRUD函数（7模块，~700行JS）
Step 4: 全局验证（27项检查：渲染/搜索/弹窗/CRUD/分页/导出/审批）
```

### 注意事项

- **数据与页面解耦**：DATA数组独立维护，页面只读DATA不修改结构
- **操作后重绘**：每次CUD操作后必须调用renderTable刷新视图
- **字段名对齐**：数据字段名必须与CRUD代码中引用的字段名完全一致（常见bug）
- **分页与搜索联动**：搜索后重置到第1页，分页后保持筛选条件
- **弹窗ID冲突**：每个页面生成弹窗时使用 `'modal-' + currentPage` 确保唯一
- **状态流转校验**：不允许非法流转（如"草稿"→"已通过"），用STATUS_TRANSITIONS白名单控制

## 原型交互按钮审计与串联工作流

当原型页面基本生成后，需要系统审计所有交互按钮并串联到正确的页面/弹窗。此工作流经历实战验证（84页原型、~200+按钮）。

### Step 1: 提取所有交互按钮

```bash
grep -n 'onclick\|data-action' prototype.html | grep -v 'showPage\|navigate\|void(0)' | head -50
```

### Step 2: 分类按钮行为

| 类别 | 特征 | 修复方案 |
|------|------|---------|
| 页面跳转 | `showPage('xxx')` 或应跳转 | 改 `data-action` → `onclick="showPage('xxx')"` |
| 打开弹窗 | `openModal('xxx')` 或应弹窗 | 添弹窗HTML + 改 `data-action` → `onclick` |
| Toast反馈 | `data-action="search/edit/submit"` | 已有全局handler → 保持 |
| 无行为 | 无onclick/data-action | 补充对应行为 |

### Step 3: 优先级修复

1. **P0 阻断**: 审批「通过/驳回」→ 打开确认弹窗（含回调逻辑）
2. **P1 高优**: 页面跳转类按钮（「新建」「查看详情」「提交审批」→对应页）
3. **P2 体验**: Toast反馈类已有全局handler → 无需改

### Step 4: 验证清单

- [ ] `node --check` 验证JS语法（尤其检查 `msg='...'` vs `msg:'...'`）
- [ ] 弹窗的 `openModal`/`closeModal` 函数存在且ID匹配
- [ ] 跳转目标 `page-xxx` 的 `<div>` 确实存在
- [ ] 审批弹窗的确认回调包含状态变更逻辑

修改单文件HTML原型后，必须运行此验证，否则CSS损坏会导致用户看到"排版好了但样式有问题"。

```python
import re
with open('prototype.html') as f:
    content = f.read()

# 1. 提取CSS
css_match = re.search(r'<style>([\s\S]*?)</style>', content)
css = css_match.group(1) if css_match else ''

# 2. 提取HTML中使用的所有class名
html_classes = set()
for m in re.finditer(r'class="([\w\s-]+)"', content):
    for cls in m.group(1).split():
        html_classes.add(cls)

# 3. 提取CSS中定义的所有class名
css_classes = set(re.findall(r'\.([\w-]+)\s*\{', css))

# 4. 找缺失的类
missing = html_classes - css_classes
common = {'btn','card','tag','link-btn','required',
          'page-section','subsystem-pages','page-content'}
missing -= common
if missing:
    print(f'❌ HTML使用但CSS未定义的类: {missing}')

# 5. 检查CSS花括号平衡
opens = css.count('{')
closes = css.count('}')
if opens != closes:
    print(f'❌ CSS花括号不平衡: {opens}开 {closes}闭')

# 6. 检查CSS中是否有JSON数据混入（典型的{key:开头）
json_lines = [l for l in css.split('\n') if "key:" in l or "label:" in l]
if json_lines:
    print(f'❌ CSS中混入了JSON数据: {len(json_lines)}行')

# 7. 检查关键CSS是否在@media内部意外生效
media_depth = 0
for line in css.split('\n'):
    if '@media' in line: media_depth += 1
    if line.strip() == '}': media_depth = max(0, media_depth - 1)
    # 检查常用样式是否意外在media内
```

**关键检查项（手动）：**
- [ ] `.kpi-grid` 不在 `@media` 内部（除非故意窄屏）
- [ ] `.page-content` 有 `padding` 定义
- [ ] `.btn`, `.card`, `.tag` 等基础组件样式完整
- [ ] CSS中无 `{key:` 或 `label:` 开头的JSON数据行
- [ ] `section`/`div` 标签开闭平衡：`content.count('<section') == content.count('</section')`

## JS Code Generation Pitfalls (tripped multiple times)

### ❌ `msg='...'` instead of `msg:'...'` in object literals
When generating `postMessage({type:'toast',msg:'text'},'*')`, agents occasionally write `msg='text'` (equals) instead of `msg:'text'` (colon). This produces "Invalid shorthand property initializer" and silently kills the entire script block. ALL functions defined after the error are unreachable.
**Fix:** Always verify JS syntax with `node --check` after any patch to `<script>` content.

### ❌ `showPage` undefined because of earlier JS error
When the `<script>` block has ANY syntax error, `showPage` becomes undefined even though it's defined later in the same block. All `onclick="showPage('...')"` buttons silently fail.
**Fix:** Fix the root JS error first. Don't patch individual onclick attributes.

## CSS Pitfalls

### ❌ `overflow-x:auto` on nav bars clips absolute dropdowns
CSS spec: setting one overflow axis to non-visible forces the other axis to auto too. A `.nav-bar{overflow-x:auto}` will clip `position:absolute` dropdowns.
**Fix:** Remove `overflow-x:auto` from nav bars.

### ❌ `display:flex` on dropdown container makes links horizontal
`nav .nav-group:hover .nav-dropdown{display:flex}` makes child elements layout in a row. Links must be `display:block`.
**Fix:** Use `display:block` for dropdown containers.

## Patch Tool Quirks

### ❌ `patch` double-escapes backslash-quote sequences
When using `patch` with strings containing `\"`, the tool writes `\\\"`. Breaks JS inside `<script>` tags.
**Fix:** Use `String.fromCharCode(34)` instead of `\"` in patch strings.

## Interactive Pattern Preference

### ✅ Real modals > Toast notifications
User rejects Toast-only button handlers. Every button must open a modal, navigate, or confirm — not just `showToast()`.

## Pitfalls

- **🔴 必须git init或备份后再修改**: 修改原型文件前先 `git init && git add file && git commit -m "before"` 或 `cp file file.bak`。没有备份直接用replace_all或批量修改HTML会导致大面积损坏且无法恢复。禁止在非git仓库中直接修改大文件HTML。
- **🔴 修改CSS前必须检查其作用域**: CSS选择器可能被包裹在 `@media`、`:not()` 等条件块内部。修改前搜索该选择器在文件中的完整上下文，确认它是全局规则还是条件规则。曾有.kpi-grid定义在@media内导致宽屏不生效，排查了4轮才发现。**不要只看选择器本身，要看到它的包裹块。**
- **🔴 不要用str.replace()修改混合HTML文件中的JSON/数据**: 当文件包含 `<style>CSS</style><script>DATA</script><body>HTML</body>` 混合内容时，一个 `str.replace()` 可能跨区匹配，将JSON数据行注入CSS区，破坏CSS语法。正确做法：用 `patch` 工具+精确上下文行，或先提取目标区域再替换。如果必须用 `str.replace()`，先验证替换字符串在文件中只有一个匹配：`assert content.count(target) == 1`。
- **🔴 Toast-only mockup is NEVER acceptable**: When the user says to supplement or complete or interactivity, they mean REAL data operations. If you only add showToast calls, the user will call it out and you will have to redo everything.
- **🔴 修改ENTITY_COLUMNS后必须验证所有实体的完整性**: 用`str.replace()`或`patch`修改ENTITY_COLUMNS时，可能截断相邻的实体定义（一个实体的逗号/花括号被吞掉）。症状：某个页面的"新建"弹窗字段不全。**修复后必须验证每个实体以`],`或`],\n`正确结束**。Python验证:`python3 -c "import re; c=open('f.html').read(); s=re.search(r'var ENTITY_COLUMNS = \{([\\s\\S]*?)\};',c); [print(f'❌ {e}') for e in re.findall(r'(\\w+):\\s*\\[[^\\]]*$(?!,)', s.group(1))]"` 应输出空。
- **Template literals in forEach closures**: `forEach(k => { return \`\${k}\` })` captures variable reference, not value. Use IIFE pattern: `forEach(k => { return (function(v){ return v })(k) })`
- **Modal ID conflicts**: Each page's modal needs a distinct ID. Use page-specific prefixes.
- **🔴 生成原型后必须 node --check 验证JS语法**: 子Agent生成的HTML可能含JS语法错误——最常见的是对象字面量中 `msg='...'` 误写为等号而非冒号 `msg:'...'`（肉眼难辨但 `node --check` 秒报），会导致整个 `<script>` 块崩溃、`showPage` 等核心函数 `undefined`，使全部按钮失效。**验证流程**: `python3 -c "import re;m=re.search(r'<script>(.*?)</script>',open('f.html').read(),re.DOTALL);open('/tmp/js.js','w').write(m.group(1))" && node --check /tmp/js.js`。此bug曾导致84页原型全部按钮失效，排查4轮才发现根因。
- **PRD gaps → prototype gaps**: The user will say "对比原系统发现少了很多字段". When this happens, do a second deep pass on the source system to discover: buttons (reveal sub-functions), select options (data dictionary), form labels (add/edit fields), and hidden modals. Then update BOTH the PRD and prototype together. Use a V2 supplement file pattern (pages-v2.js) to add/override pages without rewriting the entire pages.js — load it after the main pages file in index.html.
- **🔴 overflow-x:auto 会裁切 position:absolute 的下拉菜单**: CSS规范中设置 `overflow-x:auto` 会强制 `overflow-y` 也为 `auto`，导致导航栏内 `position:absolute;top:100%` 的下拉菜单被裁切。hover展开后看不到菜单项。修复：移除 `overflow-x:auto`，或显式设置 `overflow-y:visible`。
- **🔴 导航下拉用 display:block 不要用 display:flex**: 下拉菜单子项是 `display:block` 竖排链接，父容器若设 `display:flex`（默认 `flex-direction:row`），会导致所有子项横排挤压。统一使用 `display:block`。修改CSS display属性时必须连带检查子元素排列方向。 Use a `pages-v2.js` supplement file that OVERRIDES or ADDS page templates — load it after `pages.js` in index.html. This avoids the risk of rewriting a large working file. Each new PRD version gets a corresponding `pages-v{N}.js` supplement.
- **Delegate form page creation to sub-agents**: For large systems (50+ pages), use delegate_task to spawn parallel workers. Give each worker a specific module, the PRD field list, and design system reference. Sub-agents produce page templates in the standard PAGE_LOADERS pattern.
- **Menu entries must match page loader keys**: When adding new pages, remember to add corresponding menu entries in app.js's MENU array with matching href values — otherwise the navigation won't work.
- **Wizard反模式**: 对于字段数大于30的长表单，不要用5步Wizard（每步只露十几个字段，用户以为表单不完整）。用 **Tab面板（不超过3个Tab）**，每个Tab显示30+字段，标题标注字段数（如`基本信息（30字段）`）。提交按钮标注总字段数（如`提交（共83字段）`）。
- **子Agent更新后必须实际验证**: 子Agent声称已修复83字段但用户打开发现字段不够。原因是子Agent可能只更新了HTML结构但CSS隐藏了内容，或者步骤导航有问题。必须自己打开原型（browser或curl确认form字段数），不能轻信子Agent的self-report。
- **🔴 `overflow-x:auto` 会裁切绝对定位下拉菜单**: CSS规范中，当 `overflow-x` 设为 `auto`/`scroll`/`hidden` 时，`overflow-y` 被强制变为 `auto`（即使不显式设置）。导致 `.nav-bar` 内的 `position:absolute` 下拉菜单被裁切不可见。**修复**: 从包含绝对定位子元素的容器上移除 `overflow-x:auto`。症状：hover下拉菜单不出现，但HTML结构和CSS选择器看起来都正确。

- **🔴 PRD Ch7数据模型 → 原型表格列的对照补齐**: 原型生成后常漏PRD中定义的字段。用 `grep -n '字段名\|Ch7' prd.md` 提取每个实体的字段表，再 `grep 'columnheader' prototype.html` 对比原型表头列。缺的字段用 `patch` 直接追加 `<th>` 和对应的 `<td>`。尤其注意：(a) enum字段的选项值要完整列出（6种标签类型、6种策略类型等）；(b) 画布节点的类型必须对齐PRD的9种（START/DATA_SOURCE/FILTER/JUDGMENT/WAIT/AB_TEST/POLICY/REACH/END）；(c) 时间字段（created_at/updated_at/approved_at等）常被遗漏。
- **iframe SPA中PAGE_MODULE必须带子页面hash**: 母版壳通过iframe加载模块HTML时，`PAGE_MODULE`映射必须包含精确的子页面hash（如 `'prototype_marketing_campaign.html#campaign-list'`），不能只用模块文件名。同时 `navigate()` 函数必须直接使用映射值作为 `iframe.src`，不可再拼接 `'#' + page` 导致双重hash。另外，首次加载时 `currentPage` 初始值应设为 `null`（非 `'dashboard'`），否则初始导航被 `if (page === currentPage) return` 跳过。
- **导航下拉交互三态**: 原型中的模块内导航有三种交互模式可选——(a) 纯CSS hover展开（`nav-group:hover .nav-dropdown{display:block}`），最简单但对移动端不友好；(b) 纯JS点击手风琴（click→toggle open class），一次只展开一个，点空白处收起；(c) hover+click混合（hover展开 + click锁定），桌面端hover即出、点击固定。三者的CSS和JS差异仅在一行 `:hover` 规则和几行事件监听。选择哪种取决于用户偏好，但都依赖 `position:absolute` + `z-index` 高于父容器。

**推荐做法**：最简方案是纯CSS hover展开，下拉项用 `<span onclick="showPage('xxx')">` 而非 `<a href="#">`——消除`<a>`标签的浏览器默认导航行为干扰，同时避免JS事件监听器与inline onclick冲突。不要同时挂click事件监听器和onclick属性，二者会在同一个span上竞争触发，导致点击无效或双击才响应。

- **🔴 `display:flex` 会让下拉菜单竖排变横排**: 下拉菜单容器（`.nav-dropdown`）的hover/open规则若用 `display:flex`，默认`flex-direction:row`导致子项全部横排挤压。正确写法用 `display:block`，因为下拉项本身就是 `display:block` 竖排。修改CSS时不能只看"能不能显示"，要连带确认子元素的排列方向。

- **🔴 下拉菜单点击无效的终极方案**: 当hover正常展开但点击下拉项无反应时，不要反复尝试不同的`<a>`标签变体（`href="#"`/`href="javascript:void(0)"`/`onclick`），这些都受浏览器默认行为和JS作用域影响。按此三步走：(1) 先用 `browser_console` 检查 `typeof window.showPage` 是否为 `undefined`——如果是，说明JS有异常导致函数未注册到全局，不要在标签属性上浪费精力；(2) 用 `browser_console` 直接执行一次内联DOM操作验证逻辑正确：`document.querySelectorAll('.page').forEach(e=>e.classList.remove('active')); document.getElementById('page-campaign-plan').classList.add('active')`；(3) 如果步骤2有效，将所有 `onclick="showPage('xxx')"` 替换为内联DOM操作 `onclick="var d=document;d.querySelectorAll('.page').forEach(function(e){e.classList.remove('active')});var t=d.getElementById('page-xxx');if(t)t.classList.add('active')"`——零依赖、零作用域问题，必然可用。文件中有2个JS异常但排查成本高时，这个是最高效的兜底方案。

**推荐做法**：最简方案是纯CSS hover展开，下拉项用 `<span onclick="showPage('xxx')">` 而非 `<a href="#">`——消除`<a>`标签的浏览器默认导航行为干扰，同时避免JS事件监听器与inline onclick冲突。不要同时挂click事件监听器和onclick属性，二者会在同一个span上竞争触发，导致点击无效或双击才响应。

- **🔴 `display:flex` 会让下拉菜单竖排变横排**: 下拉菜单容器（`.nav-dropdown`）的hover/open规则若用 `display:flex`，默认`flex-direction:row`导致子项全部横排挤压。正确写法用 `display:block`，因为下拉项本身就是 `display:block` 竖排。修改CSS时不能只看"能不能显示"，要连带确认子元素的排列方向。

- **🔴 下拉菜单点击无效的排查顺序**: (1) `node --check` 验证JS语法→修 `msg=` 改 `msg:`；(2) `browser_console` 检查 `typeof showPage`；(3) 改 `<a href="#">` 为 `<span onclick="showPage('xxx')">`；(4) 兜底：内联DOM操作。不要同时挂click事件监听器和onclick属性。

## 逐字段校验工作流（V5新增）

当原型经过多轮迭代后，需要逐字段验证与PRD的一致性。使用**五路并行Agent校验法**：

### 校验部署

将全部模块按业务域分成5组，每组委派一个QA子Agent：

```
Agent 1: 回收域（订单/车辆/商务部/客户）
Agent 2: 厂区域（状态页/称重/查验/拆解/存放）
Agent 3: 生产域+仓储域（质检/拆解/入库/出库/库存/盘点）
Agent 4: 结算域+设置域（结算/导出/价格/基础资料）
Agent 5: 报表域（所有报表页）
```

### 每个Agent的执行流程

1. **read_file** 读取PRD对应章节，提取字段清单
2. **read_file** 读取原型对应PAGE_LOADERS
3. 逐字段对比：PRD字段 → 原型中是否有对应 `name="xxx"`
4. 发现缺失 → 直接用 **patch** 修复
5. 报告：哪些字段原来缺失、已补充

### Context要点

传给子Agent的context必须包含：
- PRD文件路径和对应行号范围
- 原型文件路径和PAGE_LOADER名称
- 具体字段名清单（不要指望子Agent自己提取）
- patch修复指令

### 验证收口

主Agent在全部子Agent完成后执行：
```bash
node -c js/pages.js js/pages-v2.js   # 语法检查
grep -c 'name="' js/pages.js          # 字段计数
```

**坑：** 子Agent可能因外网请求被拦截而超时。在context中明确禁止curl/HTTP请求，只允许 read_file + search_files + patch。
