# OneForAll 子域名收集实用指南

OneForAll 是一个综合型子域名枚举工具，能够组合多个公开数据源，并按配置执行子域名爆破、DNS 解析、HTTP 探测和端口探测等任务。

它比单纯的被动枚举工具覆盖更广，但也更容易产生请求。开启 `brute`、`dns`、`req`、`port` 等模块后，会分别产生字典查询、DNS 查询、HTTP 请求或 TCP 探测。以下命令只适用于自己控制的域名、靶场或明确授权的测试范围。

项目地址：https://github.com/shmilylty/OneForAll

## 1. 安装

### Linux / Kali

```bash
git clone https://github.com/shmilylty/OneForAll.git
cd OneForAll

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
```

检查是否安装成功：

```bash
python3 oneforall.py --help
python3 oneforall.py --version
```

如果项目没有提供 `--version` 参数，以 `--help` 能正常显示为准。

### Windows

```powershell
git clone https://github.com/shmilylty/OneForAll.git
cd OneForAll

py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
```

如果 PowerShell 禁止激活脚本，也可以直接使用虚拟环境中的 Python：

```powershell
.\.venv\Scripts\python.exe oneforall.py --help
```

运行过程中出现参数不识别时，先以当前版本的帮助输出为准。不同版本的参数和数据源可能有所变化。

## 2. 第一次运行

在 OneForAll 项目目录中执行：

```bash
python3 oneforall.py --target example.com run
```

Windows：

```powershell
python .\oneforall.py --target example.com run
```

`example.com` 替换为明确授权的根域名，不要把 `https://`、路径或端口写进 `--target`。

运行完成后，结果通常保存在项目的 `results/` 目录。具体文件名和字段以当前版本的输出为准：

```bash
ls -lh results/
```

Windows：

```powershell
Get-ChildItem .\results
```

## 3. 常用参数速查

| 参数 | 作用 |
|------|------|
| `--target DOMAIN` | 指定一个根域名 |
| `run` | 执行枚举任务，通常放在命令末尾 |
| `--brute True/False` | 开启或关闭字典爆破 |
| `--recursive True/False` | 开启或关闭递归枚举 |
| `--dns True/False` | 开启或关闭 DNS 解析验证 |
| `--req True/False` | 开启或关闭 HTTP 请求与 Web 信息探测 |
| `--port True/False` | 开启或关闭端口探测 |
| `--fmt FORMAT` | 指定结果格式，常用 `csv`、`json` |
| `--path PATH` | 指定结果保存目录 |
| `--wordlist FILE` | 指定爆破使用的字典文件 |
| `-h`、`--help` | 查看当前版本帮助 |

布尔参数通常使用首字母大写的 `True` 或 `False`。如果当前版本提示参数格式错误，直接运行 `python3 oneforall.py --help` 查看示例。

## 4. 推荐使用方式

### 4.1 低请求量的初步收集

先关闭爆破、DNS、HTTP 和端口模块，只观察公开数据源能收集到什么：

```bash
python3 oneforall.py \
  --target example.com \
  --brute False \
  --dns False \
  --req False \
  --port False \
  --fmt csv \
  --path ./results \
  run
```

这种模式适合先确认工具、依赖和数据源配置是否正常。它仍可能访问第三方数据源 API，不等于完全不产生网络请求。

### 4.2 常规收集

默认模式适合授权测试中的第一轮摸底：

```bash
python3 oneforall.py \
  --target example.com \
  --fmt csv \
  --path ./results \
  run
```

如果只想收集并验证子域名，不需要端口探测，可以关闭 `port`：

```bash
python3 oneforall.py \
  --target example.com \
  --port False \
  --fmt csv \
  --path ./results \
  run
```

### 4.3 针对重点域名扩大范围

对重点域名开启爆破和递归：

```bash
python3 oneforall.py \
  --target example.com \
  --brute True \
  --recursive True \
  --dns True \
  --req True \
  --port False \
  --fmt csv \
  --path ./results \
  run
```

字典爆破会增加 DNS 查询和任务时间。先用默认字典确认流程，再根据目标技术和授权范围选择更大的字典：

```bash
python3 oneforall.py \
  --target example.com \
  --brute True \
  --wordlist ./data/subnames.txt \
  run
```

字典路径以本机项目目录为准。若该路径不存在，先在项目中查找可用字典，不要直接猜路径。

### 4.4 端口探测

端口模块会对发现的子域名产生 TCP 探测，耗时和流量都更高：

```bash
python3 oneforall.py \
  --target example.com \
  --port True \
  --fmt csv \
  --path ./results \
  run
```

如果只是为了发现 Web 资产，通常先关闭 `port`，将解析结果交给专门的端口工具处理更容易控制范围和速率。

## 5. API Key 配置

OneForAll 可以调用多个公开数据源。部分数据源需要 API Key，配置后通常能提高覆盖率和稳定性。

先查看项目目录中的配置文件和注释：

```bash
find . -maxdepth 2 -type f \( -name 'config.py' -o -name '*.yaml' -o -name '*.yml' \)
```

Windows：

```powershell
Get-ChildItem -Recurse -File | Where-Object { $_.Name -in @('config.py','config.yaml','config.yml') }
```

不同版本的配置位置和字段名称可能不同，按项目内的配置模板填写。常见数据源包括 FOFA、Shodan、VirusTotal、SecurityTrails、Censys 等，未配置的来源通常会被跳过或返回提示。

配置时注意：

- API Key 不要提交到 Git、截图、公开笔记或共享压缩包；
- 配置文件只保留当前用户可读权限；
- API 配额耗尽或接口失败时，不要把错误当成“没有子域名”；
- 只配置自己有权使用的数据源，遵守对应平台的条款和速率限制。

## 6. 结果处理

### 查看结果文件

```bash
ls -lh results/
head -n 3 results/example.com.csv
```

Windows：

```powershell
Get-ChildItem .\results
Get-Content .\results\example.com.csv -TotalCount 3
```

文件名可能带有时间戳或格式不同，不要固定假设一定叫 `example.com.csv`。先以 `results/` 目录中的实际文件名为准。

OneForAll 的 CSV 结果通常会包含子域名、来源、解析状态、IP、CNAME、HTTP 状态或端口等字段，但字段名会随版本变化。重点查看以下信息：

| 信息 | 用途 |
|------|------|
| 子域名 | 后续 DNS 和 Web 验证的输入 |
| 来源 | 判断结果来自哪个数据源 |
| 解析状态 | 区分历史记录和当前可用资产 |
| IP / CNAME | 判断托管、CDN 和资产归属 |
| HTTP 状态、标题 | 优先筛选登录页、管理面板和业务系统 |
| 端口 | 进一步确认服务入口 |

### 提取子域名交给 dnsx

如果 CSV 中的字段名为 `subdomain`，Linux 可以使用 Python 的 CSV 解析器提取，避免直接用字符串切割破坏带逗号的字段：

```bash
python3 -c 'import csv,sys; r=csv.DictReader(open(sys.argv[1], newline="", encoding="utf-8-sig")); [print(x["subdomain"].strip()) for x in r if x.get("subdomain")]' results/example.com.csv | sort -u > subs.txt
```

PowerShell：

```powershell
Import-Csv .\results\example.com.csv | ForEach-Object { $_.subdomain } | Where-Object { $_ } | Sort-Object -Unique | Set-Content .\subs.txt
```

如果实际字段不是 `subdomain`，先查看 CSV 第一行表头，再替换命令中的字段名：

```bash
head -n 1 results/example.com.csv
```

进行 DNS 验证：

```bash
dnsx -l subs.txt -silent -o resolved.txt
```

继续探测 Web：

```bash
httpx -l resolved.txt -title -status-code -tech-detect -rl 10 -o alive.txt
```

### JSON 结果

需要后续程序处理时，可以保存 JSON：

```bash
python3 oneforall.py \
  --target example.com \
  --fmt json \
  --path ./results \
  run
```

JSON 的字段结构以当前版本为准。处理前先查看文件开头，确认实际字段名：

```bash
head -n 20 results/example.com.json
```

## 7. 批量目标

OneForAll 的批量参数在不同版本中可能不同。稳妥的方式是用脚本逐个调用单域名任务，并为每个任务保留独立结果。

### Bash

准备 `domains.txt`，每行一个根域名，然后执行：

```bash
while IFS= read -r domain; do
  [ -z "$domain" ] && continue
  python3 oneforall.py \
    --target "$domain" \
    --brute False \
    --port False \
    --fmt csv \
    --path ./results \
    run
done < domains.txt
```

### PowerShell

```powershell
Get-Content .\domains.txt | Where-Object { $_.Trim() } | ForEach-Object { python .\oneforall.py --target $_.Trim() --brute False --port False --fmt csv --path .\results run }
```

批量运行前先用一个域名验证输出路径和文件名规则。大批量任务应分批执行，并关注 CPU、内存、DNS 请求量和第三方 API 配额。

## 8. 与 Subfinder 的配合

Subfinder 适合快速、稳定地做被动枚举；OneForAll 适合在授权范围内叠加更多数据源和主动验证。可以先用 Subfinder 生成基线，再用 OneForAll 补充：

```bash
subfinder -d example.com -silent -o subfinder.txt
python3 oneforall.py \
  --target example.com \
  --brute False \
  --port False \
  --fmt csv \
  --path ./results \
  run
```

合并两者结果时要去重，并通过 DNS 验证后再做 HTTP 或端口探测。两个工具都可能访问第三方数据源，API 速率和结果时间点不同，结果存在差异是正常的。

## 9. 常见问题

### 依赖安装失败

优先确认 Python 版本，并在虚拟环境中重新安装依赖：

```bash
python3 --version
python3 -m pip install -r requirements.txt
```

某些依赖在新版本 Python 上可能不兼容。不要混用系统 Python 和虚拟环境中的 pip，尽量使用 `python3 -m pip`。

### 运行后没有结果

依次检查：

- `--target` 是否只填写了根域名；
- 是否在 OneForAll 项目目录中运行；
- `results/` 或 `--path` 指定的目录是否存在；
- 依赖是否安装完整；
- 数据源 API 是否可访问、是否配置正确；
- 是否把所有模块都关闭了；
- 终端输出中是否有数据源错误或超时信息。

先执行最小命令确认基础功能：

```bash
python3 oneforall.py --target example.com --brute False --port False run
```

### 运行时间很长

关闭高成本模块，先确认收集结果：

```bash
python3 oneforall.py \
  --target example.com \
  --brute False \
  --recursive False \
  --req False \
  --port False \
  run
```

如果需要扩大范围，再逐个打开模块，便于判断到底是哪一步耗时。

### 结果很多但无法访问

这是正常现象。公开数据源会返回历史子域名、已下线资产、第三方托管记录和未配置 DNS 的名称。使用 `dnsx` 筛出当前可解析结果，再用 `httpx` 确认 HTTP/HTTPS 服务，不要直接把全部结果交给高并发扫描器。

### 端口结果不可靠

端口探测受网络路径、防火墙、CDN 和扫描速率影响。对重点资产使用 Nmap 复核：

```bash
nmap -sV -p22,80,443,8080,8443 target.example.com
```

OneForAll 的端口结果适合作为线索，不应替代精确的服务识别。

## 10. 快速记忆

```bash
# 基础运行
python3 oneforall.py --target example.com run

# 低请求量初筛
python3 oneforall.py --target example.com --brute False --dns False --req False --port False run

# 常规结果保存
python3 oneforall.py --target example.com --fmt csv --path ./results run

# 扩大字典和递归枚举
python3 oneforall.py --target example.com --brute True --recursive True run

# 关闭端口探测
python3 oneforall.py --target example.com --port False run

# 结果后处理
dnsx -l subs.txt -silent -o resolved.txt
httpx -l resolved.txt -title -status-code -tech-detect -rl 10 -o alive.txt
```
