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
from flask import Flask, render_template, request, jsonify
import requests

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
  └── app.py         ← 后端逻辑（Flask，请求 + 分析安全头）
  └── index.html     ← 前端页面（表单 + 结果卡片）
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

## 后续可以扩展的方向

- 增加更多检查项（Cookie 安全属性、CORS 头、Server 头泄露等）
- 保存检查历史到 SQLite 数据库
- 添加批量检查（上传域名列表）
- 生成 PDF 报告
- 用 Nginx 做反向代理，加 HTTPS
- 加登录认证，防止被滥用

每个扩展都是一次独立的学习——往哪个方向走取决于你想深入前端、后端还是安全本身。

---

## 参考

- [MDN: HTTP Security Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#security)
- [OWASP: Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Docker 使用笔记](../Linux/Linux-Docker.md)
