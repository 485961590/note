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
