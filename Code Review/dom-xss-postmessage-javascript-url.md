# DOM XSS via postMessage + javascript: 协议绕过

> 案例来源：PortSwigger Web Security Academy — "DOM XSS using web messages and a JavaScript URL"
> 与 `dom-xss-postmessage.md` 的区别：该案例 sink 是 `innerHTML`；本案 sink 是 `location.href`，清洗为弱子串匹配，可被 `javascript:` 协议绕过。

## 审计源码

```javascript
window.addEventListener('message', function(e) {
    var url = e.data;
    if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {
        location.href = url;
    }
}, false);
```

```javascript
// labHeader.js — WebSocket + innerHTML
newWebSocket.onmessage = function (evt) {
    const labSolved = document.getElementById('notification-labsolved');
    const keepAliveMsg = evt.data === 'PONG';
    if (labSolved || keepAliveMsg) {
        return;
    }
    document.getElementById("academyLabHeader").innerHTML = evt.data;
    animateLabHeader();
};
```

---

## 漏洞等级：高危（无需用户交互，任意域触发）

---

## 一、漏洞代码：postMessage 无 origin 校验 + 弱协议检查

```javascript
window.addEventListener('message', function(e) {
    var url = e.data;
    if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {
        location.href = url;
    }
}, false);
```

### 1.1 Source → Sink 路径

```
Source: e.data（postMessage 的消息内容，攻击者可控）
   ↓     无 e.origin 校验        ← 任意域都可以发消息
   ↓     无 typeof 校验           ← 不验证数据类型
   ↓     indexOf('http:') 检查    ← 只要求包含子串，不校验协议前缀
   ↓
Sink: location.href = url         ← 接受 javascript: 协议，在当前域执行 JS
```

### 1.2 为什么 indexOf 检查无效

代码的逻辑是：URL 必须包含 `http:` 或 `https:` 才允许跳转。但这只检查**是否包含**，不检查**是否以此开头**。

```javascript
// 开发者以为的检查逻辑（实际并非如此）：
url.startsWith('http:') || url.startsWith('https:')

// 实际的检查逻辑（indexOf，仅需包含即可）：
url.indexOf('http:') > -1 || url.indexOf('https:') > -1
```

绕过方式：把 `http:` 作为注释或参数嵌入 `javascript:` URL 中：

```javascript
// 以下全部通过 indexOf 检查，但都是 javascript: 协议
"javascript:alert(document.cookie)//http:"
"javascript:alert(1)//https:"
"javascript:print()/*http:*/"
```

`location.href` 赋值给 `javascript:` URL 时，浏览器会在当前页面域下执行协议后面的 JavaScript 代码。

### 1.3 攻击链

1. 攻击者在 `attacker.com` 嵌入指向 `victim.com` 的 iframe
2. iframe 加载后，通过 `postMessage` 发送 payload：
   ```javascript
   targetWindow.postMessage('javascript:alert(document.cookie)//http:', '*')
   ```
3. victim.com 的 message 监听器收到消息
4. `indexOf('http:')` 检查通过（payload 中 `//http:` 是 URL 注释，`http:` 作为注释内容出现在字符串中）
5. `location.href = url` → 浏览器在当前域执行 `javascript:` URL
6. `alert(document.cookie)` 执行，攻击达成

---

## 二、辅助漏洞：WebSocket 消息写入 innerHTML

同一个页面中 `labHeader.js` 的另一段代码：

```javascript
newWebSocket.onmessage = function (evt) {
    const labSolved = document.getElementById('notification-labsolved');
    const keepAliveMsg = evt.data === 'PONG';    // 仅过滤心跳包
    if (labSolved || keepAliveMsg) {
        return;
    }
    document.getElementById("academyLabHeader")
        .innerHTML = evt.data;                   // 直接写入 HTML
    // ...
};
```

**Source → Sink：**

```
Source: evt.data（WebSocket 服务端推送）
   ↓     'PONG' 过滤仅用于排除心跳包，不是安全措施
   ↓     无任何 HTML 转义或清洗
   ↓
Sink: element.innerHTML = evt.data
```

**利用前提**：需要控制 WebSocket 服务端，或在未加密的 `ws://` 连接上进行中间人攻击。实际利用门槛较高，但作为防护纵深问题值得记录。

**与漏洞一的对比：**

| | 漏洞 1 (postMessage → location.href) | 漏洞 2 (WebSocket → innerHTML) |
|---|---|---|
| Source | `e.data`（postMessage） | `evt.data`（WebSocket） |
| Sink | `location.href` | `innerHTML` |
| 攻击者控制难度 | 极低（iframe + postMessage） | 较高（需控制/劫持 WebSocket） |
| Origin 校验 | 无 | N/A（WebSocket 同源在连接阶段） |
| 绕过的是 | 弱协议子串检查 | 无任何清洗 |

---

## 三、其他可疑点

### 3.1 WebSocket 协议转换 bug

```javascript
let newWebSocket = new WebSocket(
    location.origin.replace("http", "ws") + "/academyLabHeader"
);
```

`String.replace()` 只替换**第一个**匹配项。在 HTTPS 页面上：

```javascript
"https://example.com".replace("http", "ws")
// → "wsss://example.com"  ← 协议错误，WebSocket 连接可能失败
```

这不是安全问题，但在 HTTPS 部署时可能导致 WebSocket 功能异常。

### 3.2 `setInterval` 无清理

```javascript
setInterval(() => {
    newWebSocket.send("PING");
}, 5000)
```

定时器没有保存引用，页面卸载后也无法 `clearInterval`。不会导致安全问题，但长时间运行可能造成资源浪费。

---

## 四、修复方案

### 4.1 漏洞 1：postMessage 修复

```javascript
window.addEventListener('message', function(e) {
    // 1. 校验来源 — 只接受可信域
    if (e.origin !== window.location.origin) {
        return;
    }

    // 2. 校验类型
    if (typeof e.data !== 'string') {
        return;
    }

    // 3. 白名单协议 — startsWith 而非 indexOf
    var url = e.data;
    if (url.startsWith('http:') || url.startsWith('https:')) {
        location.href = url;
    }
    // 更彻底的做法：完全不用 postMessage 传 URL
}, false);
```

**修复要点：**

| 措施 | 防御什么 |
|------|---------|
| `e.origin` 校验 | 防止任意域发送消息 |
| `typeof` 检查 | 防止对象类型注入 |
| `startsWith` 替代 `indexOf` | 防止 `javascript:...//http:` 绕过 |
| 不用 postMessage 传 URL | 最根本的修复，降低攻击面 |

### 4.2 漏洞 2：WebSocket 修复

```javascript
newWebSocket.onmessage = function (evt) {
    const labSolved = document.getElementById('notification-labsolved');
    const keepAliveMsg = evt.data === 'PONG';
    if (labSolved || keepAliveMsg) {
        return;
    }

    // 如果确实需要渲染 HTML，用 DOMPurify 清洗
    const header = document.getElementById("academyLabHeader");
    header.innerHTML = DOMPurify.sanitize(evt.data);

    // 或者如果只需要文本
    // header.textContent = evt.data;

    animateLabHeader();
};
```

### 4.3 纵深防御：Content Security Policy

```
Content-Security-Policy: script-src 'self'
```

禁止内联事件处理器执行，可作为最后一道防线。但注意这会影响站点自身的内联脚本。

---

## 五、关联知识

- **CWE-79**: Cross-site Scripting (XSS)
- **OWASP Top 10 (2021)**: A03 Injection
- **PortSwigger 相关 Lab**: "DOM XSS using web messages"、"DOM XSS using web messages and `JSON.parse`"
- **postMessage 安全**: MDN — 始终校验 `e.origin`，始终校验 `e.data` 结构
- **同类文件**: [[dom-xss-postmessage]] — `innerHTML` 为 sink 的变体
