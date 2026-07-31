# PHP 类型比较绕过 — MD5 / Hash 比较漏洞

## 概述

PHP 的松散比较（`==`）与严格比较（`===`）在类型处理上的差异，导致特定输入可以使原本设计为安全校验的哈希比较逻辑完全失效。这个问题根植于 PHP 的类型转换机制（Type Juggling）本身，MD5 比较绕过只是这一底层缺陷最广为人知的载体；只要 `==` 参与了哈希比较，"0e" 绕过这一范式就普遍存在。

## 根本原因

核心在于 **PHP 的隐式类型转换**，而非哈希算法本身。

当执行 `$a == $b` 时，PHP 引擎在比较前按以下规则转换：

- 如果比较的是一个字符串和一个整数，字符串会被解析为数值
- 如果比较的是两个字符串，但 PHP 能将其同时解析为数值，则按数值比较

对于形如 `"0e12345"` 的字符串，PHP 在数值上下文中将其解析为科学计数法 `0 * 10^12345`，结果恒为整数 `0`。因此两个不同的 `0e...` 字符串用 `==` 比较时，会被转化为 `0 == 0`，计算结果为 `true`。

参考：PHP Manual — [Type Juggling](https://www.php.net/manual/en/language.types.type-juggling.php) 和 [Comparison Operators](https://www.php.net/manual/en/language.operators.comparison.php)。

## 触发条件

1. 开发者使用 `$hash1 == $hash2`（松散比较）而非 `$hash1 === $hash2`（严格比较）
2. 使用能被预测或控制的哈希值作为安全决策依据（密码验证、token 验证、签名校验等）
3. 哈希输入在用户可控范围内，或至少存在一个已知的 "0e" 原像

## 影响分析

- **认证绕过**：登录/验证逻辑中使用 `==` 比较哈希，攻击者可传入两个不同的 0e 字符串绕过
- **签名校验绕过**：JWT 或自定义签名机制若使用松散比较校验哈希，可被 0e 值欺骗
- **代码完整性校验**：文件完整性、数据完整性校验若依赖 `==`，链路上可被利用

## 深度扩展

### 1. 不止 MD5 — 所有哈希函数都受影响

"0e" 绕过不是 MD5 专属，任何产生恰好以 `0e` 后跟纯数字的哈希值的算法都能用于绕过：

| 算法 | 已知 0e 原像示例 |
|------|-----------------|
| MD5 | `QNKCDZO`, `s878926199a`, `s155964671a`, `s214587387a` |
| SHA-1 | `aaroZmOk` (输出 `0e66507019969427134894567494305185566735`) |
| SHA-256 | 已知存在但不易记忆的单向原像 |
| 自定义哈希 | 只要输出以 `0e` 后接全数字即可 |

这意味着单纯升级哈希算法（从 MD5 换到 SHA-256）并不能防御 `==` 绕过问题。

### 2. `===` 的数组绕过原理

PHP 中 `md5()` 的签名是 `md5(string $string): string`。当传入一个数组时，PHP 不会报语法错误，而是触发 Warning，然后返回 `null`。两个 `null` 用 `===` 比较自然为 `true`。

```php
// 传 a[]=1&b[]=2 可绕过以下校验
if (md5($_POST['a']) === md5($_POST['b'])) {
    // 通过
}
```

此场景的关键价值：

- **绕过 `===` 这一层防御**：当开发者认识到 `==` 不安全而改用 `===` 后，数组绕过仍是盲点
- **不限于 `md5()`**：接受 `string` 但在收到 `array` 时不抛出异常而返回 `null` 的函数都有此风险：
  - `sha1()` — 行为同 `md5()`
  - `hash()` — PHP 8 之前接受数组参数
  - `password_verify()` — PHP 7 部分版本存在行为差异

### 3. 实际利用的微妙场景

**场景 A：两边都可控**

```php
if (md5($_POST['a']) === md5($_POST['b'])) {
    // 直接传 a[]=1&b[]=2 即可绕过
}
```

**场景 B：一边固定为哈希值**

数组绕过在此失效（只有一边为 `null`，另一边是字符串）：

```php
if (md5($_POST['token']) === '0e12345') {
    // 此处无法用数组绕过，因为 null !== '0e12345'
    // 只能用已知的 0e 原像
}
```

**场景 C：JSON 反序列化**

PHP 中 `json_decode` 可构造出数组类型的值，配合 API 接口使用 JSON 传参时可绕过显式的表单校验：

```json
{"a": [], "b": []}
```

### 4. `== true` 的特殊情况

如果比较是 `$hash == true`（而非 `$hash == 0`），任何非空字符串都会为 `true`，此时 0e 绕过不成立。这点常被误解。

### 5. PHP 8.0+ 的变化

- PHP 8.0 之后新增的 `str_starts_with()`、`str_contains()` 等函数已不存在类型混淆问题
- 但 `==` 的隐式转换在 PHP 8 中**没有移除**，因此 `==` 比较哈希在 PHP 8 中仍然危险
- 在 `declare(strict_types=1);` 模式下，`md5()` 传入数组会产生 `TypeError` 而非返回 `null`

## 检测方法

- **代码层面**：搜索代码中 `md5`、`sha1`、`hash` 等函数调用后跟 `==` 或 `===` 比较的场景
- **黑盒层面**：向参数提交数组（`param[]=value`）观察服务器响应变化；提交已知 0e 原像观察认证是否绕过

## 防御方案

1. **根本性方案 — 使用 `===` 比较：**
   `0e12345 === 0` 为 `false`（字符串 vs 整数），但注意数组绕过仍有可能。

2. **根本性方案 — 使用专用哈希比较函数：**
   PHP 提供 `hash_equals()`（PHP 5.6+），它执行严格比较并实现**定时安全比较**（timing-safe comparison），防止通过响应时间推断哈希前缀的时序攻击：

   ```php
   if (hash_equals($expected_hash, $computed_hash)) { ... }
   ```

3. **缓解性方案 — 对哈希输入进行类型约束：**

   ```php
   if (!is_string($_POST['input'])) {
       throw new InvalidArgumentException('Expected string');
   }
   // 然后再计算 md5($_POST['input'])
   ```

4. **深层防御 — 启用严格类型：**
   在 PHP 8.0+ 中配合 `declare(strict_types=1);`，`md5()` 传入数组会产生 `TypeError`，从源头阻止类型混淆。

## 对比总结

| 比较方式 | 绕过条件 | Payload 示例 | 适用版本 |
|---------|---------|-------------|---------|
| `$a == $b` | 两端都是 `0e...` 的字符串 | `QNKCDZO` vs `s878926199a` | PHP 4+ |
| `$a == 0` | 任意 `0e...` 字符串 vs 整数 `0` | `QNKCDZO` vs `0` 为 `true` | PHP 4+ |
| `$a === $b` | 函数返回 `null` 的场景 | `a[]=1` & `b[]=2` | PHP 4-7.x |
| `$a === $b` (strict_types=1, PHP 8) | 严格类型下数组传递触发 `TypeError` | 无法以数组绕过 | PHP 8.0+ |
| `hash_equals($a, $b)` | 无已知绕过（类型+值+定时安全） | 不可绕过 | PHP 5.6+ |

## 补充：md5($str, true) — 原始二进制注入 SQL

### 概述

`md5($str, true)` 返回原始二进制（raw binary）而非十六进制字符串。该二进制输出中如果包含单引号、反斜杠、SQL 关键字等控制字符，拼接进 SQL 语句后可以改变原有查询逻辑，实现 SQL 注入。

### 典型 Payload

| Payload                                   | md5($str, true) 开头二进制 | 效果           |
| ----------------------------------------- | --------------------- | ------------ |
| `ffifdyop`                                | 包含 `'or'`             | 闭合引号插入 OR 逻辑 |
| `129581926211651571912466741651878684928` | 包含 `'or'`             | 同上           |
| `78684928`                                | 以 `'='` 开头            | 闭合引号插入等号比较   |
| `103634221`                               | 包含`'or'`              |              |

### 原理分析

`ffifdyop` 的 MD5 原始二进制开头恰好是 `'or'`，当该值被拼入 SQL 时：

```sql
-- 假设 SQL 为：
SELECT * FROM users WHERE password='$hash'

-- $hash = md5('ffifdyop', true) 的二进制输出为：
-- 二进制中包含 'or' 等控制字符，拼入后：
SELECT * FROM users WHERE password=''or'<后续字符>'
--                                 ^^ 闭合了前面的引号，插入 OR 逻辑
```

关键点：

- 核心不是开头固定为 `'or'`，而是二进制输出中**包含能注入 SQL 的控制字符**
- 可能出现的控制字符：单引号 `'`、反斜杠 `\`、`or`、`and`、`=`、注释符 `#` / `--`
- 只要拼接到 SQL 中能改变原有查询逻辑即可

### 暴力搜索此类 Payload

```php
<?php
// 搜索 md5($str, true) 中包含目标控制字符的输入
for ($i = 0; $i < PHP_INT_MAX; $i++) {
    $bin = md5((string)$i, true);
    if (strpos($bin, "'or'") !== false) {
        echo $i . " => " . addslashes($bin) . "\n";
        break;
    }
}
?>
```

可调整搜索条件查找不同模式，如 `'or'1`、`'='`、`')or` 等。

### 与类型比较绕过的区别

| 特性 | 类型比较绕过 | md5($str, true) SQL 注入 |
|------|-------------|------------------------|
| 利用点 | PHP 的 `==` / `===` 类型转换 | MD5 二进制输出中的 SQL 控制字符 |
| 目标 | 绕过身份验证/签名校验 | SQL 注入 |
| 涉及的函数 | `md5()` / `sha1()` / `hash()` (默认为十六进制输出) | `md5($str, true)` (第二个参数为 true) |
| 防御方案 | `hash_equals()` + 严格比较 + 类型约束 | **参数化查询**（Prepared Statement） |

### 防御方案

**根本性方案：永远使用参数化查询（Prepared Statement），绝不将 `md5($str, true)` 的输出拼入 SQL。**

即使原始二进制输出中不再包含 SQL 控制字符，依赖黑名单或转义来防护也是不可靠的：攻击者可以搜索到新的控制字符组合。

## 关联漏洞与概念

- **PHP 类型混淆（Type Juggling）**：同一底层问题的其他表现形式，如 `"abc" == 0` 为 `true`、`"123abc" == 123` 为 `true`
- **哈希长度扩展攻击（Hash Length Extension）**：另一类与哈希函数相关的攻击，针对 Merkle-Damgard 结构的哈希算法
- **时序攻击（Timing Attack）**：`hash_equals()` 专门防御的攻击类型，通过测量比较时间推断哈希前缀

## 参考资料

- PHP Manual: [Type Juggling](https://www.php.net/manual/en/language.types.type-juggling.php)
- PHP Manual: [Comparison Operators](https://www.php.net/manual/en/language.operators.comparison.php)
- PHP Manual: [hash_equals](https://www.php.net/manual/en/function.hash-equals.php)
- OWASP: [PHP Type Juggling](https://owasp.org/www-pdf-archive/PHPMagicTricks-TypeJuggling.pdf)
- WhiteHat Security: PHP Type Juggling Vulnerabilities
- GitHub - spaze/hashes: 已知 0e 字符串集合
