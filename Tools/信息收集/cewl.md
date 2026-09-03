# CeWL 网站词表生成实用指南

CeWL（Custom Word List generator）是一个基于 Ruby 的网站爬取和词表生成工具。它会抓取授权站点页面中的可见单词，也可以提取页面元数据和邮箱地址，适合生成与目标业务、产品、项目和组织名称相关的定制词表。

CeWL 的核心输出是词表，不是漏洞扫描结果。它不会判断密码是否正确，也不负责端口扫描、目录扫描或漏洞利用。页面内容越丰富，生成的词表通常越有针对性；站点内容较少时，结果也会比较少。

以下命令只适用于自己控制的站点、靶场或明确授权的测试目标。抓取站点会产生 HTTP 请求，开启更深爬取、跨站爬取或代理后要重新确认请求范围。

项目地址：https://github.com/digininja/CeWL

## 1. 安装与检查

### Kali / Debian

~~~bash
sudo apt update
sudo apt install cewl
~~~

### 从源码安装

~~~bash
git clone https://github.com/digininja/CeWL.git
cd CeWL
bundle install
~~~

源码版本的启动方式以项目说明为准。Kali 中通常可以直接使用 cewl 命令。

检查安装：

~~~bash
cewl --help
cewl --version
~~~

部分版本不支持 --version，只要 cewl --help 能正常显示即可。参数名称在不同版本中可能略有差异。

## 2. 基本语法

~~~bash
cewl [选项] <目标 URL>
~~~

最常用的命令：

~~~bash
cewl -d 2 -m 5 -w words.txt https://example.com
~~~

参数含义：

- -d 2：最多爬取两层页面；
- -m 5：只保留长度不小于 5 的单词；
- -w words.txt：将词表保存到文件；
- 最后的 URL：授权的目标站点。

不指定 -w 时，词表通常会输出到终端：

~~~bash
cewl -d 1 -m 5 https://example.com
~~~

只查看帮助，不对目标发起请求：

~~~bash
cewl --help
~~~

## 3. 常用参数速查

### 爬取和词表

| 参数 | 作用 |
|------|------|
| -d N | 设置爬取深度，默认通常为 2 |
| -m N | 设置最小单词长度，默认通常为 3 |
| -w FILE | 将生成的词表写入文件 |
| -o | 允许爬取站点外部链接，扩大请求范围 |
| --no-words | 不输出普通单词，只执行邮箱或元数据等提取 |
| -u USER_AGENT | 设置 User-Agent |
| -v | 显示更详细的运行信息 |

### 邮箱和元数据

| 参数 | 作用 |
|------|------|
| --email | 提取页面中的邮箱地址 |
| --email_file FILE | 将发现的邮箱地址单独写入文件 |
| --meta | 提取页面元数据 |
| --meta_file FILE | 将发现的元数据单独写入文件 |

### 认证和代理

| 参数 | 作用 |
|------|------|
| --auth_type TYPE | 指定 HTTP 认证类型 |
| --auth_user USER | HTTP 认证用户名 |
| --auth_pass PASS | HTTP 认证密码 |
| --proxy_host HOST | 指定代理主机 |
| --proxy_port PORT | 指定代理端口 |
| --proxy_username USER | 代理认证用户名 |
| --proxy_password PASS | 代理认证密码 |

不同版本可能使用长参数或短参数的不同组合。执行前建议确认：

~~~bash
cewl --help
~~~

## 4. 控制爬取深度

### 浅层快速收集

适合先确认工具是否工作：

~~~bash
cewl -d 1 -m 5 -w words-d1.txt https://example.com
~~~

### 常规收集

适合大多数站点：

~~~bash
cewl -d 2 -m 5 -w words-d2.txt https://example.com
~~~

### 深层收集

只有在页面链接较多、且已经确认请求量可接受时再使用：

~~~bash
cewl -d 3 -m 5 -w words-d3.txt https://example.com
~~~

深度并不是越大越好。深度提高后，页面数量、请求时间和重复内容都会增加。建议先从 -d 1 或 -d 2 开始，检查结果后再扩大。

## 5. 控制单词长度

### 常用词表

保留长度不小于 5 的单词：

~~~bash
cewl -d 2 -m 5 -w words.txt https://example.com
~~~

### 更宽松的词表

如果站点使用大量短缩写、产品代号或项目简称，可以降低最小长度：

~~~bash
cewl -d 2 -m 3 -w words-short.txt https://example.com
~~~

### 更精简的词表

如果结果过多，只保留较长词：

~~~bash
cewl -d 2 -m 7 -w words-long.txt https://example.com
~~~

-m 只影响最小长度，不代表词语一定有业务价值。生成后仍应人工查看和清洗。

## 6. 提取邮箱和元数据

### 提取邮箱到单独文件

~~~bash
cewl -d 2 -m 5 \
  --email \
  --email_file emails.txt \
  -w words-with-email.txt \
  https://example.com
~~~

emails.txt 可以用于整理站点公开联系信息、识别组织命名规律或进行资产归属分析。公开邮箱也属于个人或组织信息，输出文件应妥善保存。

### 提取页面元数据

~~~bash
cewl -d 2 -m 5 \
  --meta \
  --meta_file metadata.txt \
  -w words-with-meta.txt \
  https://example.com
~~~

元数据可能包含作者名、文档标题、软件名称、部门名称或项目代号。它们可以帮助补充业务词表，但也可能包含与当前站点无关的历史内容。

### 只提取邮箱和元数据

不需要输出普通词表时，可以使用 --no-words：

~~~bash
cewl -d 2 \
  --no-words \
  --email \
  --email_file emails.txt \
  --meta \
  --meta_file metadata.txt \
  https://example.com
~~~

如果当前版本要求只使用对应提取参数，按 cewl --help 的提示调整。

## 7. User-Agent、认证和代理

### 自定义 User-Agent

~~~bash
cewl -d 2 -m 5 \
  -u 'Mozilla/5.0' \
  -w words.txt \
  https://example.com
~~~

User-Agent 只用于标识客户端，不应被当作绕过访问控制的手段。

### 抓取需要 HTTP 认证的站点

如果目标是授权的 Basic、Digest 或其它 HTTP 认证页面，可以按当前版本支持的认证类型填写：

~~~bash
cewl -d 2 -m 5 \
  --auth_type basic \
  --auth_user testuser \
  --auth_pass 'PASSWORD' \
  -w words.txt \
  https://example.com
~~~

不要把真实密码直接写进公开脚本或命令记录。认证失败时先确认认证类型、账号权限和目标 URL，不要反复提高爬取深度。

### 通过代理访问

~~~bash
cewl -d 2 -m 5 \
  --proxy_host 127.0.0.1 \
  --proxy_port 8080 \
  -w words.txt \
  https://example.com
~~~

代理可以用于观察请求或访问必须经过指定出口的授权环境。代理不可用时，常见表现是连接超时或没有有效词表结果。

## 8. 外部链接和作用范围

默认情况下，CeWL 通常围绕指定站点爬取。使用 -o 后允许跟随站外链接：

~~~bash
cewl -d 2 -m 5 -o -w words-offsite.txt https://example.com
~~~

启用 -o 前要确认：

- 站外链接是否仍在授权范围内；
- 是否会访问 CDN、社交平台、第三方登录或外部服务；
- 输出中是否会混入其它组织的词语；
- 请求量是否会明显增加。

多数场景不需要 -o。如果目标有多个授权子域名，建议分别指定入口并分别保存结果，再按授权范围合并。

## 9. 词表清洗

CeWL 生成的词表通常已经按单词输出，但合并多个结果后仍建议去重。

### 去重并删除空行

~~~bash
sort -u words.txt | sed '/^$/d' > words-clean.txt
~~~

### 忽略大小写去重

如果不关心大小写差异：

~~~bash
sort -fu words.txt | sed '/^$/d' > words-lowercase-unique.txt
~~~

这会把大小写不同但拼写相同的词合并，适用于目录名或关键词筛选；如果需要保留原始大小写，不要使用 -f。

### 合并多个来源

~~~bash
cat words-d1.txt words-d2.txt words-with-meta.txt \
  | sort -u \
  | sed '/^$/d' \
  > words-merged.txt
~~~

### 查看词表规模

~~~bash
wc -l words-clean.txt
head -n 20 words-clean.txt
~~~

Windows PowerShell：

~~~powershell
(Get-Content .\words-clean.txt).Count
Get-Content .\words-clean.txt | Select-Object -First 20
~~~

### 按长度再次过滤

~~~bash
awk 'length($0) >= 5' words-clean.txt > words-min5.txt
~~~

过滤前要确认词表编码和目标语言。对中文、日文等非 ASCII 内容，依赖 awk 的长度判断可能与预期不同，建议用文本工具或脚本按实际字符集处理。

## 10. 一套实用流程

### 第一步：浅层测试

~~~bash
cewl -d 1 -m 5 -w cewl-d1.txt https://example.com
~~~

先确认：

- URL 是否可访问；
- 是否生成了输出文件；
- 词表内容是否与目标业务相关；
- 请求量和速度是否正常。

### 第二步：常规深度收集

~~~bash
cewl -d 2 -m 5 \
  --email \
  --email_file emails.txt \
  --meta \
  --meta_file metadata.txt \
  -w cewl-main.txt \
  https://example.com
~~~

### 第三步：清洗和合并

~~~bash
cat cewl-d1.txt cewl-main.txt | sort -u | sed '/^$/d' > cewl-final.txt
~~~

### 第四步：人工复核

重点查看：

- 产品名称、项目名称和品牌变体；
- 部门、系统、环境和主机命名；
- 公开文档中的作者名和项目代号；
- 邮箱域名和组织命名规律；
- 明显来自第三方站点或历史页面的无关词语。

不要把所有抓到的内容直接交给后续高请求量工具。先删除无关词、隐私信息和不在授权范围内的内容。

## 11. 与其它工具配合

### 生成定制目录词表

CeWL 生成的业务词表可以用于授权 Web 内容发现：

~~~bash
cewl -d 2 -m 4 -w business-words.txt https://example.com
sort -u business-words.txt > business-words-unique.txt
~~~

再将词表交给目录扫描工具时，应使用低速率、小范围和明确的授权 URL。例如：

~~~bash
ffuf -w business-words-unique.txt \
  -u https://example.com/FUZZ \
  -mc 200,301,302,403 \
  -rate 50
~~~

CeWL 生成的是自然语言词语，不是专门的 Web 路径字典。它适合补充业务相关路径，不能替代 SecLists 等通用路径字典。

### 与 SecLists 合并

~~~bash
cat business-words-unique.txt \
  /usr/share/seclists/Discovery/Web-Content/common.txt \
  | sort -u \
  > web-content-merged.txt
~~~

合并大字典会显著增加请求量。先用 CeWL 词表和小型通用字典验证流程，再决定是否扩大。

### 作为授权密码审计的词表来源

CeWL 可以帮助审计人员生成与组织业务相关的候选词，但词表本身不代表密码，也不应直接用于未授权登录尝试。进行密码策略审计时，应遵守测试范围、账号规则、速率限制和审批要求。

## 12. 常见问题

### 生成的词表为空

检查：

- URL 是否包含 http:// 或 https://；
- 目标是否能从当前网络访问；
- 页面是否需要登录；
- -m 是否设置得过大；
- 代理或认证参数是否正确；
- 结果是否被写入了指定的 -w 文件。

先用最小命令测试：

~~~bash
cewl -d 1 -m 3 -w test.txt https://example.com
~~~

### 结果太少

按顺序尝试：

~~~bash
cewl -d 2 -m 3 -w words.txt https://example.com
cewl -d 3 -m 3 -w words-deep.txt https://example.com
~~~

如果站点主要依赖 JavaScript 动态加载，CeWL 可能看不到浏览器执行后才出现的内容。此时先用浏览器或 Katana 确认真实页面和资源，再决定是否需要其它采集方式。

### 结果太多且质量差

降低爬取深度、提高最小词长，并关闭站外爬取：

~~~bash
cewl -d 1 -m 6 -w words-focused.txt https://example.com
~~~

随后使用 sort -u 去重，并删除导航菜单、通用英文词和明显无关的第三方内容。

### 爬取时间很长

深度、链接数量、站点响应速度和代理都会影响执行时间。先使用 -d 1，不要一开始就启用 -o。对动态站点和需要认证的站点，先确认入口页面能正常返回。

### 抓不到登录后的内容

CeWL 常用的认证参数面向 HTTP 认证，不等于支持所有 Web 表单登录、验证码、单点登录或复杂 Cookie 流程。对于表单登录站点，应先在浏览器或代理中确认登录态，再选择支持登录态的采集方式，不要把账号密码反复写入命令历史。

### 参数不识别

不同 CeWL 版本差异较大，先查看：

~~~bash
cewl --help
~~~

特别是邮箱、元数据、认证和代理参数，使用前以当前版本帮助输出为准。

## 13. 快速记忆

~~~bash
# 基础抓词
cewl -d 2 -m 5 -w words.txt https://example.com

# 深度和最小长度
cewl -d 1 -m 3 -w words-short.txt https://example.com

# 邮箱
cewl -d 2 --email --email_file emails.txt -w words-email.txt https://example.com

# 元数据
cewl -d 2 --meta --meta_file metadata.txt -w words-meta.txt https://example.com

# 通过代理
cewl -d 2 --proxy_host 127.0.0.1 --proxy_port 8080 -w words.txt https://example.com

# 清洗
sort -u words.txt | sed '/^$/d' > words-clean.txt

# 授权 Web 内容发现
ffuf -w words-clean.txt -u https://example.com/FUZZ -rate 50
~~~
