# DOM-based Cookie Manipulation via window.location

> 案例来源：PortSwigger Web Security Academy — "DOM-based cookie manipulation"
> 利用目标：注入恶意 cookie，使其在另一个页面触发 XSS，调用 `print()`

## 审计源码

```html
<script>
    document.cookie = 'lastViewedProduct=' + window.location + '; SameSite=None; Secure'
</script>
```

> `window.location` 被转为字符串时是完整 URL，例：`https://victim.com/product?productId=2`

---

## 漏洞等级：高危（Stored XSS via Cookie，跨页面触发）

---

## 一、漏洞结论

`window.location`（完整 URL，包括攻击者可控的查询参数）直接拼入 cookie 值，无任何清洗。另一页面读取此 cookie 后不安全地写入 DOM，导致存储型 XSS。

---

## 二、Source → Sink 路径

```
[第一页面 — product] 源码可确认

Source: window.location
        → 完整 URL，攻击者通过发钓鱼链接完全控制
    ↓     无任何清洗，直接拼入字符串
Sink:   document.cookie = 'lastViewedProduct=' + window.location
        → cookie 值 = 完整 URL（含恶意 XSS payload）

        ═══════════════════════════════════════

[第二页面 — 首页] 源码中未找到相关代码

首页 HTML 已查看，页面中仅引用了外部脚本 `labHeader.js`（实验框架通用组件），没有任何内联 JS 读取或渲染 `lastViewedProduct` cookie。

渲染"最近浏览产品"的逻辑推测在某个外部 JS 文件中（未提供）。首页的**具体 Sink 代码不可见**，只能根据实验目标推断：cookie 值被不安全地写入了 DOM。

```

**这不是单页面的漏洞**，而是一个两阶段的攻击链：product 页面负责"存储"恶意数据到 cookie，首页负责"引爆"。我们只能审计 product 页面的代码——它把不可信数据写入 cookie 是整个攻击链的起点。首页具体的 cookie 读取和渲染方式未知。

---

### 2.2 开发者意图（推测）

这是一个"最近浏览产品"功能。开发者的思路很直接：

```
用户浏览 /product?productId=2
         ↓
存 cookie: lastViewedProduct = /product?productId=2
         ↓
首页读取 cookie → 拼 <a> 链接展示 "View last viewed product"
```

存完整 URL 的原因很简单：`window.location` 拿到的就是完整 URL，直接塞进 cookie，首页读出来直接拼进 `<a href>`，**全程不需要任何解析、拼接、转换**——最省事的写法。

首页代码推测：

```javascript
var lastUrl = getCookie('lastViewedProduct');
if (lastUrl) {
    document.write('<a href="' + lastUrl + '">View last viewed product</a>');
}
```

**误区**：开发者以为 cookie 里存的永远是之前自己写进去的干净 URL（`/product?productId=2`），没想过 `window.location` 的查询参数是攻击者可以在钓鱼链接里随便改的。根本上，他**信任了 cookie 里的数据**。

---

## 三、逐行拆解

### 3.1 `window.location` — 攻击者完全可控

```
https://victim.com/product?productId=2&'><script>print()</script>
                                                    ↑
                                         攻击者构造的 XSS payload
```

`window.location` 被隐式转为字符串时等于 `location.href`，包含完整的路径、查询参数和 hash。攻击者只需把 payload 放在查询字符串中发链接给受害者。

### 3.2 `document.cookie` — 存储恶意数据

```javascript
document.cookie = 'lastViewedProduct=' + window.location + '; SameSite=None; Secure'
```

**`SameSite=None`**：浏览器在任何跨站请求中都会发送此 cookie，不受同源策略限制。

**`Secure`**：仅 HTTPS 传输。但目标站本身就是 HTTPS 的，不构成障碍。

**关键事实**：`document.cookie` 设置的是原始值。如果 URL 中包含 `<script>print()</script>`，cookie 中存的也就是这个字符串。当第二页面取出并渲染到 DOM 时，XSS 触发。

### 3.3 `&'>` 是什么？—— payload 拆解

`'>` 跟 URL 无关，它是 HTML 层面的"破壳"。假设首页把 cookie 值塞进某个标签属性中：

```html
<a href="上次浏览的URL">最近浏览</a>
```

cookie 值填进去后：

```html
<a href="https://victim.com/product?productId=1&'><script>print()</script>">最近浏览</a>
```

逐字符解析：

| 字符 | 浏览器理解 |
|------|-----------|
| `&` | URL 参数分隔符，正常 |
| `'` | **提前闭合** `href="..."` 的属性值 |
| `>` | **闭合** `<a>` 标签 |
| `<script>print()</script>` | 独立的新 script 元素 → 执行 |

**为什么 `<script>` 能执行？** HTML5 规定 `innerHTML` 不执行 `<script>` 标签，但这个实验的首页用的是 `document.write()`——它会执行 `<script>`。这说明 Sink 不是 `innerHTML`。

### 3.4 第二页面的角色

官方解答中只描述了首页的行为："the home page uses a client-side cookie called `lastViewedProduct`, whose value is the URL of the last product page that the user visited."

**首页源码未提供**，但从实验目标（"cause XSS on a different page"）可以推断：首页读取 `lastViewedProduct` cookie 后，将其值不安全地渲染到了 DOM 中（如 `innerHTML` 或 `document.write`）。具体实现方式未知，以下分析仅基于可确认的 product 页面代码。

cookie 值一旦被当作 HTML 写入页面，`<script>` 标签不执行（HTML5 规范），但 `<img src=x onerror=print()>` 会触发。

---

## 四、攻击链（来自官方解答）

官方 exploitserver 中使用的 payload：

```html
<iframe src="https://victim.com/product?productId=1&'><script>print()</script>"
    onload="if(!window.x)this.src='https://victim.com';window.x=1;">
</iframe>
```

步骤：

1. iframe 首次加载 product 页面的恶意 URL
2. product 页执行 `document.cookie = 'lastViewedProduct=' + window.location`，将含 XSS payload 的完整 URL 存入 cookie
3. iframe onload 触发 → `this.src` 改为首页 URL（victim.com）
4. 首页读取 `lastViewedProduct` cookie 并渲染到 DOM → `print()` 执行

**`window.x` 的作用**：防止死循环。iframe 跳转到首页后再次触发 onload，此时 `window.x` 已为 `true`，不再跳转。

---

## 五、修复方案

### 5.1 根本修复：不存完整 URL

```javascript
// 只存产品 ID，不存完整 URL
var productId = new URLSearchParams(window.location.search).get('productId');
document.cookie = 'lastViewedProduct=' + encodeURIComponent(productId) + '; SameSite=Strict; Secure';
```

**为什么更好**：产品 ID 是纯数字，天然不含 HTML/JS 字符，从源头消除注入可能。同时把 `SameSite` 改为 `Strict`，减少 CSRF 攻击面。

### 5.2 防御修复：编码 cookie 值

如果必须存 URL 类数据：

```javascript
document.cookie = 'lastViewedProduct=' + encodeURIComponent(window.location.href) + '; SameSite=Strict; Secure';
```

`encodeURIComponent` 将 `<` `>` `"` 等危险字符转为 `%3C` `%3E` `%22`，即使被写入 DOM 也不会被解析为 HTML。

### 5.3 防御修复：安全读取 cookie

在读取 cookie 的页面中：

```javascript
// 不要这样
element.innerHTML = getCookie('lastViewedProduct');

// 改为
element.textContent = getCookie('lastViewedProduct');
```

### 5.4 纵深防御：SameSite 属性

```
SameSite=Strict  → 跨站请求完全不发送 cookie
SameSite=Lax     → 跨站 GET 导航发送，POST 不发送（浏览器默认）
SameSite=None    → 所有跨站请求都发送（需要配合 Secure）
```

原代码用了 `SameSite=None`——最宽松的选项。没有理由让"最近浏览产品"这个 cookie 跨站发送，改为 `SameSite=Strict` 既不影响功能，又增加了防御层。

---

## 六、关联知识

- **CWE-79**: Cross-site Scripting
- **CWE-565**: Reliance on Cookies without Validation（cookie 数据被当作可信输入）
- **SameSite Cookie 属性**：Chrome 80+ 默认 `SameSite=Lax`，若需跨站发送必须显式声明 `SameSite=None; Secure`
- **同类模式**：任何"将用户输入存入 cookie → 另一页面读取并渲染"的流程都可能是此漏洞的变体
