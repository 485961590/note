# ffuf 目录发现实用指南

`ffuf` 通过字典替换 URL 中的 `FUZZ`，批量请求网站路径，常用于发现目录、文件和备份文件。

以下命令只适用于自己控制的主机、靶场或明确授权的测试目标。示例中的 `TARGET` 需要替换为目标地址，`WORDLIST` 需要替换为本机字典路径。

## 1. 基本语法

```bash
ffuf -w WORDLIST -u http://TARGET/FUZZ
```

`FUZZ` 是必须的占位符。ffuf 会依次用字典中的每一行替换它：

```text
admin
login
robots.txt
```

会被尝试为：

```text
http://TARGET/admin
http://TARGET/login
http://TARGET/robots.txt
```

先确认 ffuf 已安装，以及当前版本支持哪些参数：

```bash
ffuf -h
ffuf -V
```

## 2. 常用字典

Kali 中常见的字典路径如下，实际路径以本机安装情况为准：

| 字典                                                             | 适用场景           |
| -------------------------------------------------------------- | -------------- |
| `/usr/share/wordlists/dirb/common.txt`                         | 快速初筛，字典较小      |
| `/usr/share/seclists/Discovery/Web-Content/common.txt`         | 常用 Web 路径      |
| `/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt` | 更全面的目录发现       |
| 自己整理的路径文件                                                      | 针对特定框架、CMS 或项目 |

先用小字典确认目标路径和参数，再换大字典。大字典并不一定带来更好的结果，只会增加请求数量和误报处理成本。

## 3. 参数速查

### 目标和请求

| 参数 | 作用 |
| --- | --- |
| `-u URL` | 目标 URL，通常包含 `FUZZ` |
| `-w FILE` | 指定字典文件 |
| `-e .EXT1,.EXT2` | 给每个字典词追加文件扩展名 |
| `-H HEADER` | 添加请求头，可重复使用 |
| `-b COOKIE` | 发送 Cookie |
| `-X METHOD` | 指定 HTTP 方法 |
| `-d DATA` | 发送请求体 |
| `-r` | 跟随重定向 |
| `-x PROXY` | 通过 HTTP、HTTPS 或 SOCKS5 代理 |
| `-request FILE` | 从原始 HTTP 请求文件加载请求模板 |
| `-request-proto http/https` | 配合 `-request` 指定协议 |

### 匹配和过滤

| 参数          | 作用                             |
| ----------- | ------------------------------ |
| `-mc CODES` | 只显示指定状态码                       |
| `-fc CODES` | 隐藏指定状态码                        |
| `-ms SIZE`  | 只显示指定响应大小                      |
| `-fs SIZE`  | 隐藏指定响应大小                       |
| `-mw WORDS` | 只显示指定单词数                       |
| `-fw WORDS` | 隐藏指定单词数                        |
| `-ml LINES` | 只显示指定行数                        |
| `-fl LINES` | 隐藏指定行数                         |
| `-mr REGEX` | 只显示正文匹配正则表达式的响应                |
| `-ac`       | 自动校准并过滤统一的错误页面                 |
| -recursion  | 递归查询-recursion-depth 3（指定递归层数） |

多个状态码或数值用逗号分隔，例如 `-fc 404,403`。范围可以写成 `-fs 1000-1200`。

### 速度和输出

| 参数 | 作用 |
| --- | --- |
| `-t N` | 并发线程数，默认通常为 40 |
| `-rate N` | 限制每秒请求数 |
| `-p SEC` | 每个请求增加固定或随机延迟 |
| `-timeout SEC` | 单个请求超时时间 |
| `-maxtime SEC` | 本次扫描最长运行时间 |
| `-o FILE` | 保存扫描结果 |
| `-of FORMAT` | 输出格式，如 `json`、`csv`、`html`、`md` |
| `-c` | 开启彩色输出 |
| `-s` | 隐藏额外提示，只保留结果 |
| `-v` | 显示更完整的 URL 和重定向信息 |

## 4. 基础目录发现

最基本的目录扫描：

```bash
ffuf -w /usr/share/wordlists/dirb/common.txt \
  -u http://TARGET/FUZZ \
  -c
```

如果目标部署在某个子目录，`FUZZ` 应放在对应位置：

```bash
ffuf -w common.txt -u http://TARGET/app/FUZZ -c
```

如果想测试带结尾斜杠的路径，可以写成：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ/ -c
```

这两种写法请求的路径不同，按目标站点的路由习惯选择。发现一个目录后，应手动访问并继续针对该目录扫描。

## 5. 扫描常见文件扩展名

使用 `-e` 自动测试扩展名：

```bash
ffuf -w /usr/share/wordlists/dirb/common.txt \
  -u http://TARGET/FUZZ \
  -e .php,.txt,.bak,.zip \
  -c
```

对于字典中的 `admin`，通常会尝试 `admin`、`admin.php`、`admin.txt`、`admin.bak` 和 `admin.zip`。

扩展名应根据目标技术选择，不要一次添加几十种。Linux/PHP 目标可以先试 `.php,.txt,.bak,.zip`，静态站点可以先试 `.html,.txt`。

## 6. 处理误报

目录扫描最常见的问题不是“没有结果”，而是目标对不存在的路径也返回正常页面。先观察 ffuf 每条结果中的 `Status`、`Size`、`Words` 和 `Lines`，再决定过滤条件。

### 按状态码筛选

只看常见的成功和重定向：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ \
  -mc 200,204,301,302,307,401,403
```

只显示 200：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ -mc 200
```

隐藏 404 和 403：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ -fc 404,403
```

如果使用了 `-mc 200`，403 不会显示，不需要再写 `-fc 403`。如果使用 `-mc all` 查看所有响应，再用 `-fc` 过滤会更直观。

### 过滤统一的错误页面

先请求一个确定不存在的路径，记录返回大小：

```bash
curl -sS -o /dev/null -w 'status=%{http_code} size=%{size_download}\n' \
  http://TARGET/this-path-should-not-exist-12345
```

假设返回大小为 `422`，使用 `-fs 422` 隐藏相同大小的页面：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ \
  -mc all -fs 422
```

也可以按单词数或行数过滤：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ -fw 23
ffuf -w common.txt -u http://TARGET/FUZZ -fl 12
```

### 自动校准

不想手动找错误页面大小时，可以先试 `-ac`：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ -ac
```

如果页面内容每次都变化，自动校准可能不稳定。这时手动确认一个不存在路径，再使用 `-fs`、`-fw` 或 `-fl`，并复查过滤后是否误删了真实目录。

## 7. 登录后目录发现

需要登录才能访问的目录，可以带上现有 Cookie：

```bash
ffuf -w common.txt \
  -u http://TARGET/FUZZ \
  -b 'session=SESSION_VALUE' \
  -c
```

也可以添加请求头：

```bash
ffuf -w common.txt \
  -u http://TARGET/FUZZ \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Accept: text/html' \
  -c
```

Token 和 Cookie 只放在授权环境中使用，不要把真实值写入公开的命令记录或结果文件。

## 8. 使用原始请求模板

如果请求依赖多个请求头、Cookie 或特殊请求体，可以从 Burp 等工具导出原始请求，将需要替换的位置改为 `FUZZ`：

```text
GET /FUZZ HTTP/1.1
Host: TARGET
User-Agent: Mozilla/5.0
Accept: text/html
Connection: close

```

保存为 `request.txt` 后执行：

```bash
ffuf -request request.txt \
  -request-proto http \
  -w common.txt \
  -mc 200,301,302,403
```

如果原始请求是 HTTPS，将 `-request-proto http` 改为 `-request-proto https`。请求文件中的 `Content-Length` 如果与修改后的请求体不一致，优先删除它，让客户端重新处理，或根据当前版本帮助调整。

## 9. 递归扫描

发现目录后自动继续扫描：

```bash
ffuf -w common.txt \
  -u http://TARGET/FUZZ \
  -recursion \
  -recursion-depth 2 \
  -c
```

递归模式要求 URL 以 `FUZZ` 结尾，例如 `http://TARGET/FUZZ`。如果写成 `http://TARGET/FUZZ?x=1`，递归通常无法按预期工作。

递归扫描请求量会快速增加，先使用小字典和较浅深度。发现结果后，手动针对重点目录重新扫描通常更容易控制。

## 10. 限速和保存结果

靶场中可以适当提高并发：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ -t 80 -c
```

目标响应变慢或出现大量超时时，降低并发并限制速率：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ \
  -t 20 -rate 100 -timeout 10
```

保存 JSON 结果：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ \
  -o ffuf-result.json -of json
```

保存 CSV，方便用表格软件查看：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ \
  -o ffuf-result.csv -of csv
```

并发和速率应根据目标承受能力调整。授权测试也应避免无意义地制造大量请求。

## 11. 一套实用流程

### 第一步：小字典初扫

```bash
ffuf -w /usr/share/wordlists/dirb/common.txt \
  -u http://TARGET/FUZZ \
  -ac -c
```

### 第二步：补充文件后缀

```bash
ffuf -w /usr/share/wordlists/dirb/common.txt \
  -u http://TARGET/FUZZ \
  -e .php,.txt,.bak,.zip \
  -ac -c
```

### 第三步：换大字典复查

```bash
ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -u http://TARGET/FUZZ \
  -e .php,.txt,.bak \
  -ac -t 40 \
  -o ffuf-result.json -of json -c
```

### 第四步：针对发现的目录继续扫描

例如发现 `/admin/`：

```bash
ffuf -w common.txt -u http://TARGET/admin/FUZZ -e .php,.txt -ac -c
```

## 12. 常见问题

### 结果全部是同一个状态码或大小

这通常是软 404 或统一跳转。使用 `-ac`，或者先请求随机不存在路径，再用 `-fs`、`-fw` 或 `-fl` 过滤基线响应。

### 明明有目录，却没有扫描结果

依次检查：

- URL 是否正确，`FUZZ` 是否拼在正确位置；
- 目标是否需要结尾斜杠或固定前缀；
- 是否需要 `Host`、Cookie 或 Authorization 请求头；
- 是否使用 `-mc 200` 导致 301、302、403 等结果被排除；
- 字典是否为空、路径是否写错。

### 递归模式没有继续扫描

确认 URL 是以 `FUZZ` 结尾的形式，例如：

```bash
ffuf -w common.txt -u http://TARGET/FUZZ -recursion
```

### 请求太慢或大量超时

降低 `-t`，设置合理的 `-timeout`，必要时使用 `-rate` 限制请求速率。不要只通过不断提高线程数解决问题。

### `-e` 扫描结果太多

扩展名越多，请求量越大。先按目标技术保留少量扩展名，再对发现的目录单独补扫。

## 快速记忆

- 基础目录：`ffuf -w common.txt -u http://TARGET/FUZZ`
- 文件扩展名：`-e .php,.txt,.bak`
- 看指定状态：`-mc 200,301,302,403`
- 过滤状态：`-fc 404`
- 过滤软 404：`-fs SIZE` 或 `-ac`
- 登录后扫描：`-b 'session=VALUE'` 或 `-H 'Authorization: Bearer TOKEN'`
- 递归发现：`-recursion -recursion-depth 2`
- 保存结果：`-o result.json -of json`
