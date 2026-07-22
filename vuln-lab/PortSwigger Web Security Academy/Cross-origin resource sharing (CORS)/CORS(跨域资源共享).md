首先CORS发明出来时为了解决同源策略的限制太严格的问题，在一定程度上是为了**放宽同源策略**方便服务器加载授权的第三方资源使其加载资源更灵活而产生的**受控中间地带**。

==存在的漏洞==
**1：服务器根据客户端 Origin 头生成 ACAO（Access-Control-Allow-Origin） 头:**

响应包里出现CORS相关的响应头:

| 响应头                                | 作用                 |
| ---------------------------------- | ------------------ |
| `Access-Control-Allow-Origin`      | 指定允许哪个源访问响应（最重要）   |
| `Access-Control-Allow-Credentials` | 是否允许携带 Cookie/认证信息 |
| `Access-Control-Allow-Methods`     | 允许的 HTTP 方法（预检时使用） |
| `Access-Control-Allow-Headers`     | 允许的自定义请求头（预检时使用）   |
在数据传输过程中留意到一个数据包的响应包里存在`Access-Control-Allow-Credentials`等与CORS相关的响应头，说明这个网站多多少少与CORS相关，在观察请求数据包中是否包含Origin，如果有修改其值发送，如果没有则添加一个虚假的Origin请求头，观察响应包中是否会出现Access-Control-Allow-Origin而判断漏洞是否存在。

**2：白名单中的 null 源值**

同样的是观察到响应头中存在与CORS有关的响应头中可用尝试设置Origin为null，之所以这样是因为在开发过程中为了方便程序员调试有时会将null放进白名单中但是系统上线后没有删除null导致的，当添加或修改Origin为null后观察是否出现Access-Control-Allow-Origin的值为null。

**3：通过 CORS 信任关系利用 XSS**

通俗来讲就是CORS配置没有问题正确配置了，但是在一个存在xss漏洞的站点，恰好此站点在白名单中，我们就可用触发xss来向目标站点进行攻击，因为存在xss的站点本身受信任因此xss转发的数据也可以成功绕过CORS的检查。

```txt
存在xss的漏洞并且网站在CORS白名单中 ---> xss向目标网站发起请求（可用是直接查询数据也可以外带数据）
```