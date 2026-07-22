# SET 语句与变量

> SET 在不同场景下有不同用途：设置会话变量、用户变量、以及在 INSERT/UPDATE 中的特殊语法（MySQL）。

---

## 1. 设置会话 / 全局系统变量

```sql
-- 查看当前时区
SELECT @@time_zone;

-- 设置当前会话的时区
SET time_zone = '+08:00';

-- 设置自动提交开关（会话级别）
SET autocommit = 0;    -- 关闭，需手动 COMMIT
SET autocommit = 1;    -- 开启，每条语句自动提交

-- 设置全局变量（需要权限）
SET GLOBAL max_connections = 200;

-- 查看所有会话变量
SHOW SESSION VARIABLES LIKE '%timeout%';
```

## 2. SQL 模式设置

```sql
-- 查看当前 SQL 模式
SELECT @@sql_mode;

-- 设置严格模式
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';

-- 宽松模式（允许在非空列插入 NULL 时自动用默认值）
SET sql_mode = '';
```

## 3. 用户自定义变量（MySQL 特有）

```sql
-- 定义变量并赋值
SET @student_name = '张三';
SET @min_score = 60;
SET @course_id = 1;

-- 在查询中使用变量
SELECT * FROM students WHERE name = @student_name;
SELECT * FROM enrollments WHERE score >= @min_score AND course_id = @course_id;

-- 查询结果存入变量
SELECT id INTO @target_id FROM students WHERE name = '张三';
SELECT phone INTO @target_phone FROM students WHERE id = @target_id;

-- 使用变量进行计算
SET @total = 0;
SET @total = @total + 100;
SELECT @total;
```

## 4. 查询中的变量赋值与累加

```sql
-- 生成行号
SET @row_num = 0;
SELECT
    @row_num := @row_num + 1 AS 行号,
    name,
    birthdate
FROM students
ORDER BY birthdate;
```

## 5. INSERT ... SET（MySQL 语法）

```sql
-- 等价于 INSERT INTO ... VALUES (...)
INSERT INTO courses
SET name   = '数据结构',
    credit = 3.5,
    teacher = '王老师';
```

## 6. 事务隔离级别

```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;    -- MySQL 8.0+
SELECT @@tx_isolation;             -- MySQL 5.7

-- 设置当前会话的隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

## 7. 字符集与校对规则

```sql
-- 查看字符集
SHOW VARIABLES LIKE 'character_set%';

-- 设置客户端字符集
SET NAMES utf8mb4;

-- 等价于
SET character_set_client     = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results    = utf8mb4;
```

## 8. 安全更新模式（MySQL）

```sql
-- 开启：禁止不带 WHERE 或用不上索引的 UPDATE / DELETE
SET sql_safe_updates = 1;

-- 关闭（默认）
SET sql_safe_updates = 0;
```

---

## 常用系统变量速查

| 变量 | 说明 |
|------|------|
| `autocommit` | 是否自动提交（1=是 0=否） |
| `sql_mode` | SQL 模式（严格/宽松等） |
| `max_connections` | 最大连接数（全局） |
| `wait_timeout` | 非交互连接超时秒数 |
| `interactive_timeout` | 交互连接超时秒数 |
| `character_set_client` | 客户端字符集 |
| `time_zone` | 时区 |
| `transaction_isolation` | 事务隔离级别 |
| `sql_safe_updates` | 安全更新模式开关 |

---

## 场景练习

| 场景 | 自己写 |
|------|--------|
| 设置时区为北京时间，并查询验证 | |
| 用变量查出分数最高的学生姓名 | |
| 关闭自动提交，插入一条数据，查看后回滚 | |
| 设置严格模式后，尝试向 NOT NULL 列插入 NULL 观察报错 | |
