![](file-20260815095849837.png)

![](file-20260815095849842.png)

![](file-20260815095849844.png)

![](file-20260815095849845.png)

![](file-20260815095849846.png)

![](file-20260815095849848.png)

![](file-20260815095849850.png)

![](file-20260815095849851.png)

![](file-20260815095849852.png)

![](file-20260815095849853.png)

![](file-20260815095849855.png)

![](file-20260815095849856.png)

解码
```php
<h1>
<center>
Nebuchadnezzar Graffiti Wall

</center>
</h1>
<p>
<?php

$file="graffiti.txt";
if($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['file'])) {
       $file=$_POST['file'];
    }
    if (isset($_POST['message'])) {
        $handle = fopen($file, 'a+') or die('Cannot open file: ' . $file);
        fwrite($handle, $_POST['message']);
	fwrite($handle, "\n");
        fclose($file); 
    }
}

// Display file
$handle = fopen($file,"r");
while (!feof($handle)) {
  echo fgets($handle);
  echo "<br>\n";
}
fclose($handle);
?>
<p>
Enter message: 
<p>
<form method="post">
<label>Message</label><div><input type="text" name="message"></div>
<input type="hidden" name="file" value="graffiti.txt">
<div><button type="submit">Post</button></div>
</form>
MTExCg==
```

功能是再指定文件夹中追加内容然后展示，如果没有指定文件就是默认的graffiti.txt，**但这里没有对file参数做任何处理就如之前我们指定文件一样**。

尝试再文件夹中写入一句话木马。

![](file-20260815095849859.png)

写入phpinfo成功解析：

![](file-20260815095849861.png)

![](file-20260815095849864.png)

![](file-20260815095849867.png)

更具echo $0判断终端类型然后编写合适的反弹shell 

![](file-20260815095849870.png)

![](file-20260815095849874.png)

![](file-20260815095849877.png)

![](file-20260815095849880.png)

![](file-20260815095849884.png)

![](file-20260815095849887.png)

既然有python环境那就先升级一下shell，让其功能更全面可以补全可以

![](file-20260815095849891.png)

![](file-20260815095849896.png)

![](file-20260815095849899.png)

![](file-20260815095849902.png)

![](file-20260815095849905.png)

![](file-20260815095849909.png)

![](file-20260815095849912.png)

![](file-20260815095849915.png)

静态编译防止目标缺少依赖库

![](file-20260815095849918.png)

![](file-20260815095849921.png)

![](file-20260815095849924.png)