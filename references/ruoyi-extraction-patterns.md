# RuoYi System PRD Extraction — Field Reference

Real extraction patterns from 鑫广再生资源汽车拆解系统 (2026-06).

## Menu Extraction

```python
# Extract parent menu groups
parent_groups = re.findall(
    r'<a href="#" data-refresh="false">\s*<i class="fa ([^"]*)"></i>\s*<span class="nav-label">([^<]+)</span>\s*<span class="fa arrow"></span>\s*</a>\s*<ul class="nav nav-second-level collapse">(.*?)</ul>',
    html, re.DOTALL
)
# Extract sub-items
sub_items = re.findall(r'<a class="menuItem" href="([^"]*)"[^>]*>([^<]*)</a>', sub_html)
```

## Table Column Extraction

```python
# Bootstrap-table columns are in JS, not HTML
js_cols = re.findall(r"\{[^}]*field\s*:\s*'([^']*)'[^}]*title\s*:\s*'([^']*)'[^}]*\}", html)
```

## Form Field Extraction from /add pages

```python
# ALL name attributes (including hidden)
all_names = re.findall(r'name="([^"]*)"', html)

# Table-row label + field pairs
rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
for row in rows:
    th = re.search(r'<th[^>]*>(.*?)</th>', row, re.DOTALL)
    inp = re.search(r'name="([^"]*)"', row)
    radio = re.search(r'type="radio"[^>]*name="([^"]*)"', row)
    select_opts = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', row)
```

## Typical Field Count Discrepancy

| Module | Table Columns (list page) | Form Fields (/add page) | Ratio |
|:-------|:------------------------:|:----------------------:|:-----:|
| 车辆信息录入 | 12 | **83** | 6.9x |
| 订单管理 | 30 | 20 | 0.7x (form simpler than table) |
| 称重管理 | 21 | 15 | 0.7x |
| 客户信息 | 18 | 18 | 1.0x |

Key insight: Vehicle info has the largest gap because most fields are in the add/edit modal, not visible in the list view.

## Hidden Field Types Found

- Photo/image paths (photoDriving, photoUsercard, etc.)
- Auto-sync fields (hidden copies of visible select values)
- Checkbox aggregations (JS merges multiple checkboxes into one comma-separated hidden input)
- Status codes (stateName visible, carState hidden)
- OCR-fillable fields (carFramenumber hidden, filled by VIN OCR)

## Conditional Display Patterns

- `display:none` sections shown based on radio selection (e.g., battery section when EV selected)
- Fields with `class="qikuang"` that show/hide based on 报废类型 selection
- Required fields that become conditionally required (agent info only when haveAgent=yes)

## Account Locking

RuoYi Shiro: 5 failed attempts → 10-minute lock. Each attempt resets timer.
Always wait full 10 minutes without touching login endpoint.
