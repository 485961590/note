Proxychains 是一个代理链工具，它的核心作用是**强制任何应用程序的网络流量通过代理服务器**，即使这些程序本身不支持代理设置。
## 安装：
```bash
Ubuntu/Debian 系统
# 更新软件源
sudo apt update
# 安装proxychains
sudo apt install proxychains4

CentOS/RHEL/Fedora 系统
# CentOS/RHEL 需要先安装epel源
sudo yum install epel-release
sudo yum install proxychains-ng
# Fedora直接安装
sudo dnf install proxychains-ng

Arch Linux 系统
sudo pacman -S proxychains-ng

macOS 系统
# 使用Homebrew安装
brew install proxychains-ng

验证安装
# 检查是否安装成功
proxychains4 --version
# 或
proxychains --version
```
## 配置
- **全局配置**：`/etc/proxychains4.conf`
- **用户配置**：`~/.proxychains/proxychains.conf`（需要手动创建目录）
编辑配置文件：
```bash
sudo vim /etc/proxychains4.conf
```
配置文件中代理模式：
```bash
# 严格模式：严格按照顺序使用代理，一个失败则整体失败
strict_chain

# 动态模式：按顺序使用代理，跳过无效代理（推荐）
dynamic_chain

# 随机模式：随机选择列表中的代理
random_chain
```
**配置代理服务器列表：**
```bash
# 找到 [ProxyList] 部分，添加你的代理
[ProxyList]
# 格式：类型 IP地址 端口号 [用户名 密码]
socks5 127.0.0.1 1080
socks4 127.0.0.1 1081
http 127.0.0.1 3128
https 127.0.0.1 3129
```
可选配置：
```bash
# 启用DNS代理（防止DNS泄露）
proxy_dns

# 设置超时时间（毫秒）
tcp_read_time_out 15000
tcp_connect_time_out 8000
```
## 使用方法
```bash
# 基本语法
proxychains4 <要执行的命令>
```
## 示例：
命令行工具代理:
```bash
# curl命令通过代理
proxychains4 curl https://www.google.com

# wget下载文件
proxychains4 wget https://example.com/file.zip

# SSH连接（通过代理）
proxychains4 ssh user@server.com

# ping命令（如果代理支持ICMP）
proxychains4 ping google.com
```
图形界面程序代理:
```bash
# 浏览器代理
proxychains4 firefox

# 其他应用程序
proxychains4 thunderbird
proxychains4 telegram-desktop
```
## **虚拟机无法访问外网，利用物理机的梯子搭配虚拟机proxychain实现本地代理转发访问外网！**
- 开启物理机梯子：
![](file-20260402005806768.png)
- 找到物理机IP地址
![](file-20260402005806769.png)
**代理地址是：IPv4:端口**
- 编辑/etc/proxychains4.conf
- s'sss去除dynamic_chain前#号proxychains4会按顺序使用代理，跳过无效代理。
![](file-20260402005806770.png)
![](file-20260402005806770%201.png)
- 使用
```bash
proxychains4 <要执行的命令>
```

## 环境变量代理（最常用）
- 1. **临时设置**
```bash
# HTTP/HTTPS 代理
export http_proxy="http://192.168.16.113:7890"
export https_proxy="http://192.168.16.113:7890"
export ftp_proxy="http://192.168.16.113:7890"
export all_proxy="socks5://192.168.16.113:7891"

# 不使用代理的地址（逗号分隔）
export no_proxy="localhost,127.0.0.1,192.168.*"

# 大写形式（某些程序需要）
export HTTP_PROXY="http://192.168.16.113:7890"
export HTTPS_PROXY="http://192.168.16.113:7890"
```
- 2. **永久设置**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export http_proxy="http://192.168.16.113:7890"' >> ~/.bashrc
echo 'export https_proxy="http://192.168.16.113:7890"' >> ~/.bashrc
source ~/.bashrc
```
- 3. **为特定程序设置**
```bash
# 仅对当前命令生效
http_proxy="http://192.168.16.113:7890" curl https://example.com
# 使用 env 命令
env http_proxy="http://192.168.16.113:7890" wget https://example.com
```

## 全局系统代理（/etc/environment）
```bash
# 编辑系统环境变量文件
sudo vim /etc/environment

# 添加以下内容
http_proxy="http://192.168.16.113:7890"
https_proxy="http://192.168.16.113:7890"
no_proxy="localhost,127.0.0.1"

# 重启生效
```

## Docker 代理配置
Docker 无法直接使用 proxychains，因为 Docker 守护进程需要访问网络来拉取镜像、运行容器等。让我详细介绍 Docker 的各种代理配置方法。
### Docker Daemon 代理配置（最重要）
**systemd 配置**
- **创建代理配置文件：**
```bash
# 创建配置目录
sudo mkdir -p /etc/systemd/system/docker.service.d
# 创建代理配置文件
sudo vim /etc/systemd/system/docker.service.d/proxy.conf
```
- **添加以下内容：**
```bash
[Service]
Environment="HTTP_PROXY=http://代理IP:代理端口"
Environment="HTTPS_PROXY=http://代理IP:代理端口"
Environment="NO_PROXY=localhost,127.0.0.1,::1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12"

# SOCKS5 代理（如果需要）
# Environment="ALL_PROXY=socks5://192.168.16.113:7891"
```
- **应用配置：**
```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload
# 重启 Docker 服务
sudo systemctl restart docker
# 验证配置是否生效
sudo systemctl show docker --property Environment
```