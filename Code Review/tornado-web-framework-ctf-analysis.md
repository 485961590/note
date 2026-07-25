# Tornado Web Framework — 原理与 CTF 实战分析

## 概述

Tornado 是一个 Python 异步 Web 框架，由 FriendFeed 开发，2009 年 Facebook 收购 FriendFeed 后开源。其核心特点是**原生异步非阻塞 I/O**，自带 HTTP 服务器，不需要 WSGI 容器（如 Gunicorn/uWSGI）即可独立运行。因采用事件循环（event loop）机制，单线程即可处理数千并发连接。

### 关键特性

- **原生异步** — 基于 `ioloop` 事件循环（早于 Python asyncio 出现），单线程非阻塞
- **自带 HTTP 服务器** — 不依赖 Apache/Nginx，本身即完整 HTTP Server
- **WebSocket 原生支持** — 异步架构使其 WebSocket 支持是内置的
- **非 WSGI 标准** — 独立生态，不兼容 WSGI，Flask/Django 中间件不能直接使用

### 基础代码结构

```python
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        result = await self.some_async_function()
        self.write(result)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```

Tornado 的应用程序由三部分构成：
- **Application** — 路由表 + 全局配置（settings），相当于 Flask 的 app 对象
- **RequestHandler** — 处理具体请求的类，每个 HTTP 方法对应一个类方法（`get()`/`post()` 等）
- **IOLoop** — 事件循环，驱动整个应用运行

---

## CTF 分析：fc17e303afc1b4d41ed79550

### 靶机架构

```
OpenResty (nginx + LuaJIT) 反向代理 + WAF
    ↓
Python Tornado 后端
    ↓
Jinja2 模板引擎
```

### 攻击链

```
1. 信息收集 → 发现 /error?msg= 端点存在 SSTI
2. SSTI 探测 → {{1}} 输出 "1"，{{handler}} 暴露 Tornado 对象
3. Secret 提取 → {{handler.settings}} 泄漏 cookie_secret
4. Hash 伪造 → md5(cookie_secret + md5(filename))
5. 文件读取 → /file?filename=/fllllllllllllag&filehash=<forged_hash> → 获取 flag
```

### 关键知识点拆解

#### 1. RequestHandler 对象 (`handler`)

Tornado 的每个请求由一个 `RequestHandler` 子类处理。在模板上下文中，Tornado 默认将当前请求的 `RequestHandler` 实例暴露为 `handler`。

```python
class ErrorHandler(tornado.web.RequestHandler):
    def get(self):
        msg = self.get_argument('msg')
        # self.render() 或 self.render_string() 将 handler 注入模板
        self.render('error.html', msg=msg)
```

CTF 中通过 `{{handler}}` 获取的是 `<main.ErrorHandler object>`，确认了正在操作 Tornado 框架。

#### 2. `handler.settings` — 配置泄露

Tornado Application 的构造函数接受一个 `settings` 字典，存储了所有应用配置。**Tornado 默认将这些配置暴露给所有模板**——这在 SSTI 场景下直接导致敏感信息泄露：

```python
app = tornado.web.Application([
    (r"/error", ErrorHandler),
], cookie_secret="15fdc1a1-61a3-4984-91c5-1ad31da88cc8", debug=True)
```

通过 `{{handler.settings}}` 获取到的内容：

```python
{
    'autoreload': True,                    # debug=True 时的副作用
    'compiled_template_cache': False,      # debug=True 时的副作用
    'cookie_secret': '15fdc1a1-61a3-4984-91c5-1ad31da88cc8'
}
```

这是该 CTF 的核心漏洞点——Tornado 的设计中，`settings` 是供模板使用的（如 `{{settings["cookie_secret"]}}`），但缺少对敏感配置的隔离机制。

#### 3. Tornado 的模板渲染机制

Tornado 自带模板引擎（`tornado.template`），但许多项目会替换为 Jinja2。本 CTF 使用 Jinja2。

关键区别在于**用户输入如何进入模板渲染**——有两种模式：

**模式一：用户输入作为模板变量（安全）**
```python
# error.html 中包含 {{msg}}
self.render('error.html', msg=user_input)
# → 用户输入中的 {{...}} 不会被解析为模板代码
```

**模式二：用户输入拼入模板字符串（危险 — SSTI）**
```python
template = "<html><body>" + user_input + "</body></html>"
self.render_string(template)
# → 用户输入中的 {{...}} 会被解析为模板代码
```

CTF 中显然使用的是模式二——或者类似 `self.write(user_input)` 直接输出用户输入但输出内容经过了模板引擎。这解释了为什么 `{{handler.settings}}` 能被解析并执行。

#### 4. 与其他框架 SSTI 利用链的对比

| 框架 | SSTI 常用访问链 | 获取内容 |
|------|-----------------|----------|
| Flask | `{{config}}` | Flask 配置（SECRET_KEY 等） |
| Tornado | `{{handler.settings}}` | Tornado 应用设置（cookie_secret 等） |
| Flask | `{{request}}` | 当前请求对象 |
| Tornado | `{{request}}` | `HTTPServerRequest` 对象（可访问参数、cookies、headers） |
| Tornado | `{{handler.request}}` | 与 `{{request}}` 等价 |

#### 5. Debug 模式的信息泄露

```python
app = tornado.web.Application(..., debug=True)
```

`debug=True` 会开启两个子选项：
- `autoreload=True` — 代码修改后自动重启，生产环境不应用
- `compiled_template_cache=False` — 模板每次都重新编译（不缓存）

在 CTF 中，settings-leak 文件显示这两项均在 `handler.settings` 中暴露给了攻击者。

#### 6. 文件访问的哈希验证机制

```python
# 服务端伪代码
def verify_file_hash(filename, filehash):
    inner = md5(filename)                    # md5("/fllllllllllllag")
    expected = md5(cookie_secret + inner)     # md5(secret + inner)
    return filehash == expected
```

漏洞点：
- `cookie_secret` 可通过 SSTI 从 `handler.settings` 获取
- `md5(secret + message)` 是经典的 hash length extension attack 可攻击的构造，但这里不需要——secret 已被直接泄露
- 修复方案：使用 HMAC 如 `hmac.new(key, msg, hashlib.sha256).hexdigest()`

---

## Tornado vs Flask vs Django — 安全视角对比

| 维度 | Tornado | Flask | Django |
|------|---------|-------|--------|
| 异步支持 | 原生异步 | WSGI 同步 / Quart 异步 | WSGI 同步 / ASGI |
| 自带服务器 | 有 (生产级) | 仅开发用 | 仅开发用 |
| 模板引擎 | 自带 / Jinja2 | Jinja2 | DjangoTemplates / Jinja2 |
| 模板上下文泄露 | `handler.settings` 含全部配置 | `config` 全局对象 | 默认配置不暴露敏感值 |
| 常见安全问题 | `handler.settings` 泄露 / 配置直接暴露 | SECRET_KEY 泄露 / debug toolbar | SQL 注入 / Mass Assignment |
| CSRF 防护 | 需自行实现 | Flask-WTF 扩展 | 内置 CSRF 中间件 |
| XSS 防护 | 默认自动转义（双花括号 `{{}}`） | 默认自动转义 | 默认自动转义 |
| 适用场景 | 实时/长连接/高并发 | 微服务/API | 全栈大型应用 |

## Tornado 常见安全陷阱

### 1. `handler.settings` 泄露敏感配置

**风险:** 任何可访问模板（尤其是 SSTI）的攻击者，都可以通过 `{{handler.settings}}` 获取所有应用配置。

**防御:** 不要将敏感值放在 Application settings 中。敏感值应在环境变量中读取，按需传入。

### 2. 用户输入直接拼入模板

**风险:** 将用户输入直接拼接到模板字符串后再渲染，造成 SSTI。

**防御:**
```python
# 安全：用户输入交给模板变量
self.render("page.html", msg=user_input)

# 危险：用户输入拼接为模板代码
self.render_string("Error: " + user_input)
```

### 3. `self.get_argument()` 无默认值

```python
# 不设默认值 → 参数缺失时抛出 400 错误，可能暴露框架信息
msg = self.get_argument('msg')

# 推荐：给默认值，或包装异常
msg = self.get_argument('msg', '')
```

### 4. Debug 模式用于生产

**风险:** `debug=True` 开启 autoreload 和不缓存模板，且暴露在 `handler.settings` 中。

**防御:** `debug=False` 用于生产，通过环境变量区分：

```python
app = tornado.web.Application([...], debug=os.environ.get('DEBUG', 'false').lower() == 'true')
```

## 参考资料

- Tornado 官方文档: https://www.tornadoweb.org/
- Tornado Application Settings: https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings
- Tornado RequestHandler: https://www.tornadoweb.org/en/stable/web.html#request-handlers
- SSTI in Flask/Jinja2 与 Tornado/Jinja2 在利用链上的差异主要在暴露的对象不同
- OWASP SSTI: https://owasp.org/www-community/attacks/Server_Side_Template_Injection
