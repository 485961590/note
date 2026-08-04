# fscan

> 内网多线程快速扫描工具，一条命令自动完成主机存活、端口扫描、服务识别、弱口令爆破、漏洞探测和 Web 指纹识别。
> 项目地址: https://github.com/shadow1ng/fscan

---

## 工具定位

fscan 由 shadow1ng 用 Go 编写并开源，2020 年前后发布，因扫描速度快、功能全，成为内网渗透信息收集阶段的高频工具。

与同类工具的分工：

- **nmap**：精确、灵活、可编程（NSE），适合对具体目标做深度探测
- **sqlmap**：专精 SQL 注入检测与利用
- **fscan**：粗扫找方向，"一条龙"把资产、弱口令、已知漏洞、Web 指纹一次扫完，适合大规模内网快速摸底

实际使用中 fscan 和 nmap 常配合：fscan 快速圈定目标和服务，nmap 对重点服务做精确版本与脚本验证。

---

## 核心能力

| 能力块 | 内容 |
|--------|------|
| 信息收集 | 主机存活探测、端口扫描、服务识别、Web 路径扫描 |
| 弱口令爆破 | 常见服务内置爆破模块，命中直接输出账号密码 |
| 漏洞探测 | 常见高危漏洞检测（未授权访问、MS17-010 等） |
| Web 扫描 | Web 指纹识别、常见框架/CMS 漏洞、敏感路径探测 |

---

## 执行流程

默认一条命令内部按以下顺序工作，各阶段在输出中分别以标记行开头：

```
start infoscan    存活探测 → 端口扫描 → 服务识别 → 路径扫描
start vulscan     对开放端口做已知漏洞探测
start webscan     对 Web 服务做指纹识别 + 常见漏洞探测
start bruteforce  对支持的服务做弱口令爆破
```

各阶段可通过参数跳过（见参数表），也可用 `-m` 只跑单个模块。

---

## 安装

```bash
# 方式一：GitHub Releases 下载预编译二进制（推荐）
# https://github.com/shadow1ng/fscan/releases 下载 fscan_linux_amd64 等
chmod +x fscan
sudo mv fscan /usr/local/bin/

# 方式二：go 直接安装（需已装 go）
go install github.com/shadow1ng/fscan@latest
```

---

## 目标与端口写法

### 目标 `-h`

| 写法 | 含义 |
|------|------|
| `-h 192.168.230.143` | 单个 IP |
| `-h 192.168.230.1-255` | IP 范围 |
| `-h 192.168.230.0/24` | CIDR 网段 |
| `-h 192.168.230.143,192.168.230.144` | 多目标，逗号分隔 |
| `-h example.com` | 域名（自动解析） |

### 端口 `-p`

| 写法 | 含义 |
|------|------|
| `-p 80,443,3306` | 指定多个端口 |
| `-p 1-65535` | 全端口（较慢） |
| 不写 `-p` | 默认扫描常见端口 |

---

## 参数详解

### 目标与端口

| 参数 | 作用 |
|------|------|
| `-h` | 目标地址（必填），支持 IP/范围/CIDR/多目标/域名 |
| `-p` | 指定端口，默认常见端口 |
| `-t` | 线程数，默认 600 |

### 模块与开关

| 参数 | 作用 |
|------|------|
| `-m` | 指定模块，如 `-m ssh`、`-m smb`、`-m web` |
| `-nobr` | 跳过弱口令爆破 |
| `-nopoc` | 跳过 Web POC 探测 |
| `-u` | 指定 URL，单独扫描 Web 资产 |

### 爆破凭据控制

| 参数 | 作用 |
|------|------|
| `-user` | 指定爆破使用的单个用户名 |
| `-pwd` | 指定爆破使用的单个密码 |
| `-us` | 指定用户名字典文件 |
| `-pw` | 指定密码字典文件 |

### 输出与其他

| 参数 | 作用 |
|------|------|
| `-o` | 结果输出到文件 |
| `-proxy` | 指定代理 |

> 不同版本参数以 `fscan -h` 实际输出为准。常见开关组合：`-nobr -nopoc` 只做端口与服务识别；`-nobr` 跳过爆破防止打扰目标。

---

## 弱口令爆破模块

fscan 内置多类服务的爆破，发现对应开放端口后自动尝试：

| 服务 | 端口 | 说明 |
|------|------|------|
| SSH | 22 | `ssh:user:pass` |
| SMB | 139/445 | 也常用于 Windows 横向 |
| RDP | 3389 | Windows 远程桌面 |
| MySQL | 3306 | 数据库弱口令 |
| MSSQL | 1433 | 数据库弱口令 |
| Oracle | 1521 | 数据库弱口令 |
| PostgreSQL | 5432 | 数据库弱口令 |
| Redis | 6379 | 常配合未授权访问 |
| MongoDB | 27017 | 常配合未授权访问 |
| Elasticsearch | 9200 | 常配合未授权访问 |
| FTP | 21 | 匿名/弱口令 |
| Telnet | 23 | 弱口令 |
| WebLogic | 7001 | 中间件弱口令 |

爆破成功会在输出中直接给出账号密码，例如：

```
[+] 192.168.230.143:22 ssh:msfadmin:msfadmin
[+] 192.168.230.143:3306 mysql:root:root
```

自定义字典示例：

```bash
fscan -h 192.168.230.143 -m ssh -us users.txt -pw pass.txt
```

---

## 漏洞探测

对发现的开放端口自动匹配已知漏洞，常见检测项：

| 漏洞 | 说明 |
|------|------|
| MS17-010 | 永恒之蓝，SMB 远程代码执行 |
| CVE-2020-0796 | SMBGhost，SMBv3 远程代码执行 |
| Redis 未授权 | 6379 无认证可访问 |
| Docker API 未授权 | 2375 暴露 Docker 控制接口 |
| Elasticsearch 未授权 | 9200 无认证访问 |
| Memcached 未授权 | 11211 无认证访问 |
| MongoDB 未授权 | 27017 无认证访问 |
| ZooKeeper 未授权 | 2181 无认证访问 |

命中时输出形式：

```
[+] 192.168.230.143:445 MS17-010  vulnerable
```

---

## Web 功能

### 指纹识别

对发现的 Web 服务识别框架/CMS，常见目标：thinkPHP、Laravel、Spring、Shiro、Struts2、WordPress、Joomla、Drupal、phpMyAdmin 等。识别到后便于针对性找已知漏洞。

### 路径扫描

对 Web 服务自动探测常见敏感路径（备份文件、管理后台、phpmyadmin、源码泄露等），命中会列出：

```
[+] http://192.168.230.143/phpmyadmin/ status:200
```

### 单独扫 Web

用 `-u` 指定 URL，只针对该 Web 资产扫描：

```bash
fscan -u http://192.168.230.143 -nobr
```

---

## 输出格式解读

| 标记 | 含义 |
|------|------|
| `IP:port open` | 端口开放 |
| `[*] alive ports len is: N` | 存活端口总数 |
| `[*] ...` | 信息型结果（服务版本、Web 标题等） |
| `[+] ... vulnerable` | 漏洞命中 |
| `[+] IP:port service:user:pass` | 弱口令爆破成功 |
| `[*] WebTitle: url code:200 len:xxx title:xxx` | Web 标题与响应信息 |

示例（Metasploitable2 全扫）：

```
start infoscan
192.168.230.143:22 open
192.168.230.143:80 open
192.168.230.143:445 open
...
[*] alive ports len is: 20
start vulscan
[*] 192.168.230.143:445 SMB version 4:4.6
[+] 192.168.230.143:445 MS17-010  vulnerable
start webscan
[*] WebTitle: http://192.168.230.143 code:200 len:11025 title:Metasploitable
[+] http://192.168.230.143/phpmyadmin/ status:200
start bruteforce
[+] 192.168.230.143:21 ftp:ftp:ftp
[+] 192.168.230.143:22 ssh:msfadmin:msfadmin
[+] 192.168.230.143:3306 mysql:root:root
```

---

## 实战示例

### 1. 单目标全量摸底

```bash
fscan -h 192.168.230.143 -o metasploitable.txt
```

### 2. 扫一个网段找存活主机与服务

```bash
fscan -h 192.168.230.0/24 -o intranet.txt
```

### 3. 只要端口与服务，跳过爆破和 Web POC

```bash
fscan -h 192.168.230.143 -nobr -nopoc
```

### 4. 指定端口快速扫描

```bash
fscan -h 192.168.230.143 -p 21,22,80,445,3306,8080 -nobr -nopoc
```

### 5. 全端口扫描

```bash
fscan -h 192.168.230.143 -p 1-65535 -nobr -nopoc
```

### 6. 只爆破 SSH

```bash
fscan -h 192.168.230.143 -m ssh -us users.txt -pw pass.txt
```

### 7. 只扫 Web 资产

```bash
fscan -u http://192.168.230.143
```

---

## 与 nmap 配合

典型流程：

```
1. fscan -h 192.168.230.0/24 -nobr          # 粗扫：存活主机 + 开放端口 + 服务
2. nmap -sV -sC -p 22,80,445,3306 目标      # 对重点端口做精确版本/脚本探测
3. 对照 fscan 爆破结果 / 漏洞命中逐个利用
```

fscan 负责"快和广"，nmap 负责"准和深"。

---

## 注意事项

- **授权前提**：爆破和漏洞探测是高强度行为，只在自己有权测试的网络（如靶场）使用
- **默认线程 600**：内网快，但目标多或网络脆弱时可调低 `-t`，例如 `-t 200`
- **默认会爆破**：在大量真实机器上容易触发告警或封 IP，用 `-nobr` 关闭
- **默认会扫 Web 路径**：命中敏感路径较多时注意区分真实资产与干扰
- **结果落盘**：用 `-o` 保存，便于回看与写报告
- **参数以版本为准**：`fscan -h` 查看本机版本完整参数

---

## 参考

- GitHub: https://github.com/shadow1ng/fscan
