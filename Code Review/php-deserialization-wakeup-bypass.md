# PHP 反序列化 — __wakeup() 绕过获取 Flag

## 审计源码

**index.php:**

```php
<?php
include 'class.php';
$select = $_GET['select'];
$res=unserialize(@$select);
?>
```

**class.php:**

```php
<?php
include 'flag.php';


error_reporting(0);


class Name{
    private $username = 'nonono';
    private $password = 'yesyes';

    public function __construct($username,$password){    //创建对象时调用
        $this->username = $username;
        $this->password = $password;
    }

    function __wakeup(){  //执行 unserialize() 时调用，用于重建对象状态
        $this->username = 'guest';
    }

    function __destruct(){    //对象被销毁或所有引用被删除时调用
        if ($this->password != 100) {
            echo "</br>NO!!!hacker!!!</br>";
            echo "You name is: ";
            echo $this->username;echo "</br>";
            echo "You password is: ";
            echo $this->password;echo "</br>";
            die();
        }
        if ($this->username === 'admin') {
            global $flag;
            echo $flag;
        }else{
            echo "</br>hello my friend~~</br>sorry i can't give you the flag!";
            die();

            
        }
    }
}
?>
```

---

## 审计分析

### 结论

`index.php:4` 直接将用户输入传入 `unserialize()`，无任何清洗，存在 PHP 反序列化漏洞。`Name` 类内部用 `__wakeup()` 做安全防护（将 username 强制设为 `'guest'`），但可通过修改序列化字符串中的对象属性个数绕过（CVE-2016-7124），最终拿到 `$flag`。

### Source -> Sink 追踪

```
Source: $_GET['select'] (index.php:3, 用户完全可控)
  ↓
Sanitization: 无。@ 仅抑制错误，不做任何清洗
  ↓
Sink: unserialize(@$select) (index.php:4)
  ↓ 触发魔术方法
__wakeup() 被调用 -> 强制 $this->username = 'guest'（本意是安全防护）
__destruct() 被调用 -> 若绕过 wakeup，数据可控，输出 $flag
```

### 代码逐段拆解

**index.php — 入口，问题最严重的地方：**

`$_GET['select']` 直接取用户输入，然后用 `unserialize()` 反序列化。攻击者可以构造任意 `Name` 对象的序列化字符串，通过 GET 参数 `?select=...` 传入。`@` 错误抑制符不是安全措施——它只是不让报错显示出来，不阻止反序列化执行。

**class.php — 业务逻辑，有三层魔术方法：**

| 方法 | 触发时机 | 作用 |
|------|---------|------|
| `__construct` | `new Name()` | 设置 username 和 password，攻击者不经过这里 |
| `__wakeup` | `unserialize()` 时自动调用 | 把 username 强制改为 `'guest'`，试图阻止攻击 |
| `__destruct` | 对象销毁时自动调用 | 检查 password==100 且 username==='admin'，通过则输出 `$flag` |

开发者思路是：即使用户传入了 `username=admin, password=100` 的序列化串，`__wakeup()` 也会把它改回 `guest`，从而无法通过 `__destruct()` 的检查。

**但这个防护是可以绕过的。**

### 漏洞原理：__wakeup() 绕过 (CVE-2016-7124)

PHP 5.6.25 之前及 7.0.10 之前的版本中存在一个特性：如果序列化字符串中声明的对象属性个数**大于**实际包含的属性个数，`unserialize()` 会跳过 `__wakeup()` 的调用。

正常序列化一个 `Name` 对象（注意 private 属性在序列化时包含类名前缀和 null 字节）：

```
O:4:"Name":2:{s:14:"Nameusername";s:5:"admin";s:14:"Namepassword";i:100;}
                    ^
               属性个数 = 2，匹配实际属性数 -> __wakeup() 正常调用
```

攻击者把这个数字从 `2` 改成任意比它大的数（比如 `3` 或 `5`）：

```
O:4:"Name":3:{s:14:"Nameusername";s:5:"admin";s:14:"Namepassword";i:100;}
                    ^
               属性个数 = 3 > 实际 2 个 -> __wakeup() 被跳过！
```

效果：
- `unserialize()` 完成后，`$this->username = 'admin'`（wakeup 没执行，没被覆盖为 guest）
- `$this->password = 100`（整数，`!= 100` 为 false，通过第一关）
- `$this->username === 'admin'` 为 true（通过第二关）
- 输出 `$flag`

### 攻击链

1. 攻击者构造 payload：一个 `Name` 对象的序列化字符串，其中 `username='admin'`，`password=100`，对象属性个数被篡改为大于 2 的值（如 3）
2. 通过 URL 参数传入：`?select=O:4:"Name":3:{s:14:"%00Name%00username";s:5:"admin";s:14:"%00Name%00password";i:100;}`
   - 注意 private 属性名中的 null 字节 `\0` 在 URL 中需要编码为 `%00`
3. `index.php` 接收 `$_GET['select']`，原样传给 `unserialize()`
4. PHP 反序列化，因属性数量不匹配跳过 `__wakeup()`，username 保持为 `'admin'`
5. 脚本结束时触发 `__destruct()` -> password 检查通过 -> username 检查通过 -> `echo $flag`

### 修复方案

**根本修复 — 不要反序列化用户输入：**

```php
// index.php
$select = $_GET['select'];
// 不要 unserialize 用户输入。如果必须传复杂数据，用 json_decode
$res = json_decode($select, true);
```

**如果必须用 `unserialize()`（极少数情况），以下措施有帮助：**

1. **升级 PHP 版本** — PHP 5.6.25+ / 7.0.10+ 修复了 wakeup 绕过问题，但不要只靠版本——反序列化本身仍危险
2. **使用 `allowed_classes` 白名单**（PHP 7.0+）：
   ```php
   $res = unserialize($select, ['allowed_classes' => ['Name']]);
   ```
   这会阻止攻击者实例化任意 PHP 内置类（如 `SplFileObject`），但本题中 `Name` 类本身就在白名单里，问题仍在
3. **HMAC 签名校验** — 对序列化数据签名，防止篡改：
   ```php
   $data = $_GET['select'];
   $hash = $_GET['hash'];
   if (hash_hmac('sha256', $data, $secret) !== $hash) {
       die('Invalid data');
   }
   $res = unserialize($data);
   ```
   前提是密钥不泄露，且不把签名算法暴露给用户

**现实中最推荐的方案：用 JSON 替代序列化。** `json_decode()` 不会触发任何魔术方法，彻底消除了反序列化风险。

### 关联知识

- **CVE-2016-7124** — PHP `__wakeup()` 绕过，CVSS 7.5，影响 PHP 5 < 5.6.25、PHP 7 < 7.0.10
- **OWASP A8:2017 — Insecure Deserialization** / **OWASP A08:2021 — Software and Data Integrity Failures**
- 同类模式常出现在 CTF 比赛中，但真实世界也有类似案例——任何依赖魔术方法做"安全检查"的设计都是危险的，因为魔术方法的执行顺序和条件在不同 PHP 版本间可能变化
