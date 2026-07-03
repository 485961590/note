# SELinux 布尔值参考

> `getsebool -a` 输出的完整布尔值说明。布尔值是 SELinux 预设的策略开关，用 `setsebool -P <name> on|off` 控制。本文以 `httpd_*` 系列为重点（Apache/mod_wsgi 排障中最常遇到），也覆盖其他常见服务的布尔值。

---

## 1. 基础概念

每个布尔值对应 SELinux 策略中的一组 `allow` 规则。设为 `on` 即启用这组规则，`off` 即禁用。

```bash
getsebool -a                        # 列出全部布尔值
getsebool -a | grep httpd           # 过滤 httpd 相关
getsebool httpd_unified             # 查看单个值
setsebool -P httpd_unified 1        # 永久开启（-P 写入策略，重启不丢失）
setsebool httpd_unified 1           # 临时开启（重启后恢复默认）
semanage boolean -l                 # 查看所有布尔值的描述
```

---

## 2. httpd_* 系列布尔值

> 本次 [[Apache-mod_wsgi-SELinux排障]] 的核心问题域。按类别分组。

### 2.1 网络连接

| 布尔值 | 默认 | 说明 | 何时开启 |
|--------|------|------|---------|
| `httpd_can_network_connect` | off | 允许 Apache 向外发起 TCP 连接 | Flask/Django 应用使用 `requests` 库请求外部 URL；Apache 作反向代理 |
| `httpd_can_network_connect_db` | off | 允许 Apache 连接数据库端口 | 应用直连 MySQL(3306)、PostgreSQL(5432) 等 |
| `httpd_can_network_relay` | off | 允许 Apache 转发网络流量 | Apache 作为正向代理 |
| `httpd_can_network_memcache` | off | 允许 Apache 连接 Memcached | 应用使用 Memcached 缓存 |
| `httpd_can_connect_ftp` | off | 允许 Apache 连接 FTP 服务 | 应用通过 FTP 获取文件 |
| `httpd_can_connect_ldap` | off | 允许 Apache 连接 LDAP 服务 | LDAP 认证 |
| `httpd_can_connect_zabbix` | off | 允许 Apache 连接 Zabbix 监控 | Zabbix Web 前端 |
| `httpd_can_connect_mythtv` | off | 允许 Apache 连接 MythTV | MythTV 媒体中心前端 |
| `httpd_verify_dns` | off | 允许 Apache 验证 DNS 反向解析 | HostnameLookups 开启时需要 |

### 2.2 脚本执行与内存权限 -- 排障核心

> 这组布尔值与 mod_wsgi / Python C 扩展加载直接相关。

| 布尔值 | 默认 | 说明 | 何时开启 |
|--------|------|------|---------|
| `httpd_unified` | off | **统一 httpd 策略**。合并 httpd_t 和 httpd_sys_script_t 的权限，允许 execmem/execmod 等操作 | mod_wsgi 加载 Python C 扩展 .so 文件；综合权限需求。**这是本次排障的最关键布尔值** |
| `httpd_execmem` | off | 允许 Apache 进程申请可执行内存（execmem） | JIT 编译、某些 C 扩展的内存执行需求。注意：**单独开启不足以解决 mod_wsgi .so 加载问题，因为还缺少 execmod 等权限** |
| `httpd_ssi_exec` | on | 允许 Server-Side Includes 执行脚本 | SSI 页面需要执行外部程序 |
| `httpd_builtin_scripting` | on | 允许 Apache 内置脚本（如 mod_php） | PHP 等模块化脚本语言；默认开启 |
| `httpd_enable_cgi` | on | 允许 CGI 脚本执行 | 传统 CGI 程序；默认开启 |
| `httpd_tmp_exec` | off | 允许 Apache 执行 /tmp 下的文件 | 临时目录中的 CGI/脚本 |

### 2.3 文件系统与存储

| 布尔值 | 默认 | 说明 | 何时开启 |
|--------|------|------|---------|
| `httpd_anon_write` | off | 允许 Apache 写入标记为 public_content_rw_t 的目录 | 上传目录、可写资源 |
| `httpd_sys_script_anon_write` | off | 允许 Apache 脚本写入 public_content_rw_t 目录 | CGI/mod_wsgi 需要写入公共目录 |
| `httpd_use_nfs` | off | 允许 Apache 访问 NFS 挂载的网站文件 | 网站文件在 NFS 上 |
| `httpd_use_cifs` | off | 允许 Apache 访问 CIFS/Samba 挂载的网站文件 | 网站文件在 Windows 共享上 |
| `httpd_use_fusefs` | off | 允许 Apache 访问 FUSE 文件系统 | 网站文件在 FUSE 挂载点 |
| `httpd_use_gpg` | off | 允许 Apache 访问 GPG 密钥环 | 需要 GPG 加密/签名的应用 |

### 2.4 用户目录与权限

| 布尔值 | 默认 | 说明 | 何时开启 |
|--------|------|------|---------|
| `httpd_enable_homedirs` | off | 允许 Apache 读取用户家目录（`~user/public_html`） | UserDir 模块 |
| `httpd_read_user_content` | off | 允许 Apache 读取标记为 user_home_t 的内容 | 网站文件放在用户家目录下 |

### 2.5 特殊集成

| 布尔值 | 默认 | 说明 | 何时开启 |
|--------|------|------|---------|
| `httpd_can_sendmail` | off | 允许 Apache 调用 sendmail 发送邮件 | 应用通过 mail()/sendmail 发邮件 |
| `httpd_manage_ipa` | off | 允许 Apache 管理 FreeIPA 身份认证 | FreeIPA 集成 |
| `httpd_mod_auth_pam` | off | 允许 Apache 使用 PAM 认证 | mod_authnz_pam 模块 |
| `httpd_mod_auth_ntlm_winbind` | off | 允许 Apache 使用 NTLM/Winbind 认证 | 与 Windows AD 集成认证 |
| `httpd_dbus_avahi` | off | 允许 Apache 通过 D-Bus 访问 Avahi | mDNS/Zeroconf 服务发现 |
| `httpd_dbus_sssd` | off | 允许 Apache 通过 D-Bus 访问 SSSD | SSSD 身份认证集成 |
| `httpd_run_ipa` | off | 允许 Apache 运行 IPA 相关脚本 | FreeIPA 辅助脚本 |
| `httpd_serve_cobbler_files` | off | 允许 Apache 提供 Cobbler 文件 | Cobbler 装机服务 |
| `httpd_can_connect_cobbler` | off | 允许 Apache 连接 Cobbler 服务 | Cobbler 集成 |
| `httpd_run_preupgrade` | off | 允许 Apache 运行预升级检查 | 系统升级工具 |
| `httpd_run_stickshift` | off | 允许 Apache 运行 OpenShift 相关操作 | OpenShift 集成 |

### 2.6 调试与杂项

| 布尔值 | 默认 | 说明 | 何时开启 |
|--------|------|------|---------|
| `httpd_dontaudit_search_dirs` | off | 禁止审计目录搜索拒绝事件 | 减少审计日志噪音 |
| `httpd_graceful_shutdown` | off | 允许 Apache 优雅关闭 | 特定关闭流程需要 |
| `httpd_setrlimit` | off | 允许 Apache 修改资源限制 | 需要调整文件描述符等限制 |
| `httpd_tty_comm` | off | 允许 Apache 与终端通信 | 极罕见的调试场景 |
| `httpd_can_check_spam` | off | 允许 Apache 调用反垃圾邮件检查 | SpamAssassin 集成 |
| `httpd_manage_courier_spool` | off | 允许 Apache 管理 Courier 邮件队列 | Courier 邮件服务器集成 |
| `httpd_use_opencryptoki` | off | 允许 Apache 使用 OpenCryptoki 硬件加密 | 硬件安全模块 (HSM) |
| `httpd_use_openstack` | off | 允许 Apache 访问 OpenStack 服务 | OpenStack 集成 |
| `httpd_use_sasl` | off | 允许 Apache 使用 SASL 认证 | SASL 认证机制 |
| `httpd_enable_ftp_server` | off | 允许 Apache 启用内建 FTP | Apache FTP 模块 |

---

## 3. 本次排障涉及的布尔值（最终状态）

```
httpd_unified                --> on    # 核心：解决 .so 加载
httpd_can_network_connect    --> on    # 应用需要向外发起 HTTP 请求
httpd_can_network_connect_db --> off   # 不需要数据库，关掉
httpd_execmem                --> on    # 早期尝试（单独无效，但保留）
httpd_ssi_exec               --> on    # 默认
httpd_builtin_scripting      --> on    # 默认
httpd_enable_cgi             --> on    # 默认
```

详见 [[Apache-mod_wsgi-SELinux排障]]。

---

## 4. 其他常见服务布尔值

### 4.1 SSH

| 布尔值 | 默认 | 说明 |
|--------|------|------|
| `ssh_keysign` | off | 允许 ssh-keysign 用于主机认证 |
| `ssh_sysadm_login` | off | 允许 sysadm 角色通过 SSH 登录 |
| `ssh_chroot_rw_homedirs` | off | 允许 chroot 的 SSH 用户读写家目录 |
| `ssh_use_tcpd` | off | 允许 SSH 使用 TCP wrappers |

详见 [[SSH密钥登录配置排障实录]]。

### 4.2 NFS

| 布尔值 | 默认 | 说明 |
|--------|------|------|
| `nfs_export_all_ro` | on | 允许 NFS 导出所有文件系统（只读） |
| `nfs_export_all_rw` | on | 允许 NFS 导出所有文件系统（读写） |
| `nfsd_anon_write` | off | 允许 NFS 服务端匿名写入 |
| `use_nfs_home_dirs` | off | 允许用户家目录通过 NFS 挂载 |

### 4.3 虚拟化

| 布尔值 | 默认 | 说明 |
|--------|------|------|
| `virt_use_nfs` | on | 允许虚拟机访问 NFS 存储 |
| `virt_use_usb` | on | 允许虚拟机使用 USB 设备 |
| `virt_sandbox_use_all_caps` | on | 允许沙箱使用所有能力 |
| `virt_sandbox_use_audit` | on | 允许沙箱使用审计子系统 |
| `virt_use_execmem` | off | 允许虚拟机使用可执行内存 |
| `virt_use_fusefs` | off | 允许虚拟机访问 FUSE 文件系统 |
| `virt_use_samba` | off | 允许虚拟机访问 Samba 共享 |
| `virt_use_xserver` | off | 允许虚拟机使用 X Server |

### 4.4 容器

| 布尔值 | 默认 | 说明 |
|--------|------|------|
| `container_connect_any` | off | 允许容器连接任意网络 |
| `container_manage_cgroup` | off | 允许容器管理 cgroup |
| `container_use_devices` | off | 允许容器使用设备文件 |
| `container_use_dri_devices` | on | 允许容器使用 DRI/GPU 设备 |

### 4.5 用户环境

| 布尔值 | 默认 | 说明 |
|--------|------|------|
| `selinuxuser_ping` | on | 允许普通用户使用 ping |
| `selinuxuser_execstack` | on | 允许用户程序使用可执行栈 |
| `selinuxuser_execheap` | off | 允许用户程序使用可执行堆（安全风险） |
| `selinuxuser_execmod` | off | 允许用户程序使用可执行内存映射 |
| `use_virtualbox` | on | 允许 VirtualBox 运行 |
| `unconfined_login` | on | 允许用户以 unconfined 域登录 |
| `mozilla_plugin_can_network_connect` | on | 允许浏览器插件发起网络连接 |

### 4.6 其他服务

| 布尔值 | 默认 | 说明 |
|--------|------|------|
| `fips_mode` | on | 启用 FIPS 140-2 加密模式 |
| `nscd_use_shm` | on | 允许 nscd 使用共享内存 |
| `mount_anyfile` | on | 允许挂载任意文件 |
| `domain_fd_use` | on | 允许域内文件描述符传递 |
| `daemons_dontaudit_scheduling` | on | 禁止审计守护进程调度事件 |
| `kerberos_enabled` | on | 启用 Kerberos 认证 |
| `named_write_master_zones` | on | 允许 named 写入主 DNS 区域文件 |
| `squid_connect_any` | on | 允许 Squid 连接任意端口 |
| `postfix_local_write_mail_spool` | on | 允许 Postfix 写入本地邮件池 |
| `global_ssp` | off | 全局栈保护（Stack Smashing Protection） |

---

## 5. 快速排障技巧

### 5.1 按服务过滤

```bash
getsebool -a | grep httpd
getsebool -a | grep ssh
getsebool -a | grep nfs
getsebool -a | grep virt
```

### 5.2 查看布尔值描述

```bash
# 看某个布尔值的作用（需要 policycoreutils-devel）
semanage boolean -l | grep httpd_unified

# 查看所有 httpd 相关布尔值的描述
semanage boolean -l | grep httpd
```

### 5.3 查看当前开启的布尔值

```bash
getsebool -a | grep "--> on"
```

---

## 参考

- [[SELinux]] -- SELinux 完整指南，安全上下文、排障方法论
- [[Apache-mod_wsgi-SELinux排障]] -- httpd_unified / httpd_execmem 的实际排障案例
- [[Apache-RHEL]] -- RHEL 系 Apache 配置参考，第 6 节含 SELinux 基础
- [[SSH密钥登录配置排障实录]] -- SSH + SELinux 排障案例
