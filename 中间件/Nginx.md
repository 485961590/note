# Nginx

> Nginx 是高性能 HTTP 和反向代理服务器，并发能力强，内存占用低。既可以做 Web 服务器，也可以做反向代理、负载均衡。配置文件简洁直观。

---

## 查看发行版信息

```bash
cat /etc/os-release          # 推荐，所有发行版通用
lsb_release -a               # 需要安装 lsb-release 包
hostnamectl                  # systemd 系统可用，含内核版本
```

**发行版判断速查：**

| 家族 | 发行版 | 包管理器 | 服务名 |
|------|--------|----------|--------|
| Debian 系 | Ubuntu, Debian, **Kali Linux** | apt | `nginx` |
| RHEL 系 | CentOS 7/8, RHEL, Rocky, Alma, Fedora | dnf / yum | `nginx` |

> Nginx 在两大发行版家族中包名和服务名一致，都是 `nginx`。但默认仓库版本可能较老，建议用官方源安装最新版。
>
> Kali Linux 基于 Debian，所有命令与 Ubuntu/Debian 一致。

---

## 安装

### 方式一：系统默认仓库（版本较老，但简单）

**Ubuntu / Debian / Kali：**

```bash
sudo apt update
sudo apt install nginx
```

**CentOS 7（yum）：**

```bash
sudo yum install epel-release       # Nginx 在 EPEL 仓库
sudo yum install nginx
```

**CentOS 8+ / RHEL 8+ / Rocky / Fedora（dnf）：**

```bash
sudo dnf install nginx              # 通常自带，没有则先装 epel-release
```

### 方式二：Nginx 官方仓库（推荐，版本最新）

**Debian / Ubuntu / Kali：**

```bash
# 安装依赖
sudo apt install curl gnupg2 ca-certificates lsb-release

# 添加官方签名密钥
curl -fsSL https://nginx.org/keys/nginx_signing.key | sudo gpg --dearmor -o /usr/share/keyrings/nginx-archive-keyring.gpg

# 添加官方 apt 源
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
# Ubuntu 换成 Debian/Kali 时把 ubuntu 换成 debian

# 设置优先级
echo -e "Package: *\nPin: origin nginx.org\nPin: release o=nginx\nPin-Priority: 900" | sudo tee /etc/apt/preferences.d/99nginx

sudo apt update
sudo apt install nginx
```

**CentOS / RHEL / Rocky（dnf/yum）：**

```bash
# 创建官方源文件
sudo tee /etc/yum.repos.d/nginx.repo <<EOF
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/\$releasever/\$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
EOF

sudo dnf install nginx        # CentOS 8+ / RHEL 8+ / Rocky
# 或
sudo yum install nginx        # CentOS 7
```

---

## 服务管理

| 操作 | 命令 |
|------|------|
| 启动 | `sudo systemctl start nginx` |
| 停止 | `sudo systemctl stop nginx` |
| 重启 | `sudo systemctl restart nginx` |
| 重载配置（不中断连接） | `sudo systemctl reload nginx` |
| 开机自启 | `sudo systemctl enable nginx` |
| 禁用自启 | `sudo systemctl disable nginx` |
| 查看状态 | `sudo systemctl status nginx` |
| 测试配置文件语法 | `sudo nginx -t` |

> 注意：`reload` 和 `restart` 的区别 —— `reload` 平滑重载配置，不中断现有连接；`restart` 会断开所有连接再启动。改配置后优先用 `reload`。

---

## 默认目录

Nginx 在两大家族的目录结构基本一致：

| 内容 | 路径 |
|------|------|
| 主配置文件 | `/etc/nginx/nginx.conf` |
| 额外配置目录（server block） | `/etc/nginx/conf.d/` |
| 站点配置目录 | `/etc/nginx/sites-available/`（仅部分发行版） |
| 日志目录 | `/var/log/nginx/` |
| 访问日志 | `/var/log/nginx/access.log` |
| 错误日志 | `/var/log/nginx/error.log` |
| 默认网站根目录 | `/usr/share/nginx/html/` |
| 常用自定义根目录 | `/var/www/`（需手动创建） |
| 进程用户 | `nginx` 或 `www-data`（取决于发行版） |
| PID 文件 | `/var/run/nginx.pid` |

查看运行用户：

```bash
grep '^user' /etc/nginx/nginx.conf
```

---

## 配置文件结构

```
/etc/nginx/
├── nginx.conf                 # 主配置，入口
├── conf.d/                    # 放 server block，所有 .conf 自动加载
│   └── example.conf
├── sites-available/           # 可用站点（Debian/Ubuntu 习惯，非必须）
├── sites-enabled/             # 已启用站点 → sites-available 的符号链接
├── snippets/                  # 可复用的配置片段
├── fastcgi.conf               # FastCGI 通用参数
├── mime.types                 # MIME 类型映射
└── modules/                   # 动态模块目录
```

> 核心思想：`nginx.conf` 通过 `include /etc/nginx/conf.d/*.conf;` 自动加载，新站点在 `conf.d/` 下创建 `.conf` 文件即可。

---

## Server Block 配置（类似 Apache 虚拟主机）

### 静态网站

```bash
sudo vim /etc/nginx/conf.d/example.conf
```

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    root /var/www/example;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ =404;       # 文件不存在返回 404
    }

    # 日志（可选，默认用主配置的日志）
    access_log /var/log/nginx/example-access.log;
    error_log  /var/log/nginx/example-error.log;
}
```

```bash
sudo mkdir -p /var/www/example
echo "Hello" | sudo tee /var/www/example/index.html
sudo nginx -t && sudo systemctl reload nginx
```

### 反向代理

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;                  # 后端地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HTTPS + HTTP 跳转

```nginx
# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 主站
server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate     /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    root /var/www/example;
    index index.html;
}
```

---

## 常用命令速查

```bash
# 语法检查
sudo nginx -t

# 测试配置并显示详情
sudo nginx -T                              # 打印完整配置（含 include 展开）

# 查看版本和编译参数
nginx -v                                    # 简短版本
nginx -V                                    # 详细版本 + 编译参数

# 重载配置
sudo systemctl reload nginx
# 或直接
sudo nginx -s reload

# 优雅停止（等待请求处理完）
sudo nginx -s quit

# 快速停止
sudo nginx -s stop

# 重新打开日志文件（logrotate 用）
sudo nginx -s reopen

# 查看访问日志（实时）
sudo tail -f /var/log/nginx/access.log

# 查看错误日志
sudo tail -f /var/log/nginx/error.log

# 查看已加载的模块
nginx -V 2>&1 | grep -o '--with-\S*'

# 检查某个配置文件是否被加载
grep -r "include" /etc/nginx/nginx.conf
```

---

## 防火墙

```bash
# UFW（Ubuntu/Debian 常用）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 'Nginx Full'               # 同时开放 80+443（UFW 预置 profile）

# firewalld（CentOS/RHEL 常用）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 查看 UFW 预置的 Nginx profile
sudo ufw app list | grep -i nginx
```

---

## 常见问题

**403 Forbidden — 通常是权限问题：**

```bash
# 1. 确认 nginx 运行用户
ps aux | grep nginx

# 2. 确保网站目录对运行用户可读
sudo chown -R nginx:nginx /var/www/example      # RHEL 系
sudo chown -R www-data:www-data /var/www/example # Debian 系

# 3. 确保父目录有 x 权限
sudo chmod o+x /var /var/www
```

**端口被占用：**

```bash
sudo ss -tlnp | grep :80
# 如果 Apache 占用了 80，先停掉
sudo systemctl stop apache2   # 或 httpd
```

**修改上传文件大小限制：**

```nginx
# 在 http, server 或 location 块中添加
client_max_body_size 100M;
```

---

## Nginx vs Apache 选型参考

| 场景 | 推荐 | 理由 |
|------|------|------|
| 高并发静态文件 | Nginx | 事件驱动，内存占用低 |
| 共享主机（用户需 .htaccess） | Apache | .htaccess 让用户无需重启就能覆写配置 |
| 反向代理 / 负载均衡 | Nginx | 原生支持，配置简洁 |
| 动态内容（PHP） | 两者都行 | Nginx + PHP-FPM 或 Apache + mod_php |
| 新手入门 | Nginx | 配置文件比 Apache 更直观 |
