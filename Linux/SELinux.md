# SELinux

> SELinux 不是防火墙，也不是杀毒软件。它是一个**强制访问控制系统**——在 Linux 原生的 rwx 权限之上，再加一层规则：即使 root 拥有的文件，SELinux 说不能读就是不能读。

---

## 1. 为什么需要 SELinux

### 1.1 传统权限的局限

Linux 原生的 DAC（Discretionary Access Control，自主访问控制）有致命弱点：

```bash
# root 启动的 nginx 进程被攻破
# 攻击者以 nginx 用户身份拿到了 shell
# nginx 用户能读什么，攻击者就能读什么
cat /etc/shadow          # 不能读（权限正确）
cat /var/www/html/*      # 能读（因为 nginx 需要访问网站文件）
cat /tmp/secret.key      # 也能读！——如果管理员不小心把敏感文件设成了 644
```

DAC 的问题是：**进程的权限等于启动它的用户的权限**。一旦进程被攻破，攻击者就能访问该用户能访问的所有文件。

### 1.2 SELinux 的做法

SELinux 给**每个进程**和**每个文件**打上安全标签（security context），然后定义规则：哪个标签的进程能访问哪个标签的文件。

```
进程 nginx (httpd_t) → 能否读文件 index.html (httpd_sys_content_t) → 允许
进程 nginx (httpd_t) → 能否读文件 /etc/shadow (shadow_t) → 拒绝
进程 nginx (httpd_t) → 能否读文件 /tmp/secret.key (user_home_t) → 拒绝
```

即使 nginx 进程被完全攻破，攻击者也只能访问 `httpd_sys_content_t` 标签的文件，碰不到其他任何东西。

---

## 2. 核心概念

### 2.1 DAC 与 MAC 对比

| | DAC (自主访问控制) | MAC (强制访问控制) |
|---|---|---|
| **谁决定** | 文件所有者 | 系统管理员（策略） |
| **判断依据** | rwx 权限位、属主属组 | 安全上下文标签 |
| **能否被用户绕过** | root 可以 | 连 root 也受限制 |
| **粒度** | 读/写/执行 | 读/写/执行/追加/链接/重命名/挂载/信号/... |
| **Linux 实现** | chmod, chown | SELinux, AppArmor |

### 2.2 安全上下文（Security Context）

每个文件和进程都有一个标签，格式固定：

```
用户:角色:类型:灵敏度
user :role :type :level
```

示例：

```
system_u:object_r:ssh_home_t:s0        # 一个授权密钥文件
unconfined_u:object_r:admin_home_t:s0  # 管理员家目录下的文件
system_u:system_r:sshd_t:s0-s0:c0.c1023 # SSH 守护进程
```

四个字段中，**类型（type）**是实际起作用的部分。日常排障 99% 的问题是类型不对。

| 字段 | 含义 | 实际作用 |
|------|------|---------|
| user | SELinux 用户 | 很少关注，通常都是 `system_u` 或 `unconfined_u` |
| role | 角色 | 很少关注，文件是 `object_r`，进程是 `system_r` |
| type | 类型 -- **核心** | 决定什么进程能访问什么文件 |
| level | MLS/MCS 安全等级 | 政府和军事环境才用，日常为 `s0` |

### 2.3 Type Enforcement（类型强制）-- SELinux 的核心机制

SELinux 的核心规则极其简单：

```
规则：允许域（domain）对类型（type）执行某类操作
规则：源类型（进程的 type）→ 目标类型（文件的 type）: 权限
```

示例（简化的实际规则）：

```
sshd_t → ssh_home_t : read    # sshd 可以读 ssh_home_t 标签的文件
sshd_t → admin_home_t : ???   # 没有规则 = 拒绝
httpd_t → httpd_sys_content_t : read   # nginx 可以读网站文件
httpd_t → shadow_t : ???              # 没有规则 = 拒绝
```

**SELinux 是白名单机制：不在规则里的操作一律拒绝。**

---

## 3. 工作模式

SELinux 有三种模式：

| 模式 | 行为 | 使用场景 |
|------|------|---------|
| Enforcing | 强制 -- 拒绝违规操作并记录日志 | 生产环境 |
| Permissive | 宽容 -- 允许违规操作但记录日志 | 排障、生成策略 |
| Disabled | 关闭 | 不推荐，等同于裸奔 |

### 3.1 查看当前模式

```bash
getenforce
# 输出：Enforcing / Permissive / Disabled
```

### 3.2 临时切换模式

```bash
# 临时切换到 Permissive（重启后恢复 Enforcing）
setenforce 0       # Permissive
setenforce 1       # Enforcing
```

注意：Disabled 和 Permissive 之间不能直接用 `setenforce` 切换。从 Disabled 到 Enforcing 需要修改配置文件并**重启系统**。

### 3.3 永久修改模式

```bash
vim /etc/selinux/config
```

```
SELINUX=enforcing     # 强制
SELINUX=permissive    # 宽容
SELINUX=disabled      # 关闭
```

---

## 4. 常用命令

### 4.1 查看标签

```bash
# 查看文件的 SELinux 上下文
ls -Z /var/www/html/index.html
# -rw-r--r--. root root system_u:object_r:httpd_sys_content_t:s0 index.html

# 查看目录及其内容的上下文
ls -Z /root/.ssh/

# 查看进程的 SELinux 上下文
ps -eZ | grep sshd
# system_u:system_r:sshd_t:s0-s0:c0.c1023 843 ? 00:00:00 sshd

# 查看当前用户的上下文
id -Z
```

### 4.2 修改标签

```bash
# 根据默认策略恢复正确标签（最常用）
restorecon -R -v /root/.ssh
# -R  递归
# -v  显示变化

# 手动设置类型标签
chcon -t ssh_home_t /root/.ssh/authorized_keys

# 带参考文件设置标签（让目标文件和参考文件标签相同）
chcon --reference=/root/.ssh/known_hosts /root/.ssh/authorized_keys

# 永久修改默认标签（恢复策略的一部分）
semanage fcontext -a -t httpd_sys_content_t "/web(/.*)?"
restorecon -R -v /web
```

`chcon` 直接改标签，但下次 `restorecon` 会覆盖它。**`semanage fcontext` 配合 `restorecon` 才是永久方案。**

### 4.3 管理端口

SELinux 不止管文件，还管进程能绑定哪些端口：

```bash
# 查看 sshd_t 域允许绑定哪些端口
semanage port -l | grep ssh
# ssh_port_t   tcp   22

# 允许 sshd 绑定非标准端口 2222
semanage port -a -t ssh_port_t -p tcp 2222

# 删除端口授权
semanage port -d -t ssh_port_t -p tcp 2222
```

如果改了 `sshd_config` 中的 `Port` 但没用 `semanage` 授权新端口，sshd 启动会失败。

### 4.4 管理布尔值

布尔值是 SELinux 预设的开关，用于快速启停某类行为：

```bash
# 列出所有布尔值
getsebool -a

# 列出 SSH 相关的布尔值
getsebool -a | grep ssh

# 允许 sshd 使用家目录（如果用户家目录在非标准位置）
setsebool -P use_nfs_home_dirs on
# -P 表示永久生效，不加 -P 则重启后恢复
```

常用布尔值的详细说明见 [[SELinux布尔值参考]]。

---

## 5. 排障方法

### 5.1 排障流程

```
服务出问题了
  ↓
1. 传统权限对不对？（ls -la）
  ↓ 对
2. 是不是 SELinux 在搞鬼？
  ↓
3. sudo setenforce 0（临时切 Permissive）
  ↓
4. 重试操作 -- 成功了？→ 确认是 SELinux 问题
  ↓
5. sudo setenforce 1（切回 Enforcing）
  ↓
6. 查审计日志定位具体规则：grep <服务名> /var/log/audit/audit.log
  ↓
7. 用 restorecon 或 audit2allow 修复
```

### 5.2 查看 SELinux 审计日志

SELinux 的拒绝记录写入 `/var/log/audit/audit.log`：

```bash
# 查看最近的拒绝记录
grep denied /var/log/audit/audit.log | tail -20

# 查看 SSH 相关的拒绝
grep sshd /var/log/audit/audit.log | grep denied

# 用 sealert 工具分析（更友好的输出）
sealert -a /var/log/audit/audit.log
```

一条典型的拒绝记录：

```
type=AVC msg=audit(1624236000.123:456): avc:  denied  { read } for  pid=12345
comm="sshd" name="authorized_keys" dev="sda1" ino=789012
scontext=system_u:system_r:sshd_t:s0-s0:c0.c1023
tcontext=unconfined_u:object_r:admin_home_t:s0
tclass=file
```

关键字段解读：

| 字段 | 值 | 含义 |
|------|-----|------|
| `denied { read }` | 拒绝了读取操作 | sshd 想读文件 |
| `comm="sshd"` | 进程名 sshd | 谁发起的 |
| `name="authorized_keys"` | 文件名 | 目标文件 |
| `scontext` | `sshd_t` | 进程的 SELinux 标签 |
| `tcontext` | `admin_home_t` | 文件的 SELinux 标签 |
| `tclass=file` | 普通文件 | 目标对象类型 |

翻译成人话：进程 sshd（标签 `sshd_t`）想**读取**文件 authorized_keys（标签 `admin_home_t`），SELinux 策略里没有 `sshd_t → admin_home_t : read` 这条规则，所以拒绝。

### 5.3 从审计日志自动生成策略

```bash
# 安装 audit2allow
yum install policycoreutils-python     # RHEL 7
dnf install policycoreutils-python-utils  # RHEL 8+

# 分析拒绝记录并生成可读说明
grep sshd /var/log/audit/audit.log | audit2why

# 生成允许规则（用于临时测试）
grep sshd /var/log/audit/audit.log | audit2allow -M my-sshd-fix
# 生成 my-sshd-fix.pp 策略模块

# 加载生成的策略模块
semodule -i my-sshd-fix.pp
```

---

## 6. 常见服务与文件标签对照

### 6.1 服务进程标签

| 服务 | 进程标签 | 说明 |
|------|---------|------|
| SSH | `sshd_t` | SSH 守护进程 |
| HTTP (Nginx/Apache) | `httpd_t` | Web 服务器 |
| MySQL/MariaDB | `mysqld_t` | 数据库 |
| FTP (vsftpd) | `ftpd_t` | FTP 服务 |
| Samba | `smbd_t` | 文件共享 |
| DNS (named) | `named_t` | 域名解析 |
| DHCP | `dhcpd_t` | IP 分配 |
| rsyslog | `syslogd_t` | 日志服务 |

### 6.2 文件和目录标签

| 路径 | 标签 | 谁可以访问 |
|------|------|-----------|
| `~/.ssh/authorized_keys` | `ssh_home_t` | `sshd_t` |
| `~/.ssh/id_rsa` | `ssh_home_t` | 用户自己的进程 |
| `/var/www/html/*` | `httpd_sys_content_t` | `httpd_t`（只读） |
| `/var/www/uploads/*` | `httpd_sys_rw_content_t` | `httpd_t`（可读写） |
| `/var/lib/mysql/*` | `mysqld_db_t` | `mysqld_t` |
| `/var/log/secure` | `var_log_t` | `syslogd_t` |
| `/var/ftp/*` | `public_content_t` | `ftpd_t` |
| `/root/*` | `admin_home_t` | root 用户自己的进程 |
| `/home/*` | `user_home_t` | 对应用户的进程 |

---

## 7. SSH 密钥认证失败的 SELinux 原因

### 7.1 典型场景

在 SSH 密钥配置中最容易踩的 SELinux 坑：

```bash
# 本地生成公钥，scp 到服务器的 /root/
scp ~/.ssh/id_rsa.pub root@server:/root/

# 在服务器上 mv 到 .ssh 目录
mv /root/id_rsa.pub /root/.ssh/authorized_keys

# chmod 600 -- DAC 权限正确
chmod 600 /root/.ssh/authorized_keys

# 但是连不上！
ssh root@server
# Permission denied (publickey)
```

### 7.2 根因

文件从 `/root/`（`admin_home_t`）移动到 `/root/.ssh/`（应该继承 `ssh_home_t`），但 `mv` **保留了原始标签**：

```
mv 前：id_rsa.pub          → admin_home_t（在 /root/ 目录下，正常）
mv 后：authorized_keys      → admin_home_t（到了 /root/.ssh/ 下，错误！应该是 ssh_home_t）
```

而 SELinux 策略里没有 `sshd_t → admin_home_t : read` 这条规则，所以 sshd 无法读取。

### 7.3 为什么其他操作方式没问题

| 操作 | 标签行为 | 结果 |
|------|---------|------|
| `mv /root/pub /root/.ssh/auth_keys` | 保留 `admin_home_t` | 错误 |
| `cp /root/pub /root/.ssh/auth_keys` | 新文件继承目录标签 `ssh_home_t` | 正确 |
| `echo "..." >> /root/.ssh/auth_keys` | 新文件（或追加），标签不变 / 自动继承 | 正确 |
| `ssh-copy-id root@server` | ssh-copy-id 内部用 `echo >>`，自动继承 | 正确 |
| `scp 直接写到 /root/.ssh/` | 新文件继承目标目录标签 | 正确 |

### 7.4 修复

```bash
# 方法一：恢复默认标签（推荐）
restorecon -R -v /root/.ssh

# 方法二：手动设置
chcon -t ssh_home_t /root/.ssh/authorized_keys

# 方法三：验证是否是 SELinux 问题（临时）
setenforce 0  # 临时关闭 SELinux
ssh root@server  # 如果能连上，确认是 SELinux 问题
setenforce 1  # 恢复 Enforcing
restorecon -R -v /root/.ssh  # 修复
```

---

## 8. SELinux vs AppArmor

CentOS/RHEL 用 SELinux，Debian/Ubuntu 用 AppArmor。两者都是 MAC 实现，但风格不同：

| 维度 | SELinux | AppArmor |
|------|---------|----------|
| 策略绑定对象 | **文件标签**（inode 级别的扩展属性） | **文件路径** |
| 策略粒度 | 极细（数十种操作类型） | 较粗（读/写/执行等基本操作） |
| 管理复杂度 | 高 | 低 |
| 命令行工具 | `ls -Z`, `chcon`, `restorecon`, `semanage` | `aa-status`, `aa-enforce`, `aa-complain` |
| 默认策略覆盖 | 几乎每个服务都有策略 | 只覆盖常见的服务 |
| 维护者 | NSA / Red Hat | Canonical (Ubuntu) |
| 使用发行版 | CentOS, RHEL, Fedora | Debian, Ubuntu, Kali, openSUSE |

日常差异最大的地方：在 Debian/Ubuntu 上用 `mv` 移 authorized_keys 不会出问题，因为 AppArmor 看的是文件路径而不是文件的扩展属性标签。

---

## 9. 什么时候可以关闭 SELinux

不建议关闭，但有少数场景确实需要关：

**可以关的情况：**
- 内网隔离的测试环境
- 容器（docker/containerd）-- 容器本身提供了隔离
- 某些商业软件的安装文档明确要求关闭（这种软件本身就不安全）
- 排障期间的临时操作（`setenforce 0`，用完改回来）

**绝不能关的情况：**
- 暴露在公网的服务器
- 多用户共享的服务器
- 运行 Web 服务、数据库、邮件服务的生产环境
- 任何需要合规（等保、PCI-DSS）的环境

---

## 10. 快速参考

```bash
# 查看状态
getenforce                          # 当前模式
sestatus                            # 详细状态

# 查看标签
ls -Z <file>                        # 文件标签
ps -eZ                              # 进程标签
id -Z                               # 当前用户标签

# 修改标签
restorecon -R -v <path>             # 恢复默认标签
chcon -t <type> <file>              # 手动改标签
semanage fcontext -a -t <type> "<regex>"  # 永久修改默认标签

# 端口管理
semanage port -l                    # 列出所有端口标签
semanage port -a -t <type> -p tcp <port>  # 添加端口授权

# 布尔值
getsebool -a                        # 列出所有布尔值
setsebool -P <name> on|off          # 设置布尔值（-P 永久）

# 排障
grep denied /var/log/audit/audit.log | tail -20   # 看拒绝记录
grep <service> /var/log/audit/audit.log | audit2why  # 分析原因

# 模式切换
setenforce 0                        # 临时 Permissive（排障用）
setenforce 1                        # 恢复 Enforcing

# 彻底关闭（不推荐）
vim /etc/selinux/config             # SELINUX=disabled → 需要重启
```

---

## 参考

- [权限管理](权限管理.md) — DAC + MAC 权限管理总览
- [SSH 密钥登录配置排障实录](SSH密钥登录配置排障实录.md) — SELinux 导致 SSH 登录失败的完整排障案例
- [SELinux User's and Administrator's Guide (Red Hat)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/selinux_users_and_administrators_guide/)
- [SELinux Project Wiki](https://selinuxproject.org/)
- [The SELinux Notebook](https://github.com/SELinuxProject/selinux-notebook)
- [Gentoo SELinux Handbook](https://wiki.gentoo.org/wiki/SELinux/Handbook)
- [sshd_config(5)](https://man.openbsd.org/sshd_config)
