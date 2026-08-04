# Docker

> 容器引擎。渗透测试中主要用于快速搭建隔离靶场、运行一次性工具容器、以及做容器逃逸测试。系统学习 Docker 概念和安装步骤见 [Linux-Docker.md](../Linux/Linux-Docker.md)。

---

## 基本语法

```bash
docker <command> [options] [arguments]
docker <管理对象> <操作> [选项]
# 管理对象：image | container | volume | network | system
```

---

## 常用选项速查

### docker run 常用选项

| 选项 | 说明 |
|------|------|
| `-d` | 后台运行 |
| `-it` | 交互模式 + 分配 TTY |
| `--name NAME` | 指定容器名 |
| `-p HOST:CONT` | 端口映射（`8080:80`） |
| `-p IP:HOST:CONT` | 绑定指定 IP 的端口映射 |
| `-v HOST:CONT` | 挂载目录或卷 |
| `--rm` | 退出后自动删除容器 |
| `-e KEY=VALUE` | 设置环境变量 |
| `--network NET` | 指定网络模式 |
| `--privileged` | 特权模式（几乎等同宿主机 root） |
| `--cap-add=SYS_PTRACE` | 添加特定内核能力 |
| `--cap-drop=ALL` | 移除所有能力（最小权限） |
| `--cpus="1.5"` | CPU 限制 |
| `--memory="512m"` | 内存限制 |
| `--restart=always` | 退出后自动重启 |
| `-w /dir` | 设置容器内工作目录 |
| `--entrypoint CMD` | 覆盖镜像默认入口命令 |
| `--user UID:GID` | 以指定用户身份运行 |
| `--security-opt` | 指定 AppArmor / SELinux 标签 |
| `--hostname HOST` | 设置容器主机名 |
| `--dns 8.8.8.8` | 指定 DNS 服务器 |
| `--add-host NAME:IP` | 添加静态主机名解析 |

### 全局选项

| 选项 | 说明 |
|------|------|
| `-D` | 调试模式 |
| `-H HOST` | 指定 Docker daemon 地址（默认 `unix:///var/run/docker.sock`） |
| `--tls` | 启用 TLS 连接远程 daemon |
| `--config DIR` | 指定配置文件目录（默认 `~/.docker`） |

---

## 分类用法

### 1. 镜像操作

```bash
# 搜索镜像
docker search nginx
docker search --filter=stars=100 ubuntu

# 拉取镜像
docker pull nginx:alpine                # 指定标签
docker pull nginx                        # 默认 latest

# 查看本地镜像
docker images
docker image ls
docker images --filter dangling=true     # 只查看悬空镜像

# 查看镜像层历史
docker history nginx:alpine

# 查看镜像详细信息
docker inspect nginx:alpine
docker inspect -f '{{.Os}}' nginx:alpine

# 打标签
docker tag nginx:alpine myrepo/nginx:v1

# 删除镜像
docker rmi nginx:alpine
docker image prune                       # 删除未使用的镜像

# 导出/导入（离线传输）
docker save -o nginx.tar nginx:alpine
docker load -i nginx.tar
```

### 2. 容器生命周期

```bash
# 后台运行服务
docker run -d --name web -p 8080:80 nginx:alpine

# 交互式运行（用完即删）
docker run --rm -it ubuntu:22.04 /bin/bash

# 挂载当前目录运行
docker run --rm -it -v $(pwd):/work -w /work ubuntu:22.04 /bin/bash

# 一次性执行命令
docker run --rm python:3-alpine python -c "print('hello')"

# 启动 / 停止 / 重启
docker start web
docker stop web
docker restart web

# 暂停 / 恢复进程（不释放内存）
docker pause web
docker unpause web

# 删除容器
docker rm web
docker rm -f web                         # 强制删除（含运行中的）
docker container prune                   # 删除所有已停止的容器
```

### 3. 容器交互与调试

```bash
# 进入运行中的容器
docker exec -it web /bin/bash
docker exec -it web /bin/sh              # Alpine 用 sh

# 在容器内执行单条命令
docker exec web cat /etc/nginx/nginx.conf

# 查看日志
docker logs web
docker logs -f web                       # 实时跟踪
docker logs --tail 50 web                # 最后 50 行
docker logs --since 5m web               # 最近 5 分钟

# 查看容器内进程
docker top web

# 查看资源占用
docker stats
docker stats --no-stream                 # 只输出一次

# 查看容器详细信息
docker inspect web
docker inspect -f '{{.NetworkSettings.IPAddress}}' web
docker inspect -f '{{.State.Status}}' web

# 查看端口映射
docker port web

# 查看容器文件变更
docker diff web

# 文件拷贝
docker cp ./local.conf web:/etc/nginx/conf.d/
docker cp web:/var/log/nginx/access.log ./
```

### 4. 网络操作

```bash
# 查看网络列表
docker network ls

# 创建自定义网络（容器间可用容器名互相访问）
docker network create mynet

# 查看网络详情（含连接的容器和 IP）
docker network inspect mynet

# 在指定网络中运行容器
docker run -d --name db --network mynet mysql:8
docker run -d --name web --network mynet -p 80:80 nginx:alpine
# web 容器内可直接 ping db

# 将运行中的容器接入/断开网络
docker network connect mynet existing-container
docker network disconnect mynet existing-container

# 删除网络
docker network rm mynet
docker network prune
```

**网络模式速查：**

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `bridge`（默认） | 独立网络栈，需 `-p` 发布端口 | 一般用途 |
| `host` | 共享宿主机网络栈，无需端口映射 | 高性能扫描 |
| `none` | 无网络 | 完全隔离 |
| `container:NAME` | 共享指定容器的网络栈 | 网络调试 |

### 5. 数据卷与文件交换

```bash
# 卷管理
docker volume create mydata
docker volume ls
docker volume inspect mydata
docker volume rm mydata
docker volume prune                      # 删除未使用的卷

# 命名卷挂载（Docker 管理，生产用）
docker run -d -v mydata:/data nginx:alpine

# 绑定挂载（直接映射宿主机路径，开发用）
docker run -d -v /host/path:/container/path nginx:alpine

# 只读挂载
docker run -d -v /host/path:/container/path:ro nginx:alpine

# 挂载另一个容器的卷
docker run -d --volumes-from source-container nginx:alpine

# 用 docker cp 做一次性文件传输（不需要挂载）
docker cp ./payload.sh target:/tmp/
docker exec target /tmp/payload.sh
```

### 6. Docker Compose CLI

```bash
# 启动所有服务
docker compose up -d

# 重新构建镜像并启动
docker compose up -d --build

# 停止并删除容器/网络
docker compose down

# 停止并删除容器/网络/卷
docker compose down -v

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
docker compose logs -f web              # 只看指定服务

# 进入服务容器
docker compose exec web /bin/bash

# 在服务中执行一次性命令
docker compose run --rm app python manage.py migrate

# 重启单个服务
docker compose restart web

# 拉取最新镜像
docker compose pull

# 查看 Compose 配置（调试用）
docker compose config
```

旧版 `docker-compose`（Python 独立二进制，带连字符）和新版 `docker compose`（Docker CLI 插件，空格分隔）命令参数基本一致，脚本中建议用新版。

### 7. 系统管理

```bash
# 查看 Docker 系统信息
docker info
docker version

# 查看磁盘占用
docker system df
docker system df -v                      # 详细模式

# 一键清理（镜像+容器+网络+构建缓存）
docker system prune
docker system prune -a                   # 含所有未使用的镜像
docker system prune -a --volumes         # 含未使用的卷

# 登录/登出镜像仓库
docker login
docker login registry.example.com
docker logout
```

---

## Dockerfile 速查

### 核心指令

| 指令 | 说明 | 示例 |
|------|------|------|
| `FROM` | 基础镜像 | `FROM python:3.11-slim` |
| `RUN` | 构建时执行命令 | `RUN apt update && apt install -y curl` |
| `COPY` | 复制文件到镜像 | `COPY . /app` |
| `ADD` | 同 COPY，额外支持 URL 和 tar 自动解压 | `ADD archive.tar.gz /app` |
| `WORKDIR` | 设置工作目录 | `WORKDIR /app` |
| `ENV` | 设置环境变量 | `ENV NODE_ENV=production` |
| `EXPOSE` | 声明监听端口（文档作用） | `EXPOSE 8080` |
| `CMD` | 默认启动命令 | `CMD ["python", "app.py"]` |
| `ENTRYPOINT` | 入口命令（不会被 run 覆盖） | `ENTRYPOINT ["docker-entrypoint.sh"]` |
| `VOLUME` | 声明挂载点 | `VOLUME /data` |
| `USER` | 切换运行用户 | `USER 1000` |
| `ARG` | 构建参数 | `ARG VERSION=latest` |
| `HEALTHCHECK` | 健康检查 | `HEALTHCHECK --interval=30s CMD curl -f http://localhost/` |

### 最小示例

```dockerfile
FROM python:3.11-slim
WORKDIR /tool
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python", "scan.py"]
```

```bash
docker build -t my-scanner .
docker run --rm my-scanner -t target.com
```

---

## 实用场景

### 场景1：运行 Kali 工具（免装完整 Kali）

```bash
# 启动 Kali 容器
docker run --rm -it kalilinux/kali-rolling /bin/bash
# 容器内按需安装工具
apt update && apt install -y nmap metasploit-framework

# 直接用预装好工具的镜像
docker run --rm instrumentisto/nmap -sV -p 1-1000 target.com
docker run --rm -v $(pwd):/data wpscanteam/wpscan --url https://target.com
```

### 场景2：临时 HTTP 服务（文件传输）

```bash
# Python HTTP Server（快速传文件）
docker run --rm -d -p 8000:8000 -v /path/to/files:/files -w /files python:3-alpine python -m http.server 8000

# Nginx 静态文件
docker run --rm -d -p 8080:80 -v /path/to/html:/usr/share/nginx/html:ro nginx:alpine
```

### 场景3：端口转发 / 内网代理

```bash
# socat 端口转发
docker run --rm -d --name fwd -p 4444:4444 alpine/socat TCP-LISTEN:4444,fork,reuseaddr TCP:internal-host:4444

# 挂载宿主机网络栈做全端口转发
docker run --rm -it --network host alpine/socat TCP-LISTEN:8080,fork TCP:10.0.0.5:80
```

### 场景4：特权容器与逃逸测试

```bash
# 特权容器（几乎拥有宿主机全部能力）
docker run --rm -it --privileged ubuntu:22.04 /bin/bash

# 挂载宿主机根目录
docker run --rm -it -v /:/host ubuntu:22.04 /bin/bash
# 在容器内 chroot /host 即可操作宿主机文件系统

# 挂载 Docker Socket（经典逃逸手法）
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock docker:latest sh
# 容器内执行 docker ps 看到的是宿主机的容器
# docker run -v /:/host --privileged ... 即可逃逸
```

### 场景5：批量管理靶场

```bash
# 不同靶场用不同端口隔离
docker run -d --name dvwa -p 8081:80 vulnerables/web-dvwa
docker run -d --name sqli -p 8082:80 acgpiano/sqli-labs
docker run -d --name upload -p 8083:80 c0ny1/upload-labs

# 查看所有靶场状态
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"

# 批量停止
docker stop dvwa sqli upload

# 批量清理
docker rm -f dvwa sqli upload
```

### 场景6：跨架构编译 Exploit

```bash
# x86 机器上编译 ARM 架构的 exploit
docker run --rm -v $(pwd):/src -w /src arm32v7/gcc:latest gcc -static -o exploit exploit.c

# 编译 32 位 ELF（在 64 位机器上）
docker run --rm -v $(pwd):/src -w /src i386/gcc:latest gcc -m32 -static -o exploit exploit.c
```

### 场景7：无痕测试

```bash
# --rm 保证容器退出后不留文件系统痕迹
docker run --rm -it -v $(pwd)/output:/output kalilinux/kali-rolling /bin/bash
# 所有产出写入挂载的 output 目录
# 容器本身退出即销毁，宿主机不留容器残留
# docker ps -a 中不会出现已退出的容器
```

### 场景8：快速搭建本地测试 API

```bash
# 一行搭一个 Flask API
docker run --rm -d -p 5000:5000 python:3-slim sh -c \
  "pip install flask && python -c \"
from flask import Flask, request
app = Flask(__name__)
@app.route('/test/<id>')
def test(id): return f'ID: {id}'
app.run(host='0.0.0.0', port=5000)\""

# 测试
curl http://localhost:5000/test/123
```

---

## 常用安全/工具镜像速查

| 镜像 | 用途 |
|------|------|
| `kalilinux/kali-rolling` | Kali 完整工具链 |
| `instrumentisto/nmap` | Nmap 端口扫描 |
| `rustscan/rustscan` | 高速端口扫描（Rust 实现） |
| `wpscanteam/wpscan` | WordPress 漏洞扫描 |
| `byt3bl33d3r/crackmapexec` | 内网横向移动 |
| `vulnerables/web-dvwa` | DVWA 靶场 |
| `acgpiano/sqli-labs` | SQL 注入靶场 |
| `c0ny1/upload-labs` | 文件上传靶场 |
| `webgoat/goatandwolf` | WebGoat 靶场 |
| `alpine/socat` | 端口转发/网络瑞士军刀 |
| `python:3-alpine` | 轻量 Python（~50MB） |
| `node:alpine` | 轻量 Node.js |
| `nginx:alpine` | 临时 HTTP 服务 |
| `docker:latest` | Docker-in-Docker / socket 挂载 |

---

## 注意事项

1. **docker 组成员等同于 root**：任何在 docker 组中的用户可以轻易提权到宿主机 root，`docker run -v /:/host` 即可读写宿主机全部文件。
2. **不要暴露 Docker daemon 端口**：`-H tcp://0.0.0.0:2375` 无 TLS 保护时，等于未授权的 root 远程访问。
3. **挂载 docker.sock 是危险操作**：容器内可操控宿主机所有容器和镜像，是容器逃逸的常见切入点。
4. **特权容器 (`--privileged`) 拥有宿主机几乎所有内核能力**：仅在容器逃逸测试或特殊场景下使用。
5. **定期清理磁盘**：`docker system prune -a` 清理悬空镜像和停止的容器，否则 /var/lib/docker 会持续膨胀。
6. **`--rm` 是好习惯**：测试用容器加上 `--rm`，避免遗留大量停止的无用容器。
7. **端口冲突**：多个靶场使用不同宿主机端口映射（`-p 8081:80`, `-p 8082:80`），别让两个容器抢同一个宿主机端口。
8. **资源限制**：在低配 VPS 上跑多个容器时，用 `--cpus` 和 `--memory` 限制单个容器的资源用量。

---

## 参考

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Dockerfile 最佳实践](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Compose CLI 参考](https://docs.docker.com/compose/reference/)
- [VulHub 漏洞靶场合集](https://github.com/vulhub/vulhub)
- [HackTricks - Docker 逃逸](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-security)
