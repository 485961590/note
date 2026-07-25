# DOM XSS via postMessage + JSON.parse + iframe.src 注入

> 案例来源：PortSwigger Web Security Academy — "DOM XSS using web messages and `JSON.parse`"
> 核心教训：`JSON.parse` 只保证数据是合法 JSON，不校验字段内容，不是安全措施。

## 审计源码

```javascript
window.addEventListener('message', function(e) {
    var iframe = document.createElement('iframe'),
        ACMEplayer = {element: iframe},
        d;
    document.body.appendChild(iframe);

    try {
        d = JSON.parse(e.data);
    } catch(e) {
        return;
    }

    switch(d.type) {
        case "page-load":
            ACMEplayer.element.scrollIntoView();
            break;
        case "load-channel":
            ACMEplayer.element.src = d.url;
            break;
        case "player-height-changed":
            ACMEplayer.element.style.width = d.width + "px";
            ACMEplayer.element.style.height = d.height + "px";
            break;
    }
}, false);
```

---

## 漏洞等级：高危（无需用户交互，任意域触发）

---

## 一、代码行为概述

这段代码模拟一个视频播放器组件。页面通过 `postMessage` 接收外部指令，操作页面上的 iframe：

```javascript
window.addEventListener('message', function(e) {
    var iframe = document.createElement('iframe'),
        ACMEplayer = {element: iframe},
        d;
    document.body.appendChild(iframe);

    try {
        d = JSON.parse(e.data);       // 解析 JSON
    } catch(e) { return; }            // 格式不对就丢弃

    switch(d.type) {
        case "page-load":
            ACMEplayer.element.scrollIntoView();           // 滚动到播放器
            break;
        case "load-channel":
            ACMEplayer.element.src = d.url;                // ← 漏洞点
            break;
        case "player-height-changed":
            ACMEplayer.element.style.width = d.width + "px";   // 调整宽度
            ACMEplayer.element.style.height = d.height + "px"; // 调整高度
            break;
    }
}, false);
```

三种消息类型就像遥控器上的三个按钮：

| type | 行为 | 接收外部数据 | 安全 |
|------|------|-------------|------|
| `"page-load"` | 滚动页面到播放器位置 | 无 | 安全 |
| `"load-channel"` | 设置 iframe 加载地址 | `d.url` | **漏洞** |
| `"player-height-changed"` | 调整播放器尺寸 | `d.width`, `d.height` | 低风险 |

---

## 二、漏洞分析：load-channel 分支

### 2.1 Source → Sink 路径

```
Source: e.data（postMessage，任意域可控）
    ↓
Sanitization: JSON.parse()      ← 仅校验 JSON 语法合法性，不校验字段值
    ↓
switch(d.type)                   ← 路由分发，不限制 d.url 的内容或协议
    ↓
case "load-channel":
    iframe.src = d.url;         ← Sink: 接受任意 URL 协议
```

**`JSON.parse` 不是安全措施。** 它只保证字符串是合法 JSON，不关心字段值是什么。攻击者把恶意负载包进 JSON 就能通过：

```json
{"type": "load-channel", "url": "javascript:alert(document.cookie)"}
```

完全合法的 JSON，完全恶意的内容。

### 2.2 为什么 iframe.src 可以执行 javascript: 协议

浏览器处理 `iframe.src` 的逻辑：
- `src="https://example.com"` → 正常加载网页
- `src="javascript:alert(1)"` → 在当前页面同源的 iframe 上下文中执行 JS

iframe 是由父页面的 `document.createElement` 创建的，与父页面同源。所以 iframe 中的 JS 能通过 `parent.document` 访问父页面 DOM：

```javascript
// 攻击 payload
url: "javascript:parent.document.body.innerHTML='<h1>已入侵</h1>'"
```

### 2.3 漏洞的三个层面

| 层面 | 问题 | 应该怎么做 |
|------|------|-----------|
| origin 校验 | 没有检查 `e.origin` | 只接受可信域的消息 |
| 数据校验 | `JSON.parse` 不校验内容 | 对 `d.url` 做协议和域名白名单 |
| Sink 安全 | `iframe.src` 未限制协议 | 用 `new URL()` 解析后白名单协议 |

---

## 三、其他分支

### 3.1 page-load — 安全

```javascript
case "page-load":
    ACMEplayer.element.scrollIntoView();
    break;
```

不接收任何外部数据，纯浏览器 API 调用，无安全风险。

### 3.2 player-height-changed — 低风险

```javascript
case "player-height-changed":
    ACMEplayer.element.style.width = d.width + "px";
    ACMEplayer.element.style.height = d.height + "px";
    break;
```

`d.width` / `d.height` 拼接到 CSS 值中，理论上存在 CSS 注入可能，但后缀 `"px"` 使注入极为困难——任何注入的 CSS 语法后面都会带上 `px`，导致解析失败。实际利用价值极低。

不过从防御编码角度，仍建议加 `typeof d.width === 'number'` 类型校验。

---

## 四、攻击链

1. 攻击者构造 JSON payload：
   ```json
   {"type": "load-channel", "url": "javascript:parent.document.body.innerHTML='pwned'"}
   ```
2. 通过 `postMessage` 发送给目标页面（iframe 或 `window.open`）
3. 目标页面 message 监听器触发
4. `JSON.parse` 解析成功（合法 JSON，通过）
5. `switch(d.type)` 命中 `"load-channel"`
6. `iframe.src = d.url` → javascript: URL 在 iframe 中执行
7. iframe 与父页面同源，通过 `parent.document` 访问并篡改父页面 DOM

### 4.1 payload 中为什么 JSON 的 `"` 需要 `\"` 转义

实际利用时，payload 写在 HTML 属性中：

```html
<iframe src=https://victim.com/
    onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>
```

`\"` 是给 **JavaScript 引擎** 看的，不是给 HTML 看的。

**问题根源：同一字符 `"` 在两层含义中冲突。**

```
HTML 属性层:  onload=' ... '
                      ↑      ↑
                    单引号界定 HTML 属性值，所以内部可以放心用双引号

JS 字符串层:  postMessage(" ... ", "*")
                          ↑        ↑
                        双引号界定 JS 字符串

JSON 数据层:  {"type":"load-channel","url":"javascript:print()"}
                ↑     ↑              ↑
              这些双引号恰好和 JS 字符串的界定符相同
              → JS 引擎会误把 JSON 的 " 当成字符串结束
              → 必须加反斜杠告诉 JS：这是字面量，不是定界符
```

**如果不转义会怎样：**

```javascript
// 不加转义 — JS 语法错误
postMessage("{"type":"load-channel","url":"javascript:print()"}","*")
//               ↑ JS 认为字符串在这里结束
//               后面的 type 被当成变量名 → 语法报错
```

**加了转义后：**

```javascript
// JS 解析器看到的实际字符串值：
postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")
// 实际传入 postMessage 的字符串 →
// {"type":"load-channel","url":"javascript:print()"}
```

**一句话：** `\"` 只在 JS 字符串解析时生效一次，去掉反斜杠后得到的才是 JSON。目标页面的 `JSON.parse()` 收到的是不带反斜杠的干净 JSON。

---

## 五、修复方案

```javascript
window.addEventListener('message', function(e) {
    // 1. 校验来源
    if (e.origin !== 'https://trusted-site.com') {
        return;
    }

    var iframe = document.createElement('iframe'),
        ACMEplayer = {element: iframe},
        d;
    document.body.appendChild(iframe);

    try {
        d = JSON.parse(e.data);
    } catch(e) {
        return;
    }

    switch(d.type) {
        case "page-load":
            ACMEplayer.element.scrollIntoView();
            break;

        case "load-channel":
            // 2. 白名单: 协议 + 域名
            if (typeof d.url === 'string') {
                try {
                    var parsed = new URL(d.url);
                    if (parsed.protocol === 'https:' &&
                        parsed.hostname === 'trusted-cdn.com') {
                        ACMEplayer.element.src = d.url;
                    }
                } catch(_) {
                    // URL 解析失败，拒绝
                }
            }
            break;

        case "player-height-changed":
            // 3. 数值类型约束
            if (typeof d.width === 'number') {
                ACMEplayer.element.style.width = d.width + "px";
            }
            if (typeof d.height === 'number') {
                ACMEplayer.element.style.height = d.height + "px";
            }
            break;
    }
}, false);
```

| 措施 | 解决什么 |
|------|---------|
| `e.origin` 校验 | 阻止任意域发送消息 |
| `new URL()` 解析 + 协议/域名白名单 | 阻止 `javascript:` / `data:` 等危险协议 |
| `typeof` 类型约束 | 防止非预期类型进入样式属性 |

---

## 六、与同系列 Lab 的对比

| 变体 | Sink | 绕过的是什么 | 文件 |
|------|------|-------------|------|
| 无校验 | `innerHTML` | 无任何清洗 | [[dom-xss-postmessage]] |
| 弱子串匹配 | `location.href` | `url.indexOf('http:')` 可被 `javascript:...//http:` 绕过 | [[dom-xss-postmessage-javascript-url]] |
| JSON.parse | `iframe.src` | 误以为 `JSON.parse` 是安全措施 | 本文 |

**共性根因:** 三个变体全部都缺 `e.origin` 校验——这是 postMessage 漏洞的公共特征。

---

## 七、关联知识

- **CWE-79**: Cross-site Scripting (XSS)
- **OWASP Top 10 (2021)**: A03 Injection
- **PortSwigger**: "Controlling the Web Message Source" 实验系列
- **MDN**: `Window.postMessage()` 安全注意事项 — 始终校验 origin、始终校验消息结构
