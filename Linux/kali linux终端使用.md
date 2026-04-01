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
## 文本编辑快捷键
|快捷键|功能|
|---|---|
|`Ctrl + U`|删除光标前的所有内容|
|`Ctrl + K`|删除光标后的所有内容|
|`Ctrl + W`|删除前一个单词|
|`Ctrl + Y`|粘贴刚才删除的内容|
|`Ctrl + D`|删除当前字符|
|`Ctrl + H`|删除前一个字符|
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
## 移动文件夹压缩包或文件
```bash
mv [选项] <源压缩包.zip> <目标路径>
mv [选项] <源文件或目录> <目标路径>

	- `-i`：**交互模式**。如果目标文件已存在，会询问是否覆盖。**（推荐新手使用这个选项，避免误覆盖）**
	- `-v`：** verbose **模式。显示移动操作的详细信息。
	- `-f`：**强制模式**。直接覆盖已有文件，不进行任何提示。
	- `-n`：**不覆盖**已存在的文件。
	- `-u`：**更新**。只在源文件比目标文件新，或目标文件不存在时才移动。
	  
`mv` 命令同时也是**重命名**命令。
mv oldname.txt newname.txt
mv oldname.txt /home/kali/Documents/newname.txt
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
**基本解压**（解压到当前目录）：
unzip archive.zip
**解压到指定目录**（使用 `-d` 选项）：
unzip archive.zip -d /path/to/target/directory/
**列出压缩包内容**（不解压）：
unzip -l archive.zip
```
## 删除文件
**重要警告：Linux/Unix 命令行删除文件通常是不可逆的！没有“回收站”概念，一旦删除，很难恢复。请务必谨慎操作！**
```bash
**删除单个文件**
rm [选项] <文件或目录名>
**删除空目录**(它只能删除空文件夹，更安全)
rmdir empty_folder/

	- `-i`：**交互模式**。删除前逐一询问确认。**（强烈推荐新手和重要操作使用）**
	- `-v`：**显示详情**。告诉你删除了什么。
	- `-f`：**强制删除**。忽略不存在的文件，不做任何提示。**（非常危险！）**
	- `-r` 或 `-R`：**递归删除**。用于删除**目录及其内部所有内容**。**（与** **`-f`** **结合时威力极大，请慎用）**
```
## 创建文件/文件夹
```bash
创建文件
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


创建文件夹
mkdir new_folder
	-p：**递归创建**。一次性创建多级不存在的父目录，非常有用。
	-v：**显示详情**。告知你创建了哪些目录。
	-m：**设置权限**。在创建目录时直接指定权限模式。
```
## 查找文件
- **find**
```bash
find [起始目录] [查找条件] [执行操作]
1. **按名称查找**
# 在当前目录及子目录下精确查找名为 config.txt 的文件
find . -name "config.txt"
# 忽略文件名大小写
find /home -iname "readme.md"
# 使用通配符，查找所有 .log 结尾的文件
find /var/log -name "*.log"
2. **按类型查找**
# 查找普通文件（-f）、目录（-d）、符号链接（-l）
find /usr/bin -type l          # 查找符号链接
find /tmp -type f -name "*.tmp" # 查找普通文件且以 .tmp 结尾
3. **按大小查找**
# 查找大于 100MB 的文件 (+ 表示大于，- 表示小于)
find / -type f -size +100M
# 查找大小在 10KB 到 1MB 之间的文件
find . -size +10k -size -1M
4. **按时间查找**（非常实用）
# 查找最近 7 天内被修改过的文件（mtime 修改时间）
find /home -type f -mtime -7
# 查找 30 天前访问过的文件（atime 访问时间）
find /var/www -type f -atime +30
5. **按权限/用户/组查找**
# 查找权限为 777 的文件
find / -type f -perm 777
# 查找属于用户 alice 的文件
find /home -user alice
# 查找所属组为 dev 的文件
find /opt -group dev
```
-  **使用`locate`命令（基于索引，速度极快）**
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
- **使用`which`和`whereis`（查找命令/程序）**
这两个命令专门用于查找**可执行程序**及其相关文件。
1. **`which`****：** 查找一个命令的**完整路径**（在 `$PATH` 环境变量中）。
```bash
which python
# 输出：/usr/bin/python 或 /home/user/.pyenv/shims/python
```
2. **`whereis`****：** 查找一个命令的**二进制程序、源代码和手册页**的位置。
```bash
whereis ls
# 输出：ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz
```
- 例子
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
## Shell重定向符
输出重定向符号有“>”和“>>”，“>>”附加在重定向文件之后。而输入重定向符为“”。另外，还有错误重定向输出“2>”，可以把命令行出错的信息保存到指定的文件中去。