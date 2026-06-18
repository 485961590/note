# Docker 使用笔记

> Docker 把应用及其依赖打包成轻量容器，一处构建，处处运行。对靶场场景尤其适用——每个靶场环境依赖不同，容器互不污染。

---

## 概念理解

用日常类比理解三个核心概念：

| 概念                | 类比           | 说明                                                 |
| ----------------- | ------------ | -------------------------------------------------- |
| **镜像（Image）**     | 操作系统 ISO 安装盘 | 只读模板，包含运行应用所需的一切（系统、代码、依赖）                         |
| **容器（Container）** | 用 ISO 装好的虚拟机 | 镜像的运行实例，可启动/停止/删除，各容器相互隔离                          |
| **仓库（Registry）**  | GitHub       | 存放和分发镜像的地方，默认 [Docker Hub](https://hub.docker.com) |

**Docker 和虚拟机的区别：**

```
虚拟机：       硬件 → 宿主机 OS → Hypervisor → 客户机 OS → 应用
容器：         硬件 → 宿主机 OS → Docker 引擎 → 容器（共享内核，无独立 OS）
```

容器不需要独立的操作系统，启动快、占用少、秒级启停。

---

## 安装

### Ubuntu / Debian

```bash
# 卸载旧版本（如果有）
sudo apt remove docker docker-engine docker.io containerd runc

# 安装依赖
sudo apt update
sudo apt install ca-certificates curl

# 添加 Docker 官方 GPG 密钥和仓库
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list

# 安装
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 验证
sudo docker run hello-world

# 将当前用户加入 docker 组（免 sudo 执行 docker 命令）
sudo usermod -aG docker $USER
# 重新登录后生效
```

### CentOS / RHEL

```bash
sudo dnf remove docker docker-client docker-common docker-latest
sudo dnf install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### macOS

```bash
# 下载 Docker Desktop（推荐）
# https://www.docker.com/products/docker-desktop/

# 或通过 Homebrew
brew install --cask docker
```

---

## 镜像管理

```bash
# 搜索镜像
docker search nginx
docker search --filter=stars=100 ubuntu     # 至少 100 星

# 拉取镜像（默认拉取 latest 标签）
docker pull ubuntu
docker pull ubuntu:22.04                     # 指定版本
docker pull nginx:alpine                     # Alpine 版本（体积小）

# 查看本地镜像
docker images
docker image ls

# 查看镜像详细信息
docker inspect ubuntu:22.04

# 查看镜像历史层
docker history nginx

# 删除镜像
docker rmi ubuntu:22.04
docker image prune                           # 删除所有未使用的镜像

# 打标签
docker tag nginx:latest myrepo/nginx:v1.0
```

### 从 Dockerfile 构建镜像

```bash
# 基本构建（-t 指定标签，. 表示构建上下文为当前目录）
docker build -t myapp:v1 .

# 指定 Dockerfile 路径
docker build -f ./docker/Dockerfile -t myapp:v1 .

# 构建时不使用缓存
docker build --no-cache -t myapp:v1 .
```

---

## 容器管理

### 启动与运行

```bash
# 运行一个容器（最常用形式）
docker run -d --name my-nginx -p 8080:80 nginx:alpine
# -d          后台运行
# --name      给容器命名
# -p 8080:80  宿主机端口:容器端口
# nginx:alpine 镜像名:标签

# 交互式运行（进入容器终端）
docker run -it --name test ubuntu:22.04 /bin/bash
# -i  保持 stdin 打开
# -t  分配伪终端

# 运行后自动删除（一次性容器）
docker run --rm -it ubuntu:22.04 /bin/bash

# 挂载目录（宿主机目录:容器目录）
docker run -d --name web -p 80:80 -v /host/path:/container/path nginx

# 传递环境变量
docker run -d --name db -e MYSQL_ROOT_PASSWORD=123456 -e MYSQL_DATABASE=mydb mysql:8

# 限制资源
docker run -d --name app --cpus="1.5" --memory="512m" myapp:v1
```

### 查看容器

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（含已停止的）
docker ps -a

# 查看容器资源占用
docker stats

# 查看容器内进程
docker top my-nginx

# 查看容器日志
docker logs my-nginx
docker logs -f my-nginx            # 实时跟踪
docker logs --tail 50 my-nginx     # 最后 50 行
docker logs --since 10m my-nginx   # 最近 10 分钟

# 查看容器详细信息（IP、挂载、网络等）
docker inspect my-nginx
docker inspect -f '{{.NetworkSettings.IPAddress}}' my-nginx
```

### 进入容器

```bash
# 在运行中的容器内执行命令
docker exec my-nginx ls /etc/nginx/

# 进入交互式 shell
docker exec -it my-nginx /bin/bash
docker exec -it my-nginx /bin/sh       # Alpine 用 sh

# 以特定用户进入
docker exec -it -u root my-nginx /bin/bash
```

### 启停与删除

```bash
# 停止容器
docker stop my-nginx

# 启动已停止的容器
docker start my-nginx

# 重启
docker restart my-nginx

# 暂停 / 恢复（冻结进程，不释放内存）
docker pause my-nginx
docker unpause my-nginx

# 删除容器
docker rm my-nginx
docker rm -f my-nginx                 # 强制删除（含运行中的）
docker container prune                # 删除所有已停止的容器
```

### 文件拷贝

```bash
# 从宿主机拷贝到容器
docker cp ./config.conf my-nginx:/etc/nginx/conf.d/

# 从容器拷贝到宿主机
docker cp my-nginx:/var/log/nginx/access.log ./
```

---

## Dockerfile

Dockerfile 是构建镜像的蓝图，定义镜像的每一层。

### 核心指令

| 指令 | 说明 |
|------|------|
| `FROM` | 指定基础镜像 |
| `RUN` | 在构建时执行命令（安装依赖等） |
| `COPY` | 从宿主机复制文件到镜像 |
| `ADD` | 同 COPY，但支持自动解压 tar 和远程 URL |
| `WORKDIR` | 设置工作目录 |
| `ENV` | 设置环境变量 |
| `EXPOSE` | 声明容器监听的端口（文档作用，不实际发布） |
| `CMD` | 容器启动时默认执行的命令（可被 `docker run` 覆盖） |
| `ENTRYPOINT` | 容器入口命令（不会被覆盖，CMD 作为参数追加） |
| `VOLUME` | 声明挂载点 |
| `USER` | 切换运行用户 |

### 示例：一个 Python Web 应用

```dockerfile
# 指定基础镜像
FROM python:3.11-slim

# 设置工作目录（不存在则自动创建）
WORKDIR /app

# 先复制依赖文件（利用 Docker 缓存层，依赖不变则跳过安装）
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 声明端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 切换为非 root 用户运行（安全性）
RUN useradd -m appuser
USER appuser

# 启动命令
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
```

### .dockerignore

构建时排除不必要的文件，减少构建上下文体积：

```
# .dockerignore
__pycache__
*.pyc
.git
.env
venv/
node_modules/
*.log
```

### 多阶段构建

一个 Dockerfile 中使用多个 `FROM`，在编译阶段安装构建工具，最终镜像只保留运行所需文件：

```dockerfile
# 阶段 1：编译
FROM golang:1.21 AS builder
WORKDIR /src
COPY . .
RUN go build -o /app

# 阶段 2：运行（只复制编译好的二进制，无需 Go 环境）
FROM alpine:3.19
COPY --from=builder /app /usr/local/bin/app
CMD ["app"]
```

---

## Docker Compose

Compose 用 YAML 文件定义多个容器，一条命令统一编排。

### 安装

Docker Desktop 自带。Linux 下若未安装：

```bash
# 插件方式（推荐，与 docker 命令集成）
sudo apt install docker-compose-plugin
docker compose version

# 或独立二进制
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### docker-compose.yml 示例

```yaml
version: "3.8"

services:
  web:
    image: nginx:alpine
    container_name: my-web
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app
    restart: unless-stopped

  app:
    build: ./app                  # 从 ./app/Dockerfile 构建
    container_name: my-app
    expose:
      - "5000"
    environment:
      - DB_HOST=db
      - DB_PASSWORD=${MYSQL_PASS}  # 引用 .env 文件中的变量
    depends_on:
      - db

  db:
    image: mysql:8
    container_name: my-db
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_PASS}
      MYSQL_DATABASE: mydb
    volumes:
      - db_data:/var/lib/mysql    # 命名卷持久化数据
    ports:
      - "3306:3306"

volumes:
  db_data:                         # 声明命名卷
```

### Compose 常用命令

```bash
# 启动所有服务（-d 后台）
docker compose up -d

# 重新构建并启动
docker compose up -d --build

# 停止
docker compose down

# 停止并删除卷（警告：数据丢失）
docker compose down -v

# 查看日志
docker compose logs -f

# 查看服务状态
docker compose ps

# 在指定服务中执行命令
docker compose exec app /bin/bash

# 重启单个服务
docker compose restart web
```

---

## 卷（Volume）与网络（Network）

### 卷：持久化数据

容器删除后，容器内的数据会丢失。卷把数据存到宿主机，独立于容器生命周期。

```bash
# 创建卷
docker volume create mydata

# 查看卷列表
docker volume ls

# 查看卷详细信息
docker volume inspect mydata

# 使用卷挂载（容器内 /data 目录映射到卷）
docker run -d --name app -v mydata:/data nginx

# 绑定挂载（直接映射宿主机路径，开发时常用）
docker run -d --name app -v $(pwd)/src:/app nginx

# 删除未使用的卷
docker volume prune
```

**卷 vs 绑定挂载：**

| | 卷（Volume） | 绑定挂载（Bind Mount） |
|---|---|---|
| 管理方 | Docker 管理 | 用户手动管理 |
| 路径 | `/var/lib/docker/volumes/` 下 | 宿主机任意路径 |
| 可移植性 | 好（跨系统一致） | 差（依赖宿主机路径） |
| 适用场景 | 生产环境持久化数据 | 开发环境热更新代码 |

### 网络：容器间通信

```bash
# 创建自定义网络
docker network create mynet

# 查看网络列表
docker network ls

# 在指定网络中运行容器（同网络下容器可用容器名互相访问）
docker run -d --name db --network mynet mysql:8
docker run -d --name web --network mynet -p 80:80 nginx
# web 容器内可以直接 ping db

# 查看网络详细信息（含连接的容器和 IP）
docker network inspect mynet

# 将运行中的容器接入网络
docker network connect mynet existing-container

# 断开
docker network disconnect mynet existing-container

# 删除网络
docker network rm mynet
```

默认有 `bridge`（默认网桥）、`host`（共享宿主机网络）、`none`（无网络）三种网络模式。

---

## 常用速查

```bash
# 清理所有未使用的资源（镜像、容器、卷、网络）
docker system prune -a

# 查看磁盘占用
docker system df

# 保存镜像为 tar 文件
docker save -o nginx.tar nginx:alpine

# 从 tar 文件加载镜像
docker load -i nginx.tar
```

---

## 从零部署一个靶场环境

> 场景：部署 DVWA（Damn Vulnerable Web Application）+ MySQL，模拟一个 Web 渗透测试环境。靶场涵盖 SQL 注入、XSS、文件上传等常见漏洞。

### 第 1 步：编写 docker-compose.yml

```yaml
# docker-compose.yml
version: "3.8"

services:
  dvwa:
    image: vulnerables/web-dvwa
    container_name: dvwa
    ports:
      - "8080:80"
    environment:
      - DB_SERVER=db
      - DB_USER=dvwa
      - DB_PASSWORD=p@ssw0rd
      - DB_NAME=dvwa
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: mysql:5.7
    container_name: dvwa-db
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: dvwa
      MYSQL_USER: dvwa
      MYSQL_PASSWORD: p@ssw0rd
    volumes:
      - dvwa_db:/var/lib/mysql
    restart: unless-stopped

volumes:
  dvwa_db:
```

### 第 2 步：启动环境

```bash
# 在 docker-compose.yml 所在目录执行
docker compose up -d

# 查看启动状态
docker compose ps
# 应看到 dvwa 和 dvwa-db 两个服务状态为 Up

# 查看日志确认无报错
docker compose logs
```

### 第 3 步：初始化 DVWA 数据库

浏览器打开 `http://<你的IP>:8080`，首次访问会提示数据库未初始化：

1. 点击页面底部的 **Create / Reset Database** 按钮
2. 自动创建表结构
3. 完成后自动跳转到登录页
4. 默认账号：`admin`，密码：`password`

### 第 4 步：验证靶场功能

```bash
# 确认容器在运行
docker ps

# 进入 DVWA 容器查看文件
docker exec -it dvwa /bin/bash
ls /var/www/html/          # 应用代码
ls /var/www/html/vulnerabilities/  # 各漏洞练习目录
```

### 第 5 步：配置 DVWA 安全等级

登录后，左侧菜单 → **DVWA Security** → 选择等级：

- **Low** — 无任何防护（入门）
- **Medium** — 基础防护
- **High** — 较强防护
- **Impossible** — 理论上无漏洞

建议从 Low 开始，逐步提升难度。

### 第 6 步：安装 Kali 工具用于测试

在宿主机或另一台 Kali 虚拟机中，通过 `http://<靶场IP>:8080` 访问靶场：

```bash
# 测试 SQL 注入（以 sqlmap 为例）
sqlmap -u "http://192.168.1.100:8080/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=xxx; security=low"

# 目录爆破
gobuster dir -u http://192.168.1.100:8080 -w /usr/share/wordlists/dirb/common.txt

# 漏洞扫描
nikto -h http://192.168.1.100:8080
```

### 第 7 步：使用完毕后关闭

```bash
# 停止容器（保留数据）
docker compose down

# 停止并删除数据库（下次启动需重新 Create Database）
docker compose down -v
```

### 扩展：同时部署多个靶场

不同靶场用不同端口和 compose 文件隔离，互不影响：

```bash
# 靶场 1：DVWA（端口 8080）
cd ~/labs/dvwa && docker compose up -d

# 靶场 2：Upload-Lab（端口 8081）
cd ~/labs/upload && docker compose up -d

# 靶场 3：Sqli-Labs（端口 8082）
cd ~/labs/sqli && docker compose up -d
```

### 常用靶场镜像速查

| 靶场 | 镜像 / 仓库 |
|------|------------|
| DVWA | `vulnerables/web-dvwa` |
| Sqli-Labs | `acgpiano/sqli-labs` |
| Upload-Lab | `c0ny1/upload-labs` |
| WebGoat | `webgoat/goatandwolf` |
| BWAPP | `raesene/bwapp` |
| VulHub 系列 | `docker pull vulhub/xxx`（[github.com/vulhub/vulhub](https://github.com/vulhub/vulhub)） |
| PortSwigger 官方 | `portswigger/` 系列 |

---

## 参考

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Compose 文件参考](https://docs.docker.com/compose/compose-file/)
- [Dockerfile 最佳实践](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [VulHub 漏洞靶场合集](https://github.com/vulhub/vulhub)
