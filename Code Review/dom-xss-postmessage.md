# DOM-based XSS 漏洞审计

> 案例来源：PortSwigger Web Security Academy — "DOM XSS using web messages"

## 漏洞等级：高危（无需用户交互，任意域触发）

---

## 一、漏洞代码 1：postMessage 无 origin 校验

```javascript
// 目标页面内联脚本 — 只有 3 行
window.addEventListener('message', function(e) {
    document.getElementById('ads').innerHTML = e.data;
})
```

### 1.1 为什么 3 行代码就是完整漏洞

Source → Sink 路径**完全没有中间环节**：

```
Source: e.data（postMessage 的消息内容）
   ↓     ↑ 攻击者在 iframe 中调用 postMessage() 发送任意数据
   ↓     无 e.origin 校验 ← 任意域都可以发
   ↓     无 typeof 校验    ← 字符串、对象都接收
   ↓     无内容过滤/转义   ← HTML 标签原样写入
   ↓
Sink: innerHTML（将字符串解析为 HTML 写入 DOM）
```

### 1.2 逐行解释

#### `window.addEventListener('message', function(e) { ... })`

**`window`** 代表当前浏览器标签页的全局对象。给 `window` 绑定事件意味着：不管消息从哪里来、发给页面中的哪个元素，只要这个标签页收到了 `message` 事件，就执行这段代码。

**`'message'`** 是浏览器内置的跨域通信事件名。跟"手机收到短信"一样，不能自定义——浏览器规定只有 postMessage 发出的才算 message 事件。

**`e`** 是事件对象，包含三个关键属性：

| 属性 | 含义 | 示例 |
|------|------|------|
| `e.data` | 消息内容 | `"<img src=x onerror=alert(1)>"` |
| `e.origin` | 发送方的域名 | `"https://evil.com"` |
| `e.source` | 发送方的 window 引用 | `iframe.contentWindow` |

#### `document.getElementById('ads')`

找到 HTML 中 `id="ads"` 的 DOM 元素。目标页面中是一个空 div：

```html
<div id='ads'></div>
```

#### `.innerHTML = e.data`

`innerHTML` 是 DOM 元素的属性，读取/写入元素内部的 HTML 字符串。关键区别：

```javascript
// 安全：写入纯文本，HTML 标签会被显示为文字，不会执行
element.textContent = '<img src=x onerror=alert(1)>';
// 页面显示：<img src=x onerror=alert(1)>  （纯文本）

// 危险：写入 HTML，浏览器会解析并渲染标签
element.innerHTML = '<img src=x onerror=alert(1)>';
// 页面渲染出 img 标签，onerror 触发 → alert(1) 执行
```

### 1.3 为什么没有 origin 校验是关键

对比安全写法：

```javascript
// 漏洞代码
window.addEventListener('message', function(e) {
    document.getElementById('ads').innerHTML = e.data;
})

// 安全写法
window.addEventListener('message', function(e) {
    // 第 1 步：校验来源 — 只接受可信域名
    if (e.origin !== 'https://my-site.com') return;

    // 第 2 步：校验类型 — 只接受字符串
    if (typeof e.data !== 'string') return;

    // 第 3 步：安全输出 — 用 textContent 替代 innerHTML
    document.getElementById('ads').textContent = e.data;
})
```

**生活类比**：你家门口的邮箱没有锁。任何人（任意域）往里面投信（postMessage），你拿到信之后直接张贴在门口公告栏（innerHTML）。正确的做法是：先看寄件人是谁（origin 校验），确认是认识的人再打开（类型校验），然后只把信的文本内容抄到公告栏上（textContent），而不是把整封信连信封带邮票贴上去。

### 1.4 innerHTML 不执行 `<script>` 标签，但可以触发事件

这是很多初学者困惑的地方：

```javascript
// 这样不会弹窗（HTML5 规范规定 innerHTML 不执行脚本元素）
element.innerHTML = '<script>alert(1)</script>';

// 但这样可以——事件处理器不在规范限制范围内
element.innerHTML = '<img src=x onerror=alert(1)>';
```

**原理**：HTML5 规范说的是"通过 innerHTML 插入的 `<script>` 元素不被标记为 '已经解析器插入'，因此不执行"。但 `<img>` 的 `onerror` 是浏览器资源加载失败后的正常错误处理回调，不属于脚本元素的执行限制。

**可用的触发方式**：

| Payload | 触发条件 | 可靠性 |
|---------|---------|--------|
| `<img src=x onerror=alert(1)>` | 图片加载失败（`src=x` 不存在） | 最高 |
| `<svg onload=alert(1)>` | SVG 渲染完成 | 很高 |
| `<body onload=alert(1)>` | body 加载完成 | 高（与其他 body 冲突可能失败） |
| `<input onfocus=alert(1) autofocus>` | 输入框自动获得焦点 | 高（需要元素可 focus） |
| `<iframe srcdoc="<img src=x onerror=alert(1)>">` | iframe 内容渲染 | 中（有嵌套限制） |

### 1.5 攻击链

```
┌─────────────────────────────────────────────────┐
│ attacker.com（攻击者控制的页面）                   │
│                                                  │
│  <iframe                                          │
│    src="https://victim.com"                       │
│    onload="this.contentWindow.postMessage(        │
│      '<img src=x onerror=print()>',              │
│      '*'                                         │
│    )"                                            │
│  ></iframe>                                      │
│                                                  │
│  1. iframe 加载 victim.com                       │
│  2. victim.com 注册 message 事件监听器             │
│  3. iframe onload 触发                           │
│  4. postMessage 发送恶意 HTML                     │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────┐
│ victim.com（目标页面内）                          │
│                                                 │
│ addEventListener('message', function(e) {       │
│     document.getElementById('ads')              │
│       .innerHTML = e.data;                      │
│     // e.data = '<img src=x onerror=print()>'   │
│ })                                              │
│                                                 │
│ → 浏览器创建 <img> 元素                          │
│ → 尝试加载 src=x（失败）                         │
│ → 触发 onerror → print() 执行                   │
└────────────────────────────────────────────────┘
```

**关键知识点**：`iframe.contentWindow` 即使跨域也可以访问——这是浏览器专门为 `postMessage` 设计的。这是唯一允许跨域访问的窗口属性。`iframe.contentDocument` 跨域时则会被同源策略阻止。

---

## 二、漏洞代码 2：WebSocket + innerHTML

```javascript
// labHeader.js — Lab 框架的通用组件
completedListeners = [];

(function () {
    let labHeaderWebSocket = undefined;
    function openWebSocket() {
        return new Promise(res => {
            if (labHeaderWebSocket) {
                res(labHeaderWebSocket);
                return;
            }

            let newWebSocket = new WebSocket(
                location.origin.replace("http", "ws") + "/academyLabHeader"
            );

            newWebSocket.onopen = function (evt) {
                res(newWebSocket);
            };

            newWebSocket.onmessage = function (evt) {        // Source
                const labSolved = 
                    document.getElementById('notification-labsolved');
                const keepAliveMsg = evt.data === 'PONG';    // 只排除心跳包
                if (labSolved || keepAliveMsg) {
                    return;
                }
                document.getElementById("academyLabHeader")
                    .innerHTML = evt.data;                   // Sink
                animateLabHeader();

                for (const listener of completedListeners) {
                    listener();
                }
            };

            setInterval(() => {
                newWebSocket.send("PING");
            }, 5000)
        });
    }

    labHeaderWebSocket = openWebSocket();
})();
```

### 2.1 Source → Sink 分析

```
Source: evt.data — WebSocket 服务端发来的消息
  ↓
Sanitization: 仅判断是否等于 'PONG'（心跳包过滤），其余全部放行
  ↓
Sink: element.innerHTML = evt.data — 直接写入 DOM
```

### 2.2 为什么利用率低但仍然危险

**利用前提**：
- 需要控制 WebSocket 服务端，或者
- 在 WebSocket 连接上做中间人攻击（MITM）

**但是**：如果攻击者能做到以上两点之一（例如通过 DNS 劫持、代理劫持、或服务端本身被攻破），这个漏洞就能触发。另外 WebSocket 使用的是 `ws://` 协议（不加密），在公共 Wi-Fi 环境下更容易被劫持。

### 2.3 与漏洞 1 的对比

| | 漏洞 1 (postMessage) | 漏洞 2 (WebSocket) |
|---|---|---|
| Source | `e.data`（postMessage） | `evt.data`（WebSocket） |
| 攻击者控制难度 | 极低（iframe + postMessage） | 较高（需控制/劫持 WebSocket） |
| 触发方式 | 攻击者主动发消息 | 被动等待服务端推送 |
| Origin 校验 | 无 | N/A（WebSocket 同源检查在连接时） |
| 修复优先级 | 紧急 | 高 |

---

## 三、为什么 DOM XSS 比 Reflected/Stored XSS 更隐蔽

| | Reflected XSS | Stored XSS | DOM XSS |
|---|---|---|---|
| 恶意数据经过服务端 | 是 | 是 | **否** |
| WAF 可以检测 | 通常可以 | 可以 | **无法检测** |
| 服务端日志有记录 | 有 | N/A（已存储） | **无** |
| 在响应 HTML 中可见 | 是 | 是 | **否（JS 动态生成）** |
| 需要审计代码类型 | 服务端 | 服务端 | **前端 JS** |

DOM XSS 的数据流完全在浏览器端，服务端毫不知情。这也是为什么它经常在渗透测试中被遗漏。

---

## 四、修复方案

### 4.1 漏洞 1：postMessage 修复

```javascript
window.addEventListener('message', function(e) {
    // 1. 校验来源 — 白名单域名
    if (e.origin !== 'https://my-site.com') {
        return;
    }

    // 2. 校验类型 — 只接受字符串
    if (typeof e.data !== 'string') {
        return;
    }

    // 3. 安全输出 — 用 textContent 替代 innerHTML
    document.getElementById('ads').textContent = e.data;
})
```

### 4.2 漏洞 2：WebSocket 修复

```javascript
newWebSocket.onmessage = function (evt) {
    const labSolved = document.getElementById('notification-labsolved');
    const keepAliveMsg = evt.data === 'PONG';
    if (labSolved || keepAliveMsg) {
        return;
    }

    // 安全：创建文本节点而非直接 innerHTML
    const header = document.getElementById("academyLabHeader");
    header.textContent = evt.data;  // 替代 innerHTML

    animateLabHeader();
};
```

### 4.3 纵深防御：Content Security Policy

即使代码忘了修，CSP 可以作为最后一道防线：

```
Content-Security-Policy: script-src 'self'
```

禁止内联事件处理器（如 `onerror`、`onload`）执行。但注意：
- 这会影响站点自身的内联脚本，需要改为外部引入
- 更好的 CSP 策略需要配合 `'nonce-xxx'` 或 `'sha256-xxx'` hash

### 4.4 安全编码原则总结

| 场景 | 安全做法 | 避免 |
|------|---------|------|
| 写入 DOM 内容 | `textContent` | `innerHTML` |
| 收到 postMessage | 校验 origin + 类型检查 | 直接使用 `e.data` |
| WebSocket 消息 | 当作不可信数据处理 | 假设服务端发来的都是安全的 |
| 需要渲染 HTML | 用 DOMPurify 清洗 | 直接 innerHTML |

---

## 五、关联知识

- **CWE-79**: Cross-site Scripting (XSS)
- **OWASP Top 10 (2021)**: A03 Injection（XSS 属于注入类）
- **PortSwigger 相关 Lab**: "DOM XSS using web messages and a JavaScript URL"、"DOM XSS using web messages and `JSON.parse`"
- **innerHTML 规范**: HTML5 标准 §8.4 — Parsing HTML fragments，明确 `<script>` 不执行的原因
- **postMessage 安全**: MDN Web Docs — `Window.postMessage()` 页面中有专门的"Security concerns"一节，强调始终校验 origin
