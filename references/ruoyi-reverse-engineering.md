# RuoYi系统反向工程 → PRD 完整工作流

## 适用场景
当目标系统是基于若依(RuoYi)框架（SpringBoot + Shiro + Thymeleaf + Bootstrap）的后台管理系统，且无API文档、无源码时使用。

## 三Pass提取法

### Pass 1: 登录 + 菜单 + 表格列（快速初版）
1. 用curl登录获取session cookie
2. 访问/index获取完整侧边栏菜单HTML → 提取所有模块名和URL路径
3. 遍历每个模块页面，从JS中提取表格列定义（RuoYi用 `{field:'xxx',title:'xxx'}` 格式定义列）
4. 输出V1.0 PRD：模块列表 + 表格列

**关键脚本模式：**
```bash
# 登录
curl -s -c cookie.txt -b cookie.txt -X POST "$base/login" \
  --data-urlencode "username=admin" --data-urlencode "password=xxx"
# 提取菜单
grep -oP '<a class="menuItem" href="[^"]*">[^<]*</a>' index.html
# 提取JS列定义
grep -oP "\{field\s*:\s*'[^']*'.*?title\s*:\s*'[^']*'\}" page.html
```

### Pass 2: 深度表单提取（/add端点）
1. 表格列仅暴露30-50%字段，必须访问 `/{module}/add` 端点获取完整表单
2. 从HTML中提取所有 `name=` 属性 → 完整字段清单
3. 提取 section headers（h5标签）→ 了解表单分区
4. 提取 select options、radio values、checkbox groups
5. 输出V2.0 PRD：完整表单字段

**关键发现：列表列数 vs 表单字段数差距可达3~7倍**（如车辆信息：12列表列 → 83表单字段）

### Pass 3: 校验 + 整合
1. 逐字段对比Pass 1和Pass 2，找出遗漏
2. 检查条件显示逻辑（如：非车管→显示情况说明）
3. 检查hidden字段（图片路径、状态码等）
4. 访问 /edit/{id} 端点验证编辑表单
5. 输出最终PRD

## 常见陷阱

### RuoYi账号锁定
- 5次失败登录 → 锁定10分钟
- **每次登录尝试都重置计时器**
- 解决方案：确认密码后 `sleep 600` 不动登录接口，一次性成功

### 表单分步/Split Forms
- 82字段表单常分布在多步骤中（如5个Step）
- 前端默认只显示Step 1
- 需检查所有 `style="display:none"` 的步骤内容
- **验证方法：** 提取页面中所有 `name=` 属性，而非仅看可见区域

### 子Agent外网限制
- delegate_task的子Agent可能无法访问外部IP（如110.41.34.238）
- 解决方案：主Agent先用curl保存HTML到本地文件，子Agent用read_file解析

### AJAX加载的弹窗表单
- RuoYi的新增/编辑弹窗通过 `$.operate.add()` 加载
- 表单URL模式：`{modulePrefix}/add` 或 `{modulePrefix}/edit/{id}`
- 直接curl访问这些URL可获取完整表单HTML

## 表单字段提取正则

```python
# 所有name属性
names = re.findall(r'name="([^"]*)"', html)
# section headers
sections = re.findall(r'<h5[^>]*>(.*?)</h5>', html)
# radio选项
radios = re.findall(r'type="radio".*?value="([^"]*)".*?>([^<]+)<', row)
# checkbox组
checkboxes = re.findall(r'type="checkbox".*?name="([^"]*)".*?value="([^"]*)"', row)
# select选项
options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', row)
```

## 原型字段验证

创建HTML原型后，验证表单完整性的方法：
```bash
# 统计原型中某模块的表单字段数
grep -oP 'name="[^"]*"' prototype/js/pages.js | sed 's/name="//;s/"//' | sort -u | grep -c 'car\|Car\|Account\|photo'
```
此命令统计页面中所有name属性，比人工目测准确。
