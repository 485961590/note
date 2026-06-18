# Apache HTTP Server

> Apache 是最老牌的开源 Web 服务器，稳定可靠，.htaccess 是它的独门利器。Nginx 崛起后它依然广泛用于共享主机和需要目录级配置覆写的场景。

---

## 查看发行版信息

```bash
cat /etc/os-release          # 推荐，所有发行版通用
lsb_release -a               # 需要安装 lsb-release 包
hostnamectl                  # systemd 系统可用，含内核版本
```

**发行版判断速查：**

| 家族 | 发行版 | 包管理器 | Apache 包名 | 服务名 |
|------|--------|----------|------------|--------|
| Debian 系 | Ubuntu, Debian, **Kali Linux** | apt | `apache2` | `apache2` |
| RHEL 系 | CentOS 7/8, RHEL, Rocky, Alma, Fedora | dnf / yum | `httpd` | `httpd` |

> Kali Linux 基于 Debian，所有命令与 Ubuntu/Debian 一致。

---

## 安装

### Ubuntu / Debian / Kali

```bash
sudo apt update
sudo apt install apache2

# 安装常用工具
sudo apt install apache2-utils          # 含 htpasswd 等工具
```

### CentOS 7（yum）

```bash
sudo yum install httpd
sudo yum install httpd-tools
```

### CentOS 8+ / RHEL 8+ / Rocky / Fedora（dnf）

```bash
sudo dnf install httpd
sudo dnf install httpd-tools
```

---

## 服务管理

| 操作 | Debian 系 (apt) | RHEL 系 (dnf/yum) |
|------|----------------|-------------------|
| 启动 | `sudo systemctl start apache2` | `sudo systemctl start httpd` |
| 停止 | `sudo systemctl stop apache2` | `sudo systemctl stop httpd` |
| 重启 | `sudo systemctl restart apache2` | `sudo systemctl restart httpd` |
| 重载配置（不中断服务） | `sudo systemctl reload apache2` | `sudo systemctl reload httpd` |
| 开机自启 | `sudo systemctl enable apache2` | `sudo systemctl enable httpd` |
| 禁用自启 | `sudo systemctl disable apache2` | `sudo systemctl disable httpd` |
| 查看状态 | `sudo systemctl status apache2` | `sudo systemctl status httpd` |
| 测试配置文件语法 | `sudo apache2ctl configtest` | `sudo httpd -t` |

---

## 默认目录

| 内容 | Debian 系 | RHEL 系 |
|------|----------|---------|
| 主配置文件 | `/etc/apache2/apache2.conf` | `/etc/httpd/conf/httpd.conf` |
| 额外配置目录 | `/etc/apache2/conf-available/` | `/etc/httpd/conf.d/` |
| 虚拟主机配置 | `/etc/apache2/sites-available/` | `/etc/httpd/conf.d/` |
| 启用虚拟主机的符号链接 | `/etc/apache2/sites-enabled/` | 无此机制，直接放 `conf.d/` |
| 模块配置 | `/etc/apache2/mods-available/` | `/etc/httpd/conf.modules.d/` |
| 日志目录 | `/var/log/apache2/` | `/var/log/httpd/` |
| 默认网站根目录 | `/var/www/html/` | `/var/www/html/` |
| 进程用户 | `www-data` | `apache` |

### Debian 系的 a2ensite / a2dissite 机制

```bash
# 创建一个虚拟主机配置后，用以下命令启用/禁用
sudo a2ensite example.com.conf       # 在 sites-enabled/ 创建符号链接
sudo a2dissite example.com.conf      # 移除符号链接
sudo systemctl reload apache2        # 重载使生效

# 模块同理
sudo a2enmod rewrite                  # 启用 rewrite 模块
sudo a2dismod rewrite                 # 禁用
```

---

## 虚拟主机配置示例

### Debian 系

```bash
# 1. 创建配置文件
sudo vim /etc/apache2/sites-available/example.conf
```

```apache
<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com
    DocumentRoot /var/www/example

    <Directory /var/www/example>
        Options Indexes FollowSymLinks
        AllowOverride All              # 允许 .htaccess
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/example-error.log
    CustomLog ${APACHE_LOG_DIR}/example-access.log combined
</VirtualHost>
```

```bash
# 2. 创建网站目录
sudo mkdir -p /var/www/example

# 3. 启用站点
sudo a2ensite example.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### RHEL 系

```bash
# 直接在 conf.d/ 下创建，不需要 a2ensite
sudo vim /etc/httpd/conf.d/example.conf
```

配置内容同上，但日志路径用绝对路径：

```apache
    ErrorLog /var/log/httpd/example-error.log
    CustomLog /var/log/httpd/example-access.log combined
```

```bash
sudo httpd -t                         # 语法检查
sudo systemctl reload httpd
```

---

## SSL/HTTPS 配置

```bash
# Debian 系：启用 SSL 模块和站点
sudo a2enmod ssl
sudo a2ensite default-ssl.conf
sudo systemctl reload apache2

# RHEL 系：安装 mod_ssl
sudo dnf install mod_ssl
sudo systemctl reload httpd
```

---

## 常用命令速查

```bash
# 语法检查
sudo apache2ctl configtest           # Debian 系
sudo httpd -t                        # RHEL 系

# 查看已加载模块
sudo apache2ctl -M                   # Debian 系
sudo httpd -M                        # RHEL 系

# 查看虚拟主机列表
sudo apache2ctl -S                   # Debian 系
sudo httpd -S                        # RHEL 系

# 查看版本
apache2 -v                           # Debian 系
httpd -v                             # RHEL 系

# 查看编译参数
apache2 -V                           # Debian 系
httpd -V                             # RHEL 系

# 不重启只重载配置
sudo systemctl reload apache2        # Debian 系
sudo systemctl reload httpd          # RHEL 系

# 完全停止再启动（配置有大改动时）
sudo systemctl restart apache2       # Debian 系
sudo systemctl restart httpd         # RHEL 系

# 查看访问日志（实时跟踪）
sudo tail -f /var/log/apache2/access.log      # Debian 系
sudo tail -f /var/log/httpd/access_log        # RHEL 系

# 查看错误日志
sudo tail -f /var/log/apache2/error.log       # Debian 系
sudo tail -f /var/log/httpd/error_log         # RHEL 系

# 生成 htpasswd 密码文件
sudo htpasswd -c /etc/apache2/.htpasswd username    # Debian 系
sudo htpasswd -c /etc/httpd/.htpasswd username      # RHEL 系

# 压力测试（ab = Apache Benchmark）
ab -n 1000 -c 100 http://localhost/
```

---

## 防火墙

```bash
# UFW（Ubuntu/Debian 常用）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# firewalld（CentOS/RHEL 常用）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# iptables（通用）
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

---

## 配置文件关系图（Debian 系）

```
/etc/apache2/
├── apache2.conf              # 主配置，入口文件
├── conf-available/           # 通用额外配置
├── conf-enabled/             # 已启用的配置（符号链接）
├── mods-available/           # 可用模块
├── mods-enabled/             # 已启用模块（符号链接）
├── sites-available/          # 可用虚拟主机
│   ├── 000-default.conf      # 默认 HTTP 站点
│   └── default-ssl.conf      # 默认 HTTPS 站点
└── sites-enabled/            # 已启用虚拟主机（符号链接）
```

### 配置文件关系图（RHEL 系）

```
/etc/httpd/
├── conf/
│   └── httpd.conf            # 主配置文件
├── conf.d/                   # 所有额外配置，直接放 .conf 文件即生效
├── conf.modules.d/           # 模块加载配置
└── logs -> ../../var/log/httpd   # 日志符号链接
```
