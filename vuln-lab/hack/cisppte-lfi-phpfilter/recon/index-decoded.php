<?php error_reporting(0); ?>
<?php include("function.php"); ?>
<html>
<head>
  <title>CISP-PTE 认证考试</title>
  <link rel="stylesheet" href="../css/bootstrap.css">
  <link rel="stylesheet" href="../css/nav.css">
  <meta charset="UTF-8">
</head>

<body>

  <?php include '../header.php';?>

  <div class="container mt-5 min-height main-body">


<div class="row">
   <div class="col-7 m-auto">
         <h2>文件包含漏洞</h2>
         <?php
         	$page=$_GET['page'];

			$page=str_replace("php://", "", $page);
      $page=str_replace("file://", "", $page);
      $page=str_replace("ftp://", "", $page);
      $page=str_replace("zlib://", "", $page);
      $page=str_replace("data://", "", $page);
      $page=str_replace("glob://", "", $page);
      $page=str_replace("phar://", "", $page);
      $page=str_replace("ssh2://", "", $page);
      $page=str_replace("rar://", "", $page);
      $page=str_replace("ogg://", "", $page);
			$page=str_replace("expect://", "", $page);
#			$page= $page . ".txt";
?>
         <br>
         <span style="color:red">
         	<?php
echo ">> ".$page;

?>
</span>
         <br>
         <br>

         <?php
		
			include($page);
         ?>
  </div>
  </div>


</div>
<?php include '../footer.php';?>
</body>
</html>
