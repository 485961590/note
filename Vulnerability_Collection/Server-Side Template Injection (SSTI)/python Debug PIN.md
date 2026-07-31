## 什么是Debug Pin码

Debug Pin码是Werkzeug框架（Flask等web框架的底层服务器）在开启调试模式时生成的一个安全密码，用于保护调试器界面不被未授权访问。

对于有文件包含或文件读取的漏洞，且开启debug功能，想要执行执行需要输入pin码
输入pin码可进行命令执行！

Pin码构成：
- username ->执行代码时的用户名
- getattr(app."\_\_name\_\_",app.\_\_class\_\_.\_\_name\_\_) -->默认固定值Flask
- modname -->固定值默认flask.app
- getattr(mod,"\_\_file\_\_",None) -->app.py文件所在路径
- str(uuid.getnode()) -->电脑mac地址
- get_machine_id() -->根据操作系统不同，有四种获取方式

Debug模式
![](./img/Pasted%20image%2020251022014025.png)
![](./img/Pasted%20image%2020251022014753.png)
![](./img/Pasted%20image%2020251022023106.png)
输入pin码即可实现命令执行
## CTF例题
![](./img/Pasted%20image%2020251022022216.png)
flask debug开启了
![](./img/Pasted%20image%2020251022022303.png)
ssrf，还可以读取本地文件
![](./img/Pasted%20image%2020251022022159.png)
存在文件读取漏洞
```文件内容
root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin _apt:x:100:65534::/nonexistent:/usr/sbin/nologin systemd-network:x:101:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin systemd-resolve:x:102:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin messagebus:x:103:104::/nonexistent:/usr/sbin/nologin sshd:x:104:65534::/run/sshd:/usr/sbin/nologin
```

更具内容查看构成pin码的参数
```
- username ->root
- getattr(app."\_\_name\_\_",app.\_\_class\_\_.\_\_name\_\_) -->默认固定值Flask
- modname -->固定值默认flask.app
- getattr(mod,"\_\_file\_\_",None) -->app.py文件所在路径
- str(uuid.getnode()) -->电脑mac地址
- get_machine_id() -->根据操作系统不同，有四种获取方式
```
**getattr(mod,"\_\_file\_\_",None) -->app.py文件所在路径**
有这么个路由http://192.168.245.128:18080/flaskdebug/debug，当开启debug后报错会出现一些有用 信息
	![](./img/Pasted%20image%2020251022023432.png)
	得到/usr/local/lib/python2.7/dist-packages/flask/app.py
**str(uuid.getnode())**
读取对方靶机的mac地址，存放mac的文件可以有如下
- /sys/class/net/lo/address
- /sys/class/net/wlan0/address
- /sys/class/net/eth0/address
		- 得到02:42:ac:11:00:02转换为十进制2252356987191820062
**get_machine_id()**
读取目标机器码
- /etc/machine-id或/proc/1/cgroup
		-得到b7471d41202f4da392a4743b37ea3b69
- /proc/self/cgroup或/etc/machine-id(docker环境，machine_id分为两部分，linux(宿主机)机器码与容器机器码)
		- 得到b7471d41202f4da392a4743b37ea3b69
- 左右拼接

根据所得参数，根据python版本python2.7寻找不同版本的pin码脚本生成对应pin码，

==python2.7的**getattr(mod,"\_\_file\_\_",None) -->app.py文件所在路径**最后是app.pyc==
即使得到/usr/local/lib/python2.7/dist-packages/flask/app.py也需要改成/usr/local/lib/python2.7/dist-packages/flask/app.pyc