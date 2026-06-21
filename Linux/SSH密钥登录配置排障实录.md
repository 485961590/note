# SSH 密钥登录配置排障实录

> 一次 SSH 密钥认证的完整配置过程，记录从生成密钥到最终连通的每一步操作，着重分析中间遇到的 SELinux 权限问题。

---

## 环境说明

| 角色 | 系统 | IP | 用户 |
|------|------|-----|------|
| 客户端 | CentOS 7 (OpenSSH 7.4) | 192.168.230.138 | user |
| 服务器 | CentOS / RHEL 系列 (OpenSSH 9.9) | 192.168.230.139 | root |

服务器已禁用密码登录（`PasswordAuthentication no`），只允许密钥认证。

---

## 第一部分：配置过程

### 1.1 本地生成密钥对

在客户端执行：

```bash
ssh-keygen -t rsa -b 4096
# 一路回车，使用默认路径 ~/.ssh/id_rsa
```

生成的文件：

```bash
ls -la ~/.ssh/
# -rw-------. 1 user user 1675 Jun 21 11:17 id_rsa        # 私钥
# -rw-r--r--. 1 user user  408 Jun 21 11:17 id_rsa.pub    # 公钥
```

### 1.2 尝试连接 -- 失败

```bash
ssh root@192.168.230.139 -p 22
# Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

服务器只允许 `publickey`、`gssapi-keyex`、`gssapi-with-mic` 三种认证方式，不接受密码。

### 1.3 通过控制台登录服务器，部署公钥

由于 SSH 连不上，通过 VNC/控制台直接登录服务器（root 用户）。

服务器上已经有一份公钥文件（之前通过某种方式传上来的）：

```bash
[root@localhost ~]# ls
anaconda-ks.cfg  id_rsa.pub  security-header-checker
```

将公钥移动到 ssh 目录并改名为 authorized_keys：

```bash
mv ./id_rsa.pub ~/.ssh/authorized_keys
```

设置权限：

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

验证权限：

```bash
ls -la ~/.ssh/
# drwx------. 2 root root   71 Jun 20 13:48 .
# -rw-------. 1 root root  408 Jun 20 13:45 authorized_keys
```

### 1.4 检查 sshd_config 配置

```bash
cat /etc/ssh/sshd_config | grep -E "PubkeyAuthentication|AuthorizedKeysFile|PasswordAuthentication"
```

确认三项配置：

```
PubkeyAuthentication yes
AuthorizedKeysFile /root/.ssh/authorized_keys
PasswordAuthentication no
```

### 1.5 备份并重启 sshd

```bash
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
systemctl restart sshd
```

### 1.6 再次尝试连接 -- 仍然失败

```bash
ssh root@192.168.230.139 -p 22
# Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

配置和权限看起来都正确，但就是连不上。

---

## 第二部分：排查过程

### 2.1 客户端调试日志

用 `-v` 参数查看详细连接过程：

```bash
ssh -v root@192.168.230.139 -p 22
```

关键输出：

```
debug1: Offering RSA public key: /home/user/.ssh/id_rsa
debug1: Authentications that can continue: publickey,gssapi-keyex,gssapi-with-mic
```

客户端发送了公钥，但服务器拒绝了。问题在服务器端。

### 2.2 服务器端日志

查看 sshd 服务日志：

```bash
systemctl status sshd
```

发现关键错误：

```
sshd-session[1027784]: Could not open user 'root' authorized keys '/root/.ssh/authorized_keys': Permission denied
```

**sshd 无法读取 authorized_keys 文件。**

### 2.3 定位真正原因

文件权限已经正确（600），属主是 root，目录权限也正确（700）。为什么 sshd 还是不能读？

答案：SELinux。

执行 `restorecon` 之前的文件标签：

```bash
# 在服务器上执行 restorecon 之前的状态
# /root/.ssh/authorized_keys 的 SELinux 上下文是：
# unconfined_u:object_r:admin_home_t:s0
```

`admin_home_t` 是管理员家目录的默认标签，但 SSH 服务（进程标签为 `sshd_t`）的 SELinux 策略不允许读取 `admin_home_t` 标签的文件。SSH 服务只能读取 `ssh_home_t` 标签的文件。

### 2.4 为什么 mv 导致了标签错误

```bash
mv ./id_rsa.pub ~/.ssh/authorized_keys
```

`mv` 命令会**保留文件的原始 SELinux 标签**。

- `id_rsa.pub` 在 `/root/` 目录下时，标签是 `admin_home_t`
- `mv` 到 `/root/.ssh/` 后，标签仍然是 `admin_home_t`
- 而 `/root/.ssh/authorized_keys` 的正确标签应该是 `ssh_home_t`

如果是 `ssh-copy-id` 或手动 `echo >>` 创建 authorized_keys，新文件会自动继承所在目录的 SELinux 上下文，就不会有这个问题。

---

## 第三部分：修复

### 3.1 修正 SELinux 标签

```bash
restorecon -R -v /root/.ssh
systemctl restart sshd
```

输出：

```
Relabeled /root/.ssh/authorized_keys from unconfined_u:object_r:admin_home_t:s0 to unconfined_u:object_r:ssh_home_t:s0
```

`restorecon` 根据 SELinux 默认策略，将文件标签从 `admin_home_t` 修正为 `ssh_home_t`。

### 3.2 验证连接

在客户端执行：

```bash
ssh root@192.168.230.139 -p 22
```

预期直接登录成功，不再需要密码。

---

## 第四部分：问题分析

### 4.1 完整的失败链条

```
本地生成密钥对 (id_rsa + id_rsa.pub)
    ↓
公钥通过某种方式传到服务器 /root/ 目录（标签为 admin_home_t）
    ↓
mv 将公钥移到 /root/.ssh/authorized_keys（标签保持 admin_home_t）
    ↓
chmod 600 设置传统权限（正确，但不够）
    ↓
sshd_config 配置正确（PubkeyAuthentication yes, 路径正确）
    ↓
客户端发起 SSH 连接，发送公钥
    ↓
sshd 进程（标签 sshd_t）尝试读取 /root/.ssh/authorized_keys
    ↓
SELinux 强制访问控制检查：sshd_t 能否读取 admin_home_t 的文件？
    ↓
SELinux 策略：不允许
    ↓
sshd 返回 "Permission denied" 给客户端
    ↓
客户端看到：Permission denied (publickey)
```

### 4.2 两层权限模型

| 层次 | 名称 | 检查内容 | 本案例 |
|------|------|----------|--------|
| DAC | 自主访问控制 | 传统的 rwx 权限、属主属组 | 600/root/root -- 正确 |
| MAC | 强制访问控制 | SELinux 上下文标签 | admin_home_t -- 错误 |

DAC 检查通过后，MAC 还会再检查一次。两层都通过，进程才能访问文件。

### 4.3 关键命令对照

| 命令 | 作用 |
|------|------|
| `ls -Z` | 查看文件的 SELinux 上下文 |
| `ps -Z` | 查看进程的 SELinux 上下文 |
| `restorecon -R -v <path>` | 根据默认策略恢复正确的 SELinux 标签 |
| `chcon -t <type> <file>` | 手动设置 SELinux 类型标签 |
| `getenforce` | 查看 SELinux 当前模式（Enforcing / Permissive / Disabled） |
| `setenforce 0` | 临时切换到 Permissive 模式（不阻止，只记录） |
| `grep sshd /var/log/audit/audit.log` | 查看 SELinux 审计日志 |

### 4.4 类似场景

同样的 SELinux 标签问题也会发生在：

| 服务 | 需要的文件标签 |
|------|---------------|
| SSH (sshd_t) | `ssh_home_t` |
| Nginx/Apache (httpd_t) | `httpd_sys_content_t` |
| FTP (ftpd_t) | `public_content_t` |
| MySQL (mysqld_t) | `mysqld_db_t` |

规律：每个服务进程有自己的 SELinux 域（`_t` 后缀），文件必须有匹配的标签才能被该服务访问。

---

## 第五部分：总结

### 问题根因

**一句话：`mv` 保留了文件的原始 SELinux 标签（`admin_home_t`），导致 sshd 无法读取 authorized_keys，因为 SELinux 策略要求该文件标签为 `ssh_home_t`。**

### 避免方法

1. **用 `ssh-copy-id` 分发公钥** -- 自动处理权限和 SELinux 上下文，不存在此问题
2. **用 `echo >>` 创建 authorized_keys** -- 新文件自动继承目录的正确 SELinux 标签
3. **用 `cp` 而不是 `mv`** -- `cp` 创建新文件，自动继承目标目录的 SELinux 上下文；`mv` 保留原标签
4. **分发公钥后执行 `restorecon`** -- 保险起见，`restorecon -R -v ~/.ssh` 确保标签正确

### 排查思路

SSH 密钥登录失败时，按以下顺序检查：

1. 客户端：`ssh -v` 看公钥是否被发送
2. 服务器：`systemctl status sshd` 或 `journalctl -u sshd` 看具体错误
3. 传统权限：`ls -la ~/.ssh/` 确认目录 700、authorized_keys 600
4. SELinux：`ls -Z ~/.ssh/authorized_keys` 确认标签是 `ssh_home_t`
5. SELinux 审计日志：`grep sshd /var/log/audit/audit.log`

---

## 参考

- [SELinux 详解](SELinux.md) -- 本文档中遇到的核心问题，独立成篇
- [rsyslog 与 SSH 服务](rsyslog与SSH服务.md) -- SSH 和 rsyslog 的文件级拆解
- [SELinux User's and Administrator's Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/selinux_users_and_administrators_guide/)
- [sshd_config(5) man page](https://man.openbsd.org/sshd_config)
- [restorecon(8) man page](https://linux.die.net/man/8/restorecon)
