# DOM-based Open Redirection via URL 参数

> 案例来源：PortSwigger Web Security Academy — "DOM-based open redirection"
> 利用 URL: `https://victim.com/post?postId=6&url=https://exploit-server.net/`

## 审计源码

```html
<a href='#' onclick='returnUrl = /url=(https?:\/\/.+)/.exec(location); location.href = returnUrl ? returnUrl[1] : "/"'>Back to Blog</a>
```

---

## 漏洞等级：中危（可用于钓鱼攻击，不可执行 JS）

---

## 一、漏洞代码

页面中 "Back to Blog" 链接的 onclick 处理：

```html
<a href='#' onclick='returnUrl = /url=(https?:\/\/.+)/.exec(location); location.href = returnUrl ? returnUrl[1] : "/"'>Back to Blog</a>
```

人话翻译：

1. 从当前页面 URL 中用正则抓取 `url=` 后面的地址
2. 如果抓到了 → 跳转过去
3. 没抓到 → 跳转首页 `/`

### 1.1 什么是 DOM-based？与传统服务端重定向的区别

同样是 URL 参数导致的跳转，"DOM-based" 和"服务端"的数据流向完全不同。

**传统服务端重定向（Server-side Open Redirect）：**

```
用户访问 → 服务器收到请求 → 服务器读取参数 → 服务器返回302跳转指令 → 浏览器跳转
          ↑                 ↑
    数据到达服务器      漏洞在服务器端

数据流向：URL参数 → 发送到服务器 → 服务器处理 → 返回响应
```

服务端代码示例（PHP）：

```php
<?php
    $url = $_GET['url'];        // 服务器读取参数
    header("Location: $url");   // 服务器发送跳转指令
?>
```

**DOM-based 重定向（本题）：**

```
用户访问 → 浏览器加载页面 → JavaScript读取当前URL → 浏览器执行跳转
                                ↑
                         数据从未离开浏览器！

数据流向：URL参数 → 直接在浏览器中被JavaScript读取 → 浏览器执行跳转
```

客户端代码示例（JavaScript）：

```javascript
var url = location.href;                        // 浏览器读取URL
var match = /url=(.+)/.exec(url);               // 浏览器解析参数
location.href = match[1];                       // 浏览器自己跳转
```

**关键区别：**

| | 服务端重定向 | DOM-based 重定向 |
|---|---|---|
| 数据在哪处理 | 服务器 | 浏览器（JavaScript） |
| 服务器日志有无记录 | 有（请求到达了服务器） | 无（JS 读取 URL 不产生网络请求） |
| WAF/IDS 能否检测 | 能（检查 HTTP 请求） | 不能（数据不出浏览器） |
| HTTP 响应状态码 | 302/301 | 200（页面正常返回） |
| 审计需要看 | 服务端代码 | 前端 JS 代码 |

这也是为什么 DOM-based 漏洞更隐蔽——它完全绕过了服务端安全设备和日志。

---

## 二、代码逐段拆解

### 2.1 `location`

`location` 是浏览器内置对象，代表当前页面的完整 URL。

```
https://victim.com/post?postId=6&url=https://evil.com
                                                    ↑
                                              location 就是这个完整字符串
```

### 2.2 正则 `/url=(https?:\/\/.+)/`

```
/url=(https?:\/\/.+)/
  │    ││││││││││││
  │    │││││││││││└ +  匹配一次或多次（贪婪模式）
  │    ││││││││││└── .  匹配任意字符（除换行）
  │    │││││││││└──── /  转义后的斜杠
  │    ││││││││└───── /  转义后的斜杠
  │    │││││││└────── :  字面冒号
  │    ││││││└─────── s  字面 s
  │    │││││└──────── p  字面 p
  │    ││││└───────── t  字面 t
  │    │││└────────── t  字面 t
  │    ││└─────────── h  字面 h
  │    │└──────────── ?  前面的 s 可选 → 匹配 http:// 或 https://
  │    └───────────── 匹配字面字符串 "url="
  └────────────────── 正则定界符
```

捕获组 `()` 里的内容会被存入结果数组的 `[1]` 位置。

### 2.3 `.exec(location)` — 执行匹配

```javascript
/url=(https?:\/\/.+)/.exec("https://victim.com/post?postId=6&url=https://evil.com")
```

匹配过程：

```
https://victim.com/post?postId=6&url=https://evil.com
                                  ↑
                                 从 url= 开始匹配
                                          ↑
                                          捕获组开始
                                            ↑
                                            匹配到 https://evil.com
                                                          ↑
                                                          捕获组结束（到字符串末尾）
```

返回结果：

```javascript
returnUrl = [
    "url=https://evil.com",   // [0] 完整匹配
    "https://evil.com"        // [1] 第一个捕获组 ← 这个会被拿去跳转
]
```

### 2.4 三元运算符 + 跳转

```javascript
location.href = returnUrl ? returnUrl[1] : "/";
//             ↑            ↑               ↑
//             检查是否匹配  匹配成功：跳转    匹配失败：回家
```

逻辑等价于：

```javascript
if (returnUrl) {
    location.href = "https://evil.com";  // 跳转到攻击者站点
} else {
    location.href = "/";                 // 回首页
}
```

---

## 三、攻击链

```
攻击链：

1. 攻击者构造钓鱼链接发给受害者：`https://victim.com/post?postId=6&url=https://evil-fake-login.com`
2. 受害者点击链接，victim.com 正常渲染博客内容（看起来完全合法）
3. 受害者看到 "Back to Blog" 链接，点击
4. onclick 触发 → 正则从 URL 提取 `https://evil-fake-login.com`
5. `location.href` 跳转到攻击者站点
6. 受害者被重定向到伪造登录页，可能输入凭据
```

**利用场景：**

攻击者将带 `url=` 参数的链接发给受害者。受害者看到域名是 `victim.com`，以为安全，点击后页面也确实显示了正常博客内容。但当他们点击 "Back to Blog" 时，被重定向到攻击者的伪造登录页，以为是正常跳转，输入凭据。

---

## 四、为什么正则限制了 `https?://` 不是安全的

```javascript
/url=(https?:\/\/.+)/
       ↑
       只匹配 http:// 和 https:// 开头的 URL
```

这确实阻止了 `javascript:alert(1)` 这样的 payload：

```
url=javascript:alert(1)  → 正则不匹配 → 跳首页 → 不可利用
```

但问题不在这里。正则**允许任意 HTTP(S) 地址**，而攻击者完全可以自己注册一个域名：

```
url=https://evil-phishing-site.com
```

这是合法 HTTPS URL，正则放行，用户被重定向。所以正则在这里不是安全措施——它只限制了协议格式，没限制目标。

---

## 五、Source → Sink

```
Source: location（当前页面 URL，攻击者可通过发送链接完全控制）
    ↓
Sanitization: 正则 /url=(https?:\/\/.+)/
              ├── 限制了协议为 http/https ✓
              └── 未限制目标域名 ✗
    ↓
Sink: location.href = returnUrl[1]（跳转到攻击者指定的地址）
```

| 层面 | 问题 |
|------|------|
| Source | URL 参数完全由攻击者构造（发链接即可） |
| 域名限制 | 无 — 任意域名的 HTTPS URL 都放行 |
| 用户感知 | 点击前不知道会跳到哪里（href="#" 看不到真实目标） |

---

## 六、Open Redirection vs XSS 的区别

很多初学者容易把两者搞混：

| | Open Redirection | XSS |
|---|---|---|
| 能做什么 | 把用户导航到攻击者的网站 | 在目标网站执行任意 JS |
| 危害 | 钓鱼（伪造登录页窃取凭据） | 偷 Cookie、篡改页面、盗取数据 |
| 能否读目标站点的 Cookie | 不能（到了攻击者域） | 能（代码在目标域执行） |
| 漏洞等级 | 中危 | 高危 |
| 本案例 | `location.href` 跳转到外部 URL | 不成立（正则限制 `https?://` 阻止了 `javascript:`） |

**本题为什么不是 XSS：** 如果正则没限制协议前缀，攻击者传 `url=javascript:alert(1)` 就能执行 JS，那就是 DOM XSS。但正则要求 `http(s)://` 开头，所以只是 open redirect。

---

## 七、修复方案

### 7.1 根本修复：不把跳转目标放在 URL 参数中

用相对路径或内部路由标识符代替完整 URL：

```javascript
// 不要这样：url 参数是完整 URL
onclick="location.href = getUrlParam('url')"

// 改为：只接受路径部分，强制在同域内
onclick="location.href = '/' + getUrlParam('page')"
```

### 7.2 白名单域名校验

如果必须支持外部跳转，维护一个允许跳转的域名白名单：

```javascript
var returnUrl = /url=(https?:\/\/.+)/.exec(location);
if (returnUrl) {
    try {
        var parsed = new URL(returnUrl[1]);
        var allowedHosts = ['trusted-partner.com', 'cdn.example.com'];
        if (allowedHosts.includes(parsed.hostname)) {
            location.href = returnUrl[1];
        } else {
            location.href = "/";
        }
    } catch(e) {
        location.href = "/";
    }
} else {
    location.href = "/";
}
```

### 7.3 中间跳转确认页（用户体验方案）

```
跳转前显示："你即将离开本站前往 https://evil.com，是否继续？"
```

这不能阻止攻击，但用户有机会发现异常。

---

## 八、关联知识

- **CWE-601**: URL Redirection to Untrusted Site ('Open Redirect')
- **OWASP Top 10 (2021)**: A01 Broken Access Control（Open Redirect 常被归入此类）
- **PortSwigger**: "DOM-based open redirection" 实验
- **利用链**: Open Redirect 常用于 OAuth 流程滥用、钓鱼攻击的跳板、绕过 SSRF 的地址白名单
