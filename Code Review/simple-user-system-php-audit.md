# Simple User System — PHP 安全审计报告

## 审计源码

### config.php
```php
<?php
    $config['hostname'] = '127.0.0.1';
    $config['username'] = 'root';
    $config['password'] = '';
    $config['database'] = '';
    $flag = '';
?>
```

### class.php
```php
<?php
require('config.php');

class user extends mysql{
    private $table = 'users';

    public function is_exists($username) {
        $username = parent::filter($username);
        $where = "username = '$username'";
        return parent::select($this->table, $where);
    }
    public function register($username, $password) {
        $username = parent::filter($username);
        $password = parent::filter($password);
        $key_list = Array('username', 'password');
        $value_list = Array($username, md5($password));
        return parent::insert($this->table, $key_list, $value_list);
    }
    public function login($username, $password) {
        $username = parent::filter($username);
        $password = parent::filter($password);
        $where = "username = '$username'";
        $object = parent::select($this->table, $where);
        if ($object && $object->password === md5($password)) {
            return true;
        } else {
            return false;
        }
    }
    public function show_profile($username) {
        $username = parent::filter($username);
        $where = "username = '$username'";
        $object = parent::select($this->table, $where);
        return $object->profile;
    }
    public function update_profile($username, $new_profile) {
        $username = parent::filter($username);
        $new_profile = parent::filter($new_profile);
        $where = "username = '$username'";
        return parent::update($this->table, 'profile', $new_profile, $where);
    }
    public function __tostring() {
        return __class__;
    }
}

class mysql {
    private $link = null;

    public function connect($config) {
        $this->link = mysql_connect(
            $config['hostname'],
            $config['username'],
            $config['password']
        );
        mysql_select_db($config['database']);
        mysql_query("SET sql_mode='strict_all_tables'");
        return $this->link;
    }

    public function select($table, $where, $ret = '*') {
        $sql = "SELECT $ret FROM $table WHERE $where";
        $result = mysql_query($sql, $this->link);
        return mysql_fetch_object($result);
    }

    public function insert($table, $key_list, $value_list) {
        $key = implode(',', $key_list);
        $value = '\'' . implode('\',\'', $value_list) . '\'';
        $sql = "INSERT INTO $table ($key) VALUES ($value)";
        return mysql_query($sql);
    }

    public function update($table, $key, $value, $where) {
        $sql = "UPDATE $table SET $key = '$value' WHERE $where";
        return mysql_query($sql);
    }

    public function filter($string) {
        $escape = array('\'', '\\\\');
        $escape = '/' . implode('|', $escape) . '/';
        $string = preg_replace($escape, '_', $string);

        $safe = array('select', 'insert', 'update', 'delete', 'where');
        $safe = '/' . implode('|', $safe) . '/i';
        return preg_replace($safe, 'hacker', $string);
    }
    public function __tostring() {
        return __class__;
    }
}
session_start();
$user = new user();
$user->connect($config);
```

### index.php
```php
<?php
    require_once('class.php');
    if($_SESSION['username']) {
        header('Location: profile.php');
        exit;
    }
    if($_POST['username'] && $_POST['password']) {
        $username = $_POST['username'];
        $password = $_POST['password'];

        if(strlen($username) < 3 or strlen($username) > 16)
            die('Invalid user name');

        if(strlen($password) < 3 or strlen($password) > 16)
            die('Invalid password');

        if($user->login($username, $password)) {
            $_SESSION['username'] = $username;
            header('Location: profile.php');
            exit;
        }
        else {
            die('Invalid user name or password');
        }
    }
    else {
?>
<!DOCTYPE html>
<html>
<head>
   <title>Login</title>
   <link href="static/bootstrap.min.css" rel="stylesheet">
   <script src="static/jquery.min.js"></script>
   <script src="static/bootstrap.min.js"></script>
</head>
<body>
    <div class="container" style="margin-top:100px">
        <form action="index.php" method="post" class="well" style="width:220px;margin:0px auto;">
            <img src="static/piapiapia.gif" class="img-memeda " style="width:180px;margin:0px auto;">
            <h3>Login</h3>
            <label>Username:</label>
            <input type="text" name="username" style="height:30px"class="span3"/>
            <label>Password:</label>
            <input type="password" name="password" style="height:30px" class="span3">

            <button type="submit" class="btn btn-primary">LOGIN</button>
        </form>
    </div>
</body>
</html>
<?php
    }
?>
```

### register.php
```php
<?php
    require_once('class.php');
    if($_POST['username'] && $_POST['password']) {
        $username = $_POST['username'];
        $password = $_POST['password'];

        if(strlen($username) < 3 or strlen($username) > 16)
            die('Invalid user name');

        if(strlen($password) < 3 or strlen($password) > 16)
            die('Invalid password');
        if(!$user->is_exists($username)) {
            $user->register($username, $password);
            echo 'Register OK!<a href="index.php">Please Login</a>';
        }
        else {
            die('User name Already Exists');
        }
    }
    else {
?>
<!DOCTYPE html>
<html>
<head>
   <title>Login</title>
   <link href="static/bootstrap.min.css" rel="stylesheet">
   <script src="static/jquery.min.js"></script>
   <script src="static/bootstrap.min.js"></script>
</head>
<body>
    <div class="container" style="margin-top:100px">
        <form action="register.php" method="post" class="well" style="width:220px;margin:0px auto;">
            <img src="static/piapiapia.gif" class="img-memeda " style="width:180px;margin:0px auto;">
            <h3>Register</h3>
            <label>Username:</label>
            <input type="text" name="username" style="height:30px"class="span3"/>
            <label>Password:</label>
            <input type="password" name="password" style="height:30px" class="span3">

            <button type="submit" class="btn btn-primary">REGISTER</button>
        </form>
    </div>
</body>
</html>
<?php
    }
?>
```

### profile.php
```php
<?php
    require_once('class.php');
    if($_SESSION['username'] == null) {
        die('Login First');
    }
    $username = $_SESSION['username'];
    $profile=$user->show_profile($username);
    if($profile  == null) {
        header('Location: update.php');
    }
    else {
        $profile = unserialize($profile);
        $phone = $profile['phone'];
        $email = $profile['email'];
        $nickname = $profile['nickname'];
        $photo = base64_encode(file_get_contents($profile['photo']));
?>
<!DOCTYPE html>
<html>
<head>
   <title>Profile</title>
   <link href="static/bootstrap.min.css" rel="stylesheet">
   <script src="static/jquery.min.js"></script>
   <script src="static/bootstrap.min.js"></script>
</head>
<body>
    <div class="container" style="margin-top:100px">
        <img src="data:image/gif;base64,<?php echo $photo; ?>" class="img-memeda " style="width:180px;margin:0px auto;">
        <h3>Hi <?php echo $nickname;?></h3>
        <label>Phone: <?php echo $phone;?></label>
        <label>Email: <?php echo $email;?></label>
    </div>
</body>
</html>
<?php
    }
?>
```

### update.php
```php
<?php
    require_once('class.php');
    if($_SESSION['username'] == null) {
        die('Login First');
    }
    if($_POST['phone'] && $_POST['email'] && $_POST['nickname'] && $_FILES['photo']) {

        $username = $_SESSION['username'];
        if(!preg_match('/^\d{11}$/', $_POST['phone']))
            die('Invalid phone');

        if(!preg_match('/^[_a-zA-Z0-9]{1,10}@[_a-zA-Z0-9]{1,10}\.[_a-zA-Z0-9]{1,10}$/', $_POST['email']))
            die('Invalid email');

        if(preg_match('/[^a-zA-Z0-9_]/', $_POST['nickname']) || strlen($_POST['nickname']) > 10)
            die('Invalid nickname');

        $file = $_FILES['photo'];
        if($file['size'] < 5 or $file['size'] > 1000000)
            die('Photo size error');

        move_uploaded_file($file['tmp_name'], 'upload/' . md5($file['name']));
        $profile['phone'] = $_POST['phone'];
        $profile['email'] = $_POST['email'];
        $profile['nickname'] = $_POST['nickname'];
        $profile['photo'] = 'upload/' . md5($file['name']);

        $user->update_profile($username, serialize($profile));
        echo 'Update Profile Success!<a href="profile.php">Your Profile</a>';
    }
    else {
?>
<!DOCTYPE html>
<html>
<head>
   <title>UPDATE</title>
   <link href="static/bootstrap.min.css" rel="stylesheet">
   <script src="static/jquery.min.js"></script>
   <script src="static/bootstrap.min.js"></script>
</head>
<body>
    <div class="container" style="margin-top:100px">
        <form action="update.php" method="post" enctype="multipart/form-data" class="well" style="width:220px;margin:0px auto;">
            <img src="static/piapiapia.gif" class="img-memeda " style="width:180px;margin:0px auto;">
            <h3>Please Update Your Profile</h3>
            <label>Phone:</label>
            <input type="text" name="phone" style="height:30px"class="span3"/>
            <label>Email:</label>
            <input type="text" name="email" style="height:30px"class="span3"/>
            <label>Nickname:</label>
            <input type="text" name="nickname" style="height:30px" class="span3">
            <label for="file">Photo:</label>
            <input type="file" name="photo" style="height:30px"class="span3"/>
            <button type="submit" class="btn btn-primary">UPDATE</button>
        </form>
    </div>
</body>
</html>
<?php
    }
?>
```

---

## 审计分析

### 漏洞 (高危) — 反序列化数组绕过 + file_get_contents 任意文件读取链

**文件:** `profile.php:235,239`

#### 结论

`unserialize()` 从数据库读取 profile 数据后反序列化为数组，然后直接从数组中取出 `photo` 路径传给 `file_get_contents()` 读取文件并 base64 回显。

这构成了一个 **反序列化数组绕过 (array bypass) + 任意文件读取** 的攻击链。攻击目标是修改 `$profile['photo']` 的值来读取任意文件，而不是触发对象注入的魔术方法。

#### Source → Sink 追踪

```
Source: $_POST (phone, email, nickname) + $_FILES['photo']['name']
  ↓
校验: phone=严格数字 / email=限制字符集 / nickname=仅[a-zA-Z0-9_]
  ↓
$profile 数组构建: (4 个键, 硬编码顺序)
  ['phone'] = $_POST['phone']
  ['email'] = $_POST['email']
  ['nickname'] = $_POST['nickname']
  ['photo'] = 'upload/' . md5($file['name'])
  ↓
serialize($profile) → 产生标准序列化数组字符串
  ↓
filter() 处理 (替换关键字和引号) → 可能破坏长度一致性
  ↓
SQL UPDATE 存入数据库 profile 字段
  ↓
SQL SELECT 读取 → $profile 字符串
  ↓
Sink 1: unserialize($profile) → 反序列化为 PHP 数组
  ↓
$profile['photo'] 作为路径
  ↓
Sink 2: file_get_contents($profile['photo']) → 读取文件内容
  ↓
base64_encode → echo 到 HTML 响应体 (内容回显)
```

#### 攻击原理：PHP 反序列化数组绕过 (Array Bypass)

PHP 反序列化数组时，key-value 对是**顺序读取**的。当同一个 key 在序列化字符串中出现多次时，**后面的值覆盖前面的值**。

```
a:2:{s:5:"photo";s:4:"safe";s:5:"photo";s:11:"/etc/passwd";}
                                   ↑                       ↑
                              第二个 photo key      覆盖第一个值
```

这是"反序列化数组绕过"的核心 —— 攻击者不需要注入对象、不需要 gadget chain，只需要让序列化数据中出现第二个 `photo` key，其值就能覆盖原本安全的 `upload/<md5>` 路径。

#### 当前的可利用性分析

**直接注入路径：当前被输入校验阻断**

```
phone:  仅 \d{11}           → 不含 " ; { }
email:  [_a-zA-Z0-9@.]     → 不含 " ; { }
nick:   [a-zA-Z0-9_]       → 不含 " ; { }
photo:  upload/<hex>        → 不含 " ; { }
```

这四个字段的字符集都不包含序列化元字符 (`"`, `;`, `{`, `}`)，无法直接注入 `s:5:"photo";s:11:"/etc/passwd"` 这样的片段。

**filter() 关键字替换：不同关键字的不同影响**

`filter()` 对序列化字符串全局替换的关键字中，有两种行为：

| 关键字 | 长度 | 替换为 | 长度变化 | 对序列化的影响 |
|--------|------|--------|---------|---------------|
| `select` / `insert` / `update` / `delete` | 6 | `hacker` | 6 → 6 不变 | **无影响**，序列化结构保持完整 |
| `where` | 5 | `hacker` | 5 → 6 **+1** | **破坏序列化**，长度前缀与实际内容不匹配 |

对于 `where`（5→6）：如果 email 或 nickname 中包含 `where`，序列化字符串中对应的长度前缀会小 1。

```
例: email 设为 where@c.cc (10字符)
序列化: s:10:"where@c.cc";
filter: → s:10:"hacker@c.cc";   (内容变11字符，前缀仍是10)

反序列化读取: s:10: → 读10字符: "hacker@c.c"
              期待 "  → 实际遇到: 第11个字符 "c"
              解析失败 → 返回 false
```

`where` 的替换直接导致 `unserialize()` 返回 `false`（单字段时）。
对于 `select` / `insert` / `update` / `delete`（6→6）：长度不变，序列化结构完整。

**但结合数组绕过和字符串逃逸技巧，此漏洞可被利用（PHP < 8.0）：**

```
nickname[] 传入数组:
  → preg_match() 在 PHP < 8.0 返回 false（8.0+ 抛 TypeError）
  → 校验被绕过，nickname 以数组形式进入序列化
  → 序列化中出现嵌套数组结构 a:1:{...}
  → 大量 where 在 filter() 中替换为 hacker（每处 +1 字节）
  → 膨胀的字节"吃掉"原生 photo 序列化片段
  → 注入的新 photo key-value 覆盖原路径
  → file_get_contents(恶意路径) 读取任意文件

依赖条件: PHP < 8.0
```

#### 真正的攻击面：二阶污染 (Second-Order Injection)

当前代码中通过 `update.php` 正常更新 profile 无法实现数组绕过。但攻击链的危险在于：

```
数据库 profile 字段被污染
(通过: nickname[] 数组绕过 + 字符串逃逸 /
       未来可能的 SQL 注入 / 直接数据库写入 / 管理后台 / 缓存污染)
                   ↓
          unserialize(恶意数据)
                   ↓
          $profile['photo'] = 攻击者控制的路径
                   ↓
          file_get_contents(攻击者控制的路径)
                   ↓
          base64 编码 → 回显到 HTML
```

只要数据库中的序列化数据包含：

```
s:5:"photo";s:11:"/etc/passwd";
```

作为第二个 photo key-value 对，它就会覆盖前面正常的 `upload/<md5>` 值。

#### 修复方案

**根本性修复：不要序列化。** 将 profile 各字段独立存储在数据库列中。若必须存储聚合数据，用 `json_encode()` 替代。

**针对此利用路径的具体修复：**

```php
// 检查输入类型，杜绝数组绕过 (PHP < 8.0 绕过的关键入口)
if(is_array($_POST['nickname'])) die('Invalid nickname');
if(preg_match('/[^a-zA-Z0-9_]/', $_POST['nickname']) || strlen($_POST['nickname']) > 10)
    die('Invalid nickname');
```

**版本兼容：** PHP 8.0+ 的 TypeError 阻断了数组绕过，但不能将此视为安全修复——升级可缓解但不应依赖。核心修正是消除序列化或使用 JSON。

#### 关联知识

- CWE-502: Deserialization of Untrusted Data
- CWE-73: External Control of File Name or Path
- **PHP 反序列化数组绕过 (Array Bypass)**：`a:N:{...}` 中重复 key 后值覆盖前值，可用于篡改数组中的特定字段。与对象注入不同，不依赖魔术方法，是纯数据层面的攻击。
- Phar 反序列化：`file_get_contents('phar://...')` 在 PHP 5.x-7.x 中触发元数据反序列化。
- 同类漏洞模式：CVE-2019-16759 (vBulletin widget 反序列化 RCE)、CVE-2020-1938 (Tomcat AJP 文件包含)
