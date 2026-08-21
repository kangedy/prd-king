# Checklist-to-PRD Batch Generation Workflow

## When to Use

When you have an acceptance checklist Excel (甲方功能点清单) and need to generate supplementary PRD chapters that map 1:1 to the checklist's function points. This is the inverse of the `acceptance-checklist-audit` skill: instead of auditing existing PRD against checklist, you're **generating new PRD content from the checklist**.

Typical trigger: "输出第N批PRD补充章节" or "完成模块X的PRD补充"

## Data Sources

| Source | Format | How to Read |
|--------|--------|-------------|
| 验收清单 | .xlsx | `read_file` with offset — Excel files extracted as text with line numbers. Large files (4000+ lines) need offset-based navigation |
| 现有PRD | .docx | `read_file` with offset — DOCX extracted as text. Check existing module coverage before writing |
| 产品原型 | .html (optional) | `read_file` or browser tools — for cross-referencing page structure |

## Workflow

### Step 1: Locate Target Sections in Checklist

Use `search_files` with `target='content'` to find module names in the checklist Excel, or use `read_file` with progressively larger offsets to scan through Sheet2 (营销中心系统 typically starts at ~line 2266 of the combined XLSX).

**Pitfall**: Different Excel sheets have different column structures. Sheet1 (客户中心系统) has 7 columns, Sheet2 (营销中心系统) has 8 columns (adds "功能点类型" column). Account for this when extracting.

### Step 2: Count and Group Function Points

For each target module, extract all function points by reading the checklist rows. Group by hierarchy:

```
一级模块 → 二级模块 → 三级模块 → 功能点列表
```

Each function point row contains:
- 编号 (row number)
- 子系统
- 一级模块
- 二级模块  
- 三级模块
- 功能点计数项名称
- 上报类别 (ILF/EI/EQ/EO/EIF)

### Step 3: Check Existing PRD Coverage

Read the existing PRD DOCX to identify which sections are already covered and at what percentage. The user will typically tell you the current coverage (e.g., "45% covered"), but verify by checking if the PRD has corresponding sections.

### Step 4: Generate PRD Chapters

For each module, produce a structured PRD chapter with:

```markdown
## 1. 模块概览
  - 模块定位 (1 paragraph)
  - 功能点分布表 (table mapping 三级模块 → function point count → checklist row range)
  - 角色定义 (who uses this module)

## 2. 子模块需求详述 (one per 三级模块)
  Each sub-section:
  - 功能定位 (1 sentence)
  - 业务规则表 (规则类型 | 具体规则)
  - 数据模型表 (for ILF-heavy modules: entity | fields | type)
  - 输入输出表 (维度 | 数据项 | 来源/去向)
  - 验收标准 (checkbox list, 4-8 items)

## 3. [Optional] Cross-cutting concerns
  - Execution priority matrix (for rule engines)
  - Architecture diagrams (for orchestration modules like 营销画布)
  - Data flow summaries

## N. 验收总标准
  - Overall acceptance table
```

### Step 5: Naming Convention

Use consistent file naming and requirement IDs:

- File: `{module_name}_prd.md` (e.g., `system_mgmt_prd.md`, `compliance_risk_prd.md`)
- Requirement ID format: `{SubsystemCode}_{ModuleCode}_{SubModuleCode}_{NNNN}`
  - Example: `YXZX_XTGL_RWDD_0001` (营销中心_系统管理_任务调度_0001)

### Step 6: Map ILF/EI/EQ/EO/EIF to PRD Content

The checklist's function point types guide what to emphasize:

| Type | Meaning | PRD Emphasis |
|------|---------|-------------|
| ILF | Internal Logical File | Data model — this is a persistent data entity, describe its fields |
| EI | External Input | Business rule — this is a user action (form submit, config save), describe validation |
| EQ | External Inquiry | Query/display rule — this is a read operation, describe filter conditions and output format |
| EO | External Output | Report/export rule — this is computed output, describe calculation logic and format |
| EIF | External Interface File | Interface spec — this references external data, describe the interface contract |

## Common Pitfalls

1. **Excel offset navigation**: Large checklists (4000+ lines) require multiple `read_file` calls with increasing offsets. Start with rough skips (offset=2200 for Sheet2 start), then refine.

2. **Module naming in checklist vs PRD**: The checklist may use slightly different module names than the PRD. Always use the checklist's exact naming in requirement IDs.

3. **Function point granularity**: Don't try to make every single function point a separate section. Group by 三级模块 — each 三级模块 becomes one PRD sub-section.

4. **The "三件套" pattern**: Every sub-module needs 业务规则 + 数据模型(if ILF) + 验收标准. Don't skip the data model for ILF-heavy modules.

5. **Already-covered content**: When the PRD already covers ~50% of a module, only write the missing parts. Reference existing content rather than duplicating.

6. **Balancing depth vs speed**: For 500+ function points across 3 modules, each function point gets ~1-2 sentences in the final PRD. Don't write novels — be precise and checklist-compatible.

## Output Pattern from Real Session (某省级交通集团 · W1 Final Batch)

Generated 3 files totaling 523 function points:
- `system_mgmt_prd.md` (171 pts): 任务调度/数据维护/系统诊断/RBAC/首页
- `compliance_risk_prd.md` (166 pts): 合规审计 + 11风控子模块 with execution priority matrix
- `ai_marketing_prd.md` (186 pts): 标签对接/策略中心/营销画布编排 with architecture diagram

All files: ~18-23KB each, 400-500 lines, structured as module overview → sub-module specs → acceptance criteria.

## Mega-Scale Parallel Dispatch (4000+ Function Points / 4+ Subsystems)

When the checklist has **4000+ rows across multiple subsystems** (e.g., 4 subsystems × ~1000 rows each), sequential single-agent generation is too slow. Use **multi-wave parallel dispatch** instead.

### Prerequisites: Project Scaffolding

Before dispatching any sub-agent, create **two scaffolding files** in the output directory:

1. **分工计划表** (Work Plan): One-page MD with system architecture diagram, task decomposition table (per subsystem: agent, input files, function point range, output path), execution waves, and quality checklist.
2. **任务跟踪记录** (Task Tracker): Status table with per-task rows, states (🟢/🟡/🔴/❌), and completion timestamps. Updated as sub-agents report.

### Dispatch Pattern

```
Wave 1 (3 parallel — Hermes max_concurrent_children=3 default):
├── Agent A: 系统整体概述+架构+背景  (overview)
├── Agent B: 客户中心模块           (module: #1-#768)
└── Agent C: 营销+数据服务模块      (module: 营销~70+数据~30)

Wave 2 (queued, starts as Wave 1 slots free):
├── Agent D: 会员中心-前台+管理+积分 (module: #765-#1120)
└── Agent E: 会员中心-策略中心+触点   (module: #1121-1500+)

Wave 3 (after all sub-agents finish):
└── Merge + verify                  (consolidation)
```

### Sub-Agent Task Design

Each sub-agent gets a self-contained context with:

| Parameter | Rule |
|-----------|------|
| **boundary** | One complete subsystem — never split a subsystem mid-way |
| **function point range** | Exact checklist row numbers (e.g., #1-#768) |
| **input references** | Subset of requirement doc relevant to their subsystem |
| **output file** | Absolute unique path (never overlap between agents) |
| **format** | Per detailed PRD template: module overview→sub-module specs (功能ID/表格/数据模型/验收标准) |
| **key alignment data** | For membership center: member rule values must appear verbatim (100积分=1元, 365天有效期 etc.) |

### File Naming Convention

```
PRD生成/
├── 01-分工计划表.md                  ← scaffolding
├── 02-任务跟踪记录.md                ← scaffolding
├── 00-{subsystem}-{overview}.md     ← overview
├── 01-{subsystem}-PRD.md            ← per-subsystem
├── 02-{subsystem}-PRD.md
├── ---
├── {project}-PRD-完整版.md          ← consolidated
└── PRD覆盖率自验报告.md              ← verification
```

### Consolidation (Wave 3)

1. **Verify outputs**: stat every expected file
2. **Read and merge**: preface with system overview, then subsystem chapters, then traceability appendix
3. **Validate 100% coverage**: cross-reference checklist row numbers against PRD sections
4. **Update tracker**: mark everything complete or flag gaps

### Critical First Step: Scan ALL Excel Sheets

**This is the #1 cause of mid-project corrections.** The acceptance checklist Excel may have **multiple sheets** each covering a different subsystem.

**⚠️ `read_file` pitfall**: Hermes's `read_file` on `.xlsx` files silenly extracts **only Sheet1** content. If the checklist has Sheet2 with different subsystem data (e.g., 1924 rows of marketing module), `read_file` will show 4190 lines (all from Sheet1) and you'll never see Sheet2. You'll think you've read the whole file when you've only seen ~50%. **Always scan sheets programmatically first.**

### Procedure

Before writing any plan or dispatching any agent:

```python
import openpyxl
wb = openpyxl.load_workbook('checklist.xlsx', data_only=True)
print(wb.sheetnames)
for name in wb.sheetnames:
    ws = wb[name]
    print(f"{name}: {ws.max_row} rows x {ws.max_column} cols")
```

Typical multi-sheet layout: Sheet1 (客户中心系统 ~2200 rows), Sheet2 (营销子系统 ~1900 rows). Sheet2 may have different column structure (adds 功能点类型).

### Extracting Sheet2+ Data When `read_file` Only Shows Sheet1

When you need to process specific modules from Sheet2+ into the PRD, extract by module into TSV files for direct reading:

```python
import openpyxl
wb = openpyxl.load_workbook('checklist.xlsx', data_only=True)
ws = wb['Sheet2']
target_modules = ['结算管理', '统计分析', '系统管理', '第三方系统接口管理']
for module in target_modules:
    lines = []
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row, values_only=True):
        if row[3] and str(row[3]).strip() == module:
            vals = [str(c).strip() if c is not None else '' for c in row]
            lines.append('\t'.join(vals))
    with open(f'/tmp/sheet2_{module}.tsv', 'w') as f:
        f.write('\n'.join(lines))
```

Then use `read_file` on the `.tsv` files for the detailed content analysis needed to write PRD chapters.

### Module Structure Extraction

Write a Python script for sub-agent context:

```python
from collections import defaultdict
modules = defaultdict(lambda: {'counts': defaultdict(int)})
for row in ws.iter_rows(min_row=6, values_only=True):
    if row[0] is None: continue
    l1, l2, l3 = (row[3] or ''), (row[4] or ''), (row[5] or '')
    modules[(l1,l2,l3)]['counts'][row[7]] += 1
for k, d in sorted(modules.items()):
    t = sum(d['counts'].values())
    cats = ', '.join(f'{k}:{v}' for k,v in sorted(d['counts'].items()))
    print(f"{k[0]} -> {k[1]} -> {k[2]}: {t} ({cats})")
```

### Split Guidelines

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| Total points per sheet | >300 | Split into 2+ agents |
| 一级模块 count | >6 | Group into clusters |

### Mid-Project Discovery

When user corrects mid-project ("Sheet2也要加入"):

1. Don't cancel running agents (their deprecated output ignored at merge)
2. Mark old task as ⛔ 已弃用, add new as 🔵 新增
3. Immediately dispatch new agents for discovered scope
4. At merge: use new version, discard deprecated

## Pitfalls

- **Scan all sheets first**: Most common correction is "Sheet2 also". Check every sheet before planning.
- **Count FPs per subsystem, not just per sheet**: A subsystem may have FAR more FPs than you estimate. In 某省级交通集团, 客户数据服务 was estimated at ~80 FPs but had **347 FPs** (#1913-#2258) with a whole "专项数据服务封装" module missed. Run a per-subsystem count before sizing agents:
  ```python
  from collections import defaultdict
  for row in ws.iter_rows(min_row=6, values_only=True):
      l1 = str(row[2]) if row[2] else ''
      if '数据服务' in l1: counts['data_svc'] += 1
  ```
  200+ FPs → dedicated agent. 400+ → split into 2.
- **Don't cluster unrelated subsystems into one agent**: 营销中心 and 客户数据服务 are architecturally separate with independent data models. Bundling them leads to the under-detailed one being called out. Each subsystem gets its own agent.
- **Max 3 concurrent**: Batch in waves of 3, then 2, then consolidation.
- **No auto-merge**: Sub-agents each write their own file. The orchestrator must physically merge — never ask one sub-agent to read another's output.
- **Unique output paths required**: Overlap = last writer wins = data loss. Use absolute paths.
- **Exact function ranges**: "Roughly 1000 points" produces vague PRDs. Use exact #start-#end boundaries.
- **Verify, don't trust**: Even when every sub-agent reports "done", physically stat the files and verify coverage.
- **Track mid-project overrides explicitly**: When the user adds scope mid-project (e.g., "Sheet2也要加入"), mark the old task as ⛔ 已弃用 in the tracker, add new as 🔵 新增, and dispatch fresh agents. Don't try to amend running agents.

## Single-Agent Detailed PRD Generation Pattern

When generating a detailed PRD for 3-5 modules (500-900 function points) in a single session, use this structure pattern instead of the mega-scale parallel dispatch:

### Function Point → PRD Row Expansion

Each checklist row maps to a PRD table row with these columns:

```markdown
| 序号 | 功能ID | 功能点名称 | 类型 | 需求描述 |
|:---:|--------|-----------|:---:|---------|
| 1 | YX_HDGL_PLAN_0001 | 活动计划主数据 | ILF | 存储活动计划的核心数据实体，包含计划ID、计划名称、计划周期、计划状态等 |
```

**功能ID format**: `{SubsystemCode}_{ModuleCode}_{SubModuleCode}_{NNNN}`
- Example: `YX_HDGL_PLAN_0001` = 营销中心(YX) _ 活动管理(HDGL) _ 计划(PLAN) _ 0001

**需求描述 rules**:
- ILF rows: describe what data entity stores and its key fields
- EI rows: describe the user action, input parameters, and validation
- EQ rows: describe the query conditions and expected output format
- EO rows: describe what is computed/output and the format
- EIF rows: describe the external system and interface contract

### Template Module Compression

When the checklist has **repeated sub-module structures** (e.g., 8 activity types each with similar 22-24 function points — 满减/满赠/限时折扣/特价/会员专享/组合商品/油非互动/团购), show one module in full detail and compress the rest:

```markdown
#### 满减活动（24功能点）— 完整详述
| 序号 | 功能ID | 功能点名称 | 类型 | 需求描述 |
... (all 24 rows detailed) ...

#### 满赠活动（22功能点）— 差异化要点
**差异化配置要点**：
- 赠品类型：实物/积分/优惠券
- 阶梯满赠：多档门槛赠送不同赠品

| 序号 | 功能ID | 功能点名称 | 类型 | 需求描述 |
... (22 rows, marked as abbreviated for shared patterns) ...
```

This avoids 180+ near-duplicate table rows while preserving complete function-to-ID traceability.

### Output Structure Per Module

Each top-level module (营销活动管理 / AI精准营销推荐 / 合规与风控) follows:

```
## 模块N：{Module Name}（{N}功能点）
> 定位：{1-2 sentence positioning}
### 角色定义 (table)
### N.1 {SubModule}（NN功能点）
#### Module Overview
#### Function Point Table (expanded from checklist)
#### Business Rules Table
#### Data Model Table (if ILF-heavy)
#### Acceptance Criteria Checklist
### N.2 ... (repeat)
```

**Every sub-module gets the "四件套"**: function point table + business rules + data model + acceptance criteria.

### Mega-Scale Output Pattern (某省级交通集团 · 4 Subsystems)

5 sub-agents across 2 waves, ~4000 function points:

| File | Subsystem | Function Points | Key Sections |
|------|-----------|----------------|--------------|
| `00-系统概述+背景.md` | Overall | Overview | 项目背景/设计规范/信息架构/业务流程 |
| `01-客户中心模块-PRD.md` | 客户中心 | #1-#768 | 首页/指标分析/固定报表/自助报表/客户管理/用户/账户/规则/编码/标签画像 |
| `02-会员中心-前台+管理+积分-PRD.md` | 会员中心 | #765-#1120 | 注册登录/会员管理/积分定义/累积/兑换/互通/出账/合作伙伴/报表 |
| `03-会员中心-策略中心+触点+活动.md` | 会员中心 | #1121-#1500+ | 策略驾驶仓/创建/审批/预演/触点/渠道对接/服务活动/运营分析 |
| `04-营销中心+数据服务模块-PRD.md` | 营销+数据服务 | 营销+数据 | 商品/商户/优惠券/风控/AI营销/结算+数据汇聚/关联/标签处理/调度 |
