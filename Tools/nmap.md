# Nmap

Nmap（Network Mapper）是一款开源的网络探测和安全审计工具，用于主机发现、端口扫描、服务版本检测和操作系统识别。

## 基本语法

```bash
nmap [扫描类型] [选项] <目标>
```

目标可以是 IP、域名、网段（CIDR）、IP 范围，或从文件读取（`-iL`）。

## 快速开始

```bash
# 基本 TCP SYN 扫描（默认，需要 root 权限）
nmap 192.168.1.1

# 扫描多个目标
nmap 192.168.1.1 192.168.1.2 192.168.1.3

# 扫描网段
nmap 192.168.1.0/24

# 扫描指定端口
nmap -p 80,443,8080 192.168.1.1

# 详细输出
nmap -v 192.168.1.1
```

## 选项速查

### 目标指定

| 选项 | 说明 |
|------|------|
| `nmap <IP>` | 单个 IP |
| `nmap <IP1 IP2 IP3>` | 多个 IP，空格分隔 |
| `nmap 192.168.1.0/24` | CIDR 网段 |
| `nmap 192.168.1.1-254` | IP 范围 |
| `nmap 192.168.1-10.1-254` | 多段范围组合 |
| `nmap -iL targets.txt` | 从文件读取目标列表 |
| `nmap -iR 100` | 随机生成 100 个目标 |
| `--exclude <IP>` | 排除指定目标 |
| `--excludefile <FILE>` | 从文件读取要排除的目标 |

### 主机发现（Host Discovery）

| 选项 | 说明 |
|------|------|
| `-sn` | Ping 扫描 — 不扫端口，只判断主机是否在线 |
| `-Pn` | 跳过主机发现，假定所有目标在线 |
| `-PS<ports>` | TCP SYN Ping（默认端口 80） |
| `-PA<ports>` | TCP ACK Ping |
| `-PU<ports>` | UDP Ping |
| `-PE` | ICMP Echo Request（最常用） |
| `-PP` | ICMP Timestamp Request |
| `-PM` | ICMP Netmask Request |
| `-PO<protocols>` | IP Protocol Ping |
| `-PR` | ARP Ping（局域网内默认，最可靠） |
| `-n` | 不做 DNS 解析 |
| `-R` | 始终做 DNS 解析（包括离线主机） |
| `--dns-servers <DNS>` | 指定 DNS 服务器 |

### 扫描技术

| 选项 | 说明 | 需要权限 |
|------|------|----------|
| `-sS` | TCP SYN 扫描（半开，默认） | root |
| `-sT` | TCP Connect 扫描（全连接） | 普通用户 |
| `-sA` | TCP ACK 扫描（探测防火墙规则） | root |
| `-sW` | TCP Window 扫描（基于窗口值判断） | root |
| `-sM` | TCP Maimon 扫描（FIN/ACK） | root |
| `-sU` | UDP 扫描 | root |
| `-sN` | TCP Null 扫描（不设任何标志位） | root |
| `-sF` | TCP FIN 扫描 | root |
| `-sX` | TCP Xmas 扫描（FIN/PSH/URG） | root |
| `-sO` | IP 协议扫描 | root |

### 端口设置

| 选项 | 说明 |
|------|------|
| `-p 80` | 单个端口 |
| `-p 80,443,8080` | 多个端口 |
| `-p 1-1000` | 端口范围 |
| `-p-` | 全部 65535 个端口 |
| `-p U:53,67 T:80,443` | UDP 和 TCP 分别指定 |
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
| `--version-trace` | 显示版本探测的详细过程 |

### 操作系统检测

| 选项 | 说明 |
|------|------|
| `-O` | 启用操作系统检测 |
| `--osscan-limit` | 仅对有开放端口的主机做 OS 检测 |
| `--osscan-guess` | 积极猜测操作系统（更激进） |
| `--max-os-tries N` | 设置 OS 检测重试次数 |

### 时序与性能

| 选项 | 说明 |
|------|------|
| `-T0` | 偏执模式（IDS 规避，极慢） |
| `-T1` | 潜行模式（慢） |
| `-T2` | 礼貌模式（较慢，占用带宽少） |
| `-T3` | 正常模式（默认） |
| `-T4` | 激进模式（快速，假设网络良好） |
| `-T5` | 疯狂模式（极快，可能丢失结果） |
| `--min-rate <N>` | 每秒最少发包数 |
| `--max-rate <N>` | 每秒最多发包数 |
| `--min-parallelism <N>` | 最少并行探测数 |
| `--max-parallelism <N>` | 最多并行探测数 |
| `--host-timeout <TIME>` | 单主机超时 |
| `--scan-delay <TIME>` | 每次探测间延迟 |
| `--max-retries <N>` | 端口扫描重试次数 |

### 防火墙/IDS 规避

| 选项 | 说明 |
|------|------|
| `-f` | 分片 IP 数据包（8 字节） |
| `-ff` | 进一步分片（16 字节） |
| `--mtu <N>` | 指定 MTU 值（8 的倍数） |
| `-D <decoy1,decoy2,...>` | 诱饵扫描，混合虚假 IP |
| `-S <IP>` | 伪造源 IP |
| `-e <iface>` | 指定网络接口 |
| `-g <port>` | 指定源端口（如 53、80 绕过防火墙） |
| `--source-port <port>` | 同上 |
| `--data <hex>` | 在包尾附加自定义数据 |
| `--data-string <str>` | 在包尾附加自定义字符串 |
| `--data-length <N>` | 附加随机数据达到指定长度 |
| `--randomize-hosts` | 随机化扫描顺序 |
| `--spoof-mac <MAC>` | 伪造 MAC 地址 |
| `--badsum` | 伪造错误的校验和（探测防火墙响应） |
| `--proxies <url>` | 通过 HTTP/SOCKS4 代理代理连接 |

### 输出

| 选项 | 说明 |
|------|------|
| `-oN <FILE>` | 普通文本输出 |
| `-oX <FILE>` | XML 格式输出 |
| `-oG <FILE>` | Grepable 格式（适合 grep/awk 处理） |
| `-oA <basename>` | 同时输出三种格式 |
| `-v` | 详细输出（可叠加 `-vv`） |
| `-d` | 调试输出（1-9 级） |
| `--reason` | 显示端口状态判断依据 |
| `--open` | 只显示开放端口 |
| `--packet-trace` | 显示收发包详情 |
| `--resume <FILE>` | 从上次中断的扫描恢复 |

---

## 常用示例

### 一、主机发现

```bash
# 1. Ping 扫描整个网段（只判断哪些主机在线）
nmap -sn 192.168.230.0/24

# 2. 局域网 ARP 扫描（最可靠，不会被防火墙拦截）
nmap -sn -PR 192.168.230.0/24

# 3. 跳过主机发现，强制扫描（目标禁 Ping 时用）
nmap -Pn 192.168.230.128

# 4. TCP SYN Ping + 指定端口（防火墙可能只放行特定端口）
nmap -PS80,443,8080 192.168.230.128

# 5. 不做 DNS 反查，加速扫描
nmap -n -sn 192.168.230.0/24
```

### 二、端口扫描

```bash
# 6. 快速扫描常见 100 端口
nmap -F 192.168.230.128

# 7. 全端口扫描（65535 个端口）
nmap -p- 192.168.230.128

# 8. 指定端口范围
nmap -p 1-1000,3306,8080,9090 192.168.230.128

# 9. TCP Connect 扫描（没有 root 权限时使用）
nmap -sT -p 80,443 192.168.230.128

# 10. SYN 扫描（默认，需要 root，速度快且隐蔽）
nmap -sS -p 1-1000 192.168.230.128

# 11. UDP 端口扫描（DNS/SNMP/DHCP 等）
nmap -sU -p 53,67,68,161,162 192.168.230.128

# 12. UDP + TCP 同时扫描
nmap -sU -sS -p U:53,67,161 T:22,80,443 192.168.230.128
```

### 三、服务版本与 OS 探测

```bash
# 13. 服务版本检测
nmap -sV 192.168.230.128

# 14. 激进版本检测（更准确，但更慢）
nmap -sV --version-intensity 9 192.168.230.128

# 15. 操作系统检测
nmap -O 192.168.230.128

# 16. OS 检测 + 服务检测（经典组合）
nmap -sV -O 192.168.230.128

# 17. 综合扫描（OS + 版本 + 脚本 + 路由追踪）
nmap -A 192.168.230.128
```

> `-A` 等价于 `-sV -O -sC --traceroute`，是最常用的深度扫描选项。

### 四、NSE 脚本引擎

```bash
# 18. 默认安全脚本扫描
nmap -sC 192.168.230.128

# 19. 指定脚本分类（safe 类脚本）
nmap --script=safe 192.168.230.128

# 20. 指定单个脚本
nmap --script=http-title 192.168.230.128

# 21. 指定多个脚本（逗号分隔）
nmap --script=http-headers,http-methods,http-enum 192.168.230.128

# 22. 通配符匹配
nmap --script="http-*" 192.168.230.128

# 23. 传递脚本参数
nmap --script=http-brute --script-args="userdb=/path/users.txt,passdb=/path/pass.txt" 192.168.230.128

# 24. 查看脚本帮助
nmap --script-help=http-vuln-cve2017-5638

# 25. 漏洞扫描类脚本
nmap --script=vuln 192.168.230.128
```

#### 脚本选择语法

```bash
# 按分类加载
nmap --script=safe 192.168.1.1
nmap --script=vuln 192.168.1.1

# 按文件名 / 通配符
nmap --script=http-enum 192.168.1.1
nmap --script="http-*" 192.168.1.1
nmap --script="http-*,mysql-*" -p 80,3306 192.168.1.1

# 逻辑组合（AND / OR / NOT）
nmap --script="default or safe" 192.168.1.1
nmap --script="default and not intrusive" 192.168.1.1
nmap --script="http-* and not (http-brute or http-slowloris)" 192.168.1.1
nmap --script="(vuln or exploit) and not dos" 192.168.1.1

# 排除特定分类
nmap --script="not intrusive" 192.168.1.1
nmap --script="default and not broadcast" 192.168.1.1
```

#### 传递脚本参数

```bash
# 单个参数
nmap --script=http-title --script-args=http.title="Custom Title" 192.168.1.1

# 多个参数（逗号分隔）
nmap --script=http-brute --script-args="userdb=users.txt,passdb=pass.txt,threads=5" 192.168.1.1

# 为特定脚本指定参数（脚本名.参数名）
nmap --script="http-enum,http-title" \
  --script-args="http-enum.fingerprintfile=./fingerprints.txt,http-title.url=/" \
  192.168.1.1

# 从文件加载参数
nmap --script=http-brute --script-args-file=args.txt 192.168.1.1

# 设置 User-Agent
nmap --script="http-*" --script-args="http.useragent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'" 192.168.1.1
```

#### 脚本管理与帮助

```bash
# 列出所有已安装的脚本
ls /usr/share/nmap/scripts/ | sort

# 统计脚本总数
ls /usr/share/nmap/scripts/ | wc -l

# 按分类列出脚本
ls /usr/share/nmap/scripts/ | grep "^http-"

# 查看脚本帮助
nmap --script-help=http-enum
nmap --script-help=http-vuln-cve2017-5638

# 查看某分类所有脚本的帮助
nmap --script-help="vuln"

# 更新脚本数据库
nmap --script-updatedb

# 按关键词搜索脚本
grep -rl "sql-injection" /usr/share/nmap/scripts/
grep -rl "cve" /usr/share/nmap/scripts/
```

---

#### 14 个 NSE 脚本分类

| 分类 | 说明 | 风险 | 典型脚本 |
|------|------|------|----------|
| `auth` | 认证凭据测试、用户枚举 | 中 | `ftp-anon`, `http-auth`, `ssh-auth-methods`, `mysql-empty-password` |
| `broadcast` | 局域网广播/组播发现，无需指定目标 | 低 | `broadcast-dhcp-discover`, `broadcast-upnp-info`, `broadcast-ping` |
| `brute` | 字典/暴力破解攻击 | 高 | `http-brute`, `ftp-brute`, `ssh-brute`, `mysql-brute`, `smb-brute` |
| `default` | `-sC` 默认执行的安全脚本集（约 50+ 个） | 低 | `banner`, `http-title`, `ssh-hostkey`, `ssl-cert`, `smb-os-discovery` |
| `discovery` | 网络/服务/主机/共享信息枚举 | 中 | `http-enum`, `smb-enum-shares`, `dns-zone-transfer`, `smb-enum-users` |
| `dos` | 拒绝服务漏洞测试，可能崩溃服务 | 极高 | `http-slowloris`, `smb-flood`, `broadcast-avahi-dos` |
| `exploit` | 主动漏洞利用，获取权限/执行代码 | 极高 | `http-shellshock`, `smb-vuln-ms17-010`, `smb-psexec` |
| `external` | 依赖第三方外部服务（WHOIS, VirusTotal 等） | 低 | `whois-domain`, `whois-ip`, `shodan-api`, `http-virustotal` |
| `fuzzer` | 发送畸形/随机数据测试健壮性 | 高 | `http-form-fuzzer`, `http-sql-injection`, `dns-fuzz` |
| `intrusive` | 高侵入性脚本，易触发 IDS/IPS 告警 | 高 | 多数 brute/exploit/dos 脚本同时属于此分类 |
| `malware` | 恶意软件/后门/僵尸网络检测 | 中 | `http-google-malware`, `p2p-conficker`, `ssl-known-key` |
| `safe` | 非侵入式，不会造成损害（数量最多） | 低 | `http-headers`, `http-title`, `ssl-cert`, `banner` |
| `version` | 服务/OS 版本检测增强，`-sV` 自动调用 | 低 | `banner`, `dns-nsid`, `ike-version`, `vnc-info` |
| `vuln` | 已知漏洞检测（CVE/CVSS） | 高 | `http-vuln-cve*`, `ssl-heartbleed`, `smb-vuln-ms17-010`, `ssl-poodle` |

> 一个脚本可以属于多个分类。例如 `http-shellshock` 同时属于 `exploit` 和 `vuln`。
>
> **使用 brute、exploit、dos 类脚本前务必获得书面授权**，否则可能违反法律或造成服务中断。

---

#### 按协议/服务分类的脚本速查

##### HTTP / Web 应用

| 脚本 | 分类 | 用途 |
|------|------|------|
| `http-title` | default, safe | 获取页面标题 |
| `http-headers` | discovery, safe | 分析响应头（Server/X-Powered-By 等） |
| `http-methods` | default, safe | 检查允许的 HTTP 方法（PUT/DELETE 等危险方法） |
| `http-enum` | discovery, intrusive | 目录/文件枚举（约 2000+ 条签名） |
| `http-robots.txt` | default, safe | 读取 robots.txt 中的敏感路径 |
| `http-favicon` | default, safe | Favicon 哈希指纹识别 |
| `http-generator` | default, safe | 提取 meta generator 标签 |
| `http-git` | default, safe | 检测暴露的 .git 仓库 |
| `http-cors` | default, safe | CORS 跨域配置错误检测 |
| `http-auth` | default, safe | 获取认证方案和 realm |
| `http-webdav-scan` | default, safe | WebDAV 方法检测 |
| `http-php-version` | discovery, safe | PHP 版本指纹 |
| `http-vhosts` | discovery, safe | 虚拟主机枚举 |
| `http-userdir-enum` | discovery, intrusive | 用户目录枚举（~user/） |
| `http-iis-short-name-brute` | discovery, brute | IIS 8.3 短文件名枚举 |
| `http-shellshock` | exploit, vuln | Shellshock RCE 检测 (CVE-2014-6271) |
| `http-sql-injection` | fuzzer, intrusive | 简单 SQL 注入探测 |
| `http-stored-xss` | fuzzer, intrusive | 存储型 XSS 探测 |
| `http-csrf` | vuln, intrusive | CSRF 漏洞检测 |
| `http-form-brute` | brute, intrusive | HTTP 表单暴力破解 |
| `http-form-fuzzer` | fuzzer, intrusive | 表单参数模糊测试 |
| `http-slowloris` | dos | Slowloris 慢速 DoS 攻击测试 |
| `http-fileupload-exploiter` | exploit, vuln | 任意文件上传漏洞利用 |
| `http-internal-ip-disclosure` | vuln, safe | 内网 IP 泄露检测 |
| `http-aspnet-debug` | vuln, safe | ASP.NET DEBUG 模式检测 |
| `http-apache-negotiation` | vuln, safe | Apache mod_negotiation 文件名泄露 |
| `http-axis2-dir-traversal` | exploit, vuln | Apache Axis2 目录遍历 (CVE-2010-0219) |
| `http-vuln-cve2009-3960` | exploit, vuln | Adobe ColdFusion 目录遍历 |
| `http-vuln-cve2011-3192` | exploit, vuln | Apache Range Header DoS (CVE-2011-3192) |
| `http-vuln-cve2012-1823` | exploit, vuln | PHP-CGI 参数注入 (CVE-2012-1823) |
| `http-vuln-cve2013-0156` | exploit, vuln | Rails XML 参数注入 (CVE-2013-0156) |
| `http-vuln-cve2014-3704` | exploit, vuln | Drupal SQL 注入 (Drupalgeddon) |
| `http-vuln-cve2015-1427` | exploit, vuln | Elasticsearch Groovy RCE |
| `http-vuln-cve2017-5638` | exploit, vuln | Apache Struts2 S2-045 RCE |
| `http-vuln-cve2017-8917` | exploit, vuln | Joomla SQL 注入 |
| `http-vuln-cve2019-5418` | exploit, vuln | Rails 文件内容泄露 |
| `http-vuln-cve2021-41773` | exploit, vuln | Apache HTTPD 路径遍历 |
| `http-cakephp-version` | discovery, safe | CakePHP 版本检测 |
| `http-wordpress-*` | discovery, vuln | WordPress 用户枚举/插件检测/漏洞 |
| `http-drupal-*` | discovery, vuln | Drupal 版本/模块枚举 |
| `http-joomla-brute` | brute, intrusive | Joomla 后台暴力破解 |
| `http-adobe-coldfusion-apsa1301` | exploit, vuln | ColdFusion 管理员绕过 (APSA13-01) |
| `http-barracuda-dir-traversal` | exploit, vuln | Barracuda 目录遍历 |
| `http-cisco-anyconnect` | vuln, safe | Cisco AnyConnect 检测 |
| `http-dlink-backdoor` | exploit, vuln | D-Link 路由器后门检测 |
| `http-huawei-hg5xx-vuln` | exploit, vuln | 华为 HG5xx 路由器漏洞 |
| `http-phpmyadmin-dir-traversal` | exploit, vuln | phpMyAdmin 目录遍历 |
| `http-vmware-path-vuln` | exploit, vuln | VMware 路径遍历 (CVE-2009-3733) |
| `http-tplink-router-cve-2019-7405` | exploit, vuln | TP-Link 路由器漏洞 |
| `http-iis-webdav-vuln` | exploit, vuln | IIS WebDAV 认证绕过 (CVE-2009-1535) |
| `http-traceroute` | discovery, safe | HTTP 跳板路由追踪 |
| `http-google-malware` | malware, external | Google Safe Browsing 恶意软件检查 |
| `http-virustotal` | external, safe | VirusTotal 文件哈希查询 |

##### SMB / NetBIOS / Windows

| 脚本 | 分类 | 用途 |
|------|------|------|
| `smb-os-discovery` | default, discovery | OS/域名/计算机名信息 |
| `smb-security-mode` | default, safe | SMB 安全级别（SMB 签名等） |
| `smb-protocols` | default, safe | 支持的 SMB 协议版本 |
| `smb-enum-shares` | discovery, intrusive | 枚举共享 |
| `smb-enum-users` | discovery, intrusive | 枚举用户 |
| `smb-enum-groups` | discovery, intrusive | 枚举用户组 |
| `smb-enum-domains` | discovery, intrusive | 枚举域 |
| `smb-enum-sessions` | discovery, intrusive | 枚举活动会话 |
| `smb-enum-processes` | discovery, intrusive | 枚举运行进程 |
| `smb-ls` | discovery, safe | 共享文件列表 |
| `smb-mbenum` | discovery, safe | 主浏览器枚举 |
| `smb-brute` | brute, intrusive | SMB 凭据暴力破解 |
| `smb-print-text` | discovery, intrusive | 打印机文本文件发现 |
| `smb-psexec` | exploit, intrusive | 远程执行（需凭据） |
| `smb-flood` | dos | SMB 连接洪泛攻击 |
| `smb-vuln-ms06-025` | vuln, safe | Ras RPC 漏洞检测 |
| `smb-vuln-ms07-029` | vuln, safe | DNS Server RPC 漏洞 |
| `smb-vuln-ms08-067` | exploit, vuln | NetAPI 漏洞 (Conficker) |
| `smb-vuln-ms10-054` | vuln, safe | SMB 漏洞 |
| `smb-vuln-ms10-061` | vuln, safe | Print Spooler 漏洞 |
| `smb-vuln-ms17-010` | exploit, vuln | EternalBlue (WannaCry 传播利用) |
| `smb-vuln-regsvc-dos` | dos, vuln | Windows Registry DoS |
| `smb-vuln-webexec` | exploit, vuln | WebExec 漏洞 (CVE-2015-0009) |
| `smb-vuln-cve2009-3103` | vuln, safe | SMBv2 漏洞 |
| `smb2-capabilities` | default, safe | SMBv2 协议能力 |
| `smb2-time` | default, safe | SMBv2 远程时间 |
| `smb2-vuln-uptime` | vuln, safe | 通过 uptime 推断补丁状态 |
| `nbstat` | default, safe | NetBIOS 名称和 MAC 地址 |
| `netbus-info` | malware, safe | NetBus 后门检测 |
| `backorifice-info` | malware, safe | BackOrifice 后门检测 |
| `ms-sql-info` | version, safe | SQL Server 版本信息 |
| `ms-sql-ntlm-info` | auth, safe | SQL Server NTLM 信息 |
| `ms-sql-config` | discovery, safe | SQL Server 配置信息 |
| `ms-sql-dump-hashes` | discovery, intrusive | 导出密码哈希（需凭据） |
| `ms-sql-hasdbaccess` | discovery, intrusive | 数据库访问权限枚举 |
| `ms-sql-query` | discovery, intrusive | 执行 SQL 查询 |
| `ms-sql-tables` | discovery, intrusive | 表枚举 |
| `ms-sql-brute` | brute, intrusive | SQL Server 暴力破解 |
| `ms-sql-empty-password` | auth, safe | sa 空密码检测 |

##### SSL / TLS

| 脚本 | 分类 | 用途 |
|------|------|------|
| `ssl-cert` | default, safe | 提取 SSL 证书详情（CN/SAN/有效期） |
| `ssl-enum-ciphers` | discovery, safe | 枚举支持的加密套件并评分 |
| `ssl-known-key` | default, safe | 检测 Debian 弱密钥等已知问题密钥 |
| `ssl-heartbleed` | vuln, safe | Heartbleed 漏洞检测 (CVE-2014-0160) |
| `ssl-poodle` | vuln, safe | POODLE 漏洞检测 (CVE-2014-3566) |
| `sslv2` | default, safe | 检测是否支持 SSLv2 |
| `sslv2-drown` | vuln, safe | DROWN 攻击检测 (CVE-2016-0800) |
| `ssl-ccs-injection` | vuln, safe | CCS 注入漏洞 (CVE-2014-0224) |
| `ssl-dh-params` | vuln, safe | 弱 DH 参数检测 |
| `tls-alpn` | discovery, safe | ALPN 协议协商枚举 |
| `tls-nextprotoneg` | discovery, safe | NPN 协议协商枚举 |
| `tls-ticketbleed` | vuln, safe | Ticketbleed 漏洞 (CVE-2016-9244) |

##### SSH

| 脚本 | 分类 | 用途 |
|------|------|------|
| `ssh-hostkey` | default, safe | 显示 SSH 主机密钥指纹和类型 |
| `ssh-auth-methods` | auth, safe | 列出服务器支持的认证方法 |
| `ssh2-enum-algos` | discovery, safe | 枚举 SSHv2 支持的算法 |
| `ssh-brute` | brute, intrusive | SSH 凭据暴力破解 |
| `sshv1` | default, safe | 检测是否支持不安全的 SSHv1 |
| `ssh-run` | discovery, intrusive | 远程执行命令（需凭据） |

##### DNS

| 脚本 | 分类 | 用途 |
|------|------|------|
| `dns-nsid` | default, version | 查询 nameserver ID 和 version.bind |
| `dns-recursion` | default, safe | 检测是否开放递归查询 |
| `dns-zone-transfer` | discovery, intrusive | DNS 区域传输 (AXFR) |
| `dns-srv-enum` | discovery, safe | SRV 记录枚举 |
| `dns-brute` | discovery, brute | 子域名暴力枚举 |
| `dns-blacklist` | external, safe | DNSBL 黑名单检测 |
| `dns-fuzz` | fuzzer, intrusive | DNS 请求模糊测试 |
| `dns-client-subnet-scan` | discovery, safe | EDNS-Client-Subnet 地理定位 |
| `fcrdns` | safe | 正向-反向 DNS 一致性验证 |
| `dns-update` | discovery, intrusive | 动态 DNS 更新检测 |

##### FTP

| 脚本 | 分类 | 用途 |
|------|------|------|
| `ftp-anon` | default, auth | 匿名登录检测 |
| `ftp-syst` | default, version | SYST/STAT 获取服务器类型 |
| `ftp-brute` | brute, intrusive | FTP 凭据暴力破解 |
| `ftp-bounce` | discovery, safe | FTP Bounce 攻击检测 |
| `ftp-proftpd-backdoor` | exploit, vuln | ProFTPD 后门检测 (CVE-2011-2523) |
| `ftp-vsftpd-backdoor` | exploit, vuln | vsFTPd 后门检测 (2011 年事件) |
| `ftp-libopie` | exploit, vuln | OPIE FTP 缓冲区溢出 (CVE-2010-1938) |
| `ftp-vuln-cve2010-4221` | vuln, safe | ProFTPD 漏洞 |

##### 数据库 (MySQL / PostgreSQL / Oracle / MongoDB / Redis / CouchDB)

| 脚本 | 分类 | 用途 |
|------|------|------|
| `mysql-info` | default, version | MySQL/MariaDB 协议和版本信息 |
| `mysql-empty-password` | auth, safe | root 空密码检测 |
| `mysql-brute` | brute, intrusive | MySQL 暴力破解 |
| `mysql-databases` | discovery, intrusive | 数据库列表（需凭据） |
| `mysql-dump-hashes` | discovery, intrusive | 导出密码哈希（需凭据） |
| `mysql-enum` | discovery, intrusive | 用户/数据库枚举（需凭据） |
| `mysql-vuln-cve2012-2122` | exploit, vuln | MySQL 认证绕过 (CVE-2012-2122) |
| `mysql-audit` | discovery, intrusive | 安全配置审计 |
| `pgsql-brute` | discovery, brute | PostgreSQL 数据库/表枚举 |
| `postgres-brute` | brute, intrusive | PostgreSQL 暴力破解 |
| `oracle-brute` | brute, intrusive | Oracle 暴力破解 |
| `oracle-enum-users` | auth, intrusive | Oracle 用户枚举 |
| `oracle-sid-brute` | discovery, intrusive | Oracle SID 枚举 |
| `mongodb-info` | default, safe | MongoDB 服务器信息 |
| `mongodb-databases` | default, discovery | 数据库列表 |
| `mongodb-brute` | brute, intrusive | MongoDB 暴力破解 |
| `redis-info` | discovery, safe | Redis 服务器信息 |
| `redis-brute` | brute, intrusive | Redis 暴力破解 |
| `couchdb-databases` | discovery, safe | CouchDB 数据库列表 |
| `cassandra-info` | discovery, safe | Cassandra 集群信息 |
| `informix-brute` | brute, intrusive | IBM Informix 暴力破解 |

##### 邮件 (SMTP / POP3 / IMAP)

| 脚本 | 分类 | 用途 |
|------|------|------|
| `smtp-commands` | default, safe | 枚举支持的 SMTP 命令 (EHLO) |
| `smtp-enum-users` | discovery, intrusive | VRFY/EXPN/RCPT 用户枚举 |
| `smtp-ntlm-info` | auth, safe | SMTP NTLM 信息 |
| `smtp-brute` | brute, intrusive | SMTP 暴力破解 |
| `smtp-open-relay` | discovery, intrusive | 开放中继检测 |
| `smtp-strangeport` | malware, safe | 非标准端口 SMTP（可能为恶意软件） |
| `smtp-vuln-cve2010-4344` | vuln, safe | Exim 漏洞 |
| `smtp-vuln-cve2011-1720` | vuln, safe | Postfix 漏洞 |
| `smtp-vuln-cve2011-1764` | vuln, safe | Exim DKIM 漏洞 |
| `pop3-capabilities` | version, safe | POP3 服务能力信息 |
| `pop3-brute` | brute, intrusive | POP3 暴力破解 |
| `pop3-ntlm-info` | auth, safe | POP3 NTLM 信息 |
| `imap-capabilities` | default, version | IMAP 服务能力信息 |
| `imap-brute` | brute, intrusive | IMAP 暴力破解 |
| `imap-ntlm-info` | auth, safe | IMAP NTLM 信息 |

##### SNMP

| 脚本 | 分类 | 用途 |
|------|------|------|
| `snmp-info` | default, safe | SNMP 协议版本和基础信息 |
| `snmp-sysdescr` | default, safe | 系统描述 (sysDescr) |
| `snmp-brute` | brute, intrusive | SNMP 团体字符串暴力破解 |
| `snmp-interfaces` | discovery, safe | 网络接口信息 |
| `snmp-netstat` | discovery, safe | netstat 风格连接信息 |
| `snmp-processes` | discovery, safe | 运行进程列表 |
| `snmp-win32-services` | discovery, safe | Windows 服务列表 |
| `snmp-win32-shares` | discovery, safe | Windows 共享列表 |
| `snmp-win32-software` | discovery, safe | 已安装软件列表 |
| `snmp-win32-users` | discovery, safe | Windows 用户账户列表 |
| `snmp-ios-config` | vuln, intrusive | Cisco IOS 配置导出 |

##### 其他常用脚本

| 脚本 | 目标 | 分类 | 用途 |
|------|------|------|------|
| `banner` | 任意 TCP | default, safe | 通用 Banner 抓取 |
| `rpcinfo` | RPC (111) | default, safe | Portmapper 服务列表 |
| `nfs-showmount` | NFS (2049) | discovery, safe | NFS 导出列表 |
| `nfs-ls` | NFS | discovery, safe | NFS 文件列表 |
| `nfs-statfs` | NFS | discovery, safe | NFS 磁盘信息 |
| `ntp-info` | NTP (123) | default, safe | NTP 时间/版本/配置 |
| `ntp-monlist` | NTP | discovery, safe | NTP monlist 客户端列表 |
| `ike-version` | IKE (500) | default, version | VPN 设备/版本检测 |
| `vnc-info` | VNC (5900) | auth, safe | VNC 协议版本和安全类型 |
| `vnc-brute` | VNC | brute, intrusive | VNC 暴力破解 |
| `rdp-ntlm-info` | RDP (3389) | default, auth | RDP NTLM 信息 |
| `rdp-vuln-ms12-020` | RDP | vuln, safe | RDP DoS (MS12-020) |
| `sip-methods` | SIP (5060) | discovery, safe | SIP 方法枚举 |
| `sip-brute` | SIP | brute, intrusive | SIP 凭据暴力破解 |
| `sip-enum-users` | SIP | discovery, brute | SIP 用户枚举 |
| `ldap-search` | LDAP (389) | discovery, safe | LDAP 目录搜索 |
| `ldap-brute` | LDAP | brute, intrusive | LDAP 暴力破解 |
| `upnp-info` | UPnP | default, safe | UPnP 设备信息 |
| `broadcast-upnp-info` | UPnP | broadcast, safe | UPnP 广播发现 |
| `broadcast-dhcp-discover` | DHCP | broadcast, safe | DHCP 服务器发现 |
| `broadcast-dns-service-discovery` | mDNS | broadcast, safe | DNS 服务发现 |
| `broadcast-wsdd-discover` | WS-Discovery | broadcast, safe | WS-Discovery 设备发现 |
| `broadcast-wake-on-lan` | WOL | broadcast, safe | Wake-On-LAN 发送 |
| `whois-domain` | WHOIS | external, safe | 域名 WHOIS 查询 |
| `whois-ip` | WHOIS | external, safe | IP WHOIS 查询 |
| `shodan-api` | Shodan | external, safe | Shodan 主机信息查询 |
| `asn-query` | BGP | external, safe | IP 到 AS 号映射 |
| `ip-geolocation-*` | GeoIP | external, safe | IP 地理位置查询 |
| `clock-skew` | 通用 | safe | 时钟偏移分析 |
| `duplicates` | 通用 | safe | 多宿主主机检测 |
| `firewalk` | 防火墙 | safe | 防火墙规则探测 |
| `ipmi-cipher-zero` | IPMI (623) | exploit, vuln | IPMI 认证绕过 (CVE-2013-4786) |
| `supermicro-ipmi-conf` | IPMI | exploit, vuln | Supermicro IPMI 配置导出 |
| `java-rmi` | Java RMI | exploit, vuln | Java RMI 代码执行 |
| `rmi-vuln-classloader` | RMI | exploit, vuln | RMI ClassLoader 漏洞 (CVE-2013-1537) |
| `jdwp-exec` | JDWP | exploit, vuln | Java Debug Wire Protocol RCE |
| `clamav-exec` | ClamAV | exploit, vuln | ClamAV 命令执行 (CVE-2018-0202) |
| `realvnc-auth-bypass` | VNC | exploit, vuln | RealVNC 认证绕过 |
| `samba-vuln-cve-2012-1182` | Samba | exploit, vuln | Samba root RCE |
| `rsa-vuln-roca` | SSL/TLS | vuln, safe | ROCA 密钥漏洞 (CVE-2017-15361) |
| `p2p-conficker` | 通用 | malware, safe | Conficker 蠕虫检测 |
| `qscan` | 通用 | discovery | 网络路径可靠性分析 |

---

#### 实用脚本组合

```bash
# === 全量信息收集（安全、不具破坏性）===
nmap -sV -sC -O -p- --reason -T4 -oA full_recon 192.168.1.1

# === Web 应用全面安全检查 ===
nmap -p 80,443,8080,8443 \
  --script="http-* and (safe or vuln) and not dos" \
  --script-args="http.useragent='Mozilla/5.0 (compatible; NSE)'" \
  -oA web_audit \
  192.168.1.1

# === SSL/TLS 安全评估 ===
nmap -p 443,8443,993,995,465 \
  --script="ssl-*" \
  -oA ssl_audit \
  192.168.1.1

# === SMB 信息收集 + 漏洞检测 ===
nmap -p 139,445 \
  --script="smb-* and (safe or vuln) and not dos" \
  -oA smb_recon \
  192.168.1.0/24

# === 数据库发现 + 空密码检测 ===
nmap -p 3306,5432,1433,27017,6379 \
  --script="mysql-empty-password,ms-sql-empty-password,mongodb-databases,redis-info" \
  192.168.1.0/24

# === 漏洞快速扫描（不包含 DoS 和暴力破解）===
nmap -sV --script="vuln and not (dos or brute)" -T4 -oA vuln_scan 192.168.1.1

# === 隐蔽扫描 + 安全脚本 ===
nmap -sS -T2 -f -g 53 \
  --script="default and not intrusive" \
  --scan-delay 3s \
  -oA stealth_recon \
  192.168.1.1
```

#### NSE 脚本查找技巧

```bash
# 列出所有脚本及其分类
ls /usr/share/nmap/scripts/ | while read s; do
  echo -n "$s -> "
  head -5 /usr/share/nmap/scripts/"$s" | grep -oP 'categories\s*=\s*\{[^}]+\}' | head -1
done

# 按端口/服务找脚本
grep -rl "^portrule" /usr/share/nmap/scripts/ | xargs grep -l "port.*=.*{.*80"

# 找出高危脚本（需谨慎使用）
grep -rl "categories.*\(exploit\|dos\|brute\)" /usr/share/nmap/scripts/

# 找出所有 CVE 相关脚本
ls /usr/share/nmap/scripts/ | grep -i cve
```

### 五、防火墙 / IDS 规避

```bash
# 26. 分片数据包，绕过简单包过滤防火墙
nmap -f 192.168.230.128

# 27. 指定 MTU 分片大小
nmap --mtu 16 192.168.230.128

# 28. 源端口伪装（使用常见放行端口如 DNS 53）
nmap -g 53 -sS 192.168.230.128

# 29. 诱饵扫描（混入 3 个虚假 IP）
nmap -D 192.168.230.50,192.168.230.60,ME 192.168.230.128

# 30. 随机化扫描顺序 + 延迟
nmap --randomize-hosts --scan-delay 1s 192.168.230.0/24

# 31. 附加随机数据填充（混淆 DPI 特征检测）
nmap --data-length 100 192.168.230.128

# 32. 伪造错误校验和（探测防火墙/IDS 是否存在）
nmap --badsum 192.168.230.128

# 33. 伪造 MAC 地址（绕过内网 MAC 过滤）
nmap --spoof-mac Cisco 192.168.230.128
```

### 六、性能调优

```bash
# 34. 快速扫描内网（T4 + 无 DNS + 限端口）
nmap -T4 -n -F 192.168.230.0/24

# 35. 激进扫描外网（T4，但注意 IDS 告警）
nmap -T4 -A 192.168.230.128

# 36. 超隐蔽扫描（T1，绕过 IDS/IPS）
nmap -T1 -p 1-1000 --max-retries 0 192.168.230.128

# 37. 控制发包速率（每秒最少/最多包数）
nmap --min-rate 100 --max-rate 500 192.168.230.128

# 38. 限制单主机扫描超时
nmap --host-timeout 5m 192.168.230.0/24
```

#### 时序模板速查

| 模板 | 用途 | 扫描延迟 | 并行度 |
|------|------|----------|--------|
| `-T0` | 偏执 / IDS 规避 | 5 分钟 | 串行 |
| `-T1` | 潜行 / 避免被发现 | 15 秒 | 串行 |
| `-T2` | 礼貌 / 不占用带宽 | 0.4 秒 | 串行 |
| `-T3` | 正常（默认） | — | — |
| `-T4` | 激进 / 内网扫描 | — | 并行 |
| `-T5` | 疯狂 / 千兆局域网 | — | 高度并行 |

### 七、输出与结果处理

```bash
# 39. 三种格式同时输出
nmap -oA scan_result 192.168.230.128
# 生成: scan_result.nmap (文本), scan_result.xml, scan_result.gnmap

# 40. 只输出到屏幕，不保存文件
nmap -v 192.168.230.128

# 41. 显示端口为什么判断为 open/closed（很有用）
nmap --reason 192.168.230.128

# 42. 只显示开放端口
nmap --open 192.168.230.0/24

# 43. 从文件恢复中断的扫描
nmap --resume scan_result.nmap
```

#### 输出格式对比

| 格式 | 选项 | 适合场景 |
|------|------|----------|
| 普通文本 | `-oN` | 人工阅读 |
| XML | `-oX` | 工具解析、导入 Metasploit / Nessus |
| Grepable | `-oG` | `grep` / `awk` 快速过滤 |
| 全部 | `-oA` | 同时生成以上三种 |

#### Grepable 输出快速处理

```bash
# 提取所有开放端口的主机和端口号
grep "open" scan_result.gnmap | awk '{print $2, $5}'

# 统计在线主机数
grep "Status: Up" scan_result.gnmap | wc -l

# 提取所有开放 22 端口的 IP
grep "22/open" scan_result.gnmap | awk '{print $2}'
```

---

## 实战场景

### 场景 1：内网存活探测（快速摸清网段）

```bash
# 第一步：ARP 扫描，找出所有在线主机（最快最准）
nmap -sn -PR 192.168.230.0/24 -oA step1_alive

# 第二步：从存活主机中提取 IP 列表
grep "Nmap scan report" step1_alive.nmap | awk '{print $NF}' | tr -d '()' > alive_ips.txt

# 第三步：对在线主机做快速端口扫描
nmap -T4 -F -iL alive_ips.txt -oA step2_ports
```

### 场景 2：渗透测试信息收集

```bash
# 全端口扫描 + 服务版本 + OS 检测（适合单个目标）
nmap -p- -sV -O -sC --reason -T4 \
  -oA recon_full \
  192.168.230.128
```

扫描阶段建议：

| 阶段 | 命令 | 目的 |
|------|------|------|
| 1 | `nmap -sn 网段` | 找出存活主机 |
| 2 | `nmap -p- --min-rate 1000 目标` | 快速全端口发现 |
| 3 | `nmap -sV -sC -p 开放端口 目标` | 对开放端口做深度探测 |
| 4 | `nmap --script=vuln -p 开放端口 目标` | 漏洞检测 |

### 场景 3：Web 服务器深度探测

```bash
# HTTP 相关脚本集合
nmap -p 80,443,8080,8443 \
  --script="http-*" \
  --script-args="http.useragent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'" \
  -oA web_deep \
  192.168.230.128
```

Web 探测常用脚本：

| 脚本 | 作用 |
|------|------|
| `http-title` | 获取页面标题 |
| `http-headers` | 分析响应头（Server 版本等） |
| `http-methods` | 检查允许的 HTTP 方法 |
| `http-enum` | 目录/文件枚举（类似 dirsearch） |
| `http-robots.txt` | 读取 robots.txt |
| `http-shellshock` | Shellshock 漏洞检测 |
| `http-sql-injection` | 简单 SQL 注入探测 |
| `http-vuln-cve2017-5638` | Struts2 S2-045 漏洞检测 |

### 场景 4：SMB / Windows 内网渗透

```bash
# SMB 共享枚举 + MS17-010 检测
nmap -p 139,445 \
  --script="smb-enum-shares,smb-enum-users,smb-vuln-ms17-010,smb-os-discovery" \
  -oA smb_recon \
  192.168.230.0/24
```

SMB 常用脚本：

| 脚本 | 作用 |
|------|------|
| `smb-os-discovery` | SMB OS 信息 |
| `smb-enum-shares` | 枚举共享 |
| `smb-enum-users` | 枚举用户 |
| `smb-vuln-ms17-010` | 永恒之蓝漏洞检测 |
| `smb-vuln-ms08-067` | MS08-067 漏洞检测 |

### 场景 5：规避 WAF / IDS 的隐蔽扫描

```bash
# 低慢扫描 + 诱饵 + 源端口伪装 + 分片
nmap -sS \
  -T2 \
  -f \
  --mtu 24 \
  -g 53 \
  -D 192.168.230.10,192.168.230.20,ME \
  --randomize-hosts \
  --scan-delay 3s \
  --data-length 64 \
  -p 22,80,443,3306,8080 \
  -oA stealth_scan \
  192.168.230.128
```

---

## 端口状态含义

| 状态 | 含义 |
|------|------|
| `open` | 端口可达，有服务在监听 |
| `closed` | 端口可达，但没有服务监听 |
| `filtered` | 无法判断，可能被防火墙/SELinux 过滤 |
| `unfiltered` | 端口可达，但无法判断 open/closed（ACK 扫描结果） |
| `open|filtered` | 可能是 open 也可能是 filtered（UDP/FIN/Null/Xmas 扫描常见） |
| `closed|filtered` | 可能是 closed 也可能是 filtered（IP Protocol 扫描） |

## 实用技巧

- **内网扫描优先用 ARP**：`-sn -PR` 不会被防火墙拦截，且速度极快
- **全端口扫描分段做**：先用 `-T4 -p-` 快速发现开放端口，再对开放端口做 `-sV` 深度探测
- **UDP 扫描很慢**：只扫描关键端口（53, 67, 68, 123, 161, 500），不要全量
- **绕过禁 Ping**：目标不响应 ICMP 时加 `-Pn`，跳过主机发现直接扫描
- **`--reason` 很实用**：显示端口判断依据（如 `syn-ack`、`reset`），方便排查误判
- **`-A` 是日常首选**：一次性完成服务版本、OS、默认脚本和路由追踪
- **UDP + 版本检测陷阱**：UDP 扫描本身慢，加上 `-sV` 会更慢。仅对关键 UDP 端口做版本检测
- **避免扫描误伤**：`-T5` 在广域网几乎必丢结果；`-T3` 或 `-T4` 是最稳妥选择
- **大网段存活探测**：`-sn` 比 `-sL` 更准，`-PE`（ICMP Ping）在互联网环境中可能被过滤，优先考虑 `-PS80,443`
- **`-sV --version-intensity 0` 是轻量 banner 抓取**，`9` 是全量探测；日常用默认 7 即可，遇误判再提升
