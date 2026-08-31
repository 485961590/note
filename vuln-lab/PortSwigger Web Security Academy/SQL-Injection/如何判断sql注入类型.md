## 根据报错信息判断（开启display_errors或错误回显）
构造一个非法的sql如错误的闭合方式导致数据库报错，不同数据库的报错信息特性明显：

| 数据库        | 典型报错特征                                                           |
| ---------- | ---------------------------------------------------------------- |
| MySQL      | You have an error in your SQL syntax near ...                    |
| MSSQL      | Microsoft OLE DB Provider for SQL Server / Incorrect syntax near |
| Oracle     | ORA-01756: quoted string not properly terminated                 |
| PostgreSQL | ERROR: syntax error at or near ... / unterminated quoted string  |
| SQLite     | SQLite.Exception / unrecognized token                            |
| Access     | Microsoft JET Database Engine 错误                                 |

## 基于方言差异语法探测
各数据库对同一操作的语法不同，用“只在一个数据库里合法”的语句探测：

**字符串拼接方式**（同一个注入点分别测，哪种不报错就是哪种）：
- MySQL：`'ab' 'cd'`（空格拼接）或 `CONCAT('a','b')`
- MSSQL：`'ab'+'cd'`
- Oracle / PostgreSQL：`'ab'||'cd'`

**注释符差异**：
- `#` 只在 MySQL 有效；`--` 通用（MySQL 后要带空格或用 `--+` URL 编码）；`/* */` 通用
- MySQL 独有的内联版本注释：`/*!40119 AND 1=1*/`，被 MySQL 解析、其他数据库当普通注释，以此确认 MySQL

**特有函数 / 变量**：
- `version()`：MySQL、PostgreSQL 都有
- `@@version`：MySQL、MSSQL
- `select banner from v$version`：Oracle 专属（且 Oracle 的子查询必须带 `FROM dual`）
- `sqlite_version()`：SQLite 专属
- `database()`（MySQL）vs `DB_NAME()`（MSSQL）vs `current_database()`（PostgreSQL）

**系统表探测**（盲注下用 `and exists(select count(*) from 表名)` 的真假判断）：
- `information_schema.tables`：MySQL、PostgreSQL
- `sysobjects`（`from sysusers` 也行）：MSSQL
- `user_tables` / `all_tables`：Oracle
- `msysobjects`：Access（报权限错误也是 Access 的特征）

## 基于延时函数（盲注场景）
布尔盲注没反应时，用各库专属的延时函数探测：
- MySQL：`sleep(5)`
- MSSQL：`;waitfor delay '0:0:5'--`
- PostgreSQL：`pg_sleep(5)`
- Oracle：`dbms_pipe.receive_message(('a'),5) from dual`，或重查询（heavy query）如 `select count(*) from all_objects,all_objects` 拖慢响应

## 基于端口和后端环境旁证
辅助信息，不能单独定论但能缩小范围：

- 端口：3306=MySQL、1433=MSSQL、1521=Oracle、5432=PostgreSQL
- Web 技术栈搭配：ASP.NET + IIS → 大概率 MSSQL；PHP → 大概率 MySQL；JSP/Tomcat → 常见 Oracle 或 MySQL
- 服务器 OS：Windows 环境偏 MSSQL/Acces