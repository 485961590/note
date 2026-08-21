# ffuf

ffuf（Fuzz Faster U Fool）是基于 Go 编写的高性能 Web 模糊测试工具。它采用多线程与异步 I/O，速度远快于同类工具，常用于目录/文件爆破、虚拟主机枚举、参数与字段模糊测试。

## 基本语法

```bash
ffuf -w <字典文件> -u <URL> [选项]
```

URL 中的 `FUZZ` 是占位符，ffuf 会用字典中的每一行替换它发起请求。

---

## 一、参数速查

### 目标与字典

| 选项 | 说明 |
|------|------|
| `-u <URL>` | 目标 URL，需包含 `FUZZ` 占位符 |
| `-w <FILE>` | 字典文件；多字典用逗号分隔，可用 `:` 重命名占位符（见高级用法） |
| `-e <EXT>` | 自动追加扩展名，如 `-e .php,.bak,.zip` |
| `-ic` | 忽略字典中的注释行 |
| `-mode` | 多字典组合模式：`clusterbomb`（默认，笛卡尔积）/ `pitchfork`（按行对齐） |

### 请求设置

| 选项 | 说明 |
|------|------|
| `-X <METHOD>` | HTTP 方法（GET / POST / PUT...） |
| `-d <DATA>` | POST 请求体 |
| `-H <HEADER>` | 自定义请求头，可多次使用 |
| `-b <COOKIE>` | 设置 Cookie |
| `-x <PROXY>` | 代理（http / https / socks5） |
| `-r` | 跟随重定向 |
| `-request <FILE>` | 从原始请求文件加载模板 |

### 线程与速率

| 选项 | 说明 |
|------|------|
| `-t <N>` | 线程数，默认 40 |
| `-rate <N>` | 每秒最大请求数 |
| `-p <SEC>` | 每线程请求间隔（秒） |
| `-timeout <SEC>` | 请求超时，默认 10 秒 |
| `-maxtime <SEC>` | 最大运行时间 |

### 匹配与过滤

| 选项 | 说明 |
|------|------|
| `-mc <CODES>` | 匹配状态码，默认 `200,204,301,302,307,401,403,405,500` |
| `-fc <CODES>` | 过滤状态码 |
| `-ms / -fs <SIZE>` | 按响应大小匹配 / 过滤（支持区间如 `-fs 1000-2000`） |
| `-mw / -fw <N>` | 按响应单词数匹配 / 过滤 |
| `-ml / -fl <N>` | 按响应行数匹配 / 过滤 |
| `-ac` | 自动校准过滤（自动识别并过滤统一的模板响应） |

### 输出

| 选项          | 说明                                   |
| ----------- | ------------------------------------ |
| `-o <FILE>` | 输出文件                                 |
| `-of <FMT>` | 输出格式（json / csv / html / md，默认 json） |
| `-s`        | 静默模式                                 |
| `-v`        | 详细输出                                 |
| -c          | 输出带色彩                                |

---

## 二、基础用法

```bash
# 1. 目录扫描（字典逐行替换 FUZZ）
ffuf -w wordlist.txt -u http://target.com/FUZZ

# 2. 指定扩展名（找备份/源码文件）
ffuf -w wordlist.txt -u http://target.com/FUZZ -e .php,.html,.bak

# 3. 只关注指定状态码
ffuf -w wordlist.txt -u http://target.com/FUZZ -mc 200,301,403

# 4. 过滤统一 404 页面大小，去误报
ffuf -w wordlist.txt -u http://target.com/FUZZ -fs 4040

# 5. 多线程加速 + 输出 JSON
ffuf -w wordlist.txt -u http://target.com/FUZZ -t 100 -o result.json -of json
```

---

## 三、高级用法

### 1. 多字典组合模式

`-w` 可用 `字典:名字` 的写法给字典命名占位符，URL 与请求中用该名字代替 `FUZZ`。多字典的排列方式由 `-mode` 决定：

- `clusterbomb`（默认）：笛卡尔积，遍历所有组合，适合账号、密码各自独立爆破
- `pitchfork`：多字典按行对齐并行，适合逐行对应的键值对

```bash
# clusterbomb：账号 x 密码 全组合
ffuf -w users.txt:W1,passwords.txt:W2 -u http://target.com/login -X POST \
  -d "username=W1&password=W2" -fc 200

# pitchfork：用户名与密码逐行对应（如收集到的 用户:密码 列表）
ffuf -mode pitchfork -w users.txt:W1,passwords.txt:W2 \
  -u http://target.com/login -X POST -d "username=W1&password=W2" -fc 200
```

### 2. 从 Burp 原始请求模糊

把 Burp 中截获的请求另存为文件，将需要爆破的位置改成 `FUZZ`，用 `-request` 加载，无需手动补全所有请求头：

```bash
# request.txt 内容示例（POST body 中的 FUZZ 即爆破点）：
#   POST /api/login HTTP/1.1
#   Host: target.com
#   User-Agent: Mozilla/5.0 ...
#   Content-Type: application/json
#
#   {"username":"FUZZ","password":"admin"}

ffuf -request request.txt -w usernames.txt -mc all -fc 400
```

注意：`-request` 默认按 https 构造请求，目标是 http 时加 `-request-proto http`。

### 3. 匹配与过滤的组合逻辑

- 单个选项内多个值用逗号分隔，满足任一即命中（OR），如 `-fs 1000-2000` 支持区间
- 多个 filter 之间默认 OR：任一命中即丢弃，可用 `-fmode and` 改为全部命中才丢弃
- 多个 matcher 之间默认 OR：任一命中即显示，可用 `-mmode and` 改为全部命中才显示

```bash
# 正则匹配：命中正则才显示
ffuf -w wordlist.txt -u http://target.com/FUZZ -mr "admin|root"

# -mmode and：状态码为 200 且 大小落在区间内才显示
ffuf -w wordlist.txt -u http://target.com/FUZZ -mc 200 -ms 500-3000 -mmode and

# 多维度过滤：丢掉 404/403 状态，同时丢掉 4096 字节的模板响应
ffuf -w wordlist.txt -u http://target.com/FUZZ -fc 404,403 -fs 4096
```

### 4. 递归扫描

```bash
# 递归进入发现的目录，最深 3 层
ffuf -w wordlist.txt -u http://target.com/FUZZ -recursion -recursion-depth 3

# greedy 策略：对每个命中都继续递归（默认 default 只对目录类命中递归）
ffuf -w wordlist.txt -u http://target.com/FUZZ -recursion -recursion-strategy greedy

# 每层作业单独限时，防止递归失控
ffuf -w wordlist.txt -u http://target.com/FUZZ -recursion -recursion-depth 3 -maxtime-job 120
```

### 5. 联动 Burp

```bash
# 全流量经代理进 Burp，可逐条审查
ffuf -w wordlist.txt -u http://target.com/FUZZ -x http://127.0.0.1:8080

# 只把命中结果回放到 Burp 人工复查（-replay-codes 指定回放哪些状态码）
ffuf -w wordlist.txt -u http://target.com/FUZZ -fs 4096 \
  -replay-proxy http://127.0.0.1:8080 -replay-codes 200,302
```

### 6. 性能与隐身

```bash
# 高并发 + 每秒限速
ffuf -w big.txt -u http://target.com/FUZZ -t 100 -rate 2000

# 随机延迟 0.1~0.3 秒，模拟人工访问节奏
ffuf -w wordlist.txt -u http://target.com/FUZZ -p 0.1-0.3

# 不读取响应体，显著提速（仅按状态码/大小判断时使用）
ffuf -w wordlist.txt -u http://target.com/FUZZ -ignore-body

# 遇错即停：-sa 遇任何错误即停（隐含 -se -sc）；-sc 遇伪 403 即停
ffuf -w wordlist.txt -u http://target.com/FUZZ -sa

# 整体限时 + 缩短单次请求超时
ffuf -w wordlist.txt -u http://target.com/FUZZ -maxtime 600 -timeout 5
```

### 7. 断点续扫与批量输出

```bash
# 中断后可从上次进度续扫（需先 -o 保存 json 状态）
ffuf -w wordlist.txt -u http://target.com/FUZZ -o scan.json -of json
ffuf -w wordlist.txt -u http://target.com/FUZZ -o scan.json -of json -resume

# -od 按 job 生成多个结果文件，配合 -of 指定格式
ffuf -w wordlist.txt -u http://target.com/FUZZ -od ./out -of csv
```

### 8. 其他常用组合

```bash
# 虚拟主机枚举：Host 头带 FUZZ，按默认站点响应大小过滤
ffuf -w vhosts.txt -u http://target.com -H "Host: FUZZ.target.com" -fs 1234

# GET 参数名发现：观察哪些参数会被后端处理/反射
ffuf -w params.txt -u "http://target.com/api/user?FUZZ=1" -fc 404 -ms 123

# Cookie 模糊
ffuf -w payloads.txt -u http://target.com/admin -b "session=FUZZ" -fs 403

# POST 请求体模糊（JSON 任意字段均可替换）
ffuf -w payloads.txt -u http://target.com/api -X POST -d '{"id":"FUZZ"}' -fc 500
```

### 9. 虚拟主机枚举实战（完整流程）

以 HTB 靶机为例：目标 IP `10.129.19.199`，主域 `kobold.htb`，枚举该 IP 上配置的其它虚拟主机。

```bash
# 第一步：确认"无效 vhost"的默认响应基线（发一个必然不存在的名字，看状态码与大小）
ffuf -u http://10.129.19.199 -H "HOST:zzznotexist123.kobold.htb" -mc all -c

# 第二步：正式爆破，过滤默认响应（-fs 154 即基线大小；默认 404 尺寸不同时再加 -fc 404,403）
ffuf -u http://10.129.19.199 -k -H "HOST:FUZZ.kobold.htb" \
  -w subdomains-top1million-110000.txt -mc all -fc 404,403 \
  -fs 154 -o jieguo.csv -of csv

# 替代：让 ffuf 自动校准基线，免手写过滤值（-ac）
ffuf -u http://10.129.19.199 -H "HOST:FUZZ.kobold.htb" -w vhosts.txt -mc all -ac
```

实战要点：

- vhost 模式所有命中 URL 都是同一 IP，控制台看不出差别；看 CSV 的 `Input` 列，或终端核对时加 `-v`
- `-fs 154` 必须先用第一步确认基线，否则整个过滤基准就是错的
- 110k 子域名字典噪音较多（大量 `cdn/static/img` 类服务子域），可先跑前 10k 或专用 vhost 字典，命中后再扩大
- `-c` 只影响终端彩色显示，写文件时可去掉
- `-k` 跳过 TLS 校验，目标为 http 时冗余、跳到 https 时仍有效

> 提示：`-mmode`/`-fmode` 默认都是 `or`；字典可用 `-ic` 跳过 `#` 注释行；`-c` 开启彩色输出便于人工扫视结果。

---

## 实用技巧

- **优先用 `-ac` 自动校准**：目标返回统一模板时（如全部 200 的伪 404），能自动识别并过滤
- **先粗扫再精筛**：先用 `-mc 200,301,302` 粗扫，再用 `-fs` 精确去误报
- **真实环境限速**：加 `-rate` 控制请求频率，避免触发封禁
- **模糊位置灵活**：URL、请求头、Cookie、POST 请求体均可作为 `FUZZ` 模糊位置
