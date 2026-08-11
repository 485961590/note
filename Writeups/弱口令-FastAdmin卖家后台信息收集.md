
- 目标：chat.dig-mall.com:8048（wanlshop 商城卖家控制台）
- 时间：2026-08-05
- 性质：授权测试 / 教学演练，测试残留账号利用记录
- 关联课程：中网信安 - 业务逻辑漏洞 / 未授权访问

## 目标指纹

| 项       | 值                                                   | 来源                                            |
| ------- | --------------------------------------------------- | --------------------------------------------- |
| 框架      | FastAdmin，底层 ThinkPHP 5.x                           | meta author、/thinkphp/library/ 路径             |
| 业务插件    | wanlshop（旺铺商城）卖家控制台                                 | /index/wanlshop.* 路由、addons/wanlshop          |
| Web 服务器 | nginx（响应含 HTTP/3 Alt-Svc）                           | Server 响应头                                    |
| 端口      | 8048（HTTP 明文）                                       | 访问入口                                          |
| 真实 IP   | 203.119.115.132                                     | Trace 部署目录 /www/wwwroot/203.119.115.132_8048/ |
| 数据库     | mysql 127.0.0.1:3306，dbname=walianhe，表前缀 fa_        | Trace SQL                                     |
| 域名托管    | dns19/dns20.hichina.com（阿里云/万网）                     | nslookup NS                                   |
| 关联域名    | chat.aghgzx.com（IM/WebSocket，wss://chat.aghgzx.com） | 页面 config socketurl                           |
| 证书      | *.dig-mall.com 泛域名证书                                | crt.sh                                        |
| PHP 版本  | 加载 symfony/polyfill-php80，确切版本未确认                   | Trace 文件清单                                    |

## 登录链路（流量证据）

1. GET /index/user/login.html → 获取页面与 `__token__`（FastAdmin CSRF 令牌）
2. POST /index/user/login.html
   body:
     url=http://chat.dig-mall.com:8048/index/wanlshop.shop/profile.html
     &__token__=da3ae04729d708f337c1723c603df80b
     &account=admin
     &password=123456
   响应:
     {"code":1,"msg":"登录成功","data":"","url":"...","wait":3}
     Set-Cookie: uid=1; path=/
     Set-Cookie: token=7a5a6c88-66d9-4c84-82a4-555b070a9c5e; path=/
3. 后续请求携带 uid + token Cookie 完成会话

认证链（Trace SQL）：
fa_user_token(token) → fa_user(id=1) → fa_wanlshop_auth(user_id=1) → fa_wanlshop_shop(user_id=1)

注意点：Cookie 中的 token 是 36 字符 UUID 格式，而 DB 查询用 40 字符十六进制串（sha1 输出长度），说明框架在存储/查询时对 token 做了单向变换，具体实现需对照部署源码确认。

## 核心发现：弱口令 / 测试账号残留

账号证据：
- 账号 admin，口令 123456（默认弱口令）
- uid=1，系统第一个用户
- 昵称"测试"、店铺名"测试"、关键字"测试"、简介"1"
- 头像上传于 20241123/20241227，类目为 wanlshop 官方演示分类

卖家控制台模块：
- 交易管理：商品订单、评论管理、退款管理
- 宝贝管理：发布/编辑/下架商品
- 类目管理、店铺管理（装修/图片空间/品牌/资料）、物流运费、店铺配置

## 调试 Trace 信息泄露

页面底部存在 thinkphp_show_page_trace 控制块，app_debug / show_page_trace 在生产环境开启。

泄露内容：
1. 绝对路径 /www/wwwroot/203.119.115.132_8048/...
2. 单次请求加载 93 个文件，完整框架/插件/依赖树（alisms、crontab、wanlshop、signin、simditor）
3. SQL 语句含 SHOW COLUMNS 元查询，泄露表结构
4. ROUTE / HEADER / PARAM 数组，含完整 Cookie

## 被动 OSINT 结果

- DNS：dig-mall.com NS = dns19/dns20.hichina.com（阿里云/万网）
- A 记录：chat.dig-mall.com → 203.119.115.132（已确认）；dig-mall.com / aghgzx.com 顶级域 A 记录因本地 nslookup 输出编码问题未最终确认
- 证书透明度：dig-mall.com 仅 *.dig-mall.com 泛域名证书（掩盖子域名枚举）；aghgzx.com 无公开证书记录
- 反解：203.119.115.132 无 PTR
- 邮件：dig-mall.com 无 MX、无 TXT
- 搜索足迹：dig-mall.com / aghgzx.com 无公开搜索引擎索引

## 其他安全观察

| 项 | 观察 | 风险 |
|---|---|---|
| Cookie 安全标志 | uid、token 仅 path=/，无 HttpOnly/Secure/SameSite | XSS 可窃取会话令牌 |
| 明文传输 | 登录 POST 走 http://8048，凭据明文 | 链路嗅探截获 |
| HSTS | 响应含 HSTS 头但走 HTTP，浏览器忽略 | 无效防护 |
| url 参数 | 登录请求带 url=...，FastAdmin 登录后跳转参数 | 潜在开放重定向，待实测 |
| v-html | 聊天模板 v-html="item.message.content.text" 等 | 潜在存储型 XSS sink |
| 登录防护 | 未见验证码/频率限制证据 | 弱口令可枚举 |

## 待验证 / 未完成事项

未完成（主动探测被中止）：
- 端口扫描 203.119.115.132 全端口
- 子域名枚举（泛域名证书下改用 DNS 爆破）
- dig-mall.com / aghgzx.com 顶级域 A 记录复核
- RDAP/Whois 注册信息与 IP 归属（APNIC）
- 常见子域名解析（www/api/admin/m/h5 等）
- 目标 HTTP 80/443 入口内容

待验证：
- token 的 sha1 变换细节（对照部署源码）
- url 参数是否开放重定向（改 url=https://evil.com 观察跳转）
- 登录是否有限速/验证码
- 后端 /admin 入口是否同样弱口令
- v-html 是否可注入（聊天/店铺简介注入 img onerror 载荷）
