# Apache HTTP Server（Debian 系：Ubuntu / Debian / Kali）

> Apache 是最老牌的开源 Web 服务器。Debian 系发行版中，Apache 以模块化方式组织配置——`*-available/` 目录存放所有可用配置，`*-enabled/` 目录通过符号链接决定哪些生效。包名和服务名都是 `apache2`。

适用发行版：Ubuntu、Debian、Kali Linux。

---

## 1. 安装

```bash
sudo apt update
sudo apt install apache2

# 常用工具（htpasswd 等）
sudo apt install apache2-utils
```

安装后 Apache 自动启动并设为开机自启。访问 `http://服务器IP` 应看到默认页面。

---

## 2. 配置文件地图

理解 Apache 的文件布局是配置它的前提。这一节讲清楚每个目录和文件的作用，以及它们之间如何配合。

### 2.1 目录总览

所有 Apache 配置都在 `/etc/apache2/` 下：

| 路径 | 作用 |
|------|------|
| `/etc/apache2/apache2.conf` | **主配置入口**，通过 Include 指令加载其他所有文件 |
| `/etc/apache2/ports.conf` | 监听端口配置（默认 80、443） |
| `/etc/apache2/mods-available/` | **仓库**：所有可用模块的加载配置（`.load`）和模块配置（`.conf`） |
| `/etc/apache2/mods-enabled/` | **生效**：符号链接 → `mods-available/`。被 `apache2.conf` include |
| `/etc/apache2/sites-available/` | **仓库**：所有虚拟主机配置，放这里不代表生效 |
| `/etc/apache2/sites-enabled/` | **生效**：符号链接 → `sites-available/`。被 `apache2.conf` include |
| `/etc/apache2/conf-available/` | **仓库**：全局配置片段（如字符集、安全策略） |
| `/etc/apache2/conf-enabled/` | **生效**：符号链接 → `conf-available/`。被 `apache2.conf` include |
| `/etc/apache2/envvars` | 环境变量（APACHE_LOG_DIR 等），被启动脚本读取 |
| `/var/log/apache2/` | 日志目录：`access.log`（访问日志）、`error.log`（错误日志） |
| `/var/www/html/` | 默认网站根目录 |

### 2.2 配置文件如何配合（Include 链）

`apache2.conf` 是唯一入口，它按顺序 include 以下内容：

```
/etc/apache2/apache2.conf
│
├── IncludeOptional mods-enabled/*.load    ← ① 最先加载模块的 .so 文件
├── IncludeOptional mods-enabled/*.conf    ← ② 然后加载模块的配置
├── Include ports.conf                     ← ③ 监听端口
├── IncludeOptional conf-enabled/*.conf    ← ④ 全局配置片段
└── IncludeOptional sites-enabled/*.conf   ← ⑤ 最后加载站点（虚拟主机）
```

**关键理解**：`sites-enabled/` 和 `mods-enabled/` 下的文件都是符号链接，指向 `sites-available/` 和 `mods-available/` 中的实际文件。这就是 Debian 系 Apache 的核心设计——通过符号链接控制启用/禁用，不需要删除文件。

### 2.3 目录树全貌

```
/etc/apache2/
├── apache2.conf              # 主配置，你一般不改它
├── envvars                   # 环境变量
├── magic                     # mod_mime_magic 用，文件类型识别
├── ports.conf                # 监听端口
│
├── mods-available/           # 仓库：所有可用模块
│   ├── proxy.load            #   模块的 .load 文件 = LoadModule 指令
│   ├── proxy.conf            #   模块的 .conf 文件 = 该模块的配置
│   ├── ssl.load
│   ├── ssl.conf
│   ├── rewrite.load
│   └── ...
│
├── mods-enabled/             # 生效（符号链接 → mods-available）
│   ├── proxy.load -> ../mods-available/proxy.load
│   ├── proxy.conf -> ../mods-available/proxy.conf
│   └── ...
│
├── sites-available/          # 仓库：你的虚拟主机配置写在这里
│   ├── 000-default.conf      #   默认 HTTP 站点
│   └── default-ssl.conf      #   默认 HTTPS 站点
│
├── sites-enabled/            # 生效（符号链接 → sites-available）
│   └── 000-default.conf -> ../sites-available/000-default.conf
│
├── conf-available/           # 仓库：全局配置片段
│   ├── charset.conf
│   ├── security.conf
│   └── ...
│
└── conf-enabled/             # 生效（符号链接 → conf-available）
    └── ...
```

---

## 3. 运行一个项目需要配置哪些文件

这是核心章节。假设你有一个网站，需要让 Apache 把它托管起来。下面按步骤说明你需要创建哪些文件、放在哪里。

### 3.1 从零到运行的步骤

| 步骤 | 你要做的事 | 说明 |
|------|-----------|------|
| 1 | 放网站文件 | 把你的 HTML/CSS/JS 放到 `/var/www/你的站点名/` |
| 2 | 写虚拟主机配置文件 | 创建 `/etc/apache2/sites-available/你的站点名.conf` |
| 3 | 启用站点 | `sudo a2ensite 你的站点名.conf`（在 sites-enabled/ 创建符号链接） |
| 4 | 检查语法 | `sudo apache2ctl configtest` |
| 5 | 重载配置 | `sudo systemctl reload apache2` |

> **a2ensite 做了什么？** 就是在 `/etc/apache2/sites-enabled/` 下创建一个指向 `/etc/apache2/sites-available/` 的符号链接。`a2dissite` 则删除这个符号链接。因为 `apache2.conf` 里有 `IncludeOptional sites-enabled/*.conf`，所以符号链接存在就生效，删除就停用。

### 3.2 虚拟主机配置文件内容（你需要写的 .conf）

创建 `/etc/apache2/sites-available/mysite.conf`：

```apache
<VirtualHost *:80>
    # 这个站点响应哪个域名（没有域名就写服务器 IP）
    ServerName mysite.example.com
    ServerAlias www.mysite.example.com

    # 网站文件在哪（指向步骤 1 放的目录）
    DocumentRoot /var/www/mysite

    # 对这个目录的访问控制
    <Directory /var/www/mysite>
        Options Indexes FollowSymLinks    # Indexes: 没有 index 文件时列出目录
                                          # FollowSymLinks: 允许跟随符号链接
        AllowOverride All                 # 允许使用 .htaccess 覆写配置
        Require all granted               # 允许所有人访问
    </Directory>

    # 日志（${APACHE_LOG_DIR} = /var/log/apache2/，定义在 envvars 中）
    ErrorLog ${APACHE_LOG_DIR}/mysite-error.log
    CustomLog ${APACHE_LOG_DIR}/mysite-access.log combined
</VirtualHost>
```

**如果你需要反向代理**（把请求转发给后端应用，如 Python/Node.js 进程），用下面的写法代替 DocumentRoot：

```apache
<VirtualHost *:80>
    ServerName mysite.example.com

    # 反向代理：所有请求转发到本机 8000 端口
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # 静态文件让 Apache 直接处理，不经过后端（可选，性能更好）
    # Alias /static/ /var/www/mysite/static/
    # <Directory /var/www/mysite/static/>
    #     Require all granted
    # </Directory>

    ErrorLog ${APACHE_LOG_DIR}/mysite-error.log
    CustomLog ${APACHE_LOG_DIR}/mysite-access.log combined
</VirtualHost>
```

### 3.3 需要启用的模块

不同的项目需要不同的 Apache 模块。以下是常见场景：

| 场景 | 需要的模块 | 启用命令 |
|------|-----------|---------|
| 纯静态网站 | 不需要额外模块 | — |
| 反向代理 | proxy, proxy_http | `sudo a2enmod proxy proxy_http` |
| HTTPS | ssl | `sudo a2enmod ssl` |
| URL 重写（如 WordPress 伪静态） | rewrite | `sudo a2enmod rewrite` |
| 自定义响应头 | headers | `sudo a2enmod headers` |
| 压缩传输内容 | deflate | `sudo a2enmod deflate` |

`a2enmod 模块名` 在 `mods-enabled/` 下创建符号链接。对应的 `a2dismod 模块名` 删除符号链接。修改模块后需要 `sudo systemctl reload apache2`。

### 3.4 完整的部署命令序列

```bash
# 1. 放网站文件
sudo mkdir -p /var/www/mysite
echo "<h1>Hello</h1>" | sudo tee /var/www/mysite/index.html

# 2. 写虚拟主机配置
sudo vim /etc/apache2/sites-available/mysite.conf
# （粘贴上一节的配置内容）

# 3. 启用站点
sudo a2ensite mysite.conf

# 4. 语法检查
sudo apache2ctl configtest

# 5. 重载配置（不中断现有连接）
sudo systemctl reload apache2

# 6. 验证
curl -H "Host: mysite.example.com" http://127.0.0.1/
```

---

## 4. .htaccess —— 放在网站目录里的配置

`.htaccess` 是 Apache 的独有特性：在网站目录里放一个 `.htaccess` 文件，无需重启 Apache 就能覆写部分配置。

### 4.1 文件位置

```
/var/www/mysite/
├── index.html
├── .htaccess        ← 放在这里，影响当前目录及所有子目录
└── images/
    └── .htaccess    ← 也可以放在子目录，只影响该子目录
```

### 4.2 前提条件

VirtualHost 的 `<Directory>` 块中必须有 `AllowOverride All`（或指定允许覆写的类型）。没有这行，`.htaccess` 会被忽略。

### 4.3 常见用途

```apache
# URL 重写（需要 mod_rewrite）
RewriteEngine On
RewriteRule ^article/([0-9]+)$ /article.php?id=$1 [L]

# 访问控制：拒绝某个 IP
Deny from 192.168.1.100

# 自定义错误页面
ErrorDocument 404 /404.html

# 重定向
Redirect 301 /old-page.html /new-page.html
```

### 4.4 性能代价

Apache 每次请求都会检查请求路径的每一级目录中是否存在 `.htaccess` 文件。如果存在就解析并应用。这意味着每个请求都有额外的文件系统查找开销。如果配置不会频繁变动，把规则直接写在 VirtualHost 的 `<Directory>` 块中性能更好。

---

## 5. HTTPS 配置

### 5.1 启用 SSL 模块

```bash
sudo a2enmod ssl
sudo systemctl reload apache2
```

### 5.2 创建 HTTPS 虚拟主机

在 `/etc/apache2/sites-available/mysite-ssl.conf`：

```apache
<VirtualHost *:443>
    ServerName mysite.example.com

    DocumentRoot /var/www/mysite

    # SSL 证书路径
    SSLEngine on
    SSLCertificateFile      /etc/ssl/certs/mysite.crt
    SSLCertificateKeyFile   /etc/ssl/private/mysite.key

    # 中间证书（Let's Encrypt 需要）
    # SSLCertificateChainFile /etc/ssl/certs/chain.pem

    <Directory /var/www/mysite>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/mysite-ssl-error.log
    CustomLog ${APACHE_LOG_DIR}/mysite-ssl-access.log combined
</VirtualHost>
```

### 5.3 HTTP 跳转 HTTPS

在 `/etc/apache2/sites-available/mysite.conf`（端口 80 的配置）中添加：

```apache
<VirtualHost *:80>
    ServerName mysite.example.com
    Redirect permanent / https://mysite.example.com/
</VirtualHost>
```

### 5.4 Let's Encrypt 免费证书

```bash
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d mysite.example.com
# certbot 会自动修改你的 Apache 配置，添加 SSL 并设置自动续期
```

---

## 6. 命令速查

### 6.1 服务管理

| 操作 | 命令 |
|------|------|
| 启动 | `sudo systemctl start apache2` |
| 停止 | `sudo systemctl stop apache2` |
| 重启（中断连接） | `sudo systemctl restart apache2` |
| 重载配置（不中断连接） | `sudo systemctl reload apache2` |
| 开机自启 | `sudo systemctl enable apache2` |
| 禁用自启 | `sudo systemctl disable apache2` |
| 查看状态 | `sudo systemctl status apache2` |

### 6.2 配置验证

```bash
# 语法检查（改配置后必做）
sudo apache2ctl configtest

# 查看所有虚拟主机及加载顺序
sudo apache2ctl -S

# 查看已加载的模块
sudo apache2ctl -M

# 查看版本
apache2 -v

# 查看编译参数和版本详情
apache2 -V
```

### 6.3 站点管理

```bash
# 启用站点（在 sites-enabled/ 创建符号链接）
sudo a2ensite 站点名.conf

# 禁用站点（删除符号链接）
sudo a2dissite 站点名.conf

# 列出 sites-available 和 sites-enabled 的内容
ls -l /etc/apache2/sites-available/
ls -l /etc/apache2/sites-enabled/
```

### 6.4 模块管理

```bash
# 启用模块
sudo a2enmod 模块名

# 禁用模块
sudo a2dismod 模块名

# 查看已启用的模块
ls /etc/apache2/mods-enabled/
```

### 6.5 日志查看

```bash
# 实时跟踪访问日志
sudo tail -f /var/log/apache2/access.log

# 实时跟踪错误日志
sudo tail -f /var/log/apache2/error.log

# 查看特定站点的日志（如果你在 VirtualHost 中指定了独立日志）
sudo tail -f /var/log/apache2/mysite-access.log
```

### 6.6 工具命令

```bash
# 生成 htpasswd 密码文件（用于 Basic Auth）
sudo htpasswd -c /etc/apache2/.htpasswd 用户名
# -c 只在第一次创建文件时用，后续添加用户不用 -c

# 压力测试（ab = Apache Benchmark）
ab -n 1000 -c 100 http://mysite.example.com/
# -n 总请求数  -c 并发数
```

### 6.7 防火墙

```bash
# UFW（Ubuntu/Debian 默认防火墙）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 'Apache Full'    # 同时开放 80 和 443
```

---

## 7. 故障排查

### 403 Forbidden
Apache 进程用户 `www-data` 对网站目录没有读取权限。

```bash
# 检查 Apache 运行用户
ps aux | grep apache2

# 修复权限
sudo chown -R www-data:www-data /var/www/mysite

# 确保父目录有执行权限（x）
sudo chmod o+x /var /var/www
```

### 端口被占用

```bash
# 查看谁占用了 80 或 443 端口
sudo ss -tlnp | grep -E ':80|:443'

# 如果 Nginx 占用了，先停掉
sudo systemctl stop nginx
```

### 配置语法错误

```bash
# 语法检查会告诉你哪个文件哪一行有问题
sudo apache2ctl configtest
# 输出示例：AH00526: Syntax error on line 15 of /etc/apache2/sites-enabled/mysite.conf
```

### 模块未加载导致指令不识别

如果你用了 `ProxyPass` 但没启用 `proxy` 模块，会出现 "Invalid command 'ProxyPass'" 错误：

```bash
sudo a2enmod proxy proxy_http
sudo systemctl reload apache2
```

### 查看发行版信息（确认系统是 Debian 系）

```bash
cat /etc/os-release
# ID=ubuntu 或 ID=debian 或 ID=kali
```
