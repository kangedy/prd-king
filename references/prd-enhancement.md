---
name: prd-enhancement
description: Enhance Chinese PRD .docx files — add module-level interaction prototypes, editable business flowcharts, OR perform incremental revision aligning PRDs with policy/regulation documents via targeted table+text replacements while preserving all non-conflicting content.
---

# PRD Enhancement Workflow

Take a PRD `.docx` (Product Requirements Document) and enhance it for developer handoff by adding:
1. **Module-level interaction prototype placeholders** — "交互原型：待后续增加" as a dedicated paragraph per module
2. **Business flowcharts** — both editable draw.io files + embedded PNGs in a dedicated appendix section

## Prerequisites

```bash
pip install python-docx pillow lxml
# Chinese font for flowcharts
# Noto Sans CJK SC at /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
```

## Step 1: Analyze the Docx Structure

Chinese PRDs typically use **Heading 1/2/3** styles for subsystem/module hierarchy. Function tables have headers like "编号 | 功能点 | 详细说明".

```python
import docx
doc = docx.Document("PRD.docx")
for pi, p in enumerate(doc.paragraphs):
    if p.style and p.style.name == "Heading 3":
        print(f"P{pi}: {p.text.strip()}  # module heading")
```

Key structural elements to identify:
- **Heading 3** paragraphs = module headings (e.g. "1.2.1 客户管理")
- **Function tables** = tables with "编号" + "功能点" in header (3 columns)
- **验收标准** paragraphs = acceptance criteria destination
- **功能点** paragraphs = function table section header

## Step 2: Add Interaction Prototype Placeholders

Insert "交互原型：待后续增加" as a dedicated paragraph at module level (NOT inside function tables).

**Placement logic:**
- If module has "验收标准" → insert before it
- If no "验收标准" → insert at end of module (before next heading or end of body)

**CRITICAL: Process modules in REVERSE order** to avoid position shifting from insertions:

```python
from lxml import etree
ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def make_proto_para():
    """Create paragraph: bold prefix + regular text."""
    p = etree.Element(ns + 'p')
    r1 = etree.SubElement(p, ns + 'r')
    rPr1 = etree.SubElement(r1, ns + 'rPr')
    etree.SubElement(rPr1, ns + 'b')
    t1 = etree.SubElement(r1, ns + 't')
    t1.text = "交互原型："
    t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r2 = etree.SubElement(p, ns + 'r')
    t2 = etree.SubElement(r2, ns + 't')
    t2.text = "待后续增加"
    t2.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return p
```

## Step 3: Generate Flowcharts (Two Formats)

### 3a. Pillow PNG (for docx embedding — reliable Chinese font rendering)

Use `Pillow` + `Noto Sans CJK SC` for Chinese text. **Do NOT use cairosvg for Chinese text — it cannot render CJK fonts reliably.**

```python
from PIL import Image, ImageDraw, ImageFont
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def font(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, sz)
```

### 3b. draw.io XML (for Word-editable shapes)

See the `drawio` skill's `references/programmatic-flowchart-generation.md` for the complete template. **CRITICAL: HTML tags in value attributes MUST be XML-escaped** (`&lt;b&gt;` not `<b>`).

## Step 4: Embed Flowcharts in Docx Appendix

Create or update an "附录：核心业务流程图" section at the end of the docx:

```python
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Add image to paragraph
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run()
r.add_picture("flowchart.png", width=Inches(4.2))
```

**Subsystem grouping**: 客户中心 → 会员中心 → 营销中心 → 数据中心

Each flowchart entry: title line (▸ bold blue) → centered image → spacer

## Step 5: Version Management

```python
import shutil
# Copy original, never overwrite
shutil.copy("PRD_V2.0.docx", "PRD_V2.1.docx")
```

## Flowchart Content Standards (for developer handoff)

Each node should contain (not just a label):

| Info Type | Example |
|-----------|---------|
| Business rule | "身份证+手机+ETC卡号 三要素匹配" |
| SLA | "响应时间 < 500ms" |
| Tech param | "UUID v4 / JWT / bcrypt cost=10" |
| Exception handling | "重试3次→报错 / 回滚预案30min" |
| Integration point | "对接税控系统 / ETC路网系统" |

## Node Type Color Scheme

| Type | Fill Color | Shape | Use |
|------|-----------|-------|-----|
| Start/End | `#d5e8d4` (green) | Rounded rect | Entry/exit point |
| Process | `#dae8fc` (blue) | Rounded rect | Core action step |
| Decision | `#fff2cc` (gold) | Diamond/rhombus | Branch with yes/no labels |
| Data/System | `#e1d5e7` (purple) | Rounded rect | Data store, external system |
| Warning/Error | `#f8cecc` (red) | Rounded rect | Exception path |

## Reference Files

| File | Purpose |
|:-----|:--------|
| `references/pillow-flowchart-generation.md` | Pillow + Noto Sans CJK SC flowchart rendering |
| `references/docx-xml-fix-patterns.md` | python-docx + lxml XML patterns: structural fixes, robust text replacement (cross-run), table rebuilding, column removal, numbering corrections |

## Pitfalls
|---------|-----|
| Inserting paragraphs shifts positions of later headings | Process modules in **REVERSE order** (last module first) |
| `lxml.Element.remove()` fails with "not a child" | Iterate with `list(body)` not `body`; check element is still in tree |
| cairosvg produces blank Chinese text | Use **Pillow** with `Noto Sans CJK SC` font file directly |
| draw.io file fails with XML parse error | HTML tags in `value` must be escaped: `esc(s)` = `s.replace('<','&lt;').replace('>','&gt;')` |
| Chromium export "frame got detached" | Skip Chromium export; deliver `.drawio` files + usage instructions instead |
| Heading 3 style detection fails | The pStyle `val` attribute may be `'Heading3'` (not `'3'`). Check with: `pStyle.get(ns + 'val')` |
| Removing old images from docx | Check tag names in run children for `'drawing'` and `'inline'` (namespace both `ns_w` and `ns_wp`) |
| Text replacement misses split-run content | Use robust method: clear all runs, write full text to first run. See `references/docx-xml-fix-patterns.md` mode 6 |
| Table corruption after add_row/remove row | python-docx can leave empty cells; rebuild via lxml. See mode 7-8 in reference |
| Column count mismatch after reducing table width | Must sync-remove both `tblGrid/gridCol` AND row `tc` elements (mode 8) |

## Incremental Revision of PRD to Align with Policy Documents

When a PRD needs to be updated to match a new policy/regulation document:

1. **Extract both documents** with python-docx (paragraphs + tables)
2. **Diff systematically**: level system, pricing, rules, thresholds, entities
3. **Work in passes**: version/header → structural tables → paragraph text → verification
4. **Use robust replacements** (mode 6) for paragraph text that may span multiple XML runs
5. **Rebuild tables** (mode 7-8) when column count or row structure changes significantly
6. **Multi-pass verification**: scan for stale keywords after each pass to catch residual references

Reference: `references/docx-xml-fix-patterns.md` for all XML manipulation patterns.
