# Enterprise PRD → AI Prototype PRD Conversion Workflow

## When to Use

You have a **subsystem-organized enterprise PRD** (5编 or similar structure, output by `checklist-to-prd-batch-generation.md` pattern) and need to convert it to the **AI prototype-oriented 10-chapter format** (VERSION B / `ai-prototype-prd-template.md`) suitable for direct HTML prototype generation.

Typical trigger: "这个PRD是AI开发版的吗？" or "生成AI开发版PRD"

## The Core Difference

| Dimension | Enterprise PRD (VERSION A) | AI Prototype PRD (VERSION B) |
|-----------|---------------------------|------------------------------|
| **Organization** | By subsystem (客户中心/会员中心/营销中心/数据服务) | By PRD chapter (Ch1=Design→Ch10=Acceptance) |
| **Unit of detail** | Per-subsystem module with function ID tables | Per-page with button-level operations |
| **Data model focus** | Entity tables with field lists | Field-level specs (type/required/options/validation/control) |
| **Page mapping** | Implicit (modules imply pages) | Explicit (every data-page + modal listed) |
| **Mock data** | None or placeholder | Three-state: normal/empty/extreme |
| **Audience** | Stakeholders / dev team / contract appendix | AI prototype generator / rapid iteration |
| **When to use** | First delivery, client review | After enterprise PRD approved, before prototype build |

## Decision: Dual-Generate vs Convert

### Option A: Dual-Generate (Prefer — saves a round trip)

Ask the user up-front: "需要商用交付版、AI原型版、还是两版都出？"

When generating both from the same checklist source:

**Wave 1** (3 parallel): Generate enterprise PRD per subsystem
**Wave 2** (2 parallel, starts when Wave 1 outputs ready):
- Agent A: Read Wave 1 outputs, extract public chapters → Ch1 Design + Ch2 IA + Ch4 Context
- Agent B: Read Wave 1 outputs, extract processes → Ch3 Business Flows + State Machines

**Wave 3** (3 parallel):
- Agent C: Per-subsystem page/feature/data extraction → Ch5 Page Inventory + Ch6 Features + Ch7 Data Model
- Agent D: Same for remaining subsystems
- Agent E: Extract boundary conditions → Ch9 + Ch10 framework

**Wave 4** (1): Merge all, generate Ch8 Mock data, produce final AI-prototype PRD

Total: ~7 agents across 4 waves (vs ~10 agents for enterprise-only then convert).

### Option B: Convert (When enterprise PRD already exists)

This is the pattern used in the 某省级交通集团 project. The existing enterprise PRD (大规模, 4个子系统, 数千功能点) was converted to AI prototype format in 4 waves:

#### Wave 0 · Data Scoping (main agent, no delegation)

**Purpose**: Understand the source material before planning fragment sizes. Skip this → agents get wrong scope estimates.

**Steps**:
1. Count lines per source file: `wc -l *.md`
2. Estimate function points per subsystem: grep function ID patterns (e.g., `grep -c '^| #' 01-file.md`)
3. Identify page-like sections (grep for "页面", "管理", "列表", "详情")
4. Count data model entities per file (grep for "数据模型" and count tables)
5. **Decide agent fragment sizes**: a 16-entity / 768-FP file → one agent is fine; a 1,918-FP file could split further

**Output**: Creates `01-分工计划表.md` and `02-任务跟踪记录.md` for project management.

**Why public chapters (Ch1+Ch2+Ch4) first, not subsystems**: Public chapters define the shared language (navigation tree, role names, data-page IDs, design tokens). Subsystem agents in Wave 2 all need to reference these — every page in every subsystem must use a data-page ID from Ch2's navigation tree. Generate public chapters first so Wave 2 agents can write consistent data-page identifiers.

#### Wave 1 · Public Chapters (3 parallel agents)

| Agent | Output | Source Files |
|-------|--------|-------------|
| **P1-A**: Ch1+Ch2+Ch4 | Design tokens, navigation tree, role-permission matrix, system context | `00-系统概述+背景.md` |
| **P1-B**: Ch3 | Core business flows, exception flows, state machines (Mermaid) | All subsystem files |
| **P1-C**: Ch9+Ch10 | Boundary conditions table, acceptance criteria framework, gate definitions | All subsystem acceptance sections |

#### Wave 2 · Subsystem Chapters (4 agents, max 3 concurrent)

Each agent covers Ch5 (page inventory) + Ch6 (feature inventory) + Ch7 (data model) + Ch8 (mock data) for one subsystem:

| Agent | Subsystem | Function Points | Source File |
|-------|-----------|----------------|-------------|
| **P2-A** | 客户中心 KHZX | 768 | `01-客户中心模块-PRD.md` |
| **P2-B** | 会员中心 HYZX | ~1,145 | `02+03-会员中心*.md` |
| **P2-C** | 营销中心 YXZX | 1,918 | `05+06+07-营销*.md` |
| **P2-D** | 数据服务 KHSJ | 347 | `08-客户数据服务模块-PRD.md` |

#### Wave 3 · Merge (1 agent)

Reads all Wave 1 + Wave 2 files → assembles in 10-chapter order → generates unified Mock data (Ch8 three-state) → writes acceptance gate scripts (Ch10 G1-G10) → produces coverage report.

---

## Per-Chapter Extraction Guide

### Ch1 · Design Spec [P0]

**Source**: 00-overview "设计规范" section.

Extract:
- CSS Token variables (--brand-primary, --brand-bg, --sidebar-bg, --radius-card, --font-size-body, etc.)
- UI framework name + component library reference
- Layout specs: sidebar width, content max-width, grid columns, gutter
- Component conventions: Table, Form, Modal, Search, Tag, Button

**Output format** (CSS variables as a code block + prose descriptions):

```css
--brand-primary: #1677FF;
--brand-bg: #F5F7FA;
--sidebar-bg: #001529;
--radius-card: 6px;
--font-size-body: 14px;
```

### Ch2 · Information Architecture [P0]

**Source**: 00-overview "信息架构" or subsystem overviews.

Extract:
- Full tree with data-page identifiers on every leaf node
- Role-menu mapping table
- Default landing page per role

**Output format**:

```
├── KHZX 客户中心 (/khzx)
│   ├── 首页看板 (/khzx/dashboard)        data-page="khzx-dashboard"
│   ├── 指标分析 (/khzx/indicator)        data-page="khzx-indicator"
│   └── ...
```

### Ch3 · Business Process [P1]

**Source**: All subsystem files — look for process descriptions, flow diagrams, state transitions, business rules.

Extract:
- **Core flows** as Mermaid flowcharts: each node labels the page/modal name, edges label the action
- **Exception flows**: payment failure, rule timeout, data sync error, approve rejection
- **State machines** as Mermaid stateDiagram-v2, with state-color mapping table

**Critical**: Every label in the flowchart must be a recognizable page name that matches a data-page in Ch5.

### Ch4 · System Context [P2]

**Source**: 00-overview "用户角色" + permission-related sections.

Extract only what affects prototype:
- Role-permission rules (buttons visible/hidden per role)
- Data flow description (affects mock data relationships)
- Unified API response format ({code, msg, data})

### Ch5 · Page Inventory [P0]

**Source**: Each subsystem file's module definitions → infer page structure.

Each module typically maps to one data-page (list page) + one or more detail/form/modal pages. Infer page boundaries from:

- Module sections with "查询列表页", "详情页", "管理" in their titles
- Data model entities referenced in the module
- Feature operations that imply navigation (查看→detail, 新增→form)

**Output table**:

| data-page | Title | Module | Layout | Dependencies | Modal list |
|-----------|-------|--------|--------|--------------|------------|
| khzx-customer | 客户管理 | KHZX | table+search | Customer | add(含8字段:姓名/手机/身份证/邮箱/来源/标签/备注/创建时间)+edit+detail(只读+车辆tab+订单tab) |

**Modal list field rule**: extract field names from the module's data model section. Strip auto-generated fields (id, created_at). Use Chinese option values.

### Ch6 · Feature Inventory [P0]

**Source**: Function point tables in each subsystem file.

Convert ILF/EI/EQ/EO function point rows → button-level operations per page:

| Checklist Type | Maps to Ch6 Element |
|----------------|---------------------|
| ILF (Internal Logical File) | Data entity → referenced in data model Ch7 |
| EI (External Input) | Button/action → form submit, config save, batch operation |
| EQ (External Inquiry) | Search condition or navigation → table row click goes to detail |
| EO (External Output) | Export/download → export button, report generation |
| EIF (External Interface) | API call → sync button, import button |

**Per page, extract**:
- Feature table (# / action type / action name / trigger / result / data source)
- Search conditions field list (with control type and options)
- Modal inventory (modal ID → field list)

**Action type enum**: Search / Navigation / Modal / Submit / Download / Delete / Batch / Switch / Refresh

### Ch7 · Data Model [P0]

**Source**: Data model sections in each subsystem file.

Conversion rules:

| Enterprise PRD format | AI prototype format |
|-----------------------|---------------------|
| Entity name + field list (markdown list) | Entity table with 6 columns: field / type / required / options (Chinese) / control / validation |
| `├── member_id (PK) VARCHAR(32)` | `member_id | string | Y | — | Text(只读) | 系统自动生成` |
| Single entity table | One table per entity, same schema |

**Enum field rule**: ALWAYS use Chinese UI-visible option values, not English codes:
- ✅ `状态: 启用/停用`
- ❌ `状态: active/disabled`

**Options must match between Ch7 and Ch6** — what the user sees in the form dropdown is what appears in Ch7's options column.

### Ch8 · Mock Data [P0]

**Source**: Ch7 entities + real business data from project context.

Generate three sets per entity:

1. **Normal** (5-10 records): Realistic business data with cross-entity ID consistency. IDs must match across related entities (e.g., member_id=1001 appears in both 会员主表 and 积分账户表).

2. **Empty**: `var MOCK_X_EMPTY = [];` — empty state trigger data.

3. **Extreme**: Long text (200+ chars), large amounts (¥9,999,999.99), extreme dates (1970-01-01 / 2099-12-31).

**Cross-entity consistency rule**: If member_id=1001 is created in Ch8's member mock data, all other entities referencing member_id=1001 must use the same ID. Use a single mock data pool.

### Ch9 · Boundary Conditions [P1]

**Source**: Acceptance criteria sections per module — extract scenarios that indicate edge case handling.

Group rules into table:

| Scene | Per-subsystem variant |
|-------|----------------------|
| No permission | Button grey + tooltip (all subsystems) |
| Form validation fail | Red border + inline error (all subsystems) |
| Network error | Toast + retry button (add auto-retry for data service) |
| Empty data | Illustration + guidance (all subsystems) |
| Loading state | Skeleton (all except data service: skeleton + progress bar) |
| Long text | Truncate + Tooltip |
| Amount format | ¥1,234,567.89 (marketing/settlement: 2 decimal fixed) |
| Pagination boundary | Prev disabled on page=1, Next disabled on last page |
| Data consistency | Cross-system entity verification (KHZX), point-order verification (HYZX), coupon-settlement verification (YXZX) |
| Big data threshold | >100M report rows cache (KHZX), >1M members (HYZX), >100K campaigns (YXZX), >10M customer records (KHSJ) |
| Sensitive data | Phone/ID mask (KHZX, HYZX), bank account mask (YXZX), encrypted storage (KHSJ) |
| Concurrent operation | Same entity edit lock (KHZX), point mutual exclusion (HYZX), budget concurrent deduction (YXZX), data source mutex (KHSJ) |

### Ch10 · Acceptance Criteria [P0]

#### Per-Page Triple

For every data-page in Ch5, answer:

| data-page | List在哪 | Detail在哪 | Action有哪些 |
|-----------|---------|-----------|------------|
| khzx-customer | Ant Design Table + Pagination | Click row → customer detail (tabs: profile/vehicles/orders/points) | search/add/edit/merge/delete/export/import |

#### Gates G1-G10

```javascript
G1: Every function point has a handler (onclick/data-action/type=submit)
G2: All data-pages exist and render (no 404)
G3: Every Ch7 field appears on at least one page
G4: Cross-page entity ID consistency (same member_id shows same data everywhere)
G5: Every list page has empty state + loading state
G6: Body ≥14px, table ≥13px, label ≥12px
G7: JS passes `node --check` with zero syntax errors
G8: Every <button> has an interactive handler
G9: Every openFormModal() call has a matching <div id="..."> element
G10: Every data-page exists in the navigation menu tree
```

---

## Pitfalls

1. **Ask version first**: Before writing a single line, clarify "需要商用交付版、AI原型版、还是两版都出？". Generating one then converting costs ~2x more agent calls.

2. **06的表格格式差异**: The AI/风控 modules (营销子系统Part2) commonly use non-standard table formats. When grep-verifying, manually spot-check rather than trusting line counts.

3. **Block ID numbering**: 会员中心子系统 (02/03) uses block IDs (GL-050 = 1 ID → 3-5 sub-function-points). When converting to Ch6, unroll each block into explicit per-field or per-button entries.

4. **Modal field integrity**: Every field listed in a modal (Ch5 modal column) must have a corresponding definition in Ch7. Missing = prototype renders a form with empty labels.

5. **Mock data ID cross-referencing**: The most common QA failure is mock data inconsistency — e.g., member_id in 积分 account table doesn't match any member in 会员主表. Use a single mock data generator.

6. **Skip Ch4 bloat**: Chapter 4 is for prototype-affecting context only. Do not put microservice architecture, database schemas, or deployment configs here. If they exist in the source, move to an appendix.

7. **Copy vs reference**: When two subsystems share a data model (e.g., member appears in both KHZX and HYZX), write the entity table once in Ch7 and cross-reference it — don't duplicate.

9. **Function ID tables ≠ Ch6 feature inventory**: Enterprise PRDs use ILF/EI/EQ/EO function ID tables (e.g. "#149 | 数据源连接测试 | 操作 | EO | 测试连接"). These classify CRUD operations at the entity level. AI prototype Ch6 needs **per-page button-level** entries (e.g. "khsj-ingestion-detail: ⑤ | Modal | 测试连接 | 点击测试按钮 | 弹窗显示连接结果"). Converting requires: (a) group function IDs by their implied page, (b) infer button types from EI/EQ/EO, (c) add missing UI-only actions (search submit, reset, page navigation). Don't assume function ID tables map 1:1 to Ch6 rows.

10. **Multi-wave sub-agent max concurrency**: Hermes max_concurrent_children=3. Plan waves accordingly. Wave 1: 3 agents. Wave 2: 3 agents (queue 4th for next slot). Wave 3: 1 agent.

---

## Coverage Verification: Point-to-Point Checklist Audit

When the user asks "检查验收清单所有功能点是否都有覆盖" after a conversion, do NOT run a naive keyword grep — it produces ~0% false negatives because function point names were structurally transformed (e.g., "商品列表主数据" became a row in yxzx-product's feature table).

### The Right Approach: Module-Level Mapping

Instead of matching individual function point names against the AI PRD text, build a **source module → AI PRD page** mapping table.

#### Step 1: Extract source module structure

```python
wb = openpyxl.load_workbook("checklist.xlsx", data_only=True)
ws = wb['Sheet1']
modules = {}  # {module_name: {'total': count, 'items': [...]}}
for r in range(5, ws.max_row + 1):
    num = ws.cell(r, 1).value
    name = str(ws.cell(r, 6).value or '').strip()
    module3 = str(ws.cell(r, 5).value or '').strip()  # 三级模块
    if num and name:
        modules.setdefault(module3, {'total': 0, 'items': []})
        modules[module3]['total'] += 1
        modules[module3]['items'].append((num, name))
```

#### Step 2: Build the mapping table

Map every source module name to the corresponding AI PRD data-page(s). A single AI PRD page (e.g., `yxzx-system`) may cover 15+ source modules (user/role/permission/task scheduling/health checks/etc.).

```python
ai_mapping = {
    '客户管理': 'khzx-customer, khzx-customer-detail',
    '会员注册与登录': 'hyzx-front',
    '商品查询列表页': 'yxzx-product',
    # ... all modules mapped to AI PRD pages
}
```

**Key insight**: Source modules ending in "管理", "配置", "列表页" → list page. Modules for "接口XXX", "数据XXX", "权限XXX" → aggregate under generic system management page.

#### Step 3: Generate coverage report per module

```
✅ [27项] 商户结算信息查询页 → yxzx-settlement
⚠️ [9项] 接口连通性诊断 → yxzx-system (aggregated under system)
```

**Status**: ✅ = clear mapping, ⚠️ = aggregated under broader page (content exists, naming differs), ❌ = real gap.

#### Step 4: Verify "missing" items via constituent keyword search

```python
for part in ['优惠券', '查询接口']:
    if part.lower() in prd_text.lower():  # ✅ found under yxzx-system
```

If constituent keywords exist, the content IS covered — it's a granularity mismatch.

#### Step 5: Final report structure

```
## 总体覆盖率
| 维度 | 数据 |
| 总计 | 4,177 功能点 / 196 模块 |
| 模块级覆盖 | 196/196 = 100% |
| 精确功能点名匹配 | 84.9% (剩余为命名差异) |

## 逐模块明细
### ✅ 客户管理 (74项) → khzx-customer, khzx-customer-detail
### ⚠️ 优惠券码查询接口 (2项) → yxzx-system (aggregated)
```

### Common Source→AI PRD Mapping Patterns

| Source module pattern | AI PRD mapping | Example |
|-----------------------|----------------|---------|
| `{Entity}查询列表页` | `{prefix}-{entity}` | 商品查询列表页 → yxzx-product |
| `{Entity}详情页` | `{prefix}-{entity}-detail` | 商品详情页 → yxzx-product-detail |
| `{Action}管理` | Same entity page | 商品上下架管理 → yxzx-product |
| `{Business}分析` | Statistics page | 活动效果分析 → yxzx-statistics |
| `接口{Action}` | System management | 接口权限配置 → yxzx-system |
| `{Data}存储` | Data model section (not UI) | 安全数据存储 → yxzx-system data model |
| `超级管理员（锁定）` | System management | → yxzx-system |
| `{Rule}优先级管理` | Rule engine page | 规则优先级管理 → yxzx-rule-engine |

### Why This Works

The original Excel checklist enumerates every operation as a separate function point (e.g., "商品列表主数据"+"字段要素"+"基础查询"+"高级组合筛选"+"单字段排序"+"多字段排序"+"分页" = 7 points for ONE page). The AI PRD collapses these into one feature table row. Module-level mapping correctly accounts for this structural compression — 100% name-level match is impossible (and undesirable).
