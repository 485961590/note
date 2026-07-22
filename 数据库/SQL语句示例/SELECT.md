# SELECT 查询语句

> 沿用学生选课管理系统的表结构（参见 INSERT.md）。

---

## 1. 基本查询

```sql
-- 查询全部列
SELECT * FROM students;

-- 查询指定列
SELECT name, phone FROM students;

-- 去重
SELECT DISTINCT gender FROM students;
```

## 2. 条件过滤（WHERE）

```sql
-- 等值比较
SELECT * FROM students WHERE gender = 'F';

-- 范围查询
SELECT name, birthdate FROM students WHERE birthdate BETWEEN '2001-01-01' AND '2002-12-31';

-- 集合匹配
SELECT * FROM students WHERE id IN (1, 3, 5, 7);

-- 模糊匹配
SELECT * FROM students WHERE name LIKE '张%';      -- 以 "张" 开头
SELECT * FROM students WHERE phone LIKE '%3800%';   -- 包含 "3800"

-- 空值判断
SELECT * FROM students WHERE phone IS NULL;
SELECT * FROM students WHERE phone IS NOT NULL;

-- 多条件组合
SELECT * FROM students
WHERE gender = 'M' AND birthdate >= '2001-01-01';
```

## 3. 排序（ORDER BY）

```sql
-- 升序（默认）
SELECT name, birthdate FROM students ORDER BY birthdate;

-- 降序
SELECT name, birthdate FROM students ORDER BY birthdate DESC;

-- 多列排序
SELECT * FROM students ORDER BY gender ASC, birthdate DESC;
```

## 4. 限制结果（LIMIT / OFFSET）

```sql
-- 前 5 条
SELECT * FROM students LIMIT 5;

-- 跳过前 2 条后取 3 条（分页）
SELECT * FROM students LIMIT 3 OFFSET 2;

-- 等价写法
SELECT * FROM students LIMIT 2, 3;   -- MySQL 写法
```

## 5. 聚合函数

```sql
-- 计数
SELECT COUNT(*) FROM students;
SELECT COUNT(phone) FROM students;          -- 不统计 NULL
SELECT COUNT(DISTINCT gender) FROM students;

-- 求和、平均、最大、最小
SELECT
    SUM(score)      AS 总分,
    AVG(score)      AS 平均分,
    MAX(score)      AS 最高分,
    MIN(score)      AS 最低分
FROM enrollments
WHERE course_id = 1;
```

## 6. 分组（GROUP BY）

```sql
-- 按性别统计人数
SELECT gender, COUNT(*) AS 人数
FROM students
GROUP BY gender;

-- 按课程统计平均分，只显示平均分 >= 60 的
SELECT course_id, AVG(score) AS 平均分
FROM enrollments
GROUP BY course_id
HAVING AVG(score) >= 60;
```

## 7. 内连接（INNER JOIN）

```sql
-- 查询每位学生选了哪些课
SELECT s.name AS 学生, c.name AS 课程, e.score AS 成绩
FROM enrollments e
INNER JOIN students s ON e.student_id = s.id
INNER JOIN courses  c ON e.course_id  = c.id;
```

## 8. 左连接（LEFT JOIN）

```sql
-- 所有学生及其选课情况（包括没选课的学生）
SELECT s.name, c.name AS 课程, e.score
FROM students s
LEFT JOIN enrollments e ON s.id = e.student_id
LEFT JOIN courses    c ON e.course_id = c.id;
```

## 9. 子查询

```sql
-- 子查询在 WHERE 中：查询选了"高等数学"的学生
SELECT name FROM students
WHERE id IN (
    SELECT student_id FROM enrollments
    WHERE course_id = (SELECT id FROM courses WHERE name = '高等数学')
);

-- 子查询在 FROM 中（派生表）
SELECT 课程, 平均分
FROM (
    SELECT c.name AS 课程, AVG(e.score) AS 平均分
    FROM enrollments e
    INNER JOIN courses c ON e.course_id = c.id
    GROUP BY c.name
) AS 课程统计
WHERE 平均分 >= 70;

-- 子查询在 SELECT 中（标量子查询）
SELECT
    name,
    (SELECT COUNT(*) FROM enrollments WHERE student_id = s.id) AS 选课数
FROM students s;
```

## 10. UNION 合并结果

```sql
-- 合并两个查询结果（自动去重）
SELECT name FROM students WHERE gender = 'M'
UNION
SELECT name FROM students WHERE id IN (SELECT student_id FROM enrollments WHERE score >= 90);

-- UNION ALL 不去重
SELECT name FROM students WHERE gender = 'M'
UNION ALL
SELECT name FROM students WHERE gender = 'F';
```

## 11. CASE WHEN 条件表达式

```sql
SELECT
    name,
    score,
    CASE
        WHEN score >= 90 THEN '优秀'
        WHEN score >= 80 THEN '良好'
        WHEN score >= 60 THEN '及格'
        ELSE '不及格'
    END AS 等级
FROM enrollments e
INNER JOIN students s ON e.student_id = s.id;
```

## 12. 窗口函数（MySQL 8.0+）

```sql
-- 排名（按成绩）
SELECT
    s.name,
    c.name AS 课程,
    e.score,
    RANK()       OVER (PARTITION BY e.course_id ORDER BY e.score DESC) AS 排名,
    DENSE_RANK() OVER (PARTITION BY e.course_id ORDER BY e.score DESC) AS 密集排名,
    ROW_NUMBER() OVER (PARTITION BY e.course_id ORDER BY e.score DESC) AS 行号
FROM enrollments e
INNER JOIN students s ON e.student_id = s.id
INNER JOIN courses  c ON e.course_id  = c.id;
```

## 13. 常用日期函数

```sql
SELECT
    name,
    birthdate,
    YEAR(birthdate)          AS 出生年,
    TIMESTAMPDIFF(YEAR, birthdate, CURDATE()) AS 年龄,
    DATE_FORMAT(birthdate, '%Y年%m月%d日')    AS 格式化日期
FROM students;
```

## 14. EXISTS 相关子查询

```sql
-- 查询至少选了一门课的学生
SELECT name FROM students s
WHERE EXISTS (
    SELECT 1 FROM enrollments e WHERE e.student_id = s.id
);

-- 查询一门课都没选的学生
SELECT name FROM students s
WHERE NOT EXISTS (
    SELECT 1 FROM enrollments e WHERE e.student_id = s.id
);
```

---

## 场景练习

| 场景 | 自己写 |
|------|--------|
| 查询 2001 年后出生的女学生姓名和电话 | |
| 统计每位学生的选课数量，按数量降序排列 | |
| 找出平均分最高的课程名称 | |
| 查询同时选了课程 1 和课程 2 的学生 | |
