# Reddit — r/hermesagent 发帖内容

> 复制以下内容 → https://www.reddit.com/r/hermesagent/submit

---

**Title:**

[Skill] PRD-King: Write better PRDs that map 1:1 to prototypes — open source

**Body:**

I've been using Hermes Agent daily for product requirements, and kept running into the same problem: PRDs written for humans don't translate well to AI prototype generation.

So I built a prototype-oriented PRD standard that solves this. It's been battle-tested across several enterprise deliveries, and I just open-sourced it.

**What it is:**

A 10-chapter PRD standard where every section maps directly to DOM elements + interactions + mock data. Not a vague template — each chapter has P0/P1/P2 priority labels so you know what's essential for prototype generation.

**Key features:**

- **8 design systems** — Ant Design (default), Element Plus, TDesign, Arco Design, Semi Design, NutUI, plus WeUI and Apple HIG. Each with CSS token blocks you can copy directly.
- **Two output templates** — VERSION A for client delivery (includes non-functional requirements, API specs, SLA benchmarks, competitive analysis), VERSION B for AI prototype generation (structured data-first, complete mock data + boundary conditions).
- **Phase 0c structured interview** — Before writing, the agent asks 11 targeted questions in 3 groups, skipping anything already known from context research. No back-and-forth, no "what else".
- **14-gate quality checklist** — Run before delivery. If any P0 gate fails, don't ship.
- **5 Bad Pattern detectors** — Catches vague requirements like "supports multiple search methods" or "warehouse management - done".

**Companion project:** `prototype-king` takes the PRD output and runs it through an 8-phase workflow to produce clickable HTML prototypes, with automated verification at ≥90% pass rate.

**For Hermes Agent users:**
```bash
mkdir -p ~/.hermes/skills/product/prd/ && cp -r * ~/.hermes/skills/product/prd/
# Then: "write a PRD" → automatic interview → 10-chapter output
```

**Links:**
- PRD standard: https://github.com/kangedy/prd-king
- Prototype workflow: https://github.com/kangedy/prototype-king

Would love feedback, issues, or PRs!
