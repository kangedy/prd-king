# 超靠谱清单 · 产品需求文档

> 项目类型：Web端AI待办管理工具
> 设计规范：Ant Design 5.x
> 版本：V1.0
> 本文档遵循10章原型导向PRD标准，每章标注P0/P1/P2优先级

---

## Ch1 · 设计规范 [🔴P0]

```css
:root {
  --brand-primary: #1677FF;
  --brand-bg: #F5F7FA;
  --sidebar-bg: #001529;
  --text-primary: #1D1D1F;
  --text-secondary: #595959;
  --border: #E5E6EB;
  --color-success: #52C41A;
  --color-warning: #FA8C16;
  --color-danger: #FF4D4F;
  --radius: 6px;
  --font-body: 14px;
}
```

**UI框架：** 自研轻量组件（基于Ant Design风格）
**布局：** 左列表 + 右详情/对话区，响应式

---

## Ch2 · 信息架构 [🔴P0]

```
├── 首页 (/)
│   ├── 清单列表（左栏）
│   │   ├── 全部
│   │   ├── 今日待办
│   │   ├── 重要
│   │   └── 已完成
│   ├── 详情/编辑区（右栏）
│   │   └── 选中事项详情
│   └── AI对话区（右栏/弹窗）
│       └── 聊天输入+消息列表
```

**用户角色：** 单用户模式（无需登录）

---

## Ch3 · 业务流程 [🟡P1]

```
核心流程：
  AI对话 → 用户输入自然语言 → 系统解析 → 自动创建/修改待办
  → 清单列表实时更新 → 用户勾选完成/编辑/删除

AI对话解析流程：
  用户输入 → 调用DeepSeek v4 Flash → 提取{action, title, time, priority, importance, note}
  → action=create → 新增待办 → 列表刷新
  → action=update → 查找并更新 → 列表刷新
  → action=delete → 查找并删除 → 列表刷新
  → action=query → 返回搜索结果

异常流程：
  AI解析失败 → 返回「未能识别，请更清晰地描述」
  网络异常 → Toast提示 + 重试按钮
```

---

## Ch4 · 系统架构 [🟢P2]

**数据流向：**
```
用户输入 → 前端 → DeepSeek API → 结构化JSON → 前端更新本地数据 → 渲染
```

**数据存储：** localStorage（本地持久化）
**AI接口：** DeepSeek v4 Flash API（OpenAI兼容格式）

---

## Ch5 · 页面清单 [🔴P0]

| data-page | 标题 | 布局 | 依赖实体 |
|-----------|------|------|---------|
| page-home | 首页 | 左右分栏 | Todo |
| page-detail | 事项详情 | 右侧面板 | Todo |
| page-chat | AI对话 | 右侧面板/弹窗 | Message |

---

## Ch6 · 功能点清单 [🔴P0]

### 清单列表 (左栏)

| # | 类型 | 动作 | 触发 | 结果 |
|---|------|------|------|------|
| 1 | Search | 筛选列表 | 点击Tab(全部/今日/重要/已完成) | 列表过滤 |
| 2 | Switch | 勾选完成 | 点击复选框 | 状态切换，划线动画 |
| 3 | Navigation | 选中事项 | 点击事项行 | 右栏展示详情 |
| 4 | Modal | 删除事项 | 点击删除图标 | 确认弹窗→删除 |
| 5 | Switch | 标记重要 | 点击星标 | 重要性切换 |

### AI对话区 (右栏)

| # | 类型 | 动作 | 触发 | 结果 |
|---|------|------|------|------|
| 1 | Submit | 发送消息 | 输入框Enter/发送按钮 | 调用DeepSeek API |
| 2 | - | AI响应解析 | API返回后 | 自动执行增删改查 |
| 3 | Refresh | 清空对话 | 点击清空按钮 | 清除聊天记录 |

### 搜索条件

无搜索框，通过Tab分类筛选：
- 全部：展示所有待办
- 今日：筛选今天到期的
- 重要：筛选高重要性
- 已完成：筛选已完成

---

## Ch7 · 数据模型 [🔴P0]

### Todo (待办事项)

| 字段 | 类型 | 必填 | 默认值 | 选项/范围 | 控件 |
|------|------|------|--------|----------|------|
| id | string | Y | uuid | — | 隐藏 |
| title | string | Y | — | ≤100字 | Input |
| time | string | N | — | 日期时间 | DatePicker |
| priority | enum | Y | medium | low/medium/high | Select/标签 |
| importance | boolean | Y | false | true/false | 星标按钮 |
| done | boolean | Y | false | true/false | Checkbox |
| note | string | N | — | ≤500字 | TextArea |
| created_at | string | Y | now | ISO格式 | 只读 |
| category | string | N | default | 自定义分类 | Select |

### Message (聊天消息)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | Y | 消息ID |
| role | enum | Y | user/assistant/system |
| content | string | Y | 消息内容 |
| created_at | string | Y | 时间 |

---

## Ch8 · Mock Data [🔴P0]

```javascript
var MOCK_TODOS = [
  { id:"t1", title:"完成PRD文档编写", time:"2026-06-25 18:00",
    priority:"high", importance:true, done:false, note:"使用prd-king标准",
    created_at:"2026-06-24" },
  { id:"t2", title:"给甲方发周报", time:"2026-06-26 10:00",
    priority:"medium", importance:true, done:false, note:"包含本周进展和下周计划",
    created_at:"2026-06-24" },
  { id:"t3", title:"采购办公用品", time:"2026-06-27",
    priority:"low", importance:false, done:false, note:"笔记本、签字笔",
    created_at:"2026-06-23" },
  { id:"t4", title:"团队周会", time:"2026-06-25 14:00",
    priority:"medium", importance:true, done:true,
    created_at:"2026-06-22" },
  { id:"t5", title:"服务器续费", time:"2026-07-01",
    priority:"high", importance:true, done:false,
    note:"阿里云ECS续费一年",
    created_at:"2026-06-21" },
];
```

---

## Ch9 · 边界条件 [🟡P1]

| 场景 | 处理方式 |
|------|---------|
| AI解析失败 | 显示「未能识别，请更清晰地描述」 |
| API超时 | Toast「网络异常，请稍后重试」+ 重试按钮 |
| 空待办列表 | 显示引导「暂无待办，在AI对话中添加吧」 |
| 标题为空 | 提示「待办内容不能为空」 |
| localStorage满 | 提示「存储空间不足，请导出备份」 |
| 重复提交 | 按钮loading态，防止重复 |

---

## Ch10 · 验收标准 [🔴P0]

| data-page | List | Detail | Action |
|-----------|------|--------|--------|
| page-home | 左栏待办列表 + 筛选Tab | 点击事项→右栏展示详情 | 勾选/星标/删除/筛选 |
| page-chat | 聊天消息列表 | 每条消息气泡 | 输入/发送/清空 |

**验收门禁：**
- G1 AI对话输入后能正确创建待办
- G2 勾选完成有划线动画
- G3 筛选Tab切换列表正确过滤
- G4 删除有确认弹窗
- G5 空态有引导文案
- G6 AI解析失败有错误提示
