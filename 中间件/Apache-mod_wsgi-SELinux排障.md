# Apache + mod_wsgi + SELinux 排障实录

> Apache + mod_wsgi 部署 Python Flask 应用时遇到 500 错误，根因是 SELinux 阻止 httpd_t 进程加载 Python C 扩展共享对象（.so 文件）。记录从错误日志到 ausearch 的完整排查与修复过程，以及后续发现的 __pycache__ 写入被拒问题。

---

## 环境说明

| 项目 | 值 |
|------|-----|
| OS | Rocky Linux 9 |
| Apache | 2.4.62 (httpd) |
| Python | 3.9 (venv) |
| mod_wsgi | 4.7.1 |
| 应用 | security-header-checker (Flask，见 [[Web全栈项目]]) |
| 应用路径 | `/var/www/security-header-checker/` |
| SELinux 模式 | Enforcing |

---

## 第一部分：问题现象

Apache 已成功启动，但浏览器访问返回 `500 Internal Server Error`。

查看 Apache 错误日志：

```bash
tail -f /var/log/httpd/header-checker-error.log
```

关键错误行：

```
ImportError: /var/www/security-header-checker/venv/lib64/python3.9/site-packages/
charset_normalizer/cd.cpython-39-x86_64-linux-gnu.so: failed to map segment from shared object
```

调用链：

```
app.py
  -> import requests
    -> from .exceptions import RequestsDependencyWarning
      -> import charset_normalizer as chardet
        -> from .cd import (...)    # C 扩展 .so 加载失败
```

这个错误容易误导：`ImportError` 通常意味着模块没找到，但这里的关键是 `failed to map segment from shared object` -- 模块**找到了**，但**加载失败**。这说明问题不在 Python 路径，而在更底层的内存映射操作。

---

## 第二部分：排查过程

### 2.1 阅读 Apache 错误日志

```bash
tail -50 /var/log/httpd/header-checker-error.log
```

确认错误类型：`ImportError` + `failed to map segment from shared object`，不是简单的 `ModuleNotFoundError`。

### 2.2 排除常见原因

逐一验证以下假设：

```bash
# 1. .so 文件是否存在？
ls -la /var/www/security-header-checker/venv/lib64/python3.9/site-packages/charset_normalizer/cd*.so
# 存在 -- 不是文件缺失问题

# 2. 用虚拟环境直接运行是否正常？
source /var/www/security-header-checker/venv/bin/activate
python -c "import charset_normalizer; print('OK')"
# OK -- 不是 Python 环境或依赖安装问题

# 3. 文件权限是否正常？
ls -la /var/www/security-header-checker/venv/lib64/python3.9/site-packages/charset_normalizer/
# 权限正常 -- 不是普通 DAC 权限问题
```

结论：问题只出现在 Apache/mod_wsgi 上下文中，直接运行 Python 没有问题。

### 2.3 setenforce 0 快速定位

临时关闭 SELinux 来确认是否为 SELinux 导致的（详见 [[Apache-RHEL]] 第 6 节）：

```bash
sudo setenforce 0
sudo systemctl restart httpd
curl http://localhost/
# 返回 200 OK，应用正常工作
```

恢复 SELinux：

```bash
sudo setenforce 1
# 再次访问，500 错误复现
```

确认是 SELinux 策略阻止了 Apache 加载 C 扩展。

### 2.4 使用 ausearch 查看具体拒绝

```bash
sudo ausearch -m avc -ts recent
```

AVC 拒绝记录：

```
type=AVC msg=audit(...): avc:  denied  { mmap } for  pid=1969548 comm="httpd"
name="cd.cpython-39-x86_64-linux-gnu.so"
scontext=system_u:system_r:httpd_t:s0
tcontext=unconfined_u:object_r:httpd_sys_content_t:s0
tclass=file permissive=0
```

### 2.5 根因分析

问题的完整链路：

```
httpd_t (Apache worker 进程)
    │
    ├── [允许] 读取 httpd_sys_content_t 文件 (.py, .html)
    │
    └── [拒绝] mmap() 映射 httpd_sys_content_t 的 .so 文件
                │
                └── SELinux 类型强制：
                    httpd_sys_content_t 仅允许只读访问，
                    不包含 execmod（执行内存映射）权限
```

当 Python `import` 触发 `charset_normalizer` 加载时：

1. Python 调用 `dlopen()` 加载 `.so` 文件
2. 动态链接器调用 `mmap()` 将共享对象映射到进程地址空间
3. SELinux 检查：进程 `httpd_t` 要执行 `mmap` 操作于类型为 `httpd_sys_content_t` 的文件
4. 策略中没有 `allow httpd_t httpd_sys_content_t:file mmap` 规则
5. mmap 失败 -- `failed to map segment from shared object`

**关键点**：Apache 有权**读取**这个 .so 文件（DAC 和 MAC 都放行），但无权将其**映射为可执行内存**。这是一个比"文件读取"更细粒度的权限问题，普通的 `ls -la` 检查看不出来。

---

## 第三部分：解决方案

### 3.1 核心修复：httpd_unified

经过逐个布尔值测试，确认**只有 `httpd_unified` 是必需项**：

```bash
# 只开这一个就能解决 .so 加载问题
sudo setsebool -P httpd_unified 1
sudo systemctl restart httpd
```

验证实验：

| 组合 | 结果 |
|------|------|
| `httpd_execmem 1` 单独开启 | 仍然 500 错误 |
| `httpd_can_network_connect 1` 单独开启 | 仍然 500 错误 |
| `httpd_unified 1` 开启 | 正常访问 |

**`httpd_execmem` 单独不够**，因为 `httpd_unified` 不仅包含 execmem，还涉及 execmod 和执行内存映射等多项权限，这些是 mod_wsgi 加载 Python C 扩展所需的。

### 3.2 功能性补充

以下布尔值按需开启，与 .so 加载问题无关，但影响应用功能：

```bash
# Flask 应用使用 requests 库请求外部 URL 时需要
sudo setsebool -P httpd_can_network_connect 1

# 应用连接 MySQL/PostgreSQL 时需要（本应用不需要）
# sudo setsebool -P httpd_can_network_connect_db 1
```

| 布尔值 | 解决什么问题 | 是否必需 |
|--------|-------------|---------|
| `httpd_unified` | Python C 扩展 .so 文件 mmap 被拒 | **必需** |
| `httpd_can_network_connect` | Flask 应用向外发起 HTTP 请求被拒 | 按需 |
| `httpd_can_network_connect_db` | 应用连接远程数据库被拒 | 按需 |

本案例中，`httpd_can_network_connect_db` 最终关掉了（`setsebool -P httpd_can_network_connect_db 0`），因为应用不需要连接数据库，只保留 `httpd_can_network_connect 1` 用于向外发起 HTTP 请求。

### 3.3 验证修复

```bash
sudo systemctl restart httpd
curl http://localhost/
# 返回 200 OK，应用正常响应
```

---

## 第四部分：附加问题 -- __pycache__ 写入被拒

### 4.1 发现问题

应用虽然能正常运行，但再次执行 `ausearch` 发现仍有 AVC 拒绝记录：

```bash
sudo ausearch -m avc -ts recent
```

```
type=AVC msg=audit(...): avc:  denied  { write } for  pid=1996242 comm="httpd"
name="__pycache__"
scontext=system_u:system_r:httpd_t:s0
tcontext=unconfined_u:object_r:httpd_sys_content_t:s0
tclass=dir permissive=0
```

### 4.2 根因

Python 运行时会自动创建 `__pycache__/` 目录并写入 `.pyc` 字节码缓存文件。但 `httpd_sys_content_t` 类型仅允许**只读**访问，Apache 进程无权向该目录写入。

这个拒绝不会导致 500 错误（Python 写入失败会静默跳过），但会产生以下影响：
- 每次请求都重新编译 .py 文件（性能轻微下降）
- SELinux 审计日志被大量写入拒绝刷屏

### 4.3 方案 A：代码层面禁用字节码缓存（推荐）

在 `wsgi.py` 文件**最顶部**、所有其他 import 之前添加：

```python
import sys
sys.dont_write_bytecode = True
```

> [!NOTE] 必须放在 `from app import app` 之前，否则无效。用 `echo ... >> wsgi.py` 追加到文件末尾是常见错误——追加到 import 之后不会生效。

完整的 wsgi.py 示例：

```python
import sys
# 禁止 Python 写入 .pyc 字节码缓存，避免 SELinux 写入拒绝
# 注意：必须在所有其他 import 之前设置
sys.dont_write_bytecode = True

import os

sys.path.insert(0, '/var/www/security-header-checker')
from app import app as application
```

或在 Apache 配置中设置环境变量：

```apache
<VirtualHost *:80>
    # ... 其他配置 ...
    SetEnv PYTHONDONTWRITEBYTECODE 1
</VirtualHost>
```

优点：不修改 SELinux 策略，保持最小权限；代码即文档。

### 4.4 方案 B：SELinux 层面放行（备选）

```bash
# 将 __pycache__ 目录的安全上下文改为可读写
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/var/www/security-header-checker/venv/lib64/python3.9/site-packages/__pycache__(/.*)?"
sudo restorecon -R /var/www/security-header-checker/venv/lib64/python3.9/site-packages/__pycache__
```

对比：

| 方案 | 优点 | 缺点 |
|------|------|------|
| A: `dont_write_bytecode` | 不修改 SELinux 策略，保持只读安全 | 每次重启需重新编译 .py（影响极小） |
| B: `httpd_sys_rw_content_t` | 保留 .pyc 缓存性能 | 放宽 SELinux 限制，httpd 可写入该目录 |

推荐使用方案 A。如果某个目录确实需要 httpd 写入（如上传目录），则针对该目录单独使用方案 B。

---

## 第五部分：排查方法论总结

### 5.1 通用排障流程

```
Apache + mod_wsgi 返回 500 错误
    |
    +-- 1. tail -f /var/log/httpd/<site>-error.log     # 先看错误日志
    |
    +-- 2. 错误信息是 "failed to map segment from shared object"？
    |       或者 ImportError 的调用链经过 C 扩展？
    |       |
    |       是 -- 进入 SELinux 排查
    |
    +-- 3. sudo setenforce 0 && sudo systemctl restart httpd
    |       问题消失？ -- 确认是 SELinux
    |
    +-- 4. sudo setenforce 1 && sudo ausearch -m avc -ts recent
    |       根据 denied { 操作 } 选择修复：
    |       |
    |       +-- { mmap / execmod } -- setsebool httpd_unified 1
    |       +-- { read }           -- semanage fcontext / restorecon
    |       +-- { write }          -- sys.dont_write_bytecode 或 httpd_sys_rw_content_t
    |       +-- { connect }        -- setsebool httpd_can_network_connect 1
    |       +-- { name_connect }   -- setsebool httpd_can_network_connect 1（特定端口）
    |
    +-- 5. 修复后重启 httpd，curl 验证
    |
    +-- 6. 再次 ausearch -m avc -ts recent
            确认没有新的拒绝记录
```

### 5.2 关键教训

- 错误日志中的 `failed to map segment from shared object` 是 SELinux 拦截可执行内存映射的强烈信号 -- 不是文件缺失
- `httpd_sys_content_t` 是只读类型；Apache 进程的任何写入或内存执行操作都会被拒绝
- `httpd_unified 1` 是唯一解决 .so 加载问题的布尔值。`httpd_execmem` 单独开启无效——`httpd_unified` 涵盖的不仅是 execmem，还有 execmod、可执行内存映射等 Python WSGI 应用需要的多项权限
- 修复主要问题后务必再次检查 `ausearch` -- 可能存在二次拒绝（如 `__pycache__` 写入），虽然不致命但会刷屏审计日志

### 5.3 常见 httpd SELinux 布尔值速查

| 布尔值 | 适用场景 |
|--------|---------|
| `httpd_can_network_connect` | Flask/Django 应用需向外发起 HTTP 请求 |
| `httpd_can_network_connect_db` | 应用连接远程数据库 |
| `httpd_unified` | mod_wsgi 加载 Python C 扩展 .so 文件，或综合权限需求 |
| `httpd_execmem` | 单独放行可执行内存（**不足以替代 httpd_unified**，实测无效） |
| `httpd_can_sendmail` | 应用通过 sendmail 发送邮件 |
| `httpd_use_nfs` | 网站文件存放在 NFS 挂载点 |
| `httpd_use_cifs` | 网站文件存放在 CIFS/Samba 挂载点 |

查看所有与 httpd 相关的布尔值：

```bash
getsebool -a | grep httpd
```

完整的 `httpd_*` 及其他常见服务布尔值说明见 [[SELinux布尔值参考]]。

---

## 参考

- [[Apache-RHEL]] -- RHEL 系 Apache 完整参考，第 6 节覆盖基础 SELinux 注意事项
- [[SELinux]] -- SELinux 完整指南，安全上下文、布尔值、排障方法论
- [[SELinux布尔值参考]] -- `getsebool -a` 中 httpd_* 及其他常见布尔值的详细说明
- [[Web全栈项目]] -- security-header-checker 项目上下文与部署配置
- [[防火墙配置]] -- firewalld 配置参考
