# 渗透测试 / Web安全 实习面试资源整理

> 整理日期：2025-06-23
> 面向人群：信息安全专业大四学生，准备渗透测试/Web安全方向实习面试

---

## 目录

1. [GitHub 面试题库](渗透测试_Web安全_实习面试资源整理.md#一github-面试题库)
2. [大厂面经 & 博客文章](渗透测试_Web安全_实习面试资源整理.md#二大厂面经--博客文章)
3. [实习面试高频考点](渗透测试_Web安全_实习面试资源整理.md#三实习面试高频考点)
4. [配套学习 & 练习资源](渗透测试_Web安全_实习面试资源整理.md#四配套学习--练习资源)
5. [建议学习路线](渗透测试_Web安全_实习面试资源整理.md#五建议学习路线)
6. [拓展方向](渗透测试_Web安全_实习面试资源整理.md#六拓展方向)

---

## 一、GitHub 面试题库

### 1. evilAdan0s/RedTeamInterview [首推]
- 链接：https://github.com/evilAdan0s/RedTeamInterview
- 特点：红队面试题合集，分类极全，持续更新至 2025 年，可作为查漏补缺 checklist

| 分类 | 涵盖内容 |
|------|----------|
| 渗透测试 | SQL 注入绕过、SSRF 利用、WAF 绕过、文件上传绕过、JWT 漏洞、APP 渗透、小程序反编译、XSS 利用、同源策略绕过 |
| 攻防演练 | 资产收集、C2 隐藏、MSSQL 命令执行、代理工具、权限维持、Bypass UAC、钓鱼思路、OPSEC、凭证抓取 |
| 内网渗透 | Kerberos 认证、黄金/白银票据、委派利用、NoPAC、Zerologon、ADCS、域间信任、各种土豆提权 |
| Java 安全 | 反射、JNDI 注入、反序列化（7u21/8u20）、Shiro、Log4j2、Fastjson、内存马、回显思路 |
| 免杀/EDR | 反沙箱、反虚拟机、Shellcode Loader、360 QVM 绕过、syscall、AMSI 绕过、Sleepmask、BYOVD |

### 2. just0rg/Security-Interview
- 链接：https://github.com/just0rg/Security-Interview
- 特点：涵盖 Web 攻防、Java 攻防、企业安全、内网/域、提权、免杀，**每个知识点都附带详细答案**

精选知识点示例：
- MSSQL 各种拿 Shell 方式（sp_oacreate、CLR 提权、沙盒提权）
- Redis 未授权 -> 主从复制 GetShell 原理
- 分块传输绕 WAF 原理
- 文件上传绕 WAF 方式汇总
- HTTP-Only 绕过技术
- CSRF_TOKEN 原理与绕过

### 3. doudou6760/Sec-Interview
- 链接：https://github.com/doudou6760/Sec-Interview
- 特点：从网络公开资料收集的面试题大合集，包含**多家公司真实面经**

内含资料：
- 360 面经、阿里面经、腾讯 IEG/TEG 面经
- 华为、百度、滴滴出行、蘑菇街等面经
- 渗透测试工程师面试题大全.pdf
- 网络安全题库汇总 1000 题.pdf
- OWASP Top 10 相关题目

### 4. cvestone/Pentest_Interview
- 链接：https://github.com/cvestone/Pentest_Interview
- 特点：渗透测试/安全面试经验整理，含 HR 面问题、技术面分享、实际面试记录

### 5. Grinlcm/offensiveinterview
- 链接：https://github.com/Grinlcm/offensiveinterview
- 特点：翻译自国外 @WebBreacher 的红队面试题，按题型分为开放式问题、知识点问题、场景题

### 6. jassics/security-interview-questions（英文）
- 链接：https://github.com/jassics/security-interview-questions
- 特点：覆盖 AppSec、Pentesting、Cloud Security、DevSecOps、Network Security 等多方向

### 7. Devinterview-io/web-security-interview-questions（英文）
- 链接：https://github.com/Devinterview-io/web-security-interview-questions
- 特点：2025 年更新，130+ stars，Web 安全面试问答精编

### 8. InfoSecWarrior/Penetration-Testing-Interview-Questions（英文）
- 链接：https://github.com/InfoSecWarrior/Penetration-Testing-Interview-Questions
- 特点：渗透测试面试题库，涵盖 InfoSec、网络安全、Web 安全、API 安全

### 9. gracenolan/Notes（英文）
- 链接：https://github.com/gracenolan/Notes
- 特点：Google 安全工程岗位面试真实笔记，包含 Web 安全、云安全、密码学、恶意代码分析、漏洞开发、应急响应、**编程与算法**（作者强调这是候选人最容易挂的环节）

---

## 二、大厂面经 & 博客文章

### 知乎专栏
- [2024届校招网络安全岗位 & 面试题（字节、百度、腾讯、美团等大厂）](https://zhuanlan.zhihu.com/p/719141707)
  - 包含 30+ 大厂面试复盘：字节跳动、阿里云、腾讯科恩/玄武实验室、深信服、长亭、360、快手、蚂蚁、美团、京东、百度、华为、B站、Shopee
  - 题目覆盖：渗透流程、CDN 绕过、SQL 注入绕过、Fastjson、Shiro、内网渗透、域控攻击等

### 博客园
- [24年网络安全大厂原来都面试这些，附大厂面经下载链接](https://www.cnblogs.com/cybersecuritystools/p/18404559)
  - 涵盖虾皮、腾讯、SHEIN、字节最新面经
  - 新增考点：JWT 安全、云安全 AK 治理、SAST/SCA 工具原理、AI 安全（LLM Prompt 注入）、SDL 流程、API 安全治理

### CodeSec
- [2024面试经验分享，90+套最新安全大厂面试经（附HW面经及回答思路）](http://cn-sec.com/archives/2577645.html)
  - 30 套完整面经 + HW 面试思路，题目极其详细

### CSDN 系列（2025 年更新）
- [2025年渗透测试面试题总结-拷打题库13（题目+回答）](https://blog.csdn.net/m0_62828084/article/details/147364682)
- [2025年渗透测试面试题总结-104（题目+回答）](https://blog.csdn.net/m0_62828084/article/details/152415578)
- [2025年渗透测试面试题总结-250（题目+回答）](https://blog.csdn.net/m0_62828084/article/details/154948754)
- [2025年渗透测试面试题总结-360面经（题目+回答）](https://blog.csdn.net/m0_62828084/article/details/147975983)
- [渗透测试面试题汇总（附答题解析+配套资料）](https://blog.csdn.net/A1_3_9_7/article/details/147637529)

### 其他
- [2025年渗透测试面试题总结-某战队红队实习面经（附回答）](https://www.e-com-net.com/article/1920143902963200000.htm)
  - 红队方向，涵盖 Web 安全、内网渗透、CS 特征隐藏、免杀、隧道搭建、权限维持

---

## 三、实习面试高频考点

> 以下题目在多个资源中反复出现，是面试官最爱问的方向。

### 渗透测试基础

1. **"讲一下你的渗透测试流程，从信息收集到出具报告"**
   - 信息收集 -> 漏洞探测 -> 漏洞利用 -> 权限提升 -> 横向移动 -> 权限维持 -> 痕迹清理

2. **"如何绕过 CDN 找到真实 IP？"**
   - 子域名爆破、DNS 历史记录、邮件头分析、全球 Ping、SSL 证书搜索、Shodan/ZoomEye/Fofa 搜索

3. **"如何判断网站是否使用 CDN？有哪些绕过手法？"**

### Web 安全

4. **"SQL 注入如何绕过 WAF？逗号被过滤怎么办？"**
   - 分块传输、内联注释、参数污染、编码绕过、等价替换（如 substr 替代 mid）

5. **"CSRF 和 SSRF 的区别，分别如何利用？如何防御？"**

6. **"XSS 有哪些类型？如何绕过 HttpOnly 获取 Cookie？"**

7. **"文件上传有哪些绕过方式？"**
   - 前端绕过、MIME 类型绕过、扩展名绕过（大小写/双写/特殊后缀）、内容检测绕过、条件竞争、.htaccess/.user.ini

8. **"XXE 漏洞原理、利用方式和防御"**

9. **"SSRF 的利用手法有哪些？如何绕过过滤？如何攻击内网？"**

### 认证与协议

10. **"Kerberos 认证流程，黄金票据和白银票据的区别"**
    - AS-REQ/AS-REP、TGS-REQ/TGS-REP、AP-REQ/AP-REP 流程
    - 黄金票据（伪造 TGT）、白银票据（伪造 ST）、区别与利用条件

11. **"JWT 攻击面有哪些？"**
    - alg:none 绕过、RS256 -> HS256 密钥混淆、kid 注入、JKU/JWK 头注入、暴力破解密钥

12. **"NTLM 认证流程，NTLM Relay 攻击原理"**

### Java / 框架安全

13. **"Shiro 550 和 721 的原理和利用链"**
    - 550：rememberMe 反序列化（AES 密钥硬编码）
    - 721：使用随机密钥后的 Padding Oracle 攻击

14. **"Log4j2 (CVE-2021-44228) 漏洞原理和绕过方式"**
    - JNDI 注入、lookup 递归解析、高版本绕过、WAF 绕过

15. **"Fastjson 反序列化原理和利用"**
    - AutoType 机制、各版本 bypass 思路

16. **"内存马是什么？有哪些类型？如何查杀？"**
    - Filter 型、Servlet 型、Listener 型、Valve 型（Tomcat）

### 内网渗透

17. **"拿到 WebShell 后如何在内网横向移动？"**
    - 信息收集（ipconfig、netstat、arp、域信息）、凭证抓取（mimikatz）、票据传递、哈希传递、委派攻击

18. **"Windows 提权常见手法"**
    - 内核漏洞、服务提权、DLL 劫持、AlwaysInstallElevated、Token 窃取、土豆系列

19. **"Linux 提权常见手法"**
    - SUID 提权、sudo 配置不当、Cron 任务劫持、内核漏洞、Docker 逃逸、Capabilities 滥用

20. **"域渗透中 DCSync 攻击原理"**

### 免杀与对抗

21. **"免杀的基本思路"**
    - 静态免杀（代码混淆、加密、分离加载）
    - 动态免杀（反沙箱、反调试、API 调用方式变化）
    - 行为免杀（进程注入方式、内存申请方式）

22. **"AMSI 是什么？如何绕过？"**

---

## 四、配套学习 & 练习资源

### 在线靶场（动手实践）

| 平台 | 链接 | 说明 |
|------|------|------|
| PortSwigger Web Security Academy | https://portswigger.net/web-security | 免费，覆盖所有 OWASP 类别，带详细教程 |
| HackTheBox | https://www.hackthebox.com/ | 渗透测试综合靶场 |
| TryHackMe | https://tryhackme.com/ | 由浅入深的安全学习平台 |
| Bugcrowd University | https://www.bugcrowd.com/hackers/bugcrowd-university/ | 漏洞挖掘培训 |
| PentesterLab | https://pentesterlab.com/ | Web 安全专项练习 |

### 工具与 Payload 参考

| 资源 | 链接 | 说明 |
|------|------|------|
| PayloadsAllTheThings | https://github.com/swisskyrepo/PayloadsAllTheThings | 各类漏洞 Payload 大全 |
| HackTricks | https://book.hacktricks.xyz/ | Web/Pentest/云安全 方法论手册 |
| SecLists | https://github.com/danielmiessler/SecLists | 渗透测试字典合集 |
| awesome-web-security | https://github.com/layzhi/awesome-web-security | Web 安全资源精选列表 |
| Sec-88 | https://github.com/h0tak88r/Sec-88 | 安全笔记、方法论、资源与技巧（227+ stars） |

### 漏洞分析

| 资源 | 链接 | 说明 |
|------|------|------|
| 奇安信攻防社区 | https://forum.butian.net/ | 大量漏洞分析文章 |
| 先知社区 | https://xz.aliyun.com/ | 阿里云安全社区，漏洞分析精华 |
| 安全客 | https://www.anquanke.com/ | 安全资讯与漏洞分析 |
| 嘶吼 | https://www.4hou.com/ | 安全技术文章 |
| freebuf | https://www.freebuf.com/ | 安全社区，面经 & 技术文章 |

---

## 五、建议学习路线

### 第一阶段：构建知识框架（2-3 周）
1. 通读 [evilAdan0s/RedTeamInterview](https://github.com/evilAdan0s/RedTeamInterview)，当作查漏补缺 checklist
2. 对着 [just0rg/Security-Interview](https://github.com/just0rg/Security-Interview) 逐一理解答案
3. 把看不懂的名词和概念记下来，逐个查资料搞懂

### 第二阶段：深入理解原理（2-3 周）
4. 在 [PortSwigger Web Security Academy](https://portswigger.net/web-security) 上动手做靶场
5. 阅读 [HackTricks](https://book.hacktricks.xyz/) 对应章节，理解攻击面
6. 对着高频面试题，尝试用自己的话把原理讲清楚

### 第三阶段：面经刷题（1-2 周）
7. 看 [doudou6760/Sec-Interview](https://github.com/doudou6760/Sec-Interview) 和知乎面经了解各家风格
8. 对照 CSDN 2025 面经系列，模拟练习答题话术
9. 准备 2-3 个自己亲手复现过的漏洞案例，面试时能详细讲出原理

### 第四阶段：投简历前冲刺（1 周）
10. 准备自我介绍（突出实践项目/漏洞挖掘经历）
11. 准备 1-2 个反问面试官的问题（体现你对岗位的思考）
12. 复习 HR 面常见问题（职业规划、优缺点、期望薪资）

### 时间分配建议

| 阶段 | 时长 | 重点 |
|------|------|------|
| 知识框架 | 2-3 周 | 广度优先，覆盖所有高频考点 |
| 深入理解 | 2-3 周 | 动手实操，能讲清楚原理 |
| 面经刷题 | 1-2 周 | 熟悉面试风格，练习答题 |
| 模拟冲刺 | 1 周 | 模拟面试，打磨表达 |

---

## 六、拓展方向

> 以下是大厂面试的新趋势，建议根据目标岗位选择性准备：

| 方向 | 关键考点 |
|------|----------|
| **云安全** | AK/SK 泄露利用、S3 桶权限、K8s Pod 逃逸、容器逃逸、EC2 元数据服务攻击 |
| **AI 安全** | LLM Prompt 注入、训练数据投毒、模型窃取、AI 应用 OWASP Top 10 |
| **DevSecOps** | SAST/IAST/SCA 工具原理、Semgrep/CodeQL 规则编写、CI/CD 管道安全 |
| **代码审计** | 污点分析、常见危险函数、Java/PHP/Python 代码审计技巧 |
| **业务逻辑漏洞** | 越权、支付逻辑、验证码爆破、并发竞争、优惠券漏洞 |
| **供应链安全** | 依赖库投毒、镜像投毒、开源组件漏洞、SBOM |

---

## 附录：面试提醒

1. **不要死记硬背**：面试官更看重你是否真正理解原理，而不是背答案。你能把一个漏洞的原理从头到尾讲清楚，比记住十个漏洞的名字更有说服力。

2. **准备实战案例**：如果你挖过 SRC 漏洞、打过 CTF、复现过 CVE，一定要写进简历并提前准备好讲解话术。

3. **代码能力不要忽视**：Google、腾讯等大厂的安全面试会考编程题。建议用 Python 刷一些安全相关的编程练习（如写一个端口扫描器、SQL 注入检测脚本）。

4. **简历要有亮点**：不要只写"熟悉 OWASP Top 10"，要写"独立挖掘某厂商 SRC XX 个漏洞"、"CVE-XXXX-XXXX 复现与分析"、"XX CTF 排名"。

5. **自信但诚实**：不会的问题坦诚说不会，但可以补充说"我的理解是..."或者"我猜测可能跟...有关"，展示你的思考过程。

---

> 最后更新：2025-06-23
> 本文档将持续更新。如果你发现新的优质资源，欢迎补充。
