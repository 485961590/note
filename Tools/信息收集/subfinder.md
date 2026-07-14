# Subfinder

> 被动子域名收集工具，只查公开 API 和数据库，不向目标发送请求
> 项目地址: https://github.com/projectdiscovery/subfinder

---

## 工作原理

Subfinder 查询以下公开数据源（不碰目标服务器）：

- crt.sh — 证书透明度日志
- VirusTotal — 恶意域名库中的子域
- SecurityTrails — DNS 历史记录
- Shodan — 网络空间搜索引擎
- Chaos — ProjectDiscovery 的域名数据集
- 其他 50+ 公开 API 数据源

**合规性**：零风险，完全被动。相当于你把 crt.sh/SecurityTrails 等网站手动搜了一遍，只是自动化了。

---

## 安装

```bash
# Kali / Debian
sudo apt install subfinder

# Go 安装
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

---

## 基本用法

```bash
# 单个域名
subfinder -d example.com

# 输出到文件
subfinder -d example.com -o subs.txt

# 从文件读取多个域名
subfinder -dL domains.txt -o subs.txt

# 静默模式（只输出域名）
subfinder -d example.com -silent

# 启用所有数据源（需要配置 API key）
subfinder -d example.com -all -o subs.txt
```

---

## 常用参数

| 参数 | 作用 |
|------|------|
| `-d` | 目标域名 |
| `-dL` | 从文件读取域名列表 |
| `-o` | 输出到文件 |
| `-oJ` | JSON 格式输出（含来源信息） |
| `-silent` | 只输出发现的域名 |
| `-all` | 使用所有数据源 |
| `-timeout` | 超时时间（秒），默认 30 |
| `-t` | 并发线程数，默认 10 |
| `-rl` | 每秒请求限制 |
| `-max-time` | 最大运行时间（分钟） |

---

## 配置 API Key（推荐）

编辑 `~/.config/subfinder/provider-config.yaml`，填入各平台的 API Key 可以提高发现率：

```yaml
binaryedge:
  - 你的key
censys:
  - 你的key
chaos:
  - 你的key
securitytrails:
  - 你的key
shodan:
  - 你的key
virustotal:
  - 你的key
```

免费注册就能获取基本额度。不做也不影响使用，被动源（crt.sh）是主力。

---

## 使用示例

```bash
# 基础用法：收集所有子域名
subfinder -d cdcas.edu.cn -o cdcas_subs.txt

# 看每个子域名的来源
subfinder -d cdcas.edu.cn -oJ -silent
# 输出示例: {"host":"jw.cdcas.edu.cn","source":"crt.sh"}

# 批量收集（从文件读入多个学校域名）
subfinder -dL schools.txt -all -o all_subs.txt

# 收集 + 直接管道给 dnsx 做 DNS 验证
subfinder -d cdcas.edu.cn -silent | dnsx -silent -o resolved.txt
```

---

## 与其他工具对比

| 工具 | 类型 | 速度 | 覆盖率 |
|------|------|------|--------|
| **Subfinder** | 被动 | 快 | 高 |
| **Amass** | 被动+主动 | 慢 | 最高 |
| **Findomain** | 被动 | 最快 | 中 |
| **OneForAll** | 被动+主动 | 中 | 高（国内源多） |

如果时间充裕，Subfinder + OneForAll 组合使用，各自覆盖对方遗漏的数据源。
