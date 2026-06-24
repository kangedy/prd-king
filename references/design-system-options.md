# 国产专业设计体系 · 完整Token参考

> 当PRD需要指定设计体系时，从下方选择对应体系，复制CSS变量块到PRD Ch1即可。
> 快速决策：React→Ant Design / Vue3→Element Plus / 全端→TDesign / 现代B端→Arco / 数据密集→Semi / 移动电商→NutUI

---

## 1. Ant Design 5.x（阿里 · 默认）

```
适用场景: B端管理后台、SaaS、企业级系统、金融、政务
主色: #1677FF
框架: React
组件数: 72个（6大类）
栅格: 8px + 24列
无障碍: WCAG AA
特点: 最成熟、生态最大、Token体系最完整
原型生成: ✅ 完美支持（默认）
```

```css
:root {
  --brand-primary: #1677FF;
  --brand-bg: #F5F7FA;
  --sidebar-bg: #001529;
  --text-primary: #1D1D1F;
  --border-color: #E5E6EB;
  --radius: 6px;
  --font-body: 14px;
  --color-success: #52C41A;
  --color-warning: #FAAD14;
  --color-danger: #FF4D4F;
}
```

---

## 2. Element Plus（饿了么 · Vue3体系首选）

```
适用场景: Vue3技术栈、B端管理后台、中后台系统
主色: #409EFF
框架: Vue 3
组件数: 55+
栅格: 24列
特点: Vue3生态最流行、最接近Ant Design的完备度
注意: 组件命名不同（Table→el-table, Form→el-form）
原型生成: ✅ 支持（命名映射需调整）
```

```css
:root {
  --brand-primary: #409EFF;
  --brand-bg: #F5F7FA;
  --sidebar-bg: #304156;
  --text-primary: #303133;
  --border-color: #DCDFE6;
  --radius: 4px;
  --font-body: 14px;
  --color-success: #67C23A;
  --color-warning: #E6A23C;
  --color-danger: #F56C6C;
}
```

---

## 3. TDesign（腾讯 · 全端统一）

```
适用场景: 全端项目（Web/移动端/小程序需要统一设计语言）、腾讯生态项目
主色: #0052D9
框架: React / Vue 2 / Vue 3 / 小程序（全覆盖）
组件数: 各端60+
栅格: 8px
特点: 跨端一致性最强、移动端适配好
注意: 移动端组件丰富度优于Ant Design
原型生成: ✅ 支持（Token可映射）
```

```css
:root {
  --brand-primary: #0052D9;
  --brand-bg: #FFFFFF;
  --sidebar-bg: #1E293B;
  --text-primary: #1A1A2E;
  --border-color: #DCDCDC;
  --radius: 6px;
  --font-body: 14px;
  --color-success: #00A870;
  --color-warning: #ED7B2F;
  --color-danger: #D54941;
}
```

---

## 4. Arco Design（字节跳动 · 现代B端）

```
适用场景: B端中后台、追求现代感/年轻化的企业系统
主色: #165DFF
框架: React / Vue 3
组件数: 60+
栅格: 12列
特点: 比Ant Design更现代的设计语言、暗色模式原生支持
注意: 社区生态次于Ant Design和Element Plus
原型生成: ✅ 支持
```

```css
:root {
  --brand-primary: #165DFF;
  --brand-bg: #F2F3F5;
  --sidebar-bg: #232324;
  --text-primary: #1D2129;
  --border-color: #E5E6EB;
  --radius: 8px;
  --font-body: 14px;
  --color-success: #00B42A;
  --color-warning: #FF7D00;
  --color-danger: #F53F3F;
}
```

---

## 5. Semi Design（抖音/字节跳动 · 创新设计体系）

```
适用场景: 中后台系统、重视交互细节和数据密集型应用
主色: #0077FA
框架: React
组件数: 50+
栅格: 8px
特点: Foundation/Adapter架构、2D/3D混合图标、表单密集型优化极好
      无障碍WCAG AA+
注意: 仅有React版本，无Vue
原型生成: ✅ 支持
```

```css
:root {
  --brand-primary: #0077FA;
  --brand-bg: #F5F5F5;
  --sidebar-bg: #1C1C1E;
  --text-primary: #1C1C1E;
  --border-color: #D9D9D9;
  --radius: 6px;
  --font-body: 14px;
  --color-success: #3BCE4A;
  --color-warning: #FA8C16;
  --color-danger: #FA2C19;
}
```

---

## 6. NutUI（京东 · 移动端零售C端）

```
适用场景: 移动端H5、电商类C端应用、零售业务
主色: #FA2C19（京东红）
框架: Vue 3
组件数: 70+
栅格: 375px基准
特点: 移动端体验优先、电商组件丰富（SKU选择器/倒计时/价格组件）
      原生B端能力弱，不适合纯管理后台
注意: 仅在Vue3下可用，无React版本
原型生成: ⚠️ 部分支持（移动端组件可映射）
```

```css
:root {
  --brand-primary: #FA2C19;
  --brand-bg: #F7F7F7;
  --text-primary: #1A1A1A;
  --border-color: #EEE;
  --radius: 12px;
  --font-body: 14px;
  --mobile-base: 375px;
  --color-success: #00B42A;
  --color-warning: #FF7D00;
  --color-danger: #FA2C19;
}
```

---

## 7. 微信 WeUI（小程序标准）

```
适用场景: 小程序、移动端H5
主色: #07C160
基准宽度: 375px
触控热区: 7-9mm
特点: 四级反馈体系（原位→图标→文字→弹窗）
      三级表单报错策略
原型生成: ✅ 支持（移动端适配）
```

```css
:root {
  --brand-primary: #07C160;
  --brand-bg: #F5F5F5;
  --text-primary: #1A1A1A;
  --border-color: #E5E5E5;
  --radius: 4px;
  --font-body: 16px;
  --mobile-base: 375px;
  --touch-target: 48px;
}
```

---

## 8. Apple HIG（iOS原生）

```
适用场景: iOS原生App
主色: #0066CC
触摸目标: 44×44pt
字体: SF Pro（Dynamic Type 200%缩放）
特点: Liquid Glass材质、Safe Area、SF Symbols 7000+
      无障碍为设计基线标准
原型生成: ⚠️ 仅移动端原型，Web原型用Ant Design替代
```

```css
:root {
  --brand-primary: #0066CC;
  --brand-bg: #F5F5F7;
  --text-primary: #1D1D1F;
  --border-color: #D2D2D7;
  --radius: 10px;
  --font-body: 17px;
  --touch-target: 44px;
}
```
