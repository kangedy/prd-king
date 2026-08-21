# 开源发布 · 安全审查清单

> 将 Hermes Agent 技能或项目文档发布到 GitHub 等公开仓库前，逐项检查。
> 全部检查通过后再 push。

---

## 敏感信息检查（逐文件）

### 1. 公司/品牌名称

```
❌ 真实公司名、品牌名、店铺名
❌ 客户/甲方名称
❌ 合作伙伴名称
✅ 替换为：通用名（"某公司""某集团""某商家"）或虚构名

命令检查：grep -n -E "公司|集团|有限|科技|店铺|汽修|汽配|连锁" *.md *.html *.py 2>/dev/null
```

### 2. 真实项目信息

```
❌ 真实项目名称/代号
❌ 具体版本号（V2.2 → 改为"旧版"）
❌ 具体时间线（"7月底" → 改为"第一期"）
✅ 替换为：通用描述，仅保留可复用的方法论
```

### 3. 商业数据

```
❌ 具体金额（"¥39.9" → 改为"基础档"）
❌ 具体数据量（"21TB" → 改为"数TB"）
❌ 具体用户数（"50万+" → 改为"数十万"）
❌ 具体价格/费率
✅ 替换为：模糊范围或删除
```

### 4. 联系方式与技术凭证

```
❌ 手机号、邮箱、URL/IP地址
❌ API Key / Token / 密钥
❌ 数据库/SaaS 连接信息
✅ 替换为：占位符或引用 .env.example
```

### 5. 文件引用一致性

```
❌ SKILL.md 引用了不存在的 references/*.md
✅ 发布前检查：
  grep -oP 'references/[a-zA-Z0-9_-]+\.md' SKILL.md | sort -u > /tmp/refs.txt
  ls references/ > /tmp/existing.txt
  comm -23 /tmp/refs.txt /tmp/existing.txt  # 列出缺失文件
```

---

## 一键安全检查

```bash
# 在仓库根目录运行
echo "=== 公司名称 ===" && grep -rn -i "公司\|集团\|有限\|科技\|店铺" . --include="*.md" --include="*.html" --include="*.py" 2>/dev/null | grep -v node_modules | grep -v .git
echo "=== 联系方式 ===" && grep -rn -E "[0-9]{11}|@example|@test" . --include="*.md" --include="*.html" 2>/dev/null | grep -v node_modules | grep -v .git
echo "=== URL/IP ===" && grep -rn -E "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" . --include="*.md" --include="*.html" 2>/dev/null | grep -v node_modules | grep -v .git
echo "=== 缺失引用 ===" && grep -oP 'references/[a-zA-Z0-9_-]+\.md' SKILL.md 2>/dev/null | sort -u > /tmp/_refs && ls references/ > /tmp/_existing && comm -23 /tmp/_refs /tmp/_existing
```
