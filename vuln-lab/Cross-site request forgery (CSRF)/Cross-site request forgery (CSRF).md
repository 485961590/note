# Cross-Site Request Forgery (CSRF)

> **参考：** [XSS](../Cross-site%20scripting%20(XSS)/) | [SameSite Cookie](../../../协议/HTTPandHTTPS.md) | [CORS](../../../协议/)

---

## 什么是 CSRF？

跨站请求伪造（Cross-Site Request Forgery，简称 CSRF）是一种 Web 安全漏洞，允许攻击者诱导用户执行其本不愿意执行的操作。它使攻击者能够部分绕过同源策略（Same Origin Policy），该策略旨在防止不同网站之间相互干扰。

Same Origin Policy：“源”由**协议（Protocol）**、**域名（Host）**和**端口（Port）**三部分组成。只有当这三者**完全一致**时，才叫同源。

---

## CSRF 攻击的影响

在成功的 CSRF 攻击中，攻击者使受害用户无意中执行了某个操作。例如：

- 更改账户的邮箱地址
- 修改密码
- 进行资金转账
![](./img/file-20260703011545697.png)
根据操作的性质，攻击者可能获得对用户账户的完全控制。如果被攻陷的用户在应用程序中具有特权角色，攻击者可能能够完全控制应用程序的所有数据和功能。

---

## CSRF 的工作原理

### 核心原理：浏览器自动携带 Cookie

CSRF 的核心是利用了浏览器的"自动携带 Cookie"机制。攻击者盗用你的身份，以你的名义发送恶意请求。完整流程如下：

1. **登录信任站点**：你登录了银行网站 A，浏览器保存了登录凭证 Cookie
2. **访问恶意站点**：在未登出 A 的情况下，你访问了危险网站 B
3. **触发伪造请求**：网站 B 中隐藏了指向 A 的恶意请求，比如一段自动提交的表单代码
4. **浏览器自动执行**：浏览器发起跨域请求时，会自动带上 A 站的 Cookie
5. **攻击成功**：A 站收到请求，校验 Cookie 通过，误以为是你本人的操作，执行了转账

> **一句话总结：** CSRF 是"挟持用户在已登录的 Web 应用上执行非本意操作的攻击方法"——攻击者无法直接窃取你的 Cookie（同源策略保护了这一点），但可以利用浏览器"自动携带"的特性，让你在不知情的情况下替攻击者发出请求。

### 攻击成立的必要条件

要使 CSRF 攻击成为可能，必须同时满足三个关键条件：

| 条件 | 说明 |
|------|------|
| **一个相关的操作** | 应用程序中存在攻击者有理由诱导的操作。可能是特权操作（如修改其他用户的权限）或针对用户特定数据的操作（如修改用户自己的密码） |
| **基于 Cookie 的会话处理** | 执行操作涉及发出一个或多个 HTTP 请求，且应用程序仅依赖会话 Cookie 来识别发出请求的用户。没有其他机制来跟踪会话或验证用户请求 |
| **无可预测的请求参数** | 执行操作的请求不包含攻击者无法确定或猜测的参数值。例如，在诱导用户修改密码时，如果攻击者需要知道现有密码的值，则该功能不易受攻击 |

### 示例

假设一个应用程序允许用户更改其账户的邮箱地址。用户执行此操作时，发出如下 HTTP 请求：

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 30
Cookie: session=yvthwsztyeQkAPzeQ5gHgTvlyxHfsAfE

email=wiener@normal-user.com
```

这个请求满足 CSRF 所需的三个条件：

1. **相关操作**：更改用户邮箱地址的操作对攻击者有兴趣。通过此操作，攻击者通常可以触发密码重置并完全控制用户账户
2. **Cookie 会话处理**：应用程序使用会话 Cookie 来识别用户，没有其他令牌或机制来跟踪用户会话
3. **无不可预测参数**：攻击者可以轻松确定执行操作所需的请求参数值

### 攻击 HTML 构造

有了以上条件，攻击者可以构造包含以下 HTML 的网页：

```html
<html>
    <body>
        <form action="https://vulnerable-website.com/email/change" method="POST">
            <input type="hidden" name="email" value="pwned@evil-user.net" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

### 攻击流程

当受害用户访问攻击者的网页时，将发生以下过程：

1. 攻击者的页面触发对漏洞网站的 HTTP 请求
2. 如果用户已登录漏洞网站，浏览器会自动在请求中包含其会话 Cookie（假设未使用 SameSite Cookie）
3. 漏洞网站以正常方式处理请求，将其视为由受害用户发出，并更改其邮箱地址

**注意：** 虽然 CSRF 通常与基于 Cookie 的会话处理相关，但它也出现在应用程序自动向请求添加用户凭据的其他场景中，如 HTTP Basic 认证和基于证书的认证。

---

## 如何构造 CSRF 攻击

手动创建 CSRF 利用所需的 HTML 可能很繁琐，特别是在所需请求包含大量参数或存在其他特殊情况下。最简单的构造方法是使用 Burp Suite Professional 内置的 CSRF PoC 生成器：

1. 在 Burp Suite Professional 中选择要测试或利用的任意请求
2. 在右键菜单中选择 **Engagement tools / Generate CSRF PoC**
3. Burp Suite 将生成触发所选请求的 HTML（不含 Cookie，受害者的浏览器会自动添加）
4. 可以在 CSRF PoC 生成器中调整各种选项以微调攻击的各个方面
5. 将生成的 HTML 复制到网页中，在已登录漏洞网站的浏览器中查看，并测试请求是否成功发出且所需操作是否执行

---

## 如何交付 CSRF 利用

CSRF 攻击的交付机制与反射型 XSS 基本相同。通常，攻击者将恶意 HTML 放置在由其控制的网站上，然后诱导受害者访问该网站。这可以通过以下方式完成：

- 通过电子邮件或社交媒体消息向用户发送网站链接
- 如果攻击被放置在流行网站上（例如，在用户评论中），攻击者可能只需等待用户访问该网站

### 自包含的 GET 型 CSRF 攻击

一些简单的 CSRF 利用使用 GET 方法，可以通过一个在漏洞网站上的 URL 完全自包含。在这种情况下，攻击者可能不需要使用外部网站，可以直接向受害者提供漏洞域名上的恶意 URL。

如果更改邮箱地址的请求可以使用 GET 方法执行，则自包含攻击如下：

```html
<img src="https://vulnerable-website.com/email/change?email=pwned@evil-user.net">
```

---

## XSS 与 CSRF 的区别

### 核心差异

| 维度 | XSS (Cross-Site Scripting) | CSRF (Cross-Site Request Forgery) |
|------|---------------------------|----------------------------------|
| **定义** | 允许攻击者在受害用户浏览器中执行任意 JavaScript | 允许攻击者诱导受害用户执行其本不打算执行的操作 |
| **严重性** | 通常更严重 | 通常影响范围较小 |
| **作用范围** | 成功利用后可以诱导用户执行其能够执行的任何操作 | 通常仅适用于用户可以执行的**操作子集** |
| **数据流向** | "双向" —— 攻击者注入的脚本可以发出任意请求、读取响应并将数据外泄 | "单向" —— 攻击者可以诱导受害者发出 HTTP 请求，但**无法获取该请求的响应** |

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

假设服务器正确验证 CSRF 令牌并拒绝没有有效令牌的请求，那么令牌确实可以防止 XSS 漏洞的利用。关键点在于：反射型 XSS 涉及跨站请求，通过防止攻击者伪造跨站请求，应用程序防止了 XSS 漏洞的简单利用。

**重要注意事项：**

1. 如果站点上其他地方存在未被 CSRF 令牌保护的反射型 XSS 漏洞，该 XSS 仍可被正常利用
2. 如果站点上存在可利用的 XSS 漏洞，即使目标操作本身受 CSRF 令牌保护，漏洞也可以被用来让受害用户执行这些操作。攻击者的脚本可以请求相关页面获取有效 CSRF 令牌，然后使用该令牌执行受保护的操作
3. CSRF 令牌**不能防御存储型 XSS**。如果一个受 CSRF 令牌保护的页面同时也是存储型 XSS 的输出点，该 XSS 仍然可以正常利用

---

## CSRF 的常见防御措施

如今，成功发现和利用 CSRF 漏洞通常涉及绕过目标网站、受害者浏览器或两者部署的反 CSRF 措施。最常见的防御措施包括：

| 防御措施 | 说明 |
|----------|------|
| **CSRF 令牌** | 由服务器端应用程序生成并与客户端共享的唯一、保密且不可预测的值。执行敏感操作时，客户端必须在请求中包含正确的 CSRF 令牌 |
| **SameSite Cookie** | 浏览器安全机制，确定网站的 Cookie 何时包含在来自其他网站的请求中。Chrome 自 2021 年起默认强制执行 `Lax` SameSite 限制 |
| **Referer 头验证** | 一些应用程序使用 HTTP Referer 头来防御 CSRF 攻击，通常通过验证请求是否来自应用程序自己的域名。通常不如 CSRF 令牌验证有效 |

---

## 绕过 CSRF 令牌验证

### 什么是 CSRF 令牌？

CSRF 令牌是由服务器端应用程序生成的唯一、保密且不可预测的值，并与客户端共享。当发出执行敏感操作的请求时，客户端必须包含正确的 CSRF 令牌，否则服务器将拒绝执行请求的操作。

常见的共享方式是将令牌作为 HTML 表单中的隐藏参数：

```html
<form name="change-email-form" action="/my-account/change-email" method="POST">
    <label>Email</label>
    <input required type="email" name="email" value="example@normal-website.com">
    <input required type="hidden" name="csrf" value="50FaWgdOhi9M9wyna8taR1k3ODOR8d6u">
    <button class='button' type='submit'> Update email </button>
</form>
```

提交此表单将产生以下请求：

```
POST /my-account/change-email HTTP/1.1
Host: normal-website.com
Content-Length: 70
Content-Type: application/x-www-form-urlencoded

csrf=50FaWgdOhi9M9wyna8taR1k3ODOR8d6u&email=example@normal-website.com
```

**注意：** CSRF 令牌不一定通过 POST 请求中的隐藏参数发送。一些应用程序将 CSRF 令牌放在 HTTP 头中。令牌的传输方式对整体机制的安全性有显著影响。

### CSRF 令牌验证的常见缺陷

#### 1. 令牌验证依赖请求方法

**缺陷：** 应用程序在使用 POST 方法时正确验证令牌，但在使用 GET 方法时跳过验证。

**绕过方式：** 切换到 GET 方法来绕过验证（使用burp 的change request method而非手动修改POST为GET）：

```
GET /email/change?email=pwned@evil-user.net HTTP/1.1
Host: vulnerable-website.com
Cookie: session=2yQIDcpia41WrATfjPqvm9tOkDvkMvLm
```

---

#### 2. 令牌验证依赖令牌是否存在

**缺陷：** 应用程序在令牌存在时正确验证，但如果令牌被省略则跳过验证。

**绕过方式：** 删除整个包含令牌的参数（不仅仅是其值）：

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 25
Cookie: session=2yQIDcpia41WrATfjPqvm9tOkDvkMvLm

email=pwned@evil-user.net
```

---

#### 3. CSRF 令牌未绑定到用户会话

**缺陷：** 应用程序不验证令牌是否属于当前发起请求的用户会话。相反，应用程序维护一个已颁发令牌的全局池，并接受池中的任何令牌。

**绕过方式：** 攻击者使用自己的账户登录应用程序，获取有效令牌，然后将该令牌提供给 CSRF 攻击中的受害用户。

---

#### 4. CSRF 令牌绑定到非会话 Cookie

**缺陷：** 应用程序将 CSRF 令牌绑定到 Cookie，但绑定的并非用于跟踪会话的同一 Cookie。这通常发生在应用程序使用两个不同框架时（一个用于会话处理，一个用于 CSRF 保护），且两者未集成在一起：

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 68
Cookie: session=pSJYSScWKpmC60LpFOAHKixuFuM4uXWF; csrfKey=rZHCnSzEp8dbI6atzagGoSYyqJqTz5dv

csrf=RhV7yQDO0xcq9gLEah2WVbmuFqyOq7tY&email=wiener@normal-user.com
```

**利用方式：** 如果网站包含任何允许攻击者在受害者浏览器中设置 Cookie 的行为，则攻击可行：
1. 攻击者使用自己的账户登录，获取有效令牌和关联的 Cookie
2. 利用 Cookie 设置行为将其 Cookie 置入受害者浏览器
3. 在 CSRF 攻击中将令牌提供给受害者

**注意：** Cookie 设置行为甚至不需要存在于与 CSRF 漏洞相同的 Web 应用程序中。同一 DNS 域名内的任何其他应用程序都可以潜在地被利用来设置目标应用程序的 Cookie。

---

#### 5. CSRF 令牌在 Cookie 中简单重复（Double Submit）

**缺陷：** 应用程序不在服务器端维护已颁发令牌的记录，而是将每个令牌同时复制在 Cookie 和请求参数中。验证时仅检查请求参数中的令牌值是否与 Cookie 中提交的值匹配。这被称为 CSRF 的"双重提交"（double submit）防御：

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 68
Cookie: session=1DQGdzYbOJQzLP7460tfyiv3do7MjyPw; csrf=R8ov2YBfTYmzFyjit8o2hKBuoIjXXVpa

csrf=R8ov2YBfTYmzFyjit8o2hKBuoIjXXVpa&email=wiener@normal-user.com
```

**绕过方式：** 如果网站包含 Cookie 设置功能，攻击者无需获取自己的有效令牌：
1. 攻击者自行创造一个令牌（如果应用程序检查格式，则按要求的格式生成）
2. 利用 Cookie 设置行为将其 Cookie 置入受害者浏览器
3. 在 CSRF 攻击中将相同的令牌提供给受害者

---

### CSRF 令牌绕过方法对比总结

| 绕过方法 | 核心缺陷 | 攻击条件 | 难度 |
|----------|----------|----------|------|
| 切换请求方法 | POST 验证，GET 不验证 | 目标端点接受 GET 请求 | 低 |
| 删除令牌参数 | 令牌存在时验证，缺失时跳过 | 无 | 低 |
| 令牌池共享 | 不验证令牌与会话的绑定关系 | 攻击者有自己的账户 | 中 |
| 绑定到非会话 Cookie | CSRF 令牌绑定到独立 Cookie | 存在 Cookie 设置功能（同域亦可） | 中 |
| Double Submit | 无服务器端令牌记录 | 存在 Cookie 设置功能 | 中 |

---

## 绕过 SameSite Cookie 限制

SameSite 是一种浏览器安全机制，用于确定网站的 Cookie 何时包含在来自其他网站的请求中。SameSite Cookie 限制为各种跨站攻击（包括 CSRF、跨站泄露和某些 CORS 利用）提供了部分保护。

自 2021 年起，如果发 Cookie 的网站未明确设置自己的限制级别，Chrome 默认应用 `Lax` SameSite 限制。这是提议的标准，预计其他主流浏览器将来也会采用此行为。

### 核心概念：Site vs Origin

在 SameSite Cookie 限制的语境中，**site（站点）** 定义为顶级域名（TLD，如 `.com` 或 `.net`）加上域名的**一个额外级别**，通常称为 TLD+1。

在判断请求是否为同站（same-site）时，URL 的 scheme（协议）也会被考虑。这意味着从 `http://app.example.com` 到 `https://app.example.com` 的链接会被大多数浏览器视为跨站（cross-site）。

| 请求来源 | 请求目标 | 同站？ | 同源？ |
|----------|----------|--------|--------|
| `https://example.com` | `https://example.com` | 是 | 是 |
| `https://app.example.com` | `https://intranet.example.com` | **是** | 否（域名不匹配） |
| `https://example.com` | `https://example.com:8080` | **是** | 否（端口不匹配） |
| `https://example.com` | `https://example.co.uk` | 否（eTLD 不匹配） | 否（域名不匹配） |
| `https://example.com` | `http://example.com` | 否（scheme 不匹配） | 否（scheme 不匹配） |

**关键区别：** 跨源请求仍然可能是同站的，但反过来不行。这意味着任何允许任意 JavaScript 执行的漏洞都可以被滥用来绕过同一站点上其他域名的基于 site 的防御。

### SameSite 限制级别

所有主流浏览器目前支持以下 SameSite 限制级别：

| 级别 | 行为 | 适用场景 |
|------|------|----------|
| **Strict** | 浏览器不在**任何**跨站请求中发送 Cookie | 敏感操作（如修改数据、访问需要认证的页面）。最安全但可能影响用户体验 |
| **Lax** | 浏览器仅在满足以下**两个条件**的跨站请求中发送 Cookie：1) 使用 GET 方法；2) 请求由用户的顶级导航（如点击链接）触发。Cookie 不在跨站 POST 请求或后台请求（脚本、iframe、图片引用）中发送 | Chrome 的默认行为。在安全性和用户体验之间取得平衡 |
| **None** | 完全禁用 SameSite 限制。浏览器在所有请求中发送此 Cookie，包括由无关第三方网站触发的请求。**必须同时设置 `Secure` 属性**（仅通过 HTTPS 发送），否则浏览器拒绝设置该 Cookie | 需要在第三方上下文中使用的 Cookie（如追踪 Cookie） |

**设置方式：**

```
Set-Cookie: session=0F8tgdOhi9ynR1M9wa3ODa; SameSite=Strict
Set-Cookie: trackingId=0F8tgdOhi9ynR1M9wa3ODa; SameSite=None; Secure
```

---

### 绕过 SameSite Lax 限制：使用 GET 请求

服务器并不总是严格要求特定端点接收 GET 还是 POST 请求。如果会话 Cookie 使用 Lax 限制并允许 GET 方法，则可以通过诱导受害浏览器发起 GET 请求来执行 CSRF 攻击。

**最简单的攻击方式：**

```html
<script>
    document.location = 'https://vulnerable-website.com/account/transfer-payment?recipient=hacker&amount=1000000';
</script>
```

**方法覆盖绕过：** 即使普通的 GET 请求不被允许，一些框架提供了覆盖请求行中指定方法的方式。例如，Symfony 支持表单中的 `_method` 参数：

```html
<form action="https://vulnerable-website.com/account/transfer-payment" method="GET">
    <input type="hidden" name="_method" value="POST">
    <input type="hidden" name="recipient" value="hacker">
    <input type="hidden" name="amount" value="1000000">
</form>
```

其他框架也支持各种类似参数。

---

### 绕过 SameSite Strict 限制：使用站内 Gadget

如果 Cookie 设置了 `SameSite=Strict`，浏览器不会在任何跨站请求中包含它。可以利用站内小工具（gadget）发起同站内的二次请求来绕过此限制。

**客户端重定向（Client-side Redirect）：**

一种可能的 gadget 是客户端重定向，它使用攻击者可控制的输入（如 URL 参数）动态构造重定向目标。从浏览器角度看，这些客户端重定向被视为普通的独立请求——是同站请求，因此会包含站点的所有 Cookie，无论设置了何种限制。

如果攻击者可以操纵此 gadget 来发起恶意的二次请求，就能完全绕过 SameSite Cookie 限制。

**注意：** 等效攻击在服务端重定向中不可行。浏览器会识别出该重定向请求最初来自跨站请求，因此仍会应用适当的 Cookie 限制。

---

### 绕过 SameSite 限制：利用有漏洞的兄弟域名

请求即使跨源（cross-origin），仍然可以是同站（same-site）的。因此必须彻底审计所有可用的攻击面，包括任何兄弟域名。XSS 等能够发起任意二次请求的漏洞可以完全破坏基于 site 的防御，使站点的所有域名暴露于跨站攻击之下。

此外，如果目标网站支持 WebSocket，该功能可能容易受到跨站 WebSocket 劫持（CSWSH）攻击，这本质上是针对 WebSocket 握手的 CSRF 攻击。

---

### 绕过 SameSite Lax 限制：利用新颁发的 Cookie

为了不破坏单点登录（SSO）机制，Chrome 在 Cookie 设置后的**前 120 秒**内不对顶级 POST 请求强制执行 Lax 限制。这意味着存在一个两分钟的时间窗口，用户在此期间可能容易受到跨站攻击。

**注意：** 此两分钟窗口不适用于显式设置了 `SameSite=Lax` 属性的 Cookie。

**利用思路：**

1. 找到站内小工具，强制受害者被颁发新的会话 Cookie（如通过 OAuth 登录流程——OAuth 服务不一定知道用户是否已登录目标站点）
2. 在 Cookie 刷新后的 120 秒窗口内发起 CSRF 攻击

**触发 Cookie 刷新的方式：**

- 使用顶级导航触发 Cookie 刷新（确保包含当前 OAuth 会话的 Cookie），然后重定向回攻击者站点发起 CSRF 攻击
- 从新标签页触发 Cookie 刷新（浏览器不会离开当前页面）

**新标签页方法中的弹窗绕过：** 浏览器默认阻止弹窗标签页，除非通过手动交互打开。可以通过 `onclick` 事件处理器绕过：

```javascript
window.onclick = () => {
    window.open('https://vulnerable-website.com/login/sso');
}
```

`window.open()` 方法仅在用户点击页面上某处时被调用。

---

## 绕过基于 Referer 的 CSRF 防御

### Referer 验证依赖于头部是否存在

**缺陷：** 应用程序在请求中存在 Referer 头时验证，但如果头部被省略则跳过验证。

**绕过方式：** 通过在托管 CSRF 攻击的 HTML 页面中使用 META 标签，使浏览器在发出请求时丢弃 Referer 头：

```html
<meta name="referrer" content="never">
```

---

### Referer 验证可以被规避

**缺陷：** 应用程序以可被绕过的简单方式验证 Referer 头。例如：

- **仅验证域名前缀：** 如果应用程序验证 Referer 中的域名以预期值**开头**，攻击者可以将其作为子域名放置：

  ```
  http://vulnerable-website.com.attacker-website.com/csrf-attack
  ```

- **仅验证包含域名：** 如果应用程序仅验证 Referer 是否**包含**自己的域名，攻击者可以将所需值放在 URL 的其他位置：

  ```
  http://attacker-website.com/csrf-attack?vulnerable-website.com
  ```

**注意：** 为了减少敏感数据泄露的风险，许多浏览器现在默认从 Referer 头中去除查询字符串。可以通过确保包含利用的响应设置了 `Referrer-Policy: unsafe-url` 头来覆盖此行为（注意此处 Referrer 的拼写是**三个 r**），以确保完整 URL（含查询字符串）被发送。

---

## CSRF 防御措施绕过方法对比

| 防御类型 | 绕过方式 | 核心原理 |
|----------|----------|----------|
| CSRF 令牌 (请求方法) | 切换到 GET 方法 | POST 验证，GET 不验证 |
| CSRF 令牌 (令牌存在) | 删除令牌参数 | 有令牌时验证，无令牌时跳过 |
| CSRF 令牌 (会话绑定) | 使用自己的令牌 | 令牌池全局共享，不绑定会话 |
| CSRF 令牌 (Cookie 绑定) | Cookie 注入 + 自己的令牌 | 令牌绑定到独立 Cookie，可被覆盖 |
| CSRF 令牌 (Double Submit) | Cookie 注入 + 自创令牌 | 无服务器端记录，仅比对 Cookie 和参数值 |
| SameSite Lax | GET 请求 / 方法覆盖 | Lax 允许 GET 顶级导航；框架支持方法覆盖参数 |
| SameSite Strict | 客户端重定向 Gadget | 站内二次请求携带所有 Cookie |
| SameSite Strict | 兄弟域名 XSS | 同站跨源攻击；XSS 完全破坏 site 级防御 |
| SameSite Lax (新 Cookie) | 120 秒窗口 + Cookie 刷新 | Chrome 对无显式 SameSite 的新 Cookie 有 120s 豁免 |
| Referer (头存在) | META no-referrer | 去除 Referer 头使验证跳过 |
| Referer (域名前缀) | 子域名伪造 | `target.com.attacker.com` 通过前缀检查 |
| Referer (域名包含) | 查询参数注入 | `attacker.com?target.com` 通过包含检查 |

---

## 如何防御 CSRF 漏洞

### 1. 使用 CSRF 令牌（最健壮的方法）

CSRF 令牌必须满足以下标准：

| 要求 | 说明 |
|------|------|
| **不可预测 + 高熵** | 与会话令牌相同的属性，使用加密安全的伪随机数生成器（CSPRNG），种子为创建时间戳 + 静态密钥 |
| **绑定到用户会话** | 生成后存储在服务器端的用户会话数据中 |
| **严格验证** | 在每个需要验证的请求中执行，无论 HTTP 方法或内容类型。请求中完全缺少令牌时应与存在无效令牌一样拒绝 |

**令牌传输：**

| 方式 | 评价 |
|------|------|
| **HTML 表单隐藏字段（POST）** | 推荐方式。字段应放在 HTML 文档中尽可能早的位置，最好在任何非隐藏输入字段和用户可控数据嵌入位置之前，以减轻 HTML 操纵攻击 |
| **URL 查询字符串** | 较不安全。查询字符串在客户端和服务器端的多个地方被记录，可能通过 HTTP Referer 头传输给第三方，且可能显示在用户浏览器屏幕上 |
| **自定义请求头** | 提供额外防御（浏览器通常不允许跨域发送自定义头），但限制应用程序只能通过 XHR 发出 CSRF 保护的请求，对很多场景可能过于复杂 |
| **Cookie 中传输** | 不应在 Cookie 中传输 CSRF 令牌 |

### 2. 使用 Strict SameSite Cookie 限制

- 理想情况下，默认使用 **Strict** 策略，仅在有充分理由时降级为 **Lax**
- 永远不要使用 `SameSite=None` 禁用 SameSite 限制，除非完全了解安全影响
- 即使所有浏览器最终都采用 "Lax-by-default" 策略，也不适合所有 Cookie，且比 Strict 限制更容易被绕过

### 3. 警惕跨源同站攻击

- 如果可能，将不安全的内容（如用户上传的文件）隔离在与敏感功能或数据**不同的 site** 上
- 测试站点时，彻底审计属于同一 site 的所有可用攻击面，包括所有兄弟域名

### 防御措施总结

```
CSRF 防御层次（纵深防御）

第一层：CSRF 令牌
├── 生成：CSPRNG(时间戳 + 静态密钥)，高熵且不可预测
├── 传输：HTML 表单隐藏字段（POST），放 HTML 文档前部
├── 存储：服务器端会话数据
├── 验证：每个敏感操作，不论方法和 Content-Type
└── 缺失令牌 = 无效令牌 = 拒绝请求

第二层：SameSite Cookie
├── 默认 Strict，有需要才降级 Lax
├── 绝不使用 None（除非完全了解风险）
└── 注意：SameSite 不能防御同站跨源攻击

第三层：架构层面
├── 不安全内容隔离到独立 site
├── 审计所有同站子域的攻击面
└── 注意 WebSocket 的 CSWSH 风险
```
