# Changelog

## v1.2.0 (2026-06-25)

- 📂 **补齐12个缺失参考文件** — 原SKILL.md引用的spa反向工程/若依逆向/增量修订/竞品分析等文件已全部放入`references/`
- 🔧 **新增PRD结构校验脚本** `scripts/validate-prd.py` — 自动检查PRD是否符合10章标准，输出评分报告
- 🔒 **脱敏处理** — 案例文件中的真实项目名称已替换为通用描述
- 🐛 修复：仓库文件与SKILL.md引用路径不一致问题

## v1.1.0 (2026-06-25)

- 🔀 **项目拆分为两个独立仓库：**
  - `prd-king` — PRD写作标准（本仓库）
  - `prototype-king` — PRD→原型工作流（https://github.com/kangedy/prototype-king）
- 🗑️ 移除本仓库中的 `prototype/` 目录（已迁移至 prototype-king）
- 📖 README 更新为配套项目引用

## v1.0.0 (2026-06-24)

- 🎉 首次发布
- 📐 10章原型导向PRD标准（P0/P1/P2分级）
- 🎨 6大国产+2外部设计体系可选（Ant Design默认）
- 📝 VERSION A 商用交付版 + VERSION B AI原型生成版
- 🗂️ Phase 0c 结构化访谈（3组11问）
- ✅ PRD质量自检表（14项门禁）
- ⚡ 5个Bad Pattern自动拦截
- 📊 非功能需求SLA参考值
