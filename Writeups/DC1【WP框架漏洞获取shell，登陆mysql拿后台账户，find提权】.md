## 信息收集（Information Gathering）
确定目标IP：`arp-scan -I eth0 -l`
![](file-20260902195421551.png)
端口与服务扫描：`nmap -sS -sV -O -A  -p- 192.168.230.157`
![](file-20260902195421553.png)
`fscan -h 192.168.230.157 -p 22,80,111,437222`
![](file-20260902195421554.png)
Web指纹探测：`whatweb -a 3 192.168.230.157`
![](file-20260902195421556.png)
目录发现：
```bash
ffuf -w /usr/share/wordlists/dirb/common.txt \
  -u http://192.168.230.157:80/FUZZ \
  -e .php,.txt,.bak,.zip \
  -recursion \
  -recursion-depth 2 \
  -c -ac -o output.txt -of csv
```
![](file-20260902195421559.png)

**综上**：
- 端口22，80，111
- CMS框架Drupal\[7.22,7.23,7.24,7.25,7.26\],
- 后端语言PHP\[5.4.45-0+deb7u14\],
- web服务器]\[Apache/2.2.22 (Debian)\]
## web漏洞利用
**搜索漏洞**
优先搜索CMS相关漏洞：`searchexploit Drupal` 尝试7.x相关
![](file-20260902195421563.png)
msf中有则直接使用，没有则取拉取网上的exp
![](file-20260902195421584.png)
**获取初步shell**
直接利用exploit/unix/webapp/drupal_drupalgeddon2获取反弹shell
查看flag.txt：提示我们看配置文件
![](file-20260902195421587.png)
查看flag1.txt
![](file-20260902195421589.png)
## 内部信息提取与数据库翻找
Drupal 7.x 的核心配置文件是 **`settings.php`** 
默认路径/var/www/html/sites/default/settings.php
![](file-20260902195421592.png)
获得flag2与数据库连接账号
**升级shell**
先反弹shell到kali终端，不要在msf中直接升级可能冲突
![](file-20260902195421594.png)
反弹shell成功
![](file-20260902195421596.png)
升级shell
![](file-20260902195421598.png)
利用mysql凭证登陆mysql
![](file-20260902195421600.png)
尝试修改登陆后台密码：drupaldb数据库后台名
![](file-20260902195421601.png)
查找admin类似账号
![](file-20260902195421603.png)
三条路，修改admin密码，破解密码（加盐hash就不要去爆破了），或者创造一个新的账号（但如果没有最高权限无法创建高权限账号作用不大）
重置密码，这个密码是加salt的需要知道hash算法和salt值，好在scripts中存在密码生成脚本
新密码生成成功
![](file-20260902195421604.png)
去替换
![](file-20260902195421606.png)
admin登陆成功
![](file-20260902195421607.png)
## 系统提权
获得flag3![](file-20260902195421609.png)
home下有一个flag4用户查看其中信息:告诉我们root下也有一个flag，但是我们没有权限
![](file-20260902195421610.png)
使用find发现SUID账户
![](file-20260902195421612.png)
使用find发现SGID账户
![](file-20260902195421614.png)
使用SUID的find命令进行提权。
![](file-20260902195421616.png)