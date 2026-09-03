# Katana Web 爬虫实用指南

Katana 是 ProjectDiscovery 开源的高速 Web 爬虫，主要用于从一个或多个入口 URL 发现站内链接、接口路径、静态资源、JavaScript 文件和带参数的 URL。

Katana 会向目标发送 HTTP/HTTPS 请求。开启 JavaScript 或 Headless 模式后，请求量和资源消耗会明显增加。以下命令只适用于自己控制的站点、靶场或明确授权的测试范围。

Katana 负责发现 URL，不负责漏洞利用，也不等同于目录爆破工具。发现结果通常交给 httpx 做存活和指纹确认，再交给 ffuf 等工具进行授权范围内的定向测试。

项目地址：https://github.com/projectdiscovery/katana

## 1. 安装与检查

### Go 安装

~~~bash
go install github.com/projectdiscovery/katana/cmd/katana@latest
~~~

如果提示找不到命令，检查 Go 的 bin 目录是否已加入 PATH：

~~~bash
go env GOPATH
~~~

也可以从项目 Releases 下载对应操作系统和 CPU 架构的预编译文件，解压后将 katana 所在目录加入 PATH。

检查是否安装成功：

~~~bash
katana -version
katana -h
~~~

不同版本的参数可能略有差异，以当前版本的 katana -h 输出为准。

## 2. 基本用法

### 爬取单个站点

~~~bash
katana -u https://example.com
~~~

指定爬取深度：

~~~bash
katana -u https://example.com -d 2
~~~

深度越大，请求量增长越快。第一轮通常从 d 2 开始。

只输出 URL，适合接入管道：

~~~bash
katana -u https://example.com -silent
~~~

保存结果：

~~~bash
katana -u https://example.com -d 2 -silent -o urls.txt
~~~

### 从文件读取入口

准备 urls.txt，一行一个完整 URL：

~~~text
https://example.com
https://app.example.com
https://admin.example.com
~~~

批量爬取：

~~~bash
katana -list urls.txt -d 2 -silent -o crawl.txt
~~~

也可以使用管道：

~~~bash
cat urls.txt | katana -d 2 -silent -o crawl.txt
~~~

入口最好带有 http:// 或 https:// 协议。只有域名时，先用 httpx 探测出可访问的 URL，再交给 Katana。

## 3. 常用参数速查

### 目标与爬取

| 参数 | 作用 |
|------|------|
| -u URL | 指定单个入口 URL |
| -list FILE | 从文件读取入口 URL |
| -d N | 设置最大爬取深度 |
| -jc | 爬取 JavaScript 文件中发现的链接 |
| -jsl | 从 JavaScript 内容中提取链接 |
| -xhr | 提取和显示 XHR 请求相关的 URL |
| -headless | 使用浏览器渲染页面，处理部分动态站点 |
| -kf all | 请求常见已知文件，如 robots.txt、sitemap.xml |
| -ct DURATION | 设置单次任务最长运行时间 |

### 请求与网络

| 参数 | 作用 |
|------|------|
| -H HEADER | 添加自定义请求头，可重复使用 |
| -proxy URL | 通过 HTTP、HTTPS 或 SOCKS5 代理 |
| -timeout N | 单个请求超时时间，单位为秒 |
| -retry N | 请求失败后的重试次数 |
| -c N | 单个目标的并发请求数 |
| -p N | 并行处理的目标数量 |
| -rl N | 每秒请求数限制 |
| -rlm N | 每分钟请求数限制 |

### 作用域控制

| 参数 | 作用 |
|------|------|
| -scope REGEX | 只爬取匹配正则的 URL |
| -out-scope REGEX | 排除匹配正则的 URL |
| -no-scope | 关闭默认作用域限制，谨慎使用 |

### 输出

| 参数 | 作用 |
|------|------|
| -o FILE | 保存结果到文件 |
| -json | 以 JSON 格式输出 |
| -silent | 只输出结果，隐藏额外提示 |

参数名称和默认值可能随版本变化。某个参数无法识别时，优先查看：

~~~bash
katana -h
~~~

## 4. 推荐爬取方式

### 4.1 普通站点快速爬取

适合第一轮发现站内链接：

~~~bash
katana -u https://example.com \
  -d 2 \
  -rl 5 \
  -silent \
  -o urls.txt
~~~

先使用较浅深度和较低速率确认结果，再决定是否扩大范围。

### 4.2 JavaScript 站点

前端路由、接口地址和参数名可能写在 JavaScript 文件中：

~~~bash
katana -u https://example.com \
  -d 3 \
  -jc \
  -jsl \
  -silent \
  -o urls-js.txt
~~~

jc 和 jsl 会增加 JavaScript 请求和解析时间。对普通静态站点不必默认开启。

### 4.3 动态页面和 XHR

页面内容由 JavaScript 加载时，使用 Headless 模式：

~~~bash
katana -u https://example.com \
  -headless \
  -d 2 \
  -xhr \
  -rl 3 \
  -silent \
  -o urls-headless.txt
~~~

Headless 模式依赖浏览器运行环境，速度比普通模式慢，CPU 和内存占用也更高。只对确认存在前端动态加载的重点站点使用。

### 4.4 robots.txt 和 sitemap.xml

请求常见已知文件：

~~~bash
katana -u https://example.com \
  -kf all \
  -d 2 \
  -silent \
  -o known-files.txt
~~~

已知文件可能包含未链接页面、旧路径或站点地图中的业务 URL，但也可能暴露不应公开的内部路径。结果需要人工筛选。

## 5. 作用域控制

### 只爬取指定域名

爬取主站及其子域名时，可以使用正则限制范围：

~~~bash
katana -u https://example.com \
  -scope '(^|\\.)example\\.com$' \
  -d 3 \
  -silent \
  -o in-scope.txt
~~~

正则中的点号需要转义。使用时将 example.com 替换为实际授权域名。

### 排除退出和注销链接

不希望爬虫继续访问退出、注销或特定路径时，可以排除：

~~~bash
katana -u https://example.com \
  -out-scope '(logout|signout|delete)' \
  -d 3 \
  -silent \
  -o urls.txt
~~~

排除规则是正则表达式，写得过宽可能误删正常 URL。正式任务前先用小范围输入验证规则。

### 关闭作用域限制

~~~bash
katana -u https://example.com -no-scope -d 2 -silent
~~~

关闭作用域后可能跟随到第三方 CDN、外部登录平台或完全无关的域名，只有在明确知道影响范围时才使用。

## 6. 请求头、登录态和代理

### 自定义请求头

~~~bash
katana -u https://example.com \
  -H 'User-Agent: Mozilla/5.0' \
  -H 'Accept: text/html,application/xhtml+xml' \
  -d 2 \
  -silent
~~~

### 带 Cookie 爬取

~~~bash
katana -u https://example.com \
  -H 'Cookie: session=SESSION_VALUE' \
  -d 2 \
  -silent \
  -o authenticated-urls.txt
~~~

Cookie、Authorization Token 和其它登录凭据不要提交到 Git、截图或公开笔记。登录态下发现的 URL 也应按敏感信息处理。

### 通过 Burp 等代理

~~~bash
katana -u https://example.com \
  -proxy http://127.0.0.1:8080 \
  -d 2 \
  -silent
~~~

代理适合调试请求、观察爬取过程或复用已有测试链路。代理不可用时，Katana 可能表现为大量超时。

## 7. 限速和任务控制

### 控制每秒请求数

~~~bash
katana -u https://example.com \
  -d 3 \
  -rl 5 \
  -c 5 \
  -silent
~~~

### 限制任务时长

~~~bash
katana -u https://example.com \
  -d 5 \
  -ct 2m \
  -rl 5 \
  -silent \
  -o timed-crawl.txt
~~~

实用调整原则：

- 普通站点先使用 d 2、rl 5；
- 大量超时或目标响应变慢时，降低 rl 和 c；
- 结果过少时，先确认作用域和入口 URL，再考虑提高深度；
- JavaScript 和 Headless 模式要单独限速；
- 不要用高并发弥补错误的入口、作用域或过滤规则。

## 8. 结果保存与筛选

### 保存 JSON

~~~bash
katana -u https://example.com \
  -d 3 \
  -jc \
  -json \
  -o crawl.json
~~~

JSON 结果通常包含 URL、来源页面、请求方式或资源类型等字段，具体结构以当前版本为准。

### 去重 URL

~~~bash
sort -u urls.txt > urls-unique.txt
~~~

Katana 通常会做基础去重，但合并多个入口、多个模式或多个工具的结果后，建议再次去重。

### 初步筛选带参数的 URL

~~~bash
grep '?' urls-unique.txt > parameter-urls.txt
~~~

带参数的 URL 适合后续人工确认接口、搜索、分页和业务功能。不要因为 URL 带参数就直接判定存在漏洞。

### 筛选常见接口路径

~~~bash
grep -Ei '/(api|graphql|swagger|openapi|v[0-9]+)/' urls-unique.txt > api-urls.txt
~~~

这是关键词筛选，只能作为线索。接口也可能使用完全不同的路径命名。

## 9. 常用工作流

### 9.1 单站点标准流程

第一步，先用 httpx 确认入口：

~~~bash
echo https://example.com | httpx -silent -title -status-code
~~~

第二步，普通模式爬取：

~~~bash
katana -u https://example.com \
  -d 2 \
  -rl 5 \
  -silent \
  -o urls.txt
~~~

第三步，对重点站点补充 JavaScript：

~~~bash
katana -u https://example.com \
  -d 3 \
  -jc \
  -jsl \
  -rl 3 \
  -silent \
  -o urls-js.txt
~~~

第四步，去重后人工查看参数、接口和后台路径：

~~~bash
cat urls.txt urls-js.txt | sort -u > urls-all.txt
~~~

### 9.2 子域名到 URL 爬取

先用 httpx 将子域名转换为可访问的 URL：

~~~bash
httpx -l subs.txt -silent -o alive.txt
~~~

再批量爬取：

~~~bash
katana -list alive.txt \
  -d 2 \
  -rl 5 \
  -silent \
  -o katana.txt
~~~

需要 JavaScript 时：

~~~bash
katana -list alive.txt \
  -d 3 \
  -jc \
  -jsl \
  -rl 3 \
  -silent \
  -o katana-js.txt
~~~

### 9.3 Katana 到 ffuf

Katana 发现重点目录后，再对授权范围内的目录做定向内容发现：

~~~bash
grep -E '/(admin|api|backup|dev|test)(/|$)' urls-all.txt | sort -u > interesting.txt
~~~

确认一个重点目录后，再使用小字典进行定向扫描：

~~~bash
ffuf -w common.txt \
  -u https://example.com/admin/FUZZ \
  -mc 200,204,301,302,401,403 \
  -rate 50
~~~

Katana 的输出不是目录字典，不能直接把每一条 URL 都当作 FUZZ 的基础路径。使用前应人工确认 URL 结构和目标范围。

## 10. 常见问题

### 没有发现 URL

检查以下内容：

- 入口 URL 是否包含 http:// 或 https://；
- 目标是否可以从当前网络访问；
- 深度是否设置得过低；
- 是否误用了过窄的 scope；
- 页面是否需要登录或依赖 JavaScript；
- 是否把结果写到了其它输出文件。

先用最小命令测试：

~~~bash
katana -u https://example.com -d 1 -silent
~~~

### 动态页面爬不到内容

按以下顺序增加能力：

~~~bash
katana -u https://example.com -d 2 -jc -jsl -silent
katana -u https://example.com -d 2 -headless -xhr -silent
~~~

Headless 仍然不能保证能够处理所有登录、验证码、WebSocket 或复杂前端状态。必要时先在浏览器或代理中确认真实请求。

### 结果大量来自外部域名

这是作用域没有限制或限制过宽的表现。使用 scope 限定授权域名，并用 out-scope 排除已知的第三方平台：

~~~bash
katana -u https://example.com \
  -scope '(^|\\.)example\\.com$' \
  -out-scope '(google|facebook|cloudflare)' \
  -d 2 \
  -silent
~~~

### 运行很慢

优先降低深度、并发和速率：

~~~bash
katana -u https://example.com \
  -d 2 \
  -rl 3 \
  -c 3 \
  -timeout 10 \
  -ct 5m \
  -silent
~~~

如果开启了 Headless、jc 或 jsl，先关闭它们确认普通爬取速度，再按需重新开启。

### HTTPS 证书或代理错误

确认目标证书、系统时间和代理配置是否正常。代理模式下先用浏览器或 curl 验证代理能够访问目标，再运行 Katana。不要为了绕过未知错误而随意关闭证书校验。

## 11. 快速记忆

~~~bash
# 基础爬取
katana -u https://example.com -d 2 -silent -o urls.txt

# 批量入口
katana -list alive.txt -d 2 -rl 5 -silent -o crawl.txt

# JavaScript
katana -u https://example.com -d 3 -jc -jsl -silent -o urls-js.txt

# Headless 和 XHR
katana -u https://example.com -headless -xhr -d 2 -silent

# 作用域
katana -u https://example.com -scope '(^|\\.)example\\.com$' -d 3 -silent

# 已知文件
katana -u https://example.com -kf all -silent

# JSON 输出
katana -u https://example.com -d 2 -json -o crawl.json

# 常用联动
httpx -l subs.txt -silent | katana -d 2 -rl 5 -silent -o katana.txt
~~~
