# PRD docx 修复模式 — python-docx + lxml XML操作

> 适用于：修正PRD docx中的编号错误、缺失段落、章节重建、表格内容替换等结构化修复
> 不适用：内容增删（走正常python-docx API）

## 核心原理

python-docx 的 paragraph/run API 对复杂操作支持有限。以下场景必须走 lxml XML 直接操作：

1. 在两个段落之间插入新段落
2. 删除指定范围的段落和表格
3. 将纯文本段落升格为 Heading
4. 替换表格中分散在多个 run 中的编号文本

## 必备导入

```python
import docx
from lxml import etree
import copy

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
```

## 模式1：段落间插入

```python
body = doc.element.body
# 在 ref_elem 之前插入
body.insert(list(body).index(ref_elem), new_elem)
```

## 模式2：创建带样式的段落

```python
# 克隆现有 heading 元素并替换文本
ref_h2 = doc.paragraphs[0]._element  # 找一个已有的 Heading 2
def make_h2(text):
    h = copy.deepcopy(ref_h2)
    for r in h.findall(f'{{{W}}}r'):
        h.remove(r)
    r = etree.SubElement(h, f'{{{W}}}r')
    t = etree.SubElement(r, f'{{{W}}}t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return h

def make_para(text):
    p = etree.Element(f'{{{W}}}p')
    r = etree.SubElement(p, f'{{{W}}}r')
    t = etree.SubElement(r, f'{{{W}}}t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return p
```

**注意：** 插入顺序与最终显示顺序相反。在同一个 insert_pos 依次插入 A、B、C，最终顺序为 C、B、A。要让最终顺序为 A、B、C，需 `for block in reversed([A, B, C]): body.insert(pos, block)`。

## 模式3：段落升格为 Heading

```python
# 将纯文本段落改为 Heading 3
pPr = p._element.find(f'{{{W}}}pPr')
if pPr is None:
    pPr = etree.SubElement(p._element, f'{{{W}}}pPr')
    p._element.insert(0, pPr)
pStyle = pPr.find(f'{{{W}}}pStyle')
if pStyle is None:
    pStyle = etree.SubElement(pPr, f'{{{W}}}pStyle')
pStyle.set(f'{{{W}}}val', 'Heading3')
```

## 模式4：批量删除区间

```python
body = doc.element.body
all_kids = list(body)
start = all_kids.index(start_elem)
end = all_kids.index(end_elem)
for elem in all_kids[start:end]:
    body.remove(elem)
```

## 模式5：表格单元格文本替换

```python
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    if 'old_text' in run.text:
                        run.text = run.text.replace('old_text', 'new_text')
```

## 模式6：鲁棒全文本替换（处理跨run分散文本）

当文本跨越多个 `<w:r>` 元素时，run级别的替换会失败。鲁棒方法是清空所有runs，将完整替换文本写入第一个run：

```python
def robust_paragraph_replace(doc, old_text, new_text):
    """替换段落中文本，即使文本分散在多个XML run中"""
    for p in doc.paragraphs:
        if old_text in p.text:
            # 清空所有runs
            for run in p.runs:
                run.text = ""
            # 完整替换文本写入第一个run
            if p.runs:
                p.runs[0].text = p.text.replace(old_text, new_text)
```

同样适用于表格单元格：

```python
def robust_cell_replace(table, row_idx, col_idx, old, new):
    cell = table.rows[row_idx].cells[col_idx]
    if old in cell.text:
        for p in cell.paragraphs:
            for r in p.runs:
                r.text = ""
            if p.runs:
                p.runs[0].text = cell.text.replace(old, new)
```

## 模式7：通过 lxml 重建损坏的表格

当 python-docx 的 `table.add_row()` / `row._element.getparent().remove()` 操作导致表格结构损坏（单元格消失、行数不对），直接用 lxml 重建整表：

```python
from lxml import etree

def rebuild_table(tbl_elem, header, data_rows):
    """完全重建表格：删除所有行，用lxml重新构建"""
    W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    # 删除所有现有行
    for row in list(tbl_elem.findall(f'{{{W}}}tr')):
        tbl_elem.remove(row)
    
    def make_row(cell_texts):
        tr = etree.SubElement(tbl_elem, f'{{{W}}}tr')
        for ct in cell_texts:
            tc = etree.SubElement(tr, f'{{{W}}}tc')
            p = etree.SubElement(tc, f'{{{W}}}p')
            r = etree.SubElement(p, f'{{{W}}}r')
            t = etree.SubElement(r, f'{{{W}}}t')
            t.text = ct
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        return tr
    
    make_row(header)
    for row_data in data_rows:
        make_row(row_data)
```

## 模式8：删除表格多余列（gridCol + tc 同步移除）

当表格需要从 N 列缩减为 M 列（如6级会员→3级），必须同时删除 `tblGrid` 中的 `gridCol` 和每行的 `tc` 元素：

```python
def remove_table_columns(table, keep_cols):
    """保留前 keep_cols 列，删除其余列"""
    tbl = table._tbl
    W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    # 1. 删除多余的 gridCol
    tblGrid = tbl.find(f'{{{W}}}tblGrid')
    if tblGrid is not None:
        for gc in list(tblGrid.findall(f'{{{W}}}gridCol'))[keep_cols:]:
            tblGrid.remove(gc)
    
    # 2. 删除每行多余的 tc
    for row in table.rows:
        cells = row._element.findall(f'{{{W}}}tc')
        for tc in cells[keep_cols:]:
            row._element.remove(tc)
```

## 常见坑

| 坑 | 现象 | 原因/修复 |
|:---|:-----|:----------|
| 插入后段落不可见 | 段落存在但Word不显示 | 元素缺少 `rsidR` 等属性。克隆现有段落保留所有属性 |
| 插入顺序反了 | 内容按插入逆序排列 | 对列表 reverse 后再插入 |
| `etree.SubElement` 报 tag 无效 | `ValueError: Invalid tag name` | namespace 拼接错误，用 `f'{{{W}}}p'` 而非 `W + 'p'` |
| 替换后部分文本未变 | 只有部分 run 被替换 | 文本可能分散在多个 run 中，需用模式6清空全部run后重写 |
| `p.text.strip()` 返回 `None` | `AttributeError` | 某些元素删除后段落变为 None，先判空 `if p and p.text` |
| `table.add_row()` 后单元格为空 | 新增行cells=0 | python-docx在某些删除后状态不一致；用模式7 lxml重建 |
| 删除行后再add_row导致列数错 | 新旧行列数不匹配 | 用模式8同时更新gridCol和tc |
