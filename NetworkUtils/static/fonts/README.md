# 字体使用说明

## 字体文件说明

### fonts.css
定义了系统中使用的字体，包括Microsoft Yahei和Source Han Sans的字重和样式。

## 字体列表

### Microsoft Yahei (微软雅黑)
- **正常字重**: msyh.ttf / msyh.woff2 / msyh.woff
- **粗体字重**: msyhbd.ttf / msyhbd.woff2 / msyhbd.woff
- **用途**: 主要界面字体，适合中文显示

### Source Han Sans (思源黑体)
- **轻量字重**: SourceHanSans-Light.ttf / SourceHanSans-Light.woff2 / SourceHanSans-Light.woff
- **正常字重**: SourceHanSans-Regular.ttf / SourceHanSans-Regular.woff2 / SourceHanSans-Regular.woff
- **粗体字重**: SourceHanSans-Bold.ttf / SourceHanSans-Bold.woff2 / SourceHanSans-Bold.woff
- **用途**: 标题和重要文字，现代感强

## 使用方法

### 1. 在HTML中引入字体CSS

```html
<link rel="stylesheet" href="/static/fonts/fonts.css">
```

### 2. 在CSS中使用字体

```css
/* 使用Microsoft Yahei */
body {
  font-family: 'Microsoft Yahei', 'Source Han Sans', sans-serif;
}

/* 使用Source Han Sans */
h1, h2, h3 {
  font-family: 'Source Han Sans', 'Microsoft Yahei', sans-serif;
  font-weight: bold;
}

/* 使用轻量字重 */
.light-text {
  font-family: 'Source Han Sans', sans-serif;
  font-weight: 300;
}
```

## 字体特点

### Microsoft Yahei
- **优点**: 清晰度高，适合屏幕显示
- **适用场景**: 正文内容、用户界面文字
- **兼容性**: Windows系统自带，兼容性好

### Source Han Sans
- **优点**: 现代感强，字重丰富
- **适用场景**: 标题、重要信息、品牌文字
- **特点**: 支持多种字重，设计感强

## 字体回退方案

系统采用以下字体回退顺序：
1. Microsoft Yahei (微软雅黑)
2. Source Han Sans (思源黑体)
3. PingFang SC (苹方)
4. Hiragino Sans GB (冬青黑体)
5. Helvetica Neue
6. Arial
7. sans-serif

## 性能优化

### 字体加载优化
- 使用`font-display: swap`确保字体加载时显示回退字体
- 提供多种格式（TTF、WOFF2、WOFF）提高兼容性
- 优先使用WOFF2格式，体积最小

### 字体文件管理
- 只加载必要的字重
- 考虑使用字体子集化减少文件大小
- 使用CDN或本地缓存提高加载速度

## 扩展说明

如需添加新字体，请在`fonts.css`文件中添加新的`@font-face`定义，并更新字体回退方案。 