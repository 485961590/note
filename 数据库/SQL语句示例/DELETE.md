# DELETE 删除语句

> 沿用学生选课管理系统的表结构（参见 INSERT.md）。

---

## 1. 基础删除：按条件删除行

```sql
-- 删除指定学生
DELETE FROM students WHERE id = 10;

-- 删除所有没有手机号的学生
DELETE FROM students WHERE phone IS NULL;
```

## 2. 基于子查询删除

```sql
-- 删除所有未选课的学生
DELETE FROM students
WHERE id NOT IN (
    SELECT DISTINCT student_id FROM enrollments
);
```

> 注意：MySQL 中 DELETE 的子查询不能直接引用同一张正在删除的表。如果遇到此限制，可将子查询包装一层：
```sql
DELETE FROM students
WHERE id NOT IN (
    SELECT student_id FROM (
        SELECT DISTINCT student_id FROM enrollments
    ) AS tmp
);
```

## 3. 多表删除（MySQL）

```sql
-- 删除学生时同时删除其选课记录
DELETE s, e
FROM students s
LEFT JOIN enrollments e ON s.id = e.student_id
WHERE s.id = 5;

-- 只删除选课记录，保留学生记录
DELETE e
FROM students s
INNER JOIN enrollments e ON s.id = e.student_id
WHERE s.name = '张三';
```

## 4. 基于排序 + 限制行数删除

```sql
-- 删除最早注册的 3 个学生
DELETE FROM students
ORDER BY created_at ASC
LIMIT 3;
```

## 5. 删除重复行（保留最小 ID）

```sql
-- 假设 students 表中有同名同生日的重复记录，保留 id 最小的
DELETE s1
FROM students s1
INNER JOIN students s2
ON s1.name = s2.name AND s1.birthdate = s2.birthdate
WHERE s1.id > s2.id;
```

## 6. 安全删除：事务中执行

```sql
START TRANSACTION;

SELECT COUNT(*) FROM students WHERE phone IS NULL;   -- 先看有多少行被删
DELETE FROM students WHERE phone IS NULL;

-- ROLLBACK;   -- 错了回滚
COMMIT;       -- 对了提交
```

## 7. 软删除（推荐做法）

```sql
-- 表设计时加入 is_deleted 字段
ALTER TABLE students ADD COLUMN is_deleted TINYINT DEFAULT 0;

-- "删除" 时只标记状态，不真删
UPDATE students SET is_deleted = 1 WHERE id = 8;

-- 查询时过滤掉已删除的
SELECT * FROM students WHERE is_deleted = 0;
```

## 8. 清空整张表

```sql
-- DELETE: 逐行删除，触发触发器，可回滚（事务中），自增计数器保留
DELETE FROM temp_logs;

-- TRUNCATE: 直接释放数据页，不触发触发器，不可回滚（多数DB），重置自增计数器
TRUNCATE TABLE temp_logs;
```

---

## DELETE vs TRUNCATE vs DROP

| | DELETE | TRUNCATE | DROP |
|---|---|---|---|
| 删除内容 | 行（可带 WHERE） | 全部行 | 表结构 + 数据 |
| 速度 | 慢（逐行记日志） | 快（释放数据页） | 快 |
| 回滚 | 可（事务内） | 不可（多数 DB） | 不可（多数 DB） |
| 触发器 | 触发 | 不触发 | 不触发 |
| 自增重置 | 否 | 是 | -- |
| WHERE | 支持 | 不支持 | 不支持 |

---

## 注意事项

- **永远先 SELECT 再 DELETE**：用相同 WHERE 条件 SELECT 一遍，确认要删的是你想要的。
- **生产环境尽量用软删除**，数据恢复成本低。
- **外键约束**：如果 enrollments 的外键设置了 `ON DELETE CASCADE`，删学生会自动删选课记录；如果没有，需先删子表再删主表。

---

## 场景练习

| 场景 | 自己写 |
|------|--------|
| 删除 2000 年之前出生的学生 | |
| 删除没有任何选课记录的学生 | |
| 删除选课记录中成绩为 NULL 的行 | |
| 用软删除的方式"删除"学生 id=3 | |
