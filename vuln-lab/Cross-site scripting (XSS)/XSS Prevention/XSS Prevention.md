# XSS Prevention

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [Content Security Policy](../Content%20Security%20Policy/Content%20Security%20Policy.md) | [JavaScript for XSS](../JavaScript%20for%20XSS/JavaScript%20for%20XSS.md)

---

## 纵深防御策略

XSS 防御应实施多层防护，没有单一技术能够完全防御所有 XSS 向量：

```
XSS 防御层次（纵深防御）

第一层：输出编码（核心防线）
├── 在数据写入页面时，根据上下文选择正确的编码方式
├── HTML 上下文：HTML 实体编码
├── JavaScript 上下文：Unicode 转义
├── URL 上下文：URL 编码
└── CSS 上下文：CSS 转义

第二层：输入验证（辅助防线）
├── 白名单优先于黑名单
├── 验证数据类型、格式、长度
├── 在接收时拒绝无效输入
└── 不要尝试"清理"恶意输入使之为安全

第三层：安全响应头（环境防线）
├── Content-Type + charset
├── X-Content-Type-Options: nosniff
├── HttpOnly Cookie 标志
└── SameSite Cookie 限制

第四层：CSP（最后防线）
├── 限制脚本来源
├── 使用 nonce / hash 允许合法内联脚本
├── 禁止 object-src
└── 配置 report-uri 监控违规
```

---

## 第一层：输出编码

输出编码是 XSS 防御的**核心**。编码应在数据写入页面时直接应用，因为写入的上下文决定了编码类型。

### HTML Body 上下文

对于出现在 HTML 标签之间的文本内容，进行 HTML 实体编码：

| 字符 | 编码为 | 必要性 |
|------|--------|--------|
| `<` | `&lt;` | 防止标签注入，必须 |
| `>` | `&gt;` | 防止标签闭合，强烈建议 |
| `&` | `&amp;` | 防止实体注入，必须 |
| `"` | `&quot;` | 在属性上下文中必须，body 中可选 |
| `'` | `&#x27;` | 在属性上下文中必须，body 中可选 |

### HTML 属性上下文

对于出现在 HTML 属性值中的数据，需要根据属性的类型选择编码方式：

**普通属性（如 `<input value="...">`）：**
- 进行 HTML 实体编码（同上表）
- 始终用引号包裹属性值
- 如果可能，使用白名单限制属性值的内容

**URL 属性（如 `<a href="...">`）：**
- 首先验证 URL 以安全协议（HTTP、HTTPS）开头
- 然后进行 URL 编码
- 避免允许 `javascript:` 和 `data:` 协议

**事件处理器属性（如 `onclick="..."`）：**
- 首先进行 JavaScript 转义（Unicode 编码）
- 然后进行 HTML 实体编码
- **强烈建议：** 避免将用户数据放入事件处理器中，改用 `addEventListener`

### JavaScript 上下文

对于出现在 `<script>` 块内或事件处理器内的数据：

| 情况 | 编码方式 |
|------|---------|
| 在 JavaScript 字符串字面量中 | Unicode 转义非字母数字字符 |
| 在 `eval()` 或类似函数中 | 绝对不要将用户数据放入 eval |

**Unicode 转义示例：**

```javascript
// 危险
var name = '<?php echo $_GET['name']; ?>';

// 安全（经过 Unicode 转义后）
var name = 'Hello, <script>alert(1)<\/script>';
```

### URL 上下文

对于出现在 URL 中（如查询参数值）的数据：

- 使用 `encodeURIComponent()` 编码
- 验证整个 URL 以安全协议开头（HTTP、HTTPS、mailto 等）

### CSS 上下文

对于出现在 `<style>` 块或内联 style 属性中的数据：

- 使用 CSS 转义（`\HH ` 格式）
- 避免允许用户控制完整的 CSS 属性值
- CSS 注入可能导致数据窃取（通过 CSS 选择器和背景图片 URL）

### 多层编码

当数据流经多个上下文时，需要按**从内到外**的顺序应用编码：

```html
<!-- 数据路径：URL → JavaScript → HTML 属性 -->
<a href="#" onclick="navigate('USER_INPUT')">

<!-- 编码顺序：先 JS 转义，再 HTML 实体编码 -->
```

---

## 第二层：输入验证

### 白名单优于黑名单

**错误做法（黑名单）：**

```
过滤 javascript, data, vbscript, <script>, onerror, onload...
```

黑名单永远不完整——总有新的绕过方式被不断发现。

**正确做法（白名单）：**

```
只允许: [a-zA-Z0-9._-] 用于用户名
只允许: http:// 或 https:// 开头的 URL
只允许: 预期集合中的值（如国家代码）
```

### 具体验证示例

#### URL 验证

```php
// PHP 示例
function isValidUrl($url) {
    $allowedSchemes = ['http', 'https', 'mailto'];
    $scheme = parse_url($url, PHP_URL_SCHEME);
    return in_array(strtolower($scheme), $allowedSchemes, true);
}
```

```java
// Java 示例
boolean isValidUrl(String url) {
    Set<String> allowedSchemes = Set.of("http", "https", "mailto");
    try {
        URI uri = new URI(url);
        return allowedSchemes.contains(uri.getScheme().toLowerCase());
    } catch (URISyntaxException e) {
        return false;
    }
}
```

#### 邮箱验证

限制字符集和对格式进行验证：

```php
// 同时验证格式和字符集
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die('Invalid email format');
}
if (!preg_match('/^[a-zA-Z0-9.@_+\-]+$/', $email)) {
    die('Email contains invalid characters');
}
```

#### 纯文本字段

对于不包含任何 HTML 的字段（如用户名、标题），限制字符集：

```php
// 仅允许字母、数字、下划线和短横线
if (!preg_match('/^[a-zA-Z0-9_\- ]+$/', $username)) {
    die('Username contains invalid characters');
}
```

### 避免"清理"输入

**错误做法：** 尝试从输入中过滤"危险"内容使其变得"安全"。

```php
// 不安全的清理方式 -- 永远不够全面
$input = str_replace('<script>', '', $input);  // 可用 <scr<script>ipt> 绕过
$input = strip_tags($input, '<b><i>');        // 属性注入仍可能
```

**正确做法：** 拒绝无效输入，或在输出时进行编码。不要试图在中间环节"修复"数据。

---

## 第三层：安全响应头

### 设置正确的 Content-Type

```
Content-Type: text/html; charset=UTF-8
```

- 始终声明字符集，防止字符集嗅探攻击（如 UTF-7 XSS）
- 不要使用浏览器可嗅探的 Content-Type（如没有 charset 的 `text/html`）

### X-Content-Type-Options

```
X-Content-Type-Options: nosniff
```

阻止浏览器进行 MIME 类型嗅探，防止将用户上传的非脚本文件当作脚本执行。

### HttpOnly Cookie

```
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict
```

`HttpOnly` 标志阻止 JavaScript 通过 `document.cookie` 读取 Cookie，减轻 XSS 攻击窃取会话 Cookie 的风险。

**注意：** HttpOnly 不能阻止 XSS 本身，仅限制 Cookie 被窃取。攻击者仍然可以以受害者身份发出请求。

### SameSite Cookie

```
Set-Cookie: session=abc123; SameSite=Strict
```

限制 Cookie 仅在同站请求中发送，防止 CSRF 式攻击。关于 SameSite 的详细内容，见 [CSRF 文档](../../Cross-site%20request%20forgery%20(CSRF)/Cross-site%20request%20forgery%20(CSRF).md)。

---

## 各语言/框架的 XSS 防御实现

### PHP

**HTML 上下文编码：**

```php
// 标准 HTML 编码
echo htmlentities($input, ENT_QUOTES, 'UTF-8');

// 参数说明：
// ENT_QUOTES: 编码单引号和双引号
// 'UTF-8':   字符集
```

**JavaScript 字符串上下文编码：**

PHP 不提供内建的 JavaScript Unicode 转义 API。需要自行实现：

```php
function jsEscape($str) {
    $output = '';
    $str = str_split($str);
    for ($i = 0; $i < count($str); $i++) {
        $chrNum = ord($str[$i]);
        $chr = $str[$i];

        // 处理 LS (U+2028) 和 PS (U+2029) -- JavaScript 中的行终止符
        if ($chrNum === 226) {
            if (isset($str[$i+1]) && ord($str[$i+1]) === 128) {
                if (isset($str[$i+2]) && ord($str[$i+2]) === 168) {
                    $output .= ' '; $i += 2; continue;
                }
                if (isset($str[$i+2]) && ord($str[$i+2]) === 169) {
                    $output .= ' '; $i += 2; continue;
                }
            }
        }

        switch ($chr) {
            case "'": case '"': case "\n": case "\r":
            case "&": case "\\": case "<": case ">":
                $output .= sprintf("\\u%04x", $chrNum);
                break;
            default:
                $output .= $str[$i];
                break;
        }
    }
    return $output;
}
```

**使用模板引擎（推荐）：**

```twig
{# Twig -- 自动转义，指定上下文 #}
{{ user_input | e('html') }}
{{ user_input | e('js') }}
```

### JavaScript（客户端）

**HTML 上下文编码：**

```javascript
function htmlEncode(str) {
    return String(str).replace(/[^\w. ]/gi, function(c) {
        return '&#' + c.charCodeAt(0) + ';';
    });
}

// 使用
element.innerHTML = htmlEncode(userInput);
element.textContent = userInput;  // 更简单且更安全
```

**JavaScript 字符串 Unicode 编码：**

```javascript
function jsEscape(str) {
    return String(str).replace(/[^\w. ]/gi, function(c) {
        return '\\u' + ('0000' + c.charCodeAt(0).toString(16)).slice(-4);
    });
}
```

### Java

**使用 OWASP Encoder 库（推荐）：**

```java
import org.owasp.encoder.Encode;

// HTML 上下文
String safeHtml = Encode.forHtml(userInput);

// HTML 属性上下文
String safeAttr = Encode.forHtmlAttribute(userInput);

// JavaScript 上下文
String safeJs = Encode.forJavaScript(userInput);

// URL 上下文
String safeUrl = Encode.forUriComponent(userInput);
```

**使用 Google Guava：**

```java
import com.google.common.html.HtmlEscapers;

String safeHtml = HtmlEscapers.htmlEscaper().escape(userInput);
```

### jQuery

```javascript
// 安全：使用 text() 设置文本
$('#element').text(userInput);

// 不安全：使用 html() 设置 HTML
$('#element').html(userInput);  // 如果 userInput 未编码，危险

// 不安全：将用户输入传递给选择器
$(userInput);  // 如果 userInput 以 < 开头，创建 HTML 元素

// 安全：如果需要用用户输入构建选择器
$(document.getElementById(userInput));  // 通过 ID 查找，不会解析 HTML
```

### React

```jsx
// 安全：默认 JSX 会自动转义花括号中的值
<div>{userInput}</div>  // 自动 HTML 转义

// 危险：dangerouslySetInnerHTML 不转义
<div dangerouslySetInnerHTML={{__html: userInput}} />

// 安全替代：使用 textContent 或其他安全方式呈现 HTML
```

### Vue.js

```html
<!-- 安全：模板语法自动转义 -->
<div>{{ userInput }}</div>

<!-- 危险：v-html 不转义 -->
<div v-html="userInput"></div>

<!-- 对于需要 HTML 的场景，使用 DOMPurify -->
<div v-html="sanitizedHtml"></div>
```

---

## 安全地处理富文本 HTML

有时业务需求要求允许用户提交有限的 HTML 标记。正确实现这一点极其困难。

### 推荐方案：DOMPurify

```javascript
// 客户端净化
import DOMPurify from 'dompurify';

var clean = DOMPurify.sanitize(userHtml, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'title', 'target']
});

element.innerHTML = clean;
```

### 备选方案：Markdown

让用户以 Markdown 格式提供内容，服务器端或客户端将 Markdown 转换为 HTML。这限制了可用的 HTML 标签集：

```javascript
// 使用 marked + DOMPurify
import { marked } from 'marked';
import DOMPurify from 'dompurify';

var html = marked.parse(userMarkdown);
var clean = DOMPurify.sanitize(html);
element.innerHTML = clean;
```

### 注意事项

- 所有 HTML 净化库都会不时发现 XSS 绕过漏洞，因此需持续关注安全更新
- 服务器端净化优于客户端净化（客户端净化可被绕过）
- 如果必须在客户端进行净化，在服务器端再次验证
- 除了 JavaScript，CSS 注入和普通 HTML 在某些情况下也可能有害

---

## 模板引擎安全

### 自动转义引擎

| 引擎 | 语言 | 默认转义 | 说明 |
|------|------|---------|------|
| **Jinja2** | Python | 是 | 自动 HTML 转义 `{{ var }}` |
| **Twig** | PHP | 是 | 自动转义，支持上下文参数 |
| **React JSX** | JavaScript | 是 | `{var}` 自动转义 |
| **Vue.js** | JavaScript | 是 | `{{ var }}` 自动转义 |
| **Angular** | TypeScript | 是 | 自动转义插值表达式 |
| **Thymeleaf** | Java | 是 | `th:text` 自动转义 |

### 手动转义引擎

| 引擎 | 语言 | 说明 |
|------|------|------|
| **ERB** | Ruby | 需要显式使用 `<%= escape_html(var) %>` |
| **Freemarker** | Java | 需要显式使用 `${var?html}` |
| **Blade** | PHP | 使用 `{{ $var }}` 自动转义，`{!! $var !!}` 不转义 |
| **EJS** | JavaScript | 使用 `<%= var %>` 自动转义，`<%- var %>` 不转义 |

> **关键警告：** 如果直接将用户输入拼接到模板字符串中（非引擎变量绑定），将面临服务端模板注入（SSTI）的风险，SSTI 通常比 XSS 更严重。

---

## 安全 Cookie 配置

```
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict; Path=/
```

| 标志 | 作用 | XSS 相关性 |
|------|------|-----------|
| **HttpOnly** | 禁止 JavaScript 读取 Cookie | 阻止 `document.cookie` 窃取会话令牌 |
| **Secure** | 仅通过 HTTPS 发送 | 防止中间人攻击窃取 Cookie |
| **SameSite** | 限制跨站请求发送 Cookie | 防止 CSRF；但不能防御同站 XSS |
| **Path** | 限制 Cookie 的路径范围 | 最小化 Cookie 暴露面 |

---

## 开发流程中的 XSS 防范

### 安全审查检查清单

在代码审查中检查以下 XSS 相关项：

- [ ] 所有将用户输入写入 HTML 的地方都使用了正确的输出编码
- [ ] 编码方式与输出上下文匹配（HTML body vs 属性 vs JavaScript vs URL vs CSS）
- [ ] 没有将用户输入直接放入 `eval()`、`new Function()`、`setTimeout(string)`、`setInterval(string)`
- [ ] 没有将用户输入直接赋值给 `innerHTML`、`outerHTML`、`document.write()`
- [ ] URL 经过验证（拒绝 `javascript:` 和 `data:` 协议）
- [ ] `textContent` 或 `innerText` 用于设置文本内容而非 `innerHTML`
- [ ] 用户上传的文件不被当作可执行脚本提供服务
- [ ] CSP 头已配置且策略合理（至少不包含 `unsafe-inline`）
- [ ] 所有 Cookie 适当地设置了 `HttpOnly`、`Secure` 和 `SameSite` 标志
- [ ] 模板引擎中未使用不安全的原始输出（如 `{!! !!}` 在 Blade 中）
- [ ] 富文本库（如 DOMPurify）已更新到最新版本

### 测试建议

| 测试类型 | 工具/方法 |
|----------|----------|
| 手动测试 | 在输入点注入 `<script>alert(1)</script>` 和 `<img src=x onerror=alert(1)>`，观察是否执行 |
| 自动化扫描 | Burp Suite Scanner 的 XSS 检测能力，可覆盖大多数反射型和存储型 XSS |
| DOM XSS 检测 | Burp Suite 的 DOM Invader 扩展（内置于 Burp 浏览器）|
| 代码审查 | 搜索危险 sink 函数：`innerHTML`、`document.write`、`eval`、`new Function` 等 |
| CSP 验证 | Google CSP Evaluator 在线工具，分析策略的安全性 |

---

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [Content Security Policy](../Content%20Security%20Policy/Content%20Security%20Policy.md) | [JavaScript for XSS](../JavaScript%20for%20XSS/JavaScript%20for%20XSS.md) | [CSRF](../../Cross-site%20request%20forgery%20(CSRF)/Cross-site%20request%20forgery%20(CSRF).md)
