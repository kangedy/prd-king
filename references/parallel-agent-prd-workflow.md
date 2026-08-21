# 多Agent并行PRD生成工作流

## 适用场景
- 大型PRD（1,000+功能点，10+模块）
- 已有完整功能点清单Excel
- 已有业务规则文档（如docx）
- 需要100%覆盖所有功能点

## 前置准备

### 1. 数据预提取（关键——避免Agent超时）

**不要**让子Agent自己读Excel。主Agent先提取功能点数据，聚合为结构化的模块层次：

```python
# 主Agent提取
import openpyxl
wb = openpyxl.load_workbook('功能清单.xlsx', data_only=True)
ws = wb['功能清单']
# 按一级模块分组，统计每模块点数+类型比例
# 输出到临时文件或直接嵌入delegate context
```

提取内容格式（嵌入到context中）：
```
### 模块名 (总点数)
**子模块A (N点)**: 功能点类型比例 ILF×N/EI×N/EQ×N/EO×N
**子模块B (M点)**: ...
```

### 2. 模块分组

将模块按独立场景分组，确保：
- 每组不超过600点（避免单Agent负担过重）
- 每组内的模块在业务上关联（如"活动+优惠券"、"商户+商品+风控"）
- 组间无共享状态（不同模块写入不同Part文件）

### 3. 规则文档预处理

先读取docx/规则文档，提取核心规则摘要嵌入context：
- 积分规则（兑换比例、有效期、发放规则）
- 优惠券规则（分类、有效期限、核销规则、退还规则）
- 结算规则（轧差逻辑、结算周期）
- 风控规则（黑白名单、频次限制、违规分级）

## 执行流程（2波次）

### Wave 1: 并行3 Agent

```
delegate_task(tasks=[
  {goal: "PRD Part1", context: "模块A+B + 预提取数据 + 规则摘要"},
  {goal: "PRD Part2", context: "模块C+D + 预提取数据 + 规则摘要"},
  {goal: "PRD Part3", context: "模块E+F + 预提取数据 + 规则摘要"},
])
```

每个Agent输出独立文件（如prd_part1_xxx.md），包含：
- Ch5 页面清单
- Ch6 功能点清单（逐模块，每条标注操作类型EI/ILF/EQ/EO/EIF）
- Ch7 数据模型
- Ch8 Mock数据
- Ch9 边界条件

### Wave 2: 1 Agent（串行）

```
delegate_task(
  goal: "PRD Part4",
  context: "剩余模块 + 预提取数据 + 规则摘要"
)
```

### 合并阶段（主Agent执行）

```bash
# 不要用子Agent合并——会压缩细节
cat prd_part1_xxx.md >> 完整PRD.md
cat prd_part2_xxx.md >> 完整PRD.md
cat prd_part3_xxx.md >> 完整PRD.md
cat prd_part4_xxx.md >> 完整PRD.md
```

然后追加公共章节：
- Ch1 设计规范
- Ch2 信息架构（完整菜单树）
- Ch3 业务流程（引用Mermaid流程图）
- Ch4 系统架构（角色权限、接口规范）
- Ch10 验收标准（G1-G8门禁 + 各场景验收清单 + 系统质量门禁）
- 附录：功能点编号索引

## Context模板

发给每个Agent的context必须包含：

```
你是产品经理。编写XX项目PRD Part N。

## 功能点数据（直接使用，无需读Excel）
[预提取的模块层次+功能点类型比例]

## 场景业务流程
[文字版流程描述]

## 会员/业务规则摘要
[从docx提取的核心规则表]

## 输出章节
### Ch5 页面清单
### Ch6 功能点清单（每条标注操作类型）
### Ch7 数据模型
### Ch8 Mock数据
### Ch9 边界条件

## 输出文件
完整路径

## 约束
1. 每个功能点标注来源编号
2. 规则必须引用docx中的数值
3. 枚举值全部列全
```

## 已知陷阱

1. **Agent读Excel超时**：让Agent读1,900+行Excel→必然超时(600s+)。必须在主Agent侧预提取数据嵌入context。
2. **Context过长导致理解偏差**：预提取数据控制在2-3KB以内，用紧凑格式（模块→子模块→点数+类型比例），不要嵌入逐条功能点。
3. **终端命令被block**：WSL下某些Python操作（写/tmp目录）可能被安全规则拦截。优先用write_file工具。
4. **子Agent合并会丢失细节**：cat机械合并保真度100%，子Agent合并会压缩为摘要。
5. **公共章节重复**：各Part的Ch1文档概述会有重叠，主Agent在合并后写统一Ch1-4覆盖。

## 验证清单

- [ ] `wc -l 完整PRD.md` ≈ 各Part行数之和 + 公共章节
- [ ] 功能点总数覆盖验证（∑各Part = 总点数）
- [ ] Ch10验收标准包含G1-G8门禁
- [ ] 每个一级模块有页面清单
- [ ] 每个功能点有操作类型标注
