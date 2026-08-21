# iframe SPA 大规模原型工作流（60+页面）

## 适用场景
- 50-100页面、10+模块的系统原型
- 需要多Agent并行生成
- 最终交付单文件母版壳 + 4-5个模块HTML

## 架构

```
母版壳 (13KB)              模块HTML (各70-94KB)
┌─────────────────┐        ┌──────────────────────┐
│ 侧栏导航(12菜单) │ iframe→│ module_1.html (22+页) │
│ 面包屑           │        │ module_2.html (17+页) │
│ Toast/Modal      │ iframe→│ module_3.html (24+页) │
│ 全局交互委托     │        │ module_4.html (18+页) │
└─────────────────┘        └──────────────────────┘
```

## 四阶段执行

### Phase 1: 母版壳（主Agent）
输出一个约13KB的HTML，包含：
- 完整CSS设计系统（Ant Design 5.x 变量）
- 侧栏导航菜单（全部一级模块）
- `PAGE_MODULE` 映射表（模块文件名 + `#子页面hash`）
- `navigate()` 路由函数
- Toast / Modal / Confirm 全局组件

关键代码：
```javascript
var PAGE_MODULE = {
  'dashboard': 'module_settlement.html#dashboard',
  'campaign': 'module_campaign.html#campaign-list',
  // 每个映射: 文件名 + #子页面hash
};
var currentPage = null; // 必须null，不能是已有值
function navigate(page, label) {
  if (page === currentPage) return;
  currentPage = page;
  document.getElementById('contentFrame').src = PAGE_MODULE[page];
}
```

验证清单：
- [ ] `currentPage` 初始值为 `null`（非 `'dashboard'`）
- [ ] `navigate()` 直接用 `PAGE_MODULE[page]` 做 `iframe.src`，不拼接hash
- [ ] 所有菜单项在 `PAGE_MODULE` 中有对应映射
- [ ] 每个映射的hash与iframe内 `id="page-xxx"` 精确匹配

### Phase 2: 并行生成模块HTML（3 Agent）
每个子Agent的context必须**预嵌入**以下数据（避免Agent读大文件超时）：
- 完整CSS（压缩版 ~2KB）
- 功能点数据（模块→子模块→功能点类型分布）
- 页面清单（data-page名、标题、KPI指标、表格列定义）
- Mock数据规范（真实业务命名）
- 交互模式（data-action枚举 + postMessage Toast）
- 输出文件路径

context中禁止要求Agent读取PRD或Excel文件。

### Phase 3: 补充模块（1 Agent）
剩余模块由单Agent处理。

### Phase 4: 验证与修复
1. 逐菜单验证 `PAGE_MODULE` hash匹配
2. 检查模块HTML内导航CSS（无 `overflow-x:auto` 裁切问题）
3. 检查 `display` 属性（flex→block）
4. 验证iframe内页面切换可用
5. `git add -A && git commit` 存档

## 每个模块HTML的要求

### 页面模板（每页必备）
- 面包屑导航
- 页面标题 + 业务描述（1-2句）
- KPI卡片（3-4个，真实业务数字）
- 筛选条件栏（3-5字段）
- 数据表格（5-7列，5行Mock数据）
- 操作按钮（查询/重置/新增/导出/编辑/删除，带data-action）
- 分页组件

### 交互规范
- 所有按钮带 `data-action` 属性
- 查询/搜索: Toast反馈（`window.parent.postMessage`）
- 新增/编辑: 弹窗modal
- 删除/审批: confirm对话框
- Modal遮罩点击关闭 + Escape关闭
- 导航下拉: 纯CSS hover展开，`<span onclick="...">` 点击跳转

## 常见错误速查

| 症状 | 根因 | 修复 |
|------|------|------|
| 侧栏点击无反应 | `currentPage`初始值导致首次导航被跳过 | `var currentPage = null` |
| 侧栏点开但页面不对 | `navigate()`在映射值后又拼了`'#'+page` | 直接用`PAGE_MODULE[page]`做src |
| 模块内导航hover不出现 | 父容器有`overflow-x:auto`裁切下拉 | 移除`overflow-x:auto` |
| 下拉菜单横排挤压 | `display:flex`默认`flex-direction:row` | 改为`display:block` |
| 下拉展开但点击无效 | `<a>`标签+JS事件监听器冲突 | 改为`<span onclick="...">` |
| onclick函数未定义 | JS有异常导致函数未注册全局 | 改用内联DOM操作 |
