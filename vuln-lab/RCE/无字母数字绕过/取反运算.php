<?php
$a = 'a';
echo "原始字符: " . $a . "\n";
echo "ASCII码: " . ord($a) . "\n";
echo "十六进制: " . bin2hex($a) . "\n";
echo "二进制: " . base_convert(bin2hex($a), 16, 2) . "\n";

// 正确的取反操作
$ascii = ord($a);
$not_ascii = ~$ascii;
echo "取反ASCII: " . $not_ascii . "\n";
echo "取反后字符: '" . chr($not_ascii) . "超出了ASCII的范围了ASCII最大7E"."'\n";
echo "取反十六进制: " . dechex($not_ascii & 0xFF) . "\n";

?>