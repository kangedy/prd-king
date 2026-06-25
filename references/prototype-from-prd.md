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

## Modal Pattern

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

## Pitfalls

- **Template literals in forEach closures**: `forEach(k => { return \`\${k}\` })` captures variable reference, not value. Use IIFE pattern: `forEach(k => { return (function(v){ return v })(k) })`
- **Modal ID conflicts**: Each page's modal needs a distinct ID. Use page-specific prefixes.
- **JS syntax validation**: Run `node -c` on all JS files before delivering
- **PRD gaps → prototype gaps**: The user will say "对比原系统发现少了很多字段". When this happens, do a second deep pass on the source system to discover: buttons (reveal sub-functions), select options (data dictionary), form labels (add/edit fields), and hidden modals. Then update BOTH the PRD and prototype together. Use a V2 supplement file pattern (pages-v2.js) to add/override pages without rewriting the entire pages.js — load it after the main pages file in index.html.
- **Page server must stay running during verification**: Use `terminal(background=true)` for `python3 -m http.server PORT`. Don't forget the server is running — it won't auto-stop.
- **Incremental prototype updates**: When the PRD goes through V1→V2→V3 iterations, update the prototype incrementally too. Use a `pages-v2.js` supplement file that OVERRIDES or ADDS page templates — load it after `pages.js` in index.html. This avoids the risk of rewriting a large working file. Each new PRD version gets a corresponding `pages-v{N}.js` supplement.
- **Delegate form page creation to sub-agents**: For large systems (50+ pages), use delegate_task to spawn parallel workers. Give each worker a specific module, the PRD field list, and design system reference. Sub-agents produce page templates in the standard PAGE_LOADERS pattern.
- **Menu entries must match page loader keys**: When adding new pages, remember to add corresponding menu entries in app.js's MENU array with matching href values — otherwise the navigation won't work.
- **Wizard反模式**: 对于字段数大于30的长表单，不要用5步Wizard（每步只露十几个字段，用户以为表单不完整）。用 **Tab面板（不超过3个Tab）**，每个Tab显示30+字段，标题标注字段数（如`基本信息（30字段）`）。提交按钮标注总字段数（如`提交（共83字段）`）。
- **子Agent更新后必须实际验证**: 子Agent声称已修复83字段但用户打开发现字段不够。原因是子Agent可能只更新了HTML结构但CSS隐藏了内容，或者步骤导航有问题。必须自己打开原型（browser或curl确认form字段数），不能轻信子Agent的self-report。

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
