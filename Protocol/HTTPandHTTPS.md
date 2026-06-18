# HTTP & HTTPS

HTTP（HyperText Transfer Protocol）是 Web 通信的基础协议。HTTPS = HTTP + TLS/SSL，在 HTTP 下层增加加密层，解决明文传输的安全问题。

## 一、HTTP 基础

### 请求结构

```
METHOD /path?query=value HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 ...
Accept: text/html
Cookie: session=abc123
```

### 响应结构

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 1234
Set-Cookie: session=xyz789; HttpOnly; Secure

<html>...</html>
```

### 常用状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `200 OK` | 成功 | 正常响应 |
| `201 Created` | 已创建 | PUT/POST 成功创建资源 |
| `204 No Content` | 无内容 | 成功但无响应体 |
| `301 Moved Permanently` | 永久重定向 | 浏览器会缓存，后续直接跳转 |
| `302 Found` | 临时重定向 | 每次都会请求原 URL |
| `304 Not Modified` | 未修改 | 缓存有效，不返回内容 |
| `400 Bad Request` | 请求错误 | 参数格式有问题 |
| `401 Unauthorized` | 需认证 | 缺少或错误的认证信息 |
| `403 Forbidden` | 禁止访问 | 认证通过但无权限 |
| `404 Not Found` | 未找到 | 路径不存在 |
| `405 Method Not Allowed` | 方法不允许 | 如对只读接口使用 POST |
| `500 Internal Server Error` | 服务器错误 | 代码异常 |
| `502 Bad Gateway` | 网关错误 | 上游服务器无响应 |
| `503 Service Unavailable` | 服务不可用 | 过载或维护中 |

### HTTP 版本演进

| 版本 | 年份 | 核心特点 |
|------|------|----------|
| HTTP/0.9 | 1991 | 仅 GET，无头部，纯文本 |
| HTTP/1.0 | 1996 | 引入头部、状态码、POST |
| HTTP/1.1 | 1997 | 持久连接、管线化、Host 头、分块传输 |
| HTTP/2 | 2015 | 多路复用、头部压缩（HPACK）、服务器推送、二进制帧 |
| HTTP/3 | 2022 | 基于 QUIC（UDP）、0-RTT 握手、无队头阻塞 |

---

## 二、HTTP 安全 — 攻击面

### 1. HTTP 请求方法

| 方法 | 风险 | 利用场景 |
|------|------|----------|
| `GET` | 参数暴露在 URL | 浏览器历史/代理日志泄露敏感参数 |
| `POST` | CSRF 攻击载体 | 伪造跨站请求（转账、改密） |
| `PUT` | 文件上传 | 配置不当可上传 Webshell |
| `DELETE` | 文件删除 | 配置不当可删除资源 |
| `TRACE` | XST 攻击 | 反射用户输入，可能泄露 Cookie |
| `OPTIONS` | 信息泄露 | 泄露支持的 HTTP 方法 |

### 2. HTTP 头部 — 篡改重点

| 头部 | 安全风险 | 攻击示例 |
|------|----------|----------|
| `Cookie` | 会话劫持、越权 | 窃取 Cookie 冒充管理员 |
| `Referer` | CSRF 检测绕过 | 删除 Referer 头绕过防护 |
| `User-Agent` | WAF 绕过 | 伪造成 `Googlebot` 绕过检测 |
| `X-Forwarded-For` | IP 欺骗、越权 | 伪造 `XFF: 127.0.0.1` 访问内部接口 |
| `Host` | 虚拟主机绕过、SSRF | 修改 Host 头攻击其他站点 |
| `Content-Length` | HTTP 走私 | 与 `Transfer-Encoding` 配合绕过 WAF |

### 3. 协议特性利用

**HTTP 走私（HTTP Request Smuggling）**
- 利用前端代理和后端服务器对 `Content-Length` 和 `Transfer-Encoding` 解析差异
- 后果：绕过 WAF、劫持其他用户请求、缓存投毒

**参数污染（Parameter Pollution）**
- 提交重复参数：`?id=1&id=2`
- 不同后端解析结果不同（取第一个/取最后一个/合并为数组）

**编码混淆**
- `%00`（空字节）截断字符串
- `%0d%0a`（CRLF）注入头部
- 双重 URL 编码绕过 WAF

### 4. 会话管理攻击

Cookie 三个关键安全属性：

| 属性 | 作用 | 缺失后果 |
|------|------|----------|
| `Secure` | 仅 HTTPS 传输 | Cookie 可被明文嗅探 |
| `HttpOnly` | 禁止 JS 访问 | XSS 可直接窃取 Cookie |
| `SameSite` | 限制跨站发送 | 易受 CSRF 攻击 |

攻击手段：
- **会话固定**：诱导用户使用攻击者预设的 SessionID
- **会话劫持**：窃取有效 SessionID（XSS / 网络嗅探）
- **越权**：修改 Cookie 中的用户标识（如 `user_id=1` → `user_id=2`）

---

## 三、HTTPS 深入

### TLS 握手（简化）

```
客户端                        服务器
  |                             |
  |--- ClientHello ----------->|  ① 客户端：支持的加密套件 + 随机数
  |<-- ServerHello ------------|  ② 服务器：选定加密套件 + 随机数 + 证书
  |<-- Certificate ------------|
  |--- (密钥交换) ------------>|  ③ 验证证书，交换预主密钥
  |--- Finished -------------->|  ④ 双方确认，开始对称加密通信
  |<-- Finished ---------------|
  |                             |
  |<== 对称加密数据传输 =======>|
```

### 证书与 PKI

- **证书链**：站点证书 ← 中间 CA ← 根 CA（预置在操作系统/浏览器中）
- **证书内容**：域名、有效期、公钥、颁发者、签名
- **验证关键**：域名匹配、证书未过期、颁发者可信、未被吊销（CRL/OCSP）

### HTTPS 安全威胁

| 威胁 | 说明 | 防御 |
|------|------|------|
| **SSL 剥离** | 中间人将 HTTPS 降级为 HTTP | HSTS 预加载列表 |
| **伪造证书** | 诱导用户安装恶意 CA（如 Burp 代理证书） | 证书固定（Certificate Pinning） |
| **降级攻击** | 强制使用弱加密套件 | 服务端禁用过时套件（如 SSLv3、TLS 1.0） |
| **心脏滴血** | OpenSSL 漏洞泄露内存数据 | 及时更新 OpenSSL |
| **BEAST/POODLE** | 针对 CBC 模式的攻击 | 禁用 CBC 模式，使用 AEAD |
| **CRIME/BREACH** | 利用压缩率侧信道 | 禁用 HTTP 压缩 或 分块响应 |

### HSTS（HTTP Strict Transport Security）

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

- 浏览器强制对该域名使用 HTTPS
- `preload`：加入浏览器内置的 HSTS 预加载列表

---

## 四、HTTP 响应头 — 防御配置

| 头部 | 防护对象 | 推荐配置 |
|------|----------|----------|
| `Content-Security-Policy` | XSS | `default-src 'self'; script-src 'self'` |
| `Strict-Transport-Security` | SSL 剥离 | `max-age=31536000; includeSubDomains` |
| `X-Frame-Options` | 点击劫持 | `DENY` 或 `SAMEORIGIN` |
| `X-Content-Type-Options` | MIME 混淆 | `nosniff` |
| `Referrer-Policy` | 信息泄露 | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | 功能滥用 | `camera=(), microphone=()` |

---

## 五、实战检查清单

1. `curl -I https://target.com` 检查响应头是否有安全配置缺失
2. 用 Burp Suite Repeater 修改 HTTP 头部，观察响应变化
3. 测试请求中插入 `../`、`%00`、`%0d%0a` 等特殊字符
4. 检查 Cookie 是否缺少 `HttpOnly`、`Secure`、`SameSite`
5. 测试 HTTP 方法滥用：`curl -X OPTIONS -v http://target.com`
6. 检查是否存在混合内容（HTTPS 页面加载 HTTP 资源）
7. 用 `openssl s_client` 检查证书链和加密套件
8. 测试 HSTS：访问 `http://` 版本是否自动跳转

---

## 六、常用命令

```bash
# 查看响应头
curl -I https://example.com

# 查看完整握手过程
curl -v https://example.com

# 查看证书信息
openssl s_client -connect example.com:443 -servername example.com </dev/null
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates -subject

# 测试 SSL/TLS 版本
nmap --script ssl-enum-ciphers -p 443 example.com

# 检查 HSTS 头
curl -sI https://example.com | grep -i strict
```

---

> **核心原则：所有 Web 攻击的本质，都是对 HTTP 协议的异常使用。理解协议，才能理解漏洞。**
