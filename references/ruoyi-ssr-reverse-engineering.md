# RuoYi / Thymeleaf SSR Admin System Reverse-Engineering → PRD

When the user points at a deployed RuoYi (若依) admin system and wants a PRD. These are Thymeleaf SSR apps — NOT React/Vite SPAs, so the SPA reverse-engineering approach won't work.

## Key differences from SPA reverse-engineering

| Aspect | SPA (React/Vue) | RuoYi SSR (Thymeleaf) |
|--------|----------------|-----------------------|
| Entry | JS bundle → routes | Login page → sidebar HTML |
| Auth | JWT/Token in localStorage | Shiro session cookie |
| Menu | Route config in JS | `<ul class="nav" id="side-menu">` in HTML |
| Table columns | Component templates in chunks | `{field:'x', title:'y'}` in page-level `<script>` |
| Data loading | API calls from JS | Server-side rendered + AJAX bootstrap-table |

## Step-by-step workflow

### Step 1: Identify the system

```bash
curl -s http://IP:PORT/index | head -50
```

Look for:
- `<title>` or page heading → system name
- RuoYi signature: `/ruoyi/js/ry-ui.js`, `/ruoyi/css/ry-ui.css`, `ctx` variable
- Tech stack hints in HTML comments or login page
- Copyright info in footer

### Step 2: Login and capture session

RuoYi uses Shiro form-based auth with session cookies:

```bash
# Get session cookie first
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt "http://IP:PORT/login" -o /dev/null

# POST login credentials (use --data-urlencode for special chars)
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt \
  -X POST "http://IP:PORT/login" \
  --data-urlencode "username=admin" \
  --data-urlencode "password=xxx" \
  --data-urlencode "rememberMe=false"
```

Success response: `{"msg":"操作成功","code":0}`
Failure: `{"msg":"用户不存在/密码错误","code":500}`

**PITFALL: Account lockout.** RuoYi locks accounts after 5 failed attempts for 10 minutes. Each failed attempt resets the timer. If locked, wait 600s without any login attempts before retrying.

### Step 3: Extract full menu structure

After login, access the main page:

```bash
curl -s -b /tmp/cookies.txt "http://IP:PORT/index" > /tmp/index.html
```

Extract the sidebar menu using regex. RuoYi menus have this structure:

```html
<li>
  <a href="#" data-refresh="false">
    <i class="fa fa-icon"></i>
    <span class="nav-label">一级菜单名</span>
    <span class="fa arrow"></span>
  </a>
  <ul class="nav nav-second-level collapse">
    <li>
      <a class="menuItem" href="system/xxx">子菜单名</a>
    </li>
  </ul>
</li>
```

Use a Python regex to extract:

```python
pattern = r'<a href="#" data-refresh="false">\s*<i class="fa ([^"]*)"></i>\s*<span class="nav-label">([^<]+)</span>\s*<span class="fa arrow"></span>\s*</a>\s*<ul class="nav nav-second-level collapse">(.*?)</ul>'
groups = re.findall(pattern, html, re.DOTALL)

for icon, label, sub_html in groups:
    sub_items = re.findall(r'<a class="menuItem" href="([^"]*)"[^>]*>([^<]*)</a>', sub_html)
```

### Step 4: Batch-scrape table columns from JavaScript

RuoYi uses bootstrap-table with columns defined in page-level `<script>` blocks. Table headers in the HTML `<th>` are often empty or template-only — the real column definitions are in JS.

Use execute_code for efficient batch scraping:

```python
from hermes_tools import terminal
import re

for label, path in pages:
    html = terminal(f"curl -s -b {cookie_file} --max-time 10 '{base}{path}'")['output']
    
    # Method 1: Extract from JS column definitions (most reliable)
    js_cols = re.findall(r"\{[^}]*field\s*:\s*'([^']*)'[^}]*title\s*:\s*'([^']*)'[^}]*\}", html)
    
    # Method 2: Extract from <th data-field="...">
    th_cols = re.findall(r'<th[^>]*data-field="([^"]*)"[^>]*>(.*?)</th>', html)
```

This approach can scrape 60+ pages in ~5 seconds.

### Step 5: Extract search form fields

```python
# Search inputs
search_inputs = re.findall(r'<input[^>]*name="([^"]*)"[^>]*placeholder="([^"]*)"', html)

# Search selects
search_selects = re.findall(r'<select[^>]*name="([^"]*)"', html)
```

### Step 6: Compile PRD

Map findings:

| Source | Maps To |
|--------|---------|
| Page title | System identification |
| Menu hierarchy | Module inventory + architecture |
| JS column definitions | Table/field specifications |
| Search form fields | Query parameters |
| Page relationships | Data flow / dependencies |
| Field naming patterns | Domain model inference |

## Pitfalls

1. **Account lockout** — Wait 10 full minutes without ANY login attempts after lock. Each failed attempt resets the timer.
2. **Thymeleaf templates are empty** — Don't expect to find data in `<th>` elements. Columns are in JS.
3. **Mixed path styles** — Some menuItem hrefs start with `/`, some don't. Normalize when constructing URLs.
4. **Session expiry** — RuoYi sessions can expire. Re-login if pages start returning login HTML instead of data.
5. **Same endpoint, different data** — RuoYi uses the same URL pattern for different states (e.g., `/system/status/preliminary/305` vs `/308` for different vehicle states). The number suffix is the state code.
6. **FIRST PASS IS ALWAYS INCOMPLETE** — The user will say "对比原系统发现少了很多字段和功能入口". A single pass only extracts table columns from JS. Missing: form labels, buttons, select options, hidden modals, sub-tabs, detail pages. ALWAYS plan a second deep pass.

## Two-Pass Extraction Pattern (CRITICAL)

### Pass 1 — Structure overview
Extract table columns from JS — this gives you the page structure and field count. This is fast (~5s for 60 pages).

### Pass 2 — Deep extraction (MANDATORY)
For every page, extract ALL UI elements:

```python
# Buttons reveal sub-functions not on the menu
buttons = re.findall(r'<button[^>]*>([^<]+)</button>', html)
btn_links = re.findall(r'<a[^>]*class="[^"]*btn[^"]*"[^>]*>([^<]+)</a>', html)

# Select options reveal data dictionary values
selects = re.findall(r'<select[^>]*name="([^"]*)"[^>]*>(.*?)</select>', html, re.DOTALL)

# Form labels reveal add/edit form fields
labels = re.findall(r'<label[^>]*>([^:<]+)(?::)?</label>', html)

# Search inputs with placeholders
inputs = re.findall(r'<input[^>]*name="([^"]*)"[^>]*placeholder="([^"]*)"', html)
```

**Signals that a page has hidden sub-functions:**
- Multiple buttons in the header area (e.g., 5 buttons on 产物入库方式一 = 5 sub-workflows)
- Buttons with labels like "上传XX证明", "打印XX", "XX条码打印" — each is a separate action
- Large page size (>30KB) with few extracted columns → likely has modals/detail views
- Column count > 30 → likely an export/detail page (check for export URL patterns)

**Column count heuristics for RuoYi systems:**
- 10-20 columns → standard list page
- 20-35 columns → detail page or rich list with financial fields
- 35-50+ columns → comprehensive export page for external systems

## Three-Pass Extraction Pattern (CRITICAL — updated)

### Pass 1 — Structure overview
Extract table columns from JS — this gives you the page structure and field count. This is fast (~5s for 60 pages).

### Pass 2 — Deep UI extraction
For every page, extract ALL UI elements: buttons (→ sub-functions), select options (→ data dictionary), form labels (→ add/edit fields), search inputs.

### Pass 3 — Form-level extraction via /add and /edit endpoints (MANDATORY for complete field lists)

This is the **final critical pass** that discovers fields invisible in list pages. RuoYi admin forms are served as standalone HTML pages at `/modulePath/add` and `/modulePath/edit/{id}`. Each returns a complete form with ALL fields including hidden inputs, conditional fields, nested tables, and radio/checkbox groups.

**Why Pass 3 is necessary:**
- List pages only show ~30-50% of total fields (table columns in JS definitions)
- Add/Edit forms contain hidden fields, conditional fields (shown/hidden based on radio selections), nested sub-tables, and photo upload inputs — these are NEVER visible in list view
- Real discovery: 车辆信息录入 list shows 12 columns but the `/add` form has **83 fields** — a 7x difference

**How to extract:**

```bash
# Step 1: Identify all module paths from menu extraction (Pass 1)
# Step 2: For each module, try the /add endpoint
for path in /system/carinfo/shxg /system/carorder /system/cooperation /system/spic1rk /system/spo; do
  code=$(curl -s -o /tmp/form_${name}.html -w "%{http_code}" -b cookies "$base${path}/add")
  echo "$path/add: HTTP $code"
done

# Step 3: Parse each form HTML
```

**Python extraction for add/edit forms:**

```python
with open('/tmp/form_vehicle_add.html') as f:
    html = f.read()

# Extract ALL name attributes (including hidden fields)
all_fields = re.findall(r'name="([^"]*)"', html)

# Extract label+field pairs from table rows
rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
for row in rows:
    th = re.search(r'<th[^>]*>(.*?)</th>', row, re.DOTALL)
    names = re.findall(r'name="([^"]*)"', row)
    radios = re.findall(r'type="radio"[^>]*value="([^"]*)"[^>]*>\s*<i></i>([^<]+)', row)
    selects = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', row)
    required = 'is-required' in row
    
    if th and names:
        label = re.sub(r'<[^>]+>', '', th.group(1)).strip()
        print(f"{label} | {names[0]} | {'required' if required else ''}")
        if radios: print(f"  Options: {radios}")
```

**Form structure patterns in RuoYi:**
- Forms use `<table class="table table-bordered">` with `<th>` (labels, right-aligned, green text) and `<td>` (inputs)
- Sections divided by `<h5>` headers
- Hidden fields declared at top of form with `type="hidden"`
- Conditional sections have `style="display:none"` and are toggled via radio button JS
- Checkbox groups use multiple `<input type="checkbox">` with JS that merges values into a hidden field
- Select options loaded dynamically via AJAX but option values ARE in the HTML `<option>` tags

**Page size heuristics:**
- 2-8KB → simple form (1-5 fields)
- 8-25KB → standard form (5-20 fields)
- 25-80KB → complex form (20-40 fields, has conditional sections)
- 80KB+ → very complex form (40-80+ fields, has nested tables, photo uploads, multiple conditional sections)

**For forms that return 404 on /add:**
Try alternative patterns: `/edit/1`, or check if the module uses inline editing without a dedicated form page. Some modules (like 商务部车辆管理) use a different URL structure.

**Delegate extraction to sub-agents for scale:**
When you have 15+ form pages to extract, use delegate_task to spawn parallel workers. Save the HTML files locally first (sub-agents may not have external HTTP access), then pass file paths to each sub-agent with specific extraction instructions.

### Pass summary

| Pass | Source | Finds | Time |
|------|--------|-------|------|
| 1 | List page JS | Table columns | ~5s for 60 pages |
| 2 | List page HTML | Buttons, selects, search fields | ~5s for 60 pages |
| 3 | /add and /edit endpoints | Complete form fields (hidden, conditional, nested) | ~2-5s per page |

**Golden rule**: NEVER claim a PRD is complete after Pass 1 or Pass 2. The user WILL compare against the original system and find missing fields. Always execute Pass 3 before calling the PRD "complete".
