# JSON

> JSON（JavaScript Object Notation）是目前 Web API 最主流的数据交换格式。比 XML 轻量、人可读、所有语言都有解析器。

---

## 基本语法

```json
{
    "name": "Alice",
    "age": 25,
    "is_admin": false,
    "skills": ["Python", "Docker", "SQL"],
    "address": {
        "city": "Beijing",
        "zipcode": "100000"
    },
    "projects": null
}
```

**数据类型：**

| 类型 | 示例 | 注意 |
|------|------|------|
| 字符串 | `"hello"` | 必须双引号，支持 Unicode 转义 `\uXXXX` |
| 数字 | `42`, `3.14`, `-10`, `1.5e10` | 不支持 NaN、Infinity、十六进制 |
| 布尔 | `true`, `false` | 小写，不加引号 |
| 空值 | `null` | 小写，不加引号 |
| 对象 | `{"key": "value"}` | 键必须加双引号 |
| 数组 | `[1, "two", true, null]` | 元素类型可以混合 |

**严格限制（RFC 8259）：**
- 字符串必须用双引号，单引号非法
- 不能有注释
- 不能有尾随逗号（`{"a": 1,}` 非法）
- 键名必须加双引号（`{name: "Alice"}` 非法）
- 顶层值不限于对象，也可以是数组 `[1,2,3]` 或单个值 `"hello"`
- 数字不能有前导零（`01` 非法），不能是 NaN 或 Infinity
- 字符串中的控制字符必须转义（`\n`、`\t` 等）

---

## JSON vs JavaScript 对象

这两个长得像但不是一回事：

```javascript
// JavaScript 对象（不是合法的 JSON）
{
    name: "Alice",            // 键没加引号 → 非法
    age: 25,
    sayHi: function() {},     // 函数 → JSON 不支持
    date: new Date(),         // 日期对象 → JSON 不支持
    last: undefined,          // undefined → JSON 不支持
    score: NaN,               // NaN → JSON 不支持
    id: 001,                  // 前导零 → JSON 非法
    'key': 'single quote',    // 单引号键 → JSON 非法
}

// 合法的 JSON
{
    "name": "Alice",
    "age": 25
}
```

---

## JSON Schema

类似 XML 的 XSD，定义 JSON 数据的结构规则：

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "User",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "age": {
            "type": "integer",
            "minimum": 0,
            "maximum": 150
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "role": {
            "type": "string",
            "enum": ["admin", "user", "guest"]
        },
        "skills": {
            "type": "array",
            "items": { "type": "string" },
            "uniqueItems": true,
            "minItems": 1
        },
        "address": {
            "type": "object",
            "properties": {
                "city": { "type": "string" },
                "zipcode": { "type": "string", "pattern": "^[0-9]{6}$" }
            },
            "required": ["city"]
        }
    },
    "required": ["name", "email"],
    "additionalProperties": false
}
```

**JSON Schema 验证关键字：**

| 类别 | 关键字 |
|------|--------|
| 类型 | `type`, `enum`, `const` |
| 数值 | `minimum`, `maximum`, `multipleOf`, `exclusiveMinimum` |
| 字符串 | `minLength`, `maxLength`, `pattern`, `format`（email/uri/date-time） |
| 数组 | `items`, `minItems`, `maxItems`, `uniqueItems`, `contains` |
| 对象 | `properties`, `required`, `additionalProperties`, `minProperties` |
| 条件 | `if`/`then`/`else`, `allOf`, `anyOf`, `oneOf`, `not` |

---

## NDJSON（JSON Lines）

流式场景下用换行分隔多个 JSON 对象，每行一个独立的 JSON：

```json
{"level": "info", "message": "服务启动", "time": "10:00:01"}
{"level": "warn", "message": "磁盘使用率 85%", "time": "10:00:05"}
{"level": "error", "message": "连接超时", "time": "10:01:23"}
```

后端可以逐行解析，不需要等待整个响应。Kubernetes 日志、Elasticsearch bulk API、Docker 日志都使用 NDJSON。

---

## JSONP（JSON with Padding）

跨域取 JSON 数据的一种老旧方案，利用 `<script>` 标签不受同源策略限制：

```html
<script>
function handleData(data) {
    console.log(data);
}
</script>
<script src="https://api.example.com/data?callback=handleData"></script>
```

服务器返回函数调用包裹 JSON：`handleData({"name": "Alice"});`

**安全风险：**
- Callback 参数如果不过滤，可注入任意 JS 代码
- 如果服务器设置了错误的 Content-Type 头，可能触发 Rosetta Flash 攻击
- 现代替代方案：CORS（Cross-Origin Resource Sharing）

---

## JSON Pointer / JSON Patch

**JSON Pointer（RFC 6901）：** 用路径字符串精确定位 JSON 文档中的某个值。

```json
// 文档
{"users": [{"name": "Alice"}, {"name": "Bob"}]}

// 路径
""                              // 整个文档
"/users"                        // users 数组
"/users/0"                      // 第一个元素
"/users/0/name"                 // "Alice"
"/users/0/na~0me"              // 如果键名包含 ~ 或 /，用 ~0 替代 ~，~1 替代 /
```

**JSON Patch（RFC 6902）：** 描述对 JSON 文档的修改操作（add/remove/replace/move/copy/test）：

```json
[
    {"op": "replace", "path": "/name", "value": "Charlie"},
    {"op": "add", "path": "/skills/-", "value": "Go"},
    {"op": "remove", "path": "/projects"}
]
```

---

## JWT（JSON Web Token）

JWT 是三段 Base64URL 编码的 JSON，点号分隔，用于无状态身份认证。

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.签名部分
   ↑ Header JSON          ↑ Payload JSON    ↑ Signature
```

```json
// Header（解码后）
{"alg": "HS256", "typ": "JWT"}

// Payload（解码后）
{"sub": "123", "name": "Alice", "iat": 1718200000, "exp": 1718286400}
```

### JWT 常见攻击

**1. 算法混淆攻击**

将 Header 中 `alg: RS256` 改为 `alg: HS256`。RS256 是非对称算法（用公钥验证签名），HS256 是对称算法（用密钥签名和验证）。如果服务器逻辑是"按 alg 字段选算法"，攻击者把公钥当对称密钥用：

```python
# 攻击步骤
# 1. 拿到服务器的 RS256 公钥（通常可从 /.well-known/jwks.json 获取）
# 2. 修改 Header → {"alg": "HS256"}
# 3. 修改 Payload → {"sub": "admin"}
# 4. 用公钥作为 HMAC 密钥签名
# 5. 服务器用 HS256 算法 + 同一个公钥验证 → 通过
```

防御：服务端强制指定算法，不信任 Header 中的 alg 字段。

**2. `alg: none` 攻击**

```json
{"alg": "none", "typ": "JWT"}
```

修改 Header 为不签名，Payload 篡改后签名部分留空。老旧或配置不当的 JWT 库可能接受。

**3. JWK 头注入（jwk / jku）**

```json
{
    "alg": "RS256",
    "jwk": {
        "kty": "RSA",
        "n": "...（攻击者生成的公钥）",
        "e": "AQAB"
    }
}
```

如果服务器信任 Header 中嵌入的公钥（`jwk`）或公钥 URL（`jku`），攻击者可以自签 JWT。

**4. `kid` 注入**

`kid`（Key ID）用于选择验证签名的密钥。如果服务器用 `kid` 拼接文件路径读密钥，攻击者可以路径遍历：

```json
{"alg": "HS256", "kid": "../../etc/passwd"}
```

或 SQL 注入：

```json
{"alg": "HS256", "kid": "1 UNION SELECT 'attacker_secret'"}
```

---

## 安全考量

### 1. JSON 注入

服务器端把用户输入直接拼接到 JSON 中而不做转义：

```python
# 危险做法
name = request.form["name"]            # 用户输入：Alice"}, "is_admin": true, "x": {"
json_str = f'{{"name": "{name}"}}'    # 产生：{"name": "Alice", "is_admin": true, "x": {""}}

# 安全做法
import json
json_str = json.dumps({"name": name}) # 自动转义
```

### 2. 原型污染（JavaScript / Node.js）

恶意 JSON 通过 `__proto__` 或 `constructor.prototype` 污染对象原型：

```javascript
// 恶意 JSON
{"__proto__": {"is_admin": true}}

// 错误的合并方式
let user = {};
Object.assign(user, malicious_json);
// 所有对象都继承了 is_admin = true

// 安全做法
let user = Object.create(null);           // 创建无原型的对象
const hasOwn = Object.prototype.hasOwnProperty;
// 合并前检查 key 是否为 __proto__
```

### 3. 大数精度丢失

JavaScript 的 Number 是 64 位浮点数，超过 2^53-1 的整数会丢失精度：

```javascript
JSON.parse('{"id": 9007199254740993}');
// {id: 9007199254740992}  <- 变了
```

```python
# Python 没有此问题，int 精度无限
json.loads('{"id": 9007199254740993}')
# {'id': 9007199254740993}  # 正确
```

大整数应传字符串：`{"id": "9007199254740993"}`。

### 4. JSON 解析器差异

不同语言对同一 JSON 的解析可能不同，这在安全审计中很关键：

```json
// 重复键：不同解析器行为不同
{"user": "guest", "user": "admin"}

// Python json.loads → 取最后一个：{"user": "admin"}
// Go encoding/json → 取最后一个
// Java Jackson → 默认取最后一个（可配置抛异常）
// JavaScript JSON.parse → 取最后一个
// PHP json_decode → 取最后一个

// 尾随无效数据
{"user": "admin"} extra stuff here
// Python json.loads → 报错
// Java Gson → 默认报错
// 某些宽松解析器 → 忽略后续内容
```

### 5. JSON 反序列化漏洞

```python
# Python 的 pickle 不以 JSON 为载体但常被混淆
# 不要将 JSON 数据直接传给 pickle.loads()

# Java Jackson 的 enableDefaultTyping() 允许通过 JSON 构造任意类
# {"@class": "com.example.Malicious", "cmd": "rm -rf /"}
```

### 6. JSON 在 SQL 中的注入

```sql
-- PostgreSQL JSONB
SELECT * FROM users WHERE data->>'name' = 'Alice';

-- 如果应用拼接用户输入到 JSON 路径（类似 XPath 注入）
-- 用户输入：Alice' OR '1'='1
-- 变成：
SELECT * FROM users WHERE data->>'name' = 'Alice' OR '1'='1';
```

### 7. 哈希碰撞 DoS

JSON 对象的键组成哈希表。攻击者构造大量碰撞键，使解析器退化为 O(n^2)：

```json
{
    "Aa": 1, "BB": 1, "AaAa": 1, "BBBB": 1,
    ... 数千个碰撞键
}
```

防御：限制 JSON 大小、限制键的数量、使用随机化哈希（Python 3 默认开启）。

---

## 常见用途

| 场景 | 示例 |
|------|------|
| REST API | 前后端数据交换 |
| 配置文件 | `package.json`, `tsconfig.json`, VSCode `settings.json` |
| NoSQL 数据库 | MongoDB 文档 |
| 身份认证 | JWT |
| 日志格式 | 结构化日志 |
| 序列化 | Python `json.dumps()` / JS `JSON.stringify()` |
| 流式传输 | NDJSON（一行一个 JSON） |
| 基础设施 | AWS IAM Policy、CloudFormation、Terraform JSON |
