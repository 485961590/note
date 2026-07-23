# HTML 标签与属性速查

> 涵盖所有常用 HTML 元素的标签、属性、事件 —— 按类别索引，适合开发与审计时快速定位。

---

## 目录

1. [全局属性（所有元素可用）](#1-全局属性所有元素可用)
2. [事件处理器（通用）](#2-事件处理器通用)
3. [文档结构标签](#3-文档结构标签)
4. [文本与内联标签](#4-文本与内联标签)
5. [列表标签](#5-列表标签)
6. [表格标签](#6-表格标签)
7. [表单标签](#7-表单标签)
8. [媒体标签](#8-媒体标签)
9. [嵌入与交互标签](#9-嵌入与交互标签)
10. [语义化与分区标签](#10-语义化与分区标签)
11. [废弃标签（避免使用）](#11-废弃标签避免使用)

---

## 1. 全局属性（所有元素可用）

这些属性可以写在**任意 HTML 元素**上。

| 属性 | 值类型 | 说明 | 示例 |
|------|--------|------|------|
| `id` | string | 元素唯一标识符，同一页面中不可重复 | `id="header"` |
| `class` | string | CSS 类名，空格分隔多个 | `class="btn primary"` |
| `style` | CSS | 内联样式 | `style="color: red; font-size: 14px"` |
| `title` | string | 鼠标悬浮时的提示文字 | `title="点击提交"` |
| `lang` | BCP 47 | 元素内容的语言 | `lang="zh-CN"` |
| `dir` | `ltr` / `rtl` / `auto` | 文字方向 | `dir="rtl"` |
| `tabindex` | integer | Tab 键切换顺序，`-1` 表示不在序列中 | `tabindex="0"` |
| `accesskey` | char | 快捷键（不推荐，易冲突） | `accesskey="s"` |
| `hidden` | boolean | 隐藏元素（CSS `display: none` 级别） | `hidden` |
| `contenteditable` | `true` / `false` / `plaintext-only` | 元素是否可编辑 | `contenteditable="true"` |
| `draggable` | `true` / `false` / `auto` | 元素是否可拖拽 | `draggable="true"` |
| `spellcheck` | `true` / `false` | 是否检查拼写 | `spellcheck="true"` |
| `translate` | `yes` / `no` | 翻译时是否处理此元素 | `translate="no"` |
| `role` | ARIA role | 无障碍语义角色 | `role="navigation"` |
| `aria-*` | varies | ARIA 无障碍属性族 | `aria-label="关闭"` |
| `data-*` | string | 自定义数据属性 | `data-user-id="42"` |
| `slot` | string | Web Components 插槽名 | `slot="header"` |
| `part` | string | Shadow DOM 部件名 | `part="button"` |
| `nonce` | string | CSP nonce，仅用于 `<script>` `<style>` | `nonce="abc123"` |

---

## 2. 事件处理器（通用）

以下事件属性可绑定到大多数可见元素。`onload` 类事件只能用于特定元素（`window`、`body`、`img` 等）。

### 2.1 窗口 / 文档事件（`<body>` 或 `window`）

| 属性 | 触发时机 |
|------|---------|
| `onload` | 页面（或 iframe/img）完全加载完毕 |
| `onunload` | 页面卸载（关闭/跳转） |
| `onbeforeunload` | 页面即将卸载（可弹确认框） |
| `onerror` | 资源加载失败（需绑在 window 上才能捕获全局 JS 错误） |
| `onresize` | 窗口大小改变 |
| `onscroll` | 页面或元素滚动 |
| `onhashchange` | URL hash 部分改变（`#xxx`） |
| `onpopstate` | 浏览器历史记录变化（前进/后退） |
| `onpageshow` / `onpagehide` | 页面显示/隐藏（含 bfcache） |
| `ononline` / `onoffline` | 网络状态变化 |
| `onmessage` | 收到 postMessage 消息 |
| `onstorage` | localStorage / sessionStorage 被修改（其他标签页触发） |

### 2.2 鼠标事件

| 属性 | 触发时机 |
|------|---------|
| `onclick` | 鼠标单击（左键） |
| `ondblclick` | 鼠标双击 |
| `onmousedown` | 鼠标按下（任意键） |
| `onmouseup` | 鼠标松开 |
| `onmouseenter` | 鼠标进入元素（不冒泡） |
| `onmouseleave` | 鼠标离开元素（不冒泡） |
| `onmouseover` | 鼠标进入元素（冒泡） |
| `onmouseout` | 鼠标离开元素（冒泡） |
| `onmousemove` | 鼠标在元素内移动 |
| `oncontextmenu` | 右键打开上下文菜单 |
| `onwheel` | 鼠标滚轮滚动 |

### 2.3 键盘事件

| 属性 | 触发时机 |
|------|---------|
| `onkeydown` | 按下任意键（按住持续触发） |
| `onkeyup` | 松开按键 |
| `onkeypress` | 按下字符键（已废弃，用 `onkeydown` 替代） |

### 2.4 表单事件

| 属性 | 触发时机 |
|------|---------|
| `onfocus` | 元素获得焦点（不冒泡） |
| `onblur` | 元素失去焦点（不冒泡） |
| `onfocusin` | 元素获得焦点（冒泡） |
| `onfocusout` | 元素失去焦点（冒泡） |
| `onchange` | 表单元素值改变并失去焦点时 |
| `oninput` | 表单元素值改变时（实时触发） |
| `onselect` | 选中文本框中的文字时 |
| `onsubmit` | 表单提交时 |
| `onreset` | 表单重置时 |
| `oninvalid` | 表单元素验证失败时 |

### 2.5 触摸与指针事件

| 属性 | 触发时机 |
|------|---------|
| `ontouchstart` | 手指触摸屏幕 |
| `ontouchend` | 手指离开屏幕 |
| `ontouchmove` | 手指在屏幕上滑动 |
| `ontouchcancel` | 触摸被打断（如来电） |
| `onpointerdown` | 指针按下（统一鼠标/触摸/笔） |
| `onpointerup` | 指针松开 |
| `onpointermove` | 指针移动 |

### 2.6 拖拽事件

| 属性 | 触发时机 |
|------|---------|
| `ondrag` | 元素正在被拖动时（持续触发） |
| `ondragstart` | 开始拖动元素 |
| `ondragend` | 拖动结束 |
| `ondragenter` | 被拖元素进入目标区域 |
| `ondragleave` | 被拖元素离开目标区域 |
| `ondragover` | 被拖元素在目标区域上方（持续触发） |
| `ondrop` | 元素被放下 |

### 2.7 剪贴板事件

| 属性 | 触发时机 |
|------|---------|
| `oncopy` | 用户复制内容 |
| `oncut` | 用户剪切内容 |
| `onpaste` | 用户粘贴内容 |

### 2.8 媒体事件（`<audio>` / `<video>`）

| 属性 | 触发时机 |
|------|---------|
| `onplay` | 开始播放 |
| `onpause` | 暂停播放 |
| `onended` | 播放完毕 |
| `ontimeupdate` | 播放时间更新（持续触发） |
| `onloadeddata` | 首帧数据加载完毕 |
| `oncanplay` | 可以开始播放（有足够数据） |
| `onwaiting` | 等待下一帧数据（缓冲） |
| `onerror` | 加载或播放出错 |
| `onvolumechange` | 音量改变 |
| `onratechange` | 播放速率改变 |
| `onseeked` | 跳转播放位置完成 |

### 2.9 动画事件

| 属性 | 触发时机 |
|------|---------|
| `onanimationstart` | CSS 动画开始 |
| `onanimationend` | CSS 动画结束 |
| `onanimationiteration` | CSS 动画每次循环结束 |
| `ontransitionend` | CSS 过渡效果结束 |

---

## 3. 文档结构标签

### `<html>`

| 属性 | 说明 |
|------|------|
| `lang` | 文档语言，如 `lang="zh-CN"` |
| `dir` | 文字方向 |
| `manifest` | （已废弃）应用缓存清单 |

### `<head>`

无特有属性。包含 `<title>`、`<meta>`、`<link>`、`<style>`、`<script>` 等。

### `<title>`

无属性，纯文本内容。唯一必须存在的 `<head>` 子元素。

### `<meta>`

| 属性 | 说明 | 示例 |
|------|------|------|
| `charset` | 字符编码 | `<meta charset="UTF-8">` |
| `name` | 元数据名称 | `name="viewport"` |
| `content` | 元数据值 | `content="width=device-width"` |
| `http-equiv` | HTTP 响应头等效 | `http-equiv="refresh"` |
| `property` | Open Graph 属性名 | `property="og:title"` |

常用组合：

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="页面描述">
<meta name="keywords" content="关键词1,关键词2">
<meta name="author" content="作者名">
<meta name="robots" content="index, follow">
<meta http-equiv="refresh" content="5; url=https://example.com">
<meta property="og:title" content="Open Graph 标题">
<meta property="og:image" content="https://example.com/thumb.jpg">
```

### `<link>`

| 属性 | 说明 | 常见值 |
|------|------|--------|
| `rel` | 链接关系 | `stylesheet` / `icon` / `preload` / `canonical` / `alternate` |
| `href` | 链接 URL | — |
| `type` | MIME 类型 | `text/css` |
| `media` | 媒体查询 | `screen and (max-width: 600px)` |
| `sizes` | 图标尺寸 | `32x32` |
| `crossorigin` | CORS 模式 | `anonymous` / `use-credentials` |
| `as` | 预加载资源类型 | `script` / `style` / `image` / `font` |
| `rel="preload"` 时必填 | | |
| `integrity` | SRI 哈希 | `sha256-xxxxx` |

```html
<link rel="stylesheet" href="style.css">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>
<link rel="canonical" href="https://example.com/page">
```

### `<base>`

| 属性 | 说明 |
|------|------|
| `href` | 页面中所有相对 URL 的基础路径 |
| `target` | 所有链接的默认打开方式 |

```html
<base href="https://example.com/" target="_blank">
```

### `<script>`

| 属性 | 说明 |
|------|------|
| `src` | 外部脚本 URL |
| `type` | MIME 类型，`module` 表示 ES module |
| `async` | 异步下载，下载完立即执行（不保证顺序） |
| `defer` | 异步下载，DOM 解析完后按顺序执行 |
| `nomodule` | 不支持 ES module 的浏览器才执行 |
| `crossorigin` | CORS 模式 |
| `integrity` | SRI 哈希 |
| `nonce` | CSP nonce |
| `referrerpolicy` | Referrer 策略 |

```html
<script src="app.js" defer></script>
<script type="module" src="main.mjs"></script>
<script nomodule src="fallback.js"></script>
```

### `<noscript>`

无属性。浏览器禁用脚本时显示的内容。

### `<body>`

| 属性 | 说明 |
|------|------|
| `onload` | 页面加载完成 |
| `onunload` | 页面卸载 |
| `onbeforeunload` | 即将卸载 |
| `onscroll` | 页面滚动 |
| `onresize` | （通常绑在 window） |

---

## 4. 文本与内联标签

### `<a>` — 超链接

| 属性 | 说明 | 示例 |
|------|------|------|
| `href` | 链接目标 URL | `href="https://example.com"` |
| `target` | 打开方式 | `_self` / `_blank` / `_parent` / `_top` |
| `rel` | 链接关系 | `noopener` / `noreferrer` / `nofollow` / `noindex` |
| `download` | 下载文件（指定文件名） | `download` / `download="report.pdf"` |
| `hreflang` | 目标页面语言 | `hreflang="en"` |
| `type` | 目标 MIME 类型 | `type="application/pdf"` |
| `ping` | 点击时 POST 通知的 URL 列表（空格分隔） | `ping="/track"` |
| `referrerpolicy` | Referrer 策略 | `no-referrer` / `strict-origin` |

**安全提示**：`target="_blank"` 必须配 `rel="noopener noreferrer"` 防 `window.opener` 钓鱼（tabnabbing）。

### `<br>` — 换行  /  `<wbr>` — 可断词处

无属性。

### `<span>` — 通用内联容器

仅有全局属性。

### `<strong>` / `<b>` — 加粗

`<strong>` 有语义（重要内容），`<b>` 纯样式。仅全局属性。

### `<em>` / `<i>` — 斜体

`<em>` 有语义（强调），`<i>` 纯样式。仅全局属性。

### `<u>` — 下划线  /  `<s>` — 删除线  /  `<mark>` — 高亮

仅全局属性。

### `<small>` — 小号文字  /  `<sub>` — 下标  /  `<sup>` — 上标

仅全局属性。

### `<code>` / `<pre>` / `<kbd>` / `<samp>` / `<var>`

代码语义标签，仅全局属性。`<pre>` 保留空格和换行。

### `<blockquote>` — 块引用

| 属性 | 说明 |
|------|------|
| `cite` | 引用来源 URL |

### `<q>` — 行内引用

| 属性 | 说明 |
|------|------|
| `cite` | 引用来源 URL |

### `<cite>` — 作品标题（书名、论文名等）

仅全局属性。

### `<abbr>` — 缩写

| 属性 | 说明 | 示例 |
|------|------|------|
| `title` | 完整形式 | `<abbr title="HyperText Markup Language">HTML</abbr>` |

### `<dfn>` — 术语定义

| 属性 | 说明 |
|------|------|
| `title` | 鼠标悬浮时显示术语定义 |

### `<time>` — 时间 / 日期

| 属性 | 说明 | 示例 |
|------|------|------|
| `datetime` | 机器可读的时间格式（ISO 8601） | `datetime="2025-07-23"` / `datetime="14:30:00"` |

```html
<time datetime="2025-07-23T14:30:00+08:00">2025年7月23日 下午2:30</time>
<time datetime="PT2H30M">2小时30分钟</time>
```

### `<address>` — 联系信息

仅全局属性。通常包含 email、电话、地址。

### `<ruby>` / `<rt>` / `<rp>` — 注音

仅全局属性。日语振假名或中文拼音注音。

### `<bdo>` / `<bdi>` — 文字方向控制

| 属性 | 说明 |
|------|------|
| `dir` | `ltr` / `rtl` |

### `<ins>` / `<del>` — 插入 / 删除的文本

| 属性 | 说明 |
|------|------|
| `cite` | 修改原因的 URL |
| `datetime` | 修改时间（ISO 8601） |

---

## 5. 列表标签

### `<ul>` — 无序列表  /  `<ol>` — 有序列表

`<ul>` 仅全局属性。

`<ol>` 特有属性：

| 属性 | 说明 | 示例 |
|------|------|------|
| `start` | 起始编号 | `start="10"` |
| `reversed` | 倒序编号 | `reversed` |
| `type` | 编号类型 | `1` / `A` / `a` / `I` / `i` |

### `<li>` — 列表项

| 属性 | 说明 |
|------|------|
| `value` | 仅 `<ol>` 内的 `<li>`，覆盖当前编号 |

### `<dl>` — 描述列表  /  `<dt>` — 术语  /  `<dd>` — 描述

仅全局属性。

---

## 6. 表格标签

### `<table>`

| 属性 | 说明 |
|------|------|
| `border` | （已废弃，用 CSS）表格边框 |
| `cellpadding` | （已废弃）单元格内边距 |
| `cellspacing` | （已废弃）单元格间距 |
| `summary` | （已废弃）表格摘要 |

### `<caption>` — 表格标题

仅全局属性。必须是 `<table>` 的第一个子元素。

### `<colgroup>` / `<col>` — 列组 / 列

| 属性 | 说明 |
|------|------|
| `span` | 跨越的列数，默认 1 |

```html
<colgroup>
  <col span="2" style="background-color: red">
  <col style="background-color: yellow">
</colgroup>
```

### `<thead>` / `<tbody>` / `<tfoot>` — 表头 / 表体 / 表尾

仅全局属性。`<tfoot>` 必须在 `<tbody>` 之前（HTML 解析器要求）。

### `<tr>` — 表行

仅全局属性。

### `<th>` — 表头单元格

| 属性 | 说明 | 示例 |
|------|------|------|
| `scope` | 表头作用的范围 | `row` / `col` / `rowgroup` / `colgroup` |
| `colspan` | 横跨列数 | `colspan="2"` |
| `rowspan` | 纵跨行数 | `rowspan="3"` |
| `headers` | 关联的 `<th>` id 列表（空格分隔） | `headers="name-header age-header"` |
| `abbr` | 缩写（无障碍） | `abbr="Name"` |
| `sorted` | 排序状态 | `ascending` / `descending` |

### `<td>` — 表数据单元格

| 属性 | 说明 |
|------|------|
| `colspan` | 横跨列数 |
| `rowspan` | 纵跨行数 |
| `headers` | 关联的 `<th>` id 列表 |

---

## 7. 表单标签

### `<form>`

| 属性 | 说明 | 示例 |
|------|------|------|
| `action` | 提交 URL | `action="/submit"` |
| `method` | HTTP 方法 | `get` / `post` |
| `enctype` | 编码类型 | `application/x-www-form-urlencoded`（默认）/ `multipart/form-data`（文件上传）/ `text/plain` |
| `target` | 提交后的打开方式 | `_self` / `_blank` |
| `autocomplete` | 是否自动填充 | `on` / `off` |
| `novalidate` | 跳过 HTML5 表单验证 | `novalidate` |
| `name` | 表单名称 | |
| `accept-charset` | 接受的字符编码 | `UTF-8` |
| `rel` | 链接关系（同 `<a>`） | `noopener` |

### `<input>`

**`type` 属性的所有取值：**

| type 值 | 说明 | 特有属性 |
|----------|------|---------|
| `text` | 单行文本（默认） | `maxlength` / `minlength` / `pattern` / `placeholder` / `size` |
| `password` | 密码框 | 同上 |
| `email` | 邮箱地址 | `multiple` / `pattern` / `placeholder` |
| `url` | 网址 | `pattern` / `placeholder` |
| `tel` | 电话号码 | `pattern` / `placeholder` |
| `number` | 数字 | `min` / `max` / `step` / `value` |
| `range` | 滑块 | `min` / `max` / `step` |
| `date` | 日期 | `min` / `max` / `step` |
| `datetime-local` | 本地日期时间 | `min` / `max` |
| `month` | 月份 | `min` / `max` |
| `week` | 周 | `min` / `max` |
| `time` | 时间 | `min` / `max` / `step` |
| `color` | 颜色选择器 | — |
| `checkbox` | 多选框 | `checked` / `indeterminate` / `value` |
| `radio` | 单选框 | `checked` / `value` |
| `file` | 文件上传 | `accept` / `multiple` / `capture` / `files` (JS) |
| `hidden` | 隐藏字段 | — |
| `submit` | 提交按钮 | `formaction` / `formmethod` / `formenctype` / `formnovalidate` / `formtarget` |
| `reset` | 重置按钮 | — |
| `button` | 普通按钮 | — |
| `image` | 图片提交按钮 | `src` / `alt` / `width` / `height` / `formaction` 等 |
| `search` | 搜索框 | `maxlength` / `minlength` / `pattern` / `placeholder` |

**所有 `<input>` 的通用属性：**

| 属性 | 说明 | 示例 |
|------|------|------|
| `name` | 字段名（提交时的 key） | `name="username"` |
| `value` | 字段值 | `value="默认值"` |
| `placeholder` | 占位提示文字 | `placeholder="请输入..."` |
| `required` | 必填 | `required` |
| `disabled` | 禁用 | `disabled` |
| `readonly` | 只读 | `readonly` |
| `autofocus` | 页面加载时自动聚焦 | `autofocus` |
| `autocomplete` | 自动填充 | `on` / `off` / `new-password` / `one-time-code` |
| `size` | 可见字符宽度 | `size="30"` |
| `maxlength` | 最大字符数 | `maxlength="100"` |
| `minlength` | 最小字符数 | `minlength="6"` |
| `min` / `max` | 最小/最大值 | `min="1" max="100"` |
| `step` | 数值步进 | `step="0.5"` |
| `pattern` | 正则验证 | `pattern="[A-Za-z]{3,}"` |
| `list` | 关联的 `<datalist>` id | `list="suggestions"` |
| `multiple` | 多值（email/file） | `multiple` |
| `accept` | file 类型时限制文件类型 | `accept="image/*,.pdf"` |
| `capture` | file 类型时调用摄像头 | `capture="user"` / `capture="environment"` |
| `inputmode` | 虚拟键盘类型 | `text` / `numeric` / `tel` / `email` / `url` / `decimal` / `search` |
| `dirname` | 提交时附带文字方向 | `dirname="username.dir"` |

**表单覆盖属性**（仅 `type="submit"` / `type="image"`）：

| 属性 | 说明 |
|------|------|
| `formaction` | 覆盖 `<form action>` |
| `formmethod` | 覆盖 `<form method>` |
| `formenctype` | 覆盖 `<form enctype>` |
| `formnovalidate` | 覆盖 `<form novalidate>` |
| `formtarget` | 覆盖 `<form target>` |

### `<textarea>` — 多行文本

| 属性 | 说明 |
|------|------|
| `name` | 字段名 |
| `rows` | 可见行数 |
| `cols` | 可见列数（字符宽度） |
| `maxlength` | 最大字符数 |
| `minlength` | 最小字符数 |
| `placeholder` | 占位文字 |
| `required` / `disabled` / `readonly` / `autofocus` | 同 `<input>` |
| `wrap` | 换行方式 | `hard` / `soft` |
| `spellcheck` | 拼写检查 | `true` / `false` |
| `dirname` | 文字方向附带字段名 | |

### `<select>` — 下拉列表

| 属性 | 说明 |
|------|------|
| `name` | 字段名 |
| `multiple` | 多选 |
| `size` | 可见选项数（`multiple` 时默认 4，单选时默认 1） |
| `required` / `disabled` / `autofocus` | 同 `<input>` |

### `<optgroup>` — 选项分组

| 属性 | 说明 |
|------|------|
| `label` | 分组标题（必填） |
| `disabled` | 禁用整个分组 |

### `<option>` — 选项

| 属性 | 说明 |
|------|------|
| `value` | 提交的值（未指定则取文本内容） |
| `selected` | 默认选中 |
| `disabled` | 禁用选项 |
| `label` | 显示文本（缩写） |

### `<button>`

| 属性 | 说明 |
|------|------|
| `type` | `submit`（默认）/ `reset` / `button` |
| `name` / `value` | 提交时的字段名和值 |
| `disabled` / `autofocus` | 同 `<input>` |
| `formaction` / `formmethod` / `formenctype` / `formnovalidate` / `formtarget` | 表单覆盖属性（`type="submit"` 时） |
| `popovertarget` | 控制 popover 元素的 id |
| `popovertargetaction` | `toggle` / `show` / `hide` |

### `<label>` — 表单标签

| 属性 | 说明 |
|------|------|
| `for` | 关联的表单控件 id（点击 label 会聚焦控件） |

```html
<label for="email">邮箱：</label>
<input type="email" id="email">

<!-- 或隐式关联 -->
<label>邮箱：<input type="email"></label>
```

### `<fieldset>` — 字段分组

| 属性 | 说明 |
|------|------|
| `disabled` | 禁用内部所有表单控件 |
| `name` | 字段组名 |

### `<legend>` — 字段组标题

仅全局属性。必须是 `<fieldset>` 的第一个子元素。

### `<datalist>` — 输入建议列表

| 属性 | 说明 |
|------|------|
| `id` | 被 `<input list>` 引用 |

### `<output>` — 计算结果输出

| 属性 | 说明 | 示例 |
|------|------|------|
| `for` | 关联的输入框 id 列表 | `for="a b"` |
| `name` | 字段名 | |
| `form` | 关联的表单 id | |

### `<progress>` — 进度条

| 属性 | 说明 |
|------|------|
| `value` | 当前值 |
| `max` | 最大值（默认 1） |

### `<meter>` — 度量条（磁盘用量、评分等）

| 属性 | 说明 |
|------|------|
| `value` | 当前值 |
| `min` | 最小值（默认 0） |
| `max` | 最大值（默认 1） |
| `low` | "低"区间的上限 |
| `high` | "高"区间的下限 |
| `optimum` | 最优值 |
| `form` | 关联的表单 id |

```html
<meter value="0.6" low="0.3" high="0.8" optimum="1">60%</meter>
```

---

## 8. 媒体标签

### `<img>` — 图片

| 属性 | 说明 | 示例 |
|------|------|------|
| `src` | 图片 URL（必填） | `src="photo.jpg"` |
| `alt` | 替代文字（必填，无障碍要求） | `alt="一只猫"` |
| `width` | 宽度（像素，不含单位） | `width="800"` |
| `height` | 高度（像素，不含单位） | `height="600"` |
| `srcset` | 响应式图片源（1x/2x/3x） | `srcset="small.jpg 480w, large.jpg 1080w"` |
| `sizes` | 响应式尺寸条件 | `sizes="(max-width: 600px) 480px, 1080px"` |
| `loading` | 懒加载 | `eager`（默认）/ `lazy` |
| `decoding` | 解码方式 | `sync` / `async` / `auto` |
| `fetchpriority` | 加载优先级 | `high` / `low` / `auto` |
| `crossorigin` | CORS 模式 | `anonymous` / `use-credentials` |
| `ismap` | 服务端图片映射（需被 `<a>` 包裹） | `ismap` |
| `usemap` | 关联的 `<map>` 名称（`#` 开头） | `usemap="#image-map"` |
| `referrerpolicy` | Referrer 策略 | `no-referrer` |
| `onload` | 图片加载完毕 | |
| `onerror` | 图片加载失败 | |

```html
<img
  src="photo.jpg"
  srcset="photo@2x.jpg 2x, photo@3x.jpg 3x"
  sizes="(max-width: 600px) 480px, 1080px"
  alt="日落风景"
  loading="lazy"
  decoding="async"
>
```

**安全提示**：`onerror` 是 XSS 常用 payload `<img src=x onerror=alert(1)>`。审计时注意 `src` 和 `onerror`/`onload` 是否来自用户输入。

### `<map>` / `<area>` — 图片热区映射

**`<map>`** 属性：

| 属性 | 说明 |
|------|------|
| `name` | 映射名称（`<img usemap="#name">` 引用） |

**`<area>`** 属性：

| 属性 | 说明 | 示例 |
|------|------|------|
| `shape` | 形状 | `rect` / `circle` / `poly` / `default` |
| `coords` | 坐标 | `shape="rect" coords="0,0,100,100"` |
| `href` | 链接 URL | |
| `target` | 打开方式 | `_blank` |
| `alt` | 替代文字 | |
| `download` | 下载链接 | |
| `rel` | 链接关系 | |

### `<picture>` — 响应式图片容器

无特有属性。包含 `<source>` 和回退 `<img>`。

### `<source>` — 媒体源

| 属性 | 说明 | 示例 |
|------|------|------|
| `src` | 媒体 URL | |
| `srcset` | 多分辨率 URL 列表 | |
| `type` | MIME 类型 | `type="image/webp"` |
| `media` | 媒体查询条件 | `media="(min-width: 800px)"` |
| `sizes` | 尺寸条件 | |

```html
<picture>
  <source srcset="photo.webp" type="image/webp">
  <source srcset="photo.jpg" type="image/jpeg">
  <img src="photo.jpg" alt="日落">
</picture>
```

### `<figure>` / `<figcaption>` — 图文组合

仅全局属性。

```html
<figure>
  <img src="chart.png" alt="销量图表">
  <figcaption>图 1：2025 年 Q2 销量趋势</figcaption>
</figure>
```

### `<audio>` — 音频

| 属性 | 说明 |
|------|------|
| `src` | 音频 URL |
| `controls` | 显示播放控件 |
| `autoplay` | 自动播放（多数浏览器需 `muted` 配合） |
| `muted` | 静音 |
| `loop` | 循环播放 |
| `preload` | 预加载策略 | `none` / `metadata` / `auto` |
| `crossorigin` | CORS 模式 |

```html
<audio controls preload="metadata">
  <source src="music.mp3" type="audio/mpeg">
  <source src="music.ogg" type="audio/ogg">
  您的浏览器不支持 audio 标签
</audio>
```

### `<video>` — 视频

| 属性 | 说明 |
|------|------|
| `src` | 视频 URL |
| `controls` | 显示播放控件 |
| `autoplay` | 自动播放（需 `muted`） |
| `muted` | 静音 |
| `loop` | 循环播放 |
| `poster` | 封面图片 URL |
| `width` / `height` | 尺寸 |
| `preload` | 预加载策略 | `none` / `metadata` / `auto` |
| `playsinline` | 内联播放（iOS 需要） |
| `crossorigin` | CORS 模式 |
| `disablepictureinpicture` | 禁止画中画 |
| `disableremoteplayback` | 禁止投屏 |
| `pip` | （实验性）画中画模式 |

```html
<video controls width="720" poster="cover.jpg" playsinline>
  <source src="movie.mp4" type="video/mp4">
  <source src="movie.webm" type="video/webm">
  <track src="subtitles-zh.vtt" kind="subtitles" srclang="zh" label="中文">
</video>
```

### `<track>` — 字幕/章节轨道

| 属性 | 说明 |
|------|------|
| `src` | 轨道文件 URL (.vtt) |
| `kind` | 轨道类型 | `subtitles` / `captions` / `descriptions` / `chapters` / `metadata` |
| `srclang` | 轨道语言（BCP 47） | `zh-CN` / `en` |
| `label` | 显示名称 | |
| `default` | 默认启用 | `default` |

### `<canvas>` — 画布

| 属性 | 说明 |
|------|------|
| `width` | 画布宽度（像素，默认 300，CSS 宽度不等于画布宽度） |
| `height` | 画布高度（像素，默认 150） |

JavaScript API 操作绑图，标签本身不承载内容。回退文字写在标签之间：
```html
<canvas id="myCanvas" width="800" height="600">
  您的浏览器不支持 Canvas
</canvas>
```

---

## 9. 嵌入与交互标签

### `<iframe>` — 内联框架

| 属性 | 说明 | 示例 |
|------|------|------|
| `src` | 嵌入页面的 URL | |
| `name` | 框架名称（用于 `target` / `window.open`） | `name="myFrame"` |
| `width` / `height` | 尺寸 | |
| `sandbox` | 沙箱限制（空格分隔多个值） | `sandbox="allow-scripts allow-same-origin"` |
| `allow` | Permissions Policy | `allow="camera; microphone"` |
| `allowfullscreen` | 允许全屏（旧写法，现在用 `allow="fullscreen"`） | `allowfullscreen` |
| `loading` | 懒加载 | `eager` / `lazy` |
| `referrerpolicy` | Referrer 策略 | `no-referrer` / `strict-origin` |
| `srcdoc` | 内联 HTML（替代 src） | `srcdoc="<p>Hello</p>"` |
| `credentialless` | 无凭据模式（实验性） | `credentialless` |
| `csp` | 对框架内容施加 CSP（实验性） | `csp="script-src 'none'"` |

`sandbox` 值组合：

| 值 | 允许的操作 |
|----|-----------|
| （空字符串）| 全部限制 |
| `allow-scripts` | 执行 JS（不包含创建弹窗） |
| `allow-same-origin` | 同源访问（storage、cookie） |
| `allow-forms` | 表单提交 |
| `allow-popups` | 弹窗 |
| `allow-popups-to-escape-sandbox` | 弹窗不受沙箱限制 |
| `allow-top-navigation` | 修改顶层窗口位置 |
| `allow-top-navigation-by-user-activation` | 用户手势触发的顶层导航 |
| `allow-modals` | 模态对话框 |
| `allow-downloads` | 下载 |
| `allow-presentation` | 演示 API |
| `allow-pointer-lock` | 指针锁定 |
| `allow-orientation-lock` | 屏幕方向锁定 |

**安全提示**：不加 `sandbox` 的 iframe 几乎无隔离，嵌入不受控页面极危险。

### `<embed>` — 外部内容嵌入

| 属性 | 说明 |
|------|------|
| `src` | 嵌入内容 URL |
| `type` | MIME 类型 |
| `width` / `height` | 尺寸 |

### `<object>` — 通用嵌入对象

| 属性 | 说明 |
|------|------|
| `data` | 资源 URL |
| `type` | MIME 类型 |
| `name` | 对象名称 |
| `width` / `height` | 尺寸 |
| `form` | 关联的表单 id |
| `typemustmatch` | 严格匹配 `type` 与服务器 Content-Type |

### `<param>` — 对象参数（`<object>` 子元素）

| 属性 | 说明 |
|------|------|
| `name` | 参数名 |
| `value` | 参数值 |

### `<details>` / `<summary>` — 折叠面板

`<details>` 属性：

| 属性 | 说明 |
|------|------|
| `open` | 默认展开 |
| `name` | 手风琴组名（同 name 的 details 互斥展开） |

`<summary>` 仅全局属性。必须是 `<details>` 的第一个子元素。

```html
<details open>
  <summary>点击展开</summary>
  <p>隐藏的内容在这里</p>
</details>
```

### `<dialog>` — 对话框

| 属性 | 说明 |
|------|------|
| `open` | 显示对话框 |

JavaScript 控制：`dialog.show()` / `dialog.showModal()` / `dialog.close()`。

```html
<dialog id="myDialog">
  <p>对话框内容</p>
  <form method="dialog">
    <button>关闭</button>
  </form>
</dialog>
```

### `<template>` — 模板片段

仅全局属性。内容不被渲染，JS 克隆后使用。

```html
<template id="rowTemplate">
  <tr><td></td><td></td></tr>
</template>
```

### `<slot>` — Shadow DOM 插槽

| 属性 | 说明 |
|------|------|
| `name` | 插槽名称 |

### `<popover>` / `[popover]` — 弹出层（新标准）

任何元素加 `popover` 属性即可作为弹出层：

| 属性 | 说明 |
|------|------|
| `popover` | `auto`（默认）/ `manual` |
| `popovertarget` | 触发按钮指向的 popover id |
| `popovertargetaction` | `toggle` / `show` / `hide` |

---

## 10. 语义化与分区标签

这些标签主要用于页面布局，都是**仅全局属性**。

| 标签 | 含义 | 典型用途 |
|------|------|---------|
| `<header>` | 页头 / 区块头 | 导航栏、Logo、标题区 |
| `<footer>` | 页脚 / 区块脚 | 版权信息、联系方式 |
| `<main>` | 页面主要内容（每页仅一个） | 包裹核心内容 |
| `<nav>` | 导航区域 | 菜单、面包屑、目录 |
| `<aside>` | 侧边栏 / 补充内容 | 广告、相关链接、引用 |
| `<article>` | 独立可分发的内容 | 博客文章、新闻、评论 |
| `<section>` | 内容分区 | 章节、主题块 |
| `<div>` | 通用块级容器 | 布局、样式钩子 |
| `<hr>` | 主题分隔线 | 段落间场景切换 |
| `<h1>` ~ `<h6>` | 标题（1 级到 6 级） | 页面/区块标题 |
| `<p>` | 段落 | 正文段落 |
| `<search>` | 搜索区域（HTML5 新元素） | 搜索框 + 按钮容器 |

---

## 11. 废弃标签（避免使用）

这些标签已被 HTML5 标准废弃，用 CSS 或语义标签替代：

| 废弃标签 | 替代方案 |
|----------|---------|
| `<font>` | CSS `font-family` / `color` / `font-size` |
| `<center>` | CSS `text-align: center` 或 flexbox |
| `<big>` | CSS `font-size: larger` |
| `<strike>` | `<s>` 或 `<del>` |
| `<tt>` | `<code>` 或 CSS `font-family: monospace` |
| `<frame>` / `<frameset>` | `<iframe>` |
| `<noframes>` | `<noscript>` 或直接删除 |
| `<marquee>` | CSS animation（或直接用 JS） |
| `<blink>` | CSS animation（不推荐闪烁效果） |
| `<bgsound>` | `<audio>` |
| `<applet>` | `<object>` 或 WebAssembly |
| `<acronym>` | `<abbr>` |
| `<dir>` | `<ul>` |
| `<isindex>` | `<input>` + `<form>` |
| `<listing>` / `<xmp>` / `<plaintext>` | `<pre>` + `<code>` + HTML 实体转义 |
| `<keygen>` | Web Crypto API |
| `<menuitem>` | `<button>` 或 `<option>` |
| `<spacer>` | CSS `margin` / `padding` |
| `<basefont>` | CSS `font-size` on `<body>` |

---

## 附录 A：常用 `rel` 值汇总

用于 `<a>`、`<link>`、`<form>`：

| rel 值 | 说明 |
|--------|------|
| `noopener` | 禁止 `window.opener` 引用（防 tabnabbing，必加） |
| `noreferrer` | 不发送 Referer 头 |
| `nofollow` | 告诉搜索引擎不要追踪此链接 |
| `noindex` | （非标准）告诉搜索引擎不要索引目标页 |
| `stylesheet` | 外部样式表（仅 `<link>`） |
| `icon` | 网站图标（仅 `<link>`） |
| `preload` | 预加载资源（仅 `<link>`） |
| `prefetch` | 预取下一页资源（仅 `<link>`） |
| `dns-prefetch` | 预解析 DNS（仅 `<link>`） |
| `preconnect` | 预连接（DNS+TCP+TLS）（仅 `<link>`） |
| `canonical` | 规范 URL（仅 `<link>`） |
| `alternate` | 替代版本（RSS、多语言等） |
| `modulepreload` | 预加载 ES module（仅 `<link>`） |
| `manifest` | PWA 清单文件（仅 `<link>`） |
| `help` | 帮助文档链接 |
| `license` | 许可证链接 |
| `bookmark` | 永久链接（可收藏） |
| `tag` | 标签/关键字链接 |
| `next` / `prev` | 分页导航 |
| `author` | 作者链接 |
| `external` | 外部链接 |
| `opener` | （默认行为）允许 `window.opener`，**不安全，避免使用** |

---

## 附录 B：常用 MIME 类型速查

| MIME 类型 | 用途 |
|-----------|------|
| `text/html` | HTML 文档 |
| `text/css` | CSS 样式表 |
| `text/javascript` | JS（传统，现在用 `application/javascript`） |
| `application/javascript` | JavaScript |
| `application/json` | JSON 数据 |
| `image/jpeg` | JPEG 图片 |
| `image/png` | PNG 图片 |
| `image/webp` | WebP 图片 |
| `image/svg+xml` | SVG 矢量图 |
| `image/gif` | GIF 动图 |
| `image/x-icon` / `image/vnd.microsoft.icon` | ICO 图标 |
| `video/mp4` | MP4 视频 |
| `video/webm` | WebM 视频 |
| `audio/mpeg` | MP3 音频 |
| `audio/ogg` | OGG 音频 |
| `font/woff2` | WOFF2 字体 |
| `font/woff` | WOFF 字体 |
| `application/pdf` | PDF 文档 |
| `application/zip` | ZIP 压缩包 |
| `multipart/form-data` | 文件上传表单 |
| `application/x-www-form-urlencoded` | 普通表单提交 |

---

## 附录 C：A ria & 无障碍速查

| 场景 | ARIA 属性 | 说明 |
|------|----------|------|
| 无文字按钮 | `aria-label="关闭"` | 提供可读标签 |
| 描述性文字 | `aria-describedby="desc-id"` | 关联详细描述 |
| 隐藏装饰元素 | `aria-hidden="true"` | 对屏幕阅读器隐藏 |
| 动态内容 | `aria-live="polite"` | 内容变化时通知用户 |
| Tab 组件 | `role="tablist"` + `role="tab"` + `role="tabpanel"` | 完整 Tab 模式 |
| 模态框 | `role="dialog"` + `aria-modal="true"` | 告知当前为模态 |
| 折叠面板 | `aria-expanded="true/false"` | 展开/收起状态 |
| 当前页面 | `aria-current="page"` | 导航中标注当前位置 |
