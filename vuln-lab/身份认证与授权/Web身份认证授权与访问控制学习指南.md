# Web 身份认证、授权与访问控制学习指南

## 文档定位

本文面向正在学习 Web 安全、渗透测试和安全服务的读者，系统梳理以下问题：

- HTTP 为什么无状态，以及 Cookie、Session、JWT 分别解决什么问题
- 认证、授权、会话管理和访问控制之间的边界
- OAuth 2.0 的四大角色与 Authorization Code + PKCE 完整流程
- OAuth、OIDC、Access Token、ID Token、Refresh Token 如何配合
- 如何在自建实验环境中使用 Burp Suite 逐包分析认证授权流程
- RBAC、ABAC、ACL、ReBAC 和 OAuth Scope 的关系
- OWASP Top 10 A01 失效的访问控制与上述技术的关系
- 如何从渗透测试角度定位水平越权、垂直越权、IDOR/BOLA 和令牌类问题

文档中的测试示例只适用于自建靶场、明确获得授权的测试环境和公开教学平台。不要将真实用户的 Cookie、Token、密码或个人数据发送到第三方解析服务。

---

## 一、先建立正确的问题模型

Web 身份安全经常被概括成“登录”和“权限”，但实际至少包含五个层次：

```text
身份认证 Authentication
    ↓
会话建立 Session Establishment
    ↓
凭证传递 Credential Transport
    ↓
授权决策 Authorization Decision
    ↓
访问控制执行 Access Control Enforcement
```

可以用五个问题理解一次 API 请求：

1. 请求代表谁？
2. 请求携带的凭证由谁签发？
3. 凭证是否仍然有效，并且确实发给当前服务？
4. 这个主体是否拥有当前操作所需的权限？
5. 目标资源是否属于这个主体，当前资源状态是否允许该操作？

其中：

- “你是谁”是身份认证。
- “你能做什么”是授权。
- “服务端是否在每一个入口执行了授权策略”是访问控制。
- “凭证如何安全地保存、传输、过期和撤销”是会话与令牌管理。

最容易出现的错误是只完成了身份认证，却没有完成授权。例如，用户已经合法登录，JWT 签名也完全正确，但用户可以通过修改 `order_id` 读取别人的订单。这不是认证失败，而是对象级访问控制失败。

---

## 二、HTTP 无状态与会话管理

### 2.1 HTTP 无状态是什么意思

HTTP 协议本身不会自动记住请求之间的关系。下面两个请求在协议层面互相独立：

```http
GET /profile HTTP/1.1
Host: app.example
```

```http
GET /orders HTTP/1.1
Host: app.example
```

服务器不会因为第二个请求来自同一个 TCP 连接，就自动知道它属于同一个用户。应用需要额外携带某种凭证，或者通过服务端保存的状态建立关联。

HTTP 无状态并不等于应用不能有状态。状态可以由以下位置保存：

- 浏览器 Cookie
- 服务端内存
- Redis 等分布式缓存
- 数据库
- Access Token 或 JWT 中的声明

### 2.2 Cookie 是什么

Cookie 是浏览器保存的一小段数据，并在满足域名、路径、安全属性等条件时自动放入请求头：

```http
Cookie: session_id=opaque-random-value
```

Cookie 本身不等于认证，也不等于 Session。它只是一个传输和保存凭证的机制。Cookie 中可以放：

- Session ID
- 签名后的状态
- JWT
- CSRF Token
- 用户偏好

生产环境中，认证 Cookie 通常需要考虑：

| 属性 | 目的 |
|---|---|
| `Secure` | 只通过 HTTPS 发送 |
| `HttpOnly` | 限制 JavaScript 读取，降低部分 XSS 后果 |
| `SameSite` | 限制跨站请求自动携带 Cookie，降低 CSRF 风险 |
| `Domain` | 限制可接收 Cookie 的域名范围 |
| `Path` | 限制 Cookie 生效路径 |
| `Max-Age` 或 `Expires` | 控制有效期 |

这些属性不能替代服务端授权检查。一个用户拿着合法 Cookie，仍然不能访问其他用户的对象。

### 2.3 Session 是什么

经典的 Session 模型通常是：

```text
登录请求
    ↓
服务端验证账号密码
    ↓
服务端生成随机 Session ID
    ↓
服务端保存 Session ID → 用户身份、登录状态、过期时间
    ↓
通过 Set-Cookie 返回 Session ID
```

后续请求：

```text
浏览器携带 Session ID
    ↓
服务端查找 Session
    ↓
得到当前用户
    ↓
继续执行授权检查
```

Session 的状态存储不一定是数据库。高并发系统常使用 Redis 集群、内存缓存或专门的会话存储。数据库查询压力也可以通过缓存、连接池、分片和合理的会话设计缓解。

Session 的优点：

- 服务端可以立即撤销
- 服务端可以实时修改用户状态
- 客户端只保存不可预测的随机标识符
- 权限和会话状态不必暴露在客户端

Session 的问题：

- 分布式部署需要共享会话或会话粘滞
- 服务端需要维护状态
- 需要处理 Session Fixation、会话过期、并发登录和注销
- 每次请求可能涉及缓存或数据库读取

### 2.4 JWT 是什么

JWT 通常由三段组成：

```text
Base64Url(Header).Base64Url(Payload).Base64Url(Signature)
```

示意：

```json
Header:
{
  "alg": "RS256",
  "typ": "JWT"
}
```

```json
Payload:
{
  "iss": "https://auth.example",
  "sub": "user-123",
  "aud": "https://api.example",
  "scope": "orders.read",
  "exp": 1900000000
}
```

JWT 默认不是加密格式。Header 和 Payload 只是 Base64URL 编码，持有 Token 的人通常都能读取它们。签名的作用是：

- 防止 Header 和 Payload 被篡改
- 让验证方确认 Token 来自持有密钥的一方
- 让验证方检查 Token 是否完整

签名不提供以下能力：

- 不隐藏 Payload 内容
- 不阻止 Token 被复制后重放
- 不自动实现撤销
- 不自动保证权限声明是最新的
- 不自动保证 Token 面向当前 API

JWT 适合在验证方可以独立完成校验、并且能够接受有限撤销延迟的场景。对于需要强实时撤销、权限频繁变更或高敏感操作的场景，仍可能需要服务端状态查询、令牌版本号、Token Introspection 或额外的风险控制。

### 2.5 Cookie、Session、JWT 的关系

它们不是互相替代的同一层技术：

| 技术 | 所在层次 | 主要作用 |
|---|---|---|
| Cookie | 浏览器传输机制 | 保存并自动发送数据 |
| Session | 服务端会话模型 | 在服务端保存用户状态 |
| JWT | 令牌格式 | 在 Token 中携带可验证声明 |
| Redis/数据库 | 状态存储 | 保存会话、撤销信息或权限数据 |

实际系统可以组合使用：

- Cookie + Session
- Cookie + JWT
- Authorization Header + Opaque Token
- Authorization Header + JWT
- BFF 使用 HttpOnly Cookie，后端再使用 Access Token 调用 API

---

## 三、认证、授权、OAuth 与 OIDC

### 3.1 Authentication 与 Authorization

认证回答：

```text
你是谁？
```

常见认证因素：

- 你知道的东西：密码、PIN
- 你拥有的东西：手机、硬件密钥、证书
- 你本身的特征：指纹、人脸

授权回答：

```text
你能访问什么？能执行什么操作？
```

一个用户通过了认证，不代表他可以：

- 读取所有订单
- 修改别人的资料
- 调用管理员 API
- 跨租户访问数据
- 执行高风险操作

### 3.2 OAuth 2.0 解决什么问题

OAuth 2.0 解决的是授权委托：用户允许一个客户端在有限范围内访问资源，而不把资源服务的密码交给客户端。

例如：

```text
用户 → 授权服务器登录并同意
授权服务器 → 向客户端签发有限权限的 Token
客户端 → 使用 Token 访问资源服务器 API
```

OAuth 本身不规定用户如何登录，也不定义统一的用户信息格式。因此，“使用 OAuth 登录”通常还需要 OIDC。

### 3.3 OIDC 解决什么问题

OIDC 是建立在 OAuth 2.0 之上的身份认证协议。它主要增加：

- `openid` Scope
- ID Token
- UserInfo Endpoint
- `nonce` 等登录绑定机制
- 标准化的身份声明

简化理解：

```text
OAuth 2.0：允许客户端访问资源
OIDC：让客户端知道用户是谁
```

不要把 ID Token 当成 API Access Token。ID Token 发给客户端，Access Token 发给资源服务器使用，二者的受众和用途不同。

### 3.4 OAuth 2.1 的位置

OAuth 2.1 不应被理解成与 OAuth 2.0 完全不同的新体系。它更接近对 OAuth 2.0 使用方式和安全最佳实践的整理方向，重点强调：

- Authorization Code 优先
- 公共客户端使用 PKCE
- 不再推荐 Implicit Grant
- 不再推荐 ROPC
- 更严格地处理重定向、令牌和客户端安全

学习时应优先掌握 Authorization Code + PKCE，并结合 OAuth 安全最佳实践理解实现要求。

---

## 四、OAuth 2.0 四大角色

| 角色 | 含义 | 典型实例 |
|---|---|---|
| Resource Owner | 资源所有者 | 用户 |
| Client | 请求资源的应用 | Web 应用、移动 App、CLI |
| Authorization Server | 验证用户并签发 Token | 企业身份中心、Keycloak、某平台 OAuth 服务 |
| Resource Server | 保存资源并校验 Access Token 的 API | 订单 API、文件 API、用户资料 API |

四个角色可以由不同系统承担，也可以在同一家公司内由不同服务承担。

特别要区分：

- Authorization Server 负责签发 Token。
- Resource Server 负责保护 API 资源。
- Client 不应被默认视为可信。
- 用户密码应该只交给用户信任的 Authorization Server，而不是任意 Client。

---

## 五、Authorization Code + PKCE 完整流程

这是用户参与授权时最重要的标准流程。

### 5.1 客户端注册

在流程开始前，客户端通常需要在授权服务器注册：

- `client_id`
- 允许的 `redirect_uri`
- 客户端类型
- 支持的 Scope
- 对于保密客户端，配置客户端认证方式

重定向地址应尽量使用精确白名单。不要使用任意子路径、任意子域名或通配符替代严格校验。

### 5.2 客户端生成 PKCE 参数

客户端生成高熵随机字符串 `code_verifier`，再计算：

```text
code_challenge = BASE64URL(SHA256(code_verifier))
```

客户端只把 `code_challenge` 放进授权请求，稍后交换 Token 时再提交原始 `code_verifier`。

PKCE 的目的，是让截获授权码的其他实体无法单独使用它完成令牌交换。

### 5.3 发起授权请求

客户端通过浏览器跳转到 Authorization Server：

```http
GET /authorize?response_type=code&client_id=web-client&redirect_uri=https%3A%2F%2Fclient.example%2Foauth%2Fcallback&scope=openid%20orders.read&state=state-123&code_challenge=challenge-456&code_challenge_method=S256 HTTP/1.1
Host: auth.example
```

常见参数：

| 参数 | 作用 |
|---|---|
| `response_type=code` | 请求返回一次性授权码 |
| `client_id` | 标识客户端 |
| `redirect_uri` | 授权完成后的回调地址 |
| `scope` | 请求的权限范围 |
| `state` | 绑定浏览器会话，防止请求伪造 |
| `code_challenge` | PKCE 挑战值 |
| `nonce` | OIDC 中绑定登录请求与 ID Token |

### 5.4 授权服务器建立自己的会话

如果用户还没有登录，Authorization Server 会展示登录页面。用户的账号密码通常只提交给 Authorization Server。

登录成功后，Authorization Server 可能设置自己的 Cookie：

```http
Set-Cookie: as_session=server-side-session; Secure; HttpOnly; SameSite=Lax
```

这说明 OAuth 并没有消灭 Cookie 和 Session。它们仍然可以用于维护用户在授权服务器上的登录状态。

### 5.5 用户同意授权

授权服务器应展示客户端身份和请求的 Scope。用户同意后，授权服务器生成短时、一次性的 Authorization Code。

### 5.6 回调客户端

授权服务器重定向到注册好的回调地址：

```http
HTTP/1.1 302 Found
Location: https://client.example/oauth/callback?code=code-789&state=state-123
```

客户端必须校验返回的 `state` 与本地保存的值一致。校验失败时，不应继续交换 Token。

授权码不是 Access Token，通常具有以下特征：

- 有效期短
- 只能使用一次
- 与客户端、重定向地址和 PKCE 参数绑定
- 不应出现在日志、Referer、错误页面或公共监控数据中

### 5.7 客户端交换 Token

客户端向 Token Endpoint 发起服务端请求：

```http
POST /token HTTP/1.1
Host: auth.example
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=code-789&client_id=web-client&redirect_uri=https%3A%2F%2Fclient.example%2Foauth%2Fcallback&code_verifier=verifier-original
```

保密客户端还可能需要提供客户端认证信息。公共客户端不能把 `client_secret` 当成真正的秘密，因为移动 App 和浏览器代码都可以被用户查看或逆向。

Authorization Server 需要检查：

1. 授权码是否存在、未过期、未使用。
2. 授权码是否属于当前 `client_id`。
3. `redirect_uri` 是否与之前完全一致。
4. `code_verifier` 是否匹配 `code_challenge`。
5. 保密客户端的认证信息是否有效。
6. 用户和授权是否仍处于允许状态。

### 5.8 返回令牌

示意响应：

```json
{
  "access_token": "access-token-value",
  "token_type": "Bearer",
  "expires_in": 600,
  "refresh_token": "refresh-token-value",
  "id_token": "id-token-value",
  "scope": "openid orders.read"
}
```

Access Token 可以是 JWT，也可以是完全不透明的随机字符串。客户端不应假设所有 Access Token 都能本地解码。

### 5.9 调用资源服务器

```http
GET /api/orders HTTP/1.1
Host: api.example
Authorization: Bearer access-token-value
```

Resource Server 可以通过以下方式验证 Token：

- 本地验证 JWT 签名和声明
- 调用 Introspection Endpoint 查询不透明 Token 状态
- 通过 API Gateway 验证后，把可信身份上下文传给内部服务

无论采用哪种方式，资源服务器都必须继续执行业务授权，不能把“Token 有效”当成“所有操作都允许”。

### 5.10 刷新与轮换

Access Token 通常设置较短的有效期。过期后，客户端可以使用 Refresh Token 换取新的 Access Token。

更安全的 Refresh Token Rotation：

```text
Refresh Token A
    ↓
换取 Access Token B + Refresh Token C
    ↓
Refresh Token A 失效
```

如果服务端发现已经失效的旧 Refresh Token 再次出现，应考虑令牌被复制或重放，并撤销相关令牌族。

---

## 六、抓包分析方法

### 6.1 抓包前提

HTTPS 会加密网络内容。对于自建靶场，可以使用：

- 浏览器开发者工具 Network 面板
- Burp Suite 浏览器
- 在测试浏览器中安装 Burp CA 证书
- 服务端访问日志和授权服务器审计日志

不要在公共环境中拦截不属于自己的流量，也不要把真实 Token 粘贴到在线 JWT 解码站点。学习时应使用本地 Keycloak、测试账号和测试域名。

### 6.2 抓包观察顺序

建议按以下顺序标记请求：

```text
1. /authorize 请求
2. Authorization Server 登录请求
3. 同意页面提交
4. 带 code 的回调请求
5. /token 令牌交换请求
6. 带 Authorization 头的 API 请求
7. Refresh Token 请求
8. 注销、撤销或会话过期请求
```

每一步都记录：

- 请求方和接收方是谁
- 凭证出现在哪个位置
- 是否经过浏览器重定向
- 是否存在敏感数据泄露到 URL、日志或 Referer 的风险
- 当前安全边界由哪个组件负责

### 6.3 每个关键参数要问什么

| 参数或对象 | 分析问题 |
|---|---|
| `redirect_uri` | 是否精确匹配，是否可能被 Open Redirect 影响 |
| `state` | 是否随机、是否与浏览器会话绑定、是否校验 |
| `code_challenge` | 公共客户端是否使用 PKCE，是否使用 S256 |
| `code` | 是否一次性、短时、绑定客户端和回调地址 |
| `code_verifier` | 是否只在 Token Endpoint 提交，是否能阻止截获码重放 |
| `access_token` | 是否面向正确 API，是否短时，是否出现在安全位置 |
| `id_token` | 是否验证 `iss`、`aud`、`exp`、`nonce` |
| `scope` | 是否真的限制 API 能执行的操作 |
| `sub`、`user_id` | 是否被客户端参数覆盖，是否与服务端主体绑定 |
| `tenant_id` | 是否由服务端根据主体和资源关系决定 |

### 6.4 抓包分析的核心目标

抓包不是为了记住某个请求格式，而是为了回答三个问题：

```text
凭证在哪里产生？
凭证在哪里验证？
最终授权在哪里执行？
```

例如，Authorization Server 可能正确验证了用户并签发了 `orders.read`，但 Resource Server 只验证签名、不检查资源归属，仍然会产生 BOLA。

---

## 七、令牌验证与信任边界

### 7.1 JWT 验证不能只看签名

Resource Server 至少应验证：

| 声明 | 目的 |
|---|---|
| `iss` | 确认签发者是预期的 Authorization Server |
| `sub` | 确认主体标识 |
| `aud` | 确认 Token 是发给当前 API 的 |
| `exp` | 防止使用过期 Token |
| `nbf` | 防止提前使用尚未生效的 Token |
| `iat` | 判断签发时间和异常时钟问题 |
| `scope` | 检查委托权限范围 |
| `jti` | 支持追踪、撤销或重放检测 |

还应做到：

- 服务端显式配置允许的算法，不接受客户端随意指定算法
- 严格限制签名密钥来源和 `kid` 查找范围
- 对 JWKS 缓存、密钥轮换和未知密钥建立明确策略
- 不把 Payload 中的 `role`、`is_admin` 当成天然可信输入
- 明确区分 ID Token、Access Token 和其他业务 Token
- 对高风险操作增加实时权限查询、二次认证或风险控制

### 7.2 不透明 Token 并不天然更安全

不透明 Token 可以减少客户端看到的声明，也便于服务端撤销，但它通常需要 Introspection 或缓存查询。若资源服务器错误地把任意字符串映射为用户，或者网关与后端之间的身份上下文可被伪造，仍然会造成严重问题。

安全性取决于：

```text
生成方式 + 传输方式 + 验证方式 + 撤销方式 + 授权执行方式
```

而不是取决于 Token 是否叫 JWT。

---

## 八、权限模型

### 8.1 ACL

ACL 为每一个资源记录主体和权限：

```text
document-1001:
  alice: read, write
  bob: read
```

适合资源数量有限、权限需要精确到对象的场景。缺点是权限数据可能快速膨胀。

### 8.2 RBAC

RBAC 根据角色授予权限：

```text
customer → orders.read
operator  → orders.read, orders.write
admin     → orders.read, orders.write, users.manage
```

RBAC 易于理解和管理，但角色数量容易膨胀，且单纯角色无法表达“只能访问自己所属租户的数据”。

### 8.3 ABAC

ABAC 根据主体、资源、动作和环境属性进行决策：

```text
允许访问，当且仅当：
subject.tenant_id == resource.tenant_id
且 subject.id == resource.owner_id
且 action == read
且 resource.status != deleted
```

ABAC 表达能力强，适合复杂业务，但策略设计、测试和审计成本更高。

### 8.4 ReBAC

ReBAC 关注主体与资源之间的关系：

```text
alice 是 project-1 的 owner
bob 是 project-1 的 member
carol 与 project-1 无关系
```

它适合团队、组织、项目、共享文档和社交关系等场景。

### 8.5 OAuth Scope 的位置

Scope 通常描述客户端被委托的权限范围：

```text
orders.read
orders.write
profile.read
```

Scope 不是完整的业务授权模型。一个请求是否允许，通常至少还要考虑：

```text
Token 有效
→ Scope 满足
→ 用户角色满足
→ 租户一致
→ 资源属于用户或用户有关系权限
→ 当前状态允许该动作
```

不要用 Scope 代替所有对象级授权。

---

## 九、OWASP A01 与身份认证体系的关系

在 OWASP Top 10 2025 的语境下，A01“失效的访问控制”与本文主题高度相关，但它不等同于 OAuth 漏洞，也不等同于认证失败。

可以这样划分：

```text
身份认证：证明用户是谁
令牌管理：携带和验证认证上下文
授权策略：定义用户能做什么
访问控制：在每一个功能、对象和操作上执行策略
```

A01 通常发生在授权策略没有被正确执行的地方。

### 9.1 典型 BOLA/IDOR

Alice 请求自己的订单：

```http
GET /api/orders/1001 HTTP/1.1
Authorization: Bearer <alice-token>
```

把对象编号改成 Bob 的订单：

```http
GET /api/orders/1002 HTTP/1.1
Authorization: Bearer <alice-token>
```

如果服务端只验证 Alice 的 Token，却没有验证订单归属，就产生了对象级授权失效。

### 9.2 典型垂直越权

普通用户拥有有效登录状态，但可以直接请求：

```http
POST /api/admin/users/disable
Cookie: session_id=normal-user-session
```

隐藏前端按钮不能提供安全保护。后端必须独立检查角色、权限和目标对象。

### 9.3 典型多租户越权

请求中携带：

```json
{
  "tenant_id": "tenant-b",
  "document_id": "doc-1001"
}
```

如果服务端直接信任客户端提供的 `tenant_id`，而不是根据当前用户和资源关系重新计算，就可能造成租户边界突破。

### 9.4 JWT 与 A01

下面的判断错误：

```text
JWT 签名正确 = 可以访问请求资源
```

更完整的判断是：

```text
签名正确
+ iss 正确
 + aud 正确
 + 未过期
 + Scope 满足
 + 角色满足
 + 资源归属正确
 + 当前动作被允许
```

如果服务端没有执行后半部分，即使 JWT 算法和密钥使用完全正确，也可能存在 A01。

### 9.5 OAuth 漏洞与 A01 的边界

以下问题可能影响认证流程或授权流程，但不必然都归入 A01：

- `redirect_uri` 校验不足导致授权码泄露
- 缺少 PKCE 导致授权码拦截后可被交换
- 缺少 `state` 导致登录 CSRF
- OIDC 不校验 `nonce` 导致身份令牌混淆
- Resource Server 不验证 `aud` 导致 Token 跨 API 使用

这些问题可能最终造成账号接管、令牌滥用或权限扩大。漏洞分类应以根因、受影响边界和实际影响为依据，而不是只看使用了哪个协议。

### 9.6 A01 的常见类型

从测试角度，可以把 A01 拆成以下几类：

| 类型 | 核心问题 | 典型表现 |
|---|---|---|
| 水平越权 | 同级主体访问彼此资源 | Alice 读取 Bob 的订单 |
| 垂直越权 | 低权限主体执行高权限功能 | 普通用户调用管理员接口 |
| 对象级授权失效 | 只校验 Token，不校验对象关系 | 修改对象 ID 后获取他人数据 |
| 功能级授权失效 | 敏感端点缺少服务端权限检查 | 隐藏按钮但接口仍可直接调用 |
| 多租户隔离失效 | 资源与租户边界没有绑定 | Tenant A 访问 Tenant B 数据 |
| 强制浏览 | 通过直接访问路径绕过页面流程 | 直接访问未在导航中显示的管理路径 |
| 批量赋值 | 客户端可修改不应由其控制的属性 | 提交 `role`、`is_admin` 或价格字段 |
| 跨域策略失效 | 跨域信任范围过宽或凭证保护错误 | 不可信 Origin 读取受保护响应 |
| 工作流授权失效 | 多步骤操作只在部分步骤校验权限 | 直接调用确认或执行步骤 |

这些类型可以同时出现。例如，一个订单 API 可能先因 BOLA 允许读取其他租户数据，又因批量赋值允许修改订单归属，最终形成组合型越权。

---

## 十、授权测试方法

### 10.1 先画出身份和信任边界

测试前先标出：

- 登录入口
- 注册和密码重置入口
- Authorization Server
- Token Endpoint
- Resource Server
- 网关和内部服务
- 前端、移动端、第三方 Client
- Session、Redis、数据库和权限服务
- 不同租户和不同角色

然后明确每条凭证的使用范围：

```text
Authorization Server Session Cookie
    只能代表用户在授权服务器的登录状态

Access Token
    只能访问 aud 对应的资源服务器

ID Token
    只能用于客户端确认身份

Refresh Token
    只能向 Token Endpoint 换取新令牌
```

### 10.2 建立授权矩阵

至少准备：

- 两个普通用户
- 一个管理员
- 两个租户
- 一个无权限或过期状态的账号
- 不同客户端类型

矩阵示例：

| 主体 | 客户端 | 资源 | 动作 | 预期 |
|---|---|---|---|---|
| Alice | Web Client | Alice 订单 | 读取 | 允许 |
| Alice | Web Client | Bob 订单 | 读取 | 拒绝 |
| Bob | 普通客户端 | 管理接口 | 修改 | 拒绝 |
| Tenant A 用户 | API Client | Tenant B 数据 | 导出 | 拒绝 |
| 无 `orders.write` Scope | API Client | 订单 | 修改 | 拒绝 |
| 已过期 Token | API Client | 订单 | 读取 | 拒绝 |

### 10.3 按层测试

会话与认证层：

- 登录后是否重新生成 Session ID
- 注销后旧 Session 是否失效
- 密码修改后旧会话是否仍然有效
- Cookie 是否设置 `Secure`、`HttpOnly` 和合适的 `SameSite`
- Session 是否存在固定、预测或过长有效期

OAuth/OIDC 层：

- `redirect_uri` 是否精确匹配
- 是否使用 `state`
- 公共客户端是否使用 PKCE
- Authorization Code 是否短时且只能使用一次
- 是否验证 `nonce`
- 是否区分 ID Token 与 Access Token
- 是否验证 `iss`、`aud`、`exp` 和 Scope
- Refresh Token 是否轮换和重放检测

API 与业务层：

- 修改对象 ID 是否能访问其他用户资源
- 普通角色是否能调用管理接口
- 参数中的 `user_id`、`tenant_id`、`owner_id` 是否被服务端重新确定
- 批量接口、导出接口、文件接口是否复用同样的授权策略
- GET、POST、PUT、PATCH、DELETE 是否存在权限不一致
- 异步任务创建和任务结果读取是否分别检查权限
- GraphQL 字段、REST 子资源和内部 API 是否存在遗漏

### 10.4 记录证据

一份合格的授权测试记录应至少包含：

1. 测试主体和角色。
2. 原始请求和必要的响应差异。
3. 被访问的资源及其归属。
4. 预期授权结果和实际结果。
5. 是否可以批量复现。
6. 影响范围和业务后果。
7. 修复建议和回归测试条件。

不要只写“存在越权”。要说明“哪个主体使用什么凭证，对哪个资源执行了什么动作，服务端缺少了哪一项授权检查”。

---

## 十一、常见误区

### 误区一：JWT 是加密的，所以 Payload 安全

JWT 默认是签名编码，不是加密。敏感信息不应因为放进 JWT 就被认为安全。

### 误区二：有了 HTTPS 就没有令牌风险

HTTPS 保护传输过程，但无法防止：

- XSS 读取不安全存储的 Token
- 服务端日志泄露 Token
- 浏览器扩展或恶意依赖读取 Token
- Token 被错误发送到第三方域名
- Token 过期策略和撤销策略错误

### 误区三：前端隐藏按钮就是授权

前端只能改善用户体验，不能成为安全边界。真正授权必须在服务端执行。

### 误区四：Scope 越多，用户权限越大

Scope 描述客户端被委托的访问范围，但实际操作还要经过角色、对象归属、租户、资源状态等判断。

### 误区五：使用 UUID 就不会越权

不可预测 ID 只能增加枚举难度，不能替代对象级授权。

### 误区六：OAuth 登录后就可以信任客户端传来的用户 ID

当前用户应由经过验证的 Session 或 Token 主体确定。客户端提交的 `user_id` 只能作为业务参数，不能直接决定授权主体。

### 误区七：所有 Token 都可以拿到 JWT 解码器中查看

Access Token 可能是不透明随机字符串。即使是 JWT，也只能解码查看声明，不能因为解码成功就认为它有效。

---

## 十二、适合学习的本地实验路线

### 实验目标

搭建一个包含以下组件的本地环境：

```text
浏览器
  ↓
Web Client
  ↓
Authorization Server
  ↓
Resource Server API
  ↓
订单、用户和租户数据
```

可以使用 Keycloak 作为 Authorization Server，再编写或选择一个简单的 Web Client 和 API。生产系统不要自行实现完整的授权服务器，但学习时可以观察各个端点和验证逻辑。

### 实验对象

准备：

- Alice 和 Bob 两个普通用户
- Admin 一个管理员
- Tenant A 和 Tenant B 两个租户
- `orders.read` 和 `orders.write` 两个 Scope
- Alice、Bob 各自拥有的订单
- 一个管理员接口和一个普通用户接口

### 实验顺序

1. 完成一次 Authorization Code + PKCE 流程并记录每个 HTTP 请求。
2. 解码本地测试 JWT，区分 Header、Payload 和 Signature 的作用。
3. 比较 ID Token 和 Access Token 的 `iss`、`aud`、用途及接收方。
4. 观察 Access Token 过期和 Refresh Token 换取过程。
5. 验证旧 Refresh Token 是否会失效。
6. 使用 Alice 的身份访问 Bob 的订单，验证对象级授权。
7. 使用普通用户访问管理员接口，验证垂直授权。
8. 使用 Tenant A 用户访问 Tenant B 资源，验证租户隔离。
9. 检查批量接口、导出接口和异步任务是否执行相同的授权规则。
10. 为每个允许和拒绝场景写成回归测试。

### 实验记录模板

~~~markdown
## 测试标题

### 主体
- 用户：
- 角色：
- 租户：
- 客户端：

### 请求
~~~http
请求方法和路径
必要的请求头
必要的请求体
~~~

### 目标资源
- 资源类型：
- 资源 ID：
- 资源所有者：

### 预期结果

### 实际结果

### 根因

### 影响

### 修复建议

### 回归测试
~~~

---

## 十三、学习路线

### 阶段一：Web 基础

- HTTP 请求、响应、状态码和重定向
- Cookie、Session、TLS
- 浏览器同源策略、CORS、CSRF、XSS
- 密码哈希、MFA 和会话生命周期

阶段目标：能够从浏览器 Network 面板解释一次登录和一次 API 请求。

### 阶段二：认证与令牌

- Session 认证
- JWT、JWS、JWE 的区别
- Bearer Token 与不透明 Token
- Access Token、ID Token、Refresh Token
- 过期、撤销、轮换和重放

阶段目标：能够解释一枚 Token 在哪里产生、在哪里验证、代表谁、面向哪个服务。

### 阶段三：OAuth/OIDC

- OAuth 四大角色
- Authorization Code + PKCE
- Client Credentials
- Device Authorization
- ROPC 的问题
- OIDC 的 ID Token、UserInfo、`nonce`

阶段目标：能够逐包解释 OAuth 授权流程，并指出每一个参数所保护的边界。

### 阶段四：授权模型

- ACL、RBAC、ABAC、ReBAC
- Scope、Role、Permission、Policy 的差异
- 对象级授权和功能级授权
- 多租户隔离
- 默认拒绝和最小权限

阶段目标：能够为一个业务系统画出完整的授权矩阵。

### 阶段五：安全测试

- 水平越权和垂直越权
- IDOR/BOLA
- 批量赋值
- 强制浏览
- OAuth 配置和令牌验证问题
- 多步骤流程和异步任务授权

阶段目标：能够从身份、客户端、令牌、资源和动作五个维度设计测试用例。

### 阶段六：工程化防御

- 集中式策略管理
- API Gateway 与服务端授权
- 权限缓存和撤销
- 审计日志和异常检测
- 授权单元测试、集成测试和回归矩阵
- 高风险操作的二次认证和风险控制

阶段目标：不仅能发现越权，还能解释根因、影响、修复方式和回归验证方式。

---

## 十四、参考规范与学习资源

- OAuth 2.0 Authorization Framework，RFC 6749
- OAuth 2.0 Bearer Token Usage，RFC 6750
- Proof Key for Code Exchange，RFC 7636
- OAuth 2.0 Authorization Server Metadata，RFC 8414
- OpenID Connect Core 1.0
- OAuth 2.0 Security Best Current Practice
- OWASP Top 10，A01 Broken Access Control
- OWASP Authorization Cheat Sheet
- OWASP Web Security Testing Guide
- PortSwigger Web Security Academy：Access Control、OAuth Authentication、JWT、API Testing
- OWASP Application Security Verification Standard，访问控制与认证相关章节

阅读规范时，不要只记参数名称。对每个参数都追问：

```text
它由谁生成？
它由谁验证？
它保护哪条信任边界？
它失效时会造成什么后果？
```

---

## 十五、最终检查清单

### 身份认证

- 是否正确验证了用户身份？
- 登录后是否重新生成会话标识？
- 注销、改密、封禁后旧凭证是否失效？
- 是否设置了合理的会话有效期？

### OAuth/OIDC

- 是否使用 Authorization Code + PKCE？
- 是否严格校验 `redirect_uri`？
- 是否校验 `state`？
- OIDC 是否校验 `nonce`？
- 是否区分 ID Token 与 Access Token？
- 是否验证 `iss`、`aud`、`exp` 和 Scope？
- Refresh Token 是否轮换并检测重放？

### 访问控制

- 是否默认拒绝？
- 是否在服务端校验，而不是只依赖前端？
- 是否同时覆盖功能级和对象级权限？
- 是否验证资源所有权和租户边界？
- 是否覆盖批量、导出、文件、异步和内部接口？
- 是否对每个角色和资源组合有回归测试？

### 令牌和数据保护

- Token 是否只通过 HTTPS 传输？
- 是否避免放在 URL、日志和 Referer 中？
- JWT Payload 是否包含不必要的敏感信息？
- 是否有撤销、过期和密钥轮换机制？
- 是否对高风险操作进行额外保护？

---

## 结语

Cookie、Session、JWT、OAuth、OIDC 和访问控制并不是一条简单的技术替代链。它们分别解决状态保存、凭证传递、授权委托、身份认证和权限执行中的不同问题。

理解这部分知识的关键，不是背诵每一种协议的参数，而是始终沿着下面的链条分析：

```text
请求代表谁
→ 凭证由谁签发
→ 凭证是否有效
→ 凭证是否面向当前服务
→ 请求具有什么 Scope 和角色
→ 目标资源属于谁
→ 当前动作是否被允许
→ 服务端是否真正执行了上述判断
```

只要最后一个环节存在遗漏，前面再严谨的认证和令牌体系也可能因为 A01 失效的访问控制而失去实际安全价值。
