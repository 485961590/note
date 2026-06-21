# Linux 运维常用命令

> 系统管理日常操作：服务启停、进程端口、磁盘用户、网络包管理等命令速查。

---

## 服务管理（systemctl）

systemd 是现代 Linux 的标准初始化系统，`systemctl` 是其管理入口。

### 服务启停

```bash
# 启动服务
sudo systemctl start nginx

# 停止服务
sudo systemctl stop nginx

# 重启服务
sudo systemctl restart nginx

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 如果 reload 不支持则 restart
sudo systemctl reload-or-restart nginx
```

### 开机自启

```bash
# 启用开机自启
sudo systemctl enable nginx

# 禁用开机自启
sudo systemctl disable nginx

# 查看是否已启用
systemctl is-enabled nginx

# 启用并立即启动
sudo systemctl enable --now nginx
```

### 状态查看

```bash
# 查看服务状态
systemctl status nginx

# 查看是否运行中
systemctl is-active nginx

# 列出所有启动失败的服务
systemctl --failed

# 列出所有已启用的服务
systemctl list-unit-files --state=enabled

# 列出所有正在运行的服务
systemctl list-units --type=service --state=running
```

### 系统级操作

```bash
# 重新加载 systemd 配置（修改 unit 文件后执行）
sudo systemctl daemon-reload

# 查看服务依赖关系
systemctl list-dependencies nginx

# 屏蔽服务（禁止手动和自动启动）
sudo systemctl mask nginx
sudo systemctl unmask nginx
```

---

## 进程管理

### 查看进程（ps）

```bash
# 查看当前 shell 的进程
ps

# 查看所有进程（BSD 风格）
ps aux

# 查看所有进程（Linux 风格）
ps -ef

# 按 CPU 使用率排序
ps aux --sort=-%cpu | head -10

# 按内存使用率排序
ps aux --sort=-%mem | head -10

# 查找特定进程
ps aux | grep nginx

# 树状显示父子进程关系
ps auxf
pstree -p
```

### 实时监控（top / htop）

```bash
# 实时进程监控
top

# top 常用交互键
#   P — 按 CPU 排序
#   M — 按内存排序
#   k — 输入 PID 杀死进程
#   q — 退出
#   u — 过滤用户
#   1 — 切换各 CPU 核心显示

# 更友好的替代品（需安装）
htop
```

### 终止进程

```bash
# 按 PID 终止（默认信号 SIGTERM，15）
kill 1234

# 强制终止（SIGKILL，9）
kill -9 1234

# 列出所有信号
kill -l

# 按名称终止
killall nginx
pkill nginx

# 终止某用户所有进程
pkill -u username

# 优雅重载配置（SIGHUP）
kill -HUP $(cat /var/run/nginx.pid)

# 终止挂起的后台进程（-1 表示进程组）
kill -9 -1
```

### 后台与前台

```bash
# 命令末尾加 & 后台运行
sleep 300 &

# 查看当前终端的后台任务
jobs

# 把作业调到前台
fg %1

# 把挂起的作业放后台继续
bg %1

# 登出后继续运行
nohup ./long_script.sh &

# 脱离当前 shell 控制
disown %1
```

### 进程优先级

```bash
# 以低优先级启动（nice 值 -20 到 19，默认 0，值越大优先级越低）
nice -n 10 ./heavy_task.sh

# 调整运行中进程的优先级
renice -n 5 -p 1234

# 查看进程 nice 值
ps -o pid,ni,comm -p 1234
```

---

## 端口与连接

### ss（推荐，替代 netstat）

```bash
# 列出所有监听端口
ss -tlnp

# 列出所有 TCP 连接
ss -tanp

# 列出所有 UDP 端口
ss -ulnp

# 查看特定端口
ss -tlnp | grep :80

# 显示进程信息（需 root）
sudo ss -tlnp
```

### netstat（传统工具）

```bash
# 列出所有监听端口
netstat -tlnp

# 列出所有连接（含状态）
netstat -tanp

# 统计各状态连接数
netstat -an | awk '/^tcp/ {print $6}' | sort | uniq -c | sort -rn
```

### lsof（列出打开的文件）

```bash
# 查看占用某端口的进程
sudo lsof -i :80
sudo lsof -i :443

# 查看某进程打开的文件
sudo lsof -p 1234

# 查看某用户打开的文件
sudo lsof -u username

# 查看某目录下被打开的文件
sudo lsof +D /var/log
```

### fuser（用文件/端口反查进程）

```bash
# 查看占用端口的进程 PID
sudo fuser 80/tcp
sudo fuser 443/tcp

# 杀死占用端口的进程
sudo fuser -k 8080/tcp

# 查看占用文件的进程
fuser -v /var/log/syslog
```

---

## 磁盘与存储

### 磁盘使用情况

```bash
# 查看分区使用情况（人类可读）
df -h

# 查看 inode 使用情况（小文件过多时会耗尽）
df -i

# 查看目录占用大小
du -sh /var/log/

# 查看目录下各子目录大小
du -sh /* 2>/dev/null

# 按大小排序
du -sh * | sort -h

# 查看指定深度
du -h --max-depth=1 /home/
```

### 挂载管理

```bash
# 列出所有挂载点
mount
findmnt

# 挂载设备
sudo mount /dev/sdb1 /mnt/data

# 卸载
sudo umount /mnt/data

# 强制卸载（设备忙时）
sudo umount -l /mnt/data

# 挂载 ISO 镜像
sudo mount -o loop image.iso /mnt/iso

# 编辑 /etc/fstab 实现开机自动挂载
```

### 磁盘分区信息

```bash
# 列出块设备
lsblk
lsblk -f    # 含文件系统类型和 UUID

# 查看磁盘分区
sudo fdisk -l

# 查看磁盘 UUID
blkid

# 查看 SCSI 磁盘详细信息
sudo smartctl -a /dev/sda
```

### 文件系统操作

```bash
# 检查并修复文件系统
sudo fsck /dev/sdb1

# 格式化分区
sudo mkfs.ext4 /dev/sdb1
sudo mkfs.xfs /dev/sdb1

# 创建交换分区
sudo mkswap /dev/sdb2
sudo swapon /dev/sdb2
```

### dd（磁盘读写）

```bash
# 创建启动盘
sudo dd if=ubuntu.iso of=/dev/sdb bs=4M status=progress

# 备份磁盘到镜像
sudo dd if=/dev/sda of=/backup/disk.img bs=4M status=progress

# 制作交换文件
dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo mkswap /swapfile && sudo swapon /swapfile
```

---

## 用户与权限

### 用户管理

```bash
# 创建用户
sudo useradd -m -s /bin/bash username

# 设置 / 修改密码
sudo passwd username

# 修改用户信息
sudo usermod -aG docker username    # 加入附加组
sudo usermod -s /bin/zsh username   # 修改默认 shell
sudo usermod -L username            # 锁定账户
sudo usermod -U username            # 解锁账户

# 删除用户
sudo userdel -r username            # -r 同时删除家目录

# 查看用户信息
id username
finger username
```

### 用户组管理

```bash
# 创建组
sudo groupadd devteam

# 将用户加入组
sudo usermod -aG devteam username

# 查看用户所属组
groups username

# 查看组内成员
getent group devteam
```

### 文件权限

> 详细的权限管理（chmod 数字/符号模式、chown、chgrp、umask、setuid/setgid/sticky bit、chattr/lsattr 扩展属性、ACL、SELinux）已独立为 [权限管理](权限管理.md)。

**常用命令速查：**

```bash
# 权限
chmod 755 file                   # rwxr-xr-x
chmod 600 id_rsa                 # rw-------
chown user:group file            # 改属主属组
umask 022                        # 默认权限掩码

# 扩展属性（安全加固常用）
sudo chattr +i important.conf    # 设为不可变（连 root 也不能改/删）
sudo chattr +a app.log           # 设为仅追加（日志防清除）
lsattr file.txt                  # 查看扩展属性
```

### sudo 配置

```bash
# 编辑 sudoers（必须用 visudo）
sudo visudo

# 授予用户所有 sudo 权限
# username ALL=(ALL:ALL) ALL

# 授予用户免密码执行特定命令
# username ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx

# 查看当前用户 sudo 权限
sudo -l
```

---

## 软件包管理

### Debian/Ubuntu（apt / dpkg）

```bash
# 更新软件源
sudo apt update

# 升级所有软件包
sudo apt upgrade

# 安装软件
sudo apt install nginx vim curl

# 卸载软件（保留配置）
sudo apt remove nginx

# 完全卸载（含配置）
sudo apt purge nginx

# 清理缓存
sudo apt clean
sudo apt autoremove --purge

# 搜索软件
apt search keyword

# 查看软件信息
apt show nginx

# 列出已安装的包
apt list --installed

# 查看某文件属于哪个包
dpkg -S /etc/nginx/nginx.conf

# 列出某包安装的所有文件
dpkg -L nginx

# 安装本地 .deb 包
sudo dpkg -i package.deb

# 修复依赖
sudo apt install -f
```

### RHEL/CentOS/Fedora（dnf / yum / rpm）

```bash
# 安装软件
sudo dnf install nginx vim curl      # Fedora/CentOS 8+
sudo yum install nginx vim curl      # CentOS 7 及更早

# 更新
sudo dnf update

# 卸载
sudo dnf remove nginx

# 搜索
dnf search keyword

# 列出已安装
dnf list --installed

# 查看某文件属于哪个包
rpm -qf /etc/nginx/nginx.conf

# 安装本地 .rpm 包
sudo rpm -ivh package.rpm

# 列出某包的所有文件
rpm -ql nginx
```

### 源码编译安装（通用流程）

```bash
# 通常流程
tar -xzf source.tar.gz
cd source/
./configure --prefix=/usr/local/app
make
sudo make install

# 卸载（在源码目录执行）
sudo make uninstall
```

---

## 网络管理

### IP 地址与接口

```bash
# 查看所有网络接口
ip addr show
ip a

# 查看路由表
ip route show
ip r

# 查看 ARP 表
ip neigh show

# 启用 / 禁用网卡
sudo ip link set eth0 up
sudo ip link set eth0 down

# 添加临时 IP
sudo ip addr add 192.168.1.100/24 dev eth0

# 传统命令（部分系统需安装 net-tools）
ifconfig
route -n
```

### 网络连通性

```bash
# 连通性测试
ping -c 4 8.8.8.8

# 路由追踪
traceroute google.com
mtr google.com                     # 更直观的实时追踪

# DNS 查询
nslookup example.com
dig example.com
dig -x 8.8.8.8                     # 反向查询

# 查看 DNS 解析过程
dig +trace example.com
```

### 文件下载

```bash
# curl — 功能最全
curl -O https://example.com/file.zip               # 下载（保留原名）
curl -o newname.zip https://example.com/file.zip   # 下载（指定文件名）
curl -I https://example.com                         # 只看响应头
curl -s https://api.example.com | jq .              # 静默 + JSON 格式化

# wget — 支持递归下载
wget https://example.com/file.zip
wget -c https://example.com/large.zip               # 断点续传
wget -r -l 2 https://example.com/                   # 递归下载
```

### SSH 与远程传输

```bash
# SSH 连接
ssh user@192.168.1.100
ssh -p 2222 user@host                               # 指定端口
ssh -i ~/.ssh/id_rsa user@host                      # 指定密钥

# 复制文件
scp file.txt user@host:/path/
scp -r dir/ user@host:/path/                        # 递归复制

# 增量同步（比 scp 智能，只传差异）
rsync -avz source/ user@host:/dest/
rsync -avz --progress source/ user@host:/dest/
rsync -avz --delete source/ user@host:/dest/        # 删除目标多余文件
```

---

## 定时任务

### crontab

```bash
# 编辑当前用户定时任务
crontab -e

# 查看定时任务
crontab -l

# 删除全部定时任务
crontab -r

# 以其他用户身份编辑
sudo crontab -u username -e
```

**cron 时间格式：**

```
# 分 时 日 月 周  命令
# ┬ ┬ ┬ ┬ ┬
# │ │ │ │ └── 星期 (0-7, 0 和 7 都是周日)
# │ │ │ └──── 月份 (1-12)
# │ │ └────── 日期 (1-31)
# │ └──────── 小时 (0-23)
# └────────── 分钟 (0-59)
```

```bash
# 示例
0 3 * * * /backup/script.sh              # 每天凌晨 3 点
*/5 * * * * /usr/bin/healthcheck.sh      # 每 5 分钟
0 9-17 * * 1-5 /usr/bin/monitor.sh       # 工作日 9-17 点整点
@reboot /usr/bin/startup.sh              # 开机执行
@daily /usr/bin/logrotate.sh             # 每天 0 点
```

### at（一次性定时）

```bash
# 10 分钟后执行
echo "/path/to/script.sh" | at now + 10 minutes

# 指定时间执行
at 02:30 2026-07-01 <<< "/path/to/script.sh"

# 查看待执行任务
atq

# 删除任务
atrm 3
```

---

## 日志查看

### journalctl（systemd 日志）

```bash
# 查看所有日志
journalctl

# 查看本次启动后的日志
journalctl -b

# 查看某服务的日志
journalctl -u nginx

# 查看最近日志（倒序）
journalctl -u nginx --since "10 minutes ago"

# 实时跟踪（类似 tail -f）
journalctl -u nginx -f

# 按时间范围
journalctl --since "2026-06-01" --until "2026-06-18"

# 按优先级（0=emerg, 3=err, 6=info）
journalctl -p 3
```

### 传统日志文件

```bash
# 实时查看日志
tail -f /var/log/syslog
tail -f /var/log/nginx/access.log

# 查看最后 50 行
tail -n 50 /var/log/syslog

# 查看内核日志
dmesg
dmesg | tail -20

# 查看登录记录
last
lastb                            # 失败的登录尝试

# 查看用户登录历史
who /var/log/wtmp
```

---

## 系统信息

### 基本信息

```bash
# 内核版本
uname -a
uname -r

# 发行版信息
cat /etc/os-release
lsb_release -a

# 主机名
hostname
hostnamectl set-hostname newname     # 永久修改

# 系统运行时间
uptime

# CPU 信息
lscpu
cat /proc/cpuinfo

# 内存信息
free -h
cat /proc/meminfo

# 查看内存占用 Top 进程
ps aux --sort=-%mem | head -10
```

### 性能监控

```bash
# 虚拟内存统计
vmstat 2 5           # 每 2 秒采样，共 5 次

# CPU 和 I/O 统计
iostat -x 2

# 查看系统负载
cat /proc/loadavg

# 查看中断和 CPU 使用
mpstat -P ALL 2
```

### 硬件信息

```bash
# 列出所有 PCI 设备
lspci

# 列出 USB 设备
lsusb

# 查看硬件详细信息
sudo dmidecode -t system
sudo dmidecode -t memory

# 查看磁盘型号和序列号
sudo hdparm -I /dev/sda
```

---

## 开关机与重启

```bash
# 立即关机
sudo shutdown -h now
sudo poweroff

# 立即重启
sudo shutdown -r now
sudo reboot

# 定时关机（10 分钟后）
sudo shutdown -h +10

# 定时重启（凌晨 2 点）
sudo shutdown -r 02:00

# 取消定时
sudo shutdown -c

# 切换运行级别（传统 init 系统）
sudo init 0          # 关机
sudo init 6          # 重启
sudo init 1          # 单用户模式
```

---

## 环境变量

```bash
# 查看所有环境变量
env
printenv

# 查看单个变量
echo $PATH
echo $HOME

# 临时设置
export MY_VAR="hello"

# 永久设置当前用户
echo 'export MY_VAR="hello"' >> ~/.bashrc
source ~/.bashrc

# 永久设置所有用户
echo 'export MY_VAR="hello"' | sudo tee -a /etc/environment
```

---

## 模块与内核

```bash
# 列出已加载的内核模块
lsmod

# 加载模块
sudo modprobe module_name

# 卸载模块
sudo modprobe -r module_name

# 查看模块详细信息
modinfo module_name

# 查看内核启动参数
cat /proc/cmdline
```

---

## 系统时间

```bash
# 查看当前时间
date
date +"%Y-%m-%d %H:%M:%S"

# 查看硬件时钟
sudo hwclock --show

# 设置时间（systemd）
sudo timedatectl set-time "2026-06-18 14:30:00"

# 设置时区
sudo timedatectl set-timezone Asia/Shanghai

# 启用 NTP 自动同步
sudo timedatectl set-ntp true

# 查看时区和时间同步状态
timedatectl status
```

---

## 快速参考

| 需求 | 命令 |
|------|------|
| 启动 / 停止服务 | `systemctl start/stop <服务名>` |
| 开机自启 | `systemctl enable <服务名>` |
| 查看进程 | `ps aux` |
| 终止进程 | `kill <PID>` / `pkill <名称>` |
| 查看端口 | `ss -tlnp` |
| 查看端口占用 | `lsof -i :端口号` |
| 磁盘使用 | `df -h` / `du -sh <目录>` |
| 创建用户 | `useradd -m -s /bin/bash <用户名>` |
| 修改权限 | `chmod` / `chown` / `chattr` / `lsattr` |
| 安装软件 | `apt install` / `dnf install` |
| 网络连通 | `ping` / `traceroute` |
| 下载文件 | `curl -O` / `wget` |
| 远程连接 | `ssh user@host` |
| 定时任务 | `crontab -e` |
| 查看日志 | `journalctl -u <服务名>` / `tail -f` |
| 系统信息 | `uname -a` / `free -h` / `lscpu` |
| 关机重启 | `shutdown -h now` / `reboot` |

---

## 参考

- [权限管理](权限管理.md) — 文件权限、chattr、ACL、SELinux 完整文档
- [SELinux 详解](SELinux.md) — SELinux 强制访问控制
- [Linux服务管理](Linux服务管理.md) — systemd 服务管理
- [Bash Shell.md](Bash%20Shell.md) — Shell 编程参考
- [Linux文本处理命令.md](Linux文本处理命令.md) — 文本处理命令详解
