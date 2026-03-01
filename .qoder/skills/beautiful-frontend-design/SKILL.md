---
name: beautiful-frontend-design
description: 设计优美的 React 前端界面，使用 Ant Design 组件库。当用户需要美化界面、改进 UI/UX、创建新组件或优化布局时使用。
---

# 优美前端界面设计

## 设计原则

### 1. 视觉层次
- **大小对比**：重要元素更大，次要元素更小
- **颜色对比**：主色调用于主要操作，中性色用于背景
- **间距层次**：相关元素靠近，不同组之间留白更多

### 2. 一致性
- 使用设计系统（本项目使用 Ant Design）
- 统一圆角、阴影、边框样式
- 保持按钮、输入框等组件风格一致

### 3. 留白与呼吸感
- 卡片内边距：16-24px
- 元素间距：8px 的倍数（8, 16, 24, 32）
- 页面最大宽度：1200px，居中显示

## 本项目设计规范

### 色彩系统
```css
/* 主色调 */
--primary-color: #1890ff;        /* Ant Design 蓝色 */
--primary-gradient: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);

/* 背景色 */
--bg-body: #f5f5f5;              /* 页面背景 */
--bg-card: #ffffff;              /* 卡片背景 */

/* 文字色 */
--text-primary: #333333;         /* 主要文字 */
--text-secondary: #666666;       /* 次要文字 */
--text-muted: #999999;           /* 辅助文字 */
```

### 布局规范
```css
/* 页面 */
max-width: 1200px;
margin: 0 auto;
padding: 24px;

/* 卡片 */
border-radius: 8px;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

/* 悬停效果 */
transition: box-shadow 0.2s;
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
```

### 响应式断点
```css
/* 移动端 */
@media (max-width: 768px) {
  /* 单列布局 */
  /* 全宽按钮 */
}
```

## 常用美化模式

### 渐变头部
```jsx
<Header style={{
  background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
}}>
```

### 卡片悬停效果
```css
.card {
  transition: all 0.3s ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
```

### 文字截断
```css
.text-ellipsis {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

## 组件设计检查清单

创建或修改组件时检查：

- [ ] 使用 Ant Design 组件而非原生 HTML
- [ ] 添加适当的间距（padding/margin）
- [ ] 实现悬停/聚焦状态
- [ ] 处理空状态和加载状态
- [ ] 确保移动端可用
- [ ] 使用项目配色方案

## 常见改进场景

### 场景 1：列表项美化
**优化前**：纯文本列表
**优化后**：
- 使用 Card 组件包裹
- 添加图标和标签
- 增加操作按钮区域
- 悬停显示阴影

### 场景 2：表单美化
**优化前**：简单输入框堆叠
**优化后**：
- 使用 Form 组件统一管理
- 添加输入前缀/后缀图标
- 分组相关字段
- 添加表单验证提示

### 场景 3：数据展示
**优化前**：纯文字展示
**优化后**：
- 使用 Statistic 组件展示数字
- 添加趋势图标（上升/下降）
- 使用 Progress 展示进度
- 使用 Tag 区分状态

## Ant Design 推荐组件

| 场景 | 推荐组件 |
|------|----------|
| 页面布局 | Layout, Grid |
| 导航 | Menu, Breadcrumb, Tabs |
| 数据展示 | Card, List, Table, Collapse |
| 表单 | Form, Input, Select, DatePicker |
| 反馈 | Modal, Message, Progress, Spin |
| 按钮 | Button, Dropdown |

## 代码示例

### 美化搜索栏
```jsx
import { Input, Button, Space } from 'antd'
import { SearchOutlined } from '@ant-design/icons'

<Space.Compact style={{ width: '100%' }}>
  <Input 
    size="large"
    placeholder="搜索..."
    prefix={<SearchOutlined />}
  />
  <Button type="primary" size="large">
    搜索
  </Button>
</Space.Compact>
```

### 美化结果卡片
```jsx
import { Card, Tag, Button, Space } from 'antd'
import { FileTextOutlined, DownloadOutlined } from '@ant-design/icons'

<Card
  className="result-card"
  title={
    <Space>
      <FileTextOutlined />
      <span>{title}</span>
    </Space>
  }
  extra={<Tag color="blue">{category}</Tag>}
>
  <p className="result-snippet">{snippet}</p>
  <Space>
    <Button type="primary" icon={<DownloadOutlined />}>
      下载
    </Button>
  </Space>
</Card>
```
