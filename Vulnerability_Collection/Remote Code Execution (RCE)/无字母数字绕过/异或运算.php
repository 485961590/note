<?php
echo base_convert(bin2hex("5"),16,2)."\n";
echo base_convert(bin2hex("Z"),16,2)."\n";
echo ("5"^"Z")."\n";
//0110101
//1011010
//异或得1101111
// 二进制字符串转十进制，再转字符
$binary = "1101111";
$decimal = bindec($binary);  // 二进制转十进制
$char = chr($decimal);       // 十进制转字符

echo "二进制: $binary\n";
echo "十进制: $decimal\n";
echo "字符: $char\n";


function o(){
    echo "hello,world";
}
$_ = "/"^"@";
$_();
