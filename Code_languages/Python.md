# Python

> 语法最接近伪代码的脚本语言。信息安全领域的事实标准——大多数渗透测试工具和 PoC 都用 Python 写。

---

## 一眼认出这是 Python

```python
# 注释用 # 号
# 用缩进（4 空格）代替花括号——这是 Python 最明显的特征

def greet(name):           # def 定义函数，冒号开头
    if name:               # if/for/while 都不需要括号
        print(f"Hello, {name}")   # f-string 是 Python 3.6+ 的特性
    else:
        print("Hello, World")

# 变量不需要声明类型
name = "Alice"        # 字符串
age = 25              # 整数
pi = 3.14             # 浮点
is_active = True      # 布尔（注意大写 True/False）
nothing = None        # 空值（不是 null）

# 列表和字典
skills = ["Python", "Docker", "SQL"]          # 列表（类似数组）
user = {"name": "Alice", "age": 25}           # 字典（类似 JSON 对象）

# 列表推导式——Python 的特色语法
squares = [x**2 for x in range(10)]
```

---

## 常用场景

| 场景 | 典型框架/库 |
|------|------------|
| Web 后端 | Django, Flask, FastAPI |
| 渗透测试 | Requests, Scapy, Impacket, Pwntools |
| 数据处理 | Pandas, NumPy |
| 自动化脚本 | os, subprocess, shutil |
| AI/ML | PyTorch, TensorFlow, LangChain |

---

## 关键概念

### 虚拟环境

Python 项目之间依赖隔离靠虚拟环境，没有它全局 pip install 会乱套：

```bash
python3 -m venv myenv          # 创建虚拟环境
source myenv/bin/activate      # 激活（Linux/Mac）
myenv\Scripts\activate         # 激活（Windows）
deactivate                     # 退出
```

### pip 包管理

```bash
pip install requests           # 安装
pip install -r requirements.txt # 从依赖文件安装
pip freeze > requirements.txt  # 导出当前环境所有包
```

### `if __name__ == "__main__"`

Python 脚本可以直接运行，也可以被 import 为模块。这个惯用写法区分两种场景：

```python
def main():
    print("正在运行")

if __name__ == "__main__":    # 只有直接执行时才运行
    main()
```

---

## Python 2 vs Python 3

Python 2 已于 2020 年停止维护，但一些老旧工具仍依赖它：

| | Python 2 | Python 3 |
|---|---------|---------|
| print | `print "hello"` | `print("hello")` |
| 整数除法 | `5/2 = 2`（向下取整） | `5/2 = 2.5` |
| 字符串 | 默认 bytes | 默认 Unicode |
| 状态 | 已停维（EOL 2020） | 当前版本 |

---

## 安全相关

**反序列化是 Python 最大的安全风险之一：**

```python
# 危险：pickle 可以执行任意代码
import pickle
data = pickle.loads(user_input)          # 绝对不要反序列化不受信任的数据

# 危险：PyYAML 的 load() 同样可以代码执行
import yaml
data = yaml.load(user_input)             # 用 safe_load() 代替

# 危险：eval/exec
eval("os.system('rm -rf /')")            # eval 执行表达式
exec("import os; os.system('whoami')")   # exec 执行语句块
```

| 危险函数 | 风险 | 替代 |
|----------|------|------|
| `pickle.loads()` | 任意代码执行 | 不用 pickle 处理用户输入 |
| `yaml.load()` | 任意代码执行（`!!python/object`） | `yaml.safe_load()` |
| `eval()` | 表达式执行 | `ast.literal_eval()` |
| `exec()` | 语句块执行 | 避免使用 |
| `os.system()` | 命令执行 | `subprocess.run()` + `shell=False` |

---

## 简单总结

- **缩进即语法**：不用花括号，缩进错了代码逻辑就错
- **动态类型**：变量不用声明类型，运行时才确定
- **万物皆对象**：函数、类、模块都是对象，可以传来传去
- **pip 安装工具链**：`pip install 工具名` 是拿到安全工具后最常见的操作
- **`.py` 文件**：Python 脚本的后缀名
