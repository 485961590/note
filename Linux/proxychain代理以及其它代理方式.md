# Linux 代理全解

Linux 下代理分为两类思路：

1. **劫持类**：强制接管程序的网络调用（proxychains）
2. **配置类**：让程序自己读代理配置（环境变量、配置文件）

先理解这个关键概念，才能明白为什么有些工具"不走代理"。

---

## 为什么有些工具不走 proxychains？

proxychains 通过 `LD_PRELOAD` 劫持标准 C 库的 socket 连接函数（`connect()` 等）来实现代理。

**以下情况 proxychains 无效：**

| 原因 | 典型工具 | 说明 |
|------|----------|------|
| **静态链接** | Go 编译的二进制程序 | Go 不依赖 libc 的 socket 函数，自己实现了网络栈 syscall，LD_PRELOAD 拦截不到 |
| **守护进程模式** | Docker daemon、systemd 服务 | proxychains 只能影响直接启动的进程，无法影响已有守护进程的子请求 |
| **内部直连** | Docker 拉镜像 | Docker daemon 是后台服务，docker pull 只是给 daemon 发指令，实际网络请求是 daemon 发的，不受 proxychains 影响 |
| **setuid/setgid 程序** | 部分系统工具 | 安全机制会忽略 LD_PRELOAD，防止权限提升 |
| **纯 shell builtin** | shell 内部命令 | 不产生新进程，不加载动态库 |

---

## 1. proxychains4 -- 劫持型代理

### 原理

```
proxychains4  ->  LD_PRELOAD 注入  ->  拦截 connect()  ->  转发到代理服务器
```

### 安装

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install proxychains4

# CentOS/RHEL
sudo yum install epel-release && sudo yum install proxychains-ng

# Arch
sudo pacman -S proxychains-ng

# macOS
brew install proxychains-ng
```

### 配置文件

proxychains4 启动时会按以下优先级找配置文件（找到第一个就停）：

1. 命令行指定：`proxychains4 -f /path/to/config`
2. 当前目录：`./proxychains.conf`
3. 用户级：`~/.proxychains/proxychains.conf`（需手动创建，只影响当前用户）
4. 全局：`/etc/proxychains4.conf`（影响所有用户，需要 sudo 编辑）

**什么时候用哪个？** 只有你一个人用这台机器，改 `/etc/proxychains4.conf` 最简单。多用户环境或多台机器的场景，用用户级配置更灵活、不影响他人。

配置文件内容示例：

```bash
# 代理模式（三种选一，取消注释）
strict_chain     # 严格按顺序，一个失败则整体失败
dynamic_chain    # 按顺序，跳过失效代理（推荐）
random_chain    # 随机选代理，每次请求可能走不同代理

# 推荐开启
proxy_dns        # DNS 也走代理，防止 DNS 泄露

# 超时设置
tcp_read_time_out 15000
tcp_connect_time_out 8000

# 代理列表
[ProxyList]
socks5 127.0.0.1 1080
# http 127.0.0.1 8080
```

### 使用

```bash
proxychains4 curl https://www.google.com
proxychains4 nmap -sT target.com
proxychains4 firefox
proxychains4 ssh user@server.com
```

**注意**：Nmap SYN 扫描（`-sS`）使用 raw socket，proxychains 拦截不到，只能用 `-sT`（TCP connect 扫描）。

---

## 2. 环境变量代理 -- 最通用的配置方式

绝大多数命令行工具（curl、wget、pip、npm、cargo、apt-get 等）都认这些环境变量。

### 2.1 一次性代理（仅当前终端，关终端即失效）

```bash
# HTTP 代理
export http_proxy="http://192.168.1.100:7890"
export https_proxy="http://192.168.1.100:7890"

# SOCKS5 代理（部分工具支持）
export all_proxy="socks5://192.168.1.100:7891"

# 不走代理的地址（逗号分隔，支持通配符）
export no_proxy="localhost,127.0.0.1,192.168.*,10.*,172.16.*"

# 部分工具需要大写形式（同时设置，兼容性最好）
export HTTP_PROXY="$http_proxy"
export HTTPS_PROXY="$https_proxy"
export NO_PROXY="$no_proxy"
export ALL_PROXY="$all_proxy"
```

**特点**：只在当前 shell 会话有效，新开终端不受影响。这是最安全的方式。

### 2.2 永久代理（写入 shell 配置文件）

**先了解涉及的配置文件：**

| 文件 | 作用 | 加载时机 |
|------|------|----------|
| `~/.bashrc` | Bash shell 的用户配置 | 每次打开交互式 Bash 终端时自动执行 |
| `~/.zshrc` | Zsh shell 的用户配置 | 每次打开交互式 Zsh 终端时自动执行 |
| `~/.profile` | 登录 shell 的用户配置 | 登录时执行一次（通常 `.bashrc` 也会被它调用） |

**为什么写这里？** shell（Bash/Zsh）每次启动时会自动读取这些文件并执行里面的命令。把 `export` 写进去，等于每次打开终端都帮你自动设置好代理环境变量，不用手动敲。

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
cat >> ~/.bashrc << 'EOF'

# ---- proxy ----
export http_proxy="http://192.168.1.100:7890"
export https_proxy="$http_proxy"
export all_proxy="socks5://192.168.1.100:7891"
export no_proxy="localhost,127.0.0.1,192.168.*,10.*,172.16.*"
export HTTP_PROXY="$http_proxy"
export HTTPS_PROXY="$https_proxy"
export NO_PROXY="$no_proxy"
export ALL_PROXY="$all_proxy"
# ---- proxy end ----
EOF

source ~/.bashrc
```

**特点**：每次打开终端都生效。注意这意味着所有支持环境变量的工具都会走代理，包括本地开发时的请求。

### 2.3 系统级永久代理（所有用户）

**先了解 `/etc/environment`：** 这是系统级的环境变量文件，由 PAM（Linux 的认证模块）在用户登录时加载。它不是 shell 脚本，格式是纯 `KEY=VALUE`，不需要也不能写 `export`。修改后会影响系统中所有用户的所有 shell，所以要用 `sudo` 编辑且必须谨慎。

```bash
# 编辑 /etc/environment（无 export 语法，纯 KEY=VALUE）
sudo vim /etc/environment
```

```
http_proxy="http://192.168.1.100:7890"
https_proxy="http://192.168.1.100:7890"
no_proxy="localhost,127.0.0.1"
```

重启或重新登录生效。**慎用**，会影响所有用户。

### 2.4 便捷切换函数

把以下内容加入 `~/.bashrc`，实现快速开关代理：

```bash
# 开启代理
proxy_on() {
    export http_proxy="http://192.168.1.100:7890"
    export https_proxy="$http_proxy"
    export all_proxy="socks5://192.168.1.100:7891"
    export no_proxy="localhost,127.0.0.1,192.168.*,10.*,172.16.*"
    export HTTP_PROXY="$http_proxy"
    export HTTPS_PROXY="$https_proxy"
    export NO_PROXY="$no_proxy"
    export ALL_PROXY="$all_proxy"
    echo "proxy ON"
}

# 关闭代理
proxy_off() {
    unset http_proxy https_proxy all_proxy no_proxy
    unset HTTP_PROXY HTTPS_PROXY NO_PROXY ALL_PROXY
    echo "proxy OFF"
}

# 查看当前代理状态
proxy_status() {
    echo "http_proxy  = ${http_proxy:-未设置}"
    echo "https_proxy = ${https_proxy:-未设置}"
    echo "all_proxy   = ${all_proxy:-未设置}"
    echo "no_proxy    = ${no_proxy:-未设置}"
}
```

使用：`proxy_on` / `proxy_off` / `proxy_status`

**为什么用函数而不是写死 export？** 把 `proxy_on`/`proxy_off` 定义为函数（也写在 `~/.bashrc` 里），意味着终端启动时只定义函数但不开启代理。你需要代理的时候手动敲 `proxy_on`（即时生效，仅当前终端），不需要时 `proxy_off` 关掉。这样比永久 export 灵活得多——本地开发不污染网络，需要翻墙时一键开启。

**`source ~/.bashrc` 是干什么的？** 修改 `~/.bashrc` 后，当前已打开的终端不会自动重新读取它。`source` 命令就是让当前终端立刻重新执行一遍 `~/.bashrc`，不用关掉重开。

---

## 3. Docker 代理

Docker 不走 proxychains4，因为 `docker pull` 本质上是通过 socket 向 Docker daemon 发送指令，实际的网络连接是 daemon 进程发出的，不受命令行 proxychains 影响。需要单独配置 Docker 守护进程的代理。

### 3.1 Docker Daemon 代理（拉镜像时走代理）

**先了解 `/etc/systemd/system/docker.service.d/`：** Docker 通过 systemd 管理。`docker.service.d/` 是 systemd 的 "drop-in" 目录——你不需要修改 Docker 原生的 service 文件，只需在这里放一个 `.conf` 文件，systemd 会自动把其中的配置"覆盖/追加"到 Docker 的主 service 配置上。这样升级 Docker 不会覆盖你的代理配置。

```bash
# 创建配置目录
sudo mkdir -p /etc/systemd/system/docker.service.d

# 创建代理配置文件
sudo vim /etc/systemd/system/docker.service.d/proxy.conf
```

```ini
[Service]
Environment="HTTP_PROXY=http://192.168.1.100:7890"
Environment="HTTPS_PROXY=http://192.168.1.100:7890"
Environment="NO_PROXY=localhost,127.0.0.1,::1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12"
```

应用和验证：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl show docker --property Environment   # 验证生效
```

### 3.2 容器内代理（容器里的网络请求走代理）

**方式一：docker run 时设置环境变量**

```bash
docker run -e http_proxy="http://192.168.1.100:7890" \
           -e https_proxy="http://192.168.1.100:7890" \
           your-image
```

**方式二：全局配置（所有容器自动注入）**

**先了解 `~/.docker/config.json`：** Docker CLI 的客户端配置文件，存储镜像仓库认证、代理配置等。这里设置的代理会被 Docker CLI 在 `docker run`/`docker create` 时自动注入到容器中，省去每次手写 `-e`。

编辑 `~/.docker/config.json`：

```json
{
  "proxies": {
    "default": {
      "httpProxy": "http://192.168.1.100:7890",
      "httpsProxy": "http://192.168.1.100:7890",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

### 3.3 docker build 时的代理（构建时下载依赖）

```bash
docker build --build-arg http_proxy="http://192.168.1.100:7890" \
             --build-arg https_proxy="http://192.168.1.100:7890" \
             -t my-image .
```

---

## 4. Go 代理

Go 编译的程序不走 proxychains4（Go 是静态编译，用不了 LD_PRELOAD）。Go 有自己的一套代理体系。

### 4.1 模块代理（go get / go mod download）

```bash
# Go 模块代理（国内常用）
export GOPROXY="https://goproxy.cn,direct"

# 带私仓的情况
export GOPROXY="https://goproxy.cn,https://proxy.golang.org,direct"
export GOPRIVATE="gitlab.mycompany.com,github.com/myorg"

# 不走代理的模块（私仓）
export GONOSUMDB="gitlab.mycompany.com"
export GONOSUMCHECK="gitlab.mycompany.com"
```

### 4.2 Go 程序本身发出的 HTTP 请求

Go 标准库的 `net/http` 也认环境变量（如果代码里用了 `http.ProxyFromEnvironment`，这是默认行为）：

```bash
export http_proxy="http://192.168.1.100:7890"
export https_proxy="http://192.168.1.100:7890"
```

所以如果你自己写的 Go 程序或第三方工具用了 `net/http` 并保持默认 transport，设置环境变量就能走代理。

### 4.3 强制 Go 二进制走代理

如果某个 Go 编译的工具需要走代理但它不走环境变量，可以用 **redsocks + iptables**（见第 8 节），这是最彻底的方案。

---

## 5. Git 代理

**先了解 Git 配置的层级：** `git config --global` 写入 `~/.gitconfig`，对当前用户的所有仓库生效（最常用）。还有 `--system`（`/etc/gitconfig`，所有用户）和 `--local`（当前仓库的 `.git/config`）。

```bash
# HTTP/HTTPS 协议
git config --global http.proxy http://192.168.1.100:7890
git config --global https.proxy http://192.168.1.100:7890

# SOCKS5 代理
git config --global http.proxy socks5://192.168.1.100:7891
git config --global https.proxy socks5://192.168.1.100:7891

# SSH 协议（通过 SSH config）
# ~/.ssh/config 是 SSH 客户端的用户级配置文件，每次执行 ssh 命令时都会读取
# ProxyCommand 告诉 SSH：不要直连目标，而是通过指定的命令（这里是 nc）来中转连接
# ~/.ssh/config
Host github.com
    ProxyCommand nc -X 5 -x 192.168.1.100:7891 %h %p
    # 或使用 proxychains: ProxyCommand proxychains4 nc %h %p

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy

# 查看当前配置
git config --global --get-regexp proxy
```

**注意**：Git SSH 协议（`git@github.com:xxx`）不走 `http.proxy`，需要在 SSH config 里设置 ProxyCommand。

---

## 6. APT / Yum 包管理器代理

### 6.1 APT（Debian/Ubuntu）

**先了解 `/etc/apt/apt.conf.d/`：** APT 的主配置文件是 `/etc/apt/apt.conf`，但最佳实践是在 `apt.conf.d/` 目录下放独立的小配置文件。APT 按文件名数字顺序读取，`95proxy` 的 `95` 只是约定俗成（确保最后加载，优先级最高）。你也可以叫 `proxy.conf`，效果一样。

**方式一：配置文件**

```bash
sudo vim /etc/apt/apt.conf.d/95proxy
```

```
Acquire::http::Proxy "http://192.168.1.100:7890";
Acquire::https::Proxy "http://192.168.1.100:7890";
```

**方式二：环境变量**（需要保留环境变量到 sudo）

```bash
sudo -E apt update    # -E 保留当前环境变量
```

```bash
export http_proxy="http://192.168.1.100:7890"
sudo -E apt update
```

### 6.2 Yum / DNF（RHEL/CentOS/Fedora）

```bash
sudo vim /etc/yum.conf
```

```
proxy=http://192.168.1.100:7890
```

或对单个 repo 设置（`/etc/yum.repos.d/xxx.repo`）：

```
[repo-name]
proxy=http://192.168.1.100:7890
```

DNF 也认环境变量，同样需要 `sudo -E` 传递。

---

## 7. 桌面环境代理（GUI 程序）

### 7.1 GNOME

```bash
# 系统设置 -> 网络 -> 代理
# 或命令行：
gsettings set org.gnome.system.proxy mode 'manual'
gsettings set org.gnome.system.proxy.http host '192.168.1.100'
gsettings set org.gnome.system.proxy.http port 7890
gsettings set org.gnome.system.proxy.socks host '192.168.1.100'
gsettings set org.gnome.system.proxy.socks port 7891

# 关闭
gsettings set org.gnome.system.proxy mode 'none'
```

### 7.2 KDE

系统设置 -> 网络设置 -> 代理，或编辑 `~/.config/kioslaverc`。

### 7.3 通用 GUI 程序

多数 GUI 程序不读 shell 环境变量（因为从桌面启动，不经过 shell）。需要：
- DE 系统代理设置（如上）
- 或程序自身的代理配置（如 Firefox 的 Settings -> Network Settings）

---

## 8. 终极方案：透明代理

当以上所有方法都不适用时，用透明代理。原理是用 iptables/nftables 把所有流量重定向到代理服务器，对应用程序完全透明。

### 8.1 redsocks + iptables（SOCKS 透明代理）

```bash
# 1. 安装 redsocks
sudo apt install redsocks

# 2. 配置 /etc/redsocks.conf
```

```conf
redsocks {
    local_ip = 127.0.0.1;
    local_port = 12345;       # iptables 把流量转到这个端口
    ip = 192.168.1.100;       # 上游代理 IP
    port = 7891;              # 上游代理端口
    type = socks5;
}
```

```bash
# 3. 添加 iptables 规则（将 TCP 流量转到 redsocks）
sudo iptables -t nat -N REDSOCKS
sudo iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
sudo iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
sudo iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
sudo iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
sudo iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12345
sudo iptables -t nat -A OUTPUT -p tcp -j REDSOCKS

# 4. 启动 redsocks
sudo systemctl start redsocks

# 5. 清理规则（关闭透明代理）
sudo iptables -t nat -F REDSOCKS
sudo iptables -t nat -D OUTPUT -p tcp -j REDSOCKS
```

### 8.2 tun2socks（全协议透明代理）

创建虚拟网卡，把所有流量（包括 UDP）导入 SOCKS 代理。比 redsocks 更彻底（支持 UDP）。常用工具有 tun2socks、badvpn-tun2socks。

---

## 9. 各种方式对比总结

| 方式 | 影响范围 | 持久性 | 是否影响 Docker | 是否影响 Go | 是否影响 GUI |
|------|----------|--------|----------------|-------------|-------------|
| `export http_proxy` | 当前终端 | 关终端即失效 | 否 | 部分（net/http） | 否（桌面启动不走shell） |
| 写入 `~/.bashrc` | 用户所有终端 | 永久 | 否 | 部分 | 否 |
| `/etc/environment` | 所有用户 | 永久 | 否 | 部分 | 否 |
| proxychains4 | 单个命令 | 按需 | 否 | 否 | 可以（`proxychains firefox`） |
| Docker daemon 代理 | Docker pull | 永久 | 是 | 不适用 | 不适用 |
| Git 配置 | Git | 永久 | 不适用 | 不适用 | 不适用 |
| DE 系统代理 | GUI 程序 | 永久 | 不适用 | 不适用 | 是 |
| redsocks + iptables | 全局网络 | 重启失效 | 是 | 是 | 是 |
| tun2socks | 全局网络 | 重启失效 | 是 | 是 | 是 |

---

## 10. 快速验证代理是否生效

```bash
# 检查当前环境变量
env | grep -i proxy

# 测试 HTTP(S) 请求
curl -v https://www.google.com    # 看输出中是否经过代理
curl https://httpbin.org/ip        # 查看出口 IP
curl https://myip.ipip.net         # 同上

# 测试代理是否可达
nc -zv 192.168.1.100 7890          # TCP 端口是否通
curl -x http://192.168.1.100:7890 https://www.google.com   # 直接指定代理测试

# 测试当前 IP 归属地
curl cip.cc
```

---

## 11. 实战场景速查

| 场景 | 推荐方案 |
|------|----------|
| 命令行临时用代理 | `export` 环境变量（一次性） |
| 命令行长期用代理 | 写入 `~/.bashrc` + `proxy_off` 函数 |
| 某个不支持代理的工具 | `proxychains4` |
| Docker 拉镜像 | Docker daemon systemd 代理 |
| Docker 容器内请求外网 | `docker run -e` 或 `~/.docker/config.json` |
| Go 下载模块 | `GOPROXY` 环境变量 |
| Go 编译的二进制需要代理 | 环境变量（如果程序用了 net/http），否则透明代理 |
| Git clone | `git config http.proxy` 或 SSH ProxyCommand |
| APT 装包 | `/etc/apt/apt.conf.d/` 配置文件或 `sudo -E` |
| GUI 程序 | DE 系统代理设置 |
| 虚拟机用物理机代理 | proxychains4 + 物理机 IP（如文章开头图示） |
| 所有方法都无效 | redsocks + iptables 透明代理 |
