# PRD Incremental Revision: Technical Walkthrough

> **Core rule**: When updating an existing PRD .docx (policy alignment, version bump, module expansion), always use **incremental revision** on the original file. Never read-then-recreate.

## Why This Matters

A real session transcript shows the cost of getting this wrong:

**User**: "小乔，基于最新的XX管理办法文档，完善之前的PRD，重新输出一版。"

**Agent (wrong approach)**: Read both docs → generated fresh Document() → output 60KB with summary content.

**User**: "你看看对比之前的版本，删除了哪些内容"

**Result**: Lost all CC-M05~CC-M15 detailed function point tables, all DS-M01~DS-M15 modules, all 20 flowchart images, all MC-M05~MC-M09 detail tables, all MK-M01~MK-M37 sub-function point tables. File went from ~900KB to 60KB.

**User**: "基于V2.2b原文，用'增量修订'的方式重新生成？保留旧版全部内容，只在需要对齐管理办法的地方做精准替换。"

**Correct approach**: Open original → index → patch paragraphs → insert new sections via lxml → fix tables → save. Final file: 936KB (LARGER than original).

## The 4-Step Workflow

### Step 1: Read Both, Compare, Identify Targets

```python
# Extract full text from both .docx files
import zipfile, xml.etree.ElementTree as ET

def extract_text(path):
    z = zipfile.ZipFile(path)
    tree = ET.parse(z.open('word/document.xml'))
    texts = [''.join(t.text or '' for t in p.iter('{...}t')) 
             for p in tree.iter('{...}p')]
    return '\n'.join(texts)
```

Compare manually:
- Which paragraphs need text replacement?
- Which tables need data updates?
- Which sections need new content?
- Which sections are unchanged (DO NOT TOUCH)?

### Step 2: Index the Original

```python
from docx import Document
doc = Document('original.docx')

# Print every paragraph with index + style
for i, para in enumerate(doc.paragraphs):
    if para.text.strip():
        print(f"P[{i}] [{para.style.name}] {para.text.strip()[:150]}")

# Print every table with header context
for ti, table in enumerate(doc.tables):
    hdr = [c.text.strip()[:30] for c in table.rows[0].cells]
    print(f"TABLE[{ti}] {len(table.rows)}r×{len(table.columns)}c | {hdr}")
```

This gives you exact coordinates for every edit target.

### Step 3: Targeted Paragraph/Table Edits

```python
doc = Document('original.docx')

# Replace specific paragraphs
for i, para in enumerate(doc.paragraphs):
    t = para.text.strip()
    
    # Exact match replacement
    if t == '版本：V2.2（基于V3.7积分模型修正）':
        for r in para.runs: r.clear()
        para.runs[0].text = '版本：V3.0（对齐集团管理办法 2026.06）'
    
    # Contains match replacement
    elif '核心需求文档 V2.2' in t and 'V2.2修正要点' in t:
        for r in para.runs: r.clear()
        para.runs[0].text = '新版完整的修正要点描述...'
    
    # Partial text fix
    elif '畅享¥39/年' in t:
        for r in para.runs:
            if '畅享¥39/年' in (r.text or ''):
                r.text = r.text.replace('¥39/年', '¥39.9/年')

# Replace table cells
for ti, table in enumerate(doc.tables):
    if ti == 18:  # 等级定义表
        # Clear header row
        for ci, h in enumerate(['等级', '认证条件', '核心权益特征']):
            p = table.rows[0].cells[ci].paragraphs[0]
            p.clear()
            p.add_run(h).bold = True
        # Update data rows...
```

### Step 4: Structural Insertions (lxml level)

For inserting entire new sections between existing ones, use lxml on the raw XML:

```python
from lxml import etree
ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
body = doc.element.body

# Find insertion point (e.g., "三、营销中心" Heading1)
target = None
for elem in body:
    if elem.tag == ns + 'p':
        texts = ''.join(elem.itertext())
        if '三、营销中心' in texts:
            pPr = elem.find(ns + 'pPr')
            if pPr is not None:
                pStyle = pPr.find(ns + 'pStyle')
                if pStyle is not None and pStyle.get(ns + 'val') == 'Heading1':
                    target = elem
                    break

pos = list(body).index(target)

# Insert paragraphs BEFORE target (REVERSE order!)
def make_para(text, is_heading=False, level=3):
    """Create a minimal w:p element"""
    p = etree.Element(ns + 'p')
    if is_heading:
        pPr = etree.SubElement(p, ns + 'pPr')
        pStyle = etree.SubElement(pPr, ns + 'pStyle')
        pStyle.set(ns + 'val', f'Heading{level}')
    r = etree.SubElement(p, ns + 'r')
    t = etree.SubElement(r, ns + 't')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return p

insertions = [
    ('heading', '2.2.11 清算与结算管理（V3.0新增）'),
    ('body', '功能ID：MC-M11 | 优先级：P0...'),
    ('body', '需求描述：依据集团管理办法第五章...'),
]
for item_type, text in reversed(insertions):
    p = make_para(text, is_heading=(item_type=='heading'))
    body.insert(pos, p)

# Insert tables similarly...
```

## Critical Rules

1. **Process insertions in REVERSE order** — inserting forward shifts indices of unprocessed targets.
2. **Rebuild `list(body)` after every insertion** — the children iterator goes stale.
3. **Use `addprevious()` on the target element** when inserting before a known anchor, not after a computed index.
4. **python-docx can't read lxml-inserted paragraphs** — `doc.paragraphs` may miss them, but Word/WPS will render them correctly. Verify with raw XML search.
5. **File size must grow** — if the output is smaller than the input, you lost content. Abort and restart.
6. **Never call `Document()` with no arguments** — this is the sign of recreation. Always `Document('original.docx')`.

## Re-save Between Steps

If you mix python-docx API calls with lxml insertions, re-save and re-open between phases:

```python
# Phase A: python-docx paragraph/table edits
doc = Document('original.docx')
# ... edits ...
doc.save('intermediate.docx')

# Phase B: lxml structural insertions  
doc = Document('intermediate.docx')
# ... lxml insertions ...
doc.save('intermediate.docx')

# Phase C: python-docx table row appends
doc = Document('intermediate.docx')
# ... table edits ...
doc.save('final.docx')
```

Mixing without re-save causes `AttributeError: 'lxml.etree._Element' object has no attribute 'tr_lst'` because python-docx's internal state is stale after lxml mutations.

## Real Pitfall Transcript

```
User: "你看看对比之前的版本，删除了哪些内容"
Agent: [runs comparison, finds 100+ missing module IDs]
Agent: "V3.0丢失了大量内容。CC-M05~M15被压缩为概要，DS全部模块丢失，20张流程图完全删除..."
User: "基于V2.2b原文，用'增量修订'的方式重新生成？保留旧版全部内容，只在需要对齐管理办法的地方做精准替换。"
```

**Lesson**: When the user says "完善PRD" or "更新PRD" or "重新输出一版", they mean INCREMENTAL REVISION. The output should be 100% of the original + the changes. Never less.
