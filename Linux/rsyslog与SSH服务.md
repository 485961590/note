# rsyslog 与 SSH 服务

> Linux 一切皆文件。rsyslog 和 SSH 不是黑盒服务——拆开来看，就是几个二进制、几个配置文件、几个密钥文件和一堆日志文件。理解每个文件的角色，比记住命令更重要。

两个服务的本质：

```
rsyslog = /usr/sbin/rsyslogd（二进制）
        + /etc/rsyslog.conf（主配置）
        + /etc/rsyslog.d/*.conf（模块化配置）
        + /dev/log（Unix socket，接收日志的入口）
        + /var/log/*（日志输出文件）
        + /etc/logrotate.d/rsyslog（日志轮替）

sshd    = /usr/sbin/sshd（二进制）
        + /etc/ssh/sshd_config（服务端配置）
        + /etc/ssh/ssh_host_*_key（主机密钥）
        + ~/.ssh/authorized_keys（用户公钥白名单）
        + /etc/pam.d/sshd（PAM 认证模块）
        + /var/log/auth.log 或 /var/log/secure（SSH 日志，由 rsyslog 管理）
```

---

## 第一部分：rsyslogd 日志服务

### 1.1 /usr/sbin/rsyslogd -- 二进制程序

**角色**：rsyslog 的守护进程本体。系统启动时由 systemd 拉起，读配置文件，打开 socket 监听，把收到的日志按规则写到对应文件。

```bash
# 查看进程
ps aux | grep rsyslogd

# systemd 管理（所有发行版通用）
systemctl status rsyslog
systemctl start rsyslog
systemctl stop rsyslog
systemctl restart rsyslog
systemctl enable rsyslog        # 开机自启

# 注意服务名是 rsyslog，不是 rsyslogd
```

---

### 1.2 /etc/rsyslog.conf -- 主配置文件

**角色**：rsyslog 的入口配置文件。定义加载哪些模块、使用什么模板、日志按什么规则路由。rsyslogd 启动时第一个读它。

通常此文件本身不写具体规则，而是通过 `$IncludeConfig` 引入 `/etc/rsyslog.d/` 下的模块化配置。

```bash
# 查看主配置
cat /etc/rsyslog.conf
```

典型的 `/etc/rsyslog.conf` 结构：

```
#### MODULES ####
module(load="imuxsock")    # 从 /dev/log 读本地日志
module(load="imklog")      # 从内核日志缓冲区读
module(load="imtcp")       # TCP 接收模块（远程日志）

#### GLOBAL DIRECTIVES ####
$WorkDirectory /var/spool/rsyslog
$IncludeConfig /etc/rsyslog.d/*.conf    # 引入模块化配置

#### RULES ####
# facility.priority    action
auth,authpriv.*        /var/log/auth.log
*.*;auth,authpriv.none -/var/log/syslog
```

#### facility（日志来源）对照表

| facility | 说明 | 典型产生者 |
|----------|------|-----------|
| `auth` | 认证相关（废弃，用 authpriv） | login, su |
| `authpriv` | 认证相关（非系统守护进程也用它） | sshd, sudo, su |
| `cron` | 定时任务 | crond |
| `daemon` | 无独立 facility 的守护进程 | 各种后台服务 |
| `kern` | 内核消息 | 内核模块, dmesg |
| `lpr` | 打印服务 | CUPS |
| `mail` | 邮件服务 | postfix, sendmail |
| `news` | NNTP 新闻组 | inn |
| `syslog` | syslog 服务自身产生的日志 | rsyslogd 自身 |
| `user` | 用户进程（默认 facility） | 普通用户程序 |
| `uucp` | UUCP 系统 | 几乎不用 |
| `local0` ~ `local7` | 自定义 facility | 应用程序自定义 |
| `*` | 通配，所有 facility | -- |

#### priority（严重等级）对照表

等级从高到低，配置中指定的等级**包含该等级及更严重的所有消息**。

| priority | 说明 | 典型场景 |
|----------|------|---------|
| `emerg` (0) | 系统不可用 | kernel panic |
| `alert` (1) | 需要立即干预 | 磁盘损坏 |
| `crit` (2) | 临界条件 | 硬件错误 |
| `err` (3) | 错误 | 应用程序报错 |
| `warning` (4) | 警告 | 磁盘空间不足 |
| `notice` (5) | 正常但值得注意的事件 | 服务启动/停止 |
| `info` (6) | 信息性消息 | 正常操作日志 |
| `debug` (7) | 调试信息 | 开发排错用 |
| `*` | 所有等级 | -- |
| `none` | 不记录 | 用于排除某个 facility |

配置的含义举例：

```bash
# authpriv 的所有等级日志 → /var/log/auth.log
authpriv.*    /var/log/auth.log

# 所有 facility 的 info 及以上等级 → /var/log/messages
*.info        /var/log/messages

# 所有日志写入 syslog，但排除 auth 相关的
*.*;auth,authpriv.none    /var/log/syslog

# cron 日志只写 notice 及以上（不写 info/debug）
cron.notice   /var/log/cron

# kernel 日志除了 debug 以外全部记录
kern.*;kern.!=debug    /var/log/kern.log
```

#### action（日志目的地）的几种形式

| action 格式 | 说明 | 示例 |
|------------|------|------|
| `/path/to/file` | 写入普通文件 | `/var/log/auth.log` |
| `-/path/to/file` | 写入文件（不立即 sync，性能更好） | `-/var/log/syslog` |
| `|/path/to/program` | 管道发给程序 | `|/usr/bin/logger` |
| `/dev/console` | 输出到终端 | `/dev/console` |
| `@hostname` | UDP 发送到远程（默认 514） | `@192.168.1.100` |
| `@@hostname` | TCP 发送到远程 | `@@192.168.1.100` |
| `用户名` | 写到指定用户的终端 | `root` |
| `*` | 写到所有登录用户终端 | `*` |

---

### 1.3 /etc/rsyslog.d/ -- 模块化配置目录

**角色**：把不同场景的日志规则拆成独立文件（如 `50-default.conf`、`20-ufw.conf`），通过主配置中的 `$IncludeConfig /etc/rsyslog.d/*.conf` 自动加载。

文件命名约定：**数字前缀控制加载顺序**，数字越小越先加载。

```bash
ls /etc/rsyslog.d/
# 50-default.conf     -- 默认规则（各发行版的主要规则文件）
# 20-ufw.conf         -- Ubuntu ufw 防火墙日志
# 30-remote.conf      -- 管理员手写的远程日志规则
```

**发行版差异**：
- Debian/Ubuntu 重度使用 `rsyslog.d/`，默认规则分散在多个文件中
- CentOS/RHEL 7 的默认规则大多写死在 `/etc/rsyslog.conf` 中，`rsyslog.d/` 仅作为扩展
- Kali 基于 Debian，结构相同

---

### 1.4 /etc/default/rsyslog 与 /etc/sysconfig/rsyslog -- 启动参数

**角色**：定义 rsyslogd 进程的额外启动参数，由 systemd unit 或 init 脚本在启动前 source。

| 发行版 | 文件路径 |
|--------|---------|
| Debian / Ubuntu / Kali | `/etc/default/rsyslog` |
| CentOS / RHEL 7+ | `/etc/sysconfig/rsyslog` |

典型内容：

```bash
# /etc/default/rsyslog (Debian)
RSYSLOGD_OPTIONS="-c5"   # -c5 指定兼容模式版本 5

# /etc/sysconfig/rsyslog (CentOS)
SYSLOGD_OPTIONS="-c 5"
```

日常很少需要改这个文件，除非要远程调试（加 `-d` 开启 debug 模式）或指定其他配置文件路径（加 `-f`）。

---

### 1.5 /var/log/ -- 日志输出目录

**角色**：rsyslog 的最终产物都落在这里。这些是普通文本文件，用 `cat`、`grep`、`tail -f` 直接操作。

这是"一切皆文件"最直观的体现——系统运行的所有痕迹都变成了可以读、可以搜、可以分析的文本文件。

#### 各日志文件对照表

| 日志文件 | 记录内容 | 发行版 |
|---------|---------|--------|
| `/var/log/syslog` | 系统全局日志（除 auth 外大部分 facility 的日志），Debian 系最全面的日志文件 | Debian / Ubuntu / Kali |
| `/var/log/messages` | 系统全局日志，CentOS/RHEL 系最全面的日志文件 | CentOS / RHEL（主）; Debian/Ubuntu（少量） |
| `/var/log/auth.log` | 认证相关：SSH 登录/登出、sudo 提权、su 切换用户 | Debian / Ubuntu / Kali |
| `/var/log/secure` | 认证相关：SSH 登录/登出、sudo 提权、su 切换用户 | CentOS / RHEL |
| `/var/log/kern.log` | 内核日志（驱动加载、硬件事件、oops） | Debian / Ubuntu / Kali |
| `/var/log/cron` | cron 任务执行记录 | CentOS / RHEL（独立）；Debian 系合在 syslog 中 |
| `/var/log/mail.log` | 邮件服务日志 | Debian / Ubuntu |
| `/var/log/maillog` | 邮件服务日志 | CentOS / RHEL |
| `/var/log/boot.log` | 系统启动过程中的服务启动记录 | 各发行版基本一致 |
| `/var/log/dmesg` | 内核环缓冲区日志（开机阶段硬件检测） | 各发行版基本一致 |
| `/var/log/dpkg.log` | APT/dpkg 包管理操作日志 | Debian / Ubuntu / Kali |
| `/var/log/yum.log` | YUM 包管理操作日志 | CentOS / RHEL 7 |
| `/var/log/dnf.log` | DNF 包管理操作日志 | CentOS / RHEL 8+ |
| `/var/log/ufw.log` | ufw 防火墙日志 | 使用 ufw 的发行版 |
| `/var/log/firewalld` | firewalld 防火墙日志（目录） | 使用 firewalld 的发行版 |

#### 日常日志操作

```bash
# 实时查看最新日志（最常用）
tail -f /var/log/syslog          # Debian 系
tail -f /var/log/messages        # RHEL 系

# 搜 SSH 登录记录
grep sshd /var/log/auth.log      # Debian 系
grep sshd /var/log/secure        # RHEL 系

# 搜特定时间段的日志
grep "Jun 21 10:" /var/log/syslog

# 搜错误
grep -i "error\|fail\|critical" /var/log/syslog

# 日志文件大小监控
ls -lhS /var/log/
du -sh /var/log/*
```

---

### 1.6 /dev/log -- Unix 域 socket

**角色**：应用程序调用 `syslog()` 函数写日志时，内核把消息发送到这个 Unix socket，rsyslogd 从这头接收。这是 rsyslog 接收本地日志的入口。

这是"一切皆文件"的典型体现——进程间通信变成了对一个"文件"（socket）的读写。

```bash
ls -la /dev/log
# srw-rw-rw- 1 root root 0 Jun 21 10:00 /dev/log
# 注意类型是 s（socket），不是普通文件

# 在 systemd 系统中，/dev/log 通常是到 /run/systemd/journal/dev-log 的符号链接
ls -la /dev/log
# lrwxrwxrwx 1 root root 28 Jun 21 10:00 /dev/log -> /run/systemd/journal/dev-log
```

rsyslog 通过 `imuxsock` 模块读取此 socket：

```bash
# 在 rsyslog.conf 中加载
module(load="imuxsock")
```

#### systemd journald 与 rsyslog 的关系

在 systemd 系统中，日志流是这样的：

```
应用程序 → syslog() → /dev/log → journald → /run/systemd/journal/syslog → rsyslogd → /var/log/syslog
                               ↘ 同时 journald 自己也存到 /run/log/journal/（二进制格式，不跨重启）
```

这意味着即使 rsyslog 停了，`journalctl` 仍然能查到日志。两者互补：
- `journalctl`：内存中的短期日志，开机期间的
- rsyslog + `/var/log/`：磁盘上的持久日志，可跨重启

---

### 1.7 /var/run/rsyslogd.pid -- PID 文件

**角色**：记录 rsyslogd 主进程的 PID。systemd 和 init 脚本用它判断进程是否存活，也用于发送信号（如 `kill -HUP` 重载配置）。

```bash
cat /var/run/rsyslogd.pid
# 1234

# 实际路径可能是 /run/rsyslogd.pid（/var/run 通常是 /run 的符号链接）
```

---

### 1.8 /var/spool/rsyslog/ -- 工作目录

**角色**：rsyslog 运行时存放临时文件、队列文件、状态文件的目录。当远程目标不可达或磁盘满时，rsyslog 把未写入的日志暂存到这里。

```bash
ls /var/spool/rsyslog/
# 通常为空，只有在远程日志阻塞或配置了磁盘队列时才会有文件
```

在 rsyslog.conf 中指定：

```bash
$WorkDirectory /var/spool/rsyslog
```

---

### 1.9 /etc/logrotate.d/rsyslog -- 日志轮替配置

**角色**：这不是 rsyslog 自身的一部分，但与日志文件紧密耦合。logrotate 定期读取此文件，决定 `/var/log/` 下的日志怎么切割、保留几份、是否压缩。

```bash
cat /etc/logrotate.d/rsyslog
```

典型内容（Debian/Ubuntu）：

```conf
/var/log/syslog
/var/log/mail.log
/var/log/kern.log
/var/log/auth.log
/var/log/user.log
/var/log/cron.log
{
    rotate 7          # 保留 7 个归档
    daily             # 每天轮替
    missingok         # 文件不存在也不报错
    notifempty        # 空文件不轮替
    delaycompress     # 延迟一天压缩（当前归档不压缩）
    compress          # 压缩归档
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
```

典型内容（CentOS/RHEL）：

```conf
/var/log/messages
/var/log/secure
/var/log/maillog
/var/log/cron
/var/log/spooler
/var/log/boot.log
{
    rotate 4          # RHEL 默认保留 4 个归档（比 Debian 少）
    monthly           # 每月轮替（不再是 daily）
    ...
}
```

#### logrotate 关键参数

| 参数 | 说明 |
|------|------|
| `rotate N` | 保留 N 个历史归档 |
| `daily/weekly/monthly` | 轮替周期 |
| `size 100M` | 文件达到指定大小时轮替（和周期可以同时用） |
| `compress` | 对旧归档做 gzip 压缩 |
| `delaycompress` | 延迟一个周期再压缩（保证当前和上一个归档都是未压缩的） |
| `missingok` | 文件不存在时不报错 |
| `notifempty` | 空文件不轮替 |
| `create 0640 root adm` | 轮替后以指定权限和属主创建新文件 |
| `sharedscripts` | 多个文件的 postrotate 只执行一次 |
| `postrotate/endscript` | 轮替后执行的命令（通常是通知 rsyslog 打开新文件） |

---

### 1.10 /usr/lib/rsyslog/ -- 模块目录

**角色**：存放 rsyslog 的动态加载模块（.so 文件）。每个模块负责一种输入或输出能力。

```bash
ls /usr/lib/rsyslog/
# imuxsock.so    -- 从 /dev/log 读本地日志
# imklog.so      -- 从内核日志缓冲区读
# imtcp.so       -- TCP 接收
# imudp.so       -- UDP 接收
# omfile.so      -- 写入文件（内置，不需要显式加载）
# ommysql.so     -- 写入 MySQL
# ompipe.so      -- 写入命名管道
# ...
```

在配置中加载：

```bash
module(load="imtcp")          # 加载 TCP 接收模块
module(load="ommysql")        # 加载 MySQL 输出模块
```

不是所有模块都默认安装。如需 MySQL 输出模块：

```bash
# Debian/Ubuntu
apt install rsyslog-mysql

# CentOS/RHEL
dnf install rsyslog-mysql
```

---

### 1.11 远程日志配置

远程日志涉及两类角色和对应的配置。

#### 作为日志服务器（接收端）

```bash
# /etc/rsyslog.d/remote-receive.conf
# 加载 TCP 和 UDP 接收模块
module(load="imtcp")
module(load="imudp")

# 监听端口
input(type="imtcp" port="514")
input(type="imudp" port="514")

# 把收到的远程日志按来源 IP 分目录存放
$template RemoteLogs,"/var/log/remote/%FROMHOST-IP%/%$YEAR%/%$MONTH%/%$DAY%/syslog.log"
*.* ?RemoteLogs
```

#### 作为日志客户端（发送端）

```bash
# /etc/rsyslog.d/remote-send.conf
# 把所有日志发送到远程服务器
*.* @@192.168.1.100:514
# @@ 表示 TCP，@ 表示 UDP
# 或者只发送 auth 相关日志
auth.* @@192.168.1.100:514
```

#### TCP / UDP / RELP 对比

| 协议 | 写法 | 可靠性 | 性能 | 适用场景 |
|------|------|--------|------|---------|
| UDP | `@host` | 不可靠，丢包不重传 | 最快 | 内网、量大、丢几条无所谓 |
| TCP | `@@host` | 可靠，丢包重传 | 中等 | 需要保证不丢日志 |
| RELP | 需加 `module(load="omrelp")` | 可靠 + 背压感知 | 中等 | 专业日志传输 |

#### TLS 加密传输

涉及的文件：

```bash
# TLS 需要的额外文件（需自己准备）
/etc/rsyslog.d/ca.pem              # CA 证书
/etc/rsyslog.d/server-cert.pem     # 服务器证书
/etc/rsyslog.d/server-key.pem      # 服务器私钥
```

---

### 1.12 发行版差异汇总

| 维度 | Debian / Ubuntu | CentOS / RHEL 7+ | Kali |
|------|----------------|-------------------|------|
| 包名 | `rsyslog` | `rsyslog` | `rsyslog`（预装） |
| 主配置文件 | `/etc/rsyslog.conf` | `/etc/rsyslog.conf` | `/etc/rsyslog.conf` |
| 模块化目录 | `/etc/rsyslog.d/`（重度使用） | `/etc/rsyslog.d/`（作为扩展） | 同 Debian |
| 主系统日志 | `/var/log/syslog` | `/var/log/messages` | `/var/log/syslog` |
| 认证日志 | `/var/log/auth.log` | `/var/log/secure` | `/var/log/auth.log` |
| 启动参数文件 | `/etc/default/rsyslog` | `/etc/sysconfig/rsyslog` | `/etc/default/rsyslog` |
| 轮替周期 | daily, 保留 7 份 | monthly, 保留 4 份 | 同 Debian |
| 日志属组 | `adm` 组可读 | `root` 组可读（部分需要 sudo） | 同 Debian |

---

## 第二部分：SSH 服务（sshd）

### 2.1 /usr/sbin/sshd -- 服务端二进制

**角色**：SSH 守护进程本体。监听 TCP 22 端口，接收 SSH 客户端的连接请求，完成加密握手和用户认证，最终分配给用户一个 shell。

```bash
# 查看 sshd 进程
ps aux | grep sshd

# 测试配置文件语法（修改 sshd_config 后先跑这个）
sshd -t

# 详细模式测试（看加载了哪些配置、有没有错误）
sshd -T | head -30

# 指定配置文件测试
sshd -t -f /etc/ssh/sshd_config

# systemd 管理
systemctl status sshd       # CentOS/RHEL 服务名是 sshd
systemctl status ssh        # Debian/Ubuntu/Kali 服务名是 ssh
systemctl restart sshd
systemctl enable sshd
```

**服务名差异注意**：
- CentOS/RHEL/Fedora：`systemctl restart sshd`
- Debian/Ubuntu/Kali：`systemctl restart ssh`

---

### 2.2 /etc/ssh/sshd_config -- SSH 守护进程配置文件

**角色**：sshd 启动时读取的核心配置，控制监听端口、认证方式、允许登录的用户、加密参数等所有服务端行为。只有 root 能修改。

修改后必须检查语法再重启：

```bash
sshd -t && systemctl restart sshd    # 语法检查通过才重启
```

#### 关键参数详解

##### 监听和连接

```conf
# 监听端口（默认 22）
Port 22

# 监听地址（默认 0.0.0.0 全部接口；可指定特定 IP）
# ListenAddress 0.0.0.0
ListenAddress 192.168.1.10

# 协议版本（应只允许 2，版本 1 已不安全）
Protocol 2
```

##### 认证方式

```conf
# 是否允许 root 直接登录
# yes:              允许密码和密钥
# prohibit-password: 只允许密钥登录 root（推荐）
# no:                禁止 root 登录
PermitRootLogin prohibit-password

# 是否允许密码登录
PasswordAuthentication yes

# 是否允许公钥认证
PubkeyAuthentication yes

# 指定 authorized_keys 文件路径
AuthorizedKeysFile .ssh/authorized_keys

# SSH 密钥认证时是否检查用户家目录和 authorized_keys 的权限
StrictModes yes
```

| PermitRootLogin 值 | 含义 |
|-------------------|------|
| `yes` | root 可以用密码或密钥登录 |
| `prohibit-password` | root 只能用密钥登录（推荐） |
| `forced-commands-only` | root 只能用密钥登录且只能执行指定命令 |
| `no` | root 不能通过 SSH 登录 |

##### 用户访问控制

```conf
# 白名单：只允许这些用户登录（优先级最高）
AllowUsers alice bob

# 白名单：只允许这些用户组登录
AllowGroups sshusers admin

# 黑名单：禁止这些用户登录（处理顺序：DenyUsers → AllowUsers → DenyGroups → AllowGroups）
DenyUsers baduser1 baduser2
DenyGroups badgroup
```

`AllowUsers` 的完整语法：

```conf
# 只允许 alice 从特定 IP 登录
AllowUsers alice@192.168.1.100

# bob 只能从任一主机登录
AllowUsers bob

# 组合
AllowUsers alice@192.168.1.* bob@*.example.com
```

##### 会话与超时

```conf
# 认证阶段最大尝试次数（超过后断开连接）
MaxAuthTries 6

# 单连接允许的最大会话数（多路复用）
MaxSessions 10

# 心跳检测：每 60 秒发一次心跳
ClientAliveInterval 60
# 连续 3 次心跳无响应则断开（即 60*3=180 秒无操作后断开）
ClientAliveCountMax 3

# 登录宽限期（秒），超时未完成认证则断开
LoginGraceTime 120

# 最大并发未认证连接数
MaxStartups 10:30:100
# 意思是：10 个以下全部放行，超过后以 30% 概率拒绝，最多 100 个
```

##### 转发控制

```conf
# X11 图形转发（把远程 GUI 转发到本地）
X11Forwarding no

# TCP 端口转发（-L / -R）
AllowTcpForwarding yes

# SSH 隧道（-w）
PermitTunnel no

# 代理转发（把本地的 SSH agent 带到远程机器上）
AllowAgentForwarding yes

# 是否允许用户通过 ~/.ssh/environment 设置环境变量
PermitUserEnvironment no
```

安全建议：如果只是远程管理，关闭不需要的转发。

##### 日志

```conf
# 日志 facility：决定日志写入 rsyslog 的哪个 facility
SyslogFacility AUTH
# 可选：DAEMON, USER, AUTH, LOCAL0 ~ LOCAL7

# 日志详细级别
LogLevel INFO
# 可选：QUIET, FATAL, ERROR, INFO, VERBOSE, DEBUG1, DEBUG2, DEBUG3
```

`SyslogFacility AUTH` + `LogLevel INFO` 意味着 SSH 登录记录会以 `auth.info` 优先级写入 rsyslog，根据 rsyslog 规则最终落入 `auth.log` 或 `secure`。

##### SFTP 子系统

```conf
# SFTP 服务端实现路径
Subsystem sftp /usr/lib/openssh/sftp-server
# 或使用 internal-sftp（不需要外部二进制，推荐）
Subsystem sftp internal-sftp
```

#### 发行版默认 sshd_config 差异

| 参数 | Debian 12 / Ubuntu 24.04 | CentOS 7 | RHEL 9 | Kali |
|------|--------------------------|----------|--------|------|
| `PermitRootLogin` | `prohibit-password` | `yes` | `prohibit-password` | `yes` |
| `PasswordAuthentication` | `yes`（部分云镜像为 `no`） | `yes` | `yes` | `yes` |
| `X11Forwarding` | `yes` | `yes` | `yes` | `yes` |
| `MaxAuthTries` | `6` | `6` | `6` | `6` |
| `AcceptEnv LANG LC_*` | 有 | 有 | 有 | 有 |

Kali 的默认配置最宽松——方便渗透测试环境中的远程操作和安全评估，但在生产环境中应该收紧。

---

### 2.3 /etc/ssh/sshd_config.d/ -- 模块化配置目录

**角色**（OpenSSH 8.2+）：和 rsyslog 的 `.d/` 目录一样，把 sshd 的配置拆成多个 `.conf` 文件，避免直接修改 `sshd_config`。sshd 会按字母顺序加载此目录下所有 `.conf` 文件。

```bash
# 例如：安全加固配置单独放一个文件
/etc/ssh/sshd_config.d/99-hardening.conf
```

内容示例：

```conf
# 和 sshd_config 一样的语法
PasswordAuthentication no
PermitRootLogin no
AllowUsers alice@192.168.1.0/24
```

**发行版支持差异**：
- Ubuntu 22.04+ / Debian 12+ / RHEL 9+：默认支持，`sshd_config` 中会有 `Include /etc/ssh/sshd_config.d/*.conf`
- CentOS 7 / RHEL 8 / Debian 11：可能没有此目录，需检查 `sshd -T | grep include`

---

### 2.4 /etc/ssh/ssh_config -- SSH 客户端系统级配置

**角色**：系统范围内所有用户的 SSH 客户端默认配置。优先级低于用户自己的 `~/.ssh/config`。

```bash
cat /etc/ssh/ssh_config
```

典型内容：

```conf
Host *
    # 以 Hash 后形式保存 known_hosts 中的主机名（更安全但无法直接阅读）
    HashKnownHosts yes
    
    # 优先用这些密钥算法
    HostKeyAlgorithms ssh-ed25519-cert-v01@openssh.com,ssh-ed25519
    
    # 优先用这些密钥交换算法
    KexAlgorithms curve25519-sha256@libssh.org
```

---

### 2.5 /etc/ssh/ssh_host_*_key.pub 与 .pub -- 主机密钥文件

**角色**：服务器的身份证。客户端首次连接时看到的那串指纹，就是这些密钥的哈希值。当重装系统或更换主机后，"HOST IDENTIFICATION HAS CHANGED" 的警告就是检测到这些文件变了。

```bash
ls -la /etc/ssh/ssh_host_*
```

#### 各密钥文件

| 私钥文件 | 公钥文件 | 算法 | 说明 |
|---------|---------|------|------|
| `ssh_host_ed25519_key` | `ssh_host_ed25519_key.pub` | Ed25519 | 现代推荐，安全性和性能最优 |
| `ssh_host_ecdsa_key` | `ssh_host_ecdsa_key.pub` | ECDSA | 椭圆曲线，比 RSA 快 |
| `ssh_host_rsa_key` | `ssh_host_rsa_key.pub` | RSA | 兼容性最好，老客户端只认这个 |

#### 权限要求

```bash
# 私钥必须是 600（只有 root 能读写），否则 sshd 拒绝启动
-rw------- 1 root root  411 Jun 21 10:00 ssh_host_ed25519_key

# 公钥是 644
-rw-r--r-- 1 root root   94 Jun 21 10:00 ssh_host_ed25519_key.pub
```

#### 查看和生成

```bash
# 查看主机密钥的指纹（这是用户首次连接时看到的）
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
# 256 SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx root@host (ED25519)

# 同时显示 MD5 指纹（某些老系统用）
ssh-keygen -l -E md5 -f /etc/ssh/ssh_host_ed25519_key.pub

# 重新生成所有主机密钥（谨慎：已连接的客户端会收到警告）
ssh-keygen -A
# 或者指定算法
ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ""
```

---

### 2.6 ~/.ssh/ -- 用户级 SSH 目录

**角色**：每个用户家目录下的 `.ssh/` 目录，存放该用户的 SSH 客户端配置、私钥、授权公钥、已知主机列表。

这是"一切皆文件"在用户侧的体现——一个用户的 SSH 身份和信任关系，全由这个目录里的几个文件定义。

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh      # 目录权限必须是 700
```

#### 各文件角色与权限

| 文件 | 角色 | 权限 | 由谁创建 |
|------|------|------|---------|
| `~/.ssh/config` | 用户 SSH 客户端配置（Host 别名、端口、密钥、跳板等） | 600 | 用户手动 |
| `~/.ssh/authorized_keys` | 被授权登录的公钥列表，一行一个。远程 sshd 在密钥登录时读取此文件 | 600 | 用户或管理员 |
| `~/.ssh/id_ed25519` | 用户的 Ed25519 私钥，绝不能泄露 | 600 | `ssh-keygen -t ed25519` |
| `~/.ssh/id_ed25519.pub` | 用户的 Ed25519 公钥，可追加到远程 authorized_keys | 644 | `ssh-keygen` 自动生成 |
| `~/.ssh/id_rsa` | 用户的 RSA 私钥 | 600 | `ssh-keygen -t rsa -b 4096` |
| `~/.ssh/id_rsa.pub` | 用户的 RSA 公钥 | 644 | `ssh-keygen` 自动生成 |
| `~/.ssh/known_hosts` | 用户曾经连接过的主机及其主机公钥。下次连接时比对，变了就报警 | 644 | SSH 客户端首次连接时自动写入 |
| `~/.ssh/environment` | SSH 登录时设置的环境变量（需 sshd_config 中 `PermitUserEnvironment yes`，默认关闭） | 600 | 用户手动 |

#### ~/.ssh/config 常用配置

```conf
# 为远程主机起别名
Host myserver
    HostName 192.168.1.100
    User root
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

# 通过跳板机访问内网机器
Host internal
    HostName 10.0.0.50
    User alice
    ProxyJump jump@192.168.1.1

# 连接复用（多个终端窗口共享一个 SSH 连接，不用重复认证）
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h:%p
    ControlPersist 10m

# 对特定主机跳过主机密钥检查（仅内网用，不安全）
Host 192.168.1.*
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

#### ~/.ssh/authorized_keys 文件

**角色**：这是最重要的一张白名单。只有公钥在这个文件里的用户才能通过密钥登录。一行一个公钥，可以加选项限制来源 IP 或允许执行的命令。

```bash
# 查看当前授权
cat ~/.ssh/authorized_keys
```

每行的完整格式：

```
[选项] 密钥类型 公钥内容 注释
```

带安全限制的示例：

```bash
# 限制此密钥只能从特定 IP 使用
from="192.168.1.100" ssh-ed25519 AAAAC3... alice@laptop

# 限制此密钥连接后只能执行指定命令（不能拿到 shell）
command="/usr/local/bin/backup.sh",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAAC3... backup@server

# 无限制的普通密钥登录
ssh-ed25519 AAAAC3... alice@laptop

# 禁止此密钥（加 no-* 前缀即可）
no-port-forwarding,no-agent-forwarding ssh-ed25519 AAAAC3... restricted-user
```

公钥分发到远程机器：

```bash
# 方式一：ssh-copy-id（推荐，自动处理权限）
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@192.168.1.100

# 方式二：手动追加
cat ~/.ssh/id_ed25519.pub | ssh user@192.168.1.100 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

---

### 2.7 /etc/ssh/ssh_known_hosts -- 系统级已知主机

**角色**：管理员可为所有用户预置可信主机的公钥。效果等同于每个用户自己的 `~/.ssh/known_hosts`，但对全系统生效。

```bash
cat /etc/ssh/ssh_known_hosts
# 格式和 ~/.ssh/known_hosts 一样
# 192.168.1.100 ssh-ed25519 AAAAC3...
```

通常用于企业内部——把所有内网服务器的公钥预置进去，用户首次连接不会看到 "Are you sure you want to continue connecting?" 确认。

---

### 2.8 /etc/pam.d/sshd -- PAM 模块配置

**角色**：SSH 登录认证时，sshd 调用 PAM（Pluggable Authentication Modules）栈来执行账号检查、密码验证、会话创建。这个文件定义了 SSH 使用哪些 PAM 模块。

PAM 是 Linux 认证系统的统一接口模块，决定了"谁可以登录、登录后有什么限制"——不只是密码对不对，还要检查账号是否过期、是否有访问时间限制、登录后挂载什么文件系统等。

```bash
cat /etc/pam.d/sshd
```

#### Debian/Ubuntu/Kali 的典型内容

```conf
# 引入通用认证模块
@include common-auth         # 验证密码是否正确
@include common-account      # 检查账号是否过期/锁定
@include common-session      # 登录后创建会话（挂载、资源限制）
@include common-password     # 密码修改策略（sshd 中通常不触发）

# 打印当天的消息（motd = message of the day）
session    optional     pam_motd.so motd=/run/motd.dynamic

# 打印上次登录信息
session    optional     pam_lastlog.so showfailed
```

#### CentOS/RHEL 的典型内容

```conf
auth       required     pam_sepermit.so
auth       substack     password-auth      # RHEL 用 password-auth 而非 common-auth
auth       include      postlogin
account    required     pam_nologin.so
account    include      password-auth
password   include      password-auth
session    required     pam_selinux.so close    # SELinux 相关
session    required     pam_loginuid.so
session    include      password-auth
session    optional     pam_motd.so
session    optional     pam_lastlog.so
session    required     pam_selinux.so open
```

#### 发行版 PAM 结构差异

| 发行版 | 引用的文件 | 特点 |
|--------|-----------|------|
| Debian / Ubuntu / Kali | `common-auth`, `common-account`, `common-session`, `common-password` | 四个 common-* 文件，结构清晰 |
| CentOS / RHEL | `password-auth`, `system-auth` | 用 `password-auth` 和 `system-auth`（system-auth 含本地账户，password-auth 可被 LDAP 等覆盖） |
| 含 SELinux 的发行版 | 额外 `pam_selinux.so` | 登录/退出时管理 SELinux 上下文 |

PAM 的出现让 SSH 的权限控制不止于 `sshd_config`，还可以通过 `pam_listfile.so` 做更细粒度的限制，例如：只允许特定用户列表中的用户登录。

---

### 2.9 /etc/ssh/moduli -- DH 模数文件

**角色**：Diffie-Hellman 密钥交换用的素数组列表。SSH 连接建立时，客户端和服务端随机选取其中的一个素数来协商会话密钥。模数越大安全性越高，但密钥协商越慢。

```bash
# 查看已加载的模数
awk '$5 > 2000' /etc/ssh/moduli | head -5
```

一般不需要手动修改。但如果对安全性要求极高（或怀疑某些模数被污染），可以自己生成：

```bash
# 生成候选模数（耗时，数小时级别）
ssh-keygen -G candidate-moduli -b 4096

# 筛选安全的模数
ssh-keygen -T /etc/ssh/moduli -f candidate-moduli

# 重启 sshd
systemctl restart sshd
```

---

### 2.10 密钥管理

#### 生成用户密钥对

```bash
# Ed25519（推荐，速度快、安全性高、密钥短）
ssh-keygen -t ed25519 -C "alice@laptop"

# RSA 4096（兼容性好，老系统必选）
ssh-keygen -t rsa -b 4096 -C "alice@laptop"

# ECDSA（中间选项，比 RSA 快但兼容性不如 RSA）
ssh-keygen -t ecdsa -b 521 -C "alice@laptop"
```

生成的文件：

```bash
~/.ssh/id_ed25519      # 私钥（600 权限）
~/.ssh/id_ed25519.pub  # 公钥（644 权限）
```

`-C` 参数是注释字段，方便辨识这个密钥的用途，不影响密钥本身。

#### 修改/查看已有密钥

```bash
# 查看公钥信息
ssh-keygen -lf ~/.ssh/id_ed25519.pub

# 修改私钥的密码短语
ssh-keygen -p -f ~/.ssh/id_ed25519

# 修改公钥的注释
ssh-keygen -c -C "new-comment" -f ~/.ssh/id_ed25519

# 从私钥中提取公钥
ssh-keygen -y -f ~/.ssh/id_ed25519 > recovered.pub
```

#### 密钥算法的选择建议

| 算法 | 安全性 | 兼容性 | 推荐场景 |
|------|--------|--------|---------|
| Ed25519 | 高 | OpenSSH 6.5+ | 首选，新系统都用它 |
| ECDSA 521 | 高 | OpenSSH 5.7+ | 折中方案 |
| RSA 4096 | 中高（依赖密钥长度） | 几乎所有 SSH 版本 | 老系统兼容 |
| RSA 2048 | 中 | 全覆盖 | 仅限老设备兼容 |

---

### 2.11 安全加固

#### 基础加固 checklist

```bash
# 1. 先测试配置语法
sshd -t

# 2. 编辑配置
vim /etc/ssh/sshd_config
```

```conf
# === 推荐的安全配置 ===

# 不允许 root 用密码登录
PermitRootLogin prohibit-password

# 或者直接禁止 root 登录（先确保有普通用户能 sudo）
# PermitRootLogin no

# 禁用密码登录（先确保已配好密钥且能登录）
PasswordAuthentication no

# 禁用空密码
PermitEmptyPasswords no

# 限制尝试次数
MaxAuthTries 3

# 限制登录用户
AllowUsers alice bob

# 关闭不需要的转发
X11Forwarding no
PermitTunnel no
AllowAgentForwarding no

# 只监听内网接口（如果不需要外网访问）
ListenAddress 192.168.1.10
```

```bash
# 3. 重载配置
systemctl restart sshd
```

#### 修改 SSH 端口

```bash
# 1. 修改 sshd_config
Port 2222

# 2. CentOS/RHEL 需额外处理 SELinux（否则 sshd 无法绑定新端口）
semanage port -a -t ssh_port_t -p tcp 2222

# 3. 防火墙放行新端口
ufw allow 2222/tcp                          # Debian/Ubuntu
firewall-cmd --add-port=2222/tcp --permanent && firewall-cmd --reload  # CentOS/RHEL

# 4. 重启 sshd
systemctl restart sshd

# 5. 用另一终端测试新端口能连上之后，再关掉旧端口
```

SELinux 对 SSH 端口的影响是 CentOS/RHEL 特有的坑：即使改了 `sshd_config` 中的 `Port`，如果 SELinux 策略不认新端口，sshd 启动会失败并报 `Permission denied`。

#### fail2ban 防暴力破解

fail2ban 通过读取 `auth.log` / `secure` 中的失败登录记录，自动封禁超过阈值的 IP。

```bash
# 安装
apt install fail2ban        # Debian/Ubuntu/Kali
dnf install fail2ban        # CentOS/RHEL

# 创建本地配置（覆盖默认值）
vim /etc/fail2ban/jail.local
```

```ini
[sshd]
enabled = true
port = ssh
maxretry = 5            # 5 次失败后封禁
bantime = 3600          # 封禁 1 小时（秒）
findtime = 600          # 统计窗口 10 分钟
ignoreip = 127.0.0.1/8 192.168.1.0/24  # 不封禁的 IP

[sshd]
enabled = true
maxretry = 5
bantime = 3600
findtime = 600
```

```bash
# 启用并启动
systemctl enable fail2ban
systemctl start fail2ban

# 查看封禁状态
fail2ban-client status sshd
```

#### 发行版安全默认配置对比

| 发行版 | 默认安全水平 | 主要风险 |
|--------|------------|---------|
| Ubuntu 24.04 LTS | 较高 | 云镜像可能已禁用密码登录 |
| Debian 12 | 较高 | `PermitRootLogin prohibit-password` 是默认值 |
| CentOS 7 | 较低 | 默认允许 root 密码登录 |
| RHEL 9 | 较高 | 类似 Debian 12，默认禁止 root 密码登录 |
| Kali | 低（故意为之） | root 默认密码登录开放，适合渗透测试但绝不能用于生产 |

---

### 2.12 发行版差异汇总

| 维度 | Debian / Ubuntu | CentOS / RHEL | Kali |
|------|----------------|---------------|------|
| 服务名 | `ssh` | `sshd` | `ssh` |
| 包名 | `openssh-server` | `openssh-server` | `openssh-server`（预装） |
| 主配置 | `/etc/ssh/sshd_config` | `/etc/ssh/sshd_config` | `/etc/ssh/sshd_config` |
| 默认 PermitRootLogin | `prohibit-password` | `yes`（RHEL 7）→ `prohibit-password`（RHEL 9） | `yes` |
| 默认 PasswordAuth | `yes`（云镜像可能 `no`） | `yes` | `yes` |
| SELinux 影响 | 无（用 AppArmor） | 有，改 Port 需 `semanage` | 无 |
| PAM 引用 | `common-*` 系列 | `password-auth` / `system-auth` | 同 Debian |
| sshd_config.d | Ubuntu 22.04+ / Debian 12+ | RHEL 9+ | 同 Debian |
| 系统日志属组 | `adm` 组可读 | 通常需 root/sudo | 同 Debian |

---

## 第三部分：rsyslog 与 SSH 联动

两者的交汇点只有一个文件——`auth.log` 或 `secure`。SSH 输出日志，rsyslog 管理和存储这些日志。

### 3.1 auth.log / secure -- SSH 活动的完整记录

**角色**：记录每一次 SSH 交互——登录成功、登录失败、断开连接、无效用户名、暴力破解尝试。这是排查 SSH 问题的第一入口。

两个服务的衔接机制：

```
sshd (SyslogFacility AUTH + LogLevel INFO)
  → 调用 syslog() 将事件写入 /dev/log
    → rsyslogd 读取
      → 匹配 authpriv.* → /var/log/auth.log 的规则
        → 写入日志文件
```

`sshd_config` 中两个参数直接决定日志怎么写：

```conf
# 决定日志归属哪个 facility（一般不动）
SyslogFacility AUTH

# 决定日志详细程度
LogLevel INFO
```

`LogLevel` 对安全分析的实践影响：

| LogLevel | 能看到什么 | 看不到什么 |
|----------|-----------|-----------|
| `INFO` | 登录成功/失败、用户名、来源 IP、端口 | 具体认证步骤细节 |
| `VERBOSE` | INFO + 指纹信息、密钥交换算法 | 调试信息 |
| `DEBUG` / `DEBUG1-3` | 完整的认证流程每个步骤 | 几乎没有 |

日常运维用 `INFO` 就够了。排查认证问题时临时调到 `VERBOSE`，用完改回来。

### 3.2 典型日志行解读

```bash
# 查看 SSH 日志
grep sshd /var/log/auth.log        # Debian 系
grep sshd /var/log/secure          # RHEL 系

# 只看今天的（如果 rsyslog 做了 daily 轮替）
grep sshd /var/log/auth.log

# 实时监控 SSH 登录活动
tail -f /var/log/auth.log | grep sshd
```

#### 成功登录

```
Jun 21 10:15:22 hostname sshd[12345]: Accepted publickey for root from 192.168.1.100 port 55222 ssh2: RSA SHA256:xxxxxxxxxx
```

字段拆解：

| 字段 | 值 | 含义 |
|------|-----|------|
| `Jun 21 10:15:22` | 时间戳 | 事件发生时间 |
| `hostname` | 主机名 | 哪台机器 |
| `sshd[12345]` | 进程名[PID] | sshd 进程 PID 12345 |
| `Accepted publickey` | 事件 | 公钥认证成功 |
| `for root` | 目标用户 | root 用户登录 |
| `from 192.168.1.100` | 来源 IP | 谁在连接 |
| `port 55222` | 来源端口 | 对方使用的临时端口 |
| `ssh2` | 协议版本 | SSH 协议版本 2 |

#### 密码登录成功

```
Jun 21 10:15:30 hostname sshd[12346]: Accepted password for alice from 192.168.1.100 port 55223 ssh2
```

#### 登录失败

```
Jun 21 10:15:35 hostname sshd[12347]: Failed password for root from 203.0.113.50 port 33445 ssh2
Jun 21 10:15:36 hostname sshd[12348]: Failed password for invalid user admin from 203.0.113.50 port 33446 ssh2
```

`invalid user` 表示这个用户名在系统中不存在——典型的字典攻击特征：攻击者在枚举用户名。

#### 断开连接

```
Jun 21 10:15:40 hostname sshd[12347]: Connection closed by authenticating user root 192.168.1.100 port 55222 [preauth]
```

`[preauth]` 表示连接在认证完成前就断开了（超时、达到最大尝试次数、或被主动断开）。

### 3.3 从日志到安全响应

#### 提取暴力破解来源 IP

```bash
# Debian/Ubuntu/Kali
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -10

# CentOS/RHEL
grep "Failed password" /var/log/secure | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -10
```

输出示例：

```
    156 203.0.113.50
     42 198.51.100.22
     18 192.0.2.10
```

#### 提取无效用户名尝试

```bash
grep "invalid user" /var/log/auth.log | awk '{print $(NF-6)}' | sort | uniq -c | sort -rn | head -10
```

能看到攻击者在尝试哪些用户名：`root`、`admin`、`test`、`oracle`、`pi` 等高频目标。

#### 统计成功登录

```bash
# 今天所有成功登录的用户和来源
grep "Accepted" /var/log/auth.log | awk '{print $6, $(NF-3)}' | sort | uniq -c
```

#### 远程日志集中收集

把 SSH 日志发到远程日志服务器，防止本地日志被攻击者清除：

```bash
# /etc/rsyslog.d/30-remote-ssh.conf
# 只把 auth 相关的日志远程发送
auth.* @@192.168.1.200:514

# 同时保留本地副本（rsyslog 默认行为就是多 destination，不需要特殊配置）
```

auth.log / secure 是攻击者入侵后第一想要清除的文件。远程 rsyslog 服务器上有一份独立副本，即使本地日志被全部清除，远端仍然保留了完整的入侵痕迹。

---

## 第四部分：安全排查视角

### 4.1 日志清除 vs 检测

攻击者获得 root 权限后，常见操作：

```bash
# 清除所有日志（简单粗暴，但很容易被发现）
rm -rf /var/log/*

# 精确清除（只删除 SSH 登录痕迹，更隐蔽）
> /var/log/auth.log          # 清空文件但不删除
>/var/log/syslog
sed -i '/sshd/d' /var/log/auth.log   # 只删除含 sshd 的行

# 清除 history
history -c                   # 清空当前会话 history
> ~/.bash_history            # 清空 history 文件
unset HISTFILE               # 让当前 shell 不再记录 history
```

检测思路：

```bash
# 1. 如果配置了远程 rsyslog，本地清除无效
grep sshd /var/log/remote/*/auth.log    # 远端的副本

# 2. 检查日志文件是否存在（rm 后文件都没了）
ls -la /var/log/auth.log

# 3. 检查日志文件的修改时间（清空后 mtime 变成当前时间，和附近文件不一致）
ls -lt /var/log/ | head

# 4. 用 auditd 监控日志文件的写入和删除
auditctl -w /var/log/auth.log -p wa -k log_tamper

# 5. 如果一个应该在运行的进程没有在写日志，被强制清空了
lsof /var/log/auth.log 2>/dev/null
# 如果 rsyslogd 打开着这个文件但文件大小为 0 且最近无写入，可能被 > 清空
```

### 4.2 SSH 后门检测

#### 检查 authorized_keys 中是否有多余条目

```bash
# 查看 root 的授权密钥
cat /root/.ssh/authorized_keys

# 查看所有用户的 authorized_keys
for user_home in /home/* /root; do
    user=$(basename "$user_home")
    if [ -f "$user_home/.ssh/authorized_keys" ]; then
        echo "=== $user ==="
        cat "$user_home/.ssh/authorized_keys"
    fi
done

# 检查 authorized_keys 的修改时间
find /home/ /root/ -name authorized_keys -ls
```

重点关注：不认识的新密钥、异常修改时间、不应该有 authorized_keys 的用户（如 `www-data`、`nobody`）。

#### 检查 sshd 二进制是否被替换

```bash
# Debian/Ubuntu/Kali
debsums openssh-server
# 或用 md5sum 对比
md5sum /usr/sbin/sshd

# CentOS/RHEL
rpm -V openssh-server
# 输出为空 = 文件未被篡改
# S.5....T. /usr/sbin/sshd 表示大小和修改时间变了（严重可疑）
```

#### 检查非标准端口上的 SSH 进程

```bash
# 列出所有监听中的 TCP 端口
ss -tlnp

# 重点看有没有 sshd 监听在非 22 端口上
ss -tlnp | grep sshd

# 或者找所有类似 SSH 端口的监听
ss -tlnp | grep -E ":[0-9]+" | grep -v ":22 "
```

攻击者可能在 2222、8022、22222 等端口上运行了第二个 sshd 实例，用 `-f` 指定了不同的配置文件和 authorized_keys 路径。

#### 检查 PAM 是否被篡改

```bash
# PAM 模块中可能插入后门（如 pam_unix.so 被替换）
rpm -V pam            # RHEL
debsums libpam-modules   # Debian

# 检查是否有异常 PAM 模块加载
cat /etc/pam.d/sshd
```

### 4.3 持久化检查点

结合 SSH 和 rsyslog 的常见持久化路径：

```bash
# SSH 后门的几种常见实现方式
# 1. 添加 authorized_keys
# 2. 替换 sshd 二进制
# 3. 替换 PAM 模块
# 4. 新增 systemd service 启动第二个 sshd
# 5. 通过 crontab @reboot 启动反向 shell
# 6. 修改 /etc/rc.local 启动反向 shell
```

```bash
# 全面检查脚本
echo "=== authorized_keys ==="
find / -name authorized_keys -ls 2>/dev/null

echo "=== sshd 二进制检查 ==="
which sshd && md5sum $(which sshd)

echo "=== 监听中的 SSH 进程 ==="
ss -tlnp | grep -i ssh

echo "=== 异常 systemd SSH 服务 ==="
systemctl list-units --type=service | grep -i ssh

echo "=== 最近的日志清除迹象 ==="
ls -lt /var/log/auth.log /var/log/secure /var/log/syslog /var/log/messages 2>/dev/null

echo "=== crontab 中的 @reboot ==="
for user in $(cut -d: -f1 /etc/passwd); do
    crontab -u "$user" -l 2>/dev/null | grep -i reboot
done
```

---

## 快速参考

### rsyslog 速查

```bash
systemctl status rsyslog
tail -f /var/log/syslog            # Debian
tail -f /var/log/messages          # RHEL
grep "error" /var/log/syslog
cat /etc/rsyslog.conf
ls /etc/rsyslog.d/
```

### SSH 速查

```bash
systemctl status sshd              # RHEL
systemctl status ssh               # Debian
sshd -t && systemctl restart sshd  # 检查配置后重启
grep sshd /var/log/auth.log        # Debian: 看登录记录
grep sshd /var/log/secure          # RHEL: 看登录记录
ss -tlnp | grep :22                # 确认 SSH 在监听
```

### 日志文件速查

```bash
# Debian/Ubuntu/Kali
tail -f /var/log/auth.log          # SSH 登录日志
tail -f /var/log/syslog            # 系统日志

# CentOS/RHEL
tail -f /var/log/secure            # SSH 登录日志
tail -f /var/log/messages          # 系统日志
```

---

## 参考

- [SELinux 详解](SELinux.md) — SELinux 与 SSH/rsyslog 的交互
- [权限管理](权限管理.md) — 文件权限、chattr、ACL 完整文档
- [rsyslog 官方文档](https://www.rsyslog.com/doc/)
- [OpenSSH 手册](https://www.openssh.com/manual.html)
- [sshd_config(5) man page](https://man.openbsd.org/sshd_config)
- [sshd(8) man page](https://man.openbsd.org/sshd)
- [rsyslog.conf(5) man page](https://man.openbsd.org/rsyslog.conf)
- [logrotate(8) man page](https://linux.die.net/man/8/logrotate)
- [PAM 系统管理员指南](http://www.linux-pam.org/Linux-PAM-html/)
- [fail2ban 文档](https://www.fail2ban.org/wiki/index.php/Main_Page)
