# PHP 弱类型比较 (`==`) — Type Juggling 绕过

## 审计源码

```php
<?php
include_once "flag.php";

if(isset($_GET['key'])) {
    $key = $_GET['key'];
    if(!is_numeric($key)) {
        exit("Just num!");
    }
    $key = intval($key);
    $str = "123ffwsfwefwf24r2f32ir23jrw923rskfjwtsw54w3";
    if($key == $str) {
        echo $flag;
    }
}
else {
    echo "Try to find out source file!";
}
?>
```

---

## 审计分析

### 漏洞概述

该代码意图通过两步校验保护 flag：先用 `is_numeric()` 限制输入必须为纯数字字符串，再用 `intval()` 转整数后与 `$str` 比较。但由于 PHP `==` 运算符的弱类型比较（type juggling）特性，传入 `key=123` 即可绕过。

### 根本原因

PHP 的 `==`（松散比较运算符）在比较不同数据类型时，会自动进行类型转换。**比较规则简表：**

| 表达式 | 比较方式 | 结果 |
|--------|----------|------|
| `int == string` | 字符串强制转 int | 按 int 比较 |
| `string == string` | 直接按字符串比较 | — |
| `0 == "abc"` | `"abc"` → (int)0 | `true` |

字符串转 int 的具体规则：

- 从字符串的**第一个字符**开始扫描
- 如果以数字开头 → 提取连续的十进制数字部分作为 int 值，遇到第一个非数字字符就截断
- 如果以非数字开头 → 直接返回 `0`

```
(int)"123ffwsfwefwf..."  →  123       // 取前导数字
(int)"abc"               →  0         // 字母开头 = 0
(int)"0x10"              →  0         // int 转换不认十六进制前缀
(int)"1.9e2"             →  1         // 小数点是非法字符，截断
(int)"  -5abc"           →  -5        // 跳过前导空格，识别负号
```

### Source → Sink 数据流

```
Source: $_GET['key']  → 用户传入 "123"
  ↓
is_numeric("123")      →  true   (纯数字字符串，通过)
  ↓
intval("123")          →  123    (转为 int)
  ↓
$str = "123ffwsfwefwf24r2f32ir23jrw923rskfjwtsw54w3"
  ↓
$key == $str           →  123 == (int)"123ffws..."  →  123 == 123 → true
  ↓
Sink: echo $flag;      →  flag 输出
```

### POC

```
GET /?key=123
```

附注：`is_numeric()` 还允许十六进制/八进制/科学计数法形式，如 `0x1e`、`0123`、`1e2` 也能通过检查。

### 攻击链

```
请求 ?key=123
  → is_numeric("123") 返回 true
  → intval("123") = 123
  → 123 == "123ffwsf..."  (PHP 自动将字符串转为 int: 123)
  → 条件成立 → 输出 flag
```

### 修复方案

```php
// 修复1 (推荐): 使用 === 严格比较运算符
if($key === $str) {
    echo $flag;
}

// 修复2: 先比较类型
if(is_int($key) && is_string($str) && $key == $str) {

}
```

改为 `===` 后，`123 === "123ffwsf..."` 会在类型检查阶段就失败（int ≠ string），直接返回 `false`，flag 不会被输出。

### 关联知识

- **PHP Type Juggling**（类型混淆）是 PHP 语言内置的行为，不是 bug，但在安全上下文中常成为漏洞
- **Magic Hashes**: `"0e12345" == "0e67890"` 均为 `true`，因为 PHP 将它们视为科学计数法的 0（`0 × 10^n`）。`"0e"` 开头的 MD5 哈希（如 `"0e215962017"`）可绕过 `$hash == md5($input)` 的验证
- **`in_array()` / `array_search()` 的第三参数**: 未传入 `true` 时为松散比较，`in_array("abc", [0])` 返回 `true`
- **`switch` 语句** 也使用松散比较
- 同类模式: CTF 常见考点 "[PHP 弱类型比较](https://www.php.net/manual/en/types.comparisons.php)"
- JSON 解析：`json_decode('{"key": 0})` 得到的 value 是 int 0，与字符串 `"abc"` 作 `==` 比较也返回 `true`
