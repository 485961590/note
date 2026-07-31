# CTF Web 测试系统方法论

> 适用对象：CTF Web 方向参赛者
> 前置知识：基础 HTTP 协议、常见漏洞原理（见 [[../../vuln-lab/OWASP-Top-10|OWASP Top 10]]）
> 核心原则：**观察优先于猜测。让应用告诉你它有什么漏洞。**
>
> 本文档是导航，不是手册。每个漏洞类型的深度内容在对应笔记中，这里的链接帮你快速找到它们。

---

## 整体框架：五阶段递进模型

```
Phase 1: 环境画像 (3-5 min)     --  不碰输入，先看是什么
Phase 2: 面枚举 (5-10 min)      --  摸清攻击面，记录所有入口
Phase 3: 行为观察 (5-8 min)     --  发送探测 payload，观察反应
Phase 4: 定向测试 (15-30 min)   --  根据观察形成假设，优先级测试
Phase 5: 确认与归档 (5 min)     --  确认漏洞，记 findings.md
```

每个阶段产出**明确的中间结果**，作为下一阶段的输入。不跳过阶段。

---

## 阶段一：环境画像 (Environment Profiling)

**目标**：在不触碰任何用户输入前，确定技术栈和后端特征。

**产出**：一张技术栈表，包括 Server、编程语言、框架、已知 URL 模式。

### 1.1 HTTP 响应头分析

```bash
curl -sI <target> | grep -iE "server|x-powered|x-frame|content-type|set-cookie"
```

关键信号：

| 响应头内容 | 推断 |
|-----------|------|
| `Server: Apache/2.4.41` | PHP 环境，可能支持 `.htaccess` |
| `Server: nginx/1.18` | 反向代理常见，后端可能是 PHP/Python/Node |
| `Server: openresty` | nginx + Lua，常见于 CTF 流量控制 |
| `Server: gws` | Google Web Server（GCP 部署） |
| `Server: Microsoft-IIS/10.0` | ASP.NET，可能支持 WebDAV |
| `X-Powered-By: PHP/7.3` | PHP 后端，可测伪协议 |
| `X-Powered-By: Express` | Node.js/Express |
| `X-Frame-Options: DENY` | 有安全头配置，可能不是简单挑战 |
| `Set-Cookie: JSESSIONID=...` | Java/Spring 或 Tomcat |
| `Set-Cookie: PHPSESSID=...` | PHP 会话 |
| `Set-Cookie: rememberMe=...` | Apache Shiro（Java 反序列化入口） |

### 1.2 技术栈指纹识别

```bash
# 使用 whatweb 或 wappalyzer（浏览器插件）
whatweb <target> -v
```

输出示例：
```
http://target:80 [200 OK] Apache[2.4.41], PHP[7.3.10], HTML5, MariaDB[...]
```

> 工具参考：[[../../Tools/信息收集/httpx|httpx 使用]]

### 1.3 URL 结构分析

观察 URL 模式，参数命名习惯本身就暗示漏洞类型：

| URL 模式                       | 可能暗示         |
| ---------------------------- | ------------ |
| `?page=about`、`?file=readme` | LFI / 路径遍历   |
| `?id=1`                      | SQL 注入或 IDOR |
| `?url=http://...`            | SSRF         |
| `?cmd=ls`                    | 命令注入         |
| `?search=keyword`            | SQL 注入或 XSS  |
| `?redirect=...`              | 开放重定向        |
| `?debug=1`                   | 调试信息泄露       |
| 结尾 `.php`、`.asp`、`.jsp`      | 语言类型直接暴露     |
| `/graphql` 或 `/api`          | GraphQL 注入   |
| WebSocket 连接（ws://）          | WebSocket 注入 |

### 1.4 状态码与错误页

```bash
# 触发错误看反应
curl -v <target>/nonexistent
curl -v <target>/index.php?=
curl -v -X INVALID <target>
```

- 404 返回自定义页面？还是框架默认错误？
- 500 会暴露文件路径和代码片段？
- 405 Method Not Allowed？检查允许哪些方法。
- 403 Forbidden？目录列表禁用了但可能可猜路径。

### 1.5 阶段一自检清单

- [ ] Server 头显示什么？
- [ ] X-Powered-By 或 Set-Cookie 透露了什么语言/框架？
- [ ] whatweb/httpx 输出确认了技术栈？
- [ ] URL 中有暗示参数用途的关键词（page/file/url/cmd）？
- [ ] 触发错误页后暴露了有用信息？

---

## 阶段二：面枚举 (Surface Enumeration)

**目标**：在发送任何漏洞 payload 之前，完整记录攻击面。

**产出**：攻击面清单——所有端点、所有输入点、所有 JavaScript 文件。

### 2.1 页面源码审查

这是你提到"查看源码看是否泄露"的步骤，但不止看注释：

```bash
curl -s <target> | tee index-source.html
```

重点找：
- HTML 注释：`<!-- -->`、`<!-- flag{...} -->`、`<!-- TODO: remove debug -->`
- 隐藏表单字段：`<input type="hidden" value="...">`
- 图片/CSS/JS 中嵌入的 base64 数据
- data 属性中的非公开信息
- 页面底部包含的 JS 文件路径
- `<script>` 块中内联的 JavaScript

### 2.2 JavaScript 文件分析

```
查看页面中引用的 .js 文件
检查每个 JS 文件内容，寻找：
- API 端点 URL（/api/、/graphql、/admin/...）
- 路由定义（React Router、Vue Router 的 path 映射）
- 硬编码的密钥/Token
- 注释掉的调试代码
- WebSocket 连接地址
```

对于现代前端 SPA 应用（React/Vue/Angular），JS 文件往往包含完整的 API 接口列表和业务逻辑。

### 2.3 目录与文件爆破

```bash
dirsearch -u <target> -w <wordlist>
```

> 工具参考：[[../../Tools/信息收集/dirsearch|dirsearch 使用]]

常用小型 wordlist 路径：
- `E:\note\wordlists\sensitive-files.txt`（敏感文件列表）
- `E:\note\wordlists\web-root-dirs.txt`（Web 根目录常见路径）

CTF 中常见的可发现文件：
- `/robots.txt` — 可能提示关键路径
- `/sitemap.xml` — 站点地图
- `/.git/` — Git 泄露（如果有则用 git-dumper）
- `/.git/config` — 直接验证
- `/flag`、`/flag.txt`、`/flag.php` — 有时直接暴露
- `/admin/`、`/admin.php`、`/manage/`
- `/api/`、`/api-docs/`、`/swagger/`
- `/backup/`、`/backup.sql`、`/www.zip`
- `/.env` — 环境变量泄露
- `/phpinfo.php` — PHP 配置信息

> Git 泄露工具参考：[[../../Tools/信息收集/git-dumper|git-dumper 使用]]

### 2.4 入口点枚举

按位置分类记录所有输入点：

| 输入位置 | 示例 | 记录要点 |
|---------|------|---------|
| URL 查询参数 | `?id=1&page=home` | 参数名、值类型（数字/字符串） |
| POST Body | 登录、搜索表单 | Content-Type、参数列表 |
| Cookie | 会话 Cookie、rememberMe | 加密/签名迹象 |
| HTTP 头 | User-Agent、Referer、X-Forwarded-For | 可能被记录或反射 |
| HTTP 方法 | PUT/DELETE/OPTIONS | 权限验证是否到位 |
| 文件上传 | 头像/附件上传 | 表单 enctype |
| WebSocket | ws:// 连接 | 消息格式 |

### 2.5 阶段二自检清单

- [ ] 查看页面源码，有无注释或隐藏信息？
- [ ] 所有 JavaScript 文件是否已提取并检查？
- [ ] dirsearch 运行完成，结果已记录？
- [ ] robots.txt、sitemap.xml 已检查？
- [ ] `.git/`、`.env`、`backup` 等敏感路径已测试？
- [ ] 所有输入点已列出（URL 参数、POST 字段、Cookie、头）？
- [ ] HTML 中有 `<form>` 元素？提交到哪个端点？

---

## 阶段三：行为观察 (Behavior Observation)

**目标**：对所有输入点发送一组标准探测 payload，观察应用如何响应。

**产出**：行为观察表——每个输入点 + 每组 payload + 响应模式 + 初步假设。

**这是整个方法论中最重要的新增步骤。** 在猜测漏洞类型之前，先收集行为证据。

### 3.1 标准探测 payload 集

对每个输入点，依次发送以下 payload（非同时，观察完一个再测下一个）：

| 序号 | Payload | 观察什么 |
|------|---------|---------|
| 1 | 正常值 | 基准响应 |
| 2 | `'`（单引号） | SQL 错误？被转义（多了反斜杠）？原样返回？ |
| 3 | `"`（双引号） | 同上，检查字符型注入 |
| 4 | `1/1`（数字型探测） | 是否被计算（1=1 正常，1/0 报错？） |
| 5 | `{{7*7}}` | 是否被计算为 49（SSTI 信号） |
| 6 | `${7*7}` | Freemarker/表达式注入 |
| 7 | `<test>` | 是否原样反射到 HTML（XSS 信号） |
| 8 | `../../etc/passwd` | 路径是否被操作（LFI 信号） |
| 9 | `sleep(5)` | 页面延迟（SQLi/命令注入延时信号） |
| 10 | 超长字符串（500+ 字符） | 截断行为、报错信息长度 |
| 11 | 特殊字符：`; | & \` $ () { } < >` | 命令注入、shell 元字符处理 |
| 12 | `' OR '1'='1` | SQLi 简易确认 |
| 13 | `\x00`（空字节） | 空字节截断、过滤器绕过 |
| 14 | UTF-8 多字节字符 | 宽字节注入信号 |

### 3.2 响应模式判断表

```text
观察到的响应  →  可能含义  →  推断方向
────────────────────────────────────────
"1/1" 正常，"1/0" 报错    → 数字型 SQL 上下文    → SQLi (数字型)
单引号触发 SQL 语法错误    → 字符型 SQL 上下文    → SQLi (字符型)
单引号被转义（前面加 \）   → 转义函数（addslashes）→ SQLi (需宽字节/编码绕过)
{{7*7}} 返回 49           → 模板引擎计算          → SSTI
{{7*7}} 原样返回           → 非模板或盲                 → 排除 SSTI
<test> 原样反射到 HTML     → 无 HTML 编码          → XSS (需要确认上下文)
<test> 被编码为 &lt;...&gt; → 有 HTML 编码         → XSS 概率降低
../../etc/passwd 返回文件  → 路径拼接              → LFI / 路径遍历
sleep(5) 有 5 秒延迟       → 执行延时函数          → SQLi 盲注 / 命令注入
页面标题或内容随输入变化    → 动态包含              → LFI / SSTI
; ls 返回目录列表           → 命令未转义            → 命令注入
输入出现在 Location 头中    → 重定向参数             → 开放重定向 / SSRF
Content-Type 头可控制       → MIME 类型可控          → XSS (CSP 绕过)
```

### 3.3 行为观察记录表模板

```markdown
## 行为观察记录

| 输入位置 | Payload | 响应模式 | 初步假设 | 优先级 |
|---------|---------|---------|---------|-------|
| ?id=1 | `1'` | SQL 语法错误: MySQL | SQLi | 最高 |
| ?search= | `{{7*7}}` | 返回 "49" | SSTI | 最高 |
| ?page= | `../../etc/passwd` | 返回文件内容 | LFI | 最高 |
```

### 3.4 阶段三自检清单

- [ ] 对每个输入点发送了 `'` 并记录了响应？
- [ ] 对每个输入点发送了 `{{7*7}}` 并记录了响应？
- [ ] 对每个输入点发送了 `<test>` 并记录了响应？
- [ ] 对每个输入点发送了 `../../etc/passwd` 并记录了响应？
- [ ] 对每个输入点发送了 `sleep(5)` 并记录了是否延迟？
- [ ] 对每个输入点发送了 `;` `|` `&` 等 shell 字符？

---

## 阶段四：漏洞假设与定向测试 (Targeted Testing)

**目标**：基于阶段三的行为观察，形成优先级列表，逐一测试并确认/排除漏洞类型。

**产出**：确认的漏洞类型 + 利用方法。

### 4.1 行为到漏洞的决策树

```
观察应用行为
    │
    ├─ 用户输入以未编码形式出现在页面 HTML 中
    │   ├─ 输入在 URL 参数中 → 反射型 XSS（高优先级）
    │   ├─ 输入从某个页面存储后在另一页面显示 → 存储型 XSS（高优先级）
    │   ├─ 输入出现在 <script> 上下文中 → XSS（最高优先级）
    │   └─ 输入出现在 JavaScript 字符串中 → DOM-based XSS（高优先级）
    │   → 参考: PortSwigger XSS 目录
    │
    ├─ 用户输入导致计算或错误
    │   ├─ {{7*7}} 返回 49 → SSTI（最高优先级）
    │   ├─ 数字或数学计算可见 → SSTI（高优先级）
    │   ├─ ' 触发 SQL 语法错误 → SQLi（最高优先级）
    │   ├─ ' 被转义 → SQLi 需绕过（中优先级）
    │   └─ XML 输入触发 XML 解析错误 → XXE（高优先级）
    │
    ├─ 用户输入导致文件操作
    │   ├─ ?page=... 参数 + PHP 服务器 → LFI / PHP 伪协议（最高优先级）
    │   ├─ 参数名是 file/include/template → LFI（高优先级）
    │   ├─ .html 后缀自动附加 → 路径遍历需截断/二次编码（中优先级）
    │   └─ ?download=... 下载文件 → 路径遍历（高优先级）
    │
    ├─ 用户输入导致系统命令执行
    │   ├─ ping/tracert/nslookup 功能 → 命令注入（最高优先级）
    │   ├─ 文件转换/调整大小功能 → 命令注入（高优先级）
    │   └─ ZIP 压缩/解压功能 → 命令注入 / Zip Slip（中优先级）
    │
    ├─ 页面提供文件上传功能
    │   ├─ 无扩展名校验 → 文件上传 RCE（最高优先级）
    │   ├─ 扩展名白名单 → MIME 类型绕过 / .htaccess（高优先级）
    │   ├─ 图片处理上传 → ImageMagick / SVG-XXE（中优先级）
    │   └─ 原文件名存储 → 路径遍历上传（中优先级）
    │
    ├─ 应用根据用户输入向外部 URL 发起请求
    │   ├─ ?url=、?target=、?redirect= 参数 → SSRF（最高优先级）
    │   ├─ Webhook/回调功能 → SSRF（高优先级）
    │   ├─ 图片 URL 抓取 → SSRF（中优先级）
    │   └─ 返回头中包含 Location: + 用户输入 → 开放重定向（高优先级）
    │
    ├─ 用户输入影响权限或身份验证
    │   ├─ Cookie 中的 user=0、admin=false → 授权篡改（高优先级）
    │   ├─ JWT 在 Authorization 头中 → JWT 攻击（高优先级）
    │   ├─ Cookie 中 rememberMe= 开头 → Shiro 反序列化（高优先级）
    │   ├─ Cookie 中 PHPSESSID 可穷举 → Session 固定化（中优先级）
    │   └─ POST 中有 user_id 但不可见表单 → IDOR（高优先级）
    │
    └─ 其他特殊情况
        ├─ 页面是纯静态 HTML → 信息收集/JS 分析挑战
        ├─ 响应 JSON API → 反序列化 / GraphQL 注入（高优先级）
        ├─ WebSocket 持续连接 → WS 消息注入（高优先级）
        ├── 多次相同请求返回不同结果 → 竞争条件（中优先级）
        └─ .git/ 可访问 → Git 泄露 → 源码审计
```

### 4.2 按漏洞类型的确认方法

一旦通过决策树锁定了候选漏洞类型，用最小 payload 快速确认：

| 漏洞 | 确认方法 |
|------|---------|
| SQLi（字符型） | `' AND '1'='1` 正常，`' AND '1'='2` 空白/不同 |
| SQLi（数字型） | `1 AND 1=1` 正常，`1 AND 1=2` 空白/不同 |
| SQLi（盲注） | `' AND SLEEP(5)-- ` 延迟 5 秒 |
| XSS（反射） | `<img src=x onerror=alert(1)>` 弹窗 |
| SSTI | `{{7*7}}` 返回 49；`${7*7}` 返回 49（Java） |
| LFI | `../../../etc/passwd` 内容返回 |
| PHP 伪协议 | `php://filter/convert.base64-encode/resource=index.php` |
| 命令注入 | `; id` 或 `| id` 返回命令输出 |
| SSRF | `?url=http://127.0.0.1:80` 访问到内部服务 |
| XXE | `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>` |
| 反序列化 | `O:1:"A":0:{}` 返回异常或 __destruct 触发 |
| JWT | 修改 alg 为 none、替换密钥、KID 注入 |

### 4.3 "该换方向了"的判断信号

如果以下情况发生，很可能假设错误，应切换漏洞类型：

- 发送确认 payload 后，响应与正常请求**完全一致**（无任何变化）
- payload 中所有特殊字符都被完整转义/编码
- 应用返回了不可理解的输出（不是预期漏洞类型的特征）
- 测试了 3 种以上相关 payload 均无反应

此时退回 Phase 3 观察表，看下一个优先级假设。

### 4.4 阶段四自检清单

- [ ] 从 Phase 3 观察表提取了至少 2-3 个最可能的假设？
- [ ] 用最小确认 payload 测试最高优先级假设？
- [ ] 确认了漏洞类型再深入利用，而非跳过确认？
- [ ] 技术栈和漏洞类型匹配？（PHP 不测 SSTI，Flask 不测伪协议）
- [ ] 一个假设被排除后，有下一个假设接上？

---

## 阶段五：确认与归档 (Confirmation & Documentation)

**目标**：确认漏洞存在后，记录 findings，决定继续利用还是切换目标。

**产出**：findings.md + attack-report.md

### 5.1 归档结构

按照现有 CTF writeup 规约，每个挑战使用独立目录：

```
<challenge-name>/
├── recon/          # Phase 1-2 收集的原始信息
│   ├── headers.txt         # HTTP 响应头
│   ├── index-source.html   # 页面源码
│   ├── whatweb.txt         # 技术栈识别输出
│   ├── dirsearch-output.txt # 目录扫描结果
│   ├── robots.txt          # 如有
│   └── ...
├── exploits/       # 脚本和 payload 文件
│   ├── exploit.py
│   └── payloads.txt
├── flags/          # flag 记录
│   └── flag.txt
├── logs/           # Burp 流量、日志
├── attack-report.md   # 完整攻击报告
└── findings.md        # 发现总结
```

### 5.2 findings.md 模板

```markdown
# Findings: <challenge-name>

## Vulnerability 1: [类型]

- **位置**: URL/参数/端点
- **发现方式**: Phase 3 观察到的 [行为] 引导测试 [payload]
- **确认 payload**: `...`
- **利用方法**: [一句话说明]
- **Flag**: [如有]
- **参考资料**: [[../../vuln-lab/...|笔记链接]]

## 其他发现

- [ ] 信息点1
- [ ] 信息点2
```

### 5.3 递归思维

在一个阶段卡住超过 10 分钟 → 退一步检查是否遗漏了上一阶段的信息：

```
卡在 Phase 4（找不到漏洞）
    → 退回 Phase 3：有输入点遗漏了探测？
    → 退回 Phase 2：dirsearch 跑完了没有？
    → 退回 Phase 1：技术栈识别正确吗？有没有漏看 HTTP 头？
```

> 参考现有 CTF writeup 结构：[[../../vuln-lab/hack/dasctf-easysql-stacked|dasctf-easysql-stacked 示例]]

---

## 技术栈专项测试路径

根据 Phase 1 识别的技术栈，优先关注以下方向。

### PHP 后端

```
├─ LFI / PHP 伪协议 → 参考 伪协议文件读取清单
├─ SQL 注入         → 参考 SQL 注入探测方法论
├─ PHP 反序列化     → 参考 PHP Deserialization 笔记
├─ PHP 类型混淆     → 参考 Code Review/php-type-juggling-flag
├─ file_put_contents / 文件写入 RCE
├─ include/require 函数导致本地文件包含
├─ $_GET/$_POST/$_SERVER 变量覆盖
├─ preg_replace /e 模式（PHP < 7）代码执行
└─ create_function 注入（PHP < 7.2）
```

> 参考：[[../../Code Review/simple-user-system-php-audit|PHP 代码审计示例]]

### Python/Flask/Django 后端

```
├─ SSTI (Jinja2)    → 参考 Server-Side Template Injection 笔记
├─ Werkzeug Debug Console（/console）
├─ Pickle 反序列化（通过 Cookie 或 API）
├─ Python path traversal（send_file）
├─ 服务器端模板包含（Server-Side Template Include）
├─ Django ORM SQL 注入（extra()、RawSQL）
└─ Flask session Cookie 解密/篡改
```

### Java/Spring 后端

```
├─ Spring Boot Actuator 端点暴露
│   /actuator/  /actuator/env  /actuator/heapdump
├─ Shiro rememberMe 反序列化
├─ Struts2 RCE（S2-xxx 系列）
├─ Jackson 反序列化
├─ JWT 算法混淆 / 密钥爆破
├─ JNDI 注入（Log4j RCE）
├─ SpEL 表达式注入（参数中 ${expression}）
└─ 目录遍历（..;/ 等 Tomcat 特性）
```

### Node.js/Express 后端

```
├─ 服务端 JavaScript 注入（res.render 中的 user input）
├─ 原型链污染（Prototype Pollution）
├─ Pug/EJS/Handlebars SSTI
├─ res.sendFile 路径遍历
├─ express-session 反序列化
├─ eval/Function 构造器注入
├─ 路径遍历（__dirname 拼接）
└─ npm 依赖混淆（恶意包引入）
```

### ASP.NET/IIS 后端

```
├─ ViewState 反序列化（__VIEWSTATE 参数）
├─ IIS 短文件名泄露（~1 后缀）
├─ WebDAV PUT 上传
├─ .NET 反序列化（Soap/JSON/Binary）
├─ MachineKey 爆破（ViewState MAC 禁用时）
└─ IIS HTTP 方法覆盖（X-HTTP-Method-Override）
```

---

## 源码辅助测试路径

当通过 git 泄露、php://filter 解码、或 CTF 直接提供源码时，从无源码模式切换到代码审计模式。

### 审计目标优先级

```
1. 入口点 → 找出所有接收用户输入的变量
   PHP: $_GET, $_POST, $_REQUEST, $_COOKIE, $_SERVER
   Python: request.args, request.form, request.json, request.cookies
   Java: @RequestParam, @PathVariable, @RequestBody, getParameter()

2. 追踪数据流向 → 用户输入经过哪些函数/赋值
   gzdecode() → serialize/unserialize → eval → system → include

3. 标记危险函数（sink）→ 所有可执行/可写入/可包含的危险函数
   PHP: eval(), system(), exec(), unserialize(), include(), file_put_contents()
   Python: exec(), eval(), os.system(), subprocess.run(), pickle.loads()
   Java: Runtime.exec(), ProcessBuilder.start(), Method.invoke()

4. 检查过滤/转义
   addslashes() → 是否配合了错误编码？→ 宽字节注入
   preg_match() blacklist → 是否有小写/编码/双写可绕过
   htmlspecialchars() → 是否加对了 ENT_QUOTES 参数

5. 寻找旁路
   ─ 有 WAF/黑名单 → 双写、大小写、编码、注释符拆分
   ─ 有输入长度限制 → 截断是否安全
   ─ 有类型检查 → is_numeric() 能否被浮点数绕过
```

> 参考：[[../../Code Review|Code Review 目录]]（14 份 PHP 代码审计文档）

---

## 工具阶段映射

```
Phase 1 (环境画像):
  whatweb / httpx  → 技术栈识别
  curl -sI         → HTTP 头分析
  Burp proxy       → 观察全部请求/响应

Phase 2 (面枚举):
  dirsearch        → 目录爆破
  git-dumper       → Git 泄露下载
  subfinder        → 子域名枚举（SRC 场景）
  curl -s          → 页面源码获取
  Burp Spider      → 自动抓取链接

Phase 3 (行为观察):
  curl 手动构造    → 逐个发送探测 payload
  Burp Repeater    → 参数修改后重发
  Burp Intruder    → 批量参数测试

Phase 4 (定向测试):
  Burp Repeater    → 手工 payload 调整
  sqlmap           → 自动 SQL 注入利用
  Python 脚本      → 自定义 payload 生成/发送
  gobuster/ffuf    → 参数 fuzzing

Phase 5 (归档):
  VS Code / 文本编辑器 → 编写 findings.md
  截图/日志导出         → 保存证据
```

---

## 跨文档引用索引

每个漏洞类型映射到笔记仓库中已有的深度内容：

| 漏洞类型 | 主文档 | 辅助文档 |
|---------|-------|---------|
| SQL 注入 | [[../../vuln-lab/SQL-Injection-探测方法论\|SQL 注入探测方法论]] | [[../../vuln-lab/PortSwigger Web Security Academy/SQL-Injection/\|PortSwigger SQLi]] |
| 伪协议/LFI | [[../../vuln-lab/伪协议文件读取-信息枚举清单\|伪协议文件读取清单]] | [[../../vuln-lab/hack/cisppte-lfi-phpfilter\|CISPPTE LFI 实战]] |
| SSTI | [[../../vuln-lab/Server-Side Template Injection (SSTI)/\|SSTI 笔记]] | [[../../vuln-lab/hack/dasctf-shrine-ssti\|Shrine SSTI]] |
| XSS | [[../../vuln-lab/PortSwigger Web Security Academy/Cross-site scripting (XSS)/\|PortSwigger XSS]] | [[../../vuln-lab/PortSwigger Web Security Academy/Cross-site scripting (XSS)/JavaScript for XSS\|JS for XSS]] |
| CSRF | [[../../vuln-lab/PortSwigger Web Security Academy/Cross-site request forgery (CSRF)/\|PortSwigger CSRF]] | CORS / SameSite |
| CORS | [[../../vuln-lab/PortSwigger Web Security Academy/Cross-origin resource sharing (CORS)/\|PortSwigger CORS]] | CSRF / SOP |
| Clickjacking | [[../../vuln-lab/PortSwigger Web Security Academy/Clickjacking/\|PortSwigger Clickjacking]] | CORS / CSP |
| XXE | [[../../vuln-lab/XML External Entity (XXE)/\|XXE 笔记]] | 伪协议文件读取清单 |
| PHP 反序列化 | [[../../vuln-lab/PHP Deserialization/\|PHP Deserialization]] | [[../../Code Review/php-deserialization-wakeup-bypass\|wakeup 绕过]] |
| 类型混淆 | [[../../Code Review/php-type-juggling-flag\|PHP Type Juggling]] | — |
| 命令注入 | [[../../vuln-lab/hack/dasctf-cmdexec\|命令注入实战]] | — |
| DOM 漏洞 | [[../../vuln-lab/PortSwigger Web Security Academy/DOM-based vulnerabilities/\|PortSwigger DOM]] | [[../../Code Review\|Code Review DOM XSS 系列]] |
| OWASP 框架 | [[../../vuln-lab/OWASP-Top-10\|OWASP Top 10]] | 全部漏洞文档 |

---

## 未覆盖到的漏洞类型（尚待补充笔记）

以下漏洞类型当前在方法论中有检测手段，但仓库内尚无独立的深度利用笔记：

- File Upload 绕过与 WebShell 部署 → 当前仅有 wordlist 可用
- SSRF 绕过与云元数据访问 → 检测方法在决策树中已有
- JWT 攻击（alg none、密钥爆破、KID 注入）→ 检测方法在阶段四已有
- GraphQL 注入（introspection、批量查询）→ 检测方法在阶段一已有
- 竞争条件（Race Condition）→ 检测方法在阶段四已有
- WebSocket 消息注入 → 检测方法在阶段四已有

上方第 5 列的 `辅助文档` 中标记为 `—` 的项，是后续补全笔记的候选方向。

---

## 常见陷阱

### 陷阱 1：跳过阶段直接测试

```
拿了 URL 直接测 SQL 注入 → 测了 10 分钟没反应
    → 回头发现是 Node.js + MongoDB → NoSQL 注入
```

**解法**：强制自己过完 Phase 1 再做测试。技术栈都不知道，payload 都是瞎蒙。

### 陷阱 2：只测一种输入位置

```
只测 URL 参数 → 漏洞在 POST Body 里
只测 GET → 漏洞在 Header/Cookie 里
```

**解法**：Phase 2 完整记录所有输入位置，Phase 3 对每个位置都发送探测。

### 陷阱 3：payload 没反应就放弃

```
{{7*7}} → 返回 "{{7*7}}"（原样）→ "不是 SSTI"
    → 实际是 Python 模板但 {{ }} 被转义了，需试 {% %}
    → 或者服务端是 Java 模板需试 ${7*7}
```

**解法**：一个 payload 没反应不代表该类型不存在，换该类型的另一种语法试。

### 陷阱 4：确认和利用混为一谈

```
看到 SQL 报错就认为利用了 → 直接开始注入语句
    → 漏了判断闭合方式、漏了判断是否过滤关键词
```

**解法**：阶段四要求先确认（"这是个 SQL 注入"），再进入利用。确认步只用一个最小 payload 验证漏洞存在。

---

## 方法论速查卡

```text
首次访问 URL
  │
  ├─ Phase 1: curl -sI → whatweb → URL结构分析 → 技术栈表
  │
  ├─ Phase 2: 源码审查 → JS分析 → dirsearch → 输入点清单
  │
  ├─ Phase 3: 对每个输入点发送探测集 → 行为观察表
  │
  ├─ Phase 4: 决策树匹配 → 优先级假设 → 最小确认
  │     │
  │     ├─ 确认 → 继续利用 → 写 findings
  │     └─ 排除 → 下一个假设 → Phase 4 循环
  │
  └─ Phase 5: 归档 → attack-report.md + findings.md

总时长参考: 20-50 分钟完成一轮完整流程
```

---

> 本文档不替代任何漏洞类型的深度笔记，而是告诉你**什么时候需要打开哪份笔记**。
> 如有 bug 或改进建议，直接更新本文档。
