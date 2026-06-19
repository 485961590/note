# Web 全栈项目：从零到 Docker 部署

> 目标：写一个完整的 Web 应用，用 Docker 部署，在局域网任意设备上通过浏览器访问。全程从空文件夹开始，一步一步走到能用的产品。

---

## 项目选型：HTTP 安全头检查工具

**输入一个网址，检查它的 HTTP 安全响应头是否配置到位。**

为什么选这个：
- 和信息安全专业直接相关——CSP、HSTS、X-Frame-Options 都是渗透测试和加固绕不开的知识
- 逻辑简单：后端负责发 HTTP 请求取响应头，前端负责展示结果
- 能跑通前后端完整流程，又不会陷入业务逻辑的复杂度中
- 只有一个页面、一个 API 接口，半天可以做完

---

## 技术选型

| 层 | 技术 | 理由 |
|---|---|---|
| 后端 | Python Flask | 轻量、学习成本低、信安工具常用 |
| 前端 | 原生 HTML + CSS + JS | 不引入框架，理解 Web 基础 |
| 服务器 | Gunicorn | 生产级 WSGI 服务器 |
| 容器化 | Docker | 一键部署，环境隔离 |
| 基础镜像 | `python:3.11-slim` | 体积小，够用 |

---

## 第 1 步：项目结构

```
security-header-checker/
├── app.py                # Flask 后端
├── templates/
│   └── index.html        # 前端页面（内嵌 CSS + JS）
├── requirements.txt      # Python 依赖
├── Dockerfile            # 镜像构建
└── docker-compose.yml    # 一键启动（可选）
```

初始操作：

```bash
mkdir security-header-checker
cd security-header-checker
mkdir templates
```

---

## 第 2 步：后端（Flask）

创建 `app.py`：

```python
from flask import Flask, render_template, request, jsonify, make_response, redirect
import requests
import time
import base64
import hmac
from http import HTTPStatus

app = Flask(__name__)

# 要检查的安全头列表：{名称: {描述, 推荐值示例}}
SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "name": "HTTP 严格传输安全 (HSTS)",
        "desc": "强制浏览器只用 HTTPS 访问，防止 SSL 剥离攻击",
        "example": "max-age=31536000; includeSubDomains",
    },
    "Content-Security-Policy": {
        "name": "内容安全策略 (CSP)",
        "desc": "限制浏览器可以加载哪些资源，防御 XSS 和数据注入",
        "example": "default-src 'self'",
    },
    "X-Frame-Options": {
        "name": "X-Frame-Options",
        "desc": "防止页面被嵌入到 iframe 中，防御点击劫持",
        "example": "DENY 或 SAMEORIGIN",
    },
    "X-Content-Type-Options": {
        "name": "X-Content-Type-Options",
        "desc": "阻止浏览器 MIME 类型嗅探，防止类型混淆攻击",
        "example": "nosniff",
    },
    "Referrer-Policy": {
        "name": "Referrer-Policy",
        "desc": "控制 Referer 请求头中发送多少来源信息",
        "example": "strict-origin-when-cross-origin",
    },
    "Permissions-Policy": {
        "name": "Permissions-Policy",
        "desc": "控制浏览器 API（摄像头、麦克风等）的使用权限",
        "example": "camera=(), microphone=()",
    },
    "X-XSS-Protection": {
        "name": "X-XSS-Protection",
        "desc": "启用浏览器内置的 XSS 过滤器（旧版浏览器，已被 CSP 取代）",
        "example": "1; mode=block",
    },
}


# ============================================================
# curl 测试端点配置
# ============================================================

# Basic Auth 凭据
BASIC_AUTH_USERNAME = "admin"
BASIC_AUTH_PASSWORD = "secret123"

# 文件上传限制
MAX_UPLOAD_SIZE = 1 * 1024 * 1024  # 1 MB

# 各 Content-Type 的示例内容
CONTENT_SAMPLES = {
    "json": ("application/json", '{\n  "message": "Hello, curl!",\n  "items": [1, 2, 3]\n}'),
    "xml": ("application/xml", '<?xml version="1.0" encoding="UTF-8"?>\n<response>\n  <message>Hello, curl!</message>\n</response>'),
    "html": ("text/html; charset=utf-8", '<!DOCTYPE html>\n<html>\n<head><title>Curl Test</title></head>\n<body>\n  <h1>Hello, curl!</h1>\n</body>\n</html>'),
    "plain": ("text/plain; charset=utf-8", "Hello, curl!\nThis is a plain text response."),
    "css": ("text/css; charset=utf-8", "body {\n  color: #333;\n  font-family: sans-serif;\n}"),
    "javascript": ("application/javascript; charset=utf-8", "const greeting = 'Hello, curl!';\nconsole.log(greeting);"),
    "csv": ("text/csv; charset=utf-8", "name,age,city\nAlice,25,Beijing\nBob,30,Shanghai"),
}

# 端点元数据（供 /api/endpoints 自文档化）
ENDPOINTS = [
    {"path": "/api/endpoints", "methods": ["GET"], "desc": "列出所有可用端点（自文档化）",
     "example": "curl http://localhost:5000/api/endpoints"},
    {"path": "/api/echo", "methods": ["GET","POST","PUT","DELETE","PATCH"], "desc": "回显完整请求信息（method/headers/query/body）",
     "example": "curl -X POST http://localhost:5000/api/echo -H 'Content-Type: application/json' -d '{\"key\":\"val\"}'"},
    {"path": "/api/methods", "methods": ["GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD"], "desc": "回显 HTTP 方法，OPTIONS 返回 Allow 头",
     "example": "curl -X OPTIONS -i http://localhost:5000/api/methods"},
    {"path": "/api/status/<code>", "methods": ["GET"], "desc": "返回指定的 HTTP 状态码（100-599）",
     "example": "curl -i http://localhost:5000/api/status/404"},
    {"path": "/api/redirect", "methods": ["GET"], "desc": "重定向测试，支持 301/302/303/307/308，可链式跳转（n=1~5）",
     "example": "curl -L http://localhost:5000/api/redirect?type=301&to=/api/echo&n=2"},
    {"path": "/api/cookie/set", "methods": ["GET"], "desc": "设置 cookie（name/value/max_age/http_only/secure/same_site）",
     "example": "curl -c cookies.txt http://localhost:5000/api/cookie/set?name=session&value=abc123"},
    {"path": "/api/cookie/get", "methods": ["GET"], "desc": "读取并返回请求中的 cookie",
     "example": "curl -b cookies.txt http://localhost:5000/api/cookie/get"},
    {"path": "/api/basic-auth", "methods": ["GET"], "desc": "Basic 认证测试（admin/secret123），401 + WWW-Authenticate 挑战",
     "example": "curl -u admin:secret123 http://localhost:5000/api/basic-auth"},
    {"path": "/api/delay/<seconds>", "methods": ["GET"], "desc": "延迟响应（0-30 秒），测试超时",
     "example": "curl --max-time 2 http://localhost:5000/api/delay/5"},
    {"path": "/api/content-type/<type>", "methods": ["GET"], "desc": "返回指定 Content-Type 的示例响应（json/xml/html/plain/css/javascript/csv）",
     "example": "curl http://localhost:5000/api/content-type/xml"},
    {"path": "/api/upload", "methods": ["POST"], "desc": "接收文件上传（仅读取不保存，限制 1MB）",
     "example": "curl -F 'file=@test.txt' http://localhost:5000/api/upload"},
    {"path": "/api/size", "methods": ["POST","PUT"], "desc": "测量请求体大小并回显",
     "example": "curl -X POST http://localhost:5000/api/size -d 'Hello, HTTP!'"},
]


@app.route("/")
def index():
    """返回前端页面"""
    return render_template("index.html")


@app.route("/api/check")
def check_headers():
    """接收 URL，请求它，返回安全头分析结果"""
    url = request.args.get("url", "").strip()

    if not url:
        return jsonify({"error": "请输入 URL"}), 400

    # 自动补全协议
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        # 发起请求（禁用重定向以检测 HTTP→HTTPS 跳转，禁用 SSL 验证以兼容自签名证书）
        resp = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            verify=False,       # 忽略 SSL 证书错误
            headers={"User-Agent": "SecurityHeaderChecker/1.0"},
        )
    except requests.exceptions.SSLError:
        return jsonify({"error": "SSL 证书错误，无法建立 HTTPS 连接"}), 400
    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"无法连接到 {url}，请检查 URL 是否正确"}), 400
    except requests.exceptions.Timeout:
        return jsonify({"error": "请求超时，目标服务器无响应"}), 400
    except requests.exceptions.TooManyRedirects:
        return jsonify({"error": "重定向次数过多"}), 400
    except requests.exceptions.InvalidURL:
        return jsonify({"error": "URL 格式不正确"}), 400
    except Exception as e:
        return jsonify({"error": f"请求失败：{str(e)}"}), 400

    # 分析安全头
    response_headers = resp.headers
    results = []

    for header_key, info in SECURITY_HEADERS.items():
        value = response_headers.get(header_key)
        results.append(
            {
                "header": header_key,
                "name": info["name"],
                "desc": info["desc"],
                "example": info["example"],
                "present": value is not None,
                "value": value if value else None,
            }
        )

    return jsonify(
        {
            "url": resp.url,                # 最终请求的 URL（可能经过了重定向）
            "status_code": resp.status_code,
            "results": results,
            "total": len(results),
            "present_count": sum(1 for r in results if r["present"]),
        }
    )


# ============================================================
# curl 测试端点
# ============================================================

@app.route("/api/endpoints")
def list_endpoints():
    """返回所有 curl 测试端点的元数据"""
    return jsonify(ENDPOINTS)


@app.route("/api/echo", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def echo():
    """回显完整请求信息——最核心的端点，让 curl 用户看到请求实际长什么样"""
    body = None
    form_data = None
    json_data = None
    files = None

    if request.method in ("POST", "PUT", "PATCH"):
        # 获取原始 body（文本形式）
        body = request.get_data(as_text=True) or None
        # 尝试解析 JSON
        if request.is_json:
            json_data = request.get_json()
        # 尝试解析 URL-encoded 表单
        if request.form:
            form_data = dict(request.form)
        # 列出上传的文件名
        if request.files:
            files = [f.filename for f in request.files.values() if f.filename]

    # 收集所有请求头
    headers = {k: v for k, v in request.headers.items()}

    return jsonify({
        "method": request.method,
        "url": request.url,
        "path": request.path,
        "query_params": dict(request.args),
        "headers": headers,
        "body": body,
        "form_data": form_data,
        "json_data": json_data,
        "files": files,
        "remote_addr": request.remote_addr,
    })


@app.route("/api/methods", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
def method_test():
    """回显请求方法，OPTIONS 返回 Allow 头"""
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Allow"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD"
        return resp
    if request.method == "HEAD":
        return make_response("", 200, {"Content-Type": "application/json"})
    return jsonify({
        "method": request.method,
        "message": f"你使用了 {request.method} 方法",
    })


@app.route("/api/status/<int:code>")
def status_code(code):
    """返回指定的 HTTP 状态码"""
    if code < 100 or code > 599:
        return jsonify({"error": f"无效的状态码 {code}，范围：100-599"}), 400
    try:
        phrase = HTTPStatus(code).phrase
    except ValueError:
        phrase = "Unknown Status"
    return jsonify({"code": code, "message": phrase}), code


@app.route("/api/redirect")
def redirect_test():
    """重定向测试，支持链式跳转"""
    redir_type = request.args.get("type", "302")
    target = request.args.get("to", "/api/echo")
    n_str = request.args.get("n", "1")

    try:
        n = int(n_str)
    except ValueError:
        return jsonify({"error": "n 必须是整数"}), 400

    if n < 1 or n > 5:
        return jsonify({"error": "n 必须在 1-5 之间"}), 400

    valid_types = {"301": 301, "302": 302, "303": 303, "307": 307, "308": 308}
    if redir_type not in valid_types:
        return jsonify({
            "error": f"无效的重定向类型 '{redir_type}'",
            "supported": list(valid_types.keys()),
        }), 400

    if n == 1:
        return redirect(target, code=valid_types[redir_type])

    # 链式跳转：跳回自己，n 减 1
    next_url = f"/api/redirect?type={redir_type}&to={target}&n={n - 1}"
    return redirect(next_url, code=valid_types[redir_type])


@app.route("/api/cookie/set")
def cookie_set():
    """设置 cookie"""
    name = request.args.get("name", "test_cookie")
    value = request.args.get("value", "hello")
    max_age = request.args.get("max_age")
    http_only = request.args.get("http_only", "0")
    secure = request.args.get("secure", "0")
    same_site = request.args.get("same_site", "Lax")

    resp = make_response(jsonify({
        "message": "Cookie 已设置",
        "cookie": {
            "name": name,
            "value": value,
            "max_age": int(max_age) if max_age else None,
            "http_only": http_only == "1",
            "secure": secure == "1",
            "same_site": same_site,
        },
    }))

    kwargs = {
        "httponly": http_only == "1",
        "secure": secure == "1",
    }
    if max_age:
        kwargs["max_age"] = int(max_age)
    if same_site in ("Lax", "Strict", "None"):
        kwargs["samesite"] = same_site

    resp.set_cookie(name, value, **kwargs)
    return resp


@app.route("/api/cookie/get")
def cookie_get():
    """读取请求中的 cookie 并返回"""
    cookies = dict(request.cookies)
    if not cookies:
        return jsonify({
            "cookies": {},
            "hint": "没有收到 cookie。先用 /api/cookie/set 设置，curl 用 -c 保存、-b 发送。",
        })
    return jsonify({"cookies": cookies})


@app.route("/api/basic-auth")
def basic_auth():
    """Basic 认证测试"""
    auth = request.authorization
    if not auth:
        resp = make_response(jsonify({
            "error": "需要认证",
            "hint": "使用 curl -u admin:secret123 或设置 Authorization: Basic <base64> 头",
        }), 401)
        resp.headers["WWW-Authenticate"] = 'Basic realm="curl test"'
        return resp

    if not hmac.compare_digest(auth.username, BASIC_AUTH_USERNAME) or \
       not hmac.compare_digest(auth.password, BASIC_AUTH_PASSWORD):
        resp = make_response(jsonify({"error": "用户名或密码错误"}), 401)
        resp.headers["WWW-Authenticate"] = 'Basic realm="curl test"'
        return resp

    return jsonify({
        "message": f"认证成功，欢迎 {auth.username}！",
        "username": auth.username,
    })


@app.route("/api/delay/<float:seconds>")
def delayed(seconds):
    """延迟指定秒数后响应，用于测试超时"""
    if seconds < 0 or seconds > 30:
        return jsonify({
            "error": f"延迟时间必须在 0-30 秒之间，收到：{seconds}"
        }), 400

    start = time.monotonic()
    time.sleep(seconds)
    actual = round(time.monotonic() - start, 3)

    return jsonify({
        "requested_seconds": seconds,
        "actual_seconds": actual,
        "message": f"响应延迟了 {actual} 秒",
    })


@app.route("/api/content-type/<string:type>")
def content_type_endpoint(type):
    """返回指定 Content-Type 的示例响应"""
    type_lower = type.lower()
    if type_lower not in CONTENT_SAMPLES:
        return jsonify({
            "error": f"不支持的类型 '{type}'",
            "supported": list(CONTENT_SAMPLES.keys()),
        }), 400

    mime, content = CONTENT_SAMPLES[type_lower]
    return make_response(content, 200, {"Content-Type": mime})


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """接收文件上传——读取文件但不保存到磁盘（保持项目干净）"""
    if request.content_length and request.content_length > MAX_UPLOAD_SIZE:
        return jsonify({
            "error": f"文件过大，限制 {MAX_UPLOAD_SIZE // 1024 // 1024} MB"
        }), 413

    files_info = []
    for key in request.files:
        f = request.files[key]
        if f.filename:
            content = f.read()  # 读取以获取大小，但不写入磁盘
            files_info.append({
                "field": key,
                "filename": f.filename,
                "content_type": f.content_type or "unknown",
                "size_bytes": len(content),
            })

    if not files_info:
        return jsonify({
            "error": "没有收到文件。使用 curl -F 'file=@文件路径' 上传",
        }), 400

    return jsonify({
        "message": f"收到 {len(files_info)} 个文件（仅读取，未保存到磁盘）",
        "files": files_info,
    })


@app.route("/api/size", methods=["POST", "PUT"])
def request_size():
    """测量请求体大小"""
    body = request.get_data(as_text=False)
    size = len(body)
    content_length = request.headers.get("Content-Length", "未设置")

    try:
        preview = body[:100].decode("utf-8", errors="replace")
    except Exception:
        preview = repr(body[:100])

    return jsonify({
        "body_size_bytes": size,
        "body_size_kb": round(size / 1024, 2),
        "content_length_header": content_length,
        "first_100_chars": preview,
    })


if __name__ == "__main__":
    # 开发模式
    app.run(host="0.0.0.0", port=5000, debug=True)
```

---

## 第 3 步：前端（HTML + CSS + JS）

创建 `templates/index.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTTP 安全头检查</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 40px 20px;
        }

        .container {
            max-width: 780px;
            width: 100%;
        }

        h1 {
            font-size: 1.8rem;
            text-align: center;
            margin-bottom: 8px;
            color: #f1f5f9;
        }

        .subtitle {
            text-align: center;
            color: #94a3b8;
            margin-bottom: 32px;
            font-size: 0.95rem;
        }

        .search-box {
            display: flex;
            gap: 8px;
            margin-bottom: 32px;
        }

        .search-box input {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #334155;
            border-radius: 10px;
            background: #1e293b;
            color: #e2e8f0;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
        }

        .search-box input:focus {
            border-color: #3b82f6;
        }

        .search-box input::placeholder {
            color: #64748b;
        }

        .search-box button {
            padding: 14px 28px;
            border: none;
            border-radius: 10px;
            background: #3b82f6;
            color: #fff;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }

        .search-box button:hover {
            background: #2563eb;
        }

        .search-box button:disabled {
            background: #475569;
            cursor: not-allowed;
        }

        .error {
            background: #7f1d1d;
            border: 1px solid #ef4444;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 24px;
            color: #fca5a5;
        }

        .summary {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }

        .summary-card {
            flex: 1;
            background: #1e293b;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
        }

        .summary-card .num {
            font-size: 2rem;
            font-weight: 700;
        }

        .summary-card .num.green { color: #22c55e; }
        .summary-card .num.red { color: #ef4444; }
        .summary-card .label {
            color: #94a3b8;
            font-size: 0.85rem;
            margin-top: 4px;
        }

        .result-card {
            background: #1e293b;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 12px;
            border-left: 4px solid #334155;
        }

        .result-card.present {
            border-left-color: #22c55e;
        }

        .result-card.missing {
            border-left-color: #ef4444;
        }

        .result-card .header-name {
            font-size: 1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 100px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge.ok {
            background: #14532d;
            color: #22c55e;
        }

        .badge.fail {
            background: #7f1d1d;
            color: #ef4444;
        }

        .result-card .header-key {
            font-family: monospace;
            color: #94a3b8;
            font-size: 0.85rem;
            margin: 6px 0;
        }

        .result-card .desc {
            color: #94a3b8;
            font-size: 0.9rem;
            margin-top: 6px;
        }

        .result-card .current-value {
            margin-top: 10px;
            padding: 10px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.85rem;
            word-break: break-all;
        }

        .result-card.present .current-value {
            background: #0f172a;
            color: #22c55e;
        }

        .result-card.missing .current-value {
            background: #0f172a;
            color: #ef4444;
        }

        .example {
            color: #64748b;
            font-size: 0.8rem;
            margin-top: 6px;
        }

        .footer {
            text-align: center;
            color: #475569;
            font-size: 0.8rem;
            margin-top: 40px;
        }

        /* curl 端点参考卡片 */
        .curl-ref {
            margin-top: 32px;
            background: #1e293b;
            border-radius: 10px;
            padding: 20px;
            cursor: default;
        }

        .curl-ref-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #f1f5f9;
            cursor: pointer;
            list-style: none;
        }

        .curl-ref-title::-webkit-details-marker { display: none; }

        .curl-ref-title::before {
            content: "+ ";
            color: #3b82f6;
            font-family: monospace;
        }

        details[open] .curl-ref-title::before {
            content: "- ";
        }

        .curl-ref-hint {
            color: #94a3b8;
            font-size: 0.85rem;
            margin: 12px 0;
        }

        .curl-grid {
            display: grid;
            gap: 10px;
        }

        .curl-item {
            background: #0f172a;
            border-radius: 8px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: background 0.15s;
        }

        .curl-item:hover {
            background: #1e293b;
        }

        .curl-item .curl-method {
            font-family: monospace;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            background: #22c55e;
            color: #0f172a;
            white-space: nowrap;
        }

        .curl-item .curl-method.post { background: #3b82f6; color: #fff; }
        .curl-item .curl-method.put { background: #f59e0b; color: #0f172a; }
        .curl-item .curl-method.delete { background: #ef4444; color: #fff; }

        .curl-item .curl-path {
            font-family: monospace;
            font-size: 0.9rem;
            color: #e2e8f0;
            flex: 1;
        }

        .curl-item .curl-desc {
            color: #94a3b8;
            font-size: 0.8rem;
            min-width: 120px;
            text-align: right;
        }

        .curl-example {
            display: none;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 10px 14px;
            margin: 6px 0 6px 0;
            font-family: monospace;
            font-size: 0.8rem;
            color: #22c55e;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }

        .curl-item.active + .curl-example {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>HTTP 安全头检查</h1>
        <p class="subtitle">输入一个网址，检查它的 HTTP 安全响应头是否正确配置</p>

        <div class="search-box">
            <input
                type="text"
                id="urlInput"
                placeholder="输入网址，例如 example.com"
                autocomplete="off"
                autofocus
            >
            <button id="checkBtn" onclick="checkHeaders()">检查</button>
        </div>

        <div id="errorBox"></div>
        <div id="resultBox"></div>

        <details class="curl-ref">
            <summary class="curl-ref-title">curl 测试端点参考</summary>
            <p class="curl-ref-hint">以下端点可用 curl 命令行测试，点击可查看示例。</p>
            <div class="curl-grid" id="curlGrid"></div>
        </details>

        <p class="footer">检查项：HSTS / CSP / X-Frame-Options / X-Content-Type-Options / Referrer-Policy / Permissions-Policy / X-XSS-Protection</p>
    </div>

    <script>
        const input = document.getElementById("urlInput");
        const button = document.getElementById("checkBtn");
        const errorBox = document.getElementById("errorBox");
        const resultBox = document.getElementById("resultBox");

        // 回车触发检查
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") checkHeaders();
        });

        async function checkHeaders() {
            const url = input.value.trim();
            if (!url) return;

            // 加载状态
            button.disabled = true;
            button.textContent = "检查中...";
            errorBox.innerHTML = "";
            resultBox.innerHTML = "";

            try {
                const resp = await fetch(`/api/check?url=${encodeURIComponent(url)}`);
                const data = await resp.json();

                if (!resp.ok) {
                    errorBox.innerHTML = `<div class="error">${escapeHtml(data.error)}</div>`;
                    return;
                }

                renderResults(data);
            } catch (err) {
                errorBox.innerHTML = `<div class="error">网络错误：${escapeHtml(err.message)}</div>`;
            } finally {
                button.disabled = false;
                button.textContent = "检查";
            }
        }

        function renderResults(data) {
            const passed = data.present_count;
            const total = data.total;

            let html = `
                <div class="summary">
                    <div class="summary-card">
                        <div class="num green">${passed}</div>
                        <div class="label">已配置</div>
                    </div>
                    <div class="summary-card">
                        <div class="num red">${total - passed}</div>
                        <div class="label">缺失</div>
                    </div>
                    <div class="summary-card">
                        <div class="num" style="color:#94a3b8">${data.status_code}</div>
                        <div class="label">HTTP 状态码</div>
                    </div>
                </div>
                <p style="color:#64748b;font-size:0.85rem;margin-bottom:16px;">
                    目标：${escapeHtml(data.url)}
                </p>
            `;

            for (const r of data.results) {
                const cls = r.present ? "present" : "missing";
                const badge = r.present
                    ? '<span class="badge ok">已配置</span>'
                    : '<span class="badge fail">缺失</span>';

                html += `
                    <div class="result-card ${cls}">
                        <div class="header-name">${escapeHtml(r.name)} ${badge}</div>
                        <div class="header-key">${escapeHtml(r.header)}</div>
                        <div class="desc">${escapeHtml(r.desc)}</div>
                        <div class="current-value">
                            ${r.present ? escapeHtml(r.value) : '（未设置）'}
                        </div>
                        <div class="example">推荐：${escapeHtml(r.example)}</div>
                    </div>
                `;
            }

            resultBox.innerHTML = html;
        }

        function escapeHtml(text) {
            const div = document.createElement("div");
            div.textContent = text;
            return div.innerHTML;
        }

        // --- curl 端点参考 ---
        const curlEndpoints = [
            { path: "/api/endpoints", methods: ["GET"], desc: "列出所有端点", example: "curl http://localhost:5000/api/endpoints" },
            { path: "/api/echo", methods: ["GET","POST","PUT","DELETE","PATCH"], desc: "回显完整请求信息", example: "curl -X POST http://localhost:5000/api/echo -H 'Content-Type: application/json' -d '{\"key\":\"val\"}'" },
            { path: "/api/methods", methods: ["GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD"], desc: "回显 HTTP 方法", example: "curl -X OPTIONS -i http://localhost:5000/api/methods" },
            { path: "/api/status/<code>", methods: ["GET"], desc: "返回指定状态码", example: "curl -i http://localhost:5000/api/status/404" },
            { path: "/api/redirect", methods: ["GET"], desc: "重定向测试", example: "curl -L http://localhost:5000/api/redirect?n=2&to=/api/echo" },
            { path: "/api/cookie/set", methods: ["GET"], desc: "设置 Cookie", example: "curl -c cookies.txt http://localhost:5000/api/cookie/set?name=s&value=v" },
            { path: "/api/cookie/get", methods: ["GET"], desc: "读取 Cookie", example: "curl -b cookies.txt http://localhost:5000/api/cookie/get" },
            { path: "/api/basic-auth", methods: ["GET"], desc: "Basic 认证", example: "curl -u admin:secret123 http://localhost:5000/api/basic-auth" },
            { path: "/api/delay/<seconds>", methods: ["GET"], desc: "延迟响应", example: "curl --max-time 2 http://localhost:5000/api/delay/3" },
            { path: "/api/content-type/<type>", methods: ["GET"], desc: "指定 Content-Type", example: "curl http://localhost:5000/api/content-type/xml" },
            { path: "/api/upload", methods: ["POST"], desc: "文件上传", example: "curl -F 'file=@test.txt' http://localhost:5000/api/upload" },
            { path: "/api/size", methods: ["POST","PUT"], desc: "测量请求体大小", example: "curl -X POST http://localhost:5000/api/size -d 'Hello!'" },
        ];

        (function renderCurlGrid() {
            const grid = document.getElementById("curlGrid");
            if (!grid) return;
            let html = "";
            curlEndpoints.forEach((ep, i) => {
                const methods = ep.methods.map(m => {
                    let cls = "";
                    if (m === "POST") cls = "post";
                    else if (m === "PUT" || m === "PATCH") cls = "put";
                    else if (m === "DELETE") cls = "delete";
                    return `<span class="curl-method ${cls}">${m}</span>`;
                }).join("");
                html += `
                    <div class="curl-item" onclick="toggleExample(this)" data-i="${i}">
                        ${methods}
                        <span class="curl-path">${escapeHtml(ep.path)}</span>
                        <span class="curl-desc">${escapeHtml(ep.desc)}</span>
                    </div>
                    <div class="curl-example">$ ${escapeHtml(ep.example)}</div>`;
            });
            grid.innerHTML = html;
        })();

        function toggleExample(item) {
            const wasActive = item.classList.contains("active");
            // 关闭所有展开的
            document.querySelectorAll(".curl-item.active").forEach(el => el.classList.remove("active"));
            // 切换当前
            if (!wasActive) item.classList.add("active");
        }
    </script>
</body>
</html>
```

---

## 第 4 步：Python 依赖

创建 `requirements.txt`：

```
flask==3.0.*
requests==2.31.*
gunicorn==21.2.*
```

安装依赖验证能跑：

```bash
pip install -r requirements.txt
python app.py
# 浏览器打开 http://localhost:5000
```

---

## 第 5 步：Docker 化

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖（先复制 requirements，利用 Docker 缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .
COPY templates/ ./templates/

# 声明端口
EXPOSE 5000

# Gunicorn 启动（生产模式），关闭 SSL 警告
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
```

可选，创建 `docker-compose.yml`（更简洁的启动方式）：

```yaml
version: "3.8"

services:
  web:
    build: .
    container_name: header-checker
    ports:
      - "5000:5000"
    restart: unless-stopped
```

---

## 第 6 步：构建和运行

```bash
# 构建镜像
docker build -t header-checker .

# 运行容器
docker run -d --name header-checker -p 5000:5000 header-checker

# 或者用 compose
docker compose up -d

# 验证
docker ps | grep header-checker
curl http://localhost:5000/api/check?url=example.com
```

---

## 第 7 步：局域网访问

容器默认监听 `0.0.0.0:5000`，同一局域网内的任何设备都可以通过宿主机的 IP 访问。

```bash
# 查看宿主机局域网 IP
ip addr show | grep "inet " | grep -v 127.0.0.1
# 或 Windows：ipconfig

# 假设宿主机 IP 是 192.168.1.100
# 手机 / 其他电脑浏览器打开：
# http://192.168.1.100:5000
```

如果其他设备无法访问，检查防火墙：

```bash
# Linux（ufw）
sudo ufw allow 5000/tcp

# Linux（firewalld）
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload

# Windows：控制面板 → Windows Defender 防火墙 → 高级设置 → 入站规则 → 新建规则 → 端口 5000
```

---

## 第 8 步：验证完整流程

```bash
# 1. 确认容器正常运行
docker ps

# 2. 测试 API
curl http://localhost:5000/api/check?url=baidu.com
# 返回 JSON，包含各安全头的检查结果

# 3. 浏览器打开 http://localhost:5000
# 输入 example.com，点击检查

# 4. 手机连同一 WiFi，浏览器打开 http://<宿主机IP>:5000
```

---

## 项目总结

从零开始，你完成了：

```
空文件夹
  └── app.py         ← 后端逻辑（Flask，安全头检查 + 12 个 curl 测试端点）
  └── index.html     ← 前端页面（表单 + 结果卡片 + curl 端点参考）
  └── Dockerfile     ← 容器化
  └── docker-compose.yml  ← 一键启动
  └── 在局域网任何设备上通过 IP:5000 访问
```

**你在这个过程中接触到的知识点：**

| 阶段 | 涉及内容 |
|------|---------|
| 后端 | Flask 路由、请求参数、JSON 响应、requests 库发 HTTP 请求、错误处理 |
| 前端 | HTML 表单、CSS 布局、JavaScript fetch API、DOM 操作 |
| 信安 | 7 种 HTTP 安全响应头的作用和最佳实践 |
| 部署 | Dockerfile 编写、镜像构建、容器运行、端口映射、Gunicorn |
| curl/HTTP | HTTP 方法（GET/POST/PUT/DELETE/PATCH/OPTIONS/HEAD）、请求结构与回显、状态码含义、重定向（301/302/307/308）、Cookie 机制、Basic 认证流程、Content-Type/MIME 类型、超时控制、文件上传（multipart） |
| 网络 | 0.0.0.0 vs 127.0.0.1、局域网 IP、防火墙端口放行 |

---


## 第 9 步：真实服务器部署实战（Rocky Linux 9 + Apache + mod_wsgi）

> 本节以 security-header-checker 项目为例，记录在 Rocky Linux 9 上使用 Apache + mod_wsgi 完成生产部署的完整过程。项目从 `/root/` 迁移到 `/var/www/`，解决 403/500 错误，最终实现局域网内浏览器访问。

### 架构图

```
┌─────────────────┐     ┌─────────────────────────────────────────────┐
│ 用户浏览器       │     │ Rocky Linux 虚拟机                          │
│ (Kali 物理机)   │────▶│ ┌─────────────────────────────────────┐     │
│                 │     │ │ Apache (端口 80)                      │     │
│ 请求 URL:       │     │ │ ├── httpd.conf                       │     │
│ /api/check...   │     │ │ └── conf.d/header-checker.conf       │     │
└─────────────────┘     │ └───────────────┬─────────────────────┘     │
                        │                 │ WSGI 协议                  │
                        │                 ▼                            │
                        │ ┌─────────────────────────────────────┐     │
                        │ │ mod_wsgi                            │     │
                        │ │ (Apache 的 Python WSGI 模块)         │     │
                        │ └───────────────┬─────────────────────┘     │
                        │                 │ 调用                        │
                        │                 ▼                            │
                        │ ┌─────────────────────────────────────┐     │
                        │ │ wsgi.py (入口文件)                   │     │
                        │ │ from app import app as application   │     │
                        │ └───────────────┬─────────────────────┘     │
                        │                 │                            │
                        │                 ▼                            │
                        │ ┌─────────────────────────────────────┐     │
                        │ │ Flask 应用 (app.py)                  │     │
                        │ │ ├── 路由装饰器                       │     │
                        │ │ ├── 安全检查逻辑                     │     │
                        │ │ └── templates/ HTML 模板             │     │
                        │ └───────────────┬─────────────────────┘     │
                        │                 │ 依赖                        │
                        │                 ▼                            │
                        │ ┌─────────────────────────────────────┐     │
                        │ │ 虚拟环境 (venv/)                     │     │
                        │ │ ├── Python 3.9                       │     │
                        │ │ ├── Flask 3.0.3                      │     │
                        │ │ ├── gunicorn 21.2.0                  │     │
                        │ │ ├── requests 2.31.0                  │     │
                        │ │ └── 其他依赖包                       │     │
                        │ └─────────────────────────────────────┘     │
                        └─────────────────────────────────────────────┘
```

### 各组件角色说明

理解每个组件在请求链路中承担什么职责，是排错和优化的前提。

| 组件 | 角色 | 在整个链路中做了什么 |
|------|------|---------------------|
| **用户浏览器** | 请求发起者 | 发送 HTTP 请求到服务器的 80 端口。URL 中的域名/IP 决定了请求到达哪台机器 |
| **Apache (httpd)** | Web 服务器 / 反向代理 | 监听 80 端口，接收所有 HTTP 请求。根据 VirtualHost 配置决定把请求交给谁处理——静态文件自己直接返回，Python 请求交给 mod_wsgi |
| **mod_wsgi** | Apache 模块 / 桥梁 | 嵌入在 Apache 进程中的 Python 解释器宿主。它实现 WSGI 协议，把 Apache 收到的 HTTP 请求翻译成 Python 能理解的格式，调用 Flask 应用，再把 Flask 的返回值翻译回 HTTP 响应 |
| **WSGI 协议** | 规范 / 接口约定 | Python Web 应用和 Web 服务器之间的标准接口。它规定：服务器调用一个名为 `application` 的可调用对象，传入 `environ`（环境变量字典，含请求信息）和 `start_response`（回调函数，用来设置状态码和响应头），应用返回可迭代的响应体 |
| **wsgi.py** | 入口文件 / 适配器 | 唯一作用是暴露一个名为 `application` 的变量。它把项目路径加入 `sys.path`，然后 `from app import app as application`。Apache 不认识 Flask，它只通过 WSGI 协议找 `application` 对象 |
| **Flask 应用 (app.py)** | 业务逻辑 | 处理路由匹配、参数解析、调用安全检查逻辑、渲染模板。它不关心请求是从 Apache 来的还是从 Flask 开发服务器来的——这正是 WSGI 的价值：应用和服务器解耦 |
| **虚拟环境 (venv/)** | 依赖隔离 | 为这个项目提供独立的 Python 解释器和第三方包。Apache 通过 `python-home` 指向 venv 来使用其中的 Python 和包，不影响系统 Python 环境 |

**请求处理流程（一次完整的 API 调用）：**

```
1. 用户浏览器 → GET /api/check?url=baidu.com HTTP/1.1
2. Apache 收到请求 → 匹配 VirtualHost → 命中 WSGIScriptAlias / → 交给 mod_wsgi
3. mod_wsgi → 构造 WSGI environ 字典（PATH_INFO=/api/check, QUERY_STRING=url=baidu.com, ...）
4. mod_wsgi → 调用 wsgi.py 中的 application(environ, start_response)
5. Flask → 匹配路由 @app.route('/api/check') → 执行 check_headers()
6. Flask → requests.get(目标 URL) → 解析响应头 → 构造 JSON
7. Flask → 返回 Response 对象 → mod_wsgi 接收
8. mod_wsgi → 翻译为 HTTP 响应 → Apache 发送给浏览器
9. 浏览器 → 收到 JSON，渲染结果
```

> **关键理解**：Apache 和 Flask 之间不直接通信。mod_wsgi 是翻译官——Apache 说 HTTP，Flask 说 Python，mod_wsgi 在中间通过 WSGI 协议互相翻译。这就是为什么你在开发时用 `flask run` 也能跑，生产部署时换成 Apache+mod_wsgi 也能跑——Flask 代码本身不需要改，因为无论是 Flask 开发服务器还是 mod_wsgi，都遵循同一个 WSGI 协议。

---

### 一、初始环境检查

#### 1.1 项目原始位置

```bash
[root@localhost ~]# ls -la /root/security-header-checker/
app.py  docker-compose.yml  Dockerfile  requirements.txt  security-header-checker_venv  templates
```

项目最初位于 `/root/` 下，后续因权限问题迁移到 `/var/www/`。

#### 1.2 系统环境信息

```bash
# 操作系统
[root@localhost ~]# cat /etc/redhat-release
Rocky Linux release 9.5 (Blue Onyx)

# Python 版本
[root@localhost ~]# python3 --version
Python 3.9.18

# Apache 版本
[root@localhost ~]# httpd -v
Server version: Apache/2.4.57
```

---

### 二、Python 虚拟环境准备

#### 2.1 创建虚拟环境

```bash
[root@localhost ~]# cd /root/security-header-checker
[root@localhost security-header-checker]# python3 -m venv venv
```

#### 2.2 激活并安装依赖

```bash
[root@localhost security-header-checker]# source venv/bin/activate
(venv) [root@localhost security-header-checker]# pip install --upgrade pip
(venv) [root@localhost security-header-checker]# pip install -r requirements.txt
```

#### 2.3 验证依赖安装

```bash
(venv) [root@localhost security-header-checker]# pip list | grep -E "Flask|requests|gunicorn"
Flask              3.0.3
gunicorn           21.2.0
requests           2.31.0
```

---

### 三、Apache 与 mod_wsgi 安装

#### 3.1 安装所需软件包

```bash
[root@localhost security-header-checker]# dnf install -y httpd mod_wsgi
```

#### 3.2 验证 mod_wsgi 模块

```bash
[root@localhost security-header-checker]# ls -la /etc/httpd/modules/ | grep wsgi
-rwxr-xr-x. 1 root root 252848  7月 29  2025 mod_wsgi_python3.so

[root@localhost security-header-checker]# grep -r "mod_wsgi" /etc/httpd/conf.modules.d/
/etc/httpd/conf.modules.d/10-wsgi-python3.conf:    LoadModule wsgi_module modules/mod_wsgi_python3.so
```

---

### 四、WSGI 入口文件配置

#### 4.1 创建 wsgi.py

```bash
[root@localhost security-header-checker]# cat > wsgi.py << 'EOF'
import sys
import os

# 将项目目录添加到 Python 路径
sys.path.insert(0, '/root/security-header-checker') 

# 导入 Flask 应用
from app import app as application
EOF
```

---

### 五、Apache 虚拟主机配置

#### 5.1 创建配置文件

```bash
[root@localhost security-header-checker]# cat > /etc/httpd/conf.d/header-checker.conf << 'EOF'
<VirtualHost *:80>
    ServerName localhost
    ServerAdmin root@localhost

    WSGIDaemonProcess header-checker python-path=/root/security-header-checker:/root/security-header-checker/venv/lib/python3.11/site-packages
    WSGIProcessGroup header-checker
    WSGIScriptAlias / /root/security-header-checker/wsgi.py

    <Directory /root/security-header-checker>
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/header-checker-error.log
    CustomLog /var/log/httpd/header-checker-access.log combined
</VirtualHost>
EOF
```

---

### 六、权限与 SELinux 配置

#### 6.1 设置文件权限（此时项目还在 /root）

```bash
[root@localhost security-header-checker]# chown -R apache:apache /root/security-header-checker
[root@localhost security-header-checker]# chmod -R 755 /root/security-header-checker
[root@localhost security-header-checker]# chmod 755 /root/security-header-checker/wsgi.py
```

#### 6.2 遇到的问题与排查

**问题 1：403 Forbidden**

```bash
[root@localhost security-header-checker]# systemctl restart httpd
[root@localhost security-header-checker]# curl http://localhost/api/check?url=baidu.com
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head><title>403 Forbidden</title></head><body>...</body></html>
```

原因：Apache 用户 `apache` 无法访问 `/root` 目录。

**问题 2：500 Internal Server Error**

```bash
[root@localhost security-header-checker]# curl http://localhost/api/check?url=baidu.com
<title>500 Internal Server Error</title>
```

错误日志：

```bash
[root@localhost security-header-checker]# tail -50 /var/log/httpd/header-checker-error.log
ModuleNotFoundError: No module named 'flask'
```

原因：mod_wsgi 使用的是系统 Python，而非虚拟环境中的 Python。

---

### 七、解决方案：迁移项目到 /var/www/

#### 7.1 迁移项目文件

```bash
[root@localhost security-header-checker]# cp -r /root/security-header-checker /var/www/
```

#### 7.2 更新路径配置

```bash
# 更新 wsgi.py
[root@localhost security-header-checker]# sed -i 's|/root/security-header-checker|/var/www/security-header-checker|g' /var/www/security-header-checker/wsgi.py

# 更新 Apache 配置
[root@localhost security-header-checker]# sed -i 's|/root/security-header-checker|/var/www/security-header-checker|g' /etc/httpd/conf.d/header-checker.conf
```

#### 7.3 重新设置权限

```bash
[root@localhost security-header-checker]# chown -R apache:apache /var/www/security-header-checker
[root@localhost security-header-checker]# chmod -R 755 /var/www/security-header-checker
```

#### 7.4 更新 Apache 配置（指定虚拟环境 Python）

最终配置如下：

```apache
<VirtualHost *:80>
    ServerName localhost
    ServerAdmin root@localhost

    # 关键：指定 python-home 指向虚拟环境
    WSGIDaemonProcess header-checker python-home=/var/www/security-header-checker/venv python-path=/var/www/security-header-checker:/var/www/security-header-checker/venv/lib/python3.11/site-packages
    WSGIProcessGroup header-checker
    WSGIScriptAlias / /var/www/security-header-checker/wsgi.py

    <Directory /var/www/security-header-checker>
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/header-checker-error.log
    CustomLog /var/log/httpd/header-checker-access.log combined
</VirtualHost>
```

#### 7.5 SELinux 处理

```bash
# 临时关闭 SELinux（测试用）
[root@localhost security-header-checker]# setenforce 0
```

后续建议执行 `setsebool -P httpd_execmem 1` 永久放行，并配置正确的 SELinux 上下文。

---

### 八、防火墙配置

#### 8.1 放行 HTTP 服务

```bash
[root@localhost security-header-checker]# firewall-cmd --add-service=http --permanent
success
[root@localhost security-header-checker]# firewall-cmd --reload
success
```

#### 8.2 验证防火墙规则

```bash
[root@localhost security-header-checker]# firewall-cmd --list-all
public
  target: default
  icmp-block-inversion: no
  interfaces: ens33
  sources:
  services: dhcpv6-client http ssh
  ports:
  protocols:
  forward: no
  masquerade: no
  forward-ports:
  source-ports:
  icmp-blocks:
  rich rules:
```

---

### 九、最终验证与测试

#### 9.1 检查 Apache 服务状态

```bash
[root@localhost security-header-checker]# systemctl status httpd
● httpd.service - The Apache HTTP Server
     Loaded: loaded (/usr/lib/systemd/system/httpd.service; disabled; preset: disabled)
     Active: active (running) since Fri 2026-06-19 00:46:03 CST; 2min 10s ago
   Main PID: 505022 (httpd)
     Status: "Total requests: 15; Idle/Busy workers 100/0;Requests/sec: 0.115; Bytes served/sec:  75 B/sec"
      Tasks: 195 (limit: 10425)
     Memory: 44.0M (peak: 44.5M)
        CPU: 338ms
```

#### 9.2 本地 API 测试

```bash
[root@localhost security-header-checker]# curl http://localhost/api/check?url=baidu.com
{"present_count":2,"results":[...],"status_code":200,"total":7,"url":"https://www.baidu.com/"}
```

#### 9.3 外部访问测试（Kali 物理机）

```bash
┌──(kali㉿kali)-[~]
└─$ curl http://192.168.230.139/api/check?url=baidu.com
{"present_count":2,"results":[...],"status_code":200,"total":7,"url":"https://www.baidu.com/"}
```

#### 9.4 浏览器访问

在 Kali 物理机浏览器中输入：

```
http://192.168.230.139/api/check?url=baidu.com
```

---

### 十、项目最终目录结构

```bash
[root@localhost security-header-checker]# tree /var/www/security-header-checker/
/var/www/security-header-checker/
├── app.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── templates/
│   └── index.html
├── venv/
│   ├── bin/
│   │   ├── activate
│   │   ├── pip
│   │   ├── python -> python3
│   │   └── python3 -> /usr/bin/python3
│   ├── lib/
│   │   └── python3.11/
│   │       └── site-packages/
│   │           ├── flask/
│   │           ├── requests/
│   │           └── gunicorn/
│   ├── pyvenv.cfg
│   └── share/
└── wsgi.py
```

---

### 十一、关键配置总结

#### 11.1 Apache 虚拟主机配置

| 配置项 | 值 |
|--------|-----|
| 配置文件路径 | `/etc/httpd/conf.d/header-checker.conf` |
| 监听端口 | `80` |
| 虚拟环境路径 | `/var/www/security-header-checker/venv` |
| WSGI 入口 | `/var/www/security-header-checker/wsgi.py` |
| 错误日志 | `/var/log/httpd/header-checker-error.log` |
| 访问日志 | `/var/log/httpd/header-checker-access.log` |

#### 11.2 常用管理命令

| 操作 | 命令 |
|------|------|
| 重启 Apache | `systemctl restart httpd` |
| 查看状态 | `systemctl status httpd` |
| 查看错误日志 | `tail -50 /var/log/httpd/header-checker-error.log` |
| 查看访问日志 | `tail -50 /var/log/httpd/header-checker-access.log` |
| 测试配置文件 | `httpd -t` |
| 开机自启 | `systemctl enable httpd` |
| 防火墙放行 HTTP | `firewall-cmd --add-service=http --permanent && firewall-cmd --reload` |

---

### 十二、故障排查索引

| 错误代码 | 可能原因 | 解决方案 |
|----------|---------|---------|
| 403 Forbidden | Apache 用户无权访问目录 | 将项目移至 `/var/www/` 并设置权限 |
| 500 Internal Server Error | mod_wsgi 找不到 Flask 模块 | 在 Apache 配置中指定 `python-home` 指向虚拟环境 |
| `No module named 'flask'` | 使用了系统 Python 而非虚拟环境 | 检查 `WSGIDaemonProcess` 中 `python-home` 配置 |
| 连接被拒绝 | 防火墙未放行端口 | 执行 `firewall-cmd --add-service=http --permanent` |
| SELinux 阻止访问 | SELinux 安全策略限制 | 临时 `setenforce 0`，永久 `setsebool -P httpd_execmem 1` |

---

### 十三、更新与维护指南

#### 13.1 更新代码

```bash
# 1. 上传新代码到 /var/www/security-header-checker/
# 2. 重启 Apache
[root@localhost security-header-checker]# systemctl restart httpd
```

#### 13.2 更新 Python 依赖

```bash
[root@localhost security-header-checker]# source venv/bin/activate
(venv) [root@localhost security-header-checker]# pip install -r requirements.txt --upgrade
(venv) [root@localhost security-header-checker]# deactivate
[root@localhost security-header-checker]# systemctl restart httpd
```

---

### 十四、部署清单

- [ ] Python 虚拟环境创建与依赖安装
- [ ] Apache + mod_wsgi 安装
- [ ] `wsgi.py` 入口文件创建
- [ ] Apache 虚拟主机配置文件编写
- [ ] 项目从 `/root` 迁移到 `/var/www/`
- [ ] 文件权限设置（`chown` + `chmod`）
- [ ] SELinux 策略调整（`setenforce 0` / `setsebool`）
- [ ] 防火墙放行 HTTP 服务
- [ ] 本地 API 测试通过
- [ ] 外部网络访问测试通过
- [ ] Apache 开机自启设置

---

## 参考

- [MDN: HTTP Security Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#security)
- [OWASP: Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Docker 使用笔记](Linux-Docker.md)
- [Apache HTTP Server（RHEL 系）](../中间件/Apache-RHEL.md)
