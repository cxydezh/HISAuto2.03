# 图标使用说明

## 图标文件说明

### iconfont.svg
包含所有系统使用的SVG图标，采用symbol方式定义，便于复用和样式控制。

### logo.svg
系统主logo，包含医疗十字和AI元素，体现HIS系统的医疗和智能化特点。

## 使用方法

### 1. 在HTML中使用图标

```html
<!-- 使用SVG symbol -->
<svg class="icon">
  <use xlink:href="/static/icons/iconfont.svg#icon-user"></use>
</svg>

<!-- 使用logo -->
<img src="/static/icons/logo.svg" alt="HIS Logo" width="32" height="32">
```

### 2. 在CSS中引用

```css
.icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.logo {
  width: 32px;
  height: 32px;
}
```

## 可用图标列表

### 基础图标
- `icon-user` - 用户图标
- `icon-settings` - 设置图标
- `icon-logout` - 退出图标
- `icon-refresh` - 刷新图标

### 医疗相关图标
- `icon-patient` - 患者图标
- `icon-department` - 科室图标
- `icon-diagnosis` - 诊断图标
- `icon-treatment` - 治疗图标
- `icon-medicine` - 用药图标
- `icon-prognosis` - 预后图标
- `icon-nursing` - 护理图标

### AI功能图标
- `icon-ai` - AI图标
- `icon-run` - 运行图标
- `icon-stop` - 停止图标
- `icon-progress` - 进度图标

## 图标特点

1. **矢量图形**：SVG格式，可无损缩放
2. **颜色可控**：通过CSS的`fill`属性控制颜色
3. **大小可调**：通过CSS的`width`和`height`属性调整大小
4. **性能优化**：symbol方式复用，减少文件大小
5. **兼容性好**：现代浏览器都支持SVG

## 扩展说明

如需添加新图标，请在`iconfont.svg`文件中添加新的`<symbol>`元素，并在此文档中更新图标列表。 