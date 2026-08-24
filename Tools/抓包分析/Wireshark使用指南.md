# Wireshark 使用指南

> [!abstract] 这篇笔记解决什么问题
> Wireshark 是最经典的抓包分析工具。平时课程实验（计网的 TCP 三次握手）、CTF 流量分析题、排查"这个程序到底连了谁"，都用得上。这篇按"用的时候翻一翻"的思路整理，重点放在**过滤器**和**常用操作**上。

---

## 1. Wireshark 是什么

抓包 = 把网卡上进出的数据包复制一份存下来看。Wireshark 就是干这个的图形化工具，能解析几百种协议，把二进制字节翻译成人能读懂的字段。

**什么时候用：**
- 计算机网络课程实验（观察 TCP 三次握手、四次挥手、ARP、DNS）
- CTF Misc 方向的流量分析题
- 排查自己电脑上某个软件的联网行为
- 分析明文协议（HTTP、FTP、Telnet、DNS）传输的内容

**替代/搭配工具：**
- Fiddler / Burp Suite：偏 HTTP/HTTPS 抓包改包（安全测试常用），Wireshark 更底层、更通用
- tcpdump：命令行版，Linux 服务器上没图形界面时用
- 三者不冲突，学安全建议 Wireshark 必会

安装：Windows 直接官网下，Kali 自带。

---

## 2. 界面认识

打开后主界面三块，从上到下：

| 面板 | 作用 |
|---|---|
| 包列表面板 | 每行一个数据包：序号、时间、源/目的地址、协议、长度、Info 摘要 |
| 包详情面板 | 选中包后，按协议层展开：Frame → Ethernet → IP → TCP → HTTP，点开能看到每个字段的值 |
| 字节面板 | 最原始的十六进制字节，左边十六进制右边 ASCII，详情面板选中字段时这里会高亮对应字节 |

上面是工具栏和**显示过滤器栏**（最常用的东西），左上角开始/停止抓包的鲨鱼鳍按钮。

---

## 3. 抓包基本流程

1. 双击选中的网卡开始抓包（看哪个网卡有波形图就是哪个在活动，无线一般是 WLAN，有线是以太网）
2. 去做你要分析的操作（打开网页、登录等）
3. 点红色方块停止
4. 保存为 `.pcapng` 文件（CTF 题目里给的 `.pcap` 也是这个家族）

> [!tip] 混杂模式（Promiscuous Mode）
> 默认网卡只收发给自己的包。开启混杂模式（捕获选项里勾选）后，局域网内广播等流量也收。注意：在交换机网络里，**别人单播的包依然到不了你网卡**，不是开了混杂就全能抓到。WiFi 抓原始 802.11 帧需要监听模式（Monitor Mode），Windows 上支持较差。

---

## 4. 两种过滤器（重点，必会）

Wireshark 有两套过滤器，**语法不通用**，新手最容易在这里懵：

| | 捕获过滤器 Capture Filter | 显示过滤器 Display Filter |
|---|---|---|
| 生效时机 | 抓包**之前**设置，决定抓什么 | 抓完（或抓着）随时改，决定显示什么 |
| 位置 | 捕获选项界面里 | 主界面过滤器栏 |
| 语法 | BPF 语法（tcpdump 同款） | Wireshark 自有语法 |
| 例子 | `host 192.168.1.1` | `ip.addr == 192.168.1.1` |
| 建议 | 需要时才用（减体积） | **日常主力**，先全抓再筛 |

> [!warning] 常见报错
> 在显示过滤器栏里写 `host 192.168.1.1` 会显示红色报错——因为那是捕获过滤器语法。显示过滤器要用 `ip.addr ==` 这种写法。栏变**绿色**表示语法合法，**红色**表示写错了。

### 4.1 捕获过滤器（BPF 语法，够用版）

```
host 192.168.1.100        # 只抓与这台主机的流量
src host 10.0.0.5         # 只抓源为它的
dst host 10.0.0.5         # 只抓目的为它的
port 80                   # 只抓 80 端口
!port 22                  # 排除 SSH（远程操作服务器抓包时必加，不然自己刷屏）
net 192.168.1.0/24        # 抓这个网段
tcp                       # 只抓 TCP
udp                       # 只抓 UDP
arp or icmp               # 抓 ARP 或 ICMP
```

用 `and` / `or` / `not` 组合：

```
host 192.168.1.100 and port 80
tcp port 443 and host www.example.com
not broadcast and not arp
```

### 4.2 显示过滤器速查（日常够用）

```
# --- 按协议 ---
http / dns / arp / icmp / tcp / udp / tls / ftp / telnet
!(arp or dns or icmp)           # 排除噪音（浏览器一开就一堆 mDNS/ARP）

# --- 按 IP ---
ip.addr == 192.168.1.100        # 源或目的任一是它（最常用）
ip.src == 192.168.1.100         # 只看它发出去的
ip.dst == 192.168.1.100         # 只看发给它的

# --- 按端口 ---
tcp.port == 80
udp.port == 53

# --- 按 HTTP 内容 ---
http.request.method == "POST"   # 抓登录表单基本靠它
http.request                    # 所有请求
http.response.code == 404       # 响应码筛选
http contains "password"        # 包内容包含某字符串（区分大小写）
http.request.uri contains "login"

# --- DNS ---
dns.qry.name contains "baidu"   # 查过哪些百度域名

# --- TCP 标志位（计网实验常客）---
tcp.flags.syn == 1 && tcp.flags.ack == 0    # 三次握手第一步 SYN
tcp.flags.syn == 1 && tcp.flags.ack == 1    # SYN+ACK 第二步
tcp.flags.fin == 1                         # 四次挥手
tcp.analysis.retransmission                # 重传包（网络质量差的表现）

# --- 内容搜索（不限协议，万能）---
frame contains "flag{"          # CTF 找 flag 神器
```

> [!tip] 两个提效技巧
> 1. **右键 → Apply as Filter**：在详情面板里右键任意字段（如 ip.src），可以一键把它设为过滤器，不用手敲字段名。字段名忘了就右键看。
> 2. **过滤器栏旁的 + 号**：能把当前过滤器存成按钮，一点就切换，适合反复对比的场景。

---

## 5. 必会操作

### 5.1 Follow Stream（跟踪流）⭐ 最常用

一个 HTTP 页面/一次登录由很多包组成，一个个看太累。Follow Stream 把一次 TCP/HTTP 会话**重组还原成完整对话**，客户端发的一段、服务器回的一段直接 readable。

操作：选中某个包 → 右键 → Follow → **TCP Stream**（或 HTTP Stream）。看完点左下角 `Filter Out This Stream` 可以把这条流从视图里排除，剩下的接着看下一条。

### 5.2 导出对象（Export Objects）

**File → Export Objects → HTTP**：把流量里的 HTTP 对象（图片、JS、下载的文件）直接列出来，选中就能另存。CTF 里"从流量包里恢复图片/文件"基本就是这一步。

### 5.3 统计功能

- **Statistics → Conversations**：谁和谁聊得最多（IP/TCP/UDP 各有标签页），判断"到底连了哪个服务器"很快
- **Statistics → Protocol Hierarchy**：流量协议占比，pcap 里有没有藏 HTTP、有没有异常协议一眼看出
- **Statistics → I/O Graph**：流量随时间的曲线

### 5.4 时间显示格式

**View → Time Display Format**：默认是绝对时间，抓包分析常切到 "Seconds Since Previous Packet / Captured Frame"，方便看握手间隔、重传耗时。

### 5.5 查找

**Ctrl+F** 查找包，可按字符串搜（搜索范围记得选 "Packet bytes"），配合 `frame contains` 一个意思。

---

## 6. 实战场景

### 场景 A：看 HTTP 明文登录密码

1. 开始抓包，访问一个 **HTTP**（非 HTTPS）网站并登录（找个老站或自己搭的靶场）
2. 过滤器：`http.request.method == "POST"`
3. 找到登录那个包，Follow HTTP Stream，或直接看详情面板 HTTP 层的 `application/x-www-form-urlencoded`，表单里 `username=xxx&password=xxx` 明晃晃

> [!note] 这就是为什么 HTTPS 重要
> 同样的操作对 HTTPS 流量只能看到 TLS 加密数据。HTTPS 抓不到明文是**正常的**。想分析自己的 HTTPS 流量，可以设环境变量 `SSLKEYLOGFILE` 让浏览器导出密钥，然后在 Wireshark 的 TLS 协议设置里导入该文件即可解密（调试自己的程序时有用）。

### 场景 B：观察 TCP 三次握手（课程实验）

1. 过滤器：`tcp.flags.syn == 1 || tcp.flags.fin == 1`
2. 打开一个新网页，开头的 [SYN] → [SYN, ACK] → [ACK] 就是三次握手
3. 想单独看某一条连接：选中其中一个包右键 Follow → TCP Stream，过滤器变成 `tcp.stream eq 0`，这就是第 0 条流
4. 改 `tcp.stream eq 1`、`eq 2` 可以遍历每条连接

相关协议笔记：[[HTTPandHTTPS]]、[[DNS]]、[[ARP]]

### 场景 C：DNS 查询分析

1. 过滤器：`dns`
2. 每条查询展开看 Queries 字段是问的什么域名，Answers 是解析结果
3. `dns.qry.type == 1` 筛 A 记录，`== 28` 筛 AAAA（IPv6）

### 场景 D：CTF 流量分析题套路

1. 打开 pcap → 先看 **Protocol Hierarchy**，了解流量构成
2. `http` 过滤 → 有文件就 **Export Objects**
3. 搜关键字：`frame contains "flag"` 或 Ctrl+F 搜 `flag{`、`ctf`
4. 可疑会话逐条 Follow Stream（配合 Filter Out This Stream 排除法）
5. 没思路时想：是不是传输了压缩包/图片？（Export Objects 找）是不是藏在 DNS 查询里？（看 dns）是不是 USB 流量？（usb 过滤，另查专门方法）

---

## 7. 快捷键

| 快捷键 | 功能 |
|---|---|
| `Ctrl+E` | 开始 / 停止抓包 |
| `Ctrl+S` | 保存抓包文件 |
| `Ctrl+F` | 查找 |
| `Ctrl+G` | 跳转到指定包序号 |

另外右键包 → **Colorize Conversation** 可以给一条会话整体上色，多会话对比时很好用。

---

## 8. 常见坑

- **抓不到包**：九成是选错网卡。先 ping 一下外网，看哪个网卡波形在动。
- **过滤器报红**：显示过滤器和捕获过滤器语法混用了（见第 4 节）。
- **全是 TLS 看不懂**：正常，现代网站都是 HTTPS。想要 HTTP 明文得找老站/靶场。
- **保存格式**：保存选 `.pcapng`（多网卡、注释都支持）；题目给 `.pcap` 老格式也能开。
- **远程 SSH 里抓服务器包**：捕获过滤器加 `!port 22`，否则抓的全是自己终端的画面。
- **抓包有法律边界**：只抓自己有权限的设备和网络。校园网里抓别人流量属于违规，别拿实验环境之外的目标练手。
