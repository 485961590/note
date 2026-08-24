## 信息收集
主机发现
	![](file-20260815095849837.png)
fscan梭哈
	![](file-20260815095849842.png)
正儿八经端口扫描
	![](file-20260815095849844.png)
对扫描到的端口进行综合探测
	![](file-20260815095849845.png)
访问81端口
	![](file-20260815095849846.png)
访问80端口
	![](file-20260815095849848.png)
进行指纹探测
	![](file-20260815095849850.png)
进行目录扫描
	![](file-20260815095849851.png)
gobuster再扫描一遍尽可能多的收集信息
	![](file-20260815095849852.png)
访问扫到的文件瞅瞅都是扫描
	![](file-20260815095849853.png)
	![](file-20260815095849855.png)
## 漏洞利用
发现graffti.php很奇怪包含了txt文件的内容，这里可能存在文件包含，直接抓包分析然后发现了文件包含漏洞，使用伪协议读取graffiti.php的内容下来进行审计：
	![](file-20260815095849856.png)
## 代码审计
```php
<h1>
<center>
Nebuchadnezzar Graffiti Wall

</center>
</h1>
<p>
<?php

$file="graffiti.txt";
if($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['file'])) {
       $file=$_POST['file'];
    }
    if (isset($_POST['message'])) {
        $handle = fopen($file, 'a+') or die('Cannot open file: ' . $file);
        fwrite($handle, $_POST['message']);
	fwrite($handle, "\n");
        fclose($file); 
    }
}

// Display file
$handle = fopen($file,"r");
while (!feof($handle)) {
  echo fgets($handle);
  echo "<br>\n";
}
fclose($handle);
?>
<p>
Enter message: 
<p>
<form method="post">
<label>Message</label><div><input type="text" name="message"></div>
<input type="hidden" name="file" value="graffiti.txt">
<div><button type="submit">Post</button></div>
</form>
MTExCg==
```
功能是在指定文件夹中**追加内容然后展示**，如果没有指定文件就是默认的graffiti.txt，**但这里没有对file参数做任何处理就如之前我们指定文件一样**。
## 漏洞利用
尝试再文件夹中写入一句话木马。
	![](file-20260815095849859.png)
写入phpinfo成功解析：
	![](file-20260815095849861.png)
插入
	![](file-20260815095849864.png)
蚁剑连接：
	![](file-20260815095849867.png)
根据echo $0判断终端类型然后编写合适的反弹shell ：
	![](file-20260815095849870.png)
编写反弹shell并在本地开启http服务：
	![](file-20260815095849874.png)
将会话从蚁剑中派生到终端中使操作更灵活：
	![](file-20260815095849877.png)
访问shell.php反弹会话到kali
	![](file-20260815095849880.png)
获取反弹shell成功
	![](file-20260815095849884.png)
升级shell，使其具备命令补全等更全面的终端能力
	![](file-20260815095849887.png)
	既然有python环境那就先升级一下shell，让其功能更全面可以补全可以
	![](file-20260815095849891.png)
	![](file-20260815095849896.png)
查看当前用户拥有什么权限：
	![](file-20260815095849899.png)
查看SUID权限文件
	![](file-20260815095849902.png)
上传linpeas.sh进行全面扫描
	![](file-20260815095849905.png)
查看当前系统的内核相关信息
	![](file-20260815095849909.png)
使用linpeas.sh扫除的CVE漏洞进行攻击
![](file-20260815095849912.png)
## 提权
搜索公开漏洞库
	![](file-20260815095849915.png)
静态编译防止目标缺少依赖库
	![](file-20260815095849918.png)
wget下载到目标服务器中
	![](file-20260815095849921.png)
漏洞提权成功！！！
	![](file-20260815095849924.png)

# 攻击原理：

**任意文件写入 -> 写入 PHP Web Shell -> 利用 Dirty Pipe 内核漏洞提权。**
- `graffiti.php` 直接使用用户提交的 `file` 参数，没有限制路径。严格来说，这里的关键不是传统文件包含，而是攻击者可以指定任意文件并写入内容。
- 攻击者把 PHP 代码写入网站目录中的 `.php` 文件，访问后即可执行任意系统命令，获得 `www-data` 权限。
- 系统内核版本过旧，存在 `Dirty Pipe` 漏洞（CVE-2022-0847）。该漏洞允许普通用户篡改原本只读的系统文件，攻击者借此修改 SUID 程序，最终获得 root。

**影响是：** 攻击者从网站权限提升到整台服务器 root，可以读取、修改或删除系统文件、网站数据和凭据，并能植入后门。

**修复重点：**
- 不要让用户直接指定文件路径；使用固定文件或严格白名单，并限制文件只能写入专用数据目录。
- 上传目录和数据目录禁止解析 PHP，修复路径穿越和任意文件写入问题。
- 升级 Linux 内核到修复 Dirty Pipe 的版本，并重启生效；同时检查系统文件是否被修改。
- 因为已经获得 root，应隔离并重建主机，轮换所有系统和应用凭据。