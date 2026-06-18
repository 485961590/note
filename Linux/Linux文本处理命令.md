# Linux 文本处理命令

> 文本处理是 Linux 命令行的核心能力——搜索、过滤、切割、统计、变形，用管道串联成一条流水线。

---

## grep — 文本搜索

从文件或标准输入中匹配模式，输出匹配行。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-i` | 忽略大小写 |
| `-v` | 反向匹配（输出不匹配的行） |
| `-n` | 显示行号 |
| `-c` | 只输出匹配行数 |
| `-l` | 只列出包含匹配的文件名 |
| `-r` / `-R` | 递归搜索目录 |
| `-E` | 扩展正则（等同于 `egrep`） |
| `-P` | Perl 正则（更强大） |
| `-o` | 只输出匹配的部分（而非整行） |
| `-w` | 整词匹配 |
| `-A N` | 显示匹配行后 N 行 |
| `-B N` | 显示匹配行前 N 行 |
| `-C N` | 显示匹配行前后各 N 行 |
| `-H` | 始终显示文件名（多文件搜索时默认） |

### 基础示例

```bash
# 搜索单个关键词
grep "error" /var/log/syslog

# 忽略大小写 + 显示行号
grep -in "error" /var/log/syslog

# 递归搜索目录
grep -r "192.168.1" /etc/

# 反向匹配（排除注释行和空行）
grep -v "^#" /etc/ssh/sshd_config | grep -v "^$"

# 只输出文件名
grep -rl "TODO" ./src/

# 统计匹配次数
grep -c "ERROR" app.log

# 正则：匹配 IP 地址
grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' access.log

# 上下文：异常前后各 3 行
grep -C 3 "Exception" app.log
```

### 常见组合

```bash
# 查找进程中排除 grep 自身
ps aux | grep nginx | grep -v grep

# 统计每个 IP 的访问次数（Top 10）
grep -oE '^[0-9.]+' access.log | sort | uniq -c | sort -rn | head -10

# 搜索包含多个关键词的行（AND）
grep "error" app.log | grep "timeout"

# 搜索包含任一关键词的行（OR）
grep -E "error|fail|panic" app.log
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

### 基础示例

```bash
# 替换第一个匹配
sed 's/old/new/' file.txt

# 全局替换
sed 's/old/new/g' file.txt

# 替换第 3 次出现
sed 's/old/new/3' file.txt

# 直接修改文件（带备份）
sed -i.bak 's/old/new/g' file.txt

# 删除匹配行
sed '/pattern/d' file.txt

# 删除空行
sed '/^$/d' file.txt

# 删除第 5 到第 10 行
sed '5,10d' file.txt

# 只打印第 3 到第 7 行
sed -n '3,7p' file.txt

# 在匹配行后追加
sed '/pattern/a\新行内容' file.txt

# 在匹配行前插入
sed '/pattern/i\新行内容' file.txt

# 替换指定行
sed '3s/old/new/' file.txt

# 多个替换
sed -e 's/foo/bar/' -e 's/baz/qux/' file.txt
```

### 高级替换

```bash
# 分组引用：交换两列
echo "hello world" | sed 's/\(.*\) \(.*\)/\2 \1/'
# 输出：world hello

# 用 & 引用整个匹配
echo "abc123" | sed 's/[0-9]\+/(&)/'
# 输出：abc(123)

# 去掉行尾空格
sed 's/[[:space:]]*$//' file.txt

# HTML 标签去除
sed 's/<[^>]*>//g' file.html
```

### 常用组合

```bash
# 修改配置文件（安全做法：先不改原文件）
sed 's/^Port 22$/Port 2222/' /etc/ssh/sshd_config

# 提取日志中的时间范围
sed -n '/10:00/,/10:30/p' app.log

# 给每行加行号（比 cat -n 灵活）
sed = file.txt | sed 'N;s/\n/ /'
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

默认tab，空格等空白字符为分割变量例如 root  kali  user
	root为$1, kali为$2, user为$3

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

### 基础示例

```bash
# 打印第一列
awk '{print $1}' file.txt

# 打印第一列和第三列（制表符分隔输出）
awk '{print $1 "\t" $3}' file.txt

# 逗号分隔的文件
awk -F',' '{print $2}' data.csv

# 打印最后一列
awk '{print $NF}' file.txt

# 带行号输出
awk '{print NR ": " $0}' file.txt

# 条件过滤：第三列 > 100
awk '$3 > 100' file.txt

# 正则匹配
awk '/error/' app.log

# 字段匹配
awk '$2 == "ERROR"' app.log
```

### 计算与统计

```bash
# 求和
awk '{sum += $1} END {print sum}' numbers.txt

# 平均值
awk '{sum += $1; count++} END {print sum/count}' numbers.txt

# 最大值
awk 'max < $1 {max = $1} END {print max}' numbers.txt

# 按第二列分组求和
awk '{group[$2] += $3} END {for (g in group) print g, group[g]}' data.txt

# 统计行数、字数、字符数（相当于 wc）
awk '{lines++; words += NF; chars += length($0)}
     END {print lines, words, chars}' file.txt
```

### 格式化输出

```bash
# printf 格式化（类似 C 语言）
awk '{printf "%-20s %10d\n", $1, $2}' file.txt

# 修改输出分隔符
awk 'BEGIN {OFS=","} {print $1, $2, $3}' data.txt
```

### 常用组合

```bash
# 统计每个 IP 的请求数（等同于 grep+sort+uniq 但一步完成）
awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log | sort -rn

# 计算日志中所有响应时间的平均值
awk '{sum += $NF; n++} END {print sum/n " ms"}' response.log

# 提取特定列并格式化（top 10 内存进程）
ps aux | awk '{print $4 "\t" $11}' | sort -rn | head -10

# 合并多行（把每 3 行合并为一行，制表符分隔）
awk 'ORS=NR%3?"\t":"\n"' file.txt
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

### 基础示例

```bash
# 提取冒号分隔的第一列（/etc/passwd 用户名）
cut -d: -f1 /etc/passwd

# 提取第 1 和第 7 列（用户名 + shell）
cut -d: -f1,7 /etc/passwd

# 提取第 3 到最后一列
cut -d: -f3- /etc/passwd

# 按字符位置提取（每行第 1-10 个字符）
cut -c1-10 file.txt

# 提取 CSV 第二列（忽略无逗号行）
cut -d, -f2 -s data.csv
```

### 常用组合

```bash
# 列出所有用户及其 shell
cut -d: -f1,7 /etc/passwd | column -t -s:

# 统计每种 shell 使用人数
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn
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

### 基础示例

```bash
# 数值排序（默认按字符序会出现 1,10,2,...）
sort -n numbers.txt

# 按第二列数值逆序
sort -k2 -nr data.txt

# 按逗号分隔的第三列排序
sort -t, -k3 -n data.csv

# 去重
sort -u file.txt

# 按文件大小排序（人类可读）
du -sh * | sort -h

# 随机打乱
sort -R file.txt | head -5
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

### 基础示例

```bash
# 计数（经典用法）
sort file.txt | uniq -c | sort -rn

# 显示重复项
sort file.txt | uniq -d

# 显示唯一项
sort file.txt | uniq -u

# 不区分大小写计数
sort file.txt | uniq -ci
```

### 常用组合

```bash
# 日志中最频繁的 10 个 IP
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 统计单词频率
cat document.txt | tr ' ' '\n' | sort | uniq -c | sort -rn | head -20

# 找出只出现一次的行（异常检测）
sort data.txt | uniq -u
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

### 基础示例

```bash
# 统计文件行数
wc -l file.txt

# 统计多个文件
wc -l *.log

# 统计目录下所有 .py 文件的总行数
find . -name "*.py" | xargs wc -l
```

### 常用组合

```bash
# 统计当前目录文件数
ls | wc -l

# 统计进程数
ps aux | wc -l

# 统计代码行数（排除空行和注释）
grep -v "^$\|^#" nginx.conf | wc -l
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

### 基础示例

```bash
# 大小写转换
echo "Hello World" | tr 'a-z' 'A-Z'     # HELLO WORLD
echo "HELLO" | tr 'A-Z' 'a-z'            # hello

# 删除字符
echo "abc123" | tr -d '0-9'              # abc
echo "a  b   c" | tr -s ' '              # a b c（压缩空格）

# 替换字符
echo "hello world" | tr ' ' '_'          # hello_world

# 取反删除（只保留数字）
echo "abc123def456" | tr -cd '0-9'       # 123456

# 把换行符替换为空格（多行合并为一行）
cat file.txt | tr '\n' ' '
```

### 常用组合

```bash
# DOS/Windows 换行符转 Unix（删除 \r）
tr -d '\r' < dosfile.txt > unixfile.txt

# 生成随机密码
tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 16

# URL 编码中 % 替换（简单版）
echo "hello world" | tr ' ' '%'
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

### 基础示例

```bash
# 删除查找到的文件
find . -name "*.tmp" | xargs rm

# 安全的做法（处理含空格的文件名）
find . -name "*.tmp" -print0 | xargs -0 rm

# 每次处理 3 个文件
echo {1..10} | xargs -n3
# 输出：1 2 3
#       4 5 6
#       7 8 9
#       10

# 占位符模式（每行执行一次）
cat urls.txt | xargs -I {} curl -O {}

# 执行前确认
find . -name "*.log" | xargs -p rm
```

### 常用组合

```bash
# 批量重命名（加 .bak 后缀）
ls *.txt | xargs -I {} mv {} {}.bak

# 并行下载
cat urls.txt | xargs -P 4 -I {} wget {}

# 统计所有 .c 文件行数总和
find . -name "*.c" -print0 | xargs -0 wc -l | tail -1
```

---

## tee — 分流输出

把输出同时送到文件和标准输出（像水管的三通接头）。

### 常用选项

| 选项 | 说明 |
|------|------|
| `-a` | 追加到文件（默认覆盖） |
| `-i` | 忽略中断信号 |

### 基础示例

```bash
# 输出到屏幕同时保存到文件
./script.sh | tee output.log

# 追加到文件
echo "new line" | tee -a log.txt

# 多路输出
cat data.txt | tee file1.txt file2.txt

# 中间结果保存（不打断管道）
grep "ERROR" app.log | tee errors.txt | wc -l
```

### 常用组合

```bash
# 调试管道：保存中间结果
cat access.log \
  | grep "2024-01" | tee step1.log \
  | awk '{print $1}' | tee step2.log \
  | sort | uniq -c | sort -rn | tee final.log

# sudo 写文件（绕过重定向权限限制）
echo "new config" | sudo tee /etc/config.conf > /dev/null
```

---

## 常见组合套路

### 日志分析一条龙

```bash
# Top 10 IP 访问量
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 统计 HTTP 状态码分布
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# 响应时间超过 1 秒的请求
awk '$NF > 1' response.log | wc -l
```

### 配置文件处理

```bash
# 列出所有非注释、非空行的配置
grep -v "^#" nginx.conf | grep -v "^$"

# 查找所有 listen 端口
grep -oP 'listen\s+\K\d+' nginx.conf | sort -u
```

### 系统巡检

```bash
# 磁盘使用 Top 5 目录
du -sh /* 2>/dev/null | sort -h | tail -5

# 内存 Top 10 进程
ps aux | awk '{print $4, $11}' | sort -rn | head -10

# 最近登录的 5 个 IP
last | awk '{print $3}' | grep -oE '[0-9.]+' | sort | uniq -c | sort -rn | head -5
```

### 批量操作

```bash
# 查找并压缩 30 天前的日志
find /var/log -name "*.log" -mtime +30 -print0 | xargs -0 gzip

# 替换目录下所有文件中的字符串
grep -rl "old_domain" ./ | xargs sed -i 's/old_domain/new_domain/g'

# 统计项目代码行数（排除 node_modules）
find . -name "*.js" -not -path "*/node_modules/*" | xargs wc -l | tail -1
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
