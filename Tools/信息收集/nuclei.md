# Nuclei

> 模板化（Template-based）的快速漏洞扫描器，通过加载社区/自定义 YAML 模板，批量检测已知漏洞、错误配置与暴露服务。项目由 ProjectDiscovery 用 Go 编写。
> 项目地址: https://github.com/projectdiscovery/nuclei

---

## 工具定位

Nuclei 的核心思路是"模板即漏洞规则"：官方维护的 nuclei-templates 仓库收录数千条检测模板，覆盖 CVE、常见错误配置、暴露面板、敏感文件等。扫描时按模板逐个对目标发请求并匹配响应特征。

与同类工具的分工：

- **nmap**：网络层探测（端口、服务、操作系统）
- **fscan**：内网一条龙快速摸底（存活 + 端口 + 弱口令 + 漏洞）
- **nuclei**：专注"已知漏洞/配置问题"的模板化批量检测，覆盖面广、可自写模板，外网与内网 Web 资产均适用

典型配合：nmap 定位开放端口与服务 → nuclei 对 Web 服务批量打已知漏洞模板 → 命中后用 Metasploit 等深入利用。

---

## 安装

nuclei 需要 go >= 1.24.2 才能安装成功：

```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

没有 Go 环境的机器可直接从 GitHub Releases 下载预编译二进制。首次运行会自动下载 nuclei-templates 模板库。

---

## 基础用法

### 单目标扫描

```bash
nuclei -u https://example.com
```

`-u` 与 `-target` 等价。

### 多目标扫描

目标文件每行一个 URL/域名：

```bash
nuclei -list urls.txt
```

### 网段扫描

```bash
nuclei -target 192.168.1.0/24
```

### 上传结果到 ProjectDiscovery 云

扫描在本机执行，结果上传云平台查看与分析（需先登录授权）：

```bash
nuclei -auth
nuclei -target https://example.com -dashboard
```

---

## 常用参数

### 模板筛选（高频）

| 参数 | 作用 |
|------|------|
| `-t` | 指定模板文件或模板目录 |
| `-tags` | 按标签运行模板，如 `-tags cve,php` |
| `-etags` | 排除指定标签 |
| `-s / -severity` | 按严重级别运行：info、low、medium、high、critical、unknown |
| `-es` | 排除指定严重级别 |
| `-id` | 按模板 ID 运行，支持通配符 |
| `-tl` | 列出当前匹配的模板 |
| `-tgl` | 列出所有可用标签 |
| `-validate` | 校验模板语法（写自定义模板时用） |

### 输出控制

| 参数 | 作用 |
|------|------|
| `-o` | 结果写入文件 |
| `-silent` | 只显示命中的结果 |
| `-jsonl` | 输出 JSONL 格式，便于程序化处理 |
| `-je / -jle` | 导出为 JSON / JSONL 文件 |
| `-me` | 结果导出为 Markdown 目录 |
| `-nc` | 关闭颜色输出 |
| `-ms` | 同时显示未命中（匹配失败）状态 |

### 速率与并发

| 参数 | 作用 |
|------|------|
| `-rl` | 每秒最大请求数（默认 150） |
| `-c` | 并发执行的模板数（默认 25） |
| `-bs` | 每个模板并行分析的主机数（默认 25） |
| `-timeout` | 单请求超时秒数（默认 10） |
| `-retries` | 失败重试次数（默认 1） |

### 请求控制与调试

| 参数 | 作用 |
|------|------|
| `-H` | 自定义请求头，如 `-H "Cookie: xx"` |
| `-fr` | 跟随重定向 |
| `-p` | 走代理（http/socks5） |
| `-debug` | 显示所有请求与响应 |
| `-v` | 详细输出 |
| `-ni` | 禁用 interactsh（OAST），排除 OAST 类模板 |

### 更新

| 参数 | 作用 |
|------|------|
| `-up` | 更新 nuclei 引擎 |
| `-ut` | 更新 nuclei-templates 模板库 |
| `-nt` | 只运行最新版本新增的模板 |

---

## 自定义模板

模板是 YAML 文件，先 `-validate` 校验语法，再用 `-t` 运行：

```bash
nuclei -u https://example.com -t /path/to/your-template.yaml
```

最小示例（检测 /admin 页面）：

```yaml
id: admin-panel-detect
info:
  name: Admin Panel Detect
  severity: info
http:
  - method: GET
    path:
      - "{{BaseURL}}/admin"
    matchers:
      - type: word
        words:
          - "Admin Login"
```

---

## 实战示例

### 1. 常见模板快速扫描

```bash
nuclei -u https://example.com -tags cve,php -o result.txt
```

### 2. 只跑高危以上漏洞

```bash
nuclei -l urls.txt -severity high,critical
```

### 3. 指定模板目录

```bash
nuclei -u https://example.com -t http/cves/ -t ssl
```

### 4. 结果导出 JSON 便于处理

```bash
nuclei -l urls.txt -jsonl -o result.jsonl
```

### 5. 低速扫描避免触发防护

```bash
nuclei -l urls.txt -rl 10 -c 5 -timeout 15 -retries 2
```

### 6. 走代理调试

```bash
nuclei -u https://example.com -p http://127.0.0.1:8080 -debug
```

---

## 输出解读

```
[INF] [http] Loaded 856 templates for current scan
[WRN] [http:springboot-env] ...
[springboot-actuator] [medium] [Spring Boot Actuator Exposed] https://example.com/actuator
```

| 前缀 | 含义 |
|------|------|
| `[INF]` | 信息性输出（加载模板、扫描进度） |
| `[WRN]` / `[ERR]` | 警告 / 错误 |
| `[模板ID]` | 命中的模板标识 |
| `[严重级别]` | info / low / medium / high / critical |
| 末尾 URL | 命中的目标与路径 |

---

## 注意事项

- **授权前提**：漏洞扫描会向目标发送探测请求，只在自己有权测试的网络（如靶场）使用
- **默认速率较快**：对外网真实目标建议降低 `-rl`、`-c`，避免封 IP 或触发 WAF
- **模板噪音**：用 `-tags` / `-severity` 过滤可减少无关命中，先 `-tl` 预览会跑哪些模板
- **结果落盘**：用 `-o` / `-jsonl` 保存，便于回看与写报告
- **参数以版本为准**：`nuclei -h` 查看本机版本完整参数

---

## 参考

- 官方文档: https://docs.projectdiscovery.io/tools/nuclei
- GitHub: https://github.com/projectdiscovery/nuclei
