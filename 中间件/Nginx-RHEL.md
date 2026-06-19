# Nginx（RHEL 系：CentOS / RHEL / Rocky / Alma / Fedora）

> Nginx 是高性能 HTTP 和反向代理服务器，事件驱动架构，内存占用低。RHEL 系中 Nginx 的配置结构简洁统一——只用 `conf.d/` 目录，没有 Debian 系系统包那种 `sites-available/`/`sites-enabled/` 约定。包名和服务名在所有发行版中都是 `nginx`。

适用发行版：CentOS 7/8+、RHEL 7/8/9+、Rocky Linux、AlmaLinux、Fedora。

---

## 1. 安装

### 方式一：系统默认仓库（版本较旧，但简单）

**CentOS 7（yum）：**

```bash
sudo yum install epel-release    # Nginx 在 EPEL 仓库中
sudo yum install nginx
```

**CentOS 8+ / RHEL 8+ / Rocky / Alma / Fedora（dnf）：**

```bash
sudo dnf install nginx           # 通常自带，没有则先装 epel-release
```

安装后需要手动启动并设置开机自启：

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

> RHEL 系安装后**不会自动启动**，需要手动操作。

### 方式二：Nginx 官方仓库（推荐，版本最新）

```bash
# 创建官方源文件
sudo tee /etc/yum.repos.d/nginx.repo <<'EOF'
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
EOF

# CentOS 8+ / RHEL 8+ / Rocky / Alma / Fedora
sudo dnf install nginx

# CentOS 7
sudo yum install nginx
```

> 官方包和 EPEL 包的主要区别：版本更新、进程用户是 `nginx`（EPEL 可能是 `www-data` 或 `nginx`）、没有 `sites-available/` 目录。

---

## 2. 配置文件地图

### 2.1 设计哲学：集中式 + 层级继承

Nginx 的配置哲学：
- **一个入口**：`nginx.conf` 是唯一的主配置文件，通过 `include` 指令加载其他文件
- **层级继承**：配置分为 `http {}` → `server {}` → `location {}` 三层，下级继承上级的设置，同名指令覆盖
- **一个 server 块 = 一个站点**：每个 `server {}` 块就是一个站点
- **RHEL 系只用 `conf.d/`**：没有 `sites-available/`/`sites-enabled/`，配置结构最简单

### 2.2 目录总览

| 路径 | 作用 |
|------|------|
| `/etc/nginx/nginx.conf` | **主配置入口**，通过 include 加载其他所有配置 |
| `/etc/nginx/conf.d/` | **站点配置目录**。放 `.conf` 文件即自动加载 |
| `/etc/nginx/mime.types` | MIME 类型映射表 |
| `/etc/nginx/fastcgi.conf` | FastCGI 通用参数（PHP-FPM 用） |
| `/var/log/nginx/` | 日志目录：`access.log`、`error.log` |
| `/usr/share/nginx/html/` | 默认网站根目录 |
| `/var/run/nginx.pid` | 主进程 PID 文件 |
| `/usr/lib64/nginx/modules/` | 动态模块目录 |

> RHEL 系没有 `sites-available/`、`sites-enabled/`、`snippets/` 目录。需要复用配置片段时，可以在 `conf.d/` 下创建独立文件然后 include。

### 2.3 nginx.conf 内部结构（逐块注释）

```
/etc/nginx/nginx.conf
│
├── user nginx;                        # 进程以哪个用户运行（官方包是 nginx）
├── worker_processes auto;             # 工作进程数，auto = 按 CPU 核数
├── error_log /var/log/nginx/error.log warn;
├── pid /var/run/nginx.pid;
│
├── events {                           # 连接处理模型
│       worker_connections 1024;       # 每个 worker 最大连接数
│   }
│
└── http {                             # HTTP 核心模块——所有网站配置都在这里面
    │
    ├── include /etc/nginx/mime.types; # MIME 类型映射
    ├── default_type application/octet-stream;
    │
    ├── log_format main '...';         # 日志格式定义
    ├── access_log /var/log/nginx/access.log main;
    │
    ├── sendfile on;                   # 高效文件传输
    ├── keepalive_timeout 65;          # 长连接超时
    │
    ├── include /etc/nginx/conf.d/*.conf;    ← 你的站点配置通过这行加载
    │
    └── server { ... }                  # 默认 server 块（欢迎页面）
    }
```

**关键理解**：`include /etc/nginx/conf.d/*.conf;` 这一行意味着你在 `conf.d/` 下创建的任何 `.conf` 文件都会被自动加载。RHEL 系只有这一个 include 路径，比 Debian 系更简单——没有 `sites-enabled/` 的歧义。

### 2.4 目录树全貌

```
/etc/nginx/
├── nginx.conf                 # 主配置
├── mime.types                 # MIME 类型
├── fastcgi.conf               # FastCGI 参数
├── fastcgi_params             # FastCGI 参数（备用）
├── scgi_params                # SCGI 参数
├── uwsgi_params               # uWSGI 参数
├── koi-utf                    # 字符集转换
├── koi-win
├── win-utf
│
├── conf.d/                    # 站点配置——唯一需要你操作的目录
│   └── default.conf           #   默认欢迎页面配置
│
├── default.d/                 # 默认站点配置片段
└── modules/ -> ../../usr/lib64/nginx/modules  # 动态模块符号链接
```

---

## 3. 运行一个项目需要配置哪些文件

### 3.1 从零到运行的步骤

| 步骤 | 你要做的事 | 说明 |
|------|-----------|------|
| 1 | 放网站文件 | 把你的 HTML/CSS/JS 放到 `/var/www/你的站点名/` |
| 2 | 写 Server Block 配置文件 | 创建 `/etc/nginx/conf.d/你的站点名.conf` |
| 3 | 检查语法 | `sudo nginx -t` |
| 4 | 重载配置 | `sudo systemctl reload nginx` |

> RHEL 系 Nginx 的部署流程是所有发行版中最简短的：写一个文件 + 两个命令即可。没有符号链接、没有模块启用步骤（Nginx 模块编译在内核中）。

### 3.2 Server Block 配置文件内容（你需要写的 .conf）

创建 `/etc/nginx/conf.d/mysite.conf`：

#### 场景一：纯静态网站

```nginx
server {
    # 监听 80 端口
    listen 80;
    # IPv6 也需要的话加一行 listen [::]:80;

    # 这个站点响应哪个域名
    server_name mysite.example.com www.mysite.example.com;

    # 网站文件在哪
    root /var/www/mysite;
    # 默认首页（按顺序查找）
    index index.html index.htm;

    # 处理请求
    location / {
        try_files $uri $uri/ =404;  # 先找文件，再找目录，都找不到返回 404
    }

    # 日志
    access_log /var/log/nginx/mysite-access.log;
    error_log  /var/log/nginx/mysite-error.log;
}
```

**各指令说明：**

| 指令 | 作用 |
|------|------|
| `listen 80` | 监听 80 端口 |
| `server_name` | Nginx 根据请求头中的 Host 匹配对应的 server 块 |
| `root` | 网站文件的根目录，Nginx 会把 URL 路径拼接在 root 后面去查找文件 |
| `index` | 访问目录时默认返回的文件，按顺序查找 |
| `try_files` | 按顺序尝试查找文件：`$uri` → `$uri/` → `=404` |
| `location /` | 匹配所有以 `/` 开头的 URL |

#### 场景二：反向代理

```nginx
server {
    listen 80;
    server_name mysite.example.com;

    # 静态文件让 Nginx 直接处理，不经过后端（性能更好）
    location /static/ {
        alias /var/www/mysite/static/;
        expires 30d;                      # 浏览器缓存 30 天
    }

    # 其他所有请求转发给后端应用
    location / {
        proxy_pass http://127.0.0.1:8000;         # 后端地址
        proxy_set_header Host $host;               # 传递原始域名
        proxy_set_header X-Real-IP $remote_addr;    # 传递真实客户端 IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme; # 传递原始协议（http/https）
    }

    access_log /var/log/nginx/mysite-access.log;
    error_log  /var/log/nginx/mysite-error.log;
}
```

**反向代理关键指令：**

| 指令 | 作用 |
|------|------|
| `proxy_pass` | 把请求转发到哪个地址 |
| `proxy_set_header Host` | 传递客户端请求的域名给后端 |
| `proxy_set_header X-Real-IP` | 传递客户端真实 IP |
| `proxy_set_header X-Forwarded-For` | 代理链，每经过一层代理就追加一个 IP |
| `proxy_set_header X-Forwarded-Proto` | 告知后端前端用的协议（http 还是 https） |

### 3.3 完整的部署命令序列

```bash
# 1. 放网站文件（注意 SELinux 上下文，见第 6 节）
sudo mkdir -p /var/www/mysite
echo "<h1>Hello</h1>" | sudo tee /var/www/mysite/index.html

# 2. 写 Server Block 配置
sudo vim /etc/nginx/conf.d/mysite.conf
# （粘贴上一节的配置内容）

# 3. 语法检查
sudo nginx -t

# 4. 重载配置
sudo systemctl reload nginx

# 5. 验证
curl -H "Host: mysite.example.com" http://127.0.0.1/

# 6. 如果用了反向代理，确认后端在运行
curl http://127.0.0.1:8000/
```

---

## 4. HTTPS 配置

### 4.1 创建 HTTPS Server Block

在 `/etc/nginx/conf.d/mysite.conf` 中添加：

```nginx
# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name mysite.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 主站
server {
    listen 443 ssl http2;
    server_name mysite.example.com;

    # SSL 证书（RHEL 系常用路径）
    ssl_certificate     /etc/pki/tls/certs/mysite.crt;
    ssl_certificate_key /etc/pki/tls/private/mysite.key;

    # SSL 安全策略
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS（强制浏览器使用 HTTPS）
    add_header Strict-Transport-Security "max-age=63072000" always;

    root /var/www/mysite;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    access_log /var/log/nginx/mysite-access.log;
    error_log  /var/log/nginx/mysite-error.log;
}
```

> RHEL 系中 SSL 证书通常放在 `/etc/pki/tls/certs/` 和 `/etc/pki/tls/private/`。

### 4.2 SSL 参数复用

RHEL 系没有内置 `snippets/` 目录，但你可以自建一个来复用 SSL 配置：

```bash
sudo mkdir -p /etc/nginx/snippets
```

创建 `/etc/nginx/snippets/ssl-params.conf`：

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
add_header Strict-Transport-Security "max-age=63072000" always;
```

在 server 块中引用：

```nginx
server {
    listen 443 ssl http2;
    ...
    ssl_certificate     /etc/pki/tls/certs/mysite.crt;
    ssl_certificate_key /etc/pki/tls/private/mysite.key;
    include /etc/nginx/snippets/ssl-params.conf;
    ...
}
```

### 4.3 Let's Encrypt 免费证书

```bash
# RHEL 8+ / Rocky / Alma / Fedora
sudo dnf install epel-release
sudo dnf install certbot python3-certbot-nginx
sudo certbot --nginx -d mysite.example.com

# CentOS 7
sudo yum install epel-release
sudo yum install certbot python2-certbot-nginx
sudo certbot --nginx -d mysite.example.com
```

---

## 5. SELinux 注意事项

RHEL 系默认启用 SELinux。Nginx 的常见 SELinux 问题：

### 5.1 Nginx 连接网络（反向代理需要）

```bash
# 允许 Nginx 发起网络连接（反向代理到后端应用时需要）
sudo setsebool -P httpd_can_network_connect 1

# 允许 Nginx 连接数据库（如果后端需要）
sudo setsebool -P httpd_can_network_connect_db 1
```

### 5.2 非标准目录的网站文件

如果你的网站文件不在 `/usr/share/nginx/html/`，需要设置正确的 SELinux 上下文：

```bash
# 设置目录为 httpd 可读取的类型
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/mysite(/.*)?"
sudo restorecon -R /var/www/mysite

# 如果目录需要写入权限（如上传目录）
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/var/www/mysite/upload(/.*)?"
sudo restorecon -R /var/www/mysite/upload

# 没有 semanage 命令时
sudo dnf install policycoreutils-python-utils   # RHEL 8+
```

### 5.3 快速判断是否 SELinux 引起的问题

```bash
# 临时关闭 SELinux 测试
sudo setenforce 0

# 如果问题消失，就是 SELinux 导致的
# 测试后恢复
sudo setenforce 1

# 查看 SELinux 拒绝日志（看最近的事件）
sudo ausearch -m avc -ts recent

# 或查看 audit.log
sudo grep nginx /var/log/audit/audit.log | grep denied
```

---

## 6. 命令速查

### 6.1 服务管理

| 操作 | 命令 |
|------|------|
| 启动 | `sudo systemctl start nginx` |
| 停止 | `sudo systemctl stop nginx` |
| 重启（中断连接） | `sudo systemctl restart nginx` |
| 重载配置（不中断连接） | `sudo systemctl reload nginx` |
| 开机自启 | `sudo systemctl enable nginx` |
| 禁用自启 | `sudo systemctl disable nginx` |
| 查看状态 | `sudo systemctl status nginx` |

### 6.2 信号控制（直接发信号给 Nginx 主进程）

```bash
sudo nginx -s reload     # 重载配置（= systemctl reload）
sudo nginx -s quit       # 优雅停止（等请求处理完）
sudo nginx -s stop       # 快速停止
sudo nginx -s reopen     # 重新打开日志文件
```

### 6.3 配置验证

```bash
# 语法检查（改配置后必做）
sudo nginx -t

# 打印完整配置（展开所有 include，用于调试）
sudo nginx -T

# 查看版本（小写 v）
nginx -v

# 查看版本、编译参数、模块列表（大写 V）
nginx -V
```

### 6.4 查看运行信息

```bash
# 查看 Nginx 运行用户
grep '^user' /etc/nginx/nginx.conf

# 查看当前运行的 Nginx 进程
ps aux | grep nginx

# 查看监听的端口
sudo ss -tlnp | grep nginx
```

### 6.5 日志查看

```bash
# 实时跟踪访问日志
sudo tail -f /var/log/nginx/access.log

# 实时跟踪错误日志
sudo tail -f /var/log/nginx/error.log

# 查看特定站点的日志
sudo tail -f /var/log/nginx/mysite-access.log
```

### 6.6 防火墙

```bash
# firewalld（RHEL 系默认防火墙）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 或按端口
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# 查看当前规则
sudo firewall-cmd --list-all
```

---

## 7. 故障排查

### 403 Forbidden

通常是权限问题或 SELinux 问题。

```bash
# 1. 先检查文件系统权限
ls -la /var/www/mysite/
# 确认 Nginx 运行用户
grep '^user' /etc/nginx/nginx.conf

# 修复权限（用户通常是 nginx，官方包）
sudo chown -R nginx:nginx /var/www/mysite
sudo chmod o+x /var /var/www

# 2. 如果权限正确但仍然 403，检查 SELinux（见第 5 节）
sudo ausearch -m avc -ts recent | grep nginx
```

### 502 Bad Gateway

后端应用未运行或 Nginx 找不到后端。

```bash
# 确认后端在运行
curl http://127.0.0.1:8000/

# 如果后端在运行但 Nginx 仍然 502，检查 SELinux
sudo setsebool -P httpd_can_network_connect 1
```

### 504 Gateway Timeout

后端响应太慢。增加超时：

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_read_timeout 300s;
    proxy_connect_timeout 60s;
}
```

### 端口被占用

```bash
# 查谁占用了 80 或 443
sudo ss -tlnp | grep -E ':80|:443'

# 如果是 Apache 占用了
sudo systemctl stop httpd
sudo systemctl disable httpd
```

### 上传文件太大（413 Request Entity Too Large）

```nginx
# 在 http、server 或 location 块中添加
client_max_body_size 100M;
```

### server_names_hash_bucket_size 警告

```nginx
# 在 http 块中添加
server_names_hash_bucket_size 64;
```

### 默认 server 块拦截了你的站点请求

如果 `curl http://127.0.0.1/` 返回的是 Nginx 默认欢迎页而不是你的站点，检查 `conf.d/` 下是否还有 `default.conf`：

```bash
# 查看并移除或修改默认配置
ls /etc/nginx/conf.d/
sudo mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.disabled
sudo nginx -t && sudo systemctl reload nginx
```

### 查看发行版信息（确认系统是 RHEL 系）

```bash
cat /etc/os-release
# ID="rocky" / ID="centos" / ID="rhel" / ID="fedora" / ID="almalinux"
cat /etc/redhat-release
```
