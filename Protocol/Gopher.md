# Gopher 协议与 Web 安全中的利用

**Gopher 是一种诞生于 1991 年的文本型网络协议**，用于在互联网上检索和分发文档，是 Web（HTTP/WWW）出现之前最主要的"超媒体"信息浏览方式。它已被 HTTP 完全取代，但由于 curl 等主流客户端至今仍支持 `gopher://`，该协议在 Web 安全渗透测试（尤其是 SSRF）中依然具有很高的利用价值。

## 1. 协议简介

- **时间与来源**：1991 年由美国明尼苏达大学（University of Minnesota）的 Mark P. McCahill 等人开发，命名源自该校吉祥物"金色地鼠"（Golden Gopher）。
- **标准**：RFC 1436（1993 年 3 月）《The Internet Gopher Protocol》。
- **定位**：分布式文档检索与分发系统，其内容世界被称为 "Gopherspace"。
- **工作模型**：基于 TCP 的"请求–响应"模型，无状态，每个连接通常只获取一个资源。
- **默认端口**：TCP 70。
- **特点**：文本协议、菜单驱动、层级化组织。菜单中的每个条目可以指向**任意**服务器与端口，这正是"分布式"的含义，也是后续被滥用的根源。

## 2. 协议规范（RFC 1436）

### 2.1 请求格式

客户端建立 TCP 连接后，发送一个 **selector**（资源选择字符串），并以 **CRLF（`\r\n`）** 结尾：

```
<selector>\r\n
```

- 空 selector（直接发送 `\r\n`）表示请求服务器的顶层菜单。
- selector 是资源在服务器上的定位字符串，不包含空格，也不可包含 CR/LF。

### 2.2 响应格式

服务器返回一串"菜单条目"（menuitem），每条以 CRLF 结尾：

```
<type><display-string>\t<selector>\t<host>\t<port>\r\n
```

| 字段 | 说明 |
|------|------|
| `<type>` | 1 个字符的条目类型 |
| `<display-string>` | 展示给用户的文本 |
| `<selector>` | 请求该条目时要发送的 selector |
| `<host>` | 提供该条目的主机 |
| `<port>` | 提供该条目的端口 |

字段之间用 **TAB（`\t`）** 分隔；条目中的 `host` 与 `port` 可以与本菜单所在服务器不同（分布式引用）。

整个菜单列表以一个**单独包含句点 `.` 的行**结束：`.\r\n`。

### 2.3 条目类型（item type）

| 类型 | 含义 |
|------|------|
| `0` | 文本文件 |
| `1` | 目录（子菜单） |
| `2` | CSO 电话簿服务器 |
| `3` | 错误 |
| `4` | BinHex 编码的 Macintosh 文件 |
| `5` | DOS 二进制归档文件 |
| `6` | Unix uuencode 编码文件 |
| `7` | 索引/搜索服务器 |
| `8` | Telnet 会话 |
| `9` | 二进制文件 |
| `g` | GIF 图片 |
| `I` | 其他格式图片 |
| `T` | tn3270 会话 |
| `+` | 冗余服务器（镜像） |
| `h` | HTML 文件（扩展） |
| `s` | 声音文件（扩展） |
| `S` | SGML 文件（扩展） |
| `M` | MIME 文件（扩展） |
| `P` | PDF 文件（扩展） |

> 说明：`0`–`9`、`+`、`g`、`I`、`T` 由 RFC 1436 定义；`h`、`s`、`S`、`M`、`P` 等为后续实践中出现的扩展类型，并非全部由 RFC 1436 规定。

## 3. gopher:// URL 与 curl 的处理机制（利用的关键）

`gopher://` 是 RFC 1738 中定义的 URL scheme。curl 至今仍默认支持（除非构建时显式禁用）。

curl 对 `gopher://` URL 的处理方式，决定了它的攻击价值：

```
gopher://<host>:<port>/<type><selector>
```

- curl 会**丢弃路径的第一个字符**（视为 Gopher 条目类型，不发送）；
- 将**其余部分作为 selector 原样发送**，并在末尾**追加一个 CRLF**。

因此约定俗成的写法是：在 `_`（任意占位类型字符）之后拼上 URL 编码后的原始字节：

```
gopher://<host>:<port>/_<url-encoded-payload>
```

实际发往目标端口的字节为 `<payload>\r\n`。

关键点：

- gopher 请求**不会**被 curl 添加任何 HTTP 头或协议封装，发送的全是指定的原始字节。
- payload 中的控制字节必须 URL 编码：`\r\n` 对应 `%0d%0a`、空格对应 `%20`。
- 若 gopher URL 被嵌套在 SSRF 参数中，通常需要对**整个 gopher URL 二次编码**。

示例（向 Redis 发送 `INFO` 命令）：

```
gopher://127.0.0.1:6379/_INFO
```

## 4. 在 Web 渗透测试中的定位：SSRF

SSRF（服务端请求伪造）中，服务器代码会根据用户输入发起请求。若代码仅校验了 `http`/`https` 等常见协议，或只校验主机名是否为内网而忽略了协议，就可能被 `gopher://` 绕过。

gopher 在 SSRF 中的价值：

- **任意 TCP 数据注入**：可以"讲"任意文本协议，直接打 Redis、FastCGI、MySQL、SMTP 等内网服务；
- 相比 `dict://`、`file://` 等其它非 HTTP scheme，gopher 能携带**多行、任意字节**的载荷，表达能力强得多；
- 部分过滤规则只封禁 `file://`、`dict://`，却漏掉 `gopher://`。

利用前提：**服务端发起请求所用的 HTTP 客户端必须支持 gopher 协议**。各客户端支持情况如下：

| 客户端 | 是否支持 gopher |
|--------|----------------|
| curl / libcurl（PHP cURL 扩展、Python pycurl、curl_cffi 等） | 支持（默认） |
| GNU Wget | 不支持（上游从未实现过 gopher；旧文中“1.16 起移除”的说法有误） |
| Python urllib / requests | 不支持 |
| Java HttpURLConnection | 不支持 |
| Node.js http 模块 | 不支持 |

也就是说，gopher SSRF 的常见出现位置是**使用 curl 或 libcurl 系**的后端（典型如 PHP 的 cURL 扩展）。

若 SSRF 无回显（blind SSRF），gopher 的写文件类攻击（如 Redis 写 WebShell）依然可行，因为这类攻击不依赖读取响应。

## 5. 常见利用目标与手法

### 5.1 Redis（TCP 6379）

Redis 支持**内联命令**与 **RESP（多行协议）**。未开启认证（或弱口令）且允许 `CONFIG` 命令时，可通过 gopher 下发命令写文件，进而 RCE。

经典利用链（写 crontab 反弹 shell / 写 WebShell / 写 SSH 公钥）：

```
1. FLUSHALL                          # 清空数据库，保证写出的文件干净
2. SET <key> <payload>               # payload 为 webshell 或 crontab 内容
3. CONFIG SET dir <目标目录>          # 如 /var/spool/cron/、web 根目录、~/.ssh/
4. CONFIG SET dbfilename <文件名>     # 如 root、shell.php、authorized_keys
5. SAVE / BGSAVE                     # 触发落盘
```

为什么用 RESP 而不是内联命令：webshell / crontab 内容通常含空格，内联命令会按空格拆分参数，而 RESP 多行协议可以携带任意二进制内容。

- 写入 crontab：RHEL 系为 `/var/spool/cron/root`，Debian 系为 `/var/spool/cron/crontabs/root`；
- 写入 SSH 公钥：目标 Redis 运行用户（常为 root）的 `~/.ssh/authorized_keys`；
- 写入 WebShell：需要已知 web 根目录路径。

其它手法：

- **SLAVEOF 数据窃取**：让目标 Redis `SLAVEOF` 到攻击者服务器，把数据复制出来；
- 主从复制 + 恶意模块加载实现 RCE（依赖服务端模块加载能力）；
- `dict://` 协议也可向 Redis 下发命令：`dict://127.0.0.1:6379/CONFIG:SET:dir:/var/www/html`（dict 协议以冒号/换行分隔命令）。

示例（RESP 写一个键，说明字节结构）：

```
*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$2\r\nvv\r\n
```

URL 编码后拼接：

```
gopher://127.0.0.1:6379/_*3%0d%0a$3%0d%0aSET%0d%0a$1%0d%0ak%0d%0a$2%0d%0avv%0d%0a
```

> 注意：RESP 中的长度前缀必须与实际字节数严格一致。实际利用时宜用 Gopherus 等工具生成，避免手工算错长度。

### 5.2 FastCGI / PHP-FPM（TCP 9000）

典型脆弱场景：Nginx 配置 `fastcgi_pass` 直接指向未加防护的 PHP-FPM（常见监听 `127.0.0.1:9000`）。此时可通过 gopher 构造 FastCGI 协议包执行 PHP 代码。

- FastCGI 记录由 8 字节头 + 内容组成：`version(1)、type(1)、requestId(2)、contentLength(2)、paddingLength(1)、reserved(1)`；
- 关键记录类型：`FCGI_BEGIN_REQUEST=1`、`FCGI_PARAMS=4`、`FCGI_STDIN=5`；
- 利用要点：在 `FCGI_PARAMS` 中设置 `SCRIPT_FILENAME` 指向目标上**真实存在的一个 PHP 文件**，并通过 `PHP_VALUE` 注入配置，例如：
  - `auto_prepend_file=php://input` + `allow_url_include=On`，再把 PHP 代码放入 `FCGI_STDIN`；
- 从而将任意 PHP 代码"预加载"执行，实现 RCE。

前提：需要知道目标上存在的一个 PHP 文件路径。

### 5.3 MySQL（TCP 3306）

MySQL 是**二进制协议**，且登录需要握手认证，构造难度高于纯文本协议。

- 思路：无密码/弱口令时，先通过抓包复用一段真实的客户端认证包完成握手，再发送 `COM_QUERY`（0x03）执行 SQL；
- 可执行：`SELECT LOAD_FILE('...')` 读取文件、`SELECT ... INTO OUTFILE` 写文件（受 `secure_file_priv` 限制）、导出数据；
- 报文格式：3 字节小端长度 + 1 字节序列号 + 载荷，长度字段对后续字节数敏感；
- 技巧：在载荷末尾追加 `COM_QUIT`（0x01）包，用于吸收 curl 追加的 CRLF，避免破坏协议帧。

### 5.4 Memcached（TCP 11211）

Memcached 使用文本协议（`set`/`get`/`stat`）：

```
set <key> <flags> <exptime> <bytes>\r\n<data>\r\n
```

利用思路：

- 写入恶意序列化数据，触发下游应用反序列化（Python pickle、Ruby Marshal、PHP unserialize）；
- 或进行缓存投毒。

### 5.5 SMTP（TCP 25）

SMTP 是文本协议，可通过 gopher 直接"说"：

```
HELO x
MAIL FROM:<a@victim>
RCPT TO:<target@corp>
DATA
...
QUIT
```

利用思路：以内网/本机身份发送钓鱼邮件、滥用开放中继、构造邮件头注入。

### 5.6 Zabbix（TCP 10050）

Zabbix Agent 使用类似 `zabbix_sender` 的文本协议。若服务端配置了 `EnableRemoteCommands=1`，可通过 `system.run[...]` 执行系统命令。

### 5.7 PostgreSQL（TCP 5432）

弱口令下可通过 gopher 讲 PostgreSQL 协议：

- `COPY ... FROM PROGRAM` 执行系统命令（需足够权限）；
- 导出数据、读写文件。

### 5.8 任意 TCP 协议（通用）

凡是内部可达、使用文本协议的服务都可以尝试 gopher 直连：

- 构造**原始 HTTP 请求**打内网 Web 应用/管理接口（绕过外网 WAF 与访问控制）；
- 直连 Elasticsearch（9200）等以 HTTP/JSON 为接口的服务。

## 6. 常用工具

| 工具 | 说明 |
|------|------|
| **Gopherus**（tarunkant/Gopherus） | 最常用的 payload 生成器，支持 MySQL、PostgreSQL、FastCGI、Redis、SMTP、Zabbix、Memcached，交互式输入参数后输出可直接使用的 gopher URL |

手动构造流程：按目标协议整理原始字节 → 逐字节 URL 编码 → 拼接为 `gopher://<host>:<port>/_<encoded>` → 若嵌套在 POST 参数中则整体二次编码。

## 7. 防御与检测

针对 gopher SSRF：

- **协议白名单**：在发起请求处仅允许 `http`/`https`，拒绝其它 scheme；
- **地址校验**：解析后校验目标 IP 是否为内网/保留地址，并防范 DNS rebinding；
- **curl 层限制**：使用 `CURLOPT_PROTOCOLS` / `CURLOPT_REDIR_PROTOCOLS` 限制可用协议；
- **内部服务加固**：Redis、MySQL、FastCGI 等配置强认证、绑定回环或内网受限接口、最小权限运行；Redis 可重命名高危命令或关闭 `CONFIG` 写文件能力；
- **检测**：WAF/IDS 对请求中的 `gopher://` 特征、内网地址配合非标准端口的组合进行告警。

## 8. 使用前提与易错点

- gopher 是否可用取决于**服务端 HTTP 客户端**：curl/libcurl 系才支持，其它常见客户端默认不支持；
- 所有特殊字节需 URL 编码，`\r\n` 为 `%0d%0a`；嵌套场景需二次编码；
- curl 发送时会**追加 CRLF**：若 payload 末尾已编码 CRLF，实际会多出一个空行；对按行解析的协议（Redis 等）通常无害，对严格按长度读取的二进制协议可能破坏帧，需验证（如 MySQL 用 `COM_QUIT` 收尾）；
- RESP 长度前缀、二进制协议长度字段都**必须与实际字节数精确一致**；
- Redis 3.2+ 存在保护模式（protected mode），但**来自本机（回环）的连接通常不受限**，因此源自服务器自身的 SSRF 依然可利用；
- 写 crontab 反弹 shell 还依赖 Redis 进程对该目录的写权限与目标系统的 crontab 机制，需按实际环境验证。

## 参考

- RFC 1436 — The Internet Gopher Protocol
- RFC 1738 — Uniform Resource Locators（定义 `gopher://` URL）
- tarunkant/Gopherus — gopher payload 生成工具
- ISITDTU CTF 2018 "Friss" writeup — gopher 打 MySQL 的典型案例
