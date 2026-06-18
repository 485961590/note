# FOFA

FOFA（**F**orget **O**ther **F**uzzy **A**ppliances）是一款网络空间测绘搜索引擎，通过扫描全球互联网资产，用特定语法快速精准地定位目标。

## 一、搜索字段速查

| 字段 | 说明 | 示例 |
|------|------|------|
| `domain` | 域名（含子域名） | `domain="fofa.info"` |
| `host` | 匹配域名的所有资产 | `host=".gov.cn"` |
| `ip` | IP 或 CIDR 网段 | `ip="192.168.1.1/24"` |
| `port` | 端口 | `port="8080"` |
| `protocol` | 应用层协议 | `protocol="ftp"` |
| `country` | 国家代码 | `country="CN"` |
| `region` | 省/州 | `region="Zhejiang"` |
| `city` | 城市 | `city="Hangzhou"` |
| `os` | 操作系统 | `os="windows"` |
| `title` | 网页标题 | `title="后台登录"` |
| `body` | 网页正文 | `body="Powered by WordPress"` |
| `header` | HTTP 响应头 | `header="nginx"` |
| `server` | 服务端软件（等同 `header="server"`） | `server="Microsoft-IIS/10"` |
| `banner` | 端口 banner 信息 | `banner="mysql"` |
| `cert` | SSL 证书信息 | `cert="google.com"` |
| `icon_hash` | 网站图标 mmh3 Hash | `icon_hash="-247388890"` |
| `status_code` | HTTP 状态码 | `status_code="403"` |
| `is_domain` | 是否域名资产 | `is_domain=true` |
| `is_ipv6` | 是否 IPv6 资产 | `is_ipv6=true` |

## 二、逻辑运算符

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `&&` | 与（同时满足） | `title="login" && body="admin"` |
| `\|\|` | 或（满足其一） | `server="nginx" \|\| server="apache"` |
| `!=` | 非（排除条件） | `city!="Beijing"` |
| `=` | 匹配（需双引号） | `domain="example.com"` |
| `==` | 全等匹配（需双引号） | `domain=="example.com"` |
| `~=` | 正则匹配 | `domain~=".*\.example\.com"` |

## 三、高级语法

### 网络与时间

| 语法 | 说明 | 示例 |
|------|------|------|
| `cidr` | CIDR 地址块查询 | `cidr="192.168.1.1/24"` |
| `ip_range` | IP 范围查询 | `ip_range="192.168.1.1,192.168.2.255"` |
| `after` | 在指定时间之后更新 | `after="2023-01-01"` |
| `before` | 在指定时间之前更新 | `before="2023-12-31"` |

示例：`domain="fofa.info" && after="2023-01-01" && before="2023-12-31"`

## 四、实用示例

### 资产发现

```fofa
// 某公司的所有 Web 服务
domain="abc.com" && port="443"

// 使用 WordPress 的网站
body="wp-content" && title="Welcome to WordPress"

// 更精准：通过 WordPress 图标 Hash
icon_hash="-1472471659"
```

### 漏洞影响评估

```fofa
// 暴露在公网的 Jenkins 管理后台
title="Jenkins" && port="8080" && country="CN"

// Log4j 漏洞组件
header="x-powered-by" && header~="log4j"
```

### 网络空间测绘

```fofa
// 中国境内无密码的 Redis 服务
port="6379" && country="CN" && banner="redis"

// 使用 Let's Encrypt 证书的域名
cert="Let's Encrypt"
```

### 图标 Hash 高级用法

计算目标网站 favicon 的 mmh3 Hash 值，可找到互联网上所有使用相同图标的系统，无视 IP、域名、标题变化。

```fofa
// 某 OA 系统的图标 Hash
icon_hash="-247388890"
```

### 排除干扰

```fofa
// 排除北京的登录页面
title="登录" && body="admin" && city!="Beijing"
```

## 五、注意事项

1. **精确匹配**：使用 `=` 或 `==` 时，值用**双引号**包裹；模糊搜索可直接写值但不推荐
2. **权限限制**：非会员搜索结果数量受限，高级语法和完整数据需会员
3. **合法使用**：务必在合法授权下进行安全测试和资产梳理
4. **官方文档**：[https://fofa.info/static_pages/help](https://fofa.info/static_pages/help)
