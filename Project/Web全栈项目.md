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

## 第 9 步：从 Docker 搬到真实服务器

Docker 只是容器，最终还是要部署到一台真实的服务器上。完整路径：

```
本地开发（你现在完成的）
      │
      ▼
Docker 部署（同一台机器，验证能跑）
      │
      ▼
服务器部署（云服务器/物理机/虚拟机，挂反向代理）
```

### 常见 Web 服务器

Docker 容器里 Gunicorn 直接对外是够的。到了真实服务器上，前面需要挂一个 Web 服务器做**反向代理**——它接收外部请求，转给后面的 Gunicorn，同时处理静态文件、SSL、限流。

| | Apache | Nginx | IIS |
|---|---|---|---|
| 定位 | 老牌全能，模块丰富 | 高性能、高并发、轻量 | Windows 生态首选 |
| 反向代理 | `mod_proxy` 模块 | `proxy_pass` 指令 | ARR + URL Rewrite |
| 配置风格 | `.conf` 或 `.htaccess`（目录级覆盖） | 集中式 `.conf` | GUI 图形界面 + XML |
| 静态文件 | 快 | 极快 | 快 |
| 常见场景 | 传统企业、虚拟主机 | 互联网公司、容器化项目 | Windows 内网、.NET 应用 |

下面给出 Apache 和 Nginx 两种反代方案的完整配置。不管你选哪个，反代的本质是同一件事：

```
浏览器 → Apache/Nginx（80/443 端口）→ Gunicorn（5000 端口，不对外暴露）
         处理 SSL、静态文件              只处理 Python 逻辑
```

### 方案 A：Apache 做反向代理

确保 Apache 启用了反向代理模块：

```bash
# Ubuntu/Debian
sudo a2enmod proxy proxy_http headers
sudo systemctl restart apache2

# CentOS/RHEL
# /etc/httpd/conf.modules.d/00-proxy.conf 中确认以下行已取消注释
# LoadModule proxy_module modules/mod_proxy.so
# LoadModule proxy_http_module modules/mod_proxy_http.so
```

添加虚拟主机配置：

```apache
# /etc/apache2/sites-available/header-checker.conf（Ubuntu）
# 或 /etc/httpd/conf.d/header-checker.conf（CentOS）

<VirtualHost *:80>
    ServerName check.yourdomain.com      # 换成你的域名或 IP

    # 反向代理：把所有请求转发给 Gunicorn
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/

    # 日志
    ErrorLog ${APACHE_LOG_DIR}/header-checker-error.log
    CustomLog ${APACHE_LOG_DIR}/header-checker-access.log combined
</VirtualHost>
```

启用并重载：

```bash
# Ubuntu
sudo a2ensite header-checker.conf
sudo systemctl reload apache2

# CentOS
sudo systemctl reload httpd
```

部署流程：

```bash
# 1. 服务器上启动 Gunicorn（只监听 127.0.0.1，不对外）
gunicorn --bind 127.0.0.1:5000 --workers 2 --daemon app:app

# 2. 配好 Apache 反代后
sudo systemctl restart apache2

# 3. 访问 http://服务器IP 即可
# Gunicorn 不对外暴露 5000 端口，安全性更好
```

### 方案 B：Nginx 做反向代理

```nginx
# /etc/nginx/sites-available/header-checker.conf

server {
    listen 80;
    server_name check.yourdomain.com;    # 换成你的域名或 IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ubuntu
sudo ln -s /etc/nginx/sites-available/header-checker.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 用 Docker Compose 模拟真实架构

不必等有真实服务器才学——在本地用 Compose 把 Apache/Nginx + Gunicorn 组网，效果一样：

```yaml
# docker-compose.yml
version: "3.8"

services:
  # 反向代理层
  apache:
    image: httpd:2.4
    container_name: proxy
    ports:
      - "80:80"
    volumes:
      - ./apache.conf:/usr/local/apache2/conf/httpd.conf
    depends_on:
      - app

  # 应用层（Gunicorn 只对内部 5000，不映射到宿主机）
  app:
    build: .
    container_name: flask-app
    # 注意：没有 ports，外部无法直接访问
```

这样就真正做到了生产级结构——外部请求打到 Apache，Apache 转给 Gunicorn，Flask 容器不对外暴露。

---

## 第 10 步：内置 curl 测试端点

上面的 app.py 不仅是安全头检查工具，还内置了 12 个专门用于 curl 练习的测试端点。这些端点的设计逻辑参照了 httpbin，覆盖了 HTTP 协议的核心概念。

### 为什么加这个

写完安全头检查工具后，你会频繁用 curl 去验证 API。但 curl 能做的事情远不止 `curl http://localhost:5000/api/check?url=xxx`：

- 不同 HTTP 方法（GET/POST/PUT/DELETE/PATCH/OPTIONS/HEAD）有什么区别？
- 请求头长什么样？curl 默认发了哪些头？
- JSON body 和表单 body 有什么不同？
- 重定向有哪几种？`curl -L` 做了什么？
- Cookie 怎么设置、怎么回传？
- Basic 认证的流程是什么？
- Content-Type 有哪些常见值？

这些端点就是用来探索这些问题的——每个端点返回的信息都是**自描述的**，让你能看到 curl 命令背后实际发生的 HTTP 交互。

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/endpoints` | GET | 列出所有可用端点 |
| `/api/echo` | GET/POST/PUT/DELETE/PATCH | 回显完整请求信息（method/headers/query/body/form/json/files/IP） |
| `/api/methods` | GET/POST/PUT/DELETE/PATCH/OPTIONS/HEAD | 回显 HTTP 方法，OPTIONS 返回 Allow 头 |
| `/api/status/<code>` | GET | 返回指定的 HTTP 状态码（100-599） |
| `/api/redirect` | GET | 重定向测试（301/302/303/307/308），支持链式跳转 1-5 次 |
| `/api/cookie/set` | GET | 设置 cookie（name/value/max_age/http_only/secure/same_site） |
| `/api/cookie/get` | GET | 读取并返回请求中携带的 cookie |
| `/api/basic-auth` | GET | Basic 认证测试（admin/secret123），返回 401 + WWW-Authenticate |
| `/api/delay/<seconds>` | GET | 延迟响应（0-30 秒），测试 --max-time / --connect-timeout |
| `/api/content-type/<type>` | GET | 返回指定 Content-Type 的示例响应（json/xml/html/plain/css/javascript/csv） |
| `/api/upload` | POST | 接收文件上传（仅读取不保存，限制 1MB） |
| `/api/size` | POST/PUT | 测量请求体大小 |

### 学习路线

建议按以下顺序逐步探索（从简单到复杂）：

**阶段 1：认识 HTTP 方法**
```bash
curl http://localhost:5000/api/methods           # 默认 GET
curl -X POST http://localhost:5000/api/methods    # 显式指定方法
curl -X OPTIONS -i http://localhost:5000/api/methods  # 看 Allow 响应头
curl -I http://localhost:5000/api/methods         # HEAD 请求，只看响应头
```

**阶段 2：看清请求全貌**
```bash
# GET 带查询参数
curl "http://localhost:5000/api/echo?name=张三&age=25"

# POST JSON 数据
curl -X POST http://localhost:5000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","role":"student"}'

# POST 表单数据（curl 默认 Content-Type: application/x-www-form-urlencoded）
curl -X POST http://localhost:5000/api/echo -d "name=张三&role=student"

# 自定义请求头
curl http://localhost:5000/api/echo \
  -H "X-Custom-Header: test-value" \
  -H "Authorization: Bearer eyJhbGciOi..."
```

**阶段 3：状态码和重定向**
```bash
# 各种状态码
curl -i http://localhost:5000/api/status/200
curl -i http://localhost:5000/api/status/301
curl -i http://localhost:5000/api/status/404
curl -i http://localhost:5000/api/status/500

# 重定向：不加 -L 看到 302，加了才跟踪
curl -i "http://localhost:5000/api/redirect?to=/api/echo"
curl -L "http://localhost:5000/api/redirect?to=/api/echo"

# 链式跳转 3 次
curl -L -v "http://localhost:5000/api/redirect?n=3&to=/api/status/200" 2>&1 | grep -E "^< HTTP|^> GET"
```

**阶段 4：Cookie 和认证**
```bash
# 设置 cookie 并保存到文件
curl -c /tmp/cookies.txt "http://localhost:5000/api/cookie/set?name=session&value=abc123"

# 下次请求带上 cookie
curl -b /tmp/cookies.txt http://localhost:5000/api/cookie/get

# 不保存文件，直接传 cookie 字符串
curl -b "name1=val1; name2=val2" http://localhost:5000/api/cookie/get

# Basic 认证：无凭据返回 401
curl -i http://localhost:5000/api/basic-auth

# 带上凭据
curl -u admin:secret123 http://localhost:5000/api/basic-auth

# 手动构造 Authorization 头（等价于 -u）
echo -n "admin:secret123" | base64   # 得到 YWRtaW46c2VjcmV0MTIz
curl -H "Authorization: Basic YWRtaW46c2VjcmV0MTIz" http://localhost:5000/api/basic-auth
```

**阶段 5：高级场景**
```bash
# 超时测试
time curl -s -o /dev/null http://localhost:5000/api/delay/2
curl --max-time 1 http://localhost:5000/api/delay/3; echo "退出码: $?"

# 不同 Content-Type 的响应
curl http://localhost:5000/api/content-type/json
curl http://localhost:5000/api/content-type/xml
curl http://localhost:5000/api/content-type/html
curl -w "\nContent-Type: %{content_type}\n" -o /dev/null -s http://localhost:5000/api/content-type/javascript

# 文件上传
echo "Hello, this is a test file." > /tmp/test.txt
curl -F "file=@/tmp/test.txt" http://localhost:5000/api/upload
curl -F "file=@/tmp/test.txt" -F "note=附加说明" http://localhost:5000/api/upload

# 测量请求体大小
curl -X POST http://localhost:5000/api/size -d "Hello, HTTP!"
curl -X POST http://localhost:5000/api/size -d "AAAAAAAAAA...（一大段文本）"
```

**综合练习：组合使用 curl 的格式化输出**
```bash
# 查看完整的请求-响应时间线
curl -w "\n---\n耗时明细:\n  DNS解析: %{time_namelookup}s\n  建立连接: %{time_connect}s\n  SSL握手: %{time_appconnect}s\n  首字节: %{time_starttransfer}s\n  总耗时: %{time_total}s\n  HTTP状态码: %{http_code}\n  下载大小: %{size_download} bytes\n" -o /dev/null -s http://localhost:5000/api/echo

# 同时查看请求头和响应体
curl -v http://localhost:5000/api/echo 2>&1 | grep -E "^>|^<|^{\""
```

### 端点的安全考虑

- **文件上传不落盘**：`/api/upload` 只把文件读到内存获取大小，不写入服务器磁盘，防止滥用
- **上传大小限制 1MB**：超过返回 413
- **延迟上限 30 秒**：防止单个请求长时间占用 worker
- **重定向链上限 5 次**：防止无限重定向循环
- **密码比较用 `hmac.compare_digest`**：常量时间比较，防止时序攻击

---

## 后续可以扩展的方向

- 增加更多检查项（Cookie 安全属性、CORS 头、Server 头泄露等）
- 保存检查历史到 SQLite 数据库
- 添加批量检查（上传域名列表）
- 生成 PDF 报告
- 用 Nginx 做反向代理，加 HTTPS
- 加登录认证，防止被滥用
- 扩充 curl 测试端点（支持更多 Content-Type、JWT 认证、gzip 压缩、CORS 模拟等）

每个扩展都是一次独立的学习——往哪个方向走取决于你想深入前端、后端还是安全本身。

---

## 参考

- [MDN: HTTP Security Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#security)
- [OWASP: Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Docker 使用笔记](Linux-Docker.md)

---

## VibeCoding 自检

用 [VibeCoding.md](VibeCoding.md) 的四个标准审视本文档：

### 1. 核心链路是什么

**已明确。** 文档定义了两条核心链路：

- **业务链路**：用户输入 URL → Flask 发 HTTP 请求取响应头 → 解析 7 个安全头 → 返回 JSON → 前端渲染结果卡片
- **部署链路**：`app.py` + `index.html` → `pip install` 本地跑通 → Dockerfile 构建镜像 → `docker run` 容器化 → Apache/Nginx 反代上生产

第 1 步把项目结构画了出来（5 个文件），第 9 步画了本地→Docker→服务器的升级路线，链路清晰。

**不足**：文档长达 1447 行，核心链路被大量细节包裹。建议在文档开头加一段 5 行的"核心链路速览"，让人不读完全文也能把握主干。

### 2. 每个卡点怎么验证

**部分覆盖。** 已有的验证点：

| 卡点 | 验证方式 | 位置 |
|------|---------|------|
| 依赖安装 | `pip install -r requirements.txt && python app.py`，浏览器打开 localhost:5000 | 第 4 步 |
| Docker 构建 | `docker build -t header-checker .` 然后 `docker run`，curl 测试 | 第 6 步 |
| 防火墙 | 给出 ufw / firewalld / Windows 防火墙放行命令 | 第 7 步 |
| 全流程 | docker ps + curl API + 浏览器 + 手机 4 项检查 | 第 8 步 |
| Curl 端点 | 分 5 个阶段给出测试命令，每个阶段可独立验证 | 第 10 步 |

**缺失的验证点**：

- `app.py` 写完后到前端写完前，中间没有一个独立的 API 验证步骤。建议在写完 `app.py` 后加一段"先不写前端，用 curl 验证 API 能通"——现在的第 10 步放在了全文末尾，应该前置到第 2 步和第 3 步之间作为一个独立的验证卡点。
- 反向代理配置（Apache/Nginx）只有配置示例，没有"怎么验证反代生效"的步骤（比如 `curl -I http://服务器IP` 检查响应头中是否有代理标记）。
- Dockerfile 写完到构建之前没有验证——没有提示"先确认 `requirements.txt` 里的包和 `app.py` 的 import 一致"。

### 3. 能不能优先用 API 调用

**做到了。** 整个应用就是 API-first 设计：

- 核心功能 `/api/check?url=xxx` 是独立的 API，不依赖前端也能用 curl 测试
- 内置 12 个 curl 测试端点，覆盖 HTTP 方法、状态码、重定向、Cookie、认证、Content-Type、超时、文件上传——全部可以通过命令行独立验证
- 前端通过 `fetch()` 调用 API，前后端完全解耦
- curl 端点的学习路线（5 个阶段）就是从 API 角度逐步探索 HTTP 协议

每个端点都可以脱离 UI 单独测试，这是 VibeCoding 最看重的特质。

### 4. Spec 文档中有没有成功标准

**有，但分散在文档各处，没有集中列出。**

从文档中可以提取出以下隐含的成功标准：

- 7 个安全头全部检查（HSTS / CSP / X-Frame-Options / X-Content-Type-Options / Referrer-Policy / Permissions-Policy / X-XSS-Protection）
- 正确统计"已配置"和"缺失"数量
- 处理常见错误：无 URL、无效 URL、SSL 证书错误、连接超时、重定向过多
- Docker 容器可启动，局域网其他设备可通过 IP:5000 访问
- 12 个 curl 端点全部可正常响应

**建议**：在文档开头（第 1 步之前）加一个 `## 成功标准` 章节，用 5-8 条 checklist 把上面的标准明确列出来，每条都是可验证的布尔条件。比如：

> - [ ] `curl http://localhost:5000/api/check?url=example.com` 返回 7 个安全头的检查结果
> - [ ] 输入无协议的域名（`baidu.com`）自动补全 `https://`
> - [ ] SSL 证书错误的域名返回友好提示而非崩溃
> - [ ] Docker 容器运行后，手机连同一 WiFi 可访问
> - [ ] 12 个 curl 端点全部返回预期响应

---

**总结**：本文档在核心链路和 API-first 两点上做得很好。验证卡点大部分存在但分散，建议把 API 验证步骤前置到写完 `app.py` 之后。成功标准隐含在正文中，建议抽取为一个独立的 checklist 放在开头，实践前就能对照勾选。
