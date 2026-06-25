# SPA Reverse-Engineering → PRD

When the user points at a deployed frontend URL (React/Vite/Next.js SPA) and wants a PRD:

## Step 1: HTML Entry Point

```bash
curl -s http://IP/path/ | head -30
```

Extract:
- `<title>` → product name
- `<script>` src → main JS bundle filename
- `<link>` rel=stylesheet → CSS bundle filename
- Framework signature (React: `<div id="root">`, Vue: `<div id="app">`)

## Step 2: Main JS Bundle (index-*.js)

```bash
curl -s http://IP/path/assets/index-XXXXX.js -o /tmp/main.js
```

Extract via Python regex:
- **Routes**: `path:"..."` patterns, component imports (`import("./LoginPage-...")`)
- **Components**: All lazy-loaded chunk filenames (e.g., `LoginPage-*.js`, `AdminDashboard-*.js`)
- **Roles**: Look for constants like `{owner:{label:"车主"...}}` or `Km={...}`
- **Auth**: Token key, localStorage patterns, login function logic
- **Data constants**: Mock data arrays, status enums, default values
- **Lucide icons**: All icon imports reveal feature areas (truck=booking, dollar=payment, wrench=tools)

```python
import re
with open('/tmp/main.js','r') as f: content = f.read()
# Extract component imports
chunks = re.findall(r'import\("\./([^"]+\.js)"\)', content)
# Extract Chinese text
cn = re.findall(r'[\u4e00-\u9fff，。！？、；：（）…—]{4,80}', content)
```

## Step 3: CSS Bundle

```bash
curl -s http://IP/path/assets/index-XXXXX.css -o /tmp/main.css
```

Extract design tokens:
- Framework: `tailwindcss v4.x` or manual CSS
- Colors: `--primary`, `--background`, `--foreground` CSS variables
- Radius: `--radius` value
- Font: `--font-sans`
- Dark mode: `.dark{...}` block

## Step 4: Individual Chunk Files

Download every chunk identified in Step 2:

```bash
for f in LoginPage-*.js AdminDashboard-*.js HomePage-*.js BookingFlow-*.js OrderPageV3-*.js MessagePage-*.js ProfilePage-*.js MyCertificates-*.js OrderDetailCustomer-*.js OrderDetailStaff-*.js; do
  curl -s "http://IP/path/assets/$f" -o "/tmp/$f"
done
```

For each chunk, extract:
- **Chinese UI strings**: All user-visible labels, titles, buttons, placeholders, error messages
- **Form fields**: Input placeholders reveal field names and types
- **State variables**: `useState` calls reveal interactive state
- **Mock data**: Arrays with realistic Chinese names, plates, addresses, phone numbers
- **Status enums**: String literals like `"pending_review"`, `"towing"`, `"completed"`
- **Business rules**: Validation messages, error texts, conditional text

```python
import re
with open(f'/tmp/{chunk_name}','r') as f: content = f.read()
cn = re.findall(r'[\u4e00-\u9fff][\u4e00-\u9fff\w\s，。！？、；：（）…—\.\-\+]{3,120}', content)
states = re.findall(r'\[([a-zA-Z_]+),\s*[a-zA-Z_]+\]\s*=\s*d\.useState', content)
# Sort unique Chinese strings — they reveal all UI labels, prompts, and business terms
for s in sorted(set(cn)): print(s)
```

## Step 5: Compile PRD

Map findings to standard PRD structure:

| Source | Maps To |
|--------|---------|
| CSS tokens | Design System section |
| Routes + component tree | System Architecture |
| Role constants | User Personas |
| Chinese strings per chunk | Function Point tables |
| Mock data arrays | Data Models + Demo Data |
| Status strings | State Machine diagrams |
| Input placeholders | Form Field Specifications |
| Lucide icon imports | Feature inventory (each icon = a capability) |

Key principle: **Every visible piece of the app is recoverable from static assets.** No browser needed. Chinese text in JS bundles is not encrypted — regex extraction yields complete UI spec.
