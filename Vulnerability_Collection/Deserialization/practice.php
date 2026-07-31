<?php
class TestObject {
//    public function __destruct() {
//        include('flag.php');
//        echo $flag;
//    }
}
//$filename = $_POST['file'];
//if (isset($filename)){
//    echo md5_file($filename);
//}
echo serialize(new TestObject());
?>