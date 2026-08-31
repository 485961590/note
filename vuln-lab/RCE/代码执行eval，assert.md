## 1. **直接代码执行函数**
### eval()
```php
<?php
// 执行字符串作为PHP代码
eval('echo "Hello World";');
eval('$a = 1 + 1; echo $a;');

// 安全风险示例
$code = $_GET['code'];  // 用户输入
eval($code);  // 高危！可执行任意代码
?>
```
### assert()
```php
<?php
// 主要用于调试断言，但也可执行代码
assert('2 > 1');  // 正常使用
assert('system("whoami")');  // 可执行系统命令

// PHP 7.1+ 中assert变成语言结构，但仍可执行代码
assert($_POST['cmd']);
?>
```