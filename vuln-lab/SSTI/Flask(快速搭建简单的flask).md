快速搭建一个简单的 Web 页面。

## 一、Flask 框架介绍

### 什么是 Flask？

Flask 是一个用 Python 编写的轻量级 Web 应用框架。它被称为 "微框架"，因为核心简单但可扩展性强。

### Flask 的特点：

- **轻量级**：核心功能简洁，没有默认的数据库、表单验证等
    
- **灵活**：可以根据需要添加扩展
    
- **易于学习**：代码直观，上手快
    
- **开发快速**：几行代码就能启动一个Web服务
## 二、快速搭建 Flask Web 页面

### 步骤1：安装 Flask
```
pip install flask
```
### 步骤2：创建基础应用

创建一个名为 `app.py` 的文件：
```python
from flask import Flask, render_template

# 创建 Flask 应用实例
app = Flask(__name__)

# 定义路由和视图函数
@app.route('/')
def home():
    return "欢迎来到我的网站！"

@app.route('/hello')
def hello():
    return "<h1 style='color:blue'>Hello, World!</h1>"

@app.route('/user/<name>')
def user(name):
    return f"<h2>你好，{name}！</h2>"

# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```
### 步骤3：运行应用
```
python app.py
```
访问 `http://localhost:5000` 查看效果。

## 三、使用 HTML 模板的完整示例

### 1. 创建项目结构
```text
my_flask_app/
│── app.py
│── templates/
│   ├── index.html
│   ├── about.html
│   └── base.html
└── static/
    ├── style.css
    └── script.js
```
### 2. 创建主应用文件 `app.py`
```python
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 模拟一些数据
users = ['张三', '李四', '王五']

@app.route('/')
def index():
    return render_template('index.html', title='首页', users=users)

@app.route('/about')
def about():
    return render_template('about.html', title='关于我们')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    if username and username not in users:
        users.append(username)
    return redirect(url_for('index'))

@app.route('/delete_user/<name>')
def delete_user(name):
    if name in users:
        users.remove(name)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```
### 3. 创建基础模板 `templates/base.html`
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - 我的Flask应用</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav>
        <a href="{{ url_for('index') }}">首页</a>
        <a href="{{ url_for('about') }}">关于</a>
    </nav>
    
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    
    <footer>
        <p>&copy; 2024 我的Flask应用</p>
    </footer>
</body>
</html>
```
### 4. 创建首页模板 `templates/index.html`
```html
{% extends "base.html" %}

{% block content %}
<h1>用户管理系统</h1>

<!-- 添加用户表单 -->
<form action="{{ url_for('add_user') }}" method="POST">
    <input type="text" name="username" placeholder="输入用户名" required>
    <button type="submit">添加用户</button>
</form>

<!-- 用户列表 -->
<h2>用户列表</h2>
<ul>
    {% for user in users %}
    <li>
        {{ user }}
        <a href="{{ url_for('delete_user', name=user) }}" class="delete-btn">删除</a>
    </li>
    {% endfor %}
</ul>
{% endblock %}
```
### 5. 创建关于页面 `templates/about.html`
```html
{% extends "base.html" %}

{% block content %}
<h1>关于我们</h1>
<p>这是一个使用 Flask 框架构建的简单 Web 应用。</p>
<p>功能包括：</p>
<ul>
    <li>用户列表展示</li>
    <li>添加新用户</li>
    <li>删除用户</li>
</ul>
{% endblock %}
```
### 6. 创建样式文件 `static/style.css`
```html
body {
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

nav {
    background-color: #333;
    padding: 10px;
    margin-bottom: 20px;
}

nav a {
    color: white;
    text-decoration: none;
    margin-right: 20px;
}

nav a:hover {
    text-decoration: underline;
}

.container {
    min-height: 400px;
}

form {
    margin: 20px 0;
}

input[type="text"] {
    padding: 8px;
    width: 200px;
}

button {
    padding: 8px 16px;
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
}

button:hover {
    background-color: #45a049;
}

ul {
    list-style-type: none;
    padding: 0;
}

li {
    background-color: #f9f9f9;
    margin: 5px 0;
    padding: 10px;
    border-left: 4px solid #4CAF50;
}

.delete-btn {
    color: red;
    text-decoration: none;
    margin-left: 10px;
}

footer {
    margin-top: 40px;
    text-align: center;
    color: #666;
}
```
## 四、运行和测试

1. **启动应用**：
	`python app.py`
	
2. **访问应用**：
    
    - 首页：`http://localhost:5000`
        
    - 关于页面：`http://localhost:5000/about`
        
3. **功能测试**：
    
    - 在首页输入用户名并点击"添加用户"
        
    - 点击用户旁边的"删除"链接删除用户
## 五、Flask 核心概念总结

- **路由**：使用 `@app.route()` 装饰器定义URL路径
    
- **视图函数**：处理请求并返回响应的函数
    
- **模板**：使用 Jinja2 模板引擎渲染HTML
    
- **静态文件**：CSS、JavaScript、图片等资源
    
- **请求处理**：通过 `request` 对象获取表单数据
    
- **重定向**：使用 `redirect()` 和 `url_for()`