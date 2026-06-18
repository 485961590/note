## 确定上一条命令是否成功执行
| $?  | 成功返回0，错误返回其它 |
| --- | ------------ |
## 基本光标移动

| 快捷键        | 功能       |
| ---------- | -------- |
| `Ctrl + A` | 移动到行首    |
| `Ctrl + E` | 移动到行尾    |
| `Alt + B`  | 向后移动一个单词 |
| `Alt + F`  | 向前移动一个单词 |
| `Ctrl + B` | 向后移动一个字符 |
| `Ctrl + F` | 向前移动一个字符 |
## 历史命令导航
|快捷键|功能|
|---|---|
|`Ctrl + P`|上一条命令|
|`Ctrl + N`|下一条命令|
|`Ctrl + R`|反向搜索历史命令|
|`↑` 箭头|上一条命令|
|`↓` 箭头|下一条命令|
## 命令行快捷键
| 快捷键        | 功能         |
| ---------- | ---------- |
| `Ctrl + U` | 删除光标前的所有内容 |
| `Ctrl + K` | 删除光标后的所有内容 |
| `Ctrl + W` | 删除前一个单词    |
| `Ctrl + Y` | 粘贴刚才删除的内容  |
| `Ctrl + D` | 删除当前字符     |
| `Ctrl + H` | 删除前一个字符    |
## VIM快捷键

| 目的    | 命令           | 说明         |
| ----- | ------------ | ---------- |
| 保存    | `:w`         | 写入文件       |
| 退出    | `:q`         | 退出（未保存会提示） |
| 强制退出  | `:q!`        | 放弃修改强制退出   |
| 保存退出  | `:wq` 或 `ZZ` | 存盘后退出      |
| 撤销    | `u`          | 撤回上一步      |
| 重做    | `Ctrl + r`   | 撤销后再恢复     |
| 复制当前行 | `yy`         | 复制整行到寄存器   |
| 粘贴    | `p`          | 粘贴到光标后     |
| 删除当前行 | `dd`         | 剪切整行       |
| 搜索    | `/关键词`       | 向下查找       |
### 快速移动

| 目的       | 命令                   |
| -------- | -------------------- |
| 行首       | `0` 或 `^`            |
| 行尾       | `$`                  |
| 文件开头     | `gg`                 |
| 文件结尾     | `G`                  |
| 跳转到第 N 行 | `:N` 或 `Ng`（如 `42G`） |
| 向下翻页     | `Ctrl + f`           |
| 向上翻页     | `Ctrl + b`           |
| 设置行号     | :set nu              |
| 取消行号     | :set nonu            |

### 快速编辑

|目的|命令|
|---|---|
|进入插入（光标前）|`i`|
|进入插入（行尾）|`A`|
|换行并插入|`o`（下方新行）/ `O`（上方）|
|删除一个字符|`x`|
|删除到行尾|`d$`|
|删除单词|`dw`|
|替换一个字符|`r` + 新字符|

### 可视模式（选中）

|目的|命令|
|---|---|
|字符选择|`v`|
|行选择|`V`|
|复制选中内容|`y`|
|删除选中内容|`d`|
|替换选中内容|`c`|

### 批量操作（省时利器）

|目的|命令|
|---|---|
|全文替换|`:%s/old/new/g`|
|指定行替换|`:10,20s/old/new/g`|
|复制第 5 行到第 10 行后|`:5t10`|
|移动第 5 行到第 10 行后|`:5m10`|
|多行缩进|`>>`（右）/ `<<`（左）|

## 屏幕控制
|快捷键|功能|
|---|---|
|`Ctrl + L`|清屏|
|`Ctrl + S`|暂停输出|
|`Ctrl + Q`|恢复输出|
## 共享文件夹
```bash
# 查看可用的共享文件夹
vmware-hgfsclient

# 手动挂载共享文件夹
sudo mkdir -p /mnt/hgfs
sudo /usr/bin/vmhgfs-fuse .host:/ /mnt/hgfs -o subtype=vmhgfs-fuse,allow_other
# 创建桌面的连接相当于快捷方式
kali中：
ln -s /mnt/hgfs/share/ /home/kali/桌面/共享文件夹name(share)
centos中：
ln -s /mnt/hgfs/share/ /home/user/桌面/共享文件夹name(share)
# 查看共享文件
ls /mnt/hgfs/share/
```
## 移动文件 / 重命名（mv）

```bash
mv [选项] <源文件或目录> <目标路径>
```

| 选项 | 说明 |
|------|------|
| `-i` | 交互模式，目标已存在时询问是否覆盖（推荐新手使用） |
| `-v` | 显示详细操作信息 |
| `-f` | 强制模式，直接覆盖不提示 |
| `-n` | 不覆盖已存在的文件 |
| `-u` | 仅当源比目标新、或目标不存在时才移动 |
| `-b` | 覆盖前先创建备份（原文件加 `~` 后缀） |
| `-t 目录` | 指定目标目录（源文件放最后，配合 xargs 传文件列表时很有用） |

**重命名：**

```bash
mv oldname.txt newname.txt
mv oldname.txt /home/kali/Documents/newname.txt
```

**移动：**

```bash
# 移动单个文件到目录
mv file.txt /home/kali/Documents/

# 移动目录（不需要 -r，mv 天然递归）
mv project/ /home/kali/backup/

# 一次移动多个文件
mv *.log /var/log/archive/
mv file1.txt file2.py script.sh /home/kali/Documents/

# 移动目录内容（注意和移动目录本身的区别）
mv source/* target/       # 移动内容
mv source/ target/        # 移动目录本身
```

**交互与安全——防覆盖：**

```bash
# 交互模式——每次冲突都问你
mv -i *.txt target/

# 不覆盖已存在的文件（静默跳过）
mv -n *.txt target/

# 移动前先备份目标目录里可能被覆盖的文件
mv -b source/* target/   # target 里同名文件会自动备份为 file~
```

**批量后缀修改（mv 无法直接用通配符改后缀，需要 for 循环）：**

```bash
# 把当前目录下所有 .txt 改成 .md
for f in *.txt; do mv "$f" "${f%.txt}.md"; done

# 把所有 .jpg 改成 .jpeg
for f in *.jpg; do mv "$f" "${f%.jpg}.jpeg"; done
```

**配合 xargs 批量移动：**

```bash
# 把找到的所有 .log 文件移到 archive
find . -name "*.log" | xargs -I {} mv {} /home/kali/logs/archive/

# 用 -t 更安全（目标在前，不会因为文件名带空格而错乱）
find . -name "*.log" -print0 | xargs -0 mv -t /home/kali/logs/archive/
```
## 解压

| 压缩格式              | 文件扩展名                | 解压命令                  | 安装命令 (如果未预装)                  |
| ----------------- | -------------------- | --------------------- | ----------------------------- |
| **ZIP**           | `.zip`               | `unzip`               | `sudo apt install unzip`      |
| **TAR** (仅打包，未压缩) | `.tar`               | `tar -xf`             | (通常已安装)                       |
| **Gzip**          | `.gz` 或 `.tgz`       | `gunzip` 或 `tar -xzf` | (通常已安装)                       |
| **TAR + Gzip**    | `.tar.gz` 或 `.tgz`   | `tar -xzf`            | (通常已安装)                       |
| **TAR + Bzip2**   | `.tar.bz2` 或 `.tbz2` | `tar -xjf`            | (通常已安装)                       |
| **TAR + XZ**      | `.tar.xz` 或 `.txz`   | `tar -xJf`            | `sudo apt install xz-utils`   |
| **7-Zip**         | `.7z`                | `7z x`                | `sudo apt install p7zip-full` |
| **RAR**           | `.rar`               | `unrar x` 或 `rar x`   | `sudo apt install unrar`      |
#### 解压 ZIP 文件 (`.zip`)

```bash
# 基本解压（解压到当前目录）
unzip archive.zip

# 解压到指定目录（使用 -d 选项）
unzip archive.zip -d /path/to/target/directory/

# 列出压缩包内容（不解压）
unzip -l archive.zip
```
## 删除文件

> **重要警告：** Linux/Unix 命令行删除文件通常是不可逆的，没有”回收站”概念，一旦删除很难恢复。请务必谨慎操作！

```bash
# 删除单个文件
rm [选项] <文件或目录名>

# 删除空目录（只能删除空文件夹，更安全）
rmdir empty_folder/
```

| 选项 | 说明 |
|------|------|
| `-i` | 交互模式，删除前逐一询问确认（强烈推荐新手使用） |
| `-v` | 显示详情，告知删除了什么 |
| `-f` | 强制删除，忽略不存在的文件，不做任何提示（非常危险！） |
| `-r` / `-R` | 递归删除目录及其内部所有内容（与 `-f` 结合时威力极大，请慎用） |
## 创建文件/文件夹

```bash
# 创建单个空文件
touch newfile.txt

# 一次性创建多个空文件
touch file1.txt file2.py script.sh

# 创建带空格的文件名（需要用引号包裹）
touch "my report.docx"

# 创建一个空文件（与 `touch` 效果类似）
> empty_file.txt

# 创建一个带有初始内容的文件（非常实用！）
echo "Hello, Kali Linux!" > welcome.txt

# 追加内容到文件（如果文件不存在也会创建）
echo "This is a new line." >> logfile.log


# 创建文件夹
mkdir new_folder
```

| 选项 | 说明 |
|------|------|
| `-p` | 递归创建，一次性创建多级不存在的父目录 |
| `-v` | 显示详情，告知创建了哪些目录 |
| `-m` | 设置权限，创建时直接指定权限模式 |

## 复制文件/文件夹（cp）

```bash
cp [选项] <源文件> <目标路径>
```

| 选项 | 说明 |
|------|------|
| `-r` / `-R` | 递归复制整个目录（复制文件夹必须加这个） |
| `-i` | 交互模式，目标已存在时询问是否覆盖 |
| `-v` | 显示详细操作信息——抄了什么文件 |
| `-f` | 强制覆盖，不提示 |
| `-n` | 不覆盖已存在的文件（和 `-f` 冲突） |
| `-p` | 保留源文件的权限、时间戳等属性（`-a` 的子集） |
| `-a` | 归档模式——等于 `-dR --preserve=all`，递归 + 保留全部属性 + 跟随符号链接 |
| `-u` | 仅当源比目标新、或目标不存在时才复制（增量备份用） |
| `-b` | 覆盖前先创建备份文件（文件名加 `~` 后缀） |
| `-l` | 不复制内容，创建硬链接 |
| `-s` | 不复制内容，创建符号链接 |
| `-T` | 把目标当作普通文件而不是目录（避免歧义） |
| `--parents` | 保留源文件的完整目录结构 |

**基础用法：**

```bash
# 复制单个文件
cp file.txt /home/kali/Documents/

# 复制并重命名
cp file.txt /home/kali/Documents/newname.txt

# 复制整个目录（-r 必须加，否则报错）
cp -r project/ /home/kali/backup/

# 复制目录里的内容（不包括目录本身）
cp -r project/* /home/kali/backup/

# 一次复制多个文件到同一个目录
cp file1.txt file2.py script.sh /home/kali/Documents/
```

**保留属性复制（备份推荐）：**

```bash
# 保留权限、时间戳（-p）
cp -rp project/ /mnt/backup/

# 归档模式（-a 啥都保留——权限、时间、软链接、特殊文件等）
cp -a /etc/nginx /mnt/backup/etc/
# 这是做完整备份的首选方式
```

**防覆盖/增量复制：**

```bash
# 交互模式——每个冲突文件都会问你覆盖不覆盖
cp -ri source/ target/

# 只复制更新的文件（目标没有的才复制，源更旧的跳过）
cp -ru source/ target/

# 覆盖前自动备份原文件（备份文件就是原文件名加个 ~）
cp -rb source/ target/
```

**常见场景：**

```bash
# 复制当前目录下所有 .txt 文件到目标
cp *.txt /home/kali/Documents/

# 递归复制但排除某些文件（cp 本身不支持排除，配合 rsync 或 find）
find . -name '*.py' -exec cp --parents {} /backup/ \;

# 复制时显示进度（cp 本身无进度条，改用 rsync 或 scp）
rsync -ah --progress source/ target/
```
## 查找文件

### find
```bash
find [起始目录] [查找条件] [执行操作]
	# 1. 按名称查找
# 在当前目录及子目录下精确查找名为 config.txt 的文件
find . -name "config.txt"
# 忽略文件名大小写
find /home -iname "readme.md"
# 使用通配符，查找所有 .log 结尾的文件
find /var/log -name "*.log"
	# 2. 按类型查找
# 查找普通文件（-f）、目录（-d）、符号链接（-l）
find /usr/bin -type l          # 查找符号链接
find /tmp -type f -name "*.tmp" # 查找普通文件且以 .tmp 结尾
	# 3. 按大小查找
# 查找大于 100MB 的文件 (+ 表示大于，- 表示小于)
find / -type f -size +100M
# 查找大小在 10KB 到 1MB 之间的文件
find . -size +10k -size -1M
	# 4. 按时间查找（非常实用）
# 查找最近 7 天内被修改过的文件（mtime 修改时间）
find /home -type f -mtime -7
# 查找 30 天前访问过的文件（atime 访问时间）
find /var/www -type f -atime +30
	# 5. 按权限/用户/组查找
# 查找权限为 777 的文件
find / -type f -perm 777
# 查找属于用户 alice 的文件
find /home -user alice
# 查找所属组为 dev 的文件
find /opt -group dev
```
### locate（基于索引，速度极快）
`locate`命令通过查询一个预建的文件名数据库（通常是`/var/lib/mlocate/mlocate.db`）来查找文件，速度非常快，通常是秒级响应。
**特点：**
- **优点：** 速度极快。
- **缺点：** 数据库可能不是最新的。新建的文件需要等待数据库更新后才能被找到。
- **更新数据库：** 手动运行 `sudo updatedb`。
```bash
# 查找所有包含 “passwd” 路径名的文件
locate passwd

# 使用通配符进行更精确的匹配
locate "*.jpg"

# 限制查找结果的数量（例如，只显示前 10 个）
locate -n 10 "*.log"
```
### which 和 whereis（查找命令/程序）
这两个命令专门用于查找**可执行程序**及其相关文件。
1. **`which`**： 查找一个命令的**完整路径**（在 `$PATH` 环境变量中）。
```bash
which python
# 输出：/usr/bin/python 或 /home/user/.pyenv/shims/python
```
2. **`whereis`**： 查找一个命令的**二进制程序、源代码和手册页**的位置。
```bash
whereis ls
# 输出：ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz
```
### 综合示例
```bash
locate password.txt
locate -n 20 .conf  # 只显示前 20 个包含 .conf 的结果
sudo updatedb # 更新 locate 数据库（如果找不到新文件）

which nmap
# 输出：/usr/bin/nmap

# 在当前目录递归搜索包含 "password" 字符串的文件
grep -r "password" .

# 不区分大小写地搜索
grep -ri "username" /var/www/

# 只显示包含匹配内容的文件名
grep -rl "192.168.1." /etc/
	-r：递归搜索
	-i：忽略大小写
	-l：只列出包含匹配项的文件名
	
# 在 / 目录下查找名为 passwd 的文件
find / -name passwd

# 在当前目录及子目录中查找名为 config.php 的文件
find . -name config.php
```
## 查看文件
|命令|主要用途|优点|缺点|
|---|---|---|---|
|**`cat`**|快速查看**整个**小文件|简单直接|文件过大时终端会刷屏|
|**`less`**|**分页**查看大文件（推荐）|可前后翻页、搜索、不会刷屏|需要学习基本快捷键|
|**`more`**|分页查看大文件（老式）|简单分页|只能向前翻页，功能较少|
|**`head`**|查看文件**开头**几行|快速查看文件头部|只能看开头|
|**`tail`**|查看文件**末尾**几行|快速查看日志尾部、实时监控|只能看末尾|
|**`nl`**|**带行号**查看文件|方便调试和引用特定行|功能与 `cat -n` 类似|
|**`strings`**|查看二进制文件中的**可打印字符串**|分析二进制文件、提取信息|不显示不可打印字符|

## 创建链接（ln）

```bash
ln [选项] <源文件> <链接名>
```

| 选项 | 说明 |
|------|------|
| `-s` | 创建符号链接（软链接），类似 Windows 的快捷方式 |
| `-f` | 强制覆盖已存在的目标文件 |
| `-n` | 如果目标是已存在的符号链接，不要跟随它（避免意外套娃） |
| `-v` | 显示详细操作信息 |

**符号链接（软链接）——最常用：**

```bash
# 创建软链接
ln -s /opt/tool/bin/exec /usr/local/bin/exec

# 创建目录的软链接
ln -s /mnt/hgfs/share ~/桌面/共享文件夹

# 删除软链接（和删普通文件一样，不影响源文件）
rm /usr/local/bin/exec

# 查看链接指向哪里
ls -l /usr/local/bin/exec
# 输出：/usr/local/bin/exec -> /opt/tool/bin/exec

# 修改软链接指向（用 -sfn 覆盖）
ln -sfn /opt/tool-v2/bin/exec /usr/local/bin/exec
```

**硬链接——注意和软链接的区别：**

```bash
# 创建硬链接（两个文件名指向同一个 inode，同一个物理数据）
ln /data/bigfile.dat /backup/bigfile.dat

# 硬链接删掉任意一个文件，另一个还能正常访问数据
# 必须是同一文件系统内才能做硬链接，不能跨分区
```

| | 符号链接（-s） | 硬链接 |
|---|---|---|
| 本质 | 路径指针——存的是源文件的路径 | 同一 inode 的别名——指向同一份物理数据 |
| 跨文件系统 | 可以 | 不可以 |
| 指向目录 | 可以 | 不可以（一般不允许） |
| 源文件删除后 | 链接变死链接（dangling），指向失效 | 另一个链接还能访问数据 |
| 类比 | Windows 快捷方式 | 文件的另一个分身 |

**实用场景：**

```bash
# 把工具加入 PATH（比改 PATH 变量更干净）
sudo ln -s /opt/nmap/bin/nmap /usr/local/bin/nmap

# 版本管理——v1 切 v2 只需改一次链接
/opt/app/
  myapp-v1.0/
  myapp-v2.0/
  current -> myapp-v2.0/        # 指向当前在用版本

# 切换版本
ln -sfn /opt/app/myapp-v2.0 /opt/app/current

# 找回磁盘空间——软链接挪走大目录
sudo mv /var/lib/docker /mnt/data/docker
sudo ln -s /mnt/data/docker /var/lib/docker
```

## 查看文件类型（file）

```bash
# 基础用法——判断一个文件到底是什么类型的
file unknown_file
# 输出：unknown_file: ELF 64-bit LSB executable, x86-64

file report.pdf
# 输出：report.pdf: PDF document, version 1.4

# 查看多个文件
file *.txt
file /usr/bin/*

# 显示 MIME 类型（脚本里更好解析）
file -i index.html
# 输出：index.html: text/html; charset=utf-8

# 不解压查看压缩包类型
file archive.unknown
# 输出：archive.unknown: Zip archive data

# 查看软链接指向的文件类型（不加选项默认会跟随链接）
file /usr/bin/python
# 输出：/usr/bin/python: symbolic link to python3
```

## 磁盘与目录占用（du / df）

### df — 查看分区剩余空间

```bash
# 人类可读格式（KB/MB/GB）
df -h

# 只看本地物理分区（排除 tmpfs、snap 等）
df -h -t ext4 -t xfs -t btrfs

# 显示文件系统类型
df -hT

# 显示 inode 使用情况（小文件太多时 inode 会先耗尽）
df -i
```

### du — 查看目录/文件占用

```bash
# 查看某个目录占多少空间
du -sh /var/log/

# 递归显示每个子目录的大小
du -h /var/log/

# 只统计一层深度的子目录（很有用——找出哪个子目录最大）
du -sh */ .[!.]*/

# 按大小排序——找出当前目录下最大的 10 个东西
du -sh * .[!.]* 2>/dev/null | sort -hr | head -10

# 结合 find——查找大于 100MB 的文件
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null
```

| 选项 | 说明 |
|------|------|
| `-h` | 人类可读格式 |
| `-s` | 只显示总计，不列出子目录 |
| `-c` | 最后打印总计 |
| `-a` | 也显示文件大小，不光是目录 |
| `--max-depth=N` | 限制递归深度（`du -h --max-depth=1 /var`） |
| `-t 阈值` | 只显示大于阈值的（`du -t 100M /home`） |

## 行数/字数统计（wc）

```bash
wc [选项] <文件>

# 统计文件行数（最常用）
wc -l file.txt

# 统计单词数
wc -w file.txt

# 统计字符数
wc -c file.txt

# 统计字节数
wc -m file.txt

# 全统计（行 + 词 + 字符 + 文件名）
wc file.txt

# 统计当前目录下文件数量
ls | wc -l

# 统计代码行数（递归统计所有 .py 文件）
find . -name '*.py' -exec cat {} \; | wc -l

# 统计配置文件行数（排除空行和注释）
grep -v '^\s*#' nginx.conf | grep -v '^\s*$' | wc -l
```

## 命令别名（alias）

```bash
# 查看所有别名
alias

# 临时设置（关终端就没了）
alias ll='ls -lh'
alias la='ls -lha'
alias rm='rm -i'              # 给危险的命令加保护套

# 取消别名
unalias ll

# 永久设置——写入 ~/.bashrc 或 ~/.zshrc
echo "alias ll='ls -lh'" >> ~/.bashrc
echo "alias update='sudo apt update && sudo apt upgrade -y'" >> ~/.bashrc
source ~/.bashrc               # 立即生效

# 常用别名推荐
alias ll='ls -lh'
alias la='ls -lha'
alias cp='cp -i'               # 防止不小心覆盖文件
alias mv='mv -i'               # 防止不小心覆盖文件
alias ports='ss -tlnp'         # 快速看端口监听
alias myip='curl ifconfig.me'  # 查公网 IP
```

## 命令历史（history）

```bash
# 查看历史
history
history 20                     # 只看最近 20 条

# 执行历史命令
!42                            # 执行历史里第 42 条命令
!!                             # 重复上一条命令
!-2                            # 执行倒数第 2 条
!ssh                           # 执行最近一条以 ssh 开头的命令

# 搜索历史（比上下翻快得多）
Ctrl + R                       # 反向搜索——输几个字母就出来
Ctrl + R                       # 再按一次——跳到更早的匹配
Ctrl + G                       # 取消搜索

# 清空历史
history -c                     # 清空本次会话的历史缓存
> ~/.bash_history              # 清空持久化文件（谨慎）

# 不让某条命令进历史——在命令前加空格（需 HISTCONTROL=ignorespace）
 echo "这条不会进历史"

# 查看命令执行次数排行（看你什么命令用得最多）
history | awk '{print $2}' | sort | uniq -c | sort -rn | head -10
```

| 环境变量 | 说明 |
|---------|------|
| `HISTSIZE` | 内存中保存的历史条数（默认 1000） |
| `HISTFILESIZE` | 文件中保存的历史条数（默认 2000） |
| `HISTFILE` | 历史文件路径（默认 `~/.bash_history`） |
| `HISTCONTROL` | `ignoredups` 不存重复命令，`ignorespace` 空格开头的命令不记录 |
| `HISTTIMEFORMAT` | 给历史加时间戳：`export HISTTIMEFORMAT="%F %T "` |

## 文本排序与去重（sort / uniq）

```bash
# 按字母排序
sort file.txt
sort -r file.txt               # 倒序

# 按数字排序（重要：-n 不写的话 '10' 会排在 '2' 前面）
sort -n numbers.txt
sort -rn numbers.txt           # 数字倒序

# 按第几列排序（-k 列号）
sort -k2 file.txt              # 第 2 列
sort -t: -k3 -n /etc/passwd    # 以 : 为分隔符，按第 3 列数字排序（UID）

# 去重（只去相邻重复行，通常先 sort 再 uniq）
sort file.txt | uniq
sort file.txt | uniq -c        # 去重 + 统计出现次数
sort file.txt | uniq -d        # 只显示有重复的行
sort file.txt | uniq -u        # 只显示不重复的行

# 排序+去重一步到位
sort -u file.txt

# 统计访问最多的 IP（经典组合）
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10
```
