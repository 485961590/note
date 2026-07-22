# DDL — CREATE / ALTER / DROP

> DDL（Data Definition Language）：定义和管理数据库对象结构。

---

## 一、CREATE

### 1. 创建数据库

```sql
-- 基本创建
CREATE DATABASE school;

-- 指定字符集和校对规则
CREATE DATABASE school
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 不存在才创建（避免报错）
CREATE DATABASE IF NOT EXISTS school;
```

### 2. 创建表

```sql
-- 基本建表
CREATE TABLE students (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    name       VARCHAR(50)  NOT NULL,
    gender     CHAR(1)      DEFAULT 'M',
    birthdate  DATE,
    phone      VARCHAR(20)  UNIQUE,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 带约束的建表
CREATE TABLE enrollments (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    student_id  INT NOT NULL,
    course_id   INT NOT NULL,
    score       DECIMAL(4,1) CHECK (score >= 0 AND score <= 100),
    enrolled_at DATE DEFAULT (CURRENT_DATE),
    -- 外键约束
    CONSTRAINT fk_student FOREIGN KEY (student_id) REFERENCES students(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_course  FOREIGN KEY (course_id)  REFERENCES courses(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    -- 唯一约束
    CONSTRAINT uk_enrollment UNIQUE (student_id, course_id)
);

-- 从查询结果建表
CREATE TABLE top_students AS
SELECT s.*
FROM students s
INNER JOIN enrollments e ON s.id = e.student_id
WHERE e.score >= 90;
```

### 3. 创建索引

```sql
-- 普通索引
CREATE INDEX idx_student_name ON students(name);

-- 唯一索引
CREATE UNIQUE INDEX idx_phone ON students(phone);

-- 复合索引（多列）
CREATE INDEX idx_enrollment ON enrollments(student_id, course_id);

-- 前缀索引（只索引字符串前 N 个字符）
CREATE INDEX idx_name_prefix ON students(name(10));
```

### 4. 创建视图

```sql
-- 创建视图：学生成绩总览
CREATE VIEW v_student_scores AS
SELECT
    s.id,
    s.name AS 学生,
    c.name AS 课程,
    e.score AS 成绩,
    t.name AS 教师
FROM enrollments e
INNER JOIN students s ON e.student_id = s.id
INNER JOIN courses  c ON e.course_id  = c.id
INNER JOIN teachers t ON c.teacher_id = t.id;

-- 使用视图
SELECT * FROM v_student_scores WHERE 成绩 >= 80;

-- 可更新视图的规则：单表、无聚合、无 DISTINCT、无 GROUP BY 等
-- 满足条件时可通过视图更新基表
UPDATE v_student_scores SET 成绩 = 95 WHERE id = 1 AND 课程 = '高等数学';
```

### 5. 创建存储过程

```sql
-- 无参数
DELIMITER //
CREATE PROCEDURE sp_list_students()
BEGIN
    SELECT * FROM students ORDER BY name;
END //
DELIMITER ;

-- 带输入参数
DELIMITER //
CREATE PROCEDURE sp_student_courses(IN p_student_id INT)
BEGIN
    SELECT c.name, e.score
    FROM enrollments e
    INNER JOIN courses c ON e.course_id = c.id
    WHERE e.student_id = p_student_id;
END //
DELIMITER ;

-- 带输出参数
DELIMITER //
CREATE PROCEDURE sp_avg_score(IN p_course_id INT, OUT p_avg DECIMAL(5,2))
BEGIN
    SELECT AVG(score) INTO p_avg
    FROM enrollments
    WHERE course_id = p_course_id;
END //
DELIMITER ;

-- 调用
CALL sp_student_courses(1);

CALL sp_avg_score(1, @avg);
SELECT @avg;
```

### 6. 创建函数

```sql
DELIMITER //
CREATE FUNCTION fn_grade(score DECIMAL(4,1))
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
    DECLARE grade VARCHAR(10);
    IF score >= 90 THEN
        SET grade = '优秀';
    ELSEIF score >= 80 THEN
        SET grade = '良好';
    ELSEIF score >= 60 THEN
        SET grade = '及格';
    ELSE
        SET grade = '不及格';
    END IF;
    RETURN grade;
END //
DELIMITER ;

-- 使用函数
SELECT name, score, fn_grade(score) AS 等级 FROM enrollments;
```

### 7. 创建触发器

```sql
-- 插入选课记录前自动设置 enrolled_at 为当天
DELIMITER //
CREATE TRIGGER trg_enrollments_before_insert
BEFORE INSERT ON enrollments
FOR EACH ROW
BEGIN
    IF NEW.enrolled_at IS NULL THEN
        SET NEW.enrolled_at = CURDATE();
    END IF;
END //
DELIMITER ;

-- 记录删除日志
DELIMITER //
CREATE TRIGGER trg_students_after_delete
AFTER DELETE ON students
FOR EACH ROW
BEGIN
    INSERT INTO delete_log (table_name, record_id, deleted_at)
    VALUES ('students', OLD.id, NOW());
END //
DELIMITER ;
```

---

## 二、ALTER

### 1. 修改表结构

```sql
-- 添加列
ALTER TABLE students ADD COLUMN email VARCHAR(100);

-- 添加列到指定位置
ALTER TABLE students ADD COLUMN nickname VARCHAR(50) AFTER name;

-- 删除列
ALTER TABLE students DROP COLUMN nickname;

-- 修改列定义
ALTER TABLE students MODIFY COLUMN phone VARCHAR(30);

-- 重命名列（MySQL 8.0+）
ALTER TABLE students RENAME COLUMN phone TO mobile;

-- 重命名表
ALTER TABLE students RENAME TO student_info;
```

### 2. 添加 / 删除约束

```sql
-- 添加主键
ALTER TABLE students ADD PRIMARY KEY (id);

-- 添加外键
ALTER TABLE enrollments
ADD CONSTRAINT fk_student FOREIGN KEY (student_id)
REFERENCES students(id) ON DELETE CASCADE;

-- 删除外键
ALTER TABLE enrollments DROP FOREIGN KEY fk_student;

-- 添加唯一约束
ALTER TABLE students ADD CONSTRAINT uk_email UNIQUE (email);

-- 删除唯一约束（即删除索引）
ALTER TABLE students DROP INDEX uk_email;

-- 添加 CHECK 约束
ALTER TABLE enrollments ADD CONSTRAINT chk_score
CHECK (score >= 0 AND score <= 100);
```

### 3. 修改索引

```sql
-- 添加索引
ALTER TABLE students ADD INDEX idx_birthdate (birthdate);

-- 删除索引
ALTER TABLE students DROP INDEX idx_birthdate;

-- 重建索引（优化碎片）
ALTER TABLE students ENGINE=InnoDB;
```

---

## 三、DROP

```sql
-- 删除表
DROP TABLE IF EXISTS temp_students;

-- 删除数据库
DROP DATABASE IF EXISTS test_school;

-- 删除视图
DROP VIEW IF EXISTS v_student_scores;

-- 删除存储过程 / 函数
DROP PROCEDURE IF EXISTS sp_list_students;
DROP FUNCTION IF EXISTS fn_grade;

-- 删除触发器
DROP TRIGGER IF EXISTS trg_enrollments_before_insert;

-- 删除索引
DROP INDEX idx_phone ON students;
```

---

## 约束类型速查

| 约束 | 关键字 | 说明 |
|------|--------|------|
| 主键 | PRIMARY KEY | 唯一 + 非空，每表一个 |
| 外键 | FOREIGN KEY | 引用另一表的主键 |
| 唯一 | UNIQUE | 值不能重复，允许多个 NULL |
| 检查 | CHECK | 自定义条件验证（MySQL 8.0+ 支持） |
| 非空 | NOT NULL | 值不能为 NULL |
| 默认值 | DEFAULT | 插入时不指定则使用默认值 |

---

## 外键级联操作

| 选项 | 说明 |
|------|------|
| CASCADE | 主表删/改，子表跟随删/改 |
| SET NULL | 主表删/改，子表外键置 NULL |
| RESTRICT | 有子表记录则禁止删/改主表（默认） |
| NO ACTION | 同 RESTRICT，但在事务中检查时机不同 |
| SET DEFAULT | 主表删/改，子表外键设默认值 |

---

## 场景练习

| 场景 | 自己写 |
|------|--------|
| 创建一个图书管理数据库，包含 books、readers、borrow_records 三张表 | |
| 创建视图列出每本书被借阅的次数 | |
| 创建触发器：借书时自动记录借阅时间 | |
| 用 ALTER 为表增加一列并加上唯一约束 | |
