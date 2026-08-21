# PRD枚举字段选项值 → 原型ENTITY_COLUMNS映射规范

## 问题背景

PRD Ch7数据模型为每个enum字段定义了选项值范围（如 `status: potential/normal/active/dormant/cancelled`），但生成原型时这些值经常丢失，导致表单弹窗的枚举字段渲染为空白输入框而非下拉菜单。

## 正确链路

```
PRD Ch7 选项/范围列 (中文值)
  ↓ 提取到 ENTITY_COLUMNS 的 options 数组
ENTITY_COLUMNS: {key, label, options: ['值1','值2','值3'], format}
  ↓ getEntityFields 识别 options → 设 type='select'
getEntityFields: {key, label, type: 'select', options: ['值1','值2','值3'], required}
  ↓ openFormModal 渲染为 <select>
<select data-field="status"><option>值1</option><option>值2</option>...</select>
```

## 规范

### 1. PRD写要求

PRD Ch7的选项/范围列必须用中文值（用户可见），且这些值直接映射到原型的下拉选项：

```
| status | enum | Y | 启用/停用/冻结/待激活 | Tag |
| level | enum | Y | 普通/银卡/金卡/钻石 | Select |
| type | enum | Y | 满减/折扣/现金 | Select |
```

### 2. ENTITY_COLUMNS定义

每个枚举字段必须有 options 数组：

```javascript
customers: [
  {key:'id', label:'客户ID'},
  {key:'name', label:'客户名称'},
  {key:'customerLevel', label:'客户等级', options:['准客户','正式客户','活跃','休眠','注销']},
  {key:'source', label:'来源', options:['ETC','APP','小程序','线下','96528热线']},
  {key:'status', label:'状态', format:statusTag, options:['启用','停用','冻结','待激活']},
],
```

### 3. getEntityFields函数

必须识别 options 数组并设 type='select'：

```javascript
function getEntityFields(entity) {
  var cols = ENTITY_COLUMNS[entity] || [];
  return cols.map(function(c) {
    var f = { key: c.key, label: c.label, type: 'text', required: false };
    if (c.options && c.options.length > 0) {
      f.type = 'select';
      f.options = c.options;
    }
    else if (isNumeric(c.key)) { f.type = 'number'; }
    else if (isLongText(c.key)) { f.type = 'textarea'; }
    f.required = (c.key === 'name');
    return f;
  });
}
```

### 4. openFormModal渲染

必须有 select 渲染分支：

```javascript
if (f.type === 'select' && f.options) {
  html += '<select data-field="'+f.key+'">';
  for (var j = 0; j < f.options.length; j++) {
    var opt = f.options[j];
    html += '<option value="'+opt+'"'+(val===opt?' selected':'')+'>'+opt+'</option>';
  }
  html += '</select>';
}
```

## 常见枚举字段选项值参考

| 字段key | 常见选项值（中文） |
|---------|------------------|
| status(客户) | 启用/停用/冻结/待激活 |
| status(订单) | 待结算/已结算/已对账 |
| status(任务) | 运行中/成功/失败/暂停 |
| customerLevel | 准客户/正式客户/活跃/休眠/注销 |
| memberLevel | 普通/银卡/金卡/钻石 |
| role | 超级管理员/运营/客服/数据分析师/系统管理员 |
| type(优惠券) | 满减/折扣/现金 |
| type(积分变动) | 累积/兑换/调整/出账/互通 |
| type(规则) | 准入/编码/唯一性/存储/重复识别/校验/覆盖 |
| type(活动) | 营销/推广/会员/节日 |
| type(策略) | 满减/满赠/限时折扣/会员专享 |
| type(商户) | 企业/个人/事业单位 |
| type(任务) | 数据同步/数据清洗/报表生成/积分结算/标签计算 |
| category(商品) | 机油/轮胎/电瓶/滤清器/刹车片/雨刮/火花塞 |
| priority | 高/中/低 |
| source | ETC/APP/小程序/线下/96528热线 |
| confidence | 高/中/低 |
| apiType | RESTful/gRPC/MQ |
| level(日志) | INFO/WARN/ERROR |
| notifyWay | 系统消息/邮件/短信/企业微信/不通知 |

## 验证检查清单

- [ ] PRD Ch7所有enum字段的选项值是否已用中文列出
- [ ] ENTITY_COLUMNS中每个枚举字段是否有 options 数组
- [ ] getEntityFields 是否识别 options 并设 type='select'
- [ ] openFormModal 是否有 select 渲染分支
- [ ] 点击"+新建"按钮后，弹窗中枚举字段是否显示为下拉菜单
