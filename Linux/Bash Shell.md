# Bash Shell 编程知识指南

> 一份系统化的 Bash Shell 编程参考，涵盖基础到进阶。

---

## 目录

1. [基础概念](Bash%20Shell.md#1-基础概念)
2. [变量与参数](Bash%20Shell.md#2-变量与参数)
3. [字符串操作](Bash%20Shell.md#3-字符串操作)
4. [数组](Bash%20Shell.md#4-数组)
5. [条件判断](Bash%20Shell.md#5-条件判断)
6. [循环与迭代](Bash%20Shell.md#6-循环与迭代)
7. [函数](Bash%20Shell.md#7-函数)
8. [I/O 与重定向](Bash%20Shell.md#8-io-与重定向)
9. [进程与作业控制](Bash%20Shell.md#9-进程与作业控制)
10. [错误处理与调试](Bash%20Shell.md#10-错误处理与调试)
11. [常用命令速查](Bash%20Shell.md#11-常用命令速查)
12. [脚本模板与最佳实践](Bash%20Shell.md#12-脚本模板与最佳实践)
13. [进阶技巧](Bash%20Shell.md#13-进阶技巧)

---

## 1. 基础概念

### 1.1 Shebang

```bash
#!/bin/bash           # 最常用，可移植
#!/usr/bin/env bash   # 通过 PATH 查找，更灵活
#!/bin/bash -e        # 任何命令失败立即退出
#!/bin/bash -eu       # -e: 遇错退出, -u: 未定义变量报错
#!/bin/bash -euxo pipefail  # 严格模式（推荐用于调试）
```

**推荐的脚本开头：**

```bash
#!/usr/bin/env bash
set -euo pipefail
```

| 选项            | 含义                 |
| ------------- | ------------------ |
| `-e`          | 任何命令返回非零状态时立即退出    |
| `-u`          | 使用未定义变量时报错退出       |
| `-o pipefail` | 管道中任意命令失败，整个管道返回失败 |
| `-x`          | 执行前打印每条命令（调试用）     |

### 1.2 执行方式

```bash
bash script.sh        # 子 shell 中执行
./script.sh           # 需要执行权限 chmod +x
source script.sh      # 当前 shell 中执行（环境变量生效）
. script.sh           # 同上，POSIX 写法
```

### 1.3 注释

```bash
# 单行注释

: '
多行注释
方式一：使用冒号和引号
'

<<'COMMENT'
多行注释
方式二：使用 Here Document
COMMENT
```

### 1.4 退出码

- `0`：成功
- `1-255`：失败
- `$?`：上一条命令的退出码
- 脚本退出码由最后一条命令或 `exit N` 决定

---

## 2. 变量与参数

### 2.1 变量定义与引用

```bash
# 定义（等号两边不能有空格）
name="Alice"
age=25

# 引用（用双引号防止分词和通配符展开）
echo "$name"
echo "${name}"        # 花括号明确变量边界，推荐

# 只读变量
readonly PI=3.14
declare -r PI=3.14

# 删除变量
unset name
```

### 2.2 变量作用域

```bash
# 默认：全局
foo="global"

# 局部（函数内）
my_func() {
    local bar="i am local"
    echo "$bar"
}

# 环境变量（子进程可见）
export PATH="/usr/local/bin:$PATH"
```

### 2.3 特殊变量

| 变量          | 含义                     |
| ----------- | ---------------------- |
| `$0`        | 脚本名称                   |
| `$1` ~ `$9` | 位置参数 1-9               |
| `${10}`     | 第 10 个参数（必须用花括号）       |
| `$#`        | 参数个数                   |
| `$@`        | 所有参数，每个独立（`"$@"` 保留空格） |
| `$*`        | 所有参数，合为一个字符串           |
| `$?`        | 上一条命令退出码               |
| `$$`        | 当前 shell PID           |
| `$!`        | 最后一个后台进程 PID           |
| `$_`        | 上一个命令的最后一个参数           |
| `$-`        | 当前 shell 选项标志          |

**`$@` vs `$*` 关键区别：**

```bash
# "$@" → 正确处理含空格的参数：["arg1", "arg2 with space"]
# "$*" → 全部合并为一个字符串："arg1 arg2 with space"

set "hello world" "foo bar"
for arg in "$@"; do echo "[$arg]"; done
# [hello world]
# [foo bar]

for arg in "$*"; do echo "[$arg]"; done
# [hello world foo bar]
```

### 2.4 参数展开（Parameter Expansion）

这是 Bash 最强大的特性之一。

```bash
# 默认值
${var:-default}      # var 未设置或为空 → 返回 default，var 不变
${var:=default}      # var 未设置或为空 → 赋值为 default 并返回
${var:?message}      # var 未设置或为空 → 打印 message 并退出
${var:+replacement}  # var 已设置且非空 → 返回 replacement，否则返回空

# 示例
name="${1:-匿名用户}"           # 给参数设置默认值
echo "${UNDEFINED_VAR:-42}"    # 42

# 必须参数检查
file="${1:?错误：请提供文件名}"
```

### 2.5 间接引用

```bash
var_name="HOME"
echo "${!var_name}"   # 输出 HOME 的值，相当于 echo "$HOME"
```

---

## 3. 字符串操作

### 3.1 基本操作

```bash
# 拼接
full="${first} ${last}"

# 长度
${#str}

# 子串
${str:0:5}            # 从位置0开始取5个字符
${str: -3}            # 最后3个字符（注意空格）

# 截取
${str#pattern}        # 从左删除最短匹配
${str##pattern}       # 从左删除最长匹配（贪婪）
${str%pattern}        # 从右删除最短匹配
${str%%pattern}       # 从右删除最长匹配（贪婪）

# 替换
${str/old/new}        # 替换第一个
${str//old/new}       # 替换全部
${str/#old/new}       # 替换开头
${str/%old/new}       # 替换结尾

# 大小写（Bash 4+）
${str^^}              # 全大写
${str,,}              # 全小写
${str^}               # 首字母大写
${str,}               # 首字母小写
```

**实用示例：**

```bash
path="/home/user/file.txt"

echo "${path##*/}"    # file.txt  （取文件名）
echo "${path%/*}"     # /home/user（取目录）
echo "${path%.*}"     # /home/user/file（去扩展名）
echo "${path##*.}"    # txt（取扩展名）
```

### 3.2 引号规则

```bash
# 双引号 ""：允许变量展开和命令替换，阻止分词和通配符
name="hello world"
echo "$name"          # hello world

# 单引号 ''：一切字面量，无展开
echo '$name'          # $name

# ANSI-C 引号 $''：支持转义序列
echo $'第一行\n第二行\t缩进'
```

### 3.3 Here Documents

```bash
# 基本用法
cat <<EOF
多行文本
变量 $name 会被展开
EOF

# 禁止展开（加引号）
cat <<'EOF'
多行文本
变量 $name 不会被展开
EOF

# Here String
command <<<"$variable"       # 将字符串作为 stdin
grep "pattern" <<<"$line"
```

---

## 4. 数组

### 4.1 索引数组

```bash
# 定义
arr=("a" "b" "c")
arr[3]="d"

# 访问
echo "${arr[0]}"        # 第一个元素
echo "${arr[@]}"        # 所有元素（独立展开）
echo "${arr[*]}"        # 所有元素（合并为一个字符串）
echo "${#arr[@]}"       # 数组长度
echo "${!arr[@]}"       # 所有索引

# 追加
arr+=("new")

# 切片
echo "${arr[@]:1:2}"    # 从索引1开始取2个元素

# 删除
unset arr[1]            # 删除元素（会留下空隙）
unset arr               # 删除整个数组
```

### 4.2 关联数组（Bash 4+）

```bash
declare -A map

map=([key1]="value1" [key2]="value2")
map["key3"]="value3"

echo "${map["key1"]}"
echo "${!map[@]}"       # 所有键
echo "${map[@]}"        # 所有值
echo "${#map[@]}"       # 长度

unset map["key1"]       # 删除键
```

### 4.3 数组遍历

```bash
# 索引数组
for item in "${arr[@]}"; do
    echo "$item"
done

# 按索引遍历
for i in "${!arr[@]}"; do
    echo "$i: ${arr[$i]}"
done

# 关联数组
for key in "${!map[@]}"; do
    echo "$key -> ${map[$key]}"
done
```

**重要：** 永远给数组引用加双引号 `"${arr[@]}"`，否则含空格的元素会断裂。

---

## 5. 条件判断

### 5.1 test 命令

`[` 是 `test` 的别名，`[[` 是 Bash 关键字（更强大，推荐）。

```bash
# [ ]   POSIX 标准，不直接支持 || 和正则
# [[ ]] Bash 专属，功能更强，不需要转义

[[ "abc" == a* ]]        # 通配符匹配
[ "abc" == a* ]          # 字面比较，不匹配
```

### 5.2 字符串比较

```bash
[[ -z "$str" ]]         # 空串
[[ -n "$str" ]]         # 非空
[[ "$a" == "$b" ]]      # 相等
[[ "$a" != "$b" ]]      # 不等
[[ "$a" < "$b" ]]       # 字典序小于
[[ "$a" > "$b" ]]       # 字典序大于
[[ "$str" == pattern ]] # 通配符匹配
[[ "$str" =~ regex ]]   # 正则匹配

# 示例
[[ "$filename" == *.txt ]]
[[ "$phone" =~ ^[0-9]{11}$ ]]
```

### 5.3 数值比较

```bash
[[ "$a" -eq "$b" ]]     # 等于
[[ "$a" -ne "$b" ]]     # 不等于
[[ "$a" -lt "$b" ]]     # 小于
[[ "$a" -le "$b" ]]     # 小于等于
[[ "$a" -gt "$b" ]]     # 大于
[[ "$a" -ge "$b" ]]     # 大于等于

# 也可以用算术扩展
(( a == b ))
(( a < b ))
(( a >= b ))
```

### 5.4 文件测试

```bash
[[ -e "$path" ]]        # 存在（文件和目录）
[[ -f "$path" ]]        # 是普通文件
[[ -d "$path" ]]        # 是目录
[[ -L "$path" ]]        # 是符号链接
[[ -r "$path" ]]        # 可读
[[ -w "$path" ]]        # 可写
[[ -x "$path" ]]        # 可执行
[[ -s "$path" ]]        # 非空
[[ -t "$fd" ]]          # fd 是否指向终端
[[ "$f1" -nt "$f2" ]]   # f1 比 f2 新
[[ "$f1" -ot "$f2" ]]   # f1 比 f2 旧
```

### 5.5 逻辑运算

```bash
[[ cond1 && cond2 ]]    # AND
[[ cond1 || cond2 ]]    # OR
[[ ! cond ]]            # NOT

# 在 [ ] 中使用 -a, -o
[ cond1 -a cond2 ]
[ cond1 -o cond2 ]
[ ! cond ]
```

### 5.6 if / case 结构

```bash
if [[ "$score" -ge 90 ]]; then
    echo "优秀"
elif [[ "$score" -ge 60 ]]; then
    echo "及格"
else
    echo "不及格"
fi
```

```bash
case "$os" in
    linux)
        echo "Linux 系统"
        ;;
    macos|darwin)
        echo "macOS 系统"
        ;;
    *)
        echo "其他系统: $os"
        ;;
esac
```

```bash
# 三元风格（条件执行）
[[ -d "$dir" ]] && echo "存在" || echo "不存在"
# 注意：|| 后面会在 && 失败或成功后的命令失败时都执行
# 更安全：if [[ -d "$dir" ]]; then echo "存在"; else echo "不存在"; fi
```

---

## 6. 循环与迭代

### 6.1 for 循环

```bash
# 列表遍历
for file in *.txt; do
    echo "$file"
done

# C 风格
for ((i = 0; i < 10; i++)); do
    echo "$i"
done

# 大括号展开
for i in {1..10}; do
    echo "$i"
done

for i in {1..10..2}; do   # 步长（Bash 4+）
    echo "$i"
done
```

### 6.2 while / until

```bash
# while：条件为真时循环
count=1
while [[ "$count" -le 5 ]]; do
    echo "$count"
    ((count++))
done

# until：条件为假时循环
until [[ -f "/tmp/ready" ]]; do
    sleep 1
done

# 无限循环
while true; do
    # ...
    sleep 1
done
```

### 6.3 循环控制

```bash
break        # 跳出循环
break 2      # 跳出两层
continue     # 跳过本次迭代
continue 2   # 跳过外层
```

### 6.4 管道中的循环

```bash
# 管道中的循环在子 shell 中执行，变量不会保留
find . -type f | while read -r line; do
    count=$((count + 1))   # 这个 count 在管道结束后丢失
done

# 解决方案1：进程替换
while read -r line; do
    count=$((count + 1))
done < <(find . -type f)

# 解决方案2：Bash 4.2+ 设置 lastpipe
shopt -s lastpipe
```

### 6.5 select 菜单

```bash
select option in "叉烧饭" "海南鸡饭" "云吞面" "退出"; do
    case "$option" in
        "退出") break ;;
        "叉烧饭"|"海南鸡饭"|"云吞面") echo "您选择了: $option" ;;
        *) echo "无效选择" ;;
    esac
done
```

---

## 7. 函数

### 7.1 函数定义

```bash
# 两种写法
function my_func {
    # 函数体
}

my_func() {
    # 函数体（推荐，可移植性更好）
}
```

### 7.2 参数与返回值

```bash
greet() {
    local name="$1"          # 函数参数：$1, $2, ...
    local times="${2:-1}"    # 第二个参数带默认值

    for ((i = 0; i < times; i++)); do
        echo "你好, ${name}!"
    done

    return 0                 # 返回 0-255 整数
}

greet "世界" 3

# 返回字符串（两种方式）
get_config() {
    echo "$result"           # 方式1：用 echo（配合命令替换）
    # 不能有其他 echo，否则会污染输出
}

value=$(get_config)

get_config_alt() {
    local __resultvar="$1"
    eval "$__resultvar='$result'"  # 方式2：用引用变量
}
get_config_alt my_var              # my_var 现在包含结果
```

### 7.3 私有函数命名约定

```bash
# 用 _ 前缀表示"私有"（约定，非语法约束）
_private_helper() {
    # ...
}

# 用 _ 前缀区分同名命令（避免 shadowing）
_ls() {
    ls --color=auto -h "$@"
}
```

---

## 8. I/O 与重定向

### 8.1 文件描述符

| FD | 名称 | 用途 |
|----|------|------|
| 0 | stdin | 标准输入 |
| 1 | stdout | 标准输出 |
| 2 | stderr | 标准错误 |
| 3-9 | 自定义 | 额外文件描述符 |

### 8.2 基本重定向

```bash
cmd > file               # stdout 覆盖写入
cmd >> file              # stdout 追加写入
cmd < file               # 从文件读取 stdin
cmd 2> file              # stderr 重定向
cmd 2>&1                 # stderr 合并到 stdout
cmd &> file              # stdout + stderr 都重定向
cmd |& cmd2              # stdout + stderr 都管道传输

# 常见模式
cmd >/dev/null 2>&1      # 静默执行（丢弃所有输出）
cmd &>/dev/null          # 同上，简洁写法
> file                   # 清空/创建文件
```

**`2>&1` 的顺序陷阱：**

```bash
# 正确：先重定向 stdout 到文件，再让 stderr 跟过去
command > output.txt 2>&1
# 结果：stdout 和 stderr 都进入 output.txt

# 错误：顺序颠倒
command 2>&1 > output.txt
# 结果：stderr 仍输出到终端，只有 stdout 进入文件
# 原因：2>&1 执行时 stdout 还指向终端，之后 > 只重定向了 stdout
```

### 8.3 自定义文件描述符

```bash
# 打开文件描述符3写入
exec 3>file.log
echo "日志内容" >&3
exec 3>&-               # 关闭

# 打开文件描述符3读取
exec 3<file.txt
read -r line <&3
exec 3<&-

# 双向读写
exec 3<>/dev/tcp/example.com/80
echo "GET / HTTP/1.0" >&3
cat <&3
```

### 8.4 Process Substitution

```bash
# 将命令输出当作文件
diff <(ls dir1) <(ls dir2)
cat <(echo "hello") <(echo "world")

# 将文件当作命令输入
command > >(gzip > file.gz)
```

### 8.5 read 命令

```bash
read -r var              # -r 禁止反斜杠转义，几乎总是需要
read -p "请输入:" var    # 带提示
read -s password         # 隐藏输入
read -t 5 var            # 超时（秒）
read -a arr              # 读入数组
read -r line1 line2      # 按空格分割多个字段

# 逐行读取文件（标准写法）
while IFS= read -r line; do
    echo "第${LINE}行: $line"
done < "$input_file"
```

`IFS=` 防止去除行首尾空白，`-r` 防止反斜杠转义。这两点极其重要。

---

## 9. 进程与作业控制

### 9.1 后台与前台

```bash
cmd &                    # 后台运行
nohup cmd &              # 忽略 SIGHUP，登出后继续
disown                   # 当前作业脱离 shell 控制

jobs                     # 列出作业
fg %1                    # 将作业1调到前台
bg %1                    # 将作业1放后台运行

Ctrl+Z                   # 挂起当前前台作业
Ctrl+C                   # 中断当前前台作业
```

### 9.2 子 Shell

```bash
# ( ) 创建子 shell，不影响当前环境
(cd /tmp && rm -f temp)

# { } 在当前 shell 执行（注意空格和分号）
{ cd /tmp && rm -f temp; }

# 测试是否在子 shell
echo "$BASH_SUBSHELL"   # > 0 表示在子 shell 中
```

### 9.3 信号处理

```bash
trap 'echo "收到 SIGINT，正在清理..." && exit 1' INT TERM
trap 'rm -f /tmp/lockfile' EXIT      # 脚本退出时清理
trap '' INT                           # 忽略 SIGINT
trap -p                               # 列出所有 trap
trap - INT TERM                       # 恢复默认处理

# 常见信号
# HUP(1), INT(2), QUIT(3), KILL(9), TERM(15), USR1(10), USR2(12)
```

### 9.4 wait 与超时

```bash
# 等待子进程
pid1=$(cmd1 & echo $!)
pid2=$(cmd2 & echo $!)
wait "$pid1" "$pid2"
echo "全部完成"

# 带超时
timeout 5 ping google.com
timeout -s KILL 10 slow_cmd
```

---

## 10. 错误处理与调试

### 10.1 严格模式

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'              # 防止空格和制表符分词
```

### 10.2 错误捕获

```bash
# 全局错误处理
trap 'handle_error $LINENO' ERR

handle_error() {
    echo "第 $1 行出错，退出码: $?" >&2
    exit 1
}

# 函数级错误处理
do_something || {
    echo "操作失败" >&2
    return 1
}

# 静默失败
grep pattern file 2>/dev/null || true
```

### 10.3 调试技巧

```bash
# 运行时调试
bash -x script.sh       # 逐行打印
bash -n script.sh       # 语法检查（不执行）
bash -v script.sh       # 逐行打印原始源码

# 脚本内调试
set -x                  # 开启调试
# ... 调试区域
set +x                  # 关闭调试

# 指定行范围调试
set -x
# 需要调试的代码
set +x

# 打印调试信息
echo "DEBUG: var=$var, line=$LINENO" >&2

# PS4 自定义调试前缀
export PS4='+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
```

### 10.4 ShellCheck

```bash
# 静态分析工具，强烈推荐
shellcheck script.sh

# 常见检测项：
# - 未引用变量
# - 未使用的变量
# - read 缺少 -r
# - 错误的 test 语法
```

---

## 11. 常用命令速查

### 11.1 文本处理

```bash
# grep - 搜索
grep -n "pattern" file       # 显示行号
grep -i "pattern" file       # 忽略大小写
grep -r "pattern" dir/       # 递归搜索
grep -v "pattern" file       # 反向匹配
grep -E "pattern" file       # 扩展正则（等同于 egrep）
grep -A 3 -B 2 "pat" file   # 上下文

# sed - 流编辑器
sed 's/old/new/' file        # 替换首个
sed 's/old/new/g' file       # 全局替换
sed -i 's/old/new/g' file    # 直接修改文件
sed '/^$/d' file             # 删除空行
sed -n '5,10p' file          # 打印 5-10 行

# awk - 文本分析
awk '{print $1}' file        # 打印第一列
awk -F',' '{print $2}' file  # 逗号分隔
awk '$3 > 50' file           # 过滤
awk '{sum+=$1} END{print sum}'  # 求和
```

### 11.2 文件操作

```bash
# 查找
find . -name "*.txt"         # 按名称
find . -type f -mtime -7     # 7天内修改的文件
find . -size +1M             # 大于1MB
find . -name "*.tmp" -delete # 查找并删除
find . -name "*.log" -exec gzip {} \;   # 逐个执行
find . -name "*.log" -exec gzip {} +    # 批量执行

# 排序去重
sort file                    # 排序
sort -n file                 # 数值排序
sort -rn file                # 逆序数值
sort -u file                 # 去重
sort file | uniq -c          # 计数去重
sort file | uniq -d          # 只显示重复

# 统计
wc -l file                   # 行数
wc -w file                   # 单词数
wc -c file                   # 字节数

# 其他
cut -d: -f1 /etc/passwd      # 按分隔符取列
tee file                     # 同时输出到文件和控制台
xargs -n1 cmd                # 将 stdin 转为参数
```

> 文本处理命令（grep / sed / awk / cut / sort / uniq / wc / tr / xargs / tee）的详细用法见 [Linux文本处理命令.md](Linux文本处理命令.md)。

### 11.3 系统信息

```bash
date                         # 日期
date +"%Y-%m-%d %H:%M:%S"   # 格式化
date -d "yesterday"

df -h                        # 磁盘使用
du -sh dir/                  # 目录大小

ps aux                       # 进程状态
top                          # 实时进程

env                          # 环境变量
which cmd                    # 命令位置
command -v cmd               # 比 which 更可靠

export                       # 显示所有导出的变量
readonly                     # 显示只读变量
```

### 11.4 条件执行

```bash
cmd1 && cmd2          # cmd1 成功才执行 cmd2
cmd1 || cmd2          # cmd1 失败才执行 cmd2
cmd1 && cmd2 || cmd3  # 三元效果（需谨慎）
```

---

## 12. 脚本模板与最佳实践

### 12.1 生产级脚本模板

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# --- 配置 ---
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# --- 函数 ---
usage() {
    cat <<EOF
用法: $SCRIPT_NAME [选项] <参数>

选项:
    -h, --help      显示此帮助信息
    -v, --verbose   详细输出
    -o, --output DIR 输出目录（默认: ./output）

示例:
    $SCRIPT_NAME -o /tmp/results input.txt
EOF
    exit 0
}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

die() {
    log "错误: $*"
    exit 1
}

cleanup() {
    local exit_code=$?
    log "清理临时文件..."
    rm -rf "$TEMP_DIR"
    exit "$exit_code"
}

# --- 参数解析 ---
OUTPUT_DIR="./output"
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)    usage ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -o|--output)  OUTPUT_DIR="$2"; shift 2 ;;
        --)           shift; break ;;
        -*)           die "未知选项: $1" ;;
        *)            break ;;
    esac
done

# --- 主逻辑 ---
main() {
    local input="${1:?错误: 缺少输入参数}"

    TEMP_DIR="$(mktemp -d)"
    trap cleanup EXIT INT TERM

    [[ "$VERBOSE" == true ]] && log "输入文件: $input"
    [[ "$VERBOSE" == true ]] && log "输出目录: $OUTPUT_DIR"

    mkdir -p "$OUTPUT_DIR"

    # 你的业务逻辑...
    log "处理完成"
}

main "$@"
```

### 12.2 最佳实践清单

1. **永远双引号包裹变量**：`echo "$var"` 而非 `echo $var`
2. **用 `$(cmd)` 而非反引号** `` `cmd` ``：现代写法，可嵌套
3. **`read` 加 `-r`**：防止反斜杠转义
4. **开启 `set -euo pipefail`**：尽早暴露问题
5. **用 `[[ ]]` 替代 `[ ]`**：功能更强，更安全
6. **用 `printf` 替代 `echo`**（复杂场景）：`echo` 行为因系统而异
7. **局部变量用 `local`**：防止污染全局作用域
8. **用 `command -v` 检查命令是否存在**：比 `which` 更可靠
9. **数组引用加引号 `"${arr[@]}"`**：保护含空格的元素
10. **用 ShellCheck 静态检查**：`shellcheck script.sh`

---

## 13. 进阶技巧

### 13.1 算术运算

```bash
# 方式1：算术扩展（推荐）
result=$((1 + 2 * 3))

# 方式2：let
let "result = 1 + 2 * 3"

# 方式3：declare -i
declare -i num
num = 5 + 3

# 常见运算
((a++))                  # 自增
((a % 2 == 0))           # 取模、比较
echo $((RANDOM % 100))   # 0-99 随机数
```

### 13.2 花括号展开

```bash
echo {a,b,c}.txt          # a.txt b.txt c.txt
echo {1..5}               # 1 2 3 4 5
echo {01..10}             # 01 02 ... 10（0 补齐）
echo {a..z}               # a b c ... z
echo {1..30..3}           # 1 4 7 10 ... 28
```

### 13.3 shopt 配置

```bash
shopt -s globstar         # 启用 ** 递归通配
shopt -s nullglob         # 无匹配时展开为空，而非原字符
shopt -s dotglob          # 通配符匹配隐藏文件
shopt -s extglob          # 扩展通配符：?(abc) *(abc) +(abc) @(abc) !(abc)
shopt -s lastpipe         # 管道最后一个命令在当前 shell 执行
shopt -s histappend       # 追加历史，不覆盖
```

### 13.4 命名管道（FIFO）

```bash
mkfifo mypipe

# 终端1
cat > mypipe

# 终端2
cat < mypipe
```

### 13.5 Coprocess（协程）

```bash
# 双工通信
coproc bc_proc { bc -l; }

echo "1+2" >&"${bc_proc[1]}"   # 写入协程
read -r result <&"${bc_proc[0]}" # 读取结果
echo "$result"
```

### 13.6 网络操作

```bash
# /dev/tcp（Bash compiled with --enable-net-redirections）
exec 3<>/dev/tcp/example.com/80
echo -e "GET / HTTP/1.1\nHost: example.com\n\n" >&3
cat <&3

# 检查端口
timeout 1 bash -c 'echo >/dev/tcp/example.com/22' && echo "开放" || echo "关闭"
```

### 13.7 常用设计模式

```bash
# 锁文件（防止重复运行）
LOCKFILE="/tmp/$(basename "$0").lock"
exec 200>"$LOCKFILE"
flock -n 200 || die "已有实例在运行"

# 命令存在性检查
require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "需要安装: $1"
}
require_cmd jq
require_cmd curl

# 加载配置文件
load_config() {
    local config="${1:-./default.conf}"
    [[ -f "$config" ]] && source "$config"
}

# 重试机制
retry() {
    local max=3
    local delay=1
    for ((i = 1; i <= max; i++)); do
        "$@" && return 0
        echo "重试 $i/$max..." >&2
        sleep "$delay"
    done
    return 1
}
retry curl -s https://api.example.com/data
```

---

## 参考资源

- [Bash 手册](https://www.gnu.org/software/bash/manual/)
- [ShellCheck](https://www.shellcheck.net/)
- [Bash Hackers Wiki](https://wiki.bash-hackers.org/)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [Greg's Wiki: BashGuide](https://mywiki.wooledge.org/BashGuide)
- [The Art of Command Line](https://github.com/jlevy/the-art-of-command-line)
