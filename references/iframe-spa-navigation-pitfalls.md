# iframe SPA 原型导航陷阱与修复

## 场景
大规模多模块原型使用 iframe SPA 架构：母版壳(侧栏+Header+iframe) + N个模块HTML文件。母版壳通过 `PAGE_MODULE` 映射表决定每个菜单项加载哪个模块文件和哪个子页面。

## 三个致命陷阱

### 陷阱1：PAGE_MODULE 不包含子页面hash

```javascript
// ❌ 错误：只映射到文件，没有子页面hash
var PAGE_MODULE = {
  'campaign': 'prototype_marketing_campaign.html',
  'coupon': 'prototype_marketing_campaign.html',  // 和campaign同一个文件，不知道打开哪个子页面
};

// ✅ 正确：每个映射包含完整的 文件#子页面hash
var PAGE_MODULE = {
  'campaign': 'prototype_marketing_campaign.html#campaign-list',
  'coupon': 'prototype_marketing_campaign.html#coupon-list',
  'rules': 'prototype_marketing_ai.html#rules-config',
};
```

**症状**：菜单项打开的是模块默认页（iframe JS 中 `else showPage(default)`），不是用户点击的页面。

### 陷阱2：navigate() 函数重复拼接hash

```javascript
// ❌ 错误：mapping已包含hash，又拼接一次
frame.src = moduleFile + '#' + page;
// 结果：prototype_marketing_campaign.html#campaign-list#campaign → 404

// ✅ 正确：直接用mapping值
var src = PAGE_MODULE[page] || 'default.html#fallback';
document.getElementById('contentFrame').src = src;
```

### 陷阱3：currentPage 初始化导致首次加载被跳过

```javascript
// ❌ 错误：currentPage = 'dashboard' → navigate('dashboard') 中被 if (page === currentPage) return 拦截
var currentPage = 'dashboard';
navigate('dashboard', '首页工作台');  // 不执行！

// ✅ 正确
var currentPage = null;
navigate('dashboard', '首页工作台');  // 正常执行
```

## 完整修复清单

1. **PAGE_MODULE 每项都加 `#子页面hash`**：一个文件可能被多个菜单项共用（如 campaign.html 同时服务 campaign/coupon），每个菜单必须有独立hash
2. **navigate() 不再拼接hash**：直接用 `PAGE_MODULE[page]` 作为完整src
3. **currentPage = null**：确保首次加载必触发
4. **验证**：每个菜单项点击后，`document.getElementById('contentFrame').src` 应指向正确文件+hash
