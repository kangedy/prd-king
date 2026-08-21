

## 🔴 某省级交通集团实战关键教训（2026-07 84页原型）

以下来自本次84页营销中心原型全流程，耗时6小时+、15次git提交、修复20+问题后总结。

### JS语法Errors的排查优先级

1. `grep -n "msg='" *.html` — 找 `msg='...'` 误写（应为 `msg:'...'`）
2. `grep -n "msg= '" *.html` — 检查 `postMessage` 里 `'*'` 是否在对象外部
3. `node --check` — 每次patch后必跑

### 并行委派上下文优化

- **不要Agent读大文件**: PRD(499KB)和Excel(95KB)会超时。主Agent预提取数据嵌入context
- **必须用绝对路径**: Agent多次搜索 `/tmp/` 和 `~/` 找不到文件
- **功能点数据格式**: `模块(点数): 子模块1(点数: 类型1×N, 类型2×N), 子模块2(...)` — 紧凑高效

### 导航下拉三重坑

| 现象 | 根因 | 修复 |
|------|------|------|
| hover不出现 | `overflow-x:auto` 裁切 | 移除overflow |
| 出现但横排 | `display:flex` 默认row | 改 `display:block` |
| 出现但点不了 | JS异常导致onclick函数undefined | 修JS语法，不修onclick |

### showForm 支持 string options

需要`<option value="0">`这种带value的选项时，options不能是数组：
```javascript
// 数组方案只生成 <option>文本</option>
// 需要value时用string: '<option value="">...</option>'
showForm中: if(typeof f.options==='string') html+=f.options;
```

### 模板创建表单对齐PRD

「新建模板」弹窗常漏 Strategy 实体的核心字段：
strategy_type(6种) / target_audience / reach_plan / execute_plan(3种) / priority

### 6步工作流模式

多步骤运营流程：`.workflow-bar`进度条 + `.step-nav`上下步 + `sessionStorage`数据传递 + `showPage`联动更新步骤状态。

### postMessage 参数位置

```javascript
// ✅ postMessage(data, targetOrigin)
window.parent.postMessage({type:'toast',msg:'ok'}, '*');
// ❌ 不能把 '*' 放对象里
```

### iframe PAGE_MODULE映射

- 每条映射必须是 `'文件名.html#子页面hash'`，不能只写文件名
- `navigate()` 直接用映射值做 `iframe.src`，不要拼接hash
- `currentPage` 初始值必须 `null`，否则首次导航被跳过

### 浏览器缓存

修改 `file://` HTML后可能缓存旧版。加 `?v=N` 参数或提醒 Ctrl+F5。
