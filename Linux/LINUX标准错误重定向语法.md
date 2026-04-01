`2>&1` 是 **Linux/Unix 系统中的标准错误重定向语法**。
## 分解说明
- **`2`** = 标准错误输出 (stderr) 的文件描述符
- **`>`** = 重定向符号
- **`&1`** = 表示"文件描述符 1"（标准输出）

所以 `2>&1` 的意思是：**将标准错误重定向到标准输出**
## 文件描述符说明
|文件描述符|名称|说明|
|---|---|---|
|**0**|stdin|标准输入|
|**1**|stdout|标准输出|
|**2**|stderr|标准错误输出|
## 实际示例

### 示例 1：正常命令输出

```bash
# 这个命令会产生标准输出和标准错误
ls /tmp /nonexistent
```

**输出：**

```text
/tmp:          # 这是标准输出（文件列表）
file1.txt
file2.txt

ls: cannot access '/nonexistent': No such file or directory  # **这是标准错误**
```

### 示例 2：使用 `2>&1`

```bash
# 将标准错误重定向到标准输出
ls /tmp /nonexistent > output.txt 2>&1
```

或者等价的写法：

```bash
ls /tmp /nonexistent &> output.txt
```

**结果：** 所有输出（包括正常输出和错误信息）都保存到 `output.txt`
### 重定向顺序的重要性
**顺序很重要！** `2>&1` 的位置会影响结果：
```bash
# 正确写法：先重定向标准输出，再重定向错误
$ command > output.txt 2>&1
# 解读：
# 1. 将标准输出重定向到 output.txt
# 2. 将标准错误重定向到标准输出（此时标准输出已指向 output.txt）
# 结果：两者都输出到 output.txt

# 错误写法：顺序颠倒
$ command 2>&1 > output.txt
# 解读：
# 1. 将标准错误重定向到标准输出（此时标准输出指向终端）
# 2. 将标准输出重定向到 output.txt
# 结果：标准输出到文件，标准错误仍到终端
```