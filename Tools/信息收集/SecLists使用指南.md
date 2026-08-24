# SecLists 快速定位使用指南

> 原则：**不要一上来就用大字典**。先用小而精的字典跑通流程、确认有回显，再逐步换大字典。SecLists 里的字典按 `小 → 大` 命名（如 `common.txt` < `big.txt` < `huge`），文件名里带 ` raft ` 的来自历史爬虫数据，质量高但量大。

## 一、目录结构速览

| 目录                                   | 里面是什么                                                                                  | 什么时候用                        |
| ------------------------------------ | -------------------------------------------------------------------------------------- | ---------------------------- |
| `Discovery/Web-Content/`             | Web 目录/文件名字典                                                                           | 目录扫描（dirsearch/ffuf/dirb）    |
| `Discovery/DNS/`                     | 子域名字典                                                                                  | 子域名枚举                        |
| `Discovery/File-Upload/`             | 上传文件名相关                                                                                | 文件上传绕过测试                     |
| `Passwords/`                         | 密码字典（含 `Common-Credentials`、`Leaked-Databases`、`Default-Credentials`、`Cracked-Hashes`） | 爆破密码、撞库                      |
| `Usernames/`                         | 用户名字典                                                                                  | 枚举用户名、爆破账号                   |
| `Fuzzing/`                           | LFI/RFI、命令注入、SQL 注入、SSRF、XXE 等 payload                                                 | 漏洞 payload 注入测试              |
| `Payloads/`                          | 各类漏洞利用 payload（绕 WAF、XSS、注入变形等）                                                        | Burp Intruder / 手工构造 payload |
| `API/`                               | API 路径与参数名（含 GraphQL、Swagger 暴露）                                                       | API 接口 fuzz                  |
| `Miscellaneous/Wordlist-Generators/` | 生成器（按姓名生成用户名等）                                                                         | 定向生成字典                       |
| `Web-Shells/`                        | WebShell 样本                                                                            | 上传漏洞验证（仅授权测试）                |
| `Pattern-Matching/`                  | 敏感信息匹配正则                                                                               | 数据泄露筛查（如 trufflehog 配套）      |

---

## 二、按场景查字典（核心部分）

### 场景 1：Web 目录/文件扫描（最常用）

| 字典 | 位置 | 说明 |
|---|---|---|
| `common.txt` | Discovery/Web-Content/ | **默认首选**，约 4600 条，快而准，= dirb 自带字典 |
| `raft-medium-directories.txt` | 同上 | 次选，质量高，约 1 万+ |
| `big.txt` | 同上 | common 跑完没收获再上，2 万条 |
| `quickhits.txt` | 同上 | 专扫"已知敏感路径"（备份、git、配置泄露），**必跑** |
| `angular-templates.txt` / `swagger.txt` / `graphql.txt` | 同上 | 前端框架 / 接口文档暴露 |
| `Logins.txt` | 同上 | 扫登录页入口 |

```bash
# dirsearch 示例
dirsearch -u https://target.com -w SecLists/Discovery/Web-Content/common.txt
# ffuf 示例（更快）
ffuf -u https://target.com/FUZZ -w SecLists/Discovery/Web-Content/common.txt -mc 200,301,302,403
```

### 场景 2：子域名枚举

| 字典 | 位置 | 说明 |
|---|---|---|
| `subdomains-top1million-110000.txt` | Discovery/DNS/ | **首选**，11 万条，够用 |
| `subdomains-top1million-5000.txt` | 同上 | 快速探测用小版 |
| `deepmagic.com-prefixes-top500.txt` | 同上 | 纯数字/IP 段场景 |

```bash
ffuf -u https://FUZZ.target.com -w SecLists/Discovery/DNS/subdomains-top1million-110000.txt -mc 200
# 或用 subfinder + 子域字典兜底被动枚举
```

### 场景 3：密码爆破 / 弱口令

| 字典 | 位置 | 说明 |
|---|---|---|
| `10-million-password-list-top-100/1000/10000/100000.txt` | Passwords/Common-Credentials/ | **首选**，按量级选，先 100 再 1000 |
| `2020-200_most_used_passwords.txt` | 同上 | 超快粗扫 |
| `darkweb2017-top10000.txt` | 同上 | 暗网泄露高频密码 |
| `Probable-v2-top12000.txt` | Passwords/ | 英文姓名组合密码 |
| `Chinese passwords.txt` 等 | Passwords/ | **国内目标优先用中文常见密码**（`Passwords/` 根目录及各国语言子目录） |
| `Default-Credentials/` | Passwords/ | 各厂商设备/中间件默认口令（tomcat、rabbitmq、路由器等），打设备必查 |
| `Leaked-Databases/` | Passwords/ | 历史泄露库（rockyou 等），撞库/哈希爆破用 |

```bash
# hydra 爆破 SSH
hydra -L Usernames/top-usernames-shortlist.txt -P Passwords/Common-Credentials/10-million-password-list-top-1000.txt 192.168.1.10 ssh
```

### 场景 4：用户名枚举

| 字典 | 位置 | 说明 |
|---|---|---|
| `top-usernames-shortlist.txt` | Usernames/ | **首选**，50 条高频用户名 |
| `names.mtx.txt` / `httparchive.txt` | 同上 | 更大规模 |
| `Miscellaneous/Wordlist-Generators/` | — | 知道员工姓名规律时用生成器定制（国内姓名可用自身脚本生成拼音组合） |

### 场景 5：API 接口测试

| 字典 | 位置 | 说明 |
|---|---|---|
| `api/paths.txt` | API/ | API 路径扫描 |
| `burp-parameter-names.txt` | Discovery/Web-Content/ | 参数名 fuzz |
| `objects.json` / `swagger.txt` | API/、Web-Content/ | 接口对象与文档泄露 |
| `GraphQL/` | API/ | GraphQL 内省/字段枚举 |

### 场景 6：漏洞 Payload 注入（配合 Burp Intruder / ffuf）

| 需求 | 字典位置 |
|---|---|
| LFI 本地文件包含 | `Fuzzing/LFI/`（含 `LFI-Jhaddix.txt` 全量版） |
| 命令注入 | `Fuzzing/Command-Injection.txt` |
| SQL 注入 | `Fuzzing/SQLi/`、`Payloads/SQL-Injection/`（绕 WAF 变形在 `Payloads/.../Generic-Bypass`） |
| XSS | `Payloads/XSS/`（含 filter bypass） |
| SSRF | `Fuzzing/SSRF.txt` |
| XXE | `Payloads/XXE/` |
| SSTI 模板注入 | `Fuzzing/SSTI/` |
| 文件上传后缀绕过 | `Discovery/File-Upload/`（含双写、大小写、`::$DATA` 等变体） |
| CORS / 开放重定向 | `Fuzzing/*cors*`、`Open-redirect/` |

### 场景 7：HTTP 请求走私 / 头部 fuzz

`Fuzzing/HTTP-requests/`、`Fuzzing/http-chars.txt` 等按需取用。

---

## 三、推荐"三级递进"节奏

1. **快扫**：`common.txt` + `top-usernames-shortlist.txt` + `top-100 密码` —— 几分钟出结果
2. **标准**：`raft-medium` + `subdomains-110000` + `top-1000 密码` —— 常规交付标配
3. **深挖**：`big.txt`/`quickhits.txt` + 泄露库 + 定制生成字典 —— 前两级有信号或重要目标才上

## 四、防迷路技巧

- 记不住路径时直接 `find` / `everything` 搜文件名关键词（如 `lfi`、`top1000`、`chinese`）
- 字典选择口诀：**Web 目录找 Web-Content，爆破密码找 Passwords，payload 找 Fuzzing/Payloads，其他一切找 Discovery**
- 中文目标记得翻 `Passwords/` 下的中文与各国语言字典，命中率远高于英文通用字典
