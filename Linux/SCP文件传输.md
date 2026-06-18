# SCP 文件传输

> scp（Secure Copy）基于 SSH 协议在主机之间传文件，语法简单，加密传输。Linux 原生自带，Windows 10 1809+ 也内置了 OpenSSH 客户端。跨平台传文件的首选方案。

---

## 基本语法

```bash
# 从本地传到远程
scp [选项] 本地文件 用户名@目标IP:远程路径

# 从远程拉到本地
scp [选项] 用户名@目标IP:远程路径 本地路径

# 远程主机之间互传
scp [选项] 用户名@主机A:文件路径 用户名@主机B:目标路径
```

源和目标可以互换位置。`用户名@` 省略时默认用当前本地用户名。

---

## 常用选项

| 选项 | 说明 |
|------|------|
| `-P 端口` | 指定 SSH 端口（默认 22），**注意是大写 P** |
| `-p` | 保留文件的修改时间、访问时间和权限，**注意是小写 p** |
| `-r` | 递归复制整个目录 |
| `-i 密钥文件` | 指定私钥文件（不用密码，用密钥认证） |
| `-C` | 传输时压缩数据，慢速网络下能提速 |
| `-l 带宽` | 限制带宽，单位 Kbit/s（比如 `-l 800` 限制到 ~100KB/s） |
| `-v` | 详细输出，排查连接问题用 |
| `-q` | 静默模式，不显示进度和错误（脚本里用） |
| `-o SSH选项` | 透传 SSH 配置项（如 `-o StrictHostKeyChecking=no`） |
| `-3` | 远程互传时让数据经过本地中转（默认两个远程直连） |
| `-4` / `-6` | 强制使用 IPv4 / IPv6 |
| `-B` | 批量模式，不询问密码（密钥认证必须能用） |

---

## Linux 上传文件到目标

### 基础用法

```bash
# 上传单个文件
scp /path/to/local/file.txt user@192.168.1.100:/home/user/

# 上传并重命名
scp /path/to/local/file.txt user@192.168.1.100:/home/user/newname.txt

# 上传整个目录（-r 递归）
scp -r /path/to/local/dir user@192.168.1.100:/home/user/

# 上传目录里的所有内容（不包括目录本身）
scp -r /path/to/local/dir/* user@192.168.1.100:/home/user/target/

# 一次传多个文件
scp file1.txt file2.txt file3.txt user@192.168.1.100:/home/user/

# 通配符传一类文件
scp *.log user@192.168.1.100:/home/user/logs/
scp /var/log/*.gz user@192.168.1.100:/backup/
```

### 指定端口和密钥

```bash
# 目标 SSH 不是 22 端口时 -P 指定
scp -P 2222 file.txt user@192.168.1.100:/home/user/

# 用私钥认证而不是密码
scp -i ~/.ssh/mykey file.txt user@192.168.1.100:/home/user/

# 私钥 + 非标准端口组合
scp -P 2222 -i ~/.ssh/mykey file.txt user@192.168.1.100:/home/user/

# 跳过 host key 确认（首次连接或内网用，不安全但方便）
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null file.txt user@192.168.1.100:/tmp/
```

### 保留文件属性与压缩

```bash
# 保留原始修改时间和权限
scp -p file.txt user@192.168.1.100:/home/user/

# 慢速链路开压缩
scp -C large_file.tar.gz user@192.168.1.100:/home/user/

# 限制带宽上传（限 1MB/s = 8192 Kbit/s）
scp -l 8192 huge_file.iso user@192.168.1.100:/home/user/

# 常用组合：递归 + 压缩 + 保留属性
scp -r -C -p project/ user@192.168.1.100:/home/user/
```

### 从远程下载文件到本地

```bash
# 下载单个文件
scp user@192.168.1.100:/remote/file.txt ./local/dir/

# 下载整个目录
scp -r user@192.168.1.100:/remote/dir ./local/dir/

# 下载目录里的所有内容到当前目录（注意最后的 .）
scp -r user@192.168.1.100:/remote/dir/* .

# 带端口下载
scp -P 2222 user@192.168.1.100:/remote/file.txt ./
```

### 远程主机间互传

```bash
# 从主机 A 传到主机 B（数据在 A 到 B 之间直传，不经过本地）
scp userA@192.168.1.10:/file.txt userB@192.168.1.20:/target/

# 经过本机中转（两边网络不互通时用）
scp -3 userA@192.168.1.10:/file.txt userB@10.0.0.20:/target/
```

---

## Windows 上传文件到目标

Windows 有四种主流方式用 scp：系统自带的 OpenSSH scp、PuTTY 套件的 pscp、WinSCP 图形界面、以及 WSL 里的原生 scp。

### 方式一：Windows 内置 scp（推荐，Win10 1809+）

Windows 10 1809 及之后版本内置了 OpenSSH 客户端，打开 PowerShell 或 CMD 就能直接用，语法和 Linux 版一样。

```powershell
# PowerShell 或 CMD 中直接敲，语法完全一致
scp D:\files\report.pdf root@192.168.1.100:/tmp/

# 递归传目录
scp -r D:\project\code root@192.168.1.100:/opt/

# 指定端口
scp -P 2222 D:\backup\data.zip user@192.168.1.100:/home/user/

# 用密钥
scp -i C:\Users\name\.ssh\id_rsa D:\file.txt user@192.168.1.100:/tmp/

# 注意 Windows 路径里反斜杠也能用，但正斜杠更省事
scp C:/Users/name/Desktop/file.txt root@192.168.1.100:/tmp/

# 从远程下载到 Windows
scp root@192.168.1.100:/etc/nginx/nginx.conf D:\configs\
```

如果 `scp` 提示 "不是内部或外部命令"，说明 OpenSSH 客户端没装：

```powershell
# 管理员身份运行 PowerShell，添加 OpenSSH 客户端
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0

# 或者：设置 → 应用 → 可选功能 → 添加功能 → 搜索 "OpenSSH 客户端" → 安装
```

### 方式二：PSCP（PuTTY 套件）

`pscp.exe` 是 PuTTY 自带的命令行 scp 工具，单文件，不需要安装，适合放到 U 盘里到处用。语法和 scp 略有差异。

从 [PuTTY 官网](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) 下载 `pscp.exe`，放到 `C:\Windows\System32\` 或者随便一个在 PATH 里的目录。

```cmd
:: 上传文件（-P 端口，-i 密钥，和 scp 一样）
pscp D:\file.txt root@192.168.1.100:/tmp/

:: 递归上传目录
pscp -r D:\project root@192.168.1.100:/opt/

:: 指定端口
pscp -P 2222 D:\data.zip user@192.168.1.100:/home/user/

:: 使用 PuTTY 私钥（.ppk 格式，不是 OpenSSH 格式）
pscp -i D:\keys\mykey.ppk D:\file.txt root@192.168.1.100:/tmp/

:: 下载文件
pscp root@192.168.1.100:/var/log/syslog D:\logs\

:: 下载整个目录
pscp -r root@192.168.1.100:/etc/nginx D:\configs\

:: 批量下载（通配符）
pscp root@192.168.1.100:/var/log/*.log D:\logs\
```

**PuTTY 私钥格式转换（.ppk 转 OpenSSH）：**

Windows 内置 scp 用的是 OpenSSH 格式密钥，pscp 用的是 PuTTY 的 .ppk 格式。如果手上只有 .ppk，用 PuTTYgen 转一下：

```
1. 打开 PuTTYgen
2. Load → 选你的 .ppk 文件
3. Conversions → Export OpenSSH key
4. 保存为 id_rsa 或其它名字
```

也可以用命令行（装了 PuTTY 之后）：

```cmd
puttygen mykey.ppk -O private-openssh -o id_rsa
```

### 方式三：WinSCP（图形界面）

WinSCP 是 Windows 下最流行的 SFTP/SCP 图形客户端。适合不常敲命令行、需要拖拽传文件的场景。

```
1. 官网下载: https://winscp.net/
2. 新建会话 → 填 IP、端口、用户名、密码（或密钥）
3. 左半边是本地文件，右半边是远程文件
4. 拖拽或 F5 复制即可
```

WinSCP 也带命令行工具（安装后 `winscp.com` 在安装目录下）：

```cmd
:: WinSCP 命令行上传
winscp.com /command "open sftp://user:pass@192.168.1.100/" "put D:\file.txt /tmp/" "exit"

:: 同步整个目录
winscp.com /command "open sftp://user:pass@192.168.1.100/" "synchronize remote D:\local\dir /remote/dir" "exit"
```

### 方式四：WSL 中的 scp

如果已经装了 WSL，直接在 WSL 终端里用 Linux 原生的 scp，可以访问 Windows 文件系统：

```bash
# WSL 中访问 Windows 文件（/mnt/c/ 对应 C:\）
scp /mnt/d/files/report.pdf user@192.168.1.100:/home/user/

# 从 WSL 上传（WSL 自己的文件在 ~/ 下）
scp ~/project/code.tar.gz user@192.168.1.100:/tmp/

# 下载到 Windows 桌面
scp user@192.168.1.100:/remote/file.txt /mnt/c/Users/name/Desktop/
```

---

## 实用场景

### 场景1：批量传文件 + 输密码

```bash
# 一次 ssh 登录建立连接后保持，用 ControlMaster 复用连接
# 好处：传多个文件只输一次密码

# 先在 ~/.ssh/config 里配置
# Host myserver
#     HostName 192.168.1.100
#     User root
#     ControlMaster auto
#     ControlPath ~/.ssh/sockets/%r@%h:%p
#     ControlPersist 10m

mkdir -p ~/.ssh/sockets
ssh -fN myserver              # 建立连接，输一次密码
scp file1.txt myserver:/tmp/  # 后续 scp 不用再输密码
scp file2.txt myserver:/tmp/
scp file3.txt myserver:/tmp/
ssh -O exit myserver          # 关闭复用连接
```

### 场景2：传大文件 + 断点续传

scp 本身不支持断点续传。传大文件时建议改用 `rsync`（同样是基于 SSH）：

```bash
# rsync 通过 SSH 传输，支持断点续传
rsync -avzP --progress /path/to/large_file.iso user@192.168.1.100:/home/user/
# -a 归档模式（保留权限、时间）
# -v 详细输出
# -z 压缩
# -P 显示进度 + 支持断点续传（--partial --progress 的合并）
```

如果必须用 scp，把大文件先切割再传：

```bash
# 切割成 100MB 的小块
split -b 100M large_file.iso large_file.iso.part_

# 批量上传
scp large_file.iso.part_* user@192.168.1.100:/tmp/

# 在目标机器上合并
ssh user@192.168.1.100 "cat /tmp/large_file.iso.part_* > /home/user/large_file.iso"
```

### 场景3：无密码传输（密钥认证）

```bash
# 在本地生成密钥对（如果还没有）
ssh-keygen -t ed25519 -C "my-key"    # 推荐 ed25519
# 或兼容老系统：ssh-keygen -t rsa -b 4096

# 把公钥丢到目标机器（一行命令）
ssh-copy-id user@192.168.1.100
# 或者手动丢
cat ~/.ssh/id_ed25519.pub | ssh user@192.168.1.100 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 以后 scp 就不用输密码了
scp file.txt user@192.168.1.100:/tmp/
```

### 场景4：传文件并保持目录结构

```bash
# 只传 .log 文件但保持原来的目录结构
# scp 本身做不了，用 rsync
rsync -avzP --include='*/' --include='*.log' --exclude='*' /src/dir/ user@192.168.1.100:/dst/dir/

# 或者用 find + tar + ssh 管道（不依赖 rsync，纯标准工具）
cd /src/dir \
  && find . -name '*.log' | tar -czf - -T - \
  | ssh user@192.168.1.100 "cd /dst/dir && tar -xzf -"
```

### 场景5：跨跳板机传输（SSH 跳转）

```bash
# 场景：本地机器 → 跳板机(jump) → 目标内网机器(target)
# 本地无法直接访问 target，必须先连 jump

# 方式一：scp -J（SSH 7.3+，简单）
scp -J user@jump_host:22 file.txt user@target_host:/tmp/

# 方式二：通过 SSH config 配置 ProxyJump
# ~/.ssh/config:
# Host target
#     HostName 10.0.0.50
#     User root
#     ProxyJump user@jump_host
# 然后直接用
scp file.txt target:/tmp/

# 方式三：端口转发（老办法，兼容所有版本）
ssh -L 2222:target_host:22 user@jump_host -fN
scp -P 2222 file.txt root@127.0.0.1:/tmp/
# 用完关掉转发
ssh -O exit user@jump_host
```

---

## Windows 常见问题

### SCP 中文文件名乱码

```powershell
# 确认远程系统用的是 UTF-8（现代 Linux 都是）
# Windows 内置 scp 支持 UTF-8，一般没问题
# 如果目标系统用的不是 UTF-8（比如某些老 CentOS），传之前改名
rename-item "中文文件.txt" "chinese_file.txt"
```

### "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!"

重装过目标系统后会出现。去 `C:\Users\用户名\.ssh\known_hosts` 里删掉对应的那行，或者用命令：

```powershell
ssh-keygen -R 192.168.1.100
```

### 文件名里有空格

Windows 和 Linux 处理方法不同：

```powershell
# PowerShell：用双引号包裹
scp "D:\my files\report (2).pdf" root@192.168.1.100:"/home/user/my docs/"

# CMD：也用双引号，不过路径可以写在一起
scp "D:\my files\report.pdf" root@192.168.1.100:/tmp/
```

```bash
# Linux Bash：用反斜杠转义或双引号
scp /path/to/my\ files/report.pdf user@192.168.1.100:"/home/user/my docs/"
scp "/path/to/my files/report.pdf" "user@192.168.1.100:/home/user/my docs/"
```

---

## 快速对照：Windows 四种方式适用场景

| 方式 | 适用场景 | 缺点 |
|------|---------|------|
| 内置 scp | 偶尔用，命令行顺手 | 需 Win10 1809+ |
| PSCP | 用 PuTTY 全家桶的人，U 盘携带 | 需单独下载，.ppk 密钥格式不通用 |
| WinSCP | 不熟命令行的，经常大量传文件 | 需安装，图形界面不适合自动化 |
| WSL scp | 已有 WSL 环境的，和 Linux 命令一致 | 需要先装 WSL |

---

## 参考

- [OpenSSH SCP 手册](https://man.openbsd.org/scp)
- [PuTTY / PSCP 下载](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
- [WinSCP 官网](https://winscp.net/)
- [Windows OpenSSH 安装指南](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
