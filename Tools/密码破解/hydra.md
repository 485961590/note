# Hydra 使用指南

Hydra（THC Hydra）用于对已经确认开放的认证服务进行账号密码组合测试。适合在授权靶场、自己的实验环境或明确授权的测试范围内使用。

本文只记录日常能直接用上的命令。示例目标使用 `192.0.2.10`、`192.0.2.20` 等文档保留地址，不代表真实目标。

## 1. 安装和确认

Kali / Debian：

```bash
sudo apt update
sudo apt install hydra
```

确认安装和查看帮助：

```bash
hydra -h
hydra -U ssh
hydra -U http-post-form
```

`-U` 用来查看某个模块的专用参数。遇到命令格式不确定时，优先以本机 `hydra -U 模块名` 为准，因为不同版本支持的模块和参数可能不同。

## 2. 先记住基本格式

```bash
hydra [通用选项] [目标] [服务模块] [模块参数]
```

最常见的写法：

```bash
# 一个用户名 + 一个密码字典
hydra -l USERNAME -P passwords.txt ssh://192.0.2.10

# 用户名字典 + 密码字典
hydra -L users.txt -P passwords.txt ftp://192.0.2.20

# 用户名和密码已经配对，每行一个 login:password
hydra -C combos.txt ssh://192.0.2.10
```

常用选项：

| 选项 | 作用 |
|---|---|
| `-l USER` | 指定一个用户名 |
| `-L FILE` | 从文件读取用户名，每行一个 |
| `-p PASS` | 指定一个密码 |
| `-P FILE` | 从文件读取密码，每行一个 |
| `-C FILE` | 读取 `用户名:密码` 组合文件 |
| `-M FILE` | 从文件读取多个目标，每行一个主机或地址 |
| `-s PORT` | 指定非默认端口 |
| `-t N` | 并发任务数；建议从 `4` 或 `8` 开始 |
| `-f` | 当前目标找到一组有效凭据后停止 |
| `-F` | 多目标模式下任意目标找到凭据后停止 |
| `-e nsr` | 额外尝试空密码、用户名作为密码、用户名倒写 |
| `-o FILE` | 将结果保存到文件 |
| `-v` | 显示较详细的运行信息 |
| `-V` | 显示每一次尝试；排错有用，但会把测试内容打到终端 |
| `-w SEC` | 等待服务响应的时间 |
| `-W SEC` | 每次建立新连接之间的等待时间 |
| `-I` | 不等待恢复文件提示，直接开始 |
| `-R` | 恢复上一次中断的任务 |

用户名、密码字典的基本格式：

```text
admin
test
alice
```

组合文件的格式：

```text
admin:admin123
test:test123
```

## 3. 推荐的实际流程

### 第一步：确认端口和服务

Hydra 不是服务识别工具。先确认端口确实开放、协议没有弄错：

```bash
nmap -sV -p 21,22,80,443,3389 192.0.2.10
```

例如目标开放的是 SSH，就使用 `ssh` 模块；开放的是 Web 登录表单，就使用 `http-post-form` 或 `https-post-form`，不能只因为端口是 `80` 就直接套用 SSH 命令。

### 第二步：先用一个账号和很短的字典验证

先确认网络、用户名、模块和结果判断都正确：

```bash
hydra -l test -P short-passwords.txt ssh://192.0.2.10 -t 4 -f -V
```

验证成功后再换成完整字典。这样可以避免一开始就跑很久，最后才发现模块或参数写错。

### 第三步：保存结果并控制并发

```bash
hydra -L users.txt -P passwords.txt ssh://192.0.2.10 \
  -t 4 -w 10 -f -o hydra-ssh.txt
```

`-t` 越大不一定越快。SSH、FTP 或 Web 应用可能有连接数限制、账号锁定和速率限制，通常先从 `4` 开始，根据服务稳定性逐步调整。

### 第四步：查看结果

成功时终端会出现类似内容：

```text
[22][ssh] host: 192.0.2.10   login: test   password: example123
```

输出文件只用于记录授权测试结果。不要把真实密码、Token 或结果文件提交到公共仓库。

## 4. 常见服务用法

### SSH

默认 22 端口：

```bash
hydra -l test -P passwords.txt ssh://192.0.2.10 \
  -t 4 -f -o ssh-result.txt
```

非默认端口：

```bash
hydra -l test -P passwords.txt -s 2222 ssh://192.0.2.10 \
  -t 4 -f -o ssh-2222-result.txt
```

多个用户名：

```bash
hydra -L users.txt -P passwords.txt ssh://192.0.2.10 \
  -t 4 -e nsr -f
```

`ssh` 只适合测试 SSH 密码认证。目标如果只允许密钥登录，继续换密码字典不会得到结果，应先确认服务端确实开启了密码认证。

### FTP

```bash
hydra -L users.txt -P passwords.txt ftp://192.0.2.20 \
  -t 4 -f -o ftp-result.txt
```

FTP 使用非默认端口时：

```bash
hydra -l test -P passwords.txt -s 2121 ftp://192.0.2.20 -t 4 -f
```

### HTTP Basic Auth

如果浏览器弹出用户名和密码对话框，通常是 HTTP Basic Auth，可以尝试 `http-get`：

```bash
hydra -l admin -P passwords.txt 192.0.2.30 \
  http-get /admin -t 4 -f
```

HTTPS Basic Auth：

```bash
hydra -l admin -P passwords.txt 192.0.2.30 \
  https-get /admin -t 4 -f
```

具体模块参数可以用下面的命令查看：

```bash
hydra -U http-get
hydra -U https-get
```

### HTTP POST 表单

HTTP 表单的核心格式是：

```text
路径:提交参数:失败标记
```

示例登录请求为 `POST /login`，表单字段为 `username` 和 `password`，错误页面包含 `Invalid credentials`：

```bash
hydra -l admin -P passwords.txt 192.0.2.30 \
  http-post-form "/login:username=^USER^&password=^PASS^:F=Invalid credentials" \
  -t 4 -f -V
```

HTTPS 表单：

```bash
hydra -l admin -P passwords.txt 192.0.2.31 \
  https-post-form "/login:username=^USER^&password=^PASS^:F=Invalid credentials" \
  -t 4 -f -o https-form-result.txt
```

这里的特殊占位符：

| 写法 | 含义 |
|---|---|
| `^USER^` | Hydra 当前尝试的用户名 |
| `^PASS^` | Hydra 当前尝试的密码 |
| `F=text` | 响应中出现 `text` 时，判断登录失败 |
| `S=text` | 响应中出现 `text` 时，判断登录成功 |
| `H=Header: value` | 为请求添加额外请求头，具体格式以 `hydra -U http-post-form` 为准 |

用 `F=` 还是 `S=`：

- 页面无论成功失败都会返回 `200` 时，优先找稳定的失败文字，例如 `F=用户名或密码错误`。
- 成功后会固定跳转或出现固定文字时，可以使用 `S=Welcome` 或其他明确成功标记。
- 标记必须来自真实响应，不能凭页面标题猜测。先用浏览器开发者工具、Burp 或 curl 分别记录一次成功和失败响应，再选择只在对应场景出现的文字。

如果请求正文中有多个字段，按服务实际提交内容补上：

```bash
hydra -l admin -P passwords.txt 192.0.2.30 \
  http-post-form "/user/login:username=^USER^&password=^PASS^&submit=Login:F=Login failed" \
  -t 4 -f
```

注意事项：

- 整个表单参数建议放在双引号中，避免 `&` 被 shell 当作命令分隔符。
- 路径从 `/` 开始，不能直接把完整 URL 塞进第一个字段。
- 登录接口如果每次都需要变化的 CSRF Token、验证码、动态 Cookie 或复杂 JSON，Hydra 通常不适合直接处理。先确认请求是否能在固定参数下重复提交。
- 失败标记写错会造成假阳性，看到“成功”后必须手工用该账号密码登录确认。

### 其他常见模块

先确认本机是否有对应模块：

```bash
hydra -U rdp
hydra -U mysql
hydra -U postgres
hydra -U smb
```

常见写法：

```bash
# RDP
hydra -l administrator -P passwords.txt rdp://192.0.2.40 -t 2 -f

# MySQL
hydra -l root -P passwords.txt mysql://192.0.2.50 -t 4 -f

# PostgreSQL 非默认端口
hydra -l postgres -P passwords.txt -s 5433 postgres://192.0.2.51 -t 4 -f
```

数据库、RDP、SMB 等服务的认证行为和锁定策略差异较大，先用小字典验证，并查看模块帮助中的专用参数。

## 5. 多目标和组合测试

多个目标放入文件，每行一个：

```text
192.0.2.10
192.0.2.11
192.0.2.12
```

批量测试：

```bash
hydra -M targets.txt -l test -P passwords.txt ssh \
  -t 4 -F -o multi-target-result.txt
```

目标文件也可以写主机名和端口，具体格式以本机版本的帮助为准。批量模式前先确认文件中的所有地址都在授权范围内。

如果已经有明确的账号密码对应关系，使用 `-C`，不要把组合文件拆开后制造大量无意义的尝试：

```bash
hydra -C combos.txt ssh://192.0.2.10 -t 4 -f
```

## 6. 字典整理

字典通常是一行一个值，空行和 Windows 换行符有时会导致排查困难：

```bash
# 删除空行
sed -i '/^$/d' passwords.txt

# 去掉 Windows 换行符中的回车字符
sed -i 's/\r$//' passwords.txt

# 查看行数和前几行
wc -l passwords.txt
head passwords.txt
```

Kali 中常见字典位置：

```bash
/usr/share/wordlists/rockyou.txt
/usr/share/seclists/
```

如果 `rockyou.txt` 是压缩文件，先解压再使用：

```bash
sudo gzip -dk /usr/share/wordlists/rockyou.txt.gz
```

实际测试建议按这个顺序缩小范围：

1. 已知用户名 + 少量候选密码。
2. 已知用户名 + 针对目标环境整理的字典。
3. 多个用户名 + 针对性字典。
4. 只有在授权范围和测试目标都明确时，才考虑更大的字典或掩码。

## 7. 中断、恢复和排错

### 中断后恢复

Hydra 被中断后可能生成恢复文件。恢复上次任务：

```bash
hydra -R
```

如果不想使用旧的恢复状态，可以换一个工作目录或清理对应恢复文件；删除前先确认文件属于当前任务，避免误删其他测试记录。

### 常见问题

#### `unknown service` 或模块不存在

```bash
hydra -h
hydra -U 模块名
```

检查服务模块拼写、Hydra 版本和是否安装了完整版本。

#### 一直没有结果

按下面顺序检查：

1. 端口是否开放，服务类型是否识别正确。
2. 用户名和密码文件是否真的有内容，是否有多余的 `\r`。
3. 服务是否允许密码认证。
4. Web 表单的路径、字段名和失败标记是否来自真实请求。
5. 是否触发了限速、验证码、账号锁定或防火墙策略。
6. 先把 `-t` 降到 `1` 或 `2`，再用 `-V` 观察少量尝试。

#### HTTP 显示很多成功

大概率是 `F=` 失败标记不准确，或者服务对所有请求都返回相同页面。分别保存一次正确密码和错误密码的响应，找出真正不同的内容；确认后再重跑，并手工验证结果。

#### SSH 报连接失败或超时

降低并发并增加等待时间：

```bash
hydra -l test -P passwords.txt ssh://192.0.2.10 \
  -t 2 -w 15 -f
```

如果服务端有连接频率限制，继续加大 `-t` 只会让失败更多。

#### 任务太慢

先确认是不是字典过大，而不是盲目提高并发。只在授权环境中逐步调整：

```bash
hydra -l test -P passwords.txt ssh://192.0.2.10 \
  -t 8 -w 10 -f
```

## 8. 一个可直接改的模板

### SSH / FTP / 数据库类服务

```bash
hydra -l '用户名' -P '密码字典' \
  '服务://目标地址' -s 端口 -t 4 -w 10 -f \
  -o '结果文件'
```

默认端口时可以去掉 `-s 端口`。用户名是文件时，把 `-l` 换成 `-L 用户名字典`；单个密码时，把 `-P` 换成 `-p 密码`。

### HTTP POST 表单

```bash
hydra -l '用户名' -P '密码字典' '目标地址' \
  http-post-form \
  '/登录路径:字段1=^USER^&字段2=^PASS^:F=失败提示文字' \
  -t 4 -w 10 -f -o '结果文件'
```

HTTPS 使用 `https-post-form`。如果以成功标记判断，将最后一段改为 `S=成功提示文字`。

## 9. 安全边界

- 只对自己拥有或已获得明确授权的目标运行。
- 先确认账号锁定、告警和速率限制策略，测试账号优先使用专门的实验账号。
- 不要直接把真实生产密码、Token、Cookie 放进字典或结果文件。
- 不要把大字典、高并发和批量目标组合成一次未经评估的任务。
- 测试结束后妥善保存或删除包含凭据的结果文件，并在报告中记录测试范围、时间、字典来源和并发参数。

## 快速记忆

```bash
# 单用户 + 密码字典
hydra -l USER -P PASS.txt ssh://TARGET -t 4 -f

# 用户名字典 + 密码字典
hydra -L USERS.txt -P PASS.txt ftp://TARGET -t 4 -f

# 用户名:密码组合
hydra -C COMBOS.txt ssh://TARGET -t 4 -f

# 非默认端口
hydra -l USER -P PASS.txt -s 2222 ssh://TARGET -t 4 -f

# HTTP POST 表单
hydra -l USER -P PASS.txt TARGET \
  http-post-form '/login:user=^USER^&pass=^PASS^:F=Login failed' \
  -t 4 -f
```
