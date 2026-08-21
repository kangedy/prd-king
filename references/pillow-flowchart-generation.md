# Pillow Flowchart Generation for Docx Embedding

Alternative to draw.io when you need to embed flowcharts directly in a `.docx` file as images (PNG). Uses Pillow with Noto Sans CJK SC for reliable Chinese text rendering.

## When to Use

- You need to **automate** flowchart embedding in docx (no manual Word paste step)
- Chinese text must render correctly (cairosvg cannot handle CJK)
- The user only needs to view/print, not edit shapes

## Complete Template

```python
from PIL import Image, ImageDraw, ImageFont
import os

PNG_DIR = "/tmp/flowcharts_png"
os.makedirs(PNG_DIR, exist_ok=True)

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def font(sz, bold=False):
    try: return ImageFont.truetype(FONT_B if bold else FONT, sz)
    except: return ImageFont.load_default()

# Color scheme
BG = "#F8FAFC"
BOX_FILL = "#FFFFFF"
BOX_STROKE = "#CBD5E1"
ACCENT = "#0EA5E9"
TEXT = "#0F172A"
MUTED = "#64748B"
ARROW = "#94A3B8"

# Node type colors (matching draw.io convention)
NODE_COLORS = {
    "start": ("#d5e8d4", "#82b366"),   # green
    "end": ("#d5e8d4", "#82b366"),     # green
    "process": ("#FFFFFF", "#CBD5E1"), # white with gray border
    "data": ("#e1d5e7", "#9673a6"),   # purple
    "warn": ("#f8cecc", "#b85450"),   # red
}

def gen_flowchart_png(name, title, steps, sub_title="", box_w=330, box_h=50, gap=40):
    """Generate a vertical flowchart PNG.
    
    steps: list of (type, label, desc) — type: start|end|process|data|warn
    """
    svg_w = box_w + 80
    svg_h = 80 + 10 + len(steps) * (box_h + gap)
    
    img = Image.new('RGB', (svg_w, svg_h), BG)
    draw = ImageDraw.Draw(img)
    
    # Title
    y = 18
    draw.text((20, y), title, fill=TEXT, font=font(15, True))
    y += 20
    if sub_title:
        draw.text((20, y), sub_title, fill=MUTED, font=font(11))
        y += 16
    
    sy = y + 10
    
    for i, (stype, label, desc) in enumerate(steps):
        x = (svg_w - box_w) // 2
        yp = sy + i * (box_h + gap)
        
        fill, stroke = NODE_COLORS.get(stype, ("#FFFFFF", "#CBD5E1"))
        accent = ACCENT
        
        # Rounded rectangle
        draw.rounded_rectangle([x, yp, x+box_w, yp+box_h], radius=8, fill=fill, outline=stroke, width=2)
        
        # Step number circle
        cx = x + 18
        cy = yp + box_h // 2
        draw.ellipse([cx-9, cy-9, cx+9, cy+9], fill=accent)
        draw.text((cx-5, cy-7), str(i+1), fill="white", font=font(10, True))
        
        # Label
        lx = x + 34
        draw.text((lx, yp+8), label, fill=TEXT, font=font(12, True))
        if desc:
            draw.text((lx, yp+28), desc, fill=MUTED, font=font(10))
        
        # Arrow to next
        if i < len(steps) - 1:
            ax = x + box_w // 2
            ay = yp + box_h
            draw.line([(ax, ay), (ax, ay+gap)], fill=ARROW, width=2)
            draw.polygon([(ax-4, ay+gap-7), (ax+4, ay+gap-7), (ax, ay+gap)], fill=ARROW)
    
    png_path = os.path.join(PNG_DIR, f"{name}.png")
    img.save(png_path, "PNG")
    return png_path

# ===== Embedding in Docx =====
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def embed_flowchart_in_docx(doc, png_path, title_text):
    """Add a flowchart entry (title + image) to the docx."""
    from docx.shared import RGBColor
    
    # Title
    p = doc.add_paragraph()
    r = p.add_run(f"▸ {title_text}")
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x0E, 0xA5, 0xE9)
    
    # Image centered
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(png_path, width=Inches(4.2))
    
    # Spacer
    doc.add_paragraph()
```

## Verifying Chinese Font Rendering

Before batch-generating, verify the font works:

```bash
python3 -c "
from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 14)
img = Image.new('RGB', (400, 100), '#F8FAFB')
d = ImageDraw.Draw(img)
d.text((20, 40), '中文测试 Chinese Test', fill='#0F172A', font=f)
img.save('/tmp/font_test.png')
print('OK - check /tmp/font_test.png')
"
```

## Color Reference

| Type | Fill | Stroke | draw.io equivalent |
|------|------|--------|-------------------|
| start/end | `#d5e8d4` | `#82b366` | Same as draw.io green |
| process | `#FFFFFF` | `#CBD5E1` | White card (draw.io blue `#dae8fc`) |
| data | `#e1d5e7` | `#9673a6` | Same as draw.io purple |
| warn | `#f8cecc` | `#b85450` | Same as draw.io red |
