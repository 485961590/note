# INSERT 插入语句

> 场景：学生选课管理系统。以下所有示例共享同一套表结构。

## 表结构

```sql
-- 学生表
CREATE TABLE students (
    id         INT PRIMARY KEY AUTO_INCREMENT,
    name       VARCHAR(50)  NOT NULL,
    gender     CHAR(1)      DEFAULT 'M',
    birthdate  DATE,
    phone      VARCHAR(20),
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- 课程表
CREATE TABLE courses (
    id       INT PRIMARY KEY AUTO_INCREMENT,
    name     VARCHAR(100) NOT NULL,
    credit   DECIMAL(2,1) NOT NULL,
    teacher  VARCHAR(50)
);

-- 选课记录表
CREATE TABLE enrollments (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    student_id  INT NOT NULL,
    course_id   INT NOT NULL,
    score       DECIMAL(4,1),
    enrolled_at DATE,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id)  REFERENCES courses(id)
);
```

---

## 1. 插入单行（完整字段）

```sql
INSERT INTO students (name, gender, birthdate, phone)
VALUES ('张三', 'M', '2001-05-20', '13800138001');
```

## 2. 插入单行（省略有默认值的字段）

```sql
-- gender 默认为 'M'，created_at 有自动默认值，无需指定
INSERT INTO students (name, birthdate, phone)
VALUES ('李四', '2002-08-15', '13900139002');
```

## 3. 插入多行

```sql
INSERT INTO students (name, gender, birthdate, phone) VALUES
    ('王五', 'M', '2000-11-03', '13700137003'),
    ('赵六', 'F', '2001-03-22', '13600136004'),
    ('孙七', 'F', '2002-07-19', '13500135005');
```

## 4. 插入时使用 DEFAULT 关键字

```sql
INSERT INTO students (name, gender, birthdate, phone, created_at)
VALUES ('周八', DEFAULT, '2003-01-10', '13400134006', DEFAULT);
```

## 5. INSERT ... SET（MySQL 特有语法）

```sql
INSERT INTO students
SET name = '吴九', gender = 'F', birthdate = '2001-12-30', phone = '13300133007';
```

## 6. 从另一个表复制数据（INSERT ... SELECT）

```sql
-- 将上学期优秀学生复制到当前学期学生表中（假设有 old_students 表）
INSERT INTO students (name, gender, birthdate, phone)
SELECT name, gender, birthdate, phone
FROM old_students
WHERE score >= 90;
```

## 7. 插入查询结果并附带固定值

```sql
-- 为一门新课程批量添加选课记录
INSERT INTO enrollments (student_id, course_id, enrolled_at)
SELECT id, 5, CURDATE()
FROM students
WHERE id BETWEEN 1 AND 10;
```

## 8. ON DUPLICATE KEY UPDATE（MySQL 插入或更新）

```sql
-- 如果 id=1 存在则更新 phone，否则插入
INSERT INTO students (id, name, phone)
VALUES (1, '张三', '13800000000')
ON DUPLICATE KEY UPDATE phone = VALUES(phone);
```

## 9. INSERT IGNORE（忽略重复/错误）

```sql
-- 如果主键冲突，静默跳过不报错
INSERT IGNORE INTO courses (id, name, credit, teacher)
VALUES (1, '高等数学', 4.0, '刘老师');
```

## 10. 插入子查询结果（标量子查询）

```sql
INSERT INTO courses (name, credit, teacher) VALUES
    ('线性代数', 3.0, (SELECT name FROM students WHERE id = 1)),
    ('概率论',   2.5, '陈老师');
```

---

## 场景练习

| 场景 | 自己写 |
|------|--------|
| 为自己插入一条学生记录 | |
| 一次性插入 3 门新课程 | |
| 将某班级全部学生批量选入同一门课 | |
