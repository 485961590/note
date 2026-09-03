# Subfinder 子域名收集实用指南

Subfinder 是 ProjectDiscovery 维护的被动子域名枚举工具。它从证书透明度日志、搜索引擎、互联网资产数据库等公开数据源收集子域名，不主动对目标主机做端口扫描或目录扫描。

它适合信息收集的第一步，但结果不等于“全部子域名”：数据源覆盖范围、API 配置、证书记录和历史数据都会影响结果。收集完成后，通常还要用 `dnsx` 验证解析，再用 `httpx` 探测 Web 服务。

以下命令只适用于自己控制的域名、靶场或明确授权的测试范围。公开数据也可能包含内部资产名称，输出文件应按敏感信息管理。

项目地址：https://github.com/projectdiscovery/subfinder

## 1. 安装与检查

Kali / Debian：

```bash
sudo apt update
sudo apt install subfinder
```

使用 Go 安装最新版：

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

确认命令可用：

```bash
subfinder -version
subfinder -h
```

如果提示找不到命令，检查 Go 的 bin 目录是否已加入 `PATH`：

```bash
go env GOPATH
```

Windows 可直接从项目 Releases 下载对应架构的二进制文件，并将其所在目录加入 `PATH`。不同版本的参数可能略有差异，以本机 `subfinder -h` 为准。

## 2. 基本用法

### 单个域名

```bash
subfinder -d example.com
```

只输出子域名，适合接入管道：

```bash
subfinder -d example.com -silent
```

保存到文件：

```bash
subfinder -d example.com -silent -o subs.txt
```

输出通常是一行一个域名，例如：

```text
api.example.com
dev.example.com
www.example.com
```

### 批量收集

准备 `domains.txt`，一行一个根域名：

```text
example.com
example.org
example.net
```

执行批量枚举：

```bash
subfinder -dL domains.txt -silent -o all-subs.txt
```

输入文件只放根域名或明确授权的域名，先清理 URL、路径、协议头和空行，避免产生无效结果。

## 3. 常用参数速查

### 输入、输出与数据源

| 参数 | 作用 |
|------|------|
| `-d DOMAIN` | 指定一个根域名 |
| `-dL FILE` | 从文件读取多个根域名 |
| `-s SOURCE1,SOURCE2` | 只使用指定数据源 |
| `-es SOURCE1,SOURCE2` | 排除指定数据源 |
| `-all` | 启用所有可用数据源，可能需要更多 API Key |
| `-ls` | 列出当前版本支持的数据源 |
| `-o FILE` | 保存普通文本结果 |
| `-oJ FILE` | 保存 JSON 结果 |
| `-oD DIRECTORY` | 为批量目标分别保存结果 |
| `-silent` | 只输出发现的子域名 |
| `-cs` | 在结果中显示子域名对应的数据源 |

### 扫描控制

| 参数 | 作用 |
|------|------|
| `-t N` | 并发线程数 |
| `-timeout N` | 单个数据源请求超时时间，单位为秒 |
| `-max-time N` | 单个域名枚举的最长时间，单位为分钟 |
| `-rl N` | 每秒请求速率限制 |
| `-rlm N` | 每分钟请求速率限制 |
| `-recursive` | 使用支持递归枚举的数据源收集更深层子域名 |
| `-nW` | 过滤通配符解析产生的结果 |

### 配置文件

| 参数 | 作用 |
|------|------|
| `-config FILE` | 指定主配置文件 |
| `-pc FILE` | 指定 Provider API Key 配置文件 |
| `-r IP1,IP2` | 指定 DNS 解析服务器，主要用于需要解析验证的场景 |

参数名称会随版本变化；遇到 `flag provided but not defined` 时，先运行 `subfinder -h` 核对当前版本。

## 4. 数据源与 API Key

先查看当前版本支持哪些数据源：

```bash
subfinder -ls
```

不配置 API Key 也可以使用部分公开数据源，但覆盖率和稳定性有限。配置多个数据源通常比盲目提高线程数更有效。

推荐先指定少量数据源跑通流程：

```bash
subfinder -d example.com \
  -s crtsh,github,waybackarchive \
  -silent \
  -o subs.txt
```

使用全部可用数据源：

```bash
subfinder -d example.com -all -silent -o subs-all.txt
```

`-all` 会启用当前版本支持的全部数据源，但未配置 API Key 的源可能被跳过或返回错误提示。实际可用的数据源名称以 `subfinder -ls` 输出为准。

### Provider 配置文件

默认 Provider 配置文件通常位于：

```text
~/.config/subfinder/provider-config.yaml
```

可以用 `-pc` 显式指定路径：

```bash
subfinder -d example.com \
  -pc ./provider-config.yaml \
  -silent
```

配置文件的结构由 Subfinder 和各数据源决定，先查看安装包提供的示例或当前版本说明，再填入对应 API Key。示例结构如下，具体字段以数据源要求为准：

```yaml
github:
  - ghp_xxxxxxxxxxxxxxxxxxxx
virustotal:
  - your-virustotal-api-key
securitytrails:
  - your-securitytrails-api-key
shodan:
  - your-shodan-api-key
```

注意：

- API Key 不要直接写进公开脚本、截图、Git 仓库或命令历史；
- 配置文件权限应限制为当前用户可读；
- API 配额耗尽、数据源临时不可用时，不要把错误当成“没有子域名”；
- 运行 `-all` 前先确认目标范围和各数据源的使用条款。

## 5. 实用收集流程

### 第一步：小范围跑通

先用默认数据源快速收集并保存结果：

```bash
subfinder -d example.com -silent -o subs.txt
```

查看数量和内容：

```bash
wc -l subs.txt
head subs.txt
```

Windows PowerShell：

```powershell
(Get-Content .\subs.txt).Count
Get-Content .\subs.txt | Select-Object -First 10
```

### 第二步：启用更多数据源

配置 API Key 后扩大收集范围：

```bash
subfinder -d example.com -all -silent -o subs-all.txt
```

如果只想确认哪些源贡献了结果，可以保留来源信息：

```bash
subfinder -d example.com -all -cs -o subs-with-source.txt
```

需要机器处理时使用 JSON：

```bash
subfinder -d example.com -all -oJ subs.json
```

### 第三步：递归收集

对存在多级子域名的授权目标，可以尝试递归枚举：

```bash
subfinder -d example.com -recursive -silent -o subs-recursive.txt
```

递归会增加查询时间和数据源请求量，先对单个域名使用，再决定是否用于批量目标。

### 第四步：去重和规范化

Subfinder 通常会自动去重，但合并多个工具的结果后建议再次去重：

```bash
cat subs.txt subs-all.txt subs-recursive.txt | sort -u > subs-merged.txt
```

不要直接对未经清理的结果做后续扫描。先确认结果中没有 URL、协议、路径或明显不属于目标根域的域名：

```bash
grep -E '(^|\.)example\.com$' subs-merged.txt > subs-example.txt
```

上面的正则只适用于 `example.com`，使用时替换为实际授权域名，并注意正则中的点号需要转义。

## 6. 与 dnsx、httpx 联动

### Subfinder -> dnsx

Subfinder 输出的是“被数据源发现的名称”，不代表当前仍然有 DNS 记录。用 `dnsx` 筛出当前可解析的子域名：

```bash
subfinder -d example.com -silent \
  | dnsx -silent \
  | sort -u \
  > resolved.txt
```

保留解析到的 IP：

```bash
subfinder -d example.com -silent \
  | dnsx -silent -a -resp-only \
  | sort -u \
  > ips.txt
```

同时观察 CNAME，便于识别 CDN、云服务或第三方托管：

```bash
dnsx -l subs.txt -cname -silent -o cname.txt
```

### Subfinder -> dnsx -> httpx

这是常用的三步流程：

```bash
subfinder -d example.com -silent \
  | dnsx -silent \
  | httpx -title -status-code -tech-detect -rl 10 \
  -o alive.txt
```

如果需要重复查看中间结果，分步执行更容易排错：

```bash
subfinder -d example.com -silent -o subs.txt
dnsx -l subs.txt -silent -o resolved.txt
httpx -l resolved.txt -title -status-code -tech-detect -rl 10 -o alive.txt
```

只有完成 DNS 验证和 Web 探测后，才适合把结果交给目录扫描、端口扫描或漏洞验证工具。Subfinder 本身不执行这些动作。

## 7. 批量目标的推荐写法

### 批量收集并统一输出

```bash
subfinder -dL domains.txt -all -silent -o all-subs.txt
sort -u all-subs.txt > all-subs-unique.txt
```

### 批量收集并按目标分别保存

```bash
subfinder -dL domains.txt -all -oD subfinder-output
```

`-oD` 适合目标较多的情况，可以避免所有结果混在一个文件中。执行前确认输出目录不会覆盖已有的重要文件。

### 控制大批量任务的请求速率

```bash
subfinder -dL domains.txt \
  -all \
  -t 10 \
  -rl 5 \
  -timeout 30 \
  -max-time 10 \
  -silent \
  -o all-subs.txt
```

不同数据源对速率、并发和 API 配额的限制不同。大批量任务优先降低速率、分批执行，并检查错误输出。

## 8. 常见问题

### 结果很少

常见原因：

- 根域名写错，或把 `https://`、路径一起写进 `-d`；
- 未配置需要认证的数据源；
- 目标域名本身公开记录较少；
- 数据源 API 配额耗尽或暂时不可用；
- 只使用了少量数据源，覆盖率有限。

可以按顺序处理：

```bash
subfinder -ls
subfinder -d example.com -silent -o subs-default.txt
subfinder -d example.com -all -silent -o subs-all.txt
```

不要因为结果少就直接判断“目标没有子域名”。被动枚举只能说明当前数据源没有返回更多记录。

### 结果中出现大量无效或通配符子域名

尝试过滤通配符结果：

```bash
subfinder -d example.com -nW -silent -o subs.txt
```

随后使用 `dnsx` 再做一次解析验证。若仍有大量结果，检查目标是否配置了泛解析，并根据实际 DNS 结果人工复核。

### 想知道子域名来自哪里

启用来源信息：

```bash
subfinder -d example.com -cs -o subs-with-source.txt
```

如果需要程序化处理，使用 JSON 输出：

```bash
subfinder -d example.com -oJ subs.json
```

来源信息适合判断数据可信度和重复来源，但不能代替 DNS 或 HTTP 验证。

### 某个数据源报错

先列出当前版本支持的数据源并单独测试：

```bash
subfinder -ls
subfinder -d example.com -s crtsh -silent
```

如果只想暂时跳过问题数据源：

```bash
subfinder -d example.com -es source1,source2 -silent
```

检查 API Key、配置文件路径、网络连接和 API 配额。不要为了消除提示而盲目使用 `-all`。

### 参数不识别

不同版本的参数可能有差异，先查看帮助：

```bash
subfinder -h
subfinder -version
```

尤其是 JSON 输出、数据源列表和速率限制参数，使用前应以本机版本为准。

## 9. 快速记忆

```bash
# 单域名收集
subfinder -d example.com -silent -o subs.txt

# 批量收集
subfinder -dL domains.txt -silent -o all-subs.txt

# 启用全部数据源
subfinder -d example.com -all -silent -o subs-all.txt

# 显示数据源
subfinder -d example.com -all -cs -o subs-with-source.txt

# 过滤通配符结果
subfinder -d example.com -nW -silent -o subs.txt

# 常用三步流程
subfinder -d example.com -silent | dnsx -silent | httpx -title -status-code -rl 10
```
