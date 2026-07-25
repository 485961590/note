# SQL 注入 — MySQL `||` 运算符的双重语义利用

## 审计源码

**index.php (后端 SQL 模板):**

```sql
select $_POST['query'] || flag from Flag;
```

**过滤规则：**

- `extractvalue` 被过滤
- `updatexml` 被过滤
- `union` 被过滤
- `group_concat` 被过滤
- `"` 双引号被过滤
- 所有含 `or` 的字符串被过滤（包括 `from`、`or`、`and`、`order`、`information_schema` 等）

**数据库信息：**

```
Array
(
    [0] => ctf
)
Array
(
    [0] => ctftraining
)
Array
(
    [0] => information_schema
)
Array
(
    [0] => mysql
)
Array
(
    [0] => performance_schema
)
Array
(
    [0] => test
)
```

---

## 审计分析

### 结论

`$_POST['query']` 直接拼入 SQL，无任何清洗，存在 SQL 注入。题目设置了大量关键字过滤（union、extractvalue、updatexml、group_concat、双引号、所有含 `or` 的字符串），但利用 MySQL `||` 运算符在 `sql_mode` 不同设置下的双重语义，配合堆叠查询，可以绕过所有过滤取出 flag。

### Source -> Sink 追踪

```
Source: $_POST['query'] (用户完全可控)
  ↓
Sanitization: 有黑名单过滤（union/extractvalue/updatexml/group_concat/双引号/含or字符串），但黑名单不充分
  ↓
Sink: 直接拼入 SQL 语句执行
  select $_POST['query'] || flag from Flag;
```

黑名单过滤了常规报错注入函数和联合查询，但遗漏了堆叠查询（stacked queries）和 `||` 运算符语义绕过的组合。

### 核心考点：MySQL `||` 运算符的双重身份

MySQL 的 `||` 在不同 `sql_mode` 下有不同含义：

| sql_mode | `||` 含义 | `select 1 || flag from Flag` 的结果 |
|----------|----------|-----------------------------------|
| 默认（无 PIPES_AS_CONCAT） | 逻辑 OR | `1 OR flag`，flag 非空，等价于 `1` |
| 设置了 PIPES_AS_CONCAT | 字符串拼接 | `concat(1, flag)`，等同于 `1` + flag 内容拼接 |

### 方法一：`1;select *,1` — 用逗号隔离 `*`

注入后完整 SQL：

```sql
select 1;select *,1 || flag from Flag;
```

**为什么不能直接写 `select *` 而必须是 `select *,1`：**

如果注入 `1;select *`，后端拼好后是：

```sql
select 1;select * || flag from Flag;
```

`*` 后面紧跟着 `||`，MySQL 解析器会把 `*` 优先识别为**乘法运算符**。一个乘法运算符前面没有左操作数，后面又是 `||`，直接语法错误。

换句话说：**`*` 只有当它独立作为 select 列表项时才是通配符，一旦后面跟了运算符，它就被解析为乘法符号。**

加了逗号 `*, 1 || flag` 就完全不同了：

- `*` — 逗号隔离，独立项，解析为"所有列"
- `1 || flag` — 独立表达式，`1 OR flag` = `1`（逻辑 OR，1 是 truthy，flag 非空）

结果集：

```
  flag (来自 *)    |   1 (来自 1 || flag)
  ----------------+---------------------
  flag{xxx}       |   1
```

flag 是 `*` 作为通配符选出来的，和后面的 `|| flag` 没有任何关系。`|| flag` 那段是后端模板固定拼上去的，删不掉，但可以用逗号把它隔成一个无害的独立列。

### 方法二：`1;set sql_mode=PIPES_AS_CONCAT;select 1` — 改变游戏规则

注入后完整 SQL：

```sql
select 1;set sql_mode=PIPES_AS_CONCAT;select 1 || flag from Flag;
```

分步分析：

1. `select 1;` — 返回字面量 1，让第一条语句合法
2. `set sql_mode=PIPES_AS_CONCAT;` — 把当前会话的 `||` 语义从逻辑 OR 改成字符串拼接
3. `select 1 || flag from Flag;` — 此时 `||` 等同于 `concat`，`select concat(1, flag)`，flag 内容被拼接到 1 后面输出

`concat` 被过滤了？没关系——用 `||` + `PIPES_AS_CONCAT` 达到了完全一样的效果。而且 `PIPES_AS_CONCAT` 本身不含 `or`，不在过滤范围内。

### 攻击链（方法一）

1. 攻击者在 POST body 中传入 `query=1;select *,1`
2. 后端拼入 SQL 模板：`select 1;select *,1 || flag from Flag;`
3. 分号分隔，两条语句均合法：第一条无意义，第二条 `*` 因逗号隔离被解析为通配符，选中 flag 列
4. 应用回显结果集，第一列即为 flag 内容

### 攻击链（方法二）

1. 攻击者在 POST body 中传入 `query=1;set sql_mode=PIPES_AS_CONCAT;select 1`
2. 后端拼入 SQL 模板，堆叠执行三条语句
3. `set` 语句将 `||` 改为拼接语义
4. `select 1 || flag` 等同于 `concat(1, flag)`，拼接结果被回显

### 过滤绕过分析

| 过滤项 | 方法一 `1;select *,1` | 方法二 `1;set sql_mode=PIPES_AS_CONCAT;select 1` |
|--------|----------------------|------------------------------------------------|
| union | 没用到 | 没用到 |
| extractvalue/updatexml | 没用到 | 没用到 |
| group_concat | 没用到 | 没用到 |
| `"` | 没用到 | 没用到 |
| 含 `or` 的字符串 | 无：select 不含 or，from 由后端拼入 Flag 表 | PIPES_AS_CONCAT 不含 or |

### 修复方案

1. **参数化查询** — 根本修复。`query` 作为查询字符串不应直接拼入 SQL。如果确实需要动态拼接列名或表达式，使用白名单校验
2. **禁用堆叠查询** — 使用 `mysql_query()`（不支持堆叠）或启用 `multi_statements=0`
3. **禁用危险 sql_mode 修改** — 限制 `SET` 语句的权限，普通应用账户不应有 `SET` 权限
4. **输入白名单** — 如果 `query` 值域有限，使用白名单（如只允许特定数字）

### 关联知识

- **MySQL `||` 运算符语义** — `sql_mode` 中 `PIPES_AS_CONCAT` 标志决定 `||` 是逻辑 OR 还是字符串拼接。Oracle 兼容模式下默认开启
- **堆叠查询（Stacked Queries）** — 取决于驱动 API 是否支持。`mysqli_multi_query()` 支持，`mysql_query()` 不支持，PDO 默认不支持但可通过 `EMULATE_PREPARES` 间接支持
- 类似的 SQL 模式绕过：`NO_BACKSLASH_ESCAPES` 改变转义行为、`PAD_CHAR_TO_FULL_LENGTH` 影响 `LIKE` 行为
