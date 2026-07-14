# httpx

> HTTP 探测与指纹识别工具，批量请求网站首页，获取状态码、标题、技术栈
> 项目地址: https://github.com/projectdiscovery/httpx

---

## 工作原理

向域名列表批量发送 HTTP/HTTPS GET 请求（只请求首页），分析响应中的状态码、页面标题、响应头、HTML 源码，识别技术栈指纹。

**合规性**：相当于你用浏览器逐个打开网页看一眼首页就关掉。**需要限速，否则大量并发请求会被目标封 IP。**

---

## 安装

```bash
# Kali / Debian
sudo apt install httpx

# Go 安装
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# 预编译二进制（网络不好时用）
wget https://github.com/projectdiscovery/httpx/releases/latest/download/httpx_linux_amd64.zip
unzip httpx_linux_amd64.zip
mv httpx /usr/local/bin/
```

---

## 基本用法

```bash
# 最常用：标题 + 状态码 + 技术栈指纹 + 限速
httpx -l resolved.txt -title -status-code -tech-detect -rl 10 -o alive.txt

# 管道输入
echo "example.com" | httpx

# 静默模式
httpx -l domains.txt -silent
```

---

## 常用参数

### 输入输出

| 参数 | 作用 |
|------|------|
| `-l` | 输入文件 |
| `-o` | 输出文件 |
| `-oJ` | JSON 格式输出 |
| `-silent` | 静默模式 |

### 显示内容

| 参数                | 作用                 |
| ----------------- | ------------------ |
| `-title`          | 提取页面 `<title>` 标签  |
| `-status-code`    | HTTP 状态码           |
| `-tech-detect`    | 技术栈指纹识别            |
| `-content-length` | 响应体大小              |
| `-ip`             | 响应 IP 地址           |
| `-cname`          | CNAME 记录           |
| `-websocket`      | WebSocket 检测       |
| `-web-server`     | 提取 Web 服务器类型       |
| `-location`       | 跟随重定向并显示最终 URL     |
| `-favicon`        | 获取 favicon 哈希（指纹）  |
| `-hash`           | 响应体哈希（去重用）         |
| `-jarm`           | JARM 指纹（TLS 服务端识别） |

### 速度控制（重要）

| 参数 | 作用 |
|------|------|
| `-rl` | 每秒请求数限制（**建议 5-10**） |
| `-t` | 并发线程数 |
| `-timeout` | 单个请求超时时间（秒） |
| `-retries` | 失败重试次数 |

### 探测配置

| 参数 | 作用 |
|------|------|
| `-ports` | 指定端口（如 `80,443,8080,8443`） |
| `-path` | 请求指定路径 |
| `-follow-redirects` | 跟随重定向 |
| `-http-proxy` | 使用 HTTP 代理 |
| `-no-color` | 纯文本输出 |

### 过滤

| 参数 | 作用 |
|------|------|
| `-fc` | 过滤状态码（排除） |
| `-mc` | 匹配状态码（包含） |
| `-fl` | 过滤响应大小 |
| `-ml` | 匹配响应大小 |
| `-fep` | 过滤标题中的正则 |
| `-mep` | 匹配标题中的正则 |

---

## 使用示例

### 标准信息收集流程

```bash
# 基础扫描：标题 + 状态码 + 技术栈 + web服务器类型
httpx -l subs.txt -title -status-code -tech-detect -web-server -rl 10 -o alive.txt

# 输出示例：
# https://jw.cdcas.edu.cn [成都文理学院-教务处] [200] [Apache HTTP Server,HSTS,jQuery]
```

### 提取具体信息

```bash
# 只看 200 的
httpx -l subs.txt -mc 200 -title -tech-detect -rl 10

# 排除 403/404
httpx -l subs.txt -fc 403,404 -title -tech-detect -rl 10

# 找出所有 WordPress 站点
httpx -l subs.txt -tech-detect -rl 10 | grep -i "wordpress"

# 找出所有有登录页标题的站点
httpx -l subs.txt -mep "登录|Login|Sign in" -rl 10
```

### 指定端口探测

```bash
# 高校常见非标端口
httpx -l subs.txt -ports 80,443,8080,8443,8000,8888 -title -rl 10
```

### JSON 输出（方便后续处理）

```bash
httpx -l subs.txt -title -status-code -tech-detect -oJ -o output.json
```

JSON 输出包含：URL、状态码、标题、技术栈列表、响应大小、IP、CNAME 等完整信息。

---

## 技术栈指纹

httpx 能识别的主要技术栈类别：

| 类别 | 常见识别结果 |
|------|-------------|
| Web 服务器 | Apache, Nginx, IIS, Tomcat, Caddy |
| 编程语言 | PHP, Java, Python (Django/Flask), ASP.NET |
| JS 框架 | jQuery, React, Vue.js, Angular |
| CMS | **WordPress**, Drupal, Joomla, DedeCMS |
| CDN/WAF | Cloudflare, 阿里云 CDN, 腾讯云 CDN, Baidu Yunjiasu |
| 中间件 | WebLogic, WebSphere, JBoss, Shiro |

---

## 实战筛选策略

httpx 结果出来后，按以下优先级筛选目标：

1. **WordPress** — 插件多、历史漏洞多，最常见入口
2. **Tomcat / WebLogic / Shiro** — Java 中间件，高危 RCE 多
3. **PHP + 无框架** — 自研系统，大概率没做安全防护
4. **老旧的 jQuery 版本** — 老 jQuery = 老系统 = 老代码
5. **标题含"管理"/"后台"/"Admin"** — 后台系统，攻击面大

---

## 注意事项

- **必须限速 `-rl 10`**：不加这个参数默认全速并发，可能在几秒内发出上百请求，触发目标安全设备告警
- **不要加 `-path` 扫目录**：httpx 的 `-path` 可以向指定路径发请求，不要用它做目录爆破
- **CLOUDFLARE/阿里云 CDN 标记**：如果 `-tech-detect` 显示 CDN，说明目标在 CDN 后面，真实 IP 被隐藏
- **结果可能不全**：有些系统需要特定 `Host` 头才能正常响应，httpx 可能拿到 403/404 误判为无效
