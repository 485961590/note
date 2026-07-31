# Nmap

Nmap（Network Mapper）是开源网络探测与安全审计工具，用于主机发现、端口扫描、服务版本检测、操作系统识别与 NSE 脚本利用。

## 基本语法

```bash
nmap [扫描类型] [选项] <目标>
```

目标可以是 IP、域名、网段（CIDR）、IP 范围，或从文件读取（`-iL`）。

---

## 一、参数解释

### 目标指定

| 选项 | 说明 |
|------|------|
| `nmap <IP>` | 单个 IP |
| `nmap <IP1 IP2 IP3>` | 多个 IP，空格分隔 |
| `nmap 192.168.1.0/24` | CIDR 网段 |
| `nmap 192.168.1.1-254` | IP 范围 |
| `nmap -iL targets.txt` | 从文件读取目标列表 |
| `nmap -iR 100` | 随机生成 100 个目标 |
| `--exclude <IP>` | 排除指定目标 |
| `--excludefile <FILE>` | 从文件读取要排除的目标 |

### 主机发现

| 选项 | 说明 |
|------|------|
| `-sn` | Ping 扫描，只判断主机是否在线，不扫端口 |
| `-Pn` | 跳过主机发现，假定所有目标在线 |
| `-PS<ports>` | TCP SYN Ping（默认端口 80） |
| `-PA<ports>` | TCP ACK Ping |
| `-PU<ports>` | UDP Ping |
| `-PE` | ICMP Echo Request |
| `-PR` | ARP Ping（局域网默认，最可靠） |
| `-n` | 不做 DNS 解析 |
| `-R` | 始终做 DNS 解析（包括离线主机） |

### 扫描技术

| 选项 | 说明 | 需要权限 |
|------|------|----------|
| `-sS` | TCP SYN 扫描（半开，默认） | root |
| `-sT` | TCP Connect 扫描（全连接） | 普通用户 |
| `-sA` | TCP ACK 扫描（探测防火墙规则） | root |
| `-sU` | UDP 扫描 | root |
| `-sN` | TCP Null 扫描（不设标志位） | root |
| `-sF` | TCP FIN 扫描 | root |
| `-sX` | TCP Xmas 扫描（FIN/PSH/URG） | root |

### 端口设置

| 选项 | 说明 |
|------|------|
| `-p 80` | 单个端口 |
| `-p 80,443,8080` | 多个端口 |
| `-p 1-1000` | 端口范围 |
| `-p-` | 全部 65535 个端口 |
| `-p U:53,T:80` | UDP 和 TCP 分别指定 |
| `-F` | 快速扫描（100 个常用端口） |
| `--top-ports 100` | 扫描最常见的 100 个端口 |
| `-r` | 按顺序扫描端口（默认随机） |

### 服务与版本检测

| 选项 | 说明 |
|------|------|
| `-sV` | 服务版本探测 |
| `--version-intensity <0-9>` | 探测强度（默认 7） |
| `--version-light` | 轻量探测（强度 2） |
| `--version-all` | 全量探测（强度 9） |
| `--version-trace` | 显示版本探测详细过程 |

### 操作系统检测

| 选项                 | 说明                |
| ------------------ | ----------------- |
| `-O`               | 启用操作系统检测          |
| `--osscan-limit`   | 仅对有开放端口的主机做 OS 检测 |
| `--osscan-guess`   | 积极猜测操作系统          |
| `--max-os-tries N` | OS 检测重试次数         |

### 时序与性能

| 选项 | 说明 |
|------|------|
| `-T0` | 偏执模式（IDS 规避，极慢） |
| `-T1` | 潜行模式（慢） |
| `-T2` | 礼貌模式（较慢） |
| `-T3` | 正常模式（默认） |
| `-T4` | 激进模式（快速，假设网络良好） |
| `-T5` | 疯狂模式（极快，可能丢结果） |
| `--min-rate <N>` | 每秒最少发包数 |
| `--max-rate <N>` | 每秒最多发包数 |
| `--min-parallelism <N>` | 最少并行探测数 |
| `--host-timeout <TIME>` | 单主机超时 |
| `--scan-delay <TIME>` | 每次探测间延迟 |
| `--max-retries <N>` | 端口扫描重试次数 |

### 防火墙 / IDS 规避

| 选项 | 说明 |
|------|------|
| `-f` | 分片 IP 数据包（8 字节） |
| `--mtu <N>` | 指定 MTU 值（8 的倍数） |
| `-D <decoy1,decoy2,...>` | 诱饵扫描，混入虚假 IP |
| `-S <IP>` | 伪造源 IP |
| `-e <iface>` | 指定网络接口 |
| `-g <port>` | 指定源端口（如 53、80 绕过防火墙） |
| `--data-length <N>` | 附加随机数据达到指定长度 |
| `--randomize-hosts` | 随机化扫描顺序 |
| `--spoof-mac <MAC>` | 伪造 MAC 地址 |
| `--badsum` | 伪造错误校验和（探测防火墙响应） |

### 输出

| 选项 | 说明 |
|------|------|
| `-oN <FILE>` | 普通文本输出 |
| `-oX <FILE>` | XML 格式输出 |
| `-oG <FILE>` | Grepable 格式 |
| `-oA <basename>` | 同时输出三种格式 |
| `-v` | 详细输出（可叠加 `-vv`） |
| `--reason` | 显示端口状态判断依据 |
| `--open` | 只显示开放端口 |
| `--resume <FILE>` | 从中断的扫描恢复 |

---

## 二、测试例子

### 1. 主机发现

```bash
# Ping 扫描整个网段（只判断哪些主机在线）
nmap -sn 192.168.230.0/24

# 局域网 ARP 扫描（最可靠，不会被防火墙拦截）
nmap -sn -PR 192.168.230.0/24

# 跳过主机发现，强制扫描（目标禁 Ping 时用）
nmap -Pn 192.168.230.128

# TCP SYN Ping + 指定端口（防火墙只放行特定端口时）
nmap -PS80,443,8080 192.168.230.128

# 不做 DNS 反查，加速扫描
nmap -n -sn 192.168.230.0/24
```

### 2. 端口与版本探测

```bash
# 快速扫描常见 100 端口
nmap -F 192.168.230.128

# 全端口扫描（65535 个端口）
nmap -p- 192.168.230.128

# 指定端口范围
nmap -p 1-1000,3306,8080,9090 192.168.230.128

# TCP Connect 扫描（没有 root 权限时使用）
nmap -sT -p 80,443 192.168.230.128

# SYN 扫描（默认，需要 root，速度快且隐蔽）
nmap -sS -p 1-1000 192.168.230.128

# UDP 端口扫描（DNS/SNMP/DHCP 等）
nmap -sU -p 53,67,68,161,162 192.168.230.128

# 服务版本检测
nmap -sV 192.168.230.128

# 激进版本检测（更准确，但更慢）
nmap -sV --version-intensity 9 192.168.230.128

# 操作系统检测
nmap -O 192.168.230.128

# OS 检测 + 服务检测（经典组合）
nmap -sV -O 192.168.230.128
```

### 3. 综合信息探测

```bash
# 综合扫描
namp -sS -sV -A -O -p- 192.168.230.142

# 综合扫描（OS + 版本 + 脚本 + 路由追踪）
nmap -A 192.168.230.128

# 全量信息收集（安全、不具破坏性）
nmap -sV -sC -O -p- --reason -T4 -oA full_recon 192.168.230.128

# 渗透测试信息收集（单目标全端口深度探测）
nmap -p- -sV -O -sC --reason -T4 -oA recon_full 192.168.230.128
```

> `-A` 等价于 `-sV -O -sC --traceroute`，是最常用的深度扫描选项。

分阶段扫描建议：

| 阶段 | 命令 | 目的 |
|------|------|------|
| 1 | `nmap -sn 网段` | 找出存活主机 |
| 2 | `nmap -p- --min-rate 1000 目标` | 快速全端口发现 |
| 3 | `nmap -sV -sC -p 开放端口 目标` | 对开放端口做深度探测 |
| 4 | `nmap --script=vuln -p 开放端口 目标` | 漏洞检测 |

### 4. 防火墙 / IDS 规避

```bash
# 分片数据包，绕过简单包过滤防火墙
nmap -f 192.168.230.128

# 源端口伪装（使用常见放行端口如 DNS 53）
nmap -g 53 -sS 192.168.230.128

# 诱饵扫描（混入虚假 IP，ME 代表自己）
nmap -D 192.168.230.50,192.168.230.60,ME 192.168.230.128

# 伪造 MAC 地址（绕过内网 MAC 过滤）
nmap --spoof-mac Cisco 192.168.230.128

# 隐蔽扫描组合：低时序 + 分片 + 源端口 + 诱饵
nmap -sS -T2 -f -g 53 -D 192.168.230.10,192.168.230.20,ME \
  --scan-delay 3s -p 22,80,443,3306,8080 -oA stealth_scan 192.168.230.128
```

### 5. 性能调优

```bash
# 快速扫描内网（T4 + 无 DNS + 限端口）
nmap -T4 -n -F 192.168.230.0/24

# 控制发包速率（每秒最少/最多包数）
nmap --min-rate 100 --max-rate 500 192.168.230.128

# 限制单主机扫描超时
nmap --host-timeout 5m 192.168.230.0/24
```

时序模板速查：

| 模板 | 用途 |
|------|------|
| `-T0` | 偏执 / IDS 规避，极慢 |
| `-T2` | 礼貌 / 不占用带宽 |
| `-T3` | 正常（默认） |
| `-T4` | 激进 / 内网扫描 |
| `-T5` | 疯狂 / 可能丢结果 |

### 6. 输出与结果处理

```bash
# 三种格式同时输出
nmap -oA scan_result 192.168.230.128
# 生成 scan_result.nmap / .xml / .gnmap

# 显示端口为什么判断为 open/closed
nmap --reason 192.168.230.128

# 只显示开放端口
nmap --open 192.168.230.0/24

# 从文件恢复中断的扫描
nmap --resume scan_result.nmap
```

Grepable 输出快速处理：

```bash
# 提取所有开放端口的主机和端口号
grep "open" scan_result.gnmap | awk '{print $2, $5}'

# 统计在线主机数
grep "Status: Up" scan_result.gnmap | wc -l

# 提取所有开放 22 端口的 IP
grep "22/open" scan_result.gnmap | awk '{print $2}'
```

---

## 三、脚本测试

NSE（Nmap Scripting Engine）内置数百个脚本，按分类组织，可用于漏洞检测、暴力破解、信息枚举等。

### 脚本使用语法

```bash
# 默认安全脚本扫描（等价于 -sC）
nmap --script=default 192.168.230.128

# 指定单个脚本
nmap --script=http-title 192.168.230.128

# 指定多个脚本（逗号分隔）
nmap --script=http-headers,http-methods,http-enum 192.168.230.128

# 通配符匹配
nmap --script="http-*" 192.168.230.128

# 逻辑组合（AND / OR / NOT）
nmap --script="default or safe" 192.168.230.128
nmap --script="default and not intrusive" 192.168.230.128
nmap --script="(vuln or exploit) and not dos" 192.168.230.128

# 漏洞扫描类脚本
nmap --script=vuln 192.168.230.128
```

### 传递脚本参数

```bash
# 多个参数（逗号分隔）
nmap --script=http-brute --script-args="userdb=users.txt,passdb=pass.txt,threads=5" 192.168.1.1

# 为特定脚本指定参数（脚本名.参数名）
nmap --script="http-enum,http-title" \
  --script-args="http-enum.fingerprintfile=./fingerprints.txt,http-title.url=/" \
  192.168.1.1

# 设置 User-Agent
nmap --script="http-*" --script-args="http.useragent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'" 192.168.1.1

# 从文件加载参数
nmap --script=http-brute --script-args-file=args.txt 192.168.1.1
```

### 脚本管理与帮助

```bash
# 列出所有已安装脚本
ls /usr/share/nmap/scripts/ | sort

# 按前缀列出脚本（如 http-）
ls /usr/share/nmap/scripts/ | grep "^http-"

# 查看脚本帮助
nmap --script-help=http-enum
nmap --script-help="vuln"

# 更新脚本数据库
nmap --script-updatedb

# 按关键词搜索脚本
grep -rl "sql-injection" /usr/share/nmap/scripts/
```

### 脚本分类

| 分类 | 说明 | 风险 |
|------|------|------|
| `default` | `-sC` 默认执行的安全脚本集 | 低 |
| `safe` | 非侵入式，不会造成损害 | 低 |
| `version` | 版本检测增强，`-sV` 自动调用 | 低 |
| `discovery` | 网络/服务/共享信息枚举 | 中 |
| `auth` | 认证凭据测试、用户枚举 | 中 |
| `brute` | 字典/暴力破解 | 高 |
| `intrusive` | 高侵入性，易触发告警 | 高 |
| `vuln` | 已知漏洞检测（CVE） | 高 |
| `exploit` | 主动漏洞利用 | 极高 |
| `dos` | 拒绝服务测试，可能崩溃服务 | 极高 |

> 一个脚本可属于多个分类。**使用 brute、exploit、dos 类脚本前务必获得书面授权。**

### 常用脚本速查

#### HTTP / Web

| 脚本 | 用途 |
|------|------|
| `http-title` | 获取页面标题 |
| `http-headers` | 分析响应头（Server/X-Powered-By 等） |
| `http-methods` | 检查允许的 HTTP 方法（PUT/DELETE 等危险方法） |
| `http-enum` | 目录/文件枚举（约 2000+ 条签名） |
| `http-robots.txt` | 读取 robots.txt 中的敏感路径 |
| `http-favicon` | Favicon 哈希指纹识别 |
| `http-git` | 检测暴露的 .git 仓库 |
| `http-cors` | CORS 跨域配置错误检测 |
| `http-auth` | 获取认证方案和 realm |
| `http-webdav-scan` | WebDAV 方法检测 |
| `http-php-version` | PHP 版本指纹 |
| `http-vhosts` | 虚拟主机枚举 |
| `http-shellshock` | Shellshock RCE 检测 (CVE-2014-6271) |
| `http-sql-injection` | 简单 SQL 注入探测 |
| `http-vuln-cve2017-5638` | Apache Struts2 S2-045 RCE |
| `http-vuln-cve2021-41773` | Apache HTTPD 路径遍历 |
| `http-wordpress-*` | WordPress 用户枚举/插件检测/漏洞 |
| `http-drupal-*` | Drupal 版本/模块枚举 |

#### SMB / Windows

| 脚本 | 用途 |
|------|------|
| `smb-os-discovery` | OS/域名/计算机名信息 |
| `smb-security-mode` | SMB 安全级别（签名等） |
| `smb-protocols` | 支持的 SMB 协议版本 |
| `smb-enum-shares` | 枚举共享 |
| `smb-enum-users` | 枚举用户 |
| `smb-enum-sessions` | 枚举活动会话 |
| `smb-ls` | 共享文件列表 |
| `smb-vuln-ms17-010` | EternalBlue（WannaCry 传播利用） |
| `smb-vuln-ms08-067` | NetAPI 漏洞（Conficker） |
| `nbstat` | NetBIOS 名称和 MAC 地址 |

#### SSL / TLS

| 脚本 | 用途 |
|------|------|
| `ssl-cert` | 提取证书详情（CN/SAN/有效期） |
| `ssl-enum-ciphers` | 枚举加密套件并评分 |
| `ssl-heartbleed` | Heartbleed 漏洞检测 (CVE-2014-0160) |
| `ssl-poodle` | POODLE 漏洞检测 (CVE-2014-3566) |
| `ssl-ccs-injection` | CCS 注入漏洞 (CVE-2014-0224) |
| `sslv2` | 检测是否支持 SSLv2 |

#### SSH

| 脚本 | 用途 |
|------|------|
| `ssh-hostkey` | SSH 主机密钥指纹和类型 |
| `ssh-auth-methods` | 服务器支持的认证方法 |
| `ssh2-enum-algos` | SSHv2 支持的算法 |
| `ssh-brute` | SSH 凭据暴力破解 |
| `sshv1` | 检测是否支持不安全的 SSHv1 |

#### DNS

| 脚本 | 用途 |
|------|------|
| `dns-nsid` | 查询 nameserver ID 和 version.bind |
| `dns-recursion` | 检测是否开放递归查询 |
| `dns-zone-transfer` | DNS 区域传输（AXFR） |
| `dns-srv-enum` | SRV 记录枚举 |
| `dns-brute` | 子域名暴力枚举 |

#### FTP

| 脚本 | 用途 |
|------|------|
| `ftp-anon` | 匿名登录检测 |
| `ftp-syst` | SYST/STAT 获取服务器类型 |
| `ftp-brute` | FTP 凭据暴力破解 |
| `ftp-bounce` | FTP Bounce 攻击检测 |

#### 数据库

| 脚本 | 用途 |
|------|------|
| `mysql-info` | MySQL/MariaDB 协议和版本信息 |
| `mysql-empty-password` | root 空密码检测 |
| `mysql-brute` | MySQL 暴力破解 |
| `mysql-databases` | 数据库列表（需凭据） |
| `postgres-brute` | PostgreSQL 暴力破解 |
| `mongodb-info` | MongoDB 服务器信息 |
| `redis-info` | Redis 服务器信息 |
| `ms-sql-info` | SQL Server 版本信息 |
| `ms-sql-empty-password` | sa 空密码检测 |

#### 邮件

| 脚本 | 用途 |
|------|------|
| `smtp-commands` | 枚举支持的 SMTP 命令（EHLO） |
| `smtp-enum-users` | VRFY/EXPN/RCPT 用户枚举 |
| `smtp-open-relay` | 开放中继检测 |
| `pop3-capabilities` | POP3 服务能力信息 |
| `imap-capabilities` | IMAP 服务能力信息 |

#### SNMP

| 脚本 | 用途 |
|------|------|
| `snmp-info` | SNMP 协议版本和基础信息 |
| `snmp-brute` | 团体字符串暴力破解 |
| `snmp-interfaces` | 网络接口信息 |
| `snmp-netstat` | netstat 风格连接信息 |
| `snmp-processes` | 运行进程列表 |

#### 其他常用

| 脚本 | 用途 |
|------|------|
| `banner` | 通用 Banner 抓取 |
| `rpcinfo` | Portmapper 服务列表 |
| `nfs-showmount` | NFS 导出列表 |
| `ntp-info` | NTP 时间/版本/配置 |
| `ntp-monlist` | NTP monlist 客户端列表 |
| `vnc-info` | VNC 协议版本和安全类型 |
| `rdp-ntlm-info` | RDP NTLM 信息 |
| `ldap-search` | LDAP 目录搜索 |
| `upnp-info` | UPnP 设备信息 |
| `broadcast-dhcp-discover` | DHCP 服务器发现 |
| `whois-ip` | IP WHOIS 查询 |
| `clock-skew` | 时钟偏移分析 |

### 实用脚本组合

```bash
# Web 应用全面安全检查
nmap -p 80,443,8080,8443 \
  --script="http-* and (safe or vuln) and not dos" \
  --script-args="http.useragent='Mozilla/5.0 (compatible; NSE)'" \
  -oA web_audit 192.168.1.1

# SSL/TLS 安全评估
nmap -p 443,8443,993,995,465 --script="ssl-*" -oA ssl_audit 192.168.1.1

# SMB 信息收集 + 漏洞检测
nmap -p 139,445 --script="smb-* and (safe or vuln) and not dos" -oA smb_recon 192.168.1.0/24

# 数据库发现 + 空密码检测
nmap -p 3306,5432,1433,27017,6379 \
  --script="mysql-empty-password,ms-sql-empty-password,mongodb-info,redis-info" \
  192.168.1.0/24

# 漏洞快速扫描（不包含 DoS 和暴力破解）
nmap -sV --script="vuln and not (dos or brute)" -T4 -oA vuln_scan 192.168.1.1
```

---

## 端口状态含义

| 状态 | 含义 |
|------|------|
| `open` | 端口可达，有服务在监听 |
| `closed` | 端口可达，但没有服务监听 |
| `filtered` | 无法判断，可能被防火墙过滤 |
| `unfiltered` | 端口可达，但无法判断 open/closed（ACK 扫描结果） |
| `open\|filtered` | 可能 open 也可能 filtered（UDP/FIN/Null/Xmas 常见） |

## 实用技巧

- **内网扫描优先用 ARP**：`-sn -PR` 不会被防火墙拦截，且速度极快
- **全端口扫描分段做**：先用 `-T4 -p-` 快速发现开放端口，再对开放端口做 `-sV` 深度探测
- **UDP 扫描很慢**：只扫关键端口（53, 67, 68, 123, 161, 500），不要全量
- **绕过禁 Ping**：目标不响应 ICMP 时加 `-Pn`，跳过主机发现直接扫描
- **`--reason` 很实用**：显示端口判断依据（如 `syn-ack`、`reset`），方便排查误判
- **`-A` 是日常首选**：一次性完成服务版本、OS、默认脚本和路由追踪
- **避免 `-T5` 丢结果**：广域网几乎必丢，`-T3` 或 `-T4` 最稳妥
- **大网段存活探测**：`-PE` 在互联网可能被过滤，优先考虑 `-PS80,443`
