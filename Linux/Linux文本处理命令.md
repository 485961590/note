# Linux 文本处理命令

> 文本处理是 Linux 命令行的核心能力——搜索、过滤、切割、统计、变形，用管道串联成一条流水线。

---

## 本文使用的示例文件

后面所有例子都基于这两个文件，先看一下它们的内容：

**app.log** — 应用程序日志：

```
2024-01-15 10:23:45 INFO  Server started on port 8080
2024-01-15 10:23:46 DEBUG Loading configuration from /etc/app.conf
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:02 WARN  Retrying connection (attempt 1/3)
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306
2024-01-15 10:25:00 FATAL Unable to start application
2024-01-15 10:30:00 INFO  Server shutdown complete
```

**access.log** — Web 服务器访问日志：

```
192.168.1.10 - - [15/Jan/2024:10:23:45 +0800] "GET /index.html HTTP/1.1" 200 1234
192.168.1.10 - - [15/Jan/2024:10:23:46 +0800] "GET /style.css HTTP/1.1" 304 0
10.0.0.5 - - [15/Jan/2024:10:23:47 +0800] "POST /api/login HTTP/1.1" 200 256
192.168.1.10 - - [15/Jan/2024:10:24:01 +0800] "GET /api/data HTTP/1.1" 500 89
10.0.0.5 - - [15/Jan/2024:10:24:02 +0800] "GET /about.html HTTP/1.1" 200 2048
172.16.0.1 - - [15/Jan/2024:10:24:05 +0800] "POST /api/login HTTP/1.1" 401 45
192.168.1.10 - - [15/Jan/2024:10:24:06 +0800] "GET /index.html HTTP/1.1" 200 1234
```

---

## grep — 文本搜索

从文件或标准输入中匹配模式，输出匹配行。

### 常用选项

| 选项          | 说明                |
| ----------- | ----------------- |
| `-i`        | 忽略大小写             |
| `-v`        | 反向匹配（输出不匹配的行）     |
| `-n`        | 显示行号              |
| `-c`        | 只输出匹配行数           |
| `-l`        | 只列出包含匹配的文件名       |
| `-r` / `-R` | 递归搜索目录            |
| `-E`        | 扩展正则（等同于 `egrep`） |
| `-P`        | Perl 正则（更强大）      |
| `-o`        | 只输出匹配的部分（而非整行）    |
| `-w`        | 整词匹配              |
| `-A N`      | 显示匹配行后 N 行        |
| `-B N`      | 显示匹配行前 N 行        |
| `-C N`      | 显示匹配行前后各 N 行      |

### 示例

以下示例都基于 `app.log`（内容见上文）：

```bash
# === 基础搜索：查找包含 "ERROR" 的行 ===
$ grep "ERROR" app.log
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306

# === 忽略大小写：大小写不敏感的搜索 ===
$ grep -i "error" app.log
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306

# === 显示行号：知道匹配内容在第几行 ===
$ grep -n "ERROR" app.log
3:2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
5:2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306

# === 反向匹配：排除 INFO 行，只看有问题和值得注意的日志（WARN也算） ===
$ grep -v "INFO" app.log
2024-01-15 10:23:46 DEBUG Loading configuration from /etc/app.conf
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:02 WARN  Retrying connection (attempt 1/3)
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306
2024-01-15 10:25:00 FATAL Unable to start application

# === 统计匹配次数：只看数量，不看具体内容 ===
$ grep -c "ERROR" app.log
2

# === 只输出匹配的部分（-o 提取）：从日志中提取所有 IP 地址 ===
$ grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' app.log
192.168.1.100
192.168.1.100

# === 整词匹配（-w）：搜索 "INFO" 整词，不会匹配到 "INFO" 以外的内容 ===
$ grep -w "INFO" app.log
2024-01-15 10:23:45 INFO  Server started on port 8080
2024-01-15 10:30:00 INFO  Server shutdown complete

# === 上下文（-C）：显示匹配行及其前后各 1 行，方便看错误发生的前后文 ===
$ grep -C 1 "ERROR" app.log
2024-01-15 10:23:46 DEBUG Loading configuration from /etc/app.conf
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:02 WARN  Retrying connection (attempt 1/3)
--
2024-01-15 10:24:02 WARN  Retrying connection (attempt 1/3)
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306
2024-01-15 10:25:00 FATAL Unable to start application
```

### 常见组合

```bash
# === 查找进程并排除 grep 自身 ===
$ ps aux | grep nginx | grep -v grep
root      1234  0.0  0.1  45678  1234 ?  Ss   Jan15  0:00 nginx: master
www-data  1235  0.0  0.2  45678  2345 ?  S    Jan15  0:01 nginx: worker

# === 从 access.log 统计每个 IP 访问次数（Top 3） ===
$ grep -oE '^[0-9.]+' access.log | sort | uniq -c | sort -rn | head -3
      4 192.168.1.10
      2 10.0.0.5
      1 172.16.0.1

# === AND 逻辑：同时包含 "ERROR" 和 "timeout" 的行 ===
$ grep "ERROR" app.log | grep "timeout"
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306

# === OR 逻辑：包含 "ERROR" 或 "FATAL" 的行 ===
$ grep -E "ERROR|FATAL" app.log
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306
2024-01-15 10:25:00 FATAL Unable to start application

# === 排除注释行和空行：查看有效配置 ===
$ grep -v "^#" /etc/ssh/sshd_config | grep -v "^$"
Port 22
PermitRootLogin yes
PasswordAuthentication yes
...
```

---

## sed — 流编辑器

逐行处理文本，不改原文件（加 `-i` 才写入）。核心是 `s/旧/新/` 替换语法。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-i` | 直接修改文件（**危险**，建议先不加 `-i` 测试） |
| `-i.bak` | 修改前创建备份（如 `-i.bak` 生成 `file.bak`） |
| `-n` | 静默模式，不自动打印（配合 `p` 使用） |
| `-e` | 多个编辑命令 |
| `-E` / `-r` | 扩展正则 |

**要替换内容必须遵循 `s/旧/新/`，没有 s 则语法错误。**

**要删除内容则无需 s，只需匹配内容然后使用 d，例如：`/^$/d` 匹配空行然后删除。**

### 示例：替换

以下示例使用一个简单文件 `greeting.txt`，内容为：

```
hello world
hello world
hello world
```

```bash
# === 替换每行第一个匹配 ===
$ sed 's/hello/hi/' greeting.txt
hi world
hi world
hi world

# === 全局替换（g 标志）：替换每行所有匹配 ===
$ sed 's/hello/hi/g' greeting.txt
hi world
hi world
hi world

# === 替换指定行：只替换第 2 行 ===
$ sed '2s/hello/hi/' greeting.txt
hello world
hi world
hello world

# === 多个替换：同时替换 hello 和 world ===
$ sed -e 's/hello/hi/' -e 's/world/earth/' greeting.txt
hi earth
hi earth
hi earth
```

### 示例：删除

```bash
# === 准备一个有空白行的文件 ===
$ cat config.txt
# 这是注释
port=8080

host=localhost

# 另一条注释
debug=true

# === 删除空行 ===
$ sed '/^$/d' config.txt
# 这是注释
port=8080
host=localhost
# 另一条注释
debug=true

# === 删除注释行 ===
$ sed '/^#/d' config.txt
port=8080

host=localhost

debug=true

# === 同时删除注释行和空行（管道串联） ===
$ sed '/^#/d' config.txt | sed '/^$/d'
port=8080
host=localhost
debug=true
```

### 示例：高级替换

```bash
# === 分组引用：交换两列位置 ===
$ echo "hello world" | sed 's/\(.*\) \(.*\)/\2 \1/'
world hello

# === & 引用整个匹配：给数字加括号 ===
$ echo "abc123" | sed 's/[0-9]\+/(&)/'
abc(123)

# === 去掉行尾空格 ===
$ echo "hello   " | sed 's/[[:space:]]*$//'
hello

# === 去除 HTML 标签 ===
$ echo "<p>Hello <b>World</b></p>" | sed 's/<[^>]*>//g'
Hello World
```

### 常用组合

```bash
# === 提取日志时间范围：10:24:00 到 10:25:00 之间的日志 ===
$ sed -n '/10:24/,/10:25/p' app.log
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:02 WARN  Retrying connection (attempt 1/3)
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306
2024-01-15 10:25:00 FATAL Unable to start application

# === 修改配置文件（先预览，确认无误再加 -i） ===
$ sed 's/^Port 22$/Port 2222/' /etc/ssh/sshd_config
Port 2222
...
```

---

## awk — 文本分析语言

按字段（列）处理文本，能做计算、过滤、格式化输出。默认以空白字符分隔字段，`$1` 第一列、`$0` 整行。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-F` | 指定字段分隔符 |
| `-v` | 定义变量 |
| `-f` | 从文件读取 awk 脚本 |

### 内置变量

默认 tab、空格等空白字符为分隔符。例如 `root  kali  user` 这一行中：root 为 $1, kali 为 $2, user 为 $3。

| 变量 | 说明 |
|------|------|
| `$0` | 整行 |
| `$1, $2, ...` | 第 N 个字段 |
| `NF` | 当前行的字段数 |
| `$NF` | 最后一个字段 |
| `NR` | 当前行号（累计） |
| `FNR` | 当前文件内的行号 |
| `FS` | 输入字段分隔符（默认空白） |
| `OFS` | 输出字段分隔符（默认空格） |
| `RS` | 输入记录分隔符（默认换行） |
| `ORS` | 输出记录分隔符（默认换行） |

### 示例：列操作

以下示例基于 `access.log`（内容见本文开头）：

```bash
# === 打印第一列（客户端 IP） ===
$ awk '{print $1}' access.log
192.168.1.10
192.168.1.10
10.0.0.5
192.168.1.10
10.0.0.5
172.16.0.1
192.168.1.10

# === 打印第一列和第九列（IP + HTTP 状态码），制表符分隔 ===
$ awk '{print $1 "\t" $9}' access.log
192.168.1.10    200
192.168.1.10    304
10.0.0.5        200
192.168.1.10    500
10.0.0.5        200
172.16.0.1      401
192.168.1.10    200

# === 打印最后一列（$NF = 最后一个字段，即响应字节数） ===
$ awk '{print $NF}' access.log
1234
0
256
89
2048
45
1234

# === 带行号输出 ===
$ awk '{print NR ": " $0}' access.log
1: 192.168.1.10 - - [15/Jan/2024:10:23:45 +0800] "GET /index.html HTTP/1.1" 200 1234
2: 192.168.1.10 - - [15/Jan/2024:10:23:46 +0800] "GET /style.css HTTP/1.1" 304 0
3: 10.0.0.5 - - [15/Jan/2024:10:23:47 +0800] "POST /api/login HTTP/1.1" 200 256
...
```

### 示例：条件过滤

```bash
# === 按数值过滤：状态码 >= 400（只看错误请求） ===
$ awk '$9 >= 400' access.log
192.168.1.10 - - [15/Jan/2024:10:24:01 +0800] "GET /api/data HTTP/1.1" 500 89
172.16.0.1 - - [15/Jan/2024:10:24:05 +0800] "POST /api/login HTTP/1.1" 401 45

# === 正则匹配：包含 "ERROR" 的行 ===
$ awk '/ERROR/' app.log
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306

# === 字段精确匹配：第三列等于 "ERROR" ===
$ awk '$3 == "ERROR"' app.log
2024-01-15 10:24:01 ERROR Connection timeout to 192.168.1.100:3306
2024-01-15 10:24:05 ERROR Connection refused by 192.168.1.100:3306
```

### 示例：逗号分隔文件（CSV）

假设 `data.csv` 内容为：

```
name,age,city,score
Zhang,21,Beijing,85
Li,22,Shanghai,90
Wang,20,Guangzhou,72
Zhao,23,Shenzhen,95
```

```bash
# === 指定逗号为分隔符，提取第二列（年龄） ===
$ awk -F',' '{print $2}' data.csv
age
21
22
20
23

# === 条件过滤：分数大于 80 的行 ===
$ awk -F',' '$4 > 80' data.csv
name,age,city,score
Zhang,21,Beijing,85
Li,22,Shanghai,90
Zhao,23,Shenzhen,95
```

### 示例：计算与统计

假设 `numbers.txt` 内容为：

```
10
25
8
42
15
```

```bash
# === 求和 ===
$ awk '{sum += $1} END {print sum}' numbers.txt
100

# === 平均值 ===
$ awk '{sum += $1; count++} END {print sum/count}' numbers.txt
20

# === 最大值 ===
$ awk 'max < $1 {max = $1} END {print max}' numbers.txt
42

# === 统计行数、单词数、字符数（相当于 wc） ===
$ awk '{lines++; words += NF; chars += length($0)} END {print lines, words, chars}' app.log
7 63 475
```

### 示例：格式化输出

```bash
# === printf 格式化：左对齐 20 字符宽度输出第一列，右对齐 10 字符宽度输出最后一列 ===
$ awk '{printf "%-20s %10d\n", $1, $NF}' access.log
192.168.1.10              1234
192.168.1.10                 0
10.0.0.5                   256
192.168.1.10                89
10.0.0.5                  2048
172.16.0.1                  45
192.168.1.10              1234
```

### 常用组合

```bash
# === 统计每个 IP 的请求数（一步完成，不需要 grep+sort+uniq） ===
$ awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log | sort -rn
4 192.168.1.10
2 10.0.0.5
1 172.16.0.1

# === 提取特定列并格式化：ps 内存 Top 3 ===
$ ps aux | awk '{print $4 "\t" $11}' | sort -rn | head -3
12.5    /usr/bin/java
8.2     /usr/bin/python3
3.1     /usr/sbin/mysqld
```

---

## cut — 列提取

按分隔符或字符位置切分每一行。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-d` | 指定分隔符（默认 Tab） |
| `-f` | 提取第 N 个字段（可逗号分隔多个，`-f1,3`；可用范围 `-f1-5`） |
| `-c` | 按字符位置提取 |
| `-s` | 不输出不含分隔符的行 |
| `--complement` | 提取**不**在 `-f` 范围内的字段 |

### 示例

以下示例基于 `access.log` 和 `/etc/passwd`：

```bash
# === 按分隔符提取：/etc/passwd 第一列（用户名），分隔符为冒号 ===
$ head -3 /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin

$ cut -d: -f1 /etc/passwd | head -3
root
daemon
bin

# === 提取第 1 列和第 7 列（用户名 + 默认 shell） ===
$ cut -d: -f1,7 /etc/passwd | head -3
root:/bin/bash
daemon:/usr/sbin/nologin
bin:/usr/sbin/nologin

# === 按字符位置提取：每行第 1 到 15 个字符 ===
$ cut -c1-15 access.log
192.168.1.10 -
192.168.1.10 -
10.0.0.5 - - [
192.168.1.10 -
10.0.0.5 - - [
172.16.0.1 - -
192.168.1.10 -

# === CSV 第二列：忽略不含逗号的行（-s） ===
$ cat data.csv
name,age,city,score
Zhang,21,Beijing,85

$ cut -d, -f2 -s data.csv
age
21
```

### 常用组合

```bash
# === 统计每种 shell 的使用人数 ===
$ cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn | head -3
     25 /usr/sbin/nologin
     10 /bin/bash
      5 /bin/false
```

---

## sort — 排序

### 常用选项

| 选项 | 说明 |
|------|------|
| `-n` | 数值排序（否则按字符序，"10" < "2"） |
| `-r` | 逆序 |
| `-h` | 人类可读的数值排序（1K, 2M, 1G） |
| `-k` | 按第 N 列排序（`-k2` 第二列，`-k2,2n` 第二列数值） |
| `-t` | 指定分隔符 |
| `-u` | 去重（排序后去除重复行） |
| `-o` | 输出到文件（可覆盖原文件） |
| `-R` | 随机排序 |

### 示例

```bash
# === 字符序 vs 数值序的区别 ===
$ cat nums.txt
2
10
1
100

$ sort nums.txt           # 字符序：逐字符比较，"1" < "2"
1
10
100
2

$ sort -n nums.txt         # 数值序：按数值大小
1
2
10
100

# === 按指定列排序：access.log 按第 9 列（状态码）数值逆序排列 ===
$ awk '{print $1, $9}' access.log | sort -k2 -nr
192.168.1.10 500
10.0.0.5 401
192.168.1.10 304
192.168.1.10 200
192.168.1.10 200
10.0.0.5 200
10.0.0.5 200

# === 按逗号分隔的指定列排序 ===
$ sort -t, -k4 -nr data.csv
name,age,city,score
Zhao,23,Shenzhen,95
Li,22,Shanghai,90
Zhang,21,Beijing,85
Wang,20,Guangzhou,72

# === 去重：重复行只保留一份 ===
$ echo -e "apple\nbanana\napple\ncherry" | sort -u
apple
banana
cherry
```

---

## uniq — 去重与计数

**注意：** `uniq` 只合并**相邻**的重复行，通常需要先 `sort`。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-c` | 计数（前缀显示出现次数） |
| `-d` | 只显示重复的行 |
| `-u` | 只显示唯一的行（不重复的） |
| `-i` | 忽略大小写 |
| `-w N` | 只比较前 N 个字符 |

### 示例

```bash
# === 先 sort 再 uniq -c：统计每个 IP 出现次数 ===
$ awk '{print $1}' access.log | sort | uniq -c | sort -rn
      4 192.168.1.10
      2 10.0.0.5
      1 172.16.0.1

# === 只显示重复项 ===
$ echo -e "apple\nbanana\napple\ncherry\nbanana" | sort | uniq -d
apple
banana

# === 只显示唯一项（只出现过一次的行）===
$ echo -e "apple\nbanana\napple\ncherry\nbanana" | sort | uniq -u
cherry

# === 忽略大小写去重 ===
$ echo -e "Apple\napple\nBanana" | sort | uniq -ci
      2 Apple
      1 Banana
```

---

## wc — 统计

### 常用选项

| 选项 | 说明 |
|------|------|
| `-l` | 行数 |
| `-w` | 单词数 |
| `-c` | 字节数 |
| `-m` | 字符数（多字节字符用这个） |
| `-L` | 最长行的长度 |

### 示例

```bash
# === 统计文件行数 ===
$ wc -l app.log
7 app.log

# === 同时显示行数、单词数、字节数 ===
$ wc app.log
  7  63 475 app.log
#  行数  单词数  字节数

# === 统计多个文件 ===
$ wc -l app.log access.log
  7 app.log
  7 access.log
 14 total

# === 统计当前目录下文件数量 ===
$ ls | wc -l
12

# === 统计代码有效行数（排除空行和注释） ===
$ grep -v "^$\|^#" nginx.conf | wc -l
45
```

---

## tr — 字符转换

从标准输入读取，不支持直接读文件（需管道或 `<`）。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-d` | 删除指定字符 |
| `-s` | 压缩连续重复字符为一个 |
| `-c` | 取反（操作不在集合中的字符） |
| `-t` | 截断 SET1 到 SET2 长度 |

### 示例

```bash
# === 大小写转换 ===
$ echo "Hello World" | tr 'a-z' 'A-Z'
HELLO WORLD

$ echo "HELLO" | tr 'A-Z' 'a-z'
hello

# === 删除指定字符：去掉所有数字 ===
$ echo "abc123def456" | tr -d '0-9'
abcdef

# === 只保留数字（-c 取反 + -d 删除） ===
$ echo "abc123def456" | tr -cd '0-9'
123456

# === 压缩连续重复字符：多个空格变成一个 ===
$ echo "a   b    c" | tr -s ' '
a b c

# === 字符替换：空格换成下划线 ===
$ echo "hello world" | tr ' ' '_'
hello_world

# === 多行合并为一行：换行符换成空格 ===
$ cat app.log | tr '\n' ' '
2024-01-15 10:23:45 INFO  Server started on port 8080 2024-01-15 10:23:46 DEBUG ...
```

---

## xargs — 参数中转

把标准输入转为命令参数，解决"参数列表过长"和"管道无法传参"的问题。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-n N` | 每次传递 N 个参数给命令 |
| `-I {}` | 用 `{}` 占位替换（每个参数执行一次） |
| `-0` | 以 null 字符分隔（配合 `find -print0`） |
| `-p` | 执行前询问确认 |
| `-t` | 打印执行的命令 |
| `-P N` | 并行执行 N 个进程 |

### 示例

```bash
# === -n：指定每次传几个参数 ===
$ echo {1..10} | xargs -n3
1 2 3
4 5 6
7 8 9
10

# === -I {}：占位符模式，每个参数执行一次命令 ===
$ echo "file1.txt\nfile2.txt" | xargs -I {} cp {} {}.bak
# 等效于依次执行：
# cp file1.txt file1.txt.bak
# cp file2.txt file2.txt.bak

# === -0：处理含空格的文件名（配合 find -print0） ===
$ find . -name "*.log" -print0 | xargs -0 rm
# -print0 用 null 字符分隔文件名，-0 按 null 字符读取
# 这样即使文件名里有空格也不会被错误拆分

# === 安全删除：执行前确认（-p） ===
$ find . -name "*.tmp" | xargs -p rm
rm ./a.tmp ./b.tmp?...y   # 输入 y 确认后才执行
```

---

## tee — 分流输出

把输出同时送到文件和标准输出（像水管的三通接头）。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-a` | 追加到文件（默认覆盖） |
| `-i` | 忽略中断信号 |

### 示例

```bash
# === 输出到屏幕同时保存到文件 ===
$ ./script.sh | tee output.log
# 屏幕上正常看到输出，同时 output.log 里也存了一份

# === 追加模式：不覆盖已有内容 ===
$ echo "new log entry" | tee -a app.log
new log entry
# app.log 末尾追加了这行，原有内容不变

# === 管道调试：保存中间结果但不打断数据流 ===
$ grep "ERROR" app.log | tee errors.txt | wc -l
2
# 屏幕输出：2
# errors.txt 里保存了匹配到的完整行
```

---

## 常见组合套路

### 日志分析一条龙

```bash
# === Top IP 访问量 ===
$ awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -3
      4 192.168.1.10
      2 10.0.0.5
      1 172.16.0.1

# === HTTP 状态码分布 ===
$ awk '{print $9}' access.log | sort | uniq -c | sort -rn
      3 200
      1 500
      1 401
      1 304

# === 响应超过 1KB 的请求 ===
$ awk '$NF > 1024' access.log
192.168.1.10 - - [15/Jan/2024:10:23:45 +0800] "GET /index.html HTTP/1.1" 200 1234
10.0.0.5 - - [15/Jan/2024:10:24:02 +0800] "GET /about.html HTTP/1.1" 200 2048
192.168.1.10 - - [15/Jan/2024:10:24:06 +0800] "GET /index.html HTTP/1.1" 200 1234
```

### 配置文件处理

```bash
# === 列出所有非注释、非空行的配置 ===
$ grep -v "^#" /etc/ssh/sshd_config | grep -v "^$"
Port 22
PermitRootLogin yes
PasswordAuthentication yes
...

# === 查找所有 listen 端口 ===
$ grep -oP 'listen\s+\K\d+' /etc/nginx/nginx.conf | sort -u
80
443
```

### 系统巡检

```bash
# === 磁盘使用 Top 3 目录 ===
$ du -sh /* 2>/dev/null | sort -h | tail -3
2.3G    /usr
4.5G    /var
12G     /home

# === 内存 Top 3 进程 ===
$ ps aux | awk '{print $4 "\t" $11}' | sort -rn | head -3
12.5    /usr/bin/java
8.2     /usr/bin/python3
3.1     /usr/sbin/mysqld
```

---

## 速查决策

| 需求 | 命令 |
|------|------|
| 搜文本 | `grep` |
| 替换文本 | `sed` |
| 按列处理 / 计算 | `awk` |
| 切列 | `cut` |
| 排序 | `sort` |
| 去重计数 | `sort \| uniq -c` |
| 统计行数 | `wc -l` |
| 字符转换 | `tr` |
| stdin 转参数 | `xargs` |
| 输出分流 | `tee` |

---

## 参考

- [Bash Shell.md](Bash%20Shell.md) — Shell 编程参考（变量、流程控制、I/O 重定向）
- [GNU Coreutils Manual](https://www.gnu.org/software/coreutils/manual/)
- [GNU Grep Manual](https://www.gnu.org/software/grep/manual/)
- [GNU Sed Manual](https://www.gnu.org/software/sed/manual/)
- [GNU Awk Manual](https://www.gnu.org/software/gawk/manual/)
