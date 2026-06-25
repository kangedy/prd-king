#!/usr/bin/env python3
"""PRD 结构校验脚本 — 检查输出的 PRD 是否符合 10 章原型导向标准
用途：交付前自动校验 PRD 文档完整性，确认所有 P0 章节已覆盖
用法：python3 validate-prd.py <prd-file.md>
退出码：0=通过 1=不通过
"""
import os, re, sys

# Windows GBK 兼容
if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

REQUIRED = {
    'Ch1 设计规范': [
        (r'--brand-primary|primary.*color|主色', '品牌主色已定义'),
        (r'--font-body|font-size.*14|字号|14px', '正文字号已定义'),
        (r'Ant Design|Element Plus|TDesign|Arco|Semi|NutUI|设计体系|设计规范', '设计体系已指定'),
    ],
    'Ch2 信息架构': [
        (r'├──|└──|导航|菜单|sidebar|侧栏', '导航结构存在'),
        (r'角色|权限|role|admin|operator|merchant', '角色-权限映射存在'),
        (r'默认|首页|dashboard|data-page=', '默认落地页已指定'),
    ],
    'Ch3 业务流程': [
        (r'流程|flow|→|->', '核心流程已定义'),
        (r'异常|失败|驳回|超时|error|fail', '异常流程已处理'),
    ],
    'Ch5 页面清单': [
        (r'data-page|页面清单|Page Inventory', '页面清单存在'),
        (r'布局|table|form|modal|detail|看板|表格', '布局类型已标注'),
    ],
    'Ch6 功能点': [
        (r'Search|Modal|Navigation|Download|Submit|Batch|操作类型|功能点', '操作类型已标注'),
        (r'触发|点击|click|勾选', '触发方式已明确'),
        (r'搜索|筛选|search|filter|查询条件', '搜索条件已定义'),
    ],
    'Ch7 数据模型': [
        (r'字段|field|column|类型|string|number|enum|boolean', '字段定义存在'),
        (r'必填|required|必填项', '必填约束已标注'),
        (r'校验|validate|regex|正则|≥|长度|范围', '校验规则已定义'),
    ],
    'Ch8 Mock数据': [
        (r'MOCK|mock|模拟数据|Mock Data', 'Mock数据池存在'),
        (r'空|empty|无数据|极限|long', '空态/极限态已考虑'),
    ],
    'Ch10 验收标准': [
        (r'List|Detail|Action|验收|Acceptance', '验收标准已定义'),
        (r'门禁|gate|check|通过标准', '验收门禁已设置'),
    ],
}

OPTIONAL = {
    'Ch4 系统架构': [(r'权限|数据流向|接口格式|API', '权限/数据流向已说明')],
    'Ch9 边界条件': [(r'边界|异常|无权限|网络|并发|溢出|精度', '边界条件已覆盖')],
}

def G(t): return f"\033[92m{t}\033[0m"
def R(t): return f"\033[91m{t}\033[0m"
def Y(t): return f"\033[93m{t}\033[0m"

def check_prd(content, file_path):
    results = []
    all_pass = True

    # P0 章节必须通过
    for chapter, checks in REQUIRED.items():
        chapter_ok = True
        for pattern, desc in checks:
            if re.search(pattern, content, re.IGNORECASE):
                results.append((chapter, f"  {G('✅')} {desc}", True))
            else:
                results.append((chapter, f"  {R('❌')} 缺失: {desc}", False))
                chapter_ok = False
        if chapter_ok:
            results.append((chapter, f"  {G('━━━')} {chapter} 全部通过", True))
        else:
            results.append((chapter, f"  {R('━━━')} {chapter} 部分缺失", False))
            all_pass = False

    # P1/P2 章节建议有
    for chapter, checks in OPTIONAL.items():
        any_pass = False
        for pattern, desc in checks:
            if re.search(pattern, content, re.IGNORECASE):
                results.append((chapter, f"  {G('✅')} {desc}", True))
                any_pass = True
        if not any_pass:
            results.append((chapter, f"  {Y('⚠️')} 建议补充: {chapter} 相关内容", True))

    return all_pass, results

def main():
    if len(sys.argv) < 2:
        print("用法: python3 validate-prd.py <prd-file.md>")
        print("示例: python3 validate-prd.py my-prd.md")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"{R('❌')} 文件不存在: {path}")
        sys.exit(1)

    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    print(f"\n{'╔' + '═'*50 + '╗'}")
    print(f"{'║':<1}{'PRD · 10章结构校验报告':^48}{'║':>1}")
    print(f"{'╠' + '═'*50 + '╣'}")
    print(f"{'║ 文件: ' + os.path.basename(path):<50}{'║':>1}")
    print(f"{'║ 行数: ' + str(len(content.splitlines())):<50}{'║':>1}")
    print(f"{'╠' + '═'*50 + '╣'}")

    all_pass, results = check_prd(content, path)
    last_chapter = ''
    for chapter, msg, passed in results:
        if chapter != last_chapter:
            last_chapter = chapter
        print(f"{'║':<1}{msg:<50}{'║':>1}")

    total = sum(1 for r in results if r[0] in REQUIRED)
    passed = sum(1 for r in results if r[2] and r[0] in REQUIRED)
    pct = round(passed / max(total, 1) * 100)

    print(f"{'╠' + '═'*50 + '╣'}")
    print(f"{'║ 得分: ' + str(pct) + '%  (P0门禁通过率)':<50}{'║':>1}")
    if all_pass and pct >= 80:
        verdict = f"{'✅ PRD结构完整，可交付'}  "
    elif pct >= 60:
        verdict = f"{'⚠️ P0章节部分缺失，建议补充后交付'}  "
    else:
        verdict = f"{'❌ P0章节大量缺失，请补充关键章节'}  "
    print(f"{'║ 判定: ' + verdict:<50}{'║':>1}")
    print(f"{'╚' + '═'*50 + '╝'}")
    sys.exit(0 if all_pass and pct >= 80 else 1)

if __name__ == '__main__':
    main()
