# dnsx

> DNS 解析工具，批量验证域名解析、查 A/AAAA/CNAME/MX/NS 等记录
> 项目地址: https://github.com/projectdiscovery/dnsx

---

## 工作原理

向公共 DNS 服务器（默认从系统 DNS 获取）查询域名的 DNS 记录。不访问目标服务器，只查 DNS。

**合规性**：DNS 查询是互联网基础设施行为，相当于你访问网站之前浏览器自动做的域名解析。

---

## 安装

```bash
# Kali / Debian
sudo apt install dnsx

# Go 安装
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
```

---

## 基本用法

```bash
# 验证域名能否解析
echo "example.com" | dnsx

# 从文件读取
dnsx -l subs.txt

# 输出到文件
dnsx -l subs.txt -o resolved.txt

# 静默模式
dnsx -l subs.txt -silent

# 获取 A 记录（IPv4 地址）
dnsx -l subs.txt -a -resp-only -o ips.txt

# 获取 CNAME 记录
dnsx -l subs.txt -cname -o cname.txt

# 获取所有记录类型
dnsx -l subs.txt -a -aaaa -cname -mx -ns -txt
```

---

## 常用参数

| 参数 | 作用 |
|------|------|
| `-l` | 输入文件（域名列表） |
| `-o` | 输出文件 |
| `-silent` | 只输出有结果的域名 |
| `-a` | 查询 A 记录（IPv4） |
| `-aaaa` | 查询 AAAA 记录（IPv6） |
| `-cname` | 查询 CNAME 记录 |
| `-mx` | 查询邮件服务器 |
| `-ns` | 查询域名服务器 |
| `-txt` | 查询 TXT 记录 |
| `-resp` | 显示响应 IP（而非域名） |
| `-resp-only` | 只显示响应 IP |
| `-cdn` | 显示是否使用 CDN |
| `-rcode` | 显示 DNS 响应码 |
| `-t` | 并发线程数 |
| `-r` | 指定 DNS 解析服务器 |
| `-retry` | 重试次数 |

---

## 使用示例

### 基础验证

```bash
# 检查哪些子域名能解析
dnsx -l all_subs.txt -silent -o resolved.txt

# 只看 IP 地址
dnsx -l subs.txt -a -resp-only | sort -u
```

### 发现 CDN / 别名

```bash
# 看 CNAME，识别 CDN（如 Cloudflare、阿里云 CDN）
dnsx -l subs.txt -cname -silent
# www.example.com [cname: example.cdn.aliyun.com.]
```

### 指定 DNS 服务器

```bash
# 用国内 DNS（114DNS）避免被境外 DNS 影响结果
dnsx -l subs.txt -r 114.114.114.114 -silent
```

### 管道链式调用（典型流程）

```bash
# Subfinder -> dnsx -> httpx 标准三步
subfinder -d cdcas.edu.cn -silent | dnsx -silent | httpx -title -status-code -tech-detect -rl 10
```

---

## 注意事项

- **默认 DNS 超时可能较长**：大批量查询时用 `-retry 1` 减少等待
- **IPv6 可能干扰结果**：如果目标没有 IPv6，不加 `-aaaa` 能加快速度
- **CNAME 有用**：如果一个域名 CNAME 指向 `cdn.xxx.com`，说明用了 CDN，无法直接扫到真实 IP
