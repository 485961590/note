# whatweb

WhatWeb 是基于 Ruby 编写的 Web 技术指纹识别工具，通过内置 1800+ 插件识别网站使用的 CMS、框架、服务器、JS 库、WAF 等技术及其版本。

> 项目地址: https://github.com/urbanadventurer/WhatWeb

---

## 基本语法

```bash
whatweb [选项] <目标>
```

目标可以是 URL、域名、IP 地址、网段（CIDR/区间）或文件；默认对目标首页发起 HTTP 请求，用全部插件逐个匹配响应内容。

---

## 一、参数速查

### 目标设置

| 选项 | 说明 |
|------|------|
| `<目标>` | URL、域名、IP，支持 CIDR（`192.168.0.0/24`）与 IP 区间 |
| `-i, --input-file=<FILE>` | 从文件批量读取目标，可用 `-i /dev/stdin` 接管道输入 |
| `--url-prefix=<STR>` | 给目标 URL 统一加前缀 |
| `--url-suffix=<STR>` | 给目标 URL 统一加后缀 |
| `--url-pattern=<STR>` | 把目标插入 URL 模板中的 `%insert%` 占位符 |

### 攻击等级（-a, --aggression）

控制扫描激进程度，等级越高请求越多、识别越准，但越容易被目标发现。

| 级别 | 名称 | 行为 |
|------|------|------|
| `1` | Stealthy（默认） | 每个目标仅 1 次请求，跟随重定向，适合被动侦察 |
| `2` | （未实现） | 保留空档 |
| `3` | Aggressive | 某插件命中后追加针对性请求，确认并识别精确版本 |
| `4` | Heavy | 对全部插件匹配的 URL 逐一遍历，请求量大，易触发 WAF/IDS |

### HTTP 选项

| 选项 | 说明 |
|------|------|
| `-U, --user-agent=<AGENT>` | 自定义 User-Agent |
| `-H, --header=<STR>` | 追加自定义请求头，可多次使用 |
| `--follow-redirect=<WHEN>` | 重定向策略：`never` / `http-only` / `meta-only` / `same-site` / `always`（默认） |
| `--max-redirects=<N>` | 最大重定向次数，默认 10 |
| `-u, --user=<user:pass>` | HTTP Basic 认证 |
| `-c, --cookie=<COOKIES>` | 携带 Cookie，如 `-c "name=value; name2=value2"` |
| `--proxy=<HOST:PORT>` | 经 HTTP 代理扫描（如 Burp） |

### 插件控制

| 选项 | 说明 |
|------|------|
| `-l, --list-plugins` | 列出全部可用插件 |
| `-I, --search-plugins=<STR>` | 按名称搜索插件 |
| `-p, --plugins=<LIST>` | 只运行指定插件，逗号分隔，也可填插件文件路径（如 `plugins/wordpress.rb`） |
| `-g, --grep=<STR\|REGEXP>` | 在响应中搜索字符串/正则，仅输出命中的目标 |

### 输出

| 选项 | 说明 |
|------|------|
| `-v, --verbose` | 详细输出，显示每个插件的匹配信息 |
| `-q, --quiet` | 安静模式，抑制终端进度输出 |
| `--no-errors` | 不显示错误信息 |
| `--log-json=<FILE>` | JSON 格式保存结果 |
| `--log-xml=<FILE>` / `--log-csv=<FILE>` / `--log-sql=<FILE>` | 分别以 XML/CSV/SQL 格式保存，可同时多格式输出 |

### 性能与隐身

| 选项 | 说明 |
|------|------|
| `-t, --max-threads=<N>` | 并发线程数，默认 25 |
| `--wait=<SEC>` | 请求间隔秒数，用于限速防封 |
| `--open-timeout=<SEC>` | 建立连接超时 |
| `--read-timeout=<SEC>` | 读取响应超时 |

---

## 二、基础用法

```bash
# 1. 扫描单个目标
whatweb example.com

# 2. 详细输出，显示每个插件的匹配信息
whatweb -v example.com

# 3. 批量扫描多个域名
whatweb example.com example.org

# 4. 从文件批量读取目标
whatweb -i urls.txt

# 5. 扫描整个网段，抑制错误信息
whatweb --no-errors 192.168.0.0/24

# 6. 攻击等级 3：命中后深挖，识别精确版本
whatweb -a 3 example.com
```

输出示例：

```
http://example.com [200 OK] Country[UNITED STATES][US], HTTPServer[nginx/1.18.0], IP[93.184.216.34], Title[Example Domain], jQuery[3.5.1], X-Powered-By[PHP/7.4]
```

---

## 三、高级用法

### 1. 攻击等级与精确版本识别

默认等级 1 每目标只发 1 个请求，只能判断"用了什么技术"；等级 3 在插件命中后，会向该插件关心的路径（如 `wp-login.php`、`/robots.txt`）追加请求，从而读出精确版本。

```bash
# 默认 stealthy 级别，快速摸底
whatweb example.com

# 等级 3，识别 WordPress 精确版本
whatweb -a 3 https://target.com/wordpress/

# 等级 4 heavy 模式：对全部插件 URL 发起请求（请求量大，慎用）
whatweb -a 4 target.com
```

### 2. 插件精细控制

先用 `-I` 找到目标插件名，再用 `-p` 只运行该插件。配合等级 3 时请求更少、结果更聚焦，也减少无关误报。

```bash
# 搜索识别 WordPress 的插件
whatweb -I WordPress

# 只运行指定插件并深挖版本
whatweb -p plugins/wordpress.rb -a 3 target.com

# 只运行多个指定插件
whatweb -p wordpress,joomla,drupal target.com
```

### 3. 批量扫描与结构化输出

批量扫描固定保存 JSON，方便后续用 jq、grep 二次处理与归档。

```bash
# 批量扫描 + JSON 输出
whatweb -i targets.txt -a 3 --log-json=result.json

# 同时输出多种格式
whatweb -i targets.txt --log-json=result.json --log-csv=result.csv

# 用 jq 从 JSON 提取每个目标的指纹
jq -r '.[] | "\(.target) \(.plugins | keys | join(","))"' result.json
```

### 4. 代理与身份伪装

```bash
# 经 Burp 代理扫描，全流量可人工审查
whatweb --proxy http://127.0.0.1:8080 target.com

# 自定义 UA 与 Cookie，模拟已登录状态
whatweb -U "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -c "session=abc123; userid=42" target.com

# HTTP Basic 认证目标
whatweb -u admin:pass target.com/admin/
```

### 5. 与 httpx 联动指纹识别

httpx 批量探测存活并粗筛技术栈，whatweb 对重点目标做深度指纹，两者互补。

```bash
# httpx 先筛存活站点，并按技术栈粗筛
httpx -l subs.txt -title -status-code -tech-detect -rl 10 | grep -iE "wordpress|shiro" > candidates.txt

# 提取候选 URL 列表
awk '{print $1}' candidates.txt > urls.txt

# whatweb 对重点目标深度指纹
whatweb -i urls.txt -a 3 --log-json=fingerprint.json

# 直接从终端输出定位 CMS
whatweb -i urls.txt | grep -iE "wordpress|drupal"
```

---

## 实用技巧

- **等级按场景选**：被动侦察用默认等级 1（每目标 1 请求）；等级 3/4 只用于授权测试，等级 4 请求量大、易触发 WAF 与封禁
- **插件先搜再用**：先用 `-I` 找插件名，再用 `-p` 限定，减少无关请求、降低误报
- **批量必须限速**：加 `--wait` 控制请求间隔、`-t` 控制并发，避免短时间大量请求触发目标防护
- **与 httpx 互补**：httpx 粗扫存活与初步技术栈，whatweb 精指纹，不要重复扫同一层
- **联动 Burp**：`--proxy` 让全流量进 Burp，逐条核对请求与响应，便于确认关键指纹
- **结果结构化**：批量扫描固定 `--log-json`，后续用 jq、grep 二次筛选归档
