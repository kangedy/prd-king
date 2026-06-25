# RuoYi SSR (Thymeleaf) System Reverse-Engineering → PRD

When the user points at a **RuoYi-based SSR system** (SpringBoot + Shiro + Thymeleaf + Bootstrap, non-separated version) and wants a PRD.

## Detection Signatures

```
HTML title often empty, body class="signin"
CSS: /ruoyi/css/ry-ui.css?v=4.7.2
JS:  /ruoyi/js/ry-ui.js?v=4.7.2
Meta: <meta name="renderer" content="webkit">
JS check: if(window.top!==window.self){...redirect to login}
Copyright in footer, e.g., "Copyright © 2023 迅捷信息科技南通有限公司"
Product name in login page H4 heading
```

## Step 1: Login Page Analysis

```bash
curl -s http://IP:PORT/index | head -80
```

Extract:
- Product name from `<h4>` text
- Tech stack from commented HTML (SpringBoot, Mybatis, Shiro, Thymeleaf, Bootstrap)
- Login form fields (username, password, validateCode)
- Whether captcha is enabled

## Step 2: Static Asset Mining (Pre-Login)

Even without login, extract module hints from JS/CSS:

```bash
# ry-ui.js contains custom business field selectors and API paths
curl -s http://IP:PORT/ruoyi/js/ry-ui.js | grep -oP '(ctx\s*\+\s*"[^"]*")' | sort -u
curl -s http://IP:PORT/ruoyi/js/ry-ui.js | grep -oP '#[a-zA-Z_][a-zA-Z0-9_]*' | sort -u
```

Key patterns to look for:
- `ctx + "system/xxx/export"` → module API paths
- `$("#carNos")`, `$("#hphm")`, `$("#hpzl")` → business field names
- `$("#supervisedCar")`, `$("#carDifferentplaces")` → feature selectors

## Step 3: Route Discovery (Pre-Login)

Probe common module paths. RuoYi returns **302 → /login** for protected routes:

```bash
for path in "/system/car" "/system/car/list" "/system/part" "/system/stock"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://IP:PORT${path}")
  [ "$code" = "302" ] && echo "EXISTS: $path"
done
```

A 302 means the route is registered in Shiro — the module exists.

## Step 4: Login (Critical — Account Lock Pitfall)

**PITFALL**: RuoYi's Shiro auth locks the account for 10 minutes after **5 failed password attempts**. The lock timer may reset with each new attempt. Strategy:
- Get the CORRECT password from the user before attempting
- Acquire session cookie first (GET /login) then POST credentials
- Only make ONE login attempt — if it fails, ask user immediately, do NOT brute-force

```bash
# Correct login flow
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt "http://IP:PORT/login" -o /dev/null
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt \
  -X POST "http://IP:PORT/login" \
  --data-urlencode "username=admin" \
  --data-urlencode "password=THEPASSWORD" \
  --data-urlencode "rememberMe=false"
# Success response: {"code":0} → redirect to /index
```

If locked: sleep 600 seconds WITHOUT making any login attempts (each attempt resets timer).

## Step 5: Menu Tree Extraction (Post-Login)

After login, access the main page to get the full sidebar menu:

```bash
curl -s -b /tmp/cookies.txt "http://IP:PORT/index" | grep -A2 'menu-item'
```

RuoYi renders menus as nested `<li>` elements with `data-url` attributes. Extract:
- All menu item names (Chinese labels)
- All route paths (data-url values)
- Menu hierarchy (parent-child nesting)

## Step 6: Module Page Extraction

For each discovered route, fetch the page and extract:

```bash
curl -s -b /tmp/cookies.txt "http://IP:PORT/system/xxx" > /tmp/page.html
```

Extract from each page:
- **Table columns**: `<th>` elements in bootstrap-table headers
- **Search form fields**: `<input>`, `<select>` in search forms
- **Form fields (add/edit)**: Inputs in modal/dialog forms
- **Button actions**: 新增/修改/删除/导出/导入 buttons
- **Dictionary references**: `dictType="..."` attributes for data enums

## Step 7: Data Dictionary Extraction

RuoYi stores status enums in data dictionaries. Extract them:

```bash
# Common dict types to probe
for dt in "sys_yes_no" "sys_show_hide" "sys_normal_disable"; do
  curl -s -b /tmp/cookies.txt "http://IP:PORT/system/dict/data/type/${dt}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d)"
done
```

Look for custom dict types referenced in page templates (e.g., `dictType="car_status"`).

## Step 8: Compile PRD

Map findings:

| Source | Maps To |
|--------|---------|
| Menu tree | System Architecture + Module List |
| Table `<th>` elements | Data Model fields per entity |
| Search form fields | Query/filter specifications |
| Add/Edit form fields | Full entity field definitions |
| Dict types | Status enums and dropdown options |
| Button actions | CRUD operations per module |
| `exportUrl` in JS | Report/export features |
```
