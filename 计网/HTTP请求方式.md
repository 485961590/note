## HTTP 请求方式 (HTTP Request Methods)

HTTP 定义了一组请求方法，表明对给定资源要执行的操作。

### 常见方法

| 方法      | 说明                   |
| ------- | -------------------- |
| GET     | 请求指定资源，只用于获取数据       |
| POST    | 向指定资源提交数据（创建/更新）     |
| PUT     | 替换目标资源的全部内容          |
| PATCH   | 对资源进行部分修改            |
| DELETE  | 删除指定资源               |
| HEAD    | 与 GET 相同，但不返回响应体     |
| OPTIONS | 查询服务器支持的方法           |
| TRACE   | 回显服务器收到的请求，用于诊断      |
| CONNECT | 建立隧道，通常用于 SSL/TLS 代理 |

### 详细说明

**GET** -- 获取资源
- 参数拼接在 URL 中（Query String）
- 可被缓存、收藏、保留在浏览器历史记录中
- 有长度限制（浏览器/服务器限制，通常 2KB-8KB）
- 不应用于敏感数据（参数暴露在 URL 中）

请求示例（获取用户列表）：

```
GET /api/users?page=1&size=10 HTTP/1.1
Host: example.com
Accept: application/json
```

响应：

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 85

{
  "page": 1,
  "users": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ]
}
```

**POST** -- 提交数据
- 参数放在请求体中
- 不会被缓存，不会保留在浏览器历史记录中
- 无长度限制
- 适用于登录、表单提交、文件上传等

请求示例（创建新用户）：

```
POST /api/users HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 44

{"name": "Charlie", "email": "charlie@example.com"}
```

响应（201 Created）：

```
HTTP/1.1 201 Created
Location: /api/users/3
Content-Type: application/json

{"id": 3, "name": "Charlie", "email": "charlie@example.com"}
```

另一个常见形态 -- 表单提交（`application/x-www-form-urlencoded`）：

```
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=admin&password=123456
```

**PUT** -- 完整替换
- 请求体包含资源的完整新内容
- 幂等：多次相同的 PUT 请求结果一致
- 若资源不存在可创建，存在则替换

请求示例（完整替换用户 1 的所有字段）：

```
PUT /api/users/1 HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 52

{"name": "Alice Updated", "email": "alice_new@example.com"}
```

响应：

```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 1, "name": "Alice Updated", "email": "alice_new@example.com"}
```

**PATCH** -- 部分修改
- 只发送需要修改的字段
- 非幂等（连续多次可能产生不同结果）
- 比 PUT 更节省带宽

请求示例（仅修改用户 1 的邮箱，其他字段不变）：

```
PATCH /api/users/1 HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 36

{"email": "alice_patched@example.com"}
```

响应：

```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 1, "name": "Alice", "email": "alice_patched@example.com"}
```

**DELETE** -- 删除资源
- 删除指定 URI 的资源
- 幂等：删除后再次删除结果一致（资源已不存在）

请求示例：

```
DELETE /api/users/1 HTTP/1.1
Host: example.com
```

响应（成功删除）：

```
HTTP/1.1 204 No Content
```

第二次删除同一资源：

```
HTTP/1.1 404 Not Found
Content-Type: application/json

{"error": "User not found"}
```

**HEAD** -- 仅获取响应头
- 与 GET 行为一致，但不返回响应体
- 用于检查资源是否存在、获取元信息（Content-Length、Last-Modified 等）
- 常用于缓存验证

请求示例（只想知道文件大小，不下载内容）：

```
HEAD /files/report.pdf HTTP/1.1
Host: example.com
```

响应（有响应头，无响应体）：

```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Length: 2048000
Last-Modified: Tue, 15 Jul 2026 08:00:00 GMT
```

**OPTIONS** -- 查询支持的方法
- 响应头 `Allow` 列出该资源支持的 HTTP 方法
- 浏览器在跨域请求时会自动发出 OPTIONS 预检请求 (CORS Preflight)

请求示例（查询服务器对该 URI 支持哪些方法）：

```
OPTIONS /api/users HTTP/1.1
Host: example.com
```

响应：

```
HTTP/1.1 204 No Content
Allow: GET, POST, OPTIONS
```

CORS 预检请求示例（浏览器自动发出，带两个关键请求头）：

```
OPTIONS /api/users HTTP/1.1
Host: api.example.com
Origin: https://frontend.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

服务器响应（声明允许跨域）：

```
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://frontend.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 86400
```

**TRACE** -- 诊断回显
- 服务器将收到的请求原样返回
- 用于排查中间代理修改了哪些请求头
- 存在安全风险（XST 攻击），生产环境通常禁用

请求示例：

```
TRACE / HTTP/1.1
Host: example.com
X-Custom-Header: test
```

响应（原样返回收到的请求）：

```
HTTP/1.1 200 OK
Content-Type: message/http

TRACE / HTTP/1.1
Host: example.com
X-Custom-Header: test
```

> 生产环境建议禁用 TRACE，防止反射型 XSS（XST 攻击）窃取 Cookie。Apache 和 Nginx 默认禁用。

**CONNECT** -- 建立隧道
- 用于建立到目标服务器的 TCP 隧道
- 最常见的用途：HTTPS 通过代理时的 SSL/TLS 隧道

请求示例（通过代理访问 HTTPS 站点）：

```
CONNECT www.example.com:443 HTTP/1.1
Host: www.example.com:443
Proxy-Authorization: Basic dXNlcjpwYXNz
```

代理响应（隧道建立成功）：

```
HTTP/1.1 200 Connection Established
```

之后客户端与目标服务器之间的通信经过此隧道，代理不再解析内容（仅做 TCP 转发）。整个过程：

```
客户端  <--->  代理  <--->  目标服务器(HTTPS)
   |               |              |
   |-- CONNECT --->|              |
   |               |-- TCP 连接 -->|
   |<- 200 隧道已建立 ->|           |
   |========== 加密 TLS 流量 ===========>|
```

### RESTful 风格示例

```
GET    /api/users          # 获取用户列表
GET    /api/users/1        # 获取 ID 为 1 的用户
POST   /api/users          # 创建新用户
PUT    /api/users/1        # 完整更新用户 1
PATCH  /api/users/1        # 部分更新用户 1
DELETE /api/users/1        # 删除用户 1
```

### 幂等性 vs 安全性

- **幂等 (Idempotent)**：多次相同请求的结果与单次请求一致。GET、PUT、DELETE、HEAD、OPTIONS、TRACE 是幂等的。
- **安全 (Safe)**：不修改服务器上的资源。GET、HEAD、OPTIONS、TRACE 是安全的。
