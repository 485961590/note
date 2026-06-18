## 目录结构
```
/
├── bin/          # 基本命令（所有用户可用）
├── boot/         # 启动文件
├── dev/          # 设备文件
├── etc/          # 系统配置文件
├── home/         # 用户目录
├── kali-arm/     # Kali ARM 相关（如果安装）
├── lib/          # 系统库文件
├── media/        # 可移动媒体挂载点
├── mnt/          # 临时挂载点
├── opt/          # 第三方软件
├── proc/         # 进程和内核信息
├── root/         # root用户目录
├── run/          # 运行时数据
├── sbin/         # 系统管理命令
├── srv/          # 服务数据
├── sys/          # 系统信息
├── tmp/          # 临时文件
├── usr/          # 用户程序和数据
└── var/          # 可变数据
```
## 重要路径速查表
| 路径                     | 用途              | 示例                             |
| ---------------------- | --------------- | ------------------------------ |
| `/usr/bin/`            | 大部分渗透工具         | `nmap`,`sqlmap`,`msfconsole`   |
| `/usr/share/`          | 工具数据文件          | 字典、脚本、模块                       |
| `/etc/`                | 工具配置            | `proxychains.conf`,`nmap.conf` |
| `~/.cache/`            | 用户缓存            | `msf`缓存,`nuclei`缓存             |
| `~/.local/share/`      | 用户数据            | `nuclei-templates`             |
| `/tmp/`                | 临时文件            | 扫描结果、下载文件                      |
| `/usr/bin/nmap`        | Nmap            | 端口扫描器                          |
| `/usr/bin/sqlmap`      | SQLMap          | SQL注入工具                        |
| `/usr/bin/metasploit`  | Metasploit      | 渗透框架                           |
| `/usr/bin/hydra`       | Hydra           | 密码爆破                           |
| `/usr/bin/john`        | John the Ripper | 密码破解                           |
| `/usr/bin/hashcat`     | Hashcat         | GPU密码破解                        |
| `/usr/bin/aircrack-ng` | Aircrack-ng     | WiFi破解                         |
| `/usr/bin/wireshark`   | Wireshark       | 流量分析                           |
| `/usr/bin/nessus`      | Nessus          | 漏洞扫描                           |
| `/usr/bin/nikto`       | Nikto           | Web扫描                          |
| `/usr/bin/gobuster`    | GoBuster        | 目录爆破                           |
| `/usr/bin/ffuf`        | FFuF            | Web模糊测试                        |
## Metasploit 框架
```
# Metasploit 主要路径
/usr/share/metasploit-framework/  # 主目录
├── msfconsole                    # 控制台
├── modules/                      # 所有模块
│   ├── exploits/                 # 漏洞利用
│   ├── payloads/                 # 载荷
│   ├── auxiliary/                # 辅助模块
│   └── post/                     # 后渗透模块
├── tools/                        # 工具脚本
├── data/                         # 数据文件
└── scripts/                      # 自定义脚本
```
## 配置文件和脚本

### 1. 系统配置文件

| 路径 | 用途 | 修改示例 |
|---|---|---|
|`/etc/apt/sources.list`|软件源|`sudo nano /etc/apt/sources.list`|
|`/etc/proxychains4.conf`|代理链|`proxychains nmap`|
|`/etc/hosts`|主机名解析|`sudo nano /etc/hosts`|
|`/etc/resolv.conf`|DNS设置|设置 DNS 服务器|
|`/etc/ssh/sshd_config`|SSH 服务配置|`sudo systemctl restart ssh`|
|`/etc/nmap/nmap.conf`|Nmap 配置|自定义扫描参数|
|`/etc/wireshark/`|Wireshark 配置|捕获设置|

### 2. 用户配置文件

```
~/.bashrc                         # Bash配置
~/.zshrc                          # Zsh配置（如果安装）
~/.profile                        # 用户环境变量
~/.config/                        # 应用配置目录
~/.local/share/                   # 用户数据
~/.cache/                         # 缓存文件
```

### 3. 工具特定配置

```
~/.msf4/                          # Metasploit配置
~/.sqlmap/                        # SQLMap配置
~/.nmap/                          # Nmap脚本和数据
~/.wireshark/                     # Wireshark配置
~/.john/                          # John配置
~/.hashcat/                       # Hashcat配置
~/.ssh/                           # SSH密钥
~/.gnupg/                         # GPG密钥
```

## 数据和资源文件

### 1. 字典和单词列表

```
/usr/share/wordlists/             # 主要字典目录
├── rockyou.txt                   # 常用密码字典
├── dirb/                         # Dirb字典
├── dirbuster/                    # Dirbuster字典
├── wfuzz/                        # Wfuzz字典
├── seclists/                     # SecLists
└── nmap/                         # Nmap字典

# SecLists 详细结构
/usr/share/seclists/
├── Discovery/                    # 发现类
├── Fuzzing/                      # 模糊测试
├── Passwords/                    # 密码字典
├── Usernames/                    # 用户名字典
└── Web-Content/                  # Web内容
```

### 2. 工具脚本和模块

```
/usr/share/nmap/scripts/          # Nmap脚本
/usr/share/sqlmap/tamper/         # SQLMap编码脚本
/usr/share/webshells/             # WebShell
/usr/share/beef-xss/              # BeEF框架
/usr/share/set/                   # Social-Engineer Toolkit
/usr/share/responder/             # Responder
```
## 安全和权限

### 1. 用户和权限
```
/etc/passwd                       # 用户账户
/etc/shadow                       # 密码哈希
/etc/group                        # 用户组
/etc/sudoers                      # Sudo权限
/var/log/auth.log                 # 认证日志
```
### 2. 防火墙和网络
```
/etc/iptables/                    # iptables规则
/etc/nftables.conf                # nftables配置
/etc/network/interfaces           # 网络接口
/etc/systemd/network/             # systemd网
```
## 临时文件处理
```
# 清理临时文件
sudo rm -rf /tmp/*
sudo apt clean
sudo apt autoclean

# 但保留重要数据
mkdir -p ~/scans/ ~/tools/ ~/reports/
```
## 符号链接常见路径
```
# 查看实际路径
ls -l /bin/sh      # 通常指向 bash 或 dash
ls -l /usr/bin/python  # 指向 python3
ls -l /etc/alternatives/  # 替代系统
```
