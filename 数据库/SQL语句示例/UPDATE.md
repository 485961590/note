# UPDATE 更新语句

> 沿用学生选课管理系统的表结构（参见 INSERT.md）。

---

## 1. 更新单列

```sql
-- 将张三的手机号改为新号码
UPDATE students
SET phone = '13811111111'
WHERE name = '张三';
```

## 2. 更新多列

```sql
-- 同时修改姓名和手机号
UPDATE students
SET name = '张三丰', phone = '13800000000'
WHERE id = 1;
```

## 3. 基于表达式更新

```sql
-- 给所有选课记录加 5 分平时分
UPDATE enrollments
SET score = score + 5
WHERE course_id = 1;

-- 但不超过 100 分
UPDATE enrollments
SET score = LEAST(score + 5, 100)
WHERE course_id = 1;
```

## 4. 基于子查询更新

```sql
-- 将选了"高等数学"且成绩低于 60 的学生成绩设为 60
UPDATE enrollments
SET score = 60
WHERE course_id = (SELECT id FROM courses WHERE name = '高等数学')
  AND score < 60;
```

## 5. 从另一张表获取值更新（MySQL 多表 UPDATE）

```sql
-- 将每个学生的最新手机号从 phone_changes 临时表同步过来
UPDATE students s
INNER JOIN phone_changes pc ON s.id = pc.student_id
SET s.phone = pc.new_phone;
```

## 6. 条件更新（CASE WHEN）

```sql
-- 不同课程设置不同的及格线
UPDATE enrollments
SET score = CASE
    WHEN course_id = 1 AND score < 60 THEN 60   -- 课程1：60分及格
    WHEN course_id = 2 AND score < 50 THEN 50   -- 课程2：50分及格
    WHEN course_id = 3 AND score < 55 THEN 55   -- 课程3：55分及格
    ELSE score
END;
```

## 7. 使用 LIMIT 限制更新行数

```sql
-- 只把最早注册的 5 个学生的电话前缀改成 199
UPDATE students
SET phone = CONCAT('199', SUBSTRING(phone, 4))
ORDER BY created_at ASC
LIMIT 5;
```

## 8. 更新并返回被修改的行（MySQL / PostgreSQL）

```sql
-- PostgreSQL: RETURNING 子句
UPDATE students
SET phone = '13000000000'
WHERE id = 2
RETURNING id, name, phone;

-- MySQL: 更新后查询
UPDATE students SET phone = '13000000000' WHERE id = 2;
SELECT id, name, phone FROM students WHERE id = 2;
```

## 9. 安全更新：先 SELECT 验证再 UPDATE

```sql
-- 步骤1：确认要修改的数据
SELECT id, name, phone FROM students WHERE name LIKE '张%';

-- 步骤2：确认无误后执行更新
UPDATE students
SET phone = REPLACE(phone, '138', '139')
WHERE name LIKE '张%';
```

## 10. UPDATE ... JOIN 多表关联更新

```sql
-- 设置未选课学生的电话为空（标记为不活跃）
UPDATE students s
LEFT JOIN enrollments e ON s.id = e.student_id
SET s.phone = NULL
WHERE e.id IS NULL;
```

---

## 注意事项

- **永远先写 WHERE 条件再写 SET**，防止忘记条件导致全表更新。
- **如果 MySQL 开启了 safe-updates 模式**（`sql_safe_updates = 1`），不带 WHERE 或 WHERE 没用索引的 UPDATE/DELETE 会被拒绝。
- **建议先在事务中执行**，确认结果后再 COMMIT：

```sql
START TRANSACTION;
UPDATE students SET phone = '13899999999' WHERE id = 10;
SELECT * FROM students WHERE id = 10;  -- 检查
-- ROLLBACK;   -- 错了就回滚
COMMIT;       -- 对了就提交
```

---

## 场景练习

| 场景 | 自己写 |
|------|--------|
| 将所有女学生的选课成绩加 3 分，不超过 100 | |
| 将教师 "刘老师" 的所有课程学分统一改为 3.5 | |
| 把最早注册的 3 个学生的出生日期统一改为 2000-01-01 | |
