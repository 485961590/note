# Nginx（Debian 系：Ubuntu / Debian / Kali）

> Nginx 是高性能 HTTP 和反向代理服务器，事件驱动架构，内存占用低。Debian 系中 Nginx 配置存在两种约定并存的情况：系统自带包沿用 `sites-available/`/`sites-enabled/` 模式，官方仓库包只用 `conf.d/`。两者本质都是 `include` 指令的不同写法。

适用发行版：Ubuntu、Debian、Kali Linux。

---

## 1. 安装

### 方式一：系统默认仓库（版本较旧，但简单）

```bash
sudo apt update
sudo apt install nginx
```

安装后自动启动并设为开机自启。

### 方式二：Nginx 官方仓库（推荐，版本最新）

```bash
# 安装依赖
sudo apt install curl gnupg2 ca-certificates lsb-release

# 添加官方签名密钥
curl -fsSL https://nginx.org/keys/nginx_signing.key | sudo gpg --dearmor -o /usr/share/keyrings/nginx-archive-keyring.gpg

# 添加官方 apt 源
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
# 注意：Debian 系统把上面的 ubuntu 换成 debian

# 设置优先级
echo -e "Package: *\nPin: origin nginx.org\nPin: release o=nginx\nPin-Priority: 900" | sudo tee /etc/apt/preferences.d/99nginx

sudo apt update
sudo apt install nginx
```

> 系统包和官方包的一个重要区别：**系统包自带 `sites-available/` 和 `sites-enabled/` 目录**并在 `nginx.conf` 中 include 它们；**官方包只用 `conf.d/`**。两种都能用，推荐统一用 `conf.d/` 因为它跨发行版通用。

---

## 2. 配置文件地图

### 2.1 设计哲学：集中式 + 层级继承

Nginx 的配置哲学和 Apache 不同：
- **一个入口**：`nginx.conf` 是唯一的主配置文件，通过 `include` 指令加载其他文件
- **层级继承**：配置分为 `http {}` → `server {}` → `location {}` 三层，下级继承上级的设置，同名指令覆盖
- **一个 server 块 = 一个站点**：不像 Apache 需要 `<VirtualHost>` 标签包裹，Nginx 的每个 `server {}` 块就是一个站点

### 2.2 目录总览

| 路径 | 作用 |
|------|------|
| `/etc/nginx/nginx.conf` | **主配置入口**，通过 include 加载其他所有配置 |
| `/etc/nginx/conf.d/` | **推荐**的站点配置目录。所有 `.conf` 文件被 `nginx.conf` include |
| `/etc/nginx/sites-available/` | 站点配置仓库（仅系统包有，官方包无此目录） |
| `/etc/nginx/sites-enabled/` | 已启用站点的符号链接（仅系统包有） |
| `/etc/nginx/snippets/` | 可复用配置片段（SSL 参数等） |
| `/etc/nginx/mime.types` | MIME 类型映射表 |
| `/etc/nginx/fastcgi.conf` | FastCGI 通用参数（PHP-FPM 用） |
| `/var/log/nginx/` | 日志目录：`access.log`、`error.log` |
| `/usr/share/nginx/html/` | 默认网站根目录 |
| `/var/run/nginx.pid` | 主进程 PID 文件 |

### 2.3 nginx.conf 内部结构（逐块注释）

```
/etc/nginx/nginx.conf
│
├── user www-data;                     # 进程以哪个用户运行
├── worker_processes auto;             # 工作进程数，auto = 按 CPU 核数
├── error_log /var/log/nginx/error.log notice;
├── pid /var/run/nginx.pid;
│
├── events {                           # 连接处理模型
│       worker_connections 1024;       # 每个 worker 最大连接数
│   }
│
└── http {                             # HTTP 核心模块——所有网站配置都在这里面
    │
    ├── include /etc/nginx/mime.types; # MIME 类型映射（.html → text/html 等）
    ├── default_type application/octet-stream;
    │
    ├── access_log /var/log/nginx/access.log;
    │
    ├── sendfile on;                   # 高效文件传输
    ├── keepalive_timeout 65;          # 长连接超时
    │
    ├── include /etc/nginx/conf.d/*.conf;         ← 你的站点配置通过这行加载
    │   （系统包可能还有 include /etc/nginx/sites-enabled/*;）
    │
    └── server { ... }                  # 默认 server 块（通常是最初的欢迎页面）
    }
```

**关键理解**：`include /etc/nginx/conf.d/*.conf;` 这一行意味着你在 `conf.d/` 下创建的任何 `.conf` 文件都会被自动加载。改配置只需要创建/修改文件 + `nginx -t` + `systemctl reload nginx`。

### 2.4 目录树全貌（系统包）

```
/etc/nginx/
├── nginx.conf                 # 主配置
├── mime.types                 # MIME 类型
├── fastcgi.conf               # FastCGI 参数
├── fastcgi_params             # FastCGI 参数（备用）
├── scgi_params                # SCGI 参数
├── uwsgi_params               # uWSGI 参数
│
├── conf.d/                    # 站点配置（官方包只靠这个）
├── sites-available/           # 仓库：站点配置（仅系统包）
│   └── default                #   默认站点
├── sites-enabled/             # 生效：符号链接 → sites-available（仅系统包）
│   └── default -> ../sites-available/default
├── snippets/                  # 可复用片段
│   ├── fastcgi-php.conf
│   └── snakeoil.conf          #   默认自签名证书配置
│
└── modules-enabled/           # 动态模块符号链接 → /usr/share/nginx/modules
```

---

## 3. sites-enabled vs conf.d —— 两个约定

### 3.1 来源

- **sites-available/ + sites-enabled/** 是 Debian 打包者从 Apache 借鉴来的习惯。只有通过 `apt install nginx` 安装的系统包有这两个目录。
- **conf.d/** 是 Nginx 官方推荐的跨发行版约定，所有发行版的官方包都用它。

### 3.2 本质

两者都是被 `nginx.conf` 中的 `include` 加载的，区别仅在于目录名和是否需要符号链接：

```nginx
# 系统包的 nginx.conf 通常两行都有
include /etc/nginx/conf.d/*.conf;
include /etc/nginx/sites-enabled/*;

# 官方包的 nginx.conf 只有
include /etc/nginx/conf.d/*.conf;
```

### 3.3 推荐做法

**统一用 `conf.d/`**。原因：
- 跨发行版通用（无论是系统包还是官方包都支持）
- 不需要创建符号链接，少一步操作
- 团队中其他人更容易理解

如果系统包自动创建了 `sites-enabled/` 和指向 default 的符号链接，你可以忽略它们——用 `conf.d/` 即可。

---

## 4. 运行一个项目需要配置哪些文件

### 4.1 从零到运行的步骤

| 步骤 | 你要做的事 | 说明 |
|------|-----------|------|
| 1 | 放网站文件 | 把你的 HTML/CSS/JS 放到 `/var/www/你的站点名/` |
| 2 | 写 Server Block 配置文件 | 创建 `/etc/nginx/conf.d/你的站点名.conf` |
| 3 | 检查语法 | `sudo nginx -t` |
| 4 | 重载配置 | `sudo systemctl reload nginx` |

**只有两步操作**：写一个配置文件 + 重载。比 Apache 少了"启用站点"步骤，因为 `conf.d/*.conf` 自动加载。

### 4.2 Server Block 配置文件内容（你需要写的 .conf）

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

    # 日志（如果不写，使用 nginx.conf 中定义的默认日志）
    access_log /var/log/nginx/mysite-access.log;
    error_log  /var/log/nginx/mysite-error.log;
}
```

**各指令说明：**

| 指令 | 作用 |
|------|------|
| `listen 80` | 监听 80 端口（HTTP 标准端口） |
| `server_name` | Nginx 根据请求头中的 Host 匹配对应的 server 块 |
| `root` | 网站文件的根目录，Nginx 会把 URL 路径拼接在 root 后面去查找文件 |
| `index` | 访问目录时默认返回的文件，按顺序查找 |
| `try_files` | 按顺序尝试查找文件：`$uri`（请求路径对应的文件）→ `$uri/`（请求路径对应的目录）→ `=404`（返回 404） |
| `location /` | 匹配所有以 `/` 开头的 URL，即所有请求 |

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
| `proxy_set_header X-Real-IP` | 传递客户端真实 IP（后端日志中能看到） |
| `proxy_set_header X-Forwarded-For` | 代理链，每经过一层代理就追加一个 IP |
| `proxy_set_header X-Forwarded-Proto` | 告知后端前端用的协议（http 还是 https） |

### 4.3 完整的部署命令序列

```bash
# 1. 放网站文件
sudo mkdir -p /var/www/mysite
echo "<h1>Hello</h1>" | sudo tee /var/www/mysite/index.html

# 2. 写 Server Block 配置
sudo vim /etc/nginx/conf.d/mysite.conf
# （粘贴上一节的配置内容）

# 3. 语法检查
sudo nginx -t

# 4. 重载配置（不中断现有连接）
sudo systemctl reload nginx

# 5. 验证
curl -H "Host: mysite.example.com" http://127.0.0.1/

# 6. 如果用了反向代理，确认后端在运行
curl http://127.0.0.1:8000/
```

---

## 5. HTTPS 配置

### 5.1 创建 HTTPS Server Block

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

    # SSL 证书
    ssl_certificate     /etc/ssl/certs/mysite.crt;
    ssl_certificate_key /etc/ssl/private/mysite.key;

    # SSL 安全策略
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/mysite;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    access_log /var/log/nginx/mysite-access.log;
    error_log  /var/log/nginx/mysite-error.log;
}
```

### 5.2 SSL 参数复用

把 SSL 参数抽取到 `/etc/nginx/snippets/ssl-params.conf` 中，多个站点共用：

```nginx
# /etc/nginx/snippets/ssl-params.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
add_header Strict-Transport-Security "max-age=63072000" always;
```

然后在 server 块中引用：

```nginx
server {
    listen 443 ssl http2;
    server_name mysite.example.com;

    ssl_certificate     /etc/ssl/certs/mysite.crt;
    ssl_certificate_key /etc/ssl/private/mysite.key;
    include snippets/ssl-params.conf;    # 引用公共 SSL 配置

    # ...其余配置
}
```

### 5.3 Let's Encrypt 免费证书

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d mysite.example.com
# certbot 会自动修改 Nginx 配置并添加 HTTPS server block
# 证书会自动续期（systemd timer）
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
sudo nginx -s reopen     # 重新打开日志文件（logrotate 用）
```

### 6.3 配置验证

```bash
# 语法检查（改配置后必做）
sudo nginx -t

# 打印完整配置（展开所有 include，用于调试）
sudo nginx -T

# 查看版本和编译参数（小写 v）
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

# 查看 Nginx 监听的端口
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
# UFW（Ubuntu/Debian 默认防火墙）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 'Nginx Full'    # 同时开放 80 和 443（UFW 预置 profile）

# 查看 UFW 预置的 Nginx profile
sudo ufw app list | grep -i nginx
```

---

## 7. 故障排查

### 403 Forbidden

Nginx 进程用户对网站目录没有读取权限。

```bash
# 查看 Nginx 运行用户
grep '^user' /etc/nginx/nginx.conf
# 或
ps aux | grep nginx

# 修复权限（用户通常是 www-data，系统包）
sudo chown -R www-data:www-data /var/www/mysite

# 确保父目录有执行权限
sudo chmod o+x /var /var/www

# 确保具体文件可读
sudo chmod 644 /var/www/mysite/index.html
```

### 502 Bad Gateway

后端应用未运行或 Nginx 找不到后端。

```bash
# 确认后端应用在运行
curl http://127.0.0.1:8000/

# 确认 proxy_pass 的地址正确
grep proxy_pass /etc/nginx/conf.d/mysite.conf
```

### 504 Gateway Timeout

后端应用响应太慢。增加超时时间：

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_read_timeout 300s;       # 等待后端响应的最长时间
    proxy_connect_timeout 60s;     # 连接后端的超时时间
}
```

### 端口被占用

```bash
# 查看谁占用了 80 或 443
sudo ss -tlnp | grep -E ':80|:443'

# 如果是 Apache 占用了
sudo systemctl stop apache2
sudo systemctl disable apache2   # 防止重启后又抢占
```

### 上传文件太大（413 Request Entity Too Large）

```nginx
# 在 http、server 或 location 块中添加
client_max_body_size 100M;
```

### server_names_hash_bucket_size 警告

域名太多或太长时 `nginx -t` 会提示增加 hash bucket 大小：

```nginx
# 在 http 块中添加
server_names_hash_bucket_size 64;
```

### 查看发行版信息（确认系统是 Debian 系）

```bash
cat /etc/os-release
# ID=ubuntu 或 ID=debian 或 ID=kali
```
