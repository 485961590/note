# Apache HTTP Server（RHEL 系：CentOS / RHEL / Rocky / Alma / Fedora）

> RHEL 系发行版中，Apache 以包名 `httpd` 分发，采用扁平化配置结构——`conf.d/` 下放 `.conf` 文件即生效，没有 Debian 系的 `*-available/` / `*-enabled/` 符号链接机制。配置文件路径和服务名都与 Debian 系不同。

适用发行版：CentOS 7/8+、RHEL 7/8/9+、Rocky Linux、AlmaLinux、Fedora。

---

## 1. 安装

**CentOS 7（yum）：**

```bash
sudo yum install httpd
sudo yum install httpd-tools
```

**CentOS 8+ / RHEL 8+ / Rocky / Alma / Fedora（dnf）：**

```bash
sudo dnf install httpd
sudo dnf install httpd-tools
```

安装后需要手动启动并设置开机自启：

```bash
sudo systemctl start httpd
sudo systemctl enable httpd
```

> 注意：RHEL 系安装后**不会自动启动**，这点和 Debian 系不同。

---

## 2. 配置文件地图

### 2.1 设计哲学：扁平化

RHEL 系的 Apache 配置没有 `*-available/` / `*-enabled/` 的符号链接机制。规则很简单：**`.conf` 文件放在 `conf.d/` 下就自动生效，移走或改名就停用。**模块配置同理，放在 `conf.modules.d/` 下把注释去掉就启用。

### 2.2 目录总览

所有 Apache 配置都在 `/etc/httpd/` 下：

| 路径 | 作用 |
|------|------|
| `/etc/httpd/conf/httpd.conf` | **主配置入口**，通过 IncludeOptional 加载其他文件 |
| `/etc/httpd/conf.d/` | **站点和全局配置**：所有 `.conf` 文件自动加载。虚拟主机、全局配置片段都放这里 |
| `/etc/httpd/conf.modules.d/` | **模块加载配置**：每个 `.conf` 文件对应一个或一组模块，里面是 LoadModule 行 |
| `/var/log/httpd/` | 日志目录：`access_log`（访问日志）、`error_log`（错误日志） |
| `/var/www/html/` | 默认网站根目录 |
| `/usr/lib64/httpd/modules/` | 模块 `.so` 文件的存放位置 |
| `/etc/httpd/logs` → `../../var/log/httpd` | 日志符号链接，方便从 `/etc/httpd/` 下访问 |

### 2.3 配置文件如何配合（Include 链）

`httpd.conf` 是唯一入口，它按顺序 include 以下内容：

```
/etc/httpd/conf/httpd.conf
│
├── IncludeOptional conf.modules.d/*.conf   ← ① 先加载模块（00- 开头的文件先加载）
│   ├── 00-base.conf       # 基础模块
│   ├── 00-proxy.conf      # 代理相关模块
│   ├── 00-ssl.conf        # SSL 模块
│   ├── 01-cgi.conf        # CGI 模块
│   └── ...
│
└── IncludeOptional conf.d/*.conf           ← ② 然后加载所有站点和全局配置
    ├── autoindex.conf     # 目录索引配置
    ├── userdir.conf       # 用户目录配置
    ├── welcome.conf       # 默认欢迎页面
    ├── mysite.conf        # 你的站点配置（你创建的）
    └── ...
```

### 2.4 目录树全貌

```
/etc/httpd/
├── conf/
│   └── httpd.conf              # 主配置，你一般不改它
│
├── conf.d/                     # 放站点的 .conf，放进去即生效
│   ├── autoindex.conf          #   默认带的配置，你不需要动
│   ├── userdir.conf            #   默认带的配置
│   ├── welcome.conf            #   默认欢迎页面
│   └── mysite.conf             #   你的站点配置（你来创建）
│
├── conf.modules.d/             # 模块加载配置
│   ├── 00-base.conf            #   基础模块（rewrite, headers 等）
│   ├── 00-proxy.conf           #   代理模块（proxy, proxy_http 等）
│   ├── 00-ssl.conf             #   SSL 模块
│   └── ...
│
├── logs -> ../../var/log/httpd # 日志符号链接
└── modules -> ../../usr/lib64/httpd/modules  # 模块符号链接
```

---

## 3. 运行一个项目需要配置哪些文件

### 3.1 从零到运行的步骤

| 步骤  | 你要做的事     | 说明                                    |
| --- | --------- | ------------------------------------- |
| 1   | 放网站文件     | 把你的 HTML/CSS/JS 放到 `/var/www/你的站点名/`  |
| 2   | 写虚拟主机配置文件 | 创建 `/etc/httpd/conf.d/你的站点名.conf`     |
| 3   | 不需要"启用"步骤 | `conf.d/` 下的 `.conf` 自动生效，没有 a2ensite |
| 4   | 检查语法      | `sudo httpd -t`                       |
| 5   | 重载配置      | `sudo systemctl reload httpd`         |

> **和 Debian 系的关键区别**：RHEL 系没有 `a2ensite` 和 `sites-enabled/`。你创建的 `.conf` 文件放在 `conf.d/` 下就自动生效。如果要停用某个站点，把文件移走或改后缀（如 `.conf.disabled`），然后重载配置。

### 3.2 虚拟主机配置文件内容（你需要写的 .conf）

创建 `/etc/httpd/conf.d/mysite.conf`：

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

    # 日志（RHEL 系没有 ${APACHE_LOG_DIR} 变量，写绝对路径）
    ErrorLog /var/log/httpd/mysite-error.log
    CustomLog /var/log/httpd/mysite-access.log combined
</VirtualHost>
```

> **与 Debian 系配置的唯一差异**：日志路径必须写绝对路径 `/var/log/httpd/...`，不能使用 `${APACHE_LOG_DIR}`。其他指令完全相同。

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

    ErrorLog /var/log/httpd/mysite-error.log
    CustomLog /var/log/httpd/mysite-access.log combined
</VirtualHost>
```

### 3.3 需要启用的模块

RHEL 系启用模块的方式是：**在 `conf.modules.d/` 下的对应文件中取消 LoadModule 行的注释**。没有 `a2enmod` 命令。

| 场景 | 需要的模块 | 启用方式 |
|------|-----------|---------|
| 纯静态网站 | 不需要额外模块 | — |
| 反向代理 | proxy, proxy_http | 编辑 `/etc/httpd/conf.modules.d/00-proxy.conf`，取消以下行的注释 |
| HTTPS | ssl | `sudo dnf install mod_ssl`（安装后自动在 conf.modules.d 创建配置） |
| URL 重写 | rewrite | 编辑 `/etc/httpd/conf.modules.d/00-base.conf`，取消 `LoadModule rewrite_module` 的注释 |
| 自定义响应头 | headers | 通常默认已加载，在 `00-base.conf` 中 |

**检查模块是否已加载：**

```bash
sudo httpd -M | grep 模块名
# 例如：
sudo httpd -M | grep proxy
```

**编辑模块配置的示例（启用反向代理模块）：**

编辑 `/etc/httpd/conf.modules.d/00-proxy.conf`，确保以下行**没有** `#` 注释：

```apache
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
```

改完后重载：

```bash
sudo httpd -t && sudo systemctl reload httpd
```

### 3.4 完整的部署命令序列

```bash
# 1. 放网站文件
sudo mkdir -p /var/www/mysite
echo "<h1>Hello</h1>" | sudo tee /var/www/mysite/index.html

# 2. 写虚拟主机配置
sudo vim /etc/httpd/conf.d/mysite.conf
# （粘贴上一节的配置内容）

# 3. 语法检查
sudo httpd -t

# 4. 重载配置（不中断现有连接）
sudo systemctl reload httpd

# 5. 验证
curl -H "Host: mysite.example.com" http://127.0.0.1/
```

---

## 4. .htaccess —— 放在网站目录里的配置

`.htaccess` 在 RHEL 系 Apache 中的用法与 Debian 系完全一致。

### 4.1 文件位置

```
/var/www/mysite/
├── index.html
├── .htaccess        ← 放在这里，影响当前目录及所有子目录
└── images/
    └── .htaccess    ← 也可以放在子目录，只影响该子目录
```

### 4.2 前提条件

VirtualHost 的 `<Directory>` 块中必须有 `AllowOverride All`。

### 4.3 常见用途

```apache
# URL 重写（需要 mod_rewrite 已启用）
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

Apache 每次请求都会向上查找每一级目录中是否存在 `.htaccess`，有则解析应用。如果配置不常变动，把规则直接写在 VirtualHost 的 `<Directory>` 块中性能更好。

---

## 5. HTTPS 配置

### 5.1 安装 SSL 模块

```bash
# CentOS 8+ / RHEL 8+ / Rocky / Fedora
sudo dnf install mod_ssl

# CentOS 7
sudo yum install mod_ssl
```

安装后 `conf.modules.d/00-ssl.conf` 会自动创建，`conf.d/ssl.conf` 包含默认的 SSL 虚拟主机模板。

### 5.2 创建 HTTPS 虚拟主机

在 `/etc/httpd/conf.d/mysite-ssl.conf`：

```apache
<VirtualHost *:443>
    ServerName mysite.example.com

    DocumentRoot /var/www/mysite

    # SSL 证书路径
    SSLEngine on
    SSLCertificateFile      /etc/pki/tls/certs/mysite.crt
    SSLCertificateKeyFile   /etc/pki/tls/private/mysite.key

    # 中间证书（Let's Encrypt 需要）
    # SSLCertificateChainFile /etc/pki/tls/certs/chain.pem

    <Directory /var/www/mysite>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/mysite-ssl-error.log
    CustomLog /var/log/httpd/mysite-ssl-access.log combined
</VirtualHost>
```

> RHEL 系中 SSL 证书通常放在 `/etc/pki/tls/certs/` 和 `/etc/pki/tls/private/`。

### 5.3 HTTP 跳转 HTTPS

在 `/etc/httpd/conf.d/mysite.conf`（端口 80 的配置）中：

```apache
<VirtualHost *:80>
    ServerName mysite.example.com
    Redirect permanent / https://mysite.example.com/
</VirtualHost>
```

### 5.4 Let's Encrypt 免费证书

```bash
# CentOS 8+ / RHEL 8+ / Rocky
sudo dnf install epel-release
sudo dnf install certbot python3-certbot-apache
sudo certbot --apache -d mysite.example.com

# CentOS 7
sudo yum install epel-release
sudo yum install certbot python2-certbot-apache
sudo certbot --apache -d mysite.example.com
```

---

## 6. SELinux 注意事项

RHEL 系默认启用 SELinux，它会阻止 Apache 的一些操作。常见需要调整的：

### 6.1 Apache 连接网络（反向代理需要）

```bash
# 允许 Apache 发起网络连接（反向代理到后端应用时需要）
sudo setsebool -P httpd_can_network_connect 1

# 查看当前状态
getsebool httpd_can_network_connect
```

### 6.2 非标准目录的网站文件

如果你的网站文件不在 `/var/www/html/`，需要设置正确的 SELinux 上下文：

```bash
# 设置目录为 httpd 可读取的类型
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/mysite(/.*)?"
sudo restorecon -R /var/www/mysite

# 如果没有 semanage 命令
sudo dnf install policycoreutils-python-utils   # RHEL 8+
sudo yum install policycoreutils-python         # CentOS 7
```

### 6.3 快速判断是否 SELinux 引起的问题

```bash
# 临时关闭 SELinux 测试（重启后恢复）
sudo setenforce 0

# 如果此时问题消失，就是 SELinux 导致的
# 测试完后恢复
sudo setenforce 1

# 查看 SELinux 拒绝日志
sudo ausearch -m avc -ts recent
```

> mod_wsgi + Python C 扩展的 SELinux 排障案例见 [[Apache-mod_wsgi-SELinux排障]]。

---

## 7. 命令速查

### 7.1 服务管理

| 操作 | 命令 |
|------|------|
| 启动 | `sudo systemctl start httpd` |
| 停止 | `sudo systemctl stop httpd` |
| 重启（中断连接） | `sudo systemctl restart httpd` |
| 重载配置（不中断连接） | `sudo systemctl reload httpd` |
| 开机自启 | `sudo systemctl enable httpd` |
| 禁用自启 | `sudo systemctl disable httpd` |
| 查看状态 | `sudo systemctl status httpd` |

### 7.2 配置验证

```bash
# 语法检查（改配置后必做）
sudo httpd -t

# 查看所有虚拟主机及加载顺序
sudo httpd -S

# 查看已加载的模块
sudo httpd -M

# 查看版本
httpd -v

# 查看编译参数和版本详情
httpd -V
```

### 7.3 站点管理

RHEL 系没有 `a2ensite`/`a2dissite`。管理站点的方式是操作 `conf.d/` 下的文件：

```bash
# 启用站点：创建 .conf 文件
sudo vim /etc/httpd/conf.d/mysite.conf

# 停用站点：改后缀使其不被 include
sudo mv /etc/httpd/conf.d/mysite.conf /etc/httpd/conf.d/mysite.conf.disabled

# 或直接移走
sudo mv /etc/httpd/conf.d/mysite.conf ~/

# 列出当前所有站点配置
ls /etc/httpd/conf.d/
```

### 7.4 模块管理

```bash
# 查看已加载的模块
sudo httpd -M

# 查看模块配置文件
ls /etc/httpd/conf.modules.d/

# 启用模块：编辑对应的 .conf 文件，取消 LoadModule 行的注释
sudo vim /etc/httpd/conf.modules.d/00-proxy.conf

# 安装缺失的模块包（如 mod_ssl）
sudo dnf install mod_ssl
```

### 7.5 日志查看

```bash
# 实时跟踪访问日志
sudo tail -f /var/log/httpd/access_log

# 实时跟踪错误日志
sudo tail -f /var/log/httpd/error_log

# 查看特定站点的日志（如果你在 VirtualHost 中指定了独立日志）
sudo tail -f /var/log/httpd/mysite-access.log
```

### 7.6 工具命令

```bash
# 生成 htpasswd 密码文件（用于 Basic Auth）
sudo htpasswd -c /etc/httpd/.htpasswd 用户名
# -c 只在第一次创建文件时用，后续添加用户不用 -c

# 压力测试
ab -n 1000 -c 100 http://mysite.example.com/
# -n 总请求数  -c 并发数
```

### 7.7 防火墙

```bash
# firewalld（RHEL 系默认防火墙）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 或按端口开放
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# 查看当前规则
sudo firewall-cmd --list-all
```

---

## 8. 故障排查

### 403 Forbidden

Apache 进程用户 `apache` 对网站目录没有读取权限。

```bash
# 检查 Apache 运行用户
ps aux | grep httpd

# 修复文件权限
sudo chown -R apache:apache /var/www/mysite

# 确保父目录有执行权限（x）
sudo chmod o+x /var /var/www
```

如果权限正确但仍然 403，检查 SELinux（见第 6 节）。

### 端口被占用

```bash
# 查看谁占用了 80 或 443 端口
sudo ss -tlnp | grep -E ':80|:443'

# 如果 Nginx 占用了，先停掉
sudo systemctl stop nginx
```

### 配置语法错误

```bash
sudo httpd -t
# 输出会指明哪个文件哪一行有问题
# 示例：Syntax error on line 15 of /etc/httpd/conf.d/mysite.conf
```

### 模块未加载导致指令不识别

如果你用了 `ProxyPass` 但代理模块被注释了：

```bash
# 检查代理模块是否加载
sudo httpd -M | grep proxy

# 如果没有，编辑模块配置文件取消注释
sudo vim /etc/httpd/conf.modules.d/00-proxy.conf
# 取消 LoadModule proxy_module ... 和 LoadModule proxy_http_module ... 前的注释
sudo systemctl reload httpd
```

### SELinux 阻止操作

```bash
# 查看最近的 SELinux 拒绝记录
sudo ausearch -m avc -ts recent

# 常见修复
sudo setsebool -P httpd_can_network_connect 1     # 允许反向代理
sudo setsebool -P httpd_can_sendmail 1            # 允许发送邮件
```

### 查看发行版信息（确认系统是 RHEL 系）

```bash
cat /etc/os-release
# ID="rocky" / ID="centos" / ID="rhel" / ID="fedora" / ID="almalinux"
cat /etc/redhat-release    # RHEL 系都有这个文件
```
