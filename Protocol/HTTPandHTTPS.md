# HTTP

HTTP（HyperText Transfer Protocol，超文本传输协议）是 Web 通信的核心协议，位于 OSI 应用层，基于 TCP（HTTP/1.x 和 HTTP/2）或 QUIC/UDP（HTTP/3）。它定义了客户端与服务器之间请求-响应的交互格式。

核心特性：
- **无状态**：每个请求独立，服务器不保留上下文（Cookie/Session 是上层补充）
- **明文传输**（HTTP 自身）：数据未经加密，可被中间人读取和篡改
- **可扩展**：通过方法、头部、状态码灵活扩展功能

---
### . GET（查 / 点菜）

- **含义**：获取资源。向服务器索要数据。
- **特点**：**最 benign（无害）的方法**。参数直接拼在 URL 后面（比如 `?id=1`）。GET 请求不应该去“修改”服务器上的任何东西，只是“看”。
- **餐厅比喻**：你看菜单，问服务员“给我拿一份菜单看看”，或者“帮我上道宫保鸡丁”。你只是获取，不改变后厨的库存状态。
- **抓包特征**：没有 Request Body（请求体），数据都在 URL 里。

### 2. POST（增 / 下单）

- **含义**：提交数据给服务器处理。通常用于上传文件、提交表单（登录、注册）。
- **特点**：**数据放在 Request Body（请求体）里发送**，不会显示在 URL 中，相对安全一点（但绝不是加密！）。
- **餐厅比喻**：你填了一张点菜单（包含你要的菜、桌号），把它递给服务员。后厨收到后，会根据你的单子开始做菜（改变了服务器状态）。
- **渗透视角**：大部分的**登录爆破**、**SQL 注入**测试如果发生在登录框，都是在抓取 POST 请求后，对 Body 里的 `username` 和 `password` 进行注入。

### 3. PUT（改 / 换菜）

- **含义**：向服务器上传文件，或者**整体替换**某个已有的资源。
- **特点**：是 RESTful API 的标准方法。如果目标路径已有文件，PUT 会把它**完全覆盖**。
- **餐厅比喻**：服务员已经端上来一盘菜，你说“我不爱吃辣，把这盘**整个换**成不辣的”。
- **渗透视角**：极其危险！如果服务器配置失误（比如开启了 WebDAV），攻击者可以用 PUT 方法直接上传一个 WebShell（木马）到服务器目录下。

### 4. PATCH（部分改 / 加料）

- **含义**：对资源进行**局部修改**。（是后来才加入 HTTP 标准的）。
- **特点**：不同于 PUT 的全量替换，PATCH 只传你需要改的那几个字段。
- **餐厅比喻**：菜已经上来了，你说“不用换，**只要**在里面多加点盐就行”。
- **渗透视角**：在测试现代 API 接口时，如果发现修改密码的接口用的是 PATCH，且存在越权漏洞，你可能只需要传 `{"password": "123456"}` 就能改掉别人的密码，而不需要传用户名、邮箱等一大堆无用信息。

### 5. DELETE（删 / 退菜）

- **含义**：删除指定的资源。
- **特点**：顾名思义，干掉服务器上的某个文件或数据库里的某条记录。
- **餐厅比喻**：“这盘菜有问题，给我撤走扔掉”。
- **渗透视角**：如果存在越权漏洞（比如 IDOR），你把别人的文章 ID 放到 DELETE 请求里发出去，你就把别人的文章删了。

---

### 其他“边缘”方法（了解即可）

- **HEAD**：和 GET 一模一样，但**服务器只返回响应头，不返回响应体（不返回网页内容）**。
    - _黑客怎么用_：用来**暗中侦查**。比如我想知道一个文件存不存在，我用 GET 会下载整个文件（浪费流量且留下大日志），用 HEAD 只看状态码是 200（存在）还是 404（不存在），神不知鬼不觉。
- **OPTIONS**：问服务器“你支持哪些 HTTP 方法？”
    - _黑客怎么用_：用来探测 PUT、DELETE 等危险方法是否被允许。如果返回 `Allow: GET, POST, PUT, DELETE`，黑客就会两眼放光。
- **TRACE**：主要用于诊断。客户端发一个 TRACE，服务器会把收到的请求原封不动弹回来（用于看中间代理有没有篡改请求）。现在大部分服务器因为安全原因（防 XST 攻击）都禁用了。

## 一、HTTP 版本演进

| 版本 | 年份 | RFC | 核心特点 |
|------|------|-----|----------|
| HTTP/0.9 | 1991 | — | 仅 `GET /path`，无头部、无状态码、纯文本响应 |
| HTTP/1.0 | 1996 | 1945 | 引入头部（Header）、状态码、`POST`/`HEAD`、`Content-Type` |
| HTTP/1.1 | 1997 | 2068→2616→7230~7235 | 持久连接（Keep-Alive）、Host 头（虚拟主机）、管线化、分块传输、缓存协商 |
| HTTP/2 | 2015 | 7540 | 二进制帧、多路复用、头部压缩（HPACK）、服务器推送、流优先级 |
| HTTP/3 | 2022 | 9114 | 基于 QUIC（UDP）、0-RTT 握手、无队头阻塞、连接迁移 |

> 当前主流：HTTP/1.1 和 HTTP/2 共存（HTTP/3 快速增长中）。

---

## 二、HTTP 请求

### 2.1 请求结构

一个完整的 HTTP/1.1 请求由三部分组成，每部分严格按以下顺序排列：

```
请求行（Request Line）
请求头部（Request Headers）
空行（\r\n）
请求体（Request Body，可选）
```

实例如下：

```http
POST /api/users?role=admin HTTP/1.1\r\n
Host: example.com\r\n
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n
Accept: application/json, text/plain;q=0.9\r\n
Accept-Encoding: gzip, deflate, br\r\n
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\n
Content-Type: application/x-www-form-urlencoded\r\n
Content-Length: 27\r\n
Cookie: session=abc123; theme=dark\r\n
Referer: https://example.com/admin\r\n
Origin: https://example.com\r\n
Connection: keep-alive\r\n
\r\n
username=admin&password=123
```

#### 请求行（Request Line）

```
METHOD SP request-target SP HTTP-version CRLF
```

三个字段用空格分隔：
- **METHOD**：请求方法（GET / POST / PUT / DELETE 等）
- **request-target**：路径 + 查询参数（origin-form: `/path?query`，或 absolute-form: `http://host/path` 用于代理）
- **HTTP-version**：协议版本（HTTP/1.0、HTTP/1.1、HTTP/2 以伪头部形式表达）

#### 空行

`\r\n`（CRLF）单独一行，是头部与请求体之间的分隔。HTTP/1.1 中每个头部行也以 `\r\n` 结尾。

### 2.2 请求头部详解

头部顺序遵循 RFC 7230 的规定：**除请求行必须在最前外，不同名称的头部之间没有强制顺序**。但实际工程中有约定俗成的排列习惯（从通用到具体），且同名头部必须保持发送顺序（如多个 `Cookie`）。

#### 按功能分类

**① 目标路由类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Host` | **HTTP/1.1 唯一必需头部**。指定目标主机名和端口（非默认端口时），用于虚拟主机路由。 | `Host: www.example.com:8080` |
| `:authority` | HTTP/2 伪头部，等价于 Host。格式同 Host，但不含端口时默认推断。 | `:authority: www.example.com` |

**② 客户端标识类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `User-Agent` | 客户端软件标识。浏览器发送完整 UA（含引擎、版本、OS），爬虫通常设独特值。安全意义：WAF 常基于此做访问控制，可被伪造。 | `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36` |
| `From` | 客户端用户邮箱，极少使用。 | `From: user@example.com` |

**③ 内容协商类**（Accept-*）

| 头部 | 说明 | 示例 |
|------|------|------|
| `Accept` | 客户端可处理的 MIME 类型列表。`q` 值（0~1）表示优先级，默认 q=1。 | `Accept: text/html, application/json;q=0.9, */*;q=0.5` |
| `Accept-Encoding` | 客户端支持的内容编码（压缩算法）。常见值：`gzip`、`deflate`、`br`（Brotli）。 | `Accept-Encoding: gzip, deflate, br` |
| `Accept-Language` | 客户端偏好语言，按优先级排列。 | `Accept-Language: zh-CN,zh;q=0.9,en;q=0.8` |
| `Accept-Charset` | 已废弃（HTML5 统一 UTF-8），几乎不再使用。 | — |

**④ 认证类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Authorization` | 携带认证凭据。格式取决于认证类型：`Basic`（Base64 编码用户名:密码）、`Bearer`（Token）、`Digest`。 | `Authorization: Bearer eyJhbGciOi...` |
| `Proxy-Authorization` | 向代理服务器认证的凭据，格式同 `Authorization`。 | `Proxy-Authorization: Basic dXNlcjpwYXNz` |
| `Cookie` | 携带当前域名下存储的所有 Cookie（不含 HttpOnly 的仍会被发往服务器）。每个 `; ` 分隔一个键值对。 | `Cookie: session=abc123; csrf_token=xyz` |

**⑤ 请求体描述类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Content-Type` | 请求体的 MIME 类型。POST/PUT 时必填。常见值：`application/json`、`application/x-www-form-urlencoded`、`multipart/form-data`。 | `Content-Type: application/json; charset=utf-8` |
| `Content-Length` | 请求体的字节数（十进制）。**不包含头部和空行**。与 `Transfer-Encoding: chunked` 互斥。 | `Content-Length: 256` |
| `Content-Encoding` | 请求体的压缩编码，服务器据此解压。 | `Content-Encoding: gzip` |
| `Transfer-Encoding` | 传输编码方式。`chunked` 表示分块传输（边长内容），每块格式：`十六进制长度\r\n数据\r\n`，以 `0\r\n\r\n` 结尾。 | `Transfer-Encoding: chunked` |

**⑥ 缓存与条件请求类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Cache-Control` | 缓存指令。`no-cache`（必须验证）、`no-store`（不缓存）、`max-age=N`（有效秒数）、`only-if-cached`。 | `Cache-Control: no-cache` |
| `Pragma` | HTTP/1.0 遗留，`Pragma: no-cache` 等同 `Cache-Control: no-cache`（向后兼容）。 | `Pragma: no-cache` |
| `If-Modified-Since` | 条件 GET：仅在指定时间后有修改时返回 200，否则返回 304。 | `If-Modified-Since: Wed, 21 Oct 2025 07:28:00 GMT` |
| `If-None-Match` | 条件 GET：仅在 ETag 不匹配时返回 200。与 `If-Modified-Since` 同时存在时，ETag 优先级更高。 | `If-None-Match: "abc123"` |
| `If-Match` | 条件 PUT/PATCH/DELETE：仅在 ETag 匹配时执行，防止覆盖他人修改。 | `If-Match: "abc123"` |
| `If-Unmodified-Since` | 条件操作：仅在指定时间后无修改时执行。 | `If-Unmodified-Since: Wed, 21 Oct 2025 07:28:00 GMT` |
| `If-Range` | 结合 `Range`：若资源未变则返回部分内容（206），否则返回完整内容（200）。 | `If-Range: "abc123"` |
| `Range` | 请求部分内容，格式 `bytes=start-end`（两端都含）。多段：`bytes=0-499, 1000-1499`。 | `Range: bytes=0-1023` |

**⑦ 来源与上下文类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Referer` | 来源页面的完整 URL。从 HTTPS 页面跳转到 HTTP 页面时浏览器不发送（隐私）。安全意义：用于防盗链、CSRF 防御，但可被删除或伪造。 | `Referer: https://www.google.com/search?q=test` |
| `Origin` | 请求的来源（协议 + 主机 + 端口），不含路径。CORS 和 POST 请求自动发送，比 Referer 更可靠。 | `Origin: https://example.com` |
| `Referrer-Policy` | 指示浏览器 Referer 的发送策略。注意：单词拼写为 Referrer（正确），但头部名 Referer 是历史拼写错误。 | `Referrer-Policy: strict-origin-when-cross-origin` |

**⑧ 连接控制类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Connection` | `keep-alive`（保持 TCP 连接复用）、`close`（请求完成后关闭）、`Upgrade`（协议升级）。HTTP/1.1 默认 keep-alive。 | `Connection: keep-alive` |
| `Upgrade` | 请求升级到其他协议（如 WebSocket、HTTP/2）。 | `Upgrade: websocket` |
| `Keep-Alive` | 持久连接参数：`timeout=N`（空闲保持秒数）、`max=M`（最大复用次数）。 | `Keep-Alive: timeout=5, max=100` |
| `TE` | 接受哪些传输编码（类似 Accept-Encoding 但对传输编码），`trailers` 表示接受尾部头部。 | `TE: trailers, gzip` |

**⑨ 代理与中间件类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `X-Forwarded-For`（XFF） | 代理链中客户端的原始 IP 及经过的代理 IP（逗号分隔，左侧最近）。**可被客户端伪造**，仅当第一跳代理可信时可靠。 | `X-Forwarded-For: 203.0.113.1, 10.0.0.1` |
| `X-Forwarded-Host` | 原始请求的 Host（代理修改 Host 时保留原值）。 | `X-Forwarded-Host: original.example.com` |
| `X-Forwarded-Proto` | 原始请求的协议（`http` 或 `https`），用于代理后端的混合内容判断。 | `X-Forwarded-Proto: https` |
| `X-Real-IP` | Nginx 等代理提供的单一客户端真实 IP，不及 XFF 通用。 | `X-Real-IP: 203.0.113.1` |
| `Forwarded` | RFC 7239 标准的代理头部，统一替代上述 X-* 头。 | `Forwarded: for=203.0.113.1; proto=https; host=example.com` |
| `Via` | 记录请求经过的代理（每跳一个 Via 值），用于调试和检测循环。 | `Via: 1.1 proxy1.example.com` |
| `DNT` | Do Not Track，`1` 表示用户不希望被追踪（已被大多数站点忽略，已废弃）。 | `DNT: 1` |

**⑩ 其他**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Upgrade-Insecure-Requests` | `1` 表示客户端支持将 HTTP 资源自动升级到 HTTPS（CSP `upgrade-insecure-requests` 指令的配套头部）。 | `Upgrade-Insecure-Requests: 1` |
| `Expect` | 期望服务器行为。`100-continue` 表示先发头部，收到 100 Continue 后再发请求体（大文件上传优化）。 | `Expect: 100-continue` |
| `Max-Forwards` | 限制 TRACE/OPTIONS 请求的最大转发次数（防循环），每跳减 1，归零时直接返回。 | `Max-Forwards: 10` |
| `Save-Data` | 客户端请求精简数据（节省流量），值为 `on`。 | `Save-Data: on` |

#### 头部排列约定（非强制）

实际工程中常见的排列次序（通用 → 特定 → 安全/认证 → 内容描述）：

```
1. Host                    （路由目标，紧跟请求行）
2. User-Agent              （客户端身份）
3. Accept / Accept-Encoding / Accept-Language  （内容协商）
4. Authorization / Proxy-Authorization  （认证）
5. Cache-Control / Pragma / If-*  （缓存控制）
6. Referer / Origin        （来源上下文）
7. Cookie                  （会话状态）
8. Content-Type / Content-Length / Content-Encoding  （请求体描述）
9. Connection / Keep-Alive / Upgrade  （连接控制）
10. X-Forwarded-* / Forwarded / Via  （代理信息，靠后）
```

> RFC 强调：中间代理不得依赖头部顺序做路由/安全决策——顺序在所有实现间不保证一致。

### 2.3 HTTP 方法

| 方法 | 安全 | 幂等 | 可缓存 | 说明 |
|------|------|------|--------|------|
| `GET` | 是 | 是 | 是 | 获取资源。参数在 URL 中，长度受限于浏览器和服务器（通常 2K-8K） |
| `HEAD` | 是 | 是 | 是 | 与 GET 相同但不返回响应体，用于获取元数据（文件大小、是否缓存有效） |
| `POST` | 否 | 否 | 极少 | 提交数据（创建资源或触发操作）。请求体传参，无长度限制 |
| `PUT` | 否 | 是 | 否 | 完整替换指定资源（幂等：多次 PUT 相同内容结果一致） |
| `PATCH` | 否 | 否 | 否 | 部分修改资源（非幂等，除非使用 JSON Patch 等确定性格式） |
| `DELETE` | 否 | 是 | 否 | 删除资源。幂等：多次删除结果相同（资源已不存在） |
| `OPTIONS` | 是 | 是 | 否 | 查询服务器对指定 URL 支持的方法（预检请求），返回 `Allow` 头 |
| `TRACE` | 是 | 是 | 否 | 回显请求内容，用于调试代理链。安全风险：可能泄露 Cookie（XST 攻击），生产环境应禁用 |
| `CONNECT` | 否 | 否 | 否 | 建立到目标主机的隧道（用于 HTTPS 代理连接） |

- **安全**：不修改服务器状态
- **幂等**：多次相同请求的结果一致
- 上述特征来自规范定义，实际行为取决于服务器实现

### 2.4 HTTP/2 请求伪头部

HTTP/2 使用伪头部（前缀 `:`）替代 HTTP/1.1 的请求行：

```
:method: GET
:scheme: https
:authority: www.example.com
:path: /api/users?page=1
```

这 4 个伪头部必须在所有普通头部之前发送（HTTP/2 规范强制要求），且必须只出现一次。

---

## 三、HTTP 响应

### 3.1 响应结构

```
状态行（Status Line）
响应头部（Response Headers）
空行（\r\n）
响应体（Response Body）
```

实例：

```http
HTTP/1.1 200 OK\r\n
Date: Mon, 22 Jun 2026 10:30:00 GMT\r\n
Server: nginx/1.24.0\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 4567\r\n
Content-Encoding: gzip\r\n
Cache-Control: public, max-age=3600\r\n
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"\r\n
Last-Modified: Mon, 22 Jun 2026 08:00:00 GMT\r\n
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax\r\n
Strict-Transport-Security: max-age=31536000; includeSubDomains\r\n
Content-Security-Policy: default-src 'self'; script-src 'self'\r\n
X-Content-Type-Options: nosniff\r\n
X-Frame-Options: DENY\r\n
Referrer-Policy: strict-origin-when-cross-origin\r\n
Connection: keep-alive\r\n
\r\n
<!DOCTYPE html>...
```

#### 状态行（Status Line）

```
HTTP-version SP status-code SP reason-phrase CRLF
```

- **HTTP-version**：协议版本
- **status-code**：三位数字状态码
- **reason-phrase**：可读的状态描述（HTTP/2 中删除，HTTP/3 以伪头部表达）

### 3.2 响应头部详解

响应头部的顺序同样没有 RFC 强制规定，但工程实践中有合理的排列逻辑。

#### 按功能分类

**① 基本信息类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Date` | 响应生成的日期时间（GMT 格式）。用于计算 `Age` 和缓存新鲜度。 | `Date: Mon, 22 Jun 2026 10:30:00 GMT` |
| `Server` | 服务器软件名称和版本。安全建议：隐藏具体版本号（ServerTokens Prod），减少信息泄露。 | `Server: nginx` |

**② 响应体描述类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Content-Type` | 响应体的 MIME 类型和字符集。浏览器据此决定如何渲染（是 HTML 解析还是下载）。缺失时浏览器会做 MIME 嗅探（安全风险）。 | `Content-Type: application/json; charset=utf-8` |
| `Content-Length` | 响应体的字节数。必需头之一（除非使用 chunked 分块传输）。浏览器据此判断传输是否完成。 | `Content-Length: 4567` |
| `Content-Encoding` | 响应体的压缩编码。客户端依据请求中的 `Accept-Encoding` 声明支持，服务器选择一个应用。常见值：`gzip`、`br`（Brotli）、`zstd`。 | `Content-Encoding: br` |
| `Content-Language` | 响应内容的自然语言。 | `Content-Language: zh-CN` |
| `Content-Disposition` | 指示浏览器如何处理内容。`inline`（默认，直接在浏览器显示）、`attachment; filename="xxx"`（下载）。 | `Content-Disposition: attachment; filename="report.pdf"` |
| `Content-Range` | 部分内容响应的范围（206 Partial Content），格式 `bytes start-end/total`。 | `Content-Range: bytes 0-1023/4567` |
| `Transfer-Encoding` | 传输编码。`chunked` 表示分块传输（边生成边发送）；`gzip` 等较少用于 Transfer-Encoding（更常用 Content-Encoding）。`chunked` 时可附加尾部头部（Trailer）。 | `Transfer-Encoding: chunked` |
| `Trailer` | 预告在分块传输结束时会有哪些尾部头部（如 `Digest`、数字签名）。 | `Trailer: Digest` |

**③ 缓存控制类**

缓存控制是 HTTP 中设计最精细的子系统之一。缓存优先级：`Cache-Control` > `Expires` > 启发式（Last-Modified 推算）。

| 头部 | 说明 | 示例 |
|------|------|------|
| `Cache-Control` | 核心缓存指令。**请求**中：`no-cache`（必须验证）、`no-store`（禁止存储）、`max-age=0`（立即过期）、`only-if-cached`。**响应**中：`public`（可被任何缓存存储）、`private`（仅浏览器缓存）、`no-cache`（每次需验证）、`no-store`（禁止缓存）、`max-age=N`（保鲜秒数）、`s-maxage=N`（仅共享缓存的有效秒数，优先级高于 max-age）、`must-revalidate`（过期后必须验证）、`immutable`（内容永不变，刷新时不验证）。 | `Cache-Control: public, max-age=86400, must-revalidate` |
| `Expires` | HTTP/1.0 的过期时间（GMT）。`Cache-Control: max-age` 比 `Expires` 优先级高。两者同时存在时，`max-age` 生效。 | `Expires: Tue, 23 Jun 2026 10:30:00 GMT` |
| `Pragma` | HTTP/1.0 兼容头，`Pragma: no-cache` 等于 `Cache-Control: no-cache`。仅用于向后兼容。 | `Pragma: no-cache` |
| `ETag` | 实体标签，标识资源的特定版本（通常是内容的哈希或版本号）。强验证符用双引号 `"abc123"`，弱验证符以 `W/` 开头 `W/"abc123"`（内容语义相同但字节不同）。 | `ETag: "33a64df551425f"` |
| `Last-Modified` | 资源最后修改时间（GMT），精确到秒。精确度不如 ETag（秒级 vs 内容级）。 | `Last-Modified: Mon, 22 Jun 2026 08:00:00 GMT` |
| `Vary` | 告诉缓存：响应内容会因指定请求头的值不同而变化。`Vary: Accept-Encoding` 表示 gzip 版和无压缩版需分开缓存。**多个值用逗号分隔，或使用多个 Vary 头。** | `Vary: Accept-Encoding, Origin` |
| `Age` | 响应在缓存中已存活的秒数。透过代理时表示响应不是新鲜的（从源服务器生成到现在的总时间，由缓存累加）。 | `Age: 3600` |

**④ 连接控制类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Connection` | 控制当前连接行为：`keep-alive`（保持持久连接）、`close`（响应后关闭）、`Upgrade`（协议升级中）。逐跳头部（Hop-by-hop），代理必须删除后重新处理。 | `Connection: keep-alive` |
| `Keep-Alive` | 持久连接参数，`timeout=N`（空闲超时秒数）、`max=M`（最大请求数）。逐跳头部。 | `Keep-Alive: timeout=5, max=100` |
| `Upgrade` | 服务端接受协议升级（如 101 Switching Protocols 切换为 WebSocket）。 | `Upgrade: websocket` |

**⑤ 重定向与跳转类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Location` | 重定向目标 URL（3xx 或 201 Created 时使用）。可相对路径或绝对 URL。301/302 中浏览器自动跳转；201 中指定新创建资源的 URL。 | `Location: https://example.com/new-url` |
| `Refresh` | 非标准头，指示浏览器在 N 秒后跳转。安全风险：攻击者可通过 HTML `<meta>` 或头部注入实现钓鱼重定向。 | `Refresh: 5; url=https://example.com` |
| `Retry-After` | 503 或 429（请求过多）时告知客户端等待多少秒后重试。可填秒数或 GMT 时间。 | `Retry-After: 120` |

**⑥ 认证类**

| 头部 | 说明 | 示例 |
|------|------|------|
| `WWW-Authenticate` | 401 时声明服务器接受的认证方式，`realm` 为保护域描述。浏览器据此弹出登录框或处理 Token 续期。 | `WWW-Authenticate: Basic realm="Admin Area"` |
| `Proxy-Authenticate` | 407（Proxy Authentication Required）时声明代理的认证方式。 | `Proxy-Authenticate: Basic realm="Proxy"` |

**⑦ 会话类（Set-Cookie）**

`Set-Cookie` 是所有响应头中使用最频繁也最容易出安全问题的头部之一：

```
Set-Cookie: <name>=<value>; <属性1>; <属性2>; ...
```

完整属性列表：

| 属性 | 说明 | 缺失后果 |
|------|------|----------|
| `Domain` | Cookie 生效的域。默认当前域（不含子域）。`Domain=example.com` 允许子域（`a.example.com`）访问。**安全建议：除非必要，不设置 Domain，限制为当前精确域。** | Cookie 会被更广泛的域读取 |
| `Path` | Cookie 生效的路径前缀。`/admin` 仅管理路径发。默认当前路径。**注意：Path 的同源限制弱于 SameSite。** | 同域其他路径也能读取 Cookie |
| `Expires` | 绝对过期时间（GMT）。不设则为会话 Cookie（浏览器关闭即删除）。 | 持久化过多 |
| `Max-Age` | 相对过期时间（秒）。优先级高于 `Expires`。`Max-Age=0` 立即删除。 | — |
| `Secure` | 仅 HTTPS 连接发送。HTTP 连接下该 Cookie 不存在。 | Cookie 被明文嗅探 |
| `HttpOnly` | 禁止 `document.cookie`（JS）访问。XSS 攻击者无法直接窃取。 | XSS 可直接窃取 Cookie |
| `SameSite` | 跨站请求策略：`Strict`（完全不跨站）、`Lax`（顶级导航允许，推荐）、`None`（允许跨站，须配 `Secure`）。**Chrome 默认 Lax。** | 易受 CSRF 攻击 |
| `__Host-` 前缀 | 特殊前缀，Cookie 名以 `__Host-` 开头时，浏览器强制要求：`Secure` + `Path=/` + 无 `Domain`。最严格约束。 | — |
| `__Secure-` 前缀 | Cookie 名以 `__Secure-` 开头时，浏览器强制要求 `Secure`。 | — |
| `Partitioned` | 存储分区（CHIPS），Cookie 与顶级站点绑定而非只能第三方共享。`SameSite=None` 时可加。 | — |

示例：

```http
Set-Cookie: session=abc123; Secure; HttpOnly; SameSite=Lax; Path=/
Set-Cookie: __Host-csrf_token=xyz789; Secure; Path=/; SameSite=Strict
```

**⑧ CORS（跨域资源共享）类**

CORS 头由 OPTIONS 预检响应和实际响应返回：

| 头部 | 说明 | 示例 |
|------|------|------|
| `Access-Control-Allow-Origin` | 允许跨域访问的来源。`*`（不含凭据）或具体域名。**必须包含协议和端口（80/443 也需一致），不能多个值。** | `Access-Control-Allow-Origin: https://app.example.com` |
| `Access-Control-Allow-Credentials` | `true` 表示允许携带 Cookie 的跨域请求。此时 `Allow-Origin` 不能是 `*`，且 `Access-Control-Expose-Headers` 中需包含 `*` 或用具体值。 | `Access-Control-Allow-Credentials: true` |
| `Access-Control-Allow-Methods` | 预检响应中告诉客户端允许哪些方法。 | `Access-Control-Allow-Methods: GET, POST, PUT, DELETE` |
| `Access-Control-Allow-Headers` | 预检响应中告诉客户端允许哪些自定义请求头。 | `Access-Control-Allow-Headers: Content-Type, Authorization, X-Custom` |
| `Access-Control-Max-Age` | 预检响应缓存秒数，在此期间浏览器不发送预检。上限通常 86400（24h）。 | `Access-Control-Max-Age: 86400` |
| `Access-Control-Expose-Headers` | 告诉客户端允许 JS 从响应中读取哪些头部（默认仅 `Cache-Control`、`Content-Language`、`Content-Type`、`Expires`、`Last-Modified`、`Pragma` 可读）。 | `Access-Control-Expose-Headers: X-Total-Count, Link` |

**⑨ 安全类响应头**

| 头部 | 防护对象 | 说明 | 推荐配置 |
|------|----------|------|----------|
| `Content-Security-Policy`（CSP） | XSS、数据注入 | 白名单机制，限制页面可加载/执行的资源来源。`default-src 'self'` 为基准；`script-src`（含 `'nonce-'`、`'strict-dynamic'`）；`style-src`；`img-src`；`connect-src`；`frame-src`；`frame-ancestors`；`form-action`；`base-uri`等。**有专门 RFC 规范（CSP Level 3）。** | `default-src 'self'; script-src 'self' 'nonce-random'; frame-ancestors 'self'` |
| `Strict-Transport-Security`（HSTS） | SSL 剥离、中间人 | 强制浏览器仅通过 HTTPS 访问。`max-age` 必填（秒）；`includeSubDomains` 覆盖所有子域；`preload` 可提交到浏览器预加载列表。**首次访问前仍有窗口期风险。** | `max-age=31536000; includeSubDomains; preload` |
| `X-Frame-Options` | 点击劫持 | 控制页面能否被嵌入 `<iframe>`：`DENY`（禁止）、`SAMEORIGIN`（同源允许）。已被 CSP `frame-ancestors` 取代，但为兼容旧浏览器仍建议配置。 | `DENY` 或 `SAMEORIGIN` |
| `X-Content-Type-Options` | MIME 嗅探攻击 | `nosniff` 禁止浏览器猜测 Content-Type。防止攻击者上传 `text/html` 的 `<script>` 文件被嗅探为 HTML 执行。 | `nosniff` |
| `X-XSS-Protection` | XSS | 已废弃（CSP 替代）。老浏览器的反射型 XSS 过滤器控制：`1; mode=block` 启用，`0` 禁用。**现代安全建议：不设置或设 0（避免副作用），依赖 CSP。** | `0` |
| `Referrer-Policy` | 信息泄露 | 控制 Referer 头发送策略：`no-referrer`、`strict-origin-when-cross-origin`（推荐）、`same-origin`、`strict-origin`、`unsafe-url`。 | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | 浏览器功能滥用 | 控制哪些功能（摄像头、麦克风、定位、USB 等）对当前页面和嵌入的 iframe 可用。原名 `Feature-Policy`。 | `camera=(), microphone=(), geolocation=(self)` |
| `Cross-Origin-Resource-Policy`（CORP） | 跨域资源读取 | 控制其他源能否加载此资源。`same-origin`（最严格）、`same-site`、`cross-origin`。 | `same-origin` |
| `Cross-Origin-Opener-Policy`（COOP） | 跨域窗口交互（Spectre 等） | 控制顶级浏览上下文组。`same-origin`（独立进程组）、`same-origin-allow-popups`。 | `same-origin` |
| `Cross-Origin-Embedder-Policy`（COEP） | 跨域资源嵌入（需 COOP 配合） | `require-corp` 要求所有跨域资源显式允许（通过 CORP 或 CORS）。启用后 `SharedArrayBuffer` 等 API 才可用。 | `require-corp` |

**⑩ 其他**

| 头部 | 说明 | 示例 |
|------|------|------|
| `Allow` | 告诉客户端此资源允许哪些 HTTP 方法。与 405 Method Not Allowed 配合使用。 | `Allow: GET, HEAD, OPTIONS` |
| `Accept-Ranges` | 声明支持部分请求：`bytes` 表示支持断点续传。`none` 表示不支持。 | `Accept-Ranges: bytes` |
| `Alt-Svc` | 告知客户端有其他可用服务端点（支持升级 HTTP 版本），可指定 h2/h3 及端口。 | `Alt-Svc: h3=":443"; ma=86400` |
| `Link` | 表达资源间的关系（RFC 8288）。`rel=preload` 用于资源预加载提示。`rel=dns-prefetch`、`rel=stylesheet` 等。 | `Link: </style.css>; rel=preload; as=style` |
| `Timing-Allow-Origin` | 控制哪些源可通过 Resource Timing API 读取完整的资源加载计时。 | `Timing-Allow-Origin: *` |
| `Server-Timing` | 将服务器端性能指标传递给浏览器（PerformanceServerTiming API）。 | `Server-Timing: db; dur=53, cache; dur=12` |
| `X-Robots-Tag` | 页面级别的搜索引擎爬虫指令（等同 `<meta name="robots">` 但更通用）。 | `X-Robots-Tag: noindex, nofollow` |
| `X-Powered-By` | 服务器框架/语言标识（如 `Express`、`PHP/7.4`）。安全建议：关闭，避免泄露技术栈。 | `X-Powered-By: Express` |
| `Access-Control-Request-Method` | 预检请求中（OPTIONS），客户端告知实际请求将使用的方法。 | `Access-Control-Request-Method: POST` |
| `Access-Control-Request-Headers` | 预检请求中，客户端告知实际请求将使用的自定义头部。 | `Access-Control-Request-Headers: Authorization` |

#### 响应头部排列约定（非强制）

工程实践中常见的排列次序（首先基本信息，然后内容描述，然后缓存，最后安全策略）：

```
1. Date                    （生成时间，最先，便于计算 Age）
2. Server                  （软件版本）
3. Content-Type / Content-Length / Content-Encoding / Content-Language  （响应体描述）
4. Cache-Control / Expires / ETag / Last-Modified / Vary / Age  （缓存策略）
5. Location / Refresh      （重定向，仅 3xx）
6. Set-Cookie              （会话状态）
7. WWW-Authenticate / Proxy-Authenticate  （认证）
8. Access-Control-Allow-*  （CORS）
9. CSP / HSTS / X-Frame-Options / X-Content-Type-Options / Referrer-Policy / Permissions-Policy  （安全策略）
10. Alt-Svc                （协议升级提示）
11. Connection / Keep-Alive  （连接控制）
```

> 服务器/框架通常按自身内部顺序输出头部，不应假设任何特定顺序。

### 3.3 HTTP 状态码

#### 1xx 信息

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `100 Continue` | 继续发送 | 服务器已收到请求头，客户端应继续发送请求体（配合 Expect 头） |
| `101 Switching Protocols` | 协议切换 | 服务器同意升级协议（如 HTTP → WebSocket） |
| `102 Processing` | 处理中 | WebDAV，服务器正在处理耗时请求，防止超时断开 |
| `103 Early Hints` | 预提示 | 在最终响应前发送关键资源链接（Link 头），浏览器可提前预加载 |

#### 2xx 成功

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `200 OK` | 成功 | GET/PUT 成功，或 POST 的响应体包含处理结果 |
| `201 Created` | 已创建 | POST/PUT 成功创建资源，通常 `Location` 头指向新资源 URL |
| `202 Accepted` | 已接受 | 请求已接受但尚未处理（异步任务），响应体应描述处理状态和检查端点 |
| `203 Non-Authoritative Information` | 非权威信息 | 响应来自缓存或第三方，而非源服务器 |
| `204 No Content` | 无内容 | 成功但无响应体（DELETE 后常见），浏览器不刷新页面 |
| `205 Reset Content` | 重置内容 | 成功，要求客户端重置表单（清空输入） |
| `206 Partial Content` | 部分内容 | 响应 `Range` 请求，返回指定字节范围的内容 |

#### 3xx 重定向

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `300 Multiple Choices` | 多选 | 一个 URL 对应多个资源（极少使用） |
| `301 Moved Permanently` | 永久重定向 | 浏览器缓存重定向地址，后续请求直接跳转。搜索引擎将索引权重转移到新 URL |
| `302 Found` | 临时重定向 | 每次请求仍访问原 URL。**注意：历史原因，部分浏览器将 302 按 303 处理（改方法为 GET）** |
| `303 See Other` | 查看其他 | 明确要求使用 GET 请求重定向目标（即使原请求是 POST） |
| `304 Not Modified` | 未修改 | 条件请求命中，缓存有效，不返回响应体。**隐式重定向到缓存** |
| `307 Temporary Redirect` | 临时重定向 | 与 302 不同：**严格保持原方法和请求体**（POST 仍为 POST） |
| `308 Permanent Redirect` | 永久重定向 | 与 301 不同：**严格保持原方法和请求体** |
| `304` / `307` / `308` | — | `304` 适用缓存场景；`307/308` 是关键的安全改进（防止方法被意外改为 GET） |

#### 4xx 客户端错误

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `400 Bad Request` | 请求错误 | 服务器无法理解请求（格式错误、损坏的 JSON） |
| `401 Unauthorized` | 需认证 | 缺少或无效的认证凭据，须配合 `WWW-Authenticate` 头 |
| `402 Payment Required` | 需付费 | 保留状态码，极少使用（未来可能用于数字支付场景） |
| `403 Forbidden` | 禁止访问 | 认证通过但无权限。与 401 的区别：再登录也没用，需要更高权限 |
| `404 Not Found` | 未找到 | 路径不存在，或有意隐藏资源存在性 |
| `405 Method Not Allowed` | 方法不允许 | 对应 URL 不支持该 HTTP 方法，需返回 `Allow` 头 |
| `406 Not Acceptable` | 无法接受 | 服务器无法生成满足 Accept 头部要求的内容类型 |
| `407 Proxy Authentication Required` | 代理认证 | 须先通过代理服务器的认证（类似 401 但是代理级别） |
| `408 Request Timeout` | 请求超时 | 客户端发送请求耗时过长，服务器断开连接 |
| `409 Conflict` | 冲突 | 请求与资源当前状态冲突（如并发修改导致版本不匹配） |
| `410 Gone` | 已消失 | 资源永久删除，不会恢复。与 404 的区别：明知资源曾经存在但已删除 |
| `411 Length Required` | 需 Content-Length | 服务器要求请求必须有 `Content-Length` 头 |
| `412 Precondition Failed` | 前提条件失败 | 条件请求中的 `If-Match`/`If-Unmodified-Since` 等条件不满足 |
| `413 Payload Too Large` | 负载过大 | 请求体超过服务器允许的最大大小 |
| `414 URI Too Long` | URI 过长 | URL 超过服务器限制（通常因过多查询参数导致） |
| `415 Unsupported Media Type` | 不支持的媒体类型 | 请求体的 Content-Type 服务器无法处理 |
| `416 Range Not Satisfiable` | 范围无法满足 | `Range` 头指定的范围超出资源大小 |
| `417 Expectation Failed` | 期望失败 | `Expect` 头的要求服务器无法满足 |
| `418 I'm a teapot` | 我是茶壶 | RFC 2324 愚人节 RFC（HTCPCP 协议），被保留用于反自动化测试 |
| `421 Misdirected Request` | 请求误导 | 请求发到了无法生成响应的服务器（HTTP/2 中连接复用时） |
| `422 Unprocessable Entity` | 无法处理的实体 | 请求体语义正确但内容有问题（如必填字段缺失、格式校验失败） |
| `423 Locked` | 已锁定 | 资源被 WebDAV 锁锁定 |
| `424 Failed Dependency` | 依赖失败 | 当前请求依赖的其他请求失败 |
| `425 Too Early` | 过早 | 服务器拒绝可能重放的请求（0-RTT 首次使用） |
| `426 Upgrade Required` | 需升级 | 服务器要求客户端升级到更高版本的协议 |
| `428 Precondition Required` | 需要前提条件 | 要求使用条件请求（防丢失更新）。服务器要求客户端发送 `If-Match` |
| `429 Too Many Requests` | 请求过多 | 触发限速，须配合 `Retry-After` 头告知等待时间 |
| `431 Request Header Fields Too Large` | 头部过大 | 请求头（单个或总计）超过服务器限制 |
| `451 Unavailable For Legal Reasons` | 法律原因不可用 | 因政府/法律要求而屏蔽（如版权投诉） |

#### 5xx 服务器错误

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `500 Internal Server Error` | 服务器内部错误 | 未分类的服务器异常（代码崩溃、未捕获异常） |
| `501 Not Implemented` | 未实现 | 服务器不支持请求的方法或功能 |
| `502 Bad Gateway` | 网关错误 | 网关/代理从上游服务器收到无效响应 |
| `503 Service Unavailable` | 服务不可用 | 服务器临时过载或维护中，应配合 `Retry-After` 头 |
| `504 Gateway Timeout` | 网关超时 | 网关/代理等待上游服务器响应超时 |
| `505 HTTP Version Not Supported` | 版本不支持 | 不支持的 HTTP 版本 |
| `506 Variant Also Negotiates` | 变体也协商 | 透明内容协商配置错误导致循环 |
| `507 Insufficient Storage` | 存储不足 | WebDAV，服务器空间不足 |
| `508 Loop Detected` | 检测到循环 | WebDAV，请求处理过程中检测到无限循环 |
| `510 Not Extended` | 未扩展 | 请求缺少服务器要求的扩展 |
| `511 Network Authentication Required` | 需要网络认证 | 客户端需先登录网络（如 Wi-Fi 认证门户） |

---

## 四、HTTP 攻击面

### 4.1 请求方法滥用

| 方法 | 风险 | 利用场景 |
|------|------|----------|
| `GET` | 参数暴露在 URL | 浏览器历史/代理/服务器日志泄露敏感参数（密码、Token） |
| `POST` | CSRF 载体 | 伪造跨站请求（转账、改密），浏览器自动带 Cookie |
| `PUT` | 文件上传 | 配置不当可将任意内容写入服务器（Webshell） |
| `DELETE` | 资源删除 | 配置不当可删除关键文件 |
| `PATCH` | 属性篡改 | 修改用户角色、订单金额等敏感字段 |
| `TRACE` | XST（跨站追踪） | 回显请求内容，配合 XSS 可窃取 HttpOnly Cookie |
| `OPTIONS` | 信息泄露 | 通过 `Allow` 头暴露支持的方法，辅助攻击 |
| `CONNECT` | 隧道滥用 | 代理配置不当可用于访问内部网络 |

### 4.2 头部篡改攻击

| 头部 | 攻击方式 | 防护 |
|------|----------|------|
| `Cookie` | 篡改会话 ID（越权）、注入恶意值（如修改 `role=admin`） | 服务端 Session、签名 Cookie（JWT/HS256） |
| `Referer` / `Origin` | 删除或伪造 Referer 绕过 CSRF 防护 | 同时校验 Origin 和 CSRF Token |
| `User-Agent` | 伪造成搜索引擎爬虫（`Googlebot`）绕过访问控制和 WAF | 反向 DNS 验证爬虫 IP |
| `X-Forwarded-For` | 伪造 IP 绕过 IP 白名单和速率限制 | 仅信任可信代理设置的值，配置 `real_ip_header` |
| `Host` | 修改 Host 头进行虚拟主机投毒（SSRF、密码重置投毒） | 白名单校验 Host，防御性禁用绝对 URI |
| `Content-Length` | 与 `Transfer-Encoding` 配合进行 HTTP 走私 | 统一前端/后端协议解析，使用 HTTP/2 消除走私 |
| `Content-Type` | 发送 `application/json` 的 XSS Payload 或文件上传绕过 | 严格校验 Content-Type 且不依赖它做安全决策 |

### 4.3 协议层攻击

**HTTP 请求走私（HTTP Request Smuggling）**

成因：前端代理（CDN/负载均衡）和后端服务器对 `Content-Length`（CL）和 `Transfer-Encoding`（TE）的解析优先级不同。

三种变体：
- **CL.TE**：前端信任 CL，后端信任 TE。攻击者在 TE chunked 中隐藏第二个请求。
- **TE.CL**：前端信任 TE，后端信任 CL。攻击者在 CL 中设小值截断，其余部分成为新请求。
- **TE.TE**：前后端都信任 TE，但攻击者构造混淆的 Transfer-Encoding 值（如 `Transfer-Encoding: xchunked`）使一方不解析。

后果：绕过 WAF/访问控制、劫持其他用户请求、缓存投毒。

**HTTP 参数污染（HPP）**

提交重复参数，不同后端解析方式不同：

```
GET /search?q=foo&q=bar
```

- PHP/Apache：取最后一个 `bar`
- Java/Tomcat：取第一个 `foo`
- .NET/IIS：合并为数组 `foo, bar`
- 某些 WAF：只检查第一个，后端用最后一个 → 绕过

**编码混淆**

| 技术 | 原始 | 编码后 | 利用效果 |
|------|------|--------|----------|
| 空字节注入 | `../../` | `%00` 截断 | 截断文件路径或字符串（老 PHP `<5.3.4`） |
| CRLF 注入 | `\r\n` | `%0d%0a` | 注入响应头（HTTP 响应拆分）、日志污染 |
| 双重 URL 编码 | `../` | `%252e%252e%252f` | 绕过仅做一次 URL 解码的 WAF |
| Unicode 规范化 | `/` | `%C0%AF` | 超长 UTF-8 编码绕过路径检查 |

### 4.4 会话管理攻击

| 攻击类型 | 方式 | 防护 |
|----------|------|------|
| 会话固定 | 诱导用户使用攻击者预设的 Session ID | 登录后生成新 SessionID |
| 会话劫持 | XSS/网络嗅探窃取有效 SessionID | HttpOnly + Secure + SameSite + 短有效期 |
| 越权访问 | 修改 Cookie 中的用户标识（`user_id=1` → `user_id=2`） | 服务端 Session，不信任客户端传来的身份标识 |
| CSRF | 跨站请求携带自动附带的 Cookie | SameSite Cookie + CSRF Token + Origin/Referer 校验 |
| 会话超时不足 | 用户未退出，攻击者获得设备访问权 | 短有效期 + 滑动过期 + 登出强制失效 |

---

# HTTPS

HTTPS = HTTP + TLS（Transport Layer Security），在 HTTP 和 TCP 之间加入 TLS 层，提供：
- **加密性**：内容加密，中间人无法读取
- **完整性**：检测数据是否被篡改
- **身份认证**：通过证书验证服务器身份（及可选的客户端证书认证）

HTTPS 默认端口 443（HTTP 默认 80）。

---

## 一、TLS 基础

### 1.1 协议层次

```
应用层    HTTP / HTTP/2
          ↑
表示层    │  ─── 实际上 TLS 在 OSI 模型中
会话层    TLS    介于会话层和传输层之间
          ↓
传输层    TCP（或 QUIC 用于 HTTP/3）
网络层    IP
```

### 1.2 TLS 版本演进

| 版本 | 年份 | 状态 | 说明 |
|------|------|------|------|
| SSL 1.0 | — | 从未发布 | 内部 Netscape 开发版本 |
| SSL 2.0 | 1995 | 2011 年废弃 | 严重安全缺陷（MD5、无握手完整性验证） |
| SSL 3.0 | 1996 | 2015 年废弃 | POODLE 攻击，禁用 |
| TLS 1.0 | 1999 | 2020 年废弃 | 等同于 SSL 3.1，支持 CBC（BEAST 攻击），PCI 标准禁用 |
| TLS 1.1 | 2006 | 2020 年废弃 | 改进 IV 处理、支持 AEAD |
| TLS 1.2 | 2008 | 当前主流 | AEAD 加密（GCM、CCM）、SHA-256、灵活密码套件协商 |
| TLS 1.3 | 2018 | 推荐使用 | 1-RTT 握手（0-RTT 可选）、移除弱算法、前向安全性强制、加密更多握手消息 |

### 1.3 加密套件（Cipher Suite）

加密套件定义了一组算法，TLS 1.2 格式（完整示例）：

```
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
   │     │        │         │       │
   │     │        │         │       └─ HMAC/PRF（SHA-256）
   │     │        │         └───────── 对称加密算法（AES-128-GCM，AEAD）
   │     │        └─────────────────── 认证算法（RSA 签名）
   │     └──────────────────────────── 密钥交换算法（ECDHE = 椭圆曲线临时 DH）
   └────────────────────────────────── 协议标识
```

TLS 1.3 简化格式：

```
TLS_AES_128_GCM_SHA256
    │         │       │
    │         │       └─ HKDF 哈希（SHA-256）
    │         └───────── AEAD 加密算法（AES-128-GCM）
    └─────────────────── 协议标识
```

TLS 1.3 去掉了密钥交换算法和认证算法的选项——密钥交换固定为 (EC)DHE（强制前向安全），认证在 Certificate 消息中单独指定。

---

## 二、TLS 握手详解

### 2.1 TLS 1.2 完整握手（2-RTT）

```
客户端                                           服务器
  |                                               |
  |—— ① ClientHello ───────────────────────────→|  （明文）
  |   支持的 TLS 版本、密码套件列表               |
  |   随机数（Client Random）                      |
  |   扩展（SNI, ALPN, 签名算法等）                |
  |                                               |
  |←─ ② ServerHello ────────────────────────────|  （明文）
  |                    选定的密码套件、TLS 版本    |
  |                    随机数（Server Random）      |
  |                    扩展（确认 ALPN 等）         |
  |                                               |
  |←─ ③ Certificate ────────────────────────────|  （明文）
  |                    服务器证书链                 |
  |                    （X.509，含公钥和 CA 签名）   |
  |                                               |
  |←─ ④ ServerKeyExchange ──────────────────────|  （明文）
  |                    ECDHE 公钥参数 + 数字签名    |
  |                    （RSA 密钥交换时无此步骤）    |
  |                                               |
  |←─ ⑤ ServerHelloDone ────────────────────────|  （明文）
  |                                               |
  |—— ⑥ ClientKeyExchange ─────────────────────→|  （明文/加密）
  |    客户端 ECDHE 公钥参数（至此双方计算出预主密钥）|
  |    或：用服务器 RSA 公钥加密的预主密钥            |
  |                                               |
  |—— ⑦ ChangeCipherSpec ──────────────────────→|  （标记）
  |    通知服务器：之后的消息用协商密钥加密            |
  |                                               |
  |—— ⑧ Finished（加密）─────────────────────────→|  （加密）
  |    握手消息的 MAC（验证握手未被篡改）             |
  |                                               |
  |←─ ⑨ ChangeCipherSpec ────────────────────────|  （标记）
  |                    同样通知客户端                |
  |                                               |
  |←─ ⑩ Finished（加密）──────────────────────────|  （加密）
  |                    握手消息的 MAC                |
  |                                               |
  |==== 应用数据（对称加密传输）=====================|
```

密钥计算过程（简化）：

```
预主密钥（Pre-Master Secret）
  ↓  + Client Random + Server Random → PRF
主密钥（Master Secret，48 字节）
  ↓  + Client Random + Server Random → PRF
会话密钥（Session Keys）
  ├─ 客户端写密钥（Client Write Key）
  ├─ 服务器写密钥（Server Write Key）
  ├─ 客户端写 MAC 密钥（非 AEAD 时使用）
  └─ 服务器写 MAC 密钥（非 AEAD 时使用）
```

PRF（Pseudo-Random Function）为伪随机函数，TLS 1.2 使用 HMAC-SHA256 构建。

### 2.2 TLS 1.3 握手机制（1-RTT）

TLS 1.3 大幅精简握手：

```
客户端                                           服务器
  |                                               |
  |—— ① ClientHello ───────────────────────────→|
  |    支持的密码套件、密钥交换参数（一次性发送）    |
  |    (DHE/ECDHE 公钥+算法猜测）、SNI              |
  |                                               |
  |←─ ② ServerHello + EncryptedExtensions ──────|
  |    选定套件、服务器密钥交换参数                  |
  |    + Certificate + CertificateVerify         |
  |    + Finished                                  |
  |    （服务器一次性发送，Certificate 之后均为加密） |
  |                                               |
  |—— ③ Finished ──────────────────────────────→|
  |    （客户端收到证书和密钥参数后，立即发送完成）    |
  |                                               |
  |==== 应用数据 =================================|
```

**关键变化：**
- 服务器在 ServerHello 后立即发送加密数据，而非等客户端先发 Finished
- 握手仅 1-RTT（往返时延），相比 TLS 1.2 减少一半
- 几乎所有握手消息都是加密的（TLS 1.2 中大部分是明文）
- Certificate 和 CertificateVerify 均为服务器到客户端的加密消息

### 2.3 0-RTT 恢复握手机制

TLS 1.3 支持 0-RTT（零往返），适用于已建立过连接的客户端：

```
客户端                                           服务器
  |                                               |
  |—— ① ClientHello（含 PSK 扩展）                 |
  |    + 0-RTT 应用数据 ──────────────────────────→|  ← 第一条消息就带数据！
  |                                               |
  |←─ ② ServerHello（PSK 确认）                    |
  |    + EncryptedExtensions                      |
  |    + Finished ────────────────────────────────|
  |                                               |
  |==== 应用数据 =================================|
```

代价：0-RTT 数据不可重放保护（服务器可配置拒绝或缓存检验）。

### 2.4 会话恢复（Session Resumption）

避免每次完整握手，有两种机制：

**Session ID**（TLS 1.2）
- 首次握手服务器返回 Session ID
- 客户端在 ClientHello 中带 Session ID
- 服务器从缓存中查找对应的会话密钥
- 缺点：服务器需维护会话缓存（不适合分布式环境）

**Session Ticket**（TLS 1.2 / 1.3）
- 服务器生成加密的 Session Ticket，发送给客户端
- 客户端在 ClientHello 中携带 Ticket
- 服务器解密 Ticket 恢复会话密钥（无需本地缓存）
- TLS 1.3 中通过 PSK（Pre-Shared Key）实现

---

## 三、证书与 PKI 体系

### 3.1 X.509 证书结构

X.509 v3 标准定义了数字证书的格式。证书内容：

| 字段 | 说明 | 示例 |
|------|------|------|
| **版本** | v3（当前标准） | `Version: 3` |
| **序列号** | CA 分配的唯一标识 | `Serial Number: 0a:1b:2c:...` |
| **签名算法** | 证书签名的算法 | `sha256WithRSAEncryption` |
| **颁发者**（Issuer） | 签发此证书的 CA 的 DN（识别名称） | `CN = Let's Encrypt, O = Internet Security Research Group` |
| **有效期** | Not Before / Not After | `2026-01-01 ~ 2027-01-01` |
| **主体**（Subject） | 证书持有者的 DN | `CN = www.example.com` |
| **主体公钥** | 公钥 + 算法 | `RSA 2048 bit` 或 `EC secp256r1` |
| **扩展**（SAN 等） | 域名、IP、用途约束等 | `DNS:www.example.com, DNS:example.com` |
| **签名** | CA 用私钥对上述字段的签名 | `Signature: 30:45:02:...` |

### 3.2 证书链验证

```
根 CA 证书（自签名）
  └─ 信任锚：预置在操作系统 / 浏览器 / TLS 库中
  └─ 私钥通常离线存储

  ↓ 签发

中间 CA 证书
  └─ 由根 CA 签名
  └─ 日常签发操作使用

  ↓ 签发

站点证书（末端实体证书）
  └─ 由中间 CA 签名
  └─ 安装到 Web 服务器
```

**验证过程：**
1. 验证站点证书：检查颁发者签名是否匹配中间 CA 的公钥
2. 验证中间 CA 证书：检查颁发者签名是否匹配根 CA 的公钥
3. 直到到达信任锚（根 CA）
4. 同时检查：证书未过期、域名匹配 SAN（Subject Alternative Name）、未被吊销（OCSP/CRL）、用途正确（Extended Key Usage）

### 3.3 证书透明（Certificate Transparency, CT）

Google 推动的体系，防止 CA 恶意签发或错误签发证书：

- CA 签发证书时，必须将证书提交到公开的 CT 日志服务器
- 日志服务器返回 SCT（Signed Certificate Timestamp）
- SCT 嵌入在证书中（或通过 TLS 扩展/Ocsp Stapling 交付）
- 浏览器和监控服务定期扫描 CT 日志，发现未授权的证书

### 3.4 吊销机制

| 机制 | 说明 | 优缺点 |
|------|------|--------|
| **CRL** | CA 发布的证书吊销列表（巨大文件） | 需要定期下载整个列表，延迟高 |
| **OCSP** | 在线证书状态协议，客户端向 CA 查询特定证书 | 实时但暴露访问隐私（CA 知道你访问哪个站点） |
| **OCSP Stapling** | 服务器定期向 CA 获取 OCSP 响应，握手时随证书一同发送 | 隐私保护 + 低延迟，推荐使用 |
| **CRLite** | Firefox 的方案：将 CT 日志信息压缩为布隆过滤器，客户端本地检测 | 离线 + 隐私，Firefox 已部署 |

---

## 四、HTTPS 安全威胁与防御

### 4.1 攻击类型总览

| 攻击 | 机制 | 影响 | 防御 |
|------|------|------|------|
| **SSL 剥离** | 中间人拦截 HTTP→HTTPS 的 301 跳转，对客户端维持 HTTP 明文连接 | 完全解密流量 | HSTS 预加载 + `https://` 直接访问 |
| **降级攻击** | 中间人篡改 ClientHello 支持的版本/套件列表，强制使用弱算法 | 使用可破解的弱加密 | 服务端禁用旧版本（<TLS 1.2）+ 弱套件 |
| **伪造证书攻击** | 攻击者让客户端信任恶意 CA（或盗取 CA 私钥） | 任意域名冒充 | 证书固定（HPKP 已废弃，用 Expect-CT + CT 日志监控） |
| **中间人代理** | 合法 CA 签发的透明代理证书（企业安全产品），解密后检查再重新加密 | 流量被第三方解密 | 企业环境中是预期的；非企业环境需用户警觉 |
| **重放攻击** | 记录加密流量后在非原始上下文中重放 | 重复执行幂等操作 | TLS 序列号 + 0-RTT 不可用于非幂等请求 |
| **协议降级（POODLE）** | 浏览器失败后回退到 SSL 3.0 | padding oracle 逐步猜测明文 | 彻底禁用 SSL 3.0（2014 年） |
| **BEAST** | 预测 CBC 模式的 IV 实现明文恢复 | 解密 HTTPS Cookie | 使用 AEAD（GCM/CCM）或 TLS 1.1+ 的显式 IV |
| **Lucky13** | Timing 侧信道利用 CBC padding 检查 | 逐步解密 | AEAD 算法或常数时间 HMAC 实现 |
| **CRIME/BREACH** | 利用 HTTP 压缩率测量推断明文（压缩后更小 = 猜测正确） | 泄露 CSRF Token、Cookie | 禁用 HTTP 压缩 / 跨域隔离（SameSite Cookie）/ CSRF Token 随机化长度 |
| **心脏滴血** | OpenSSL heartbeat 扩展实现缺陷，可读取服务器内存（CVE-2014-0160） | 泄露私钥、会话、密码 | 及时更新 OpenSSL |
| **ROBOT** | RSA PKCS#1 v1.5 padding 的 Bleichenbacher oracle | 解密/签名 | 禁用 RSA 密钥交换（用 ECDHE） |
| **DROWN** | 支持 SSLv2 的服务器使用相同密钥对，解密 TLS 流量 | 解密会话 | 禁用 SSLv2，不同服务不同密钥对 |
| **Logjam** | 降级到 512 位 DH，预计算破解 | 解密会话 | 使用 ≥2048 位 DH 或 ECDHE |

### 4.2 TLS 1.3 的安全改进

TLS 1.3 从设计上消除了大量历史问题：

- **移除所有弱算法**：无 RC4、无 CBC 模式、无 SHA-1、无静态 RSA/静态 DH 密钥交换
- **强制前向安全**：所有密钥交换必须是 (EC)DHE（临时密钥），即使长期私钥泄露历史通信也不被解密
- **加密握手**：ServerHello 后的所有握手消息均加密，减少信息泄露
- **精简握手状态机**：移除不必要的协商步骤，减少攻击面
- **0-RTT 安全性**：0-RTT 数据附带 PSK，服务器必须显式选择接受

### 4.3 部署加固清单

**服务端配置要点（以 Nginx 为例）：**

```nginx
# 协议版本：仅 TLS 1.2 和 1.3
ssl_protocols TLSv1.2 TLSv1.3;

# 密码套件：TLS 1.2 仅强套件（AEAD + 前向安全）
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:
            ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:
            ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;

# 服务器偏好密码套件（而非客户端偏好）
ssl_prefer_server_ciphers on;

# 会话票证：开启（有前向安全保护）
ssl_session_tickets on;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;

# DH 参数（TLS 1.2 中非 ECDHE 的 DH 密钥交换）
ssl_dhparam /etc/ssl/dhparam.pem;  # 2048 位及以上

# 证书和密钥
ssl_certificate     /etc/ssl/certs/example.com.pem;
ssl_certificate_key /etc/ssl/private/example.com.key;
```

---

## 五、HTTPS 响应头安全配置

这些头部必须出现在 HTTPS 响应中，HTTP 响应中即便发送也不会被浏览器执行（如 HSTS）。

### 5.1 HSTS（HTTP Strict Transport Security）

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

工作机制：
1. 浏览器首次通过 HTTPS 访问站点，收到 HSTS 头
2. 在 `max-age` 指定时间内，该域名的所有 HTTP 请求都会被浏览器自动转为 HTTPS（内部 307 重定向），不从网络发送 HTTP 请求
3. `includeSubDomains`：覆盖所有子域
4. `preload`：提交到浏览器内置的 HSTS 预加载列表（即使从未访问过也会强制 HTTPS）

限制与风险：
- 首次访问前的 TOFU（Trust On First Use）窗口期仍然脆弱；`preload` 彻底消除
- 证书失效时网站完全无法访问（用户无绕过选项）——必须确保证书续期自动化（Let's Encrypt + Certbot）
- `max-age` 设得过小则保护时间太短；建议至少一年（31536000）

### 5.2 CSP（Content-Security-Policy）

CSP 是防御 XSS 的最核心头部，通过白名单限制浏览器可执行的资源来源。

```http
Content-Security-Policy:
    default-src 'self';
    script-src 'self' 'nonce-r4nd0m123' 'strict-dynamic';
    style-src 'self' 'unsafe-inline';
    img-src 'self' https: data:;
    connect-src 'self' https://api.example.com;
    frame-ancestors 'self';
    form-action 'self';
    base-uri 'self';
    upgrade-insecure-requests;
    block-all-mixed-content;
```

关键指令说明：
- `default-src 'self'`：基准策略，只加载同源资源
- `script-src 'nonce-...'`：仅执行携带匹配 nonce 属性的 `<script>`（每次响应 nonce 随机生成）
- `'strict-dynamic'`：信任 nonce 脚本动态创建的脚本（无需重复指定 CDN 域名）
- `frame-ancestors`：替代 `X-Frame-Options`（优先级更高），控制嵌入来源
- `form-action`：限制表单提交目标
- `base-uri`：限制 `<base>` 标签（防止窃取相对路径资源）
- `upgrade-insecure-requests`：自动将 HTTP 资源引用升级为 HTTPS
- `report-uri` / `report-to`：指定 CSP 违规报告的端点（旧/新语法）
- `block-all-mixed-content`：彻底阻止混合内容加载

CSP 常见误区：
- `script-src 'unsafe-inline'` 完全禁用 CSP 的内联脚本保护——几乎等于未配置
- 同时存在 `Content-Security-Policy` 和 `Content-Security-Policy-Report-Only` 时，前者强制执行，后者仅报告

### 5.3 其他核心安全头

```http
# 防止 MIME 类型嗅探（必须置位）
X-Content-Type-Options: nosniff

# 防止点击劫持
X-Frame-Options: DENY
# 或
Content-Security-Policy: frame-ancestors 'none'

# 控制 Referer 信息泄露
Referrer-Policy: strict-origin-when-cross-origin

# 控制浏览器功能权限
Permissions-Policy: camera=(), microphone=(), geolocation=(self), payment=()

# 清除站点数据（登出时发送）
Clear-Site-Data: "cache", "cookies", "storage"

# 跨域隔离（配合 COEP 使用）
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

---

## 六、HTTPS 实战

### 6.1 信息收集命令

```bash
# 完整响应头
curl -I https://example.com

# 详细握手过程（含 TLS 协商和证书）
curl -v https://example.com

# 仅查看 TLS 握手细节
curl -w '\nTLS version: %{ssl_verify_result}\n' -so /dev/null https://example.com

# 查看证书完整信息
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -text

# 仅查看证书有效期和主题
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -dates -subject -issuer

# 查看证书 SAN（Subject Alternative Names）
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -ext subjectAltName

# 枚举服务器支持的加密套件
nmap --script ssl-enum-ciphers -p 443 example.com

# 测试 TLS 版本支持
testssl.sh https://example.com

# 查看 HSTS
curl -sI https://example.com | grep -i strict
```

### 6.2 检查清单

1. 响应头安全审核：`curl -I https://target.com` 检查 CSP、HSTS、X-Frame-Options、X-Content-Type-Options、Referrer-Policy、Permissions-Policy 是否配置
2. 证书验证：域名匹配、未过期、SAN 正确、证书链完整、OCSP Stapling 启用
3. 加密配置：仅支持 TLS 1.2+、禁用弱套件（RC4、CBC 模式、导出套件）、启用前向安全
4. 混合内容：HTTPS 页面是否加载了 HTTP 资源（JS/CSS/图片）——浏览器控制台会警告
5. Cookie 安全：`Secure`、`HttpOnly`、`SameSite` 属性齐全
6. HSTS：`max-age` 足够长、是否启用 `includeSubDomains` 和 `preload`
7. 用 Burp Suite Repeater 修改请求头（Host、XFF、Origin）测试，观察响应变化
8. 测试 TRACE 方法是否启用：`curl -X TRACE -v http://target.com`
9. 测试 OPTIONS 方法泄露的信息：`curl -X OPTIONS -v http://target.com`
10. 对于已部署的 HSTS，确认 `http://` 版本完全不可访问（无 HTTP 到 HTTPS 的首次明文跳转）

---

> **核心原则：HTTP 定义了 Web 通信的语言；HTTPS 保证了这语言在不可信网络上的安全传递。理解协议，才能理解攻击与防御。**

> **相关文档**：[CVE模板](../CVE_TEMPLATE.md) · [CURL工具](../Tools/curl.md)
