# DNS

**DNS 是互联网的"电话簿"**。将人类可读的域名（如 `www.google.com`）转换为机器可读的 IP 地址（如 `142.251.42.206`）。

## DNS 记录类型速查

| 类型      | 用途                 | 示例                                                 |
| ------- | ------------------ | -------------------------------------------------- |
| `A`     | 域名 → IPv4          | `example.com → 93.184.216.34`                      |
| `AAAA`  | 域名 → IPv6          | `example.com → 2606:2800:220:1:248:1893:25c8:1946` |
| `CNAME` | 别名（域名 → 域名）        | `www.example.com → example.com`                    |
| `MX`    | 邮件服务器              | `example.com → mail.example.com (priority 10)`     |
| `NS`    | 权威 DNS 服务器         | `example.com → ns1.example.com`                    |
| `TXT`   | 文本记录（SPF/DMARC/验证） | `v=spf1 mx -all`                                   |
| `SOA`   | 域的管理信息             | 主 DNS 服务器、管理员邮箱、序列号等                               |
| `PTR`   | IP → 域名（反向解析）      | `34.216.184.93 → example.com`                      |
| `SRV`   | 服务定位               | `_sip._tcp.example.com → sipserver:5060`           |

## DNS 解析流程

```
用户 → 浏览器缓存 → 系统 DNS 缓存 / hosts 文件
                ↓ (未命中)
        递归解析器 (ISP / 8.8.8.8)
                ↓
        根域名服务器 (.)
                ↓
        顶级域服务器 (.com)
                ↓
        权威 DNS 服务器 (example.com)
                ↓
        返回 IP 地址
```

### 两种解析角色

| 角色 | 说明 |
|------|------|
| **递归解析器（Recursive Resolver）** | 替你完成全部查询，如 ISP DNS、`8.8.8.8` |
| **权威服务器（Authoritative Server）** | 存储域名的原始解析记录，提供最终答案 |

---

## DNS 安全缺陷 — 为什么 DNS 不安全？

### 1. 原始设计缺陷

- **明文传输**：传统 DNS（UDP/TCP 53 端口）无加密，任何中间节点可看到查询内容
- **无认证**：客户端无法验证响应是否来自合法服务器，攻击者可轻易伪造

### 2. 过度信任

几乎所有网络活动都始于 DNS 查询。DNS 被劫持 → 后续通信全部落入攻击者控制。

---

## 主要攻击手段

### 1. DNS 欺骗 / 缓存投毒（Cache Poisoning）

**原理**：向递归 DNS 服务器注入伪造记录，使其缓存错误的 IP。

**后果**：
- 将用户引向钓鱼网站
- 分发恶意软件
- 实施中间人攻击

### 2. DNS 劫持（DNS Hijacking）

**原理**：直接修改设备/路由器的 DNS 服务器设置，指向恶意 DNS。

**实现方式**：
- **恶意软件**：修改本机 `/etc/resolv.conf` 或 Windows DNS 设置
- **路由器攻击**：利用弱口令修改 DHCP 下发的 DNS
- **ISP/国家劫持**：在骨干网层面劫持 DNS 请求

### 3. DNS 隧道（DNS Tunneling）

**原理**：将其他协议数据编码在 DNS 查询中，利用防火墙对 UDP 53 的宽松策略穿透内网。

**用途**：
- 绕过网络安全控制，从内网窃取数据
- C&C 远程控制僵尸网络

### 4. DNS 放大攻击（Amplification Attack）

**原理**：伪造受害者 IP 发送小型 DNS 查询，利用响应包远大于请求包（可达 50 倍以上）的特性发起 DDoS。

**关键**：利用开放的递归 DNS 服务器作为放大器。

### 5. 域名抢注（Domain Hijacking）

**原理**：通过社工/窃取邮箱获取域名注册商账户权限，非法转移域名。

---

## 防护措施

### DNSSEC（DNS Security Extensions）

| 方面 | 说明 |
|------|------|
| **目的** | 验证数据**真实性和完整性**，防欺骗和投毒 |
| **原理** | 对 DNS 记录进行数字签名，递归服务器可层层验证 |
| **局限性** | **不提供加密**，查询内容仍是明文；部署复杂 |

### DoT（DNS over TLS）& DoH（DNS over HTTPS）

| | DoT | DoH |
|------|-----|------|
| **端口** | TCP 853 | TCP 443 |
| **加密方式** | TLS | HTTPS |
| **特点** | 独立流量，易于管控 | 混在 Web 流量中，难以封锁 |
| **隐私** | 网络管理员仍可知 DNS 目标 | 与普通 HTTPS 无异，隐私更强 |

### 纵深防御总结

| 角色 | 措施 |
|------|------|
| **普通用户** | 使用支持 DoH/DoT 的公共 DNS（`1.1.1.1` / `8.8.8.8`），保持系统更新 |
| **网站管理员** | 部署 DNSSEC，监控 WHOIS 和 DNS 记录变更 |
| **网络架构师** | 限制开放的递归 DNS，对 DNS 流量进行异常检测（大量 NXDOMAIN、隧道特征等） |

---

## 常用命令

```bash
# 查询 A 记录
nslookup example.com
dig example.com A

# 指定 DNS 服务器查询
dig @8.8.8.8 example.com

# 查询 MX 记录
dig example.com MX

# 反向解析
dig -x 8.8.8.8

# DNS 追踪（查看完整解析路径）
dig +trace example.com

# 测试 DoH
curl -H "Accept: application/dns-json" "https://cloudflare-dns.com/dns-query?name=example.com&type=A"

# 查看本地 DNS 缓存（Windows）
ipconfig /displaydns
```

> **DNS 安全是纵深防御体系中不可或缺的一环。保护 DNS，就是保护所有网络通信的"第一公里"。**
