# Iframe SPA 原型集成方法（Base64嵌入架构）

当目标原型使用 iframe + base64 嵌入架构（而非 PAGE_LOADERS SPA）时，集成新页面需要理解其架构并做4点patch。

## 架构识别

特征：
- 一个壳 HTML 文件，内部 JS 包含 `embeddedSources` 对象（key=中心名, value=base64编码的HTML）
- 导航通过 JS 动态生成（`renderNavigation()` 函数）
- 页面切换通过 `buildEmbeddedDocument()` 加载对应 base64 源
- 每个 base64 源内部有自己的页面切换逻辑

典型结构：
```javascript
const embeddedSources = {
  "customer": "base64...",
  "data": "base64...",
  "marketing": "base64...",
  "member": "base64..."
};
```

## 4点 Patch 集成法

将新页面（通常是一个独立的 HTML 文件，含多个 section.page）集成到现有 iframe 原型中：

### Patch 1: 添加 base64 嵌入源

将新页面 HTML 文件 base64 编码后，添加到 `embeddedSources` 对象：

```python
import base64
with open('new_pages.html', 'r', encoding='utf-8') as f:
    html = f.read()
b64 = base64.b64encode(html.encode('utf-8')).decode('utf-8')

# 在 embeddedSources 中添加新源
# 找到 member 源位置，在其后插入 "customer-ext": "{b64}"
```

注意：需要在 `embeddedSources` 对象中找到一个已有源（如 `member`）在其后插入，保持 JSON 结构有效。

### Patch 2: 更新导航分组（centerSections）

找到 `function centerSections(center)`，为对应中心添加新导航分组：

```javascript
function centerSections(center) {
  if (center.sections) return center.sections;
  if (center.id === "customer") {
    return [
      // ... 原始分组 ...
      ["新分组名称", ["new-page-1", "new-page-2", "new-page-3"]],
      // ... 更多新分组 ...
    ].map(([title, routes]) => ({
      title,
      items: routes.map(route => center.items.find(item => item[0] === route)).filter(Boolean)
    }));
  }
  // ... 其他中心 ...
}
```

### Patch 3: 添加路由到 items 数组

在对应中心的 `items` 数组中追加新路由条目（`[routeId, "显示名称"]` 格式）：

```javascript
// 在 customer 的 items 中找到最后一个条目，在其后追加
["crowds", "客户细分配置"],
["event-list","事件时机管理"],
["event-create","创建事件时机"],
// ... 所有新路由 ...
["acct-detail","账户详情"],
```

### Patch 4: 更新路由分发（buildEmbeddedDocument）

在 `buildEmbeddedDocument` 函数中，添加路由到新源的分发逻辑：

```javascript
// 创建新路由的 Set
const newRoutes = new Set(["route1", "route2", ...]);

const sourceCenterId = center.id === "customer" && newRoutes.has(embeddedRoute)
  ? "customer-ext"  // 新源名称
  : /* 原始路由逻辑 */;
```

## 验证清单

Patch 完成后验证以下 10 项：

1. ✅ `embeddedSources` 包含新源（key 和 base64 值完整）
2. ✅ `centerSections` 包含所有新分组
3. ✅ 对应中心的 `items` 数组包含所有新路由
4. ✅ `buildEmbeddedDocument` 中新源的路由分发逻辑正确
5. ✅ 原始中心的菜单和内容未丢失
6. ✅ 所有一级中心按钮（5个）正常
7. ✅ 新页面路由可在导航中点击
8. ✅ system 中心通过委托机制可正常加载（如适用）
9. ✅ 文件中所有 HTML 标签平衡（section数、div数匹配）
10. ✅ 文件大小合理（base64 编码约增大 1.37 倍）

## 常见陷阱

- ❌ **system源不在embeddedSources外层**：system 中心可能通过 `systemDelegatedMarketingRoutes` 委托到 marketing 源，这是设计决策，不要修复
- ❌ **导航中未添加新分组**：只加 base64 源不加导航分组会导致页面虽嵌入但用户找不到
- ❌ **items 数组未更新**：`centerSections` 通过 `center.items` 查找路由，如果 items 中没有新路由，导航分组会显示空
- ❌ **base64 格式错误**：base64 字符串中不能有换行，Python 的 `b64encode()` 输出需确保是单行
- ✅ **大文件base64性能可接受**：400KB base64（约300KB原始HTML）对现代浏览器无压力

## 案例数据

某省级交通集团客户中心项目实战：
- 原始原型：11.9MB（含5个base64源 + JS架构）
- 新增页面：49页，295KB HTML → 402KB base64
- Patch 耗时：约5分钟（含验证）
- 验证通过率：10/10 项全部通过
