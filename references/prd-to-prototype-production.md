# PRD→原型 批量生产工作流

当PRD（VERSION B，10章标准）完成后，需要从中生成完整的可交互HTML原型时，使用此工作流。

## 适用场景

- PRD的Ch5页面清单有50+页面
- 需要从零生成完整原型，或基于已有框架扩展
- 团队需要快速产出可评审的交互原型

## 工作流

### Phase 1: 从PRD提取页面清单

从PRD Ch5提取所有 `data-page` 标识和对应的页面信息：

```python
# Ch5表格格式：| data-page | 标题 | 布局类型 | 依赖实体 | 补充PRD |
pages = {
    "khzx-dashboard": {"title": "客户中心首页", "layout": "dashboard"},
    "khzx-customer-list": {"title": "客户管理列表", "layout": "table"},
    ...
}
```

同时从Ch2 IA提取导航结构（4层树形菜单）。

### Phase 2: 建立内容映射

检查是否有可复用的现有页面内容（来自之前版本的原型或其他项目），建立映射表：

```python
content_map = {
    "khzx-strategy-event": "event-list",   # 复用现有页面
    "hyzx-points-define": None,            # 需新生成
}
```

### Phase 3: 生成初始SPA原型

创建单文件SPA原型，包含：
- 完整CSS（基于PRD Ch1设计规范）
- 4层导航结构（来自Ch2 IA）
- 所有页面占位（来自Ch5页面清单）
- 复用已有内容页面（来自Phase 2映射）
- 未映射页面生成简洁占位（含面包屑+标题+"该页面内容将在后续迭代中补充"）

**文件结构**：单HTML文件，SPA架构，`switchPage()` + `switchSubsystem()` 实现无刷新切换。

### Phase 4: 并行填充占位页

对于占位页，按子系统/模块拆分任务，并行委派子agent填充：

```
子agent 1: KHZX客户中心 (14页) + HYZX会员中心 (14页)
子agent 2: YXZX营销中心 (25页)
子agent 3: KHSJ数据服务 (6页)
```

**每个占位页的填充标准**：
- 面包屑导航
- 页面标题+业务描述
- KPI卡片（2-6个业务统计数据）
- 筛选条件栏（2-5个筛选字段）
- 数据表格（5-8列，5行真实Mock数据）
- 操作按钮（查询/重置/新增/导出/编辑等）
- 分页组件

**Mock数据规范**：数据要有业务真实感（如"2,156,389总客户"而非"测试数据1"）。

### Phase 5: 覆盖率量化验证

用源码分析而非浏览器渲染来量化覆盖率：

```python
with open('prototype.html', 'r') as f:
    c = f.read()

metrics = {
    'data_page': len(re.findall(r'data-page="[\w-]+"', c)),
    'kpi_value': c.count('kpi-value'),
    'tables': c.count('<table'),
    'td_cells': c.count('<td'),
    'th_cells': c.count('<th'),
    'buttons': c.count('<button'),
}
```

对比PRD Ch5页面清单（预期data-page数）计算页面覆盖率。

### Phase 6: 输出覆盖报告

生成HTML覆盖报告，内容：
- 统计卡片（页面数/KPI数/表格数/数据单元格数/按钮数）
- 逐模块覆盖矩阵（对照验收清单）
- 进度条展示整体覆盖率
- 未覆盖项及原因说明

## 关键原则

1. **不要从零写所有页面** — 先建立内容映射，最大化复用
2. **占位页优于缺失页** — 先确保所有页面存在（即使占位），再逐步填充
3. **并行填充** — 50+页面的填充工作必须拆分给多个子agent并行执行
4. **源码验证** — 用统计计数代替肉眼检查，更快更准
5. **子agent操作同一个文件** — 按data-page前缀（如khzx-/hyzx-）分隔，避免冲突

## Pitfalls

- ❌ **子agent各自创建独立文件** — 必须操作同一个HTML文件，最后手动合并容易出错
- ❌ **过度追求「完美」第一版** — 先出91页占位原型，再分批填充，比先做10页完美页面更有价值
- ❌ **data-page命名不一致** — PRD和原型的data-page必须一一对应，不一致会导致覆盖率统计失真
- ❌ **忘记更新导航** — 新增页面必须在导航菜单中注册，否则用户找不到
