# DOM and Browser

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [JavaScript for XSS](../JavaScript%20for%20XSS/JavaScript%20for%20XSS.md) | [XSS Payloads](../XSS%20Payloads/XSS%20Payloads.md)

---

## 什么是 DOM？

DOM（Document Object Model，文档对象模型）是浏览器将 HTML 文档解析后生成的树形结构编程接口。它将网页表示为一个节点树，使得编程语言（主要是 JavaScript）可以访问和修改文档的内容、结构和样式。

### DOM 与 HTML 源代码的区别

| 维度 | HTML 源代码 | DOM |
|------|-----------|-----|
| **本质** | 服务器发送的静态文本 | 浏览器解析后生成的内存中的动态对象 |
| **内容** | 仅包含服务器返回的原始标记 | 包含 JavaScript 动态修改后的所有内容 |
| **查看方式** | 浏览器"查看源代码" | 浏览器"检查元素"（DevTools） |
| **修改者** | 仅服务器端 | 服务器 + 客户端 JavaScript + 浏览器自动修正 |
| **安全性** | 可以通过输出编码在服务器端修复 XSS | DOM XSS 需要在客户端正确处理数据 |

> **关键理解：** DOM XSS 测试中，浏览器的"查看源代码"选项不可用，因为它不考虑 JavaScript 对 HTML 的修改。必须使用 DevTools 的 Elements 面板查看当前的 DOM 状态。

### DOM 树结构

一个简单的 HTML 文档：

```html
<!DOCTYPE html>
<html>
<head>
    <title>Example</title>
</head>
<body>
    <h1>Hello</h1>
    <p id="msg">World</p>
</body>
</html>
```

对应的 DOM 树：

```
document
└── html
    ├── head
    │   └── title
    │       └── "Example"
    └── body
        ├── h1
        │   └── "Hello"
        └── p#msg
            └── "World"
```

### DOM 节点类型

| 类型 | NodeType | 说明 | 示例 |
|------|----------|------|------|
| Element | 1 | HTML 元素 | `<div>`, `<p>`, `<script>` |
| Text | 3 | 元素的文本内容 | "Hello World" |
| Comment | 8 | HTML 注释 | `<!-- comment -->` |
| Document | 9 | 整个文档的根 | `document` |
| DocumentFragment | 11 | 轻量级的 Document 片段 | `document.createDocumentFragment()` |

---

## 浏览器解析 HTML 的完整流程

理解浏览器的解析流程对掌握 DOM XSS 至关重要。浏览器处理 HTML 的完整流程：

```
网络字节流 (Bytes)
    ↓ 字符解码 (根据 Content-Type 或 meta charset)
字符流 (Characters)
    ↓ Tokenization（标记化）
HTML Tokens
    ↓ Tree Construction（树构建）
DOM 树
    ↓ 同时解析 CSS → CSSOM
    ↓ JavaScript 在特定时机执行
完整渲染树 → Layout → Paint
```

### HTML 解析与 JavaScript 执行的关系

**关键规则：**

1. **同步 `<script>` 标签阻塞 HTML 解析：** 当 HTML 解析器遇到 `<script>` 标签时，暂停 HTML 解析，下载并执行脚本，然后继续解析。这意味着脚本可以访问到其之前已解析的 DOM，但无法访问未解析的后续元素。

2. **`<script>` 标签的闭合优先于 JavaScript 解析：** 浏览器首先通过 HTML 解析识别 `<script>` 块的边界（查找 `</script>` 字符串），然后才将内容传递给 JavaScript 引擎。这就是为什么可以在 JavaScript 字符串中通过 `</script>` 终止 script 块：

```html
<script>
var x = '</script><img src=x onerror=alert(1)>';
</script>
```

浏览器在 HTML 解析阶段看到 `</script>`，认为 script 块已结束，后面的 `<img>` 作为新的 HTML 元素被处理，导致 XSS 执行。而 JavaScript 引擎永远看不到后面的内容。

3. **`async` 和 `defer` 脚本不阻塞解析：**
   - `defer`：后台下载，HTML 解析完成后、`DOMContentLoaded` 之前按顺序执行
   - `async`：后台下载，下载完成后立即执行，不保证顺序

### DOMContentLoaded vs load

| 事件 | 触发时机 | 对 XSS 的影响 |
|------|---------|-------------|
| `DOMContentLoaded` | HTML 完全解析，DOM 构建完成（不等待图片、样式表） | 此时可以安全操作所有 DOM 元素 |
| `load` | 页面所有资源（图片、样式、iframe）加载完成 | 更晚触发，适合需要等待资源的 payload |

---

## 服务器端渲染 vs 客户端渲染

### 服务器端渲染（SSR）

- 服务器生成完整的 HTML 页面并发送给浏览器
- 浏览器直接渲染接收到的 HTML
- **XSS 影响：** 反射型和存储型 XSS 发生在 SSR 中，由服务器端代码在嵌入用户数据时未正确编码导致

### 客户端渲染（CSR）

- 服务器发送空壳 HTML + JavaScript bundle
- JavaScript 在浏览器中动态构建 DOM（React、Vue、Angular 等框架）
- **XSS 影响：** 现代框架提供自动 HTML 转义（如 React 的 JSX），但开发者显式使用的不安全 API（如 React 的 `dangerouslySetInnerHTML`、Vue 的 `v-html`、Angular 的 `bypassSecurityTrustHtml`）可能引入 DOM XSS

### 框架中的危险 API

```javascript
// React -- dangerouslySetInnerHTML (类似 innerHTML)
<div dangerouslySetInnerHTML={{__html: userInput}} />

// Vue -- v-html 指令
<div v-html="userInput"></div>

// Angular -- bypassSecurityTrustHtml
this.sanitizer.bypassSecurityTrustHtml(userInput);
```

---

## Sources（源）详解

Source 是攻击者能够控制的、浏览器端的输入点。在 DOM XSS 的 taint flow 模型中，source 是数据流的起点。

### URL 相关 Sources

URL 是最常见的 DOM XSS source，攻击者可以通过构造恶意链接将 payload 传递给受害者。

| Source | 说明 | 内容示例 |
|--------|------|---------|
| `window.location` | 当前页面的完整 Location 对象 | `https://site.com/page?q=search` |
| `window.location.href` | 完整 URL 字符串 | `"https://site.com/page?q=search"` |
| `window.location.search` | URL 查询字符串（含 `?`） | `"?q=search"` |
| `window.location.hash` | URL 片段标识符（含 `#`） | `"#section1"` |
| `window.location.pathname` | URL 路径 | `"/page"` |
| `document.URL` | 当前文档的完整 URL | `"https://site.com/page"` |
| `document.documentURI` | 文档 URI（与 URL 类似） | `"https://site.com/page"` |
| `document.baseURI` | 文档的基础 URI | `"https://site.com/"` |

**URL 编码行为差异：**

| 浏览器 | location.search | location.hash |
|--------|----------------|---------------|
| Chrome | URL 编码 | URL 编码 |
| Firefox | URL 编码 | URL 编码 |
| Safari | URL 编码 | URL 编码 |
| IE11 / Edge (旧) | 不编码 | 不编码 |

如果浏览器对 source 值进行 URL 编码后再传递给 JavaScript，攻击者需要确保 payload 在 URL 编码后仍然有效（即 payload 中使用不包含需编码字符的技术）。

### 其他浏览器 Sources

| Source | 说明 | 攻击向量 |
|--------|------|---------|
| `document.cookie` | 当前页面的 Cookie（非 HttpOnly） | Cookie 值可控时（通过其他漏洞设置），在某些条件可作 source |
| `document.referrer` | 引用页面的 URL | 攻击者控制来源页面，可在 referrer 中放入 payload |
| `window.name` | 窗口名称，跨域持久存在 | 通过 `window.open()` 设置，跨域导航后仍然保留 |
| `postMessage` 接收的数据 | 跨窗口/iframe 消息 | 如果接收方不验证 origin，攻击者可以发送任意数据 |
| `localStorage` / `sessionStorage` | 浏览器本地存储 | 如果攻击者能向存储中写入数据（通过其他漏洞或功能），可能被读取到 sink |
| `history.pushState` / `replaceState` | 修改的 URL | 修改后的状态可能被其他代码读取 |
| `XMLHttpRequest` / `fetch` 响应 | 网络请求的响应数据 | 如果响应数据被不安全地写入 DOM |
| `navigator.userAgent` | 用户代理字符串 | 在某些情况下可控或部分可控 |

---

## Sinks（汇）详解

Sink 是可导致任意 JavaScript 执行的 API 或 DOM 操作。在 DOM XSS 的 taint flow 模型中，sink 是数据流的终点。

### JavaScript 执行 Sinks

这些 sink 直接将字符串作为 JavaScript 代码执行：

| Sink | 类型 | 示例 | 风险等级 |
|------|------|------|---------|
| `eval()` | JS 执行 | `eval(userInput)` | 极高 |
| `new Function()` | JS 执行 | `new Function('return ' + userInput)()` | 极高 |
| `setTimeout()` (字符串) | JS 执行 | `setTimeout(userInput, 1000)` | 高 |
| `setInterval()` (字符串) | JS 执行 | `setInterval(userInput, 5000)` | 高 |
| `execScript()` | JS 执行 (仅IE) | `execScript(userInput)` | 极高 |

### HTML 注入 Sinks

这些 sink 将字符串作为 HTML 写入 DOM。它们不执行 `<script>` 标签（在现代浏览器中），但会触发事件处理器：

| Sink | 说明 | 示例 |
|------|------|------|
| `element.innerHTML` | 设置元素的 HTML 内容 | `div.innerHTML = userInput` |
| `element.outerHTML` | 替换整个元素 | `element.outerHTML = userInput` |
| `document.write()` | 向文档写入 HTML | `document.write(userInput)` |
| `document.writeln()` | 同 write()，追加换行 | `document.writeln(userInput)` |
| `element.insertAdjacentHTML()` | 在指定位置插入 HTML | `div.insertAdjacentHTML('beforeend', userInput)` |
| `Range.createContextualFragment()` | 从 HTML 字符串创建片段 | `range.createContextualFragment(userInput)` |

### URL 导航 Sinks

当输入以 `javascript:` 开头时，这些 sink 可以执行 JavaScript：

| Sink | 说明 | 示例 |
|------|------|------|
| `location.href` | 导航到新 URL | `location.href = userInput` |
| `location.replace()` | 替换当前 URL | `location.replace(userInput)` |
| `location.assign()` | 导航到新 URL | `location.assign(userInput)` |
| `window.open()` | 打开新窗口 | `window.open(userInput)` |
| `<a>.href` | 设置链接目标 | `link.href = userInput` |
| `<iframe>.src` | 设置 iframe 源 | `iframe.src = userInput` |

### jQuery Sinks

| Sink | 说明 |
|------|------|
| `$()` | 如果输入以 `<` 开头，创建新的 DOM 元素 |
| `$().html()` | 设置元素的 HTML 内容 |
| `$().append()` / `$().prepend()` | 在元素内追加/前置 HTML |
| `$().after()` / `$().before()` | 在元素后/前插入 HTML |
| `$().replaceAll()` / `$().replaceWith()` | 替换元素 |
| `$().wrap()` / `$().wrapInner()` / `$().wrapAll()` | 包裹元素 |
| `$().attr('href', ...)` / `$().attr('src', ...)` | 修改危险属性 |
| `$.parseHTML()` | 解析 HTML 字符串（需要注意上下文） |

---

## Taint Flow：Source 到 Sink 的数据流

DOM XSS 的本质是存在一个从 source 到 sink 的可执行路径。这个数据流路径称为 **taint flow**。

### 简单示例

```javascript
// Source: URL 查询参数
var search = new URLSearchParams(location.search).get('q');

// 中间处理（可能存在，也可能没有）
var message = 'You searched for: ' + search;

// Sink: innerHTML
document.getElementById('results').innerHTML = message;
```

攻击者构造 URL：`https://site.com/search?q=<img src=x onerror=alert(1)>`

### 复杂 Taint Flow

```javascript
// Source
var hash = location.hash.slice(1);

// 赋值给其他变量
var config = JSON.parse(decodeURIComponent(hash));

// 传递到函数
function updateUI(data) {
    // 间接传递
    var html = template.replace('{{content}}', data.content);

    // Sink（深层嵌套）
    document.querySelector('.main').innerHTML = html;
}

updateUI(config);
```

这种复杂流程中，追踪 source 的传播路径需要进行代码审查或使用 DOM Invader 等自动化工具。

### Source 到 Sink 的追踪方法

1. **手动追踪：** 使用 Chrome DevTools 的全局搜索（Control+Shift+F）搜索 source 关键字（如 `location.search`），找到所有引用，然后添加断点追踪数据流
2. **DOM Invader：** Burp Suite 浏览器内置的扩展，自动注入 canary 值到各个 source，监控哪些值到达了 sink
3. **静态分析：** 审查 JavaScript 代码，识别 source → variable → function → sink 的完整路径

---

## DOM API 安全性对比

| API | 执行 `<script>` | 触发事件处理器 | 推荐度 | 说明 |
|-----|----------------|--------------|--------|------|
| `textContent` | 否 | 否 | 推荐 | 纯文本，最安全 |
| `innerText` | 否 | 否 | 推荐 | 类似 textContent，考虑 CSS 样式 |
| `createElement` + `appendChild` | 否 | 否 | 推荐 | 通过 DOM API 构建元素 |
| `createTextNode` | 否 | 否 | 推荐 | 纯文本节点 |
| `innerHTML` | 否（现代浏览器） | 是 | 避免 | `<script>` 不执行，但 `<img onerror>` 等执行 |
| `outerHTML` | 否（现代浏览器） | 是 | 避免 | 同 innerHTML |
| `document.write` | 是 | 是 | 绝对避免 | 直接写入文档流，可执行 `<script>` |
| `insertAdjacentHTML` | 否（现代浏览器） | 是 | 避免 | 同 innerHTML |
| `eval` | N/A | N/A | 绝对避免 | 直接执行任意 JavaScript |

---

## DOM Clobbering

DOM Clobbering 是一种利用 HTML 元素覆盖 JavaScript 全局变量的技术，可能导致安全检查被绕过或制造 XSS 条件。

### 基本原理

浏览器会自动为具有 `id` 或 `name` 属性的 HTML 元素创建全局 JavaScript 变量：

```html
<!-- 这个元素会自动创建全局变量 config -->
<form id="config">
    <input name="debug" value="true">
</form>

<script>
// config 现在是 HTMLFormElement，而非预期的配置对象
if (config.debug) {  // config.debug 是 <input name="debug">
    // 可能绕过安全检查
}
</script>
```

### DOM Clobbering 在 XSS 中的利用

```html
<!-- 覆盖 document.cookie -->
<img name="cookie" src="x">

<!-- 覆盖检查函数 -->
<a id="isAdmin" href="x">

<!-- 覆盖配置 -->
<form id="appConfig">
    <input name="allowHtml" value="true">
</form>
```

如果 JavaScript 代码依赖这些全局变量进行安全检查，DOM Clobbering 可以完全绕过这些检查。

---

## Shadow DOM 与安全边界

Shadow DOM 是 Web Components 的核心技术，允许在元素内部创建封装的 DOM 树。

**安全影响：**

- Shadow DOM 内部的 XSS 影响范围**通常**限于 Shadow tree 内
- 但 Shadow DOM 并非安全边界——攻击者仍可以通过其他方式访问外部 DOM
- 如果 Shadow DOM 内使用了不安全的 API，仍可能触发 XSS

---

## 浏览器差异对 DOM XSS 的影响

| 行为 | Chrome | Firefox | Safari | Edge (旧) |
|------|--------|---------|--------|-----------|
| `location.search` URL 编码 | 是 | 是 | 是 | 否 |
| `location.hash` URL 编码 | 是 | 是 | 是 | 否 |
| `<script>` 通过 innerHTML 执行 | 否 | 否 | 否 | 否 |
| `<script>` 通过 document.write 执行 | 是 | 是 | 是 | 是 |
| `javascript:` URL 在 `<iframe>` src | 是 | 是 | 是 | 是 |
| dangling markup 保护 | 是（Chrome 修复） | 部分 | 部分 | 否 |

---

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [JavaScript for XSS](../JavaScript%20for%20XSS/JavaScript%20for%20XSS.md) | [XSS Payloads](../XSS%20Payloads/XSS%20Payloads.md)
