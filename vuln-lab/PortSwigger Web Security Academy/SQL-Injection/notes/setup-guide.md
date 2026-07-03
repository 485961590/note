# SQLi-Labs 靶场搭建指南

## 环境要求

| 组件 | 版本建议 |
|------|---------|
| OS | Linux (Ubuntu 20.04+ / Kali / CentOS 7+) |
| PHP | 5.6 或 7.x（推荐 5.6，兼容性最好） |
| MySQL | 5.x（推荐 5.7） |
| Web Server | Apache 2.4+ 或 Nginx + PHP-FPM |

> 不建议在 Windows 上直接搭，PHP 5.x + MySQL 老版本在 Windows 上问题较多。推荐用 Docker。

## 方式一：Docker（推荐，5 分钟搞定）

```bash
# 拉取镜像
docker pull acgpiano/sqli-labs

# 启动容器，映射到本机 8080 端口
docker run -d -p 8080:80 --name sqli-labs acgpiano/sqli-labs

# 初始化数据库（首次必须执行）
docker exec -it sqli-labs bash
# 进入容器后：
mysql -u root -p
# 默认密码为空，直接回车
# 然后在 MySQL 中执行：
source /var/www/html/sqli-labs/sql-connections/sql-connections.sql
exit
```

访问 `http://localhost:8080/`，点击 "Setup/reset Database for labs" 完成初始化。

## 方式二：手动搭建（Kali / Ubuntu）

```bash
# 1. 安装 LAMP
sudo apt update
sudo apt install apache2 mysql-server php php-mysql php-mbstring -y

# 2. 配置 MySQL
sudo mysql_secure_installation
# 设置 root 密码，其余选 Y

# 3. 下载 SQLi-Labs
cd /var/www/html
sudo git clone https://github.com/Audi-1/sqli-labs.git
sudo chmod -R 777 sqli-labs/

# 4. 创建数据库连接配置
cd sqli-labs/sql-connections/
# 编辑 db-creds.inc，设置你的 MySQL root 密码
sudo nano db-creds.inc
```

内容示例：
```php
<?php
$dbhost = 'localhost';
$dbuser = 'root';
$dbpass = 'your_password_here';
$dbname = "security";
?>
```

然后访问 `http://localhost/sqli-labs/`，点击 "Setup/reset Database"。

## 方式三：Docker Compose（完整环境）

```yaml
# docker-compose.yml
version: '3'
services:
  db:
    image: mysql:5.7
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: security
    ports:
      - "3306:3306"

  web:
    image: acgpiano/sqli-labs
    ports:
      - "8080:80"
    depends_on:
      - db
```

```bash
docker-compose up -d
```

## 初始化数据库

无论哪种方式搭建，首次使用都需要：

1. 浏览器访问靶场首页（如 `http://localhost:8080/`）
2. 点击页面上的 **"Setup/reset Database for labs"**
3. 看到成功提示后即可开始

这一步会创建 `security` 数据库并插入所有关卡的测试数据。

## 靶场重置

部分关卡（如 Less 54-65 挑战关）有尝试次数限制。如果被锁定：

1. 回到首页点击 "Setup/reset Database for labs" 即可重置
2. 或者手动执行：
```bash
docker exec -it sqli-labs mysql -u root -e "DROP DATABASE security;"
# 然后重新 Setup
```

## 验证靶场是否正常

```bash
# 测试 Less-1 是否能正常访问
curl -s "http://localhost:8080/Less-1/?id=1" | head -20

# 应该返回包含 "Your Login name" 或 "Dumb" 的 HTML
```

## 脚本配置

搭建完成后，修改脚本中的 `TARGET` 变量：

```bash
# scripts/01_get_basic.sh 第二段配置区：
TARGET="http://localhost:8080"  # 改成你的实际地址
```
