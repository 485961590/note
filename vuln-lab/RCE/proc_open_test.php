<?php
$descriptors = [
    0 => ["pipe", "r"], // 标准输入
    1 => ["pipe", "w"], // 标准输出
    2 => ["pipe", "w"]  // 标准错误
];

$process = proc_open("dir", $descriptors, $pipes);

if (is_resource($process)) {
    // 重要：关闭输入管道，否则进程可能等待输入
    fclose($pipes[0]);

    // 读取标准输出
    $output = stream_get_contents($pipes[1]);
    fclose($pipes[1]);

    // 读取标准错误（可选）
    $errors = stream_get_contents($pipes[2]);
    fclose($pipes[2]);

    // 关闭进程并获取退出码
    $return_value = proc_close($process);

    echo "输出: " . $output . PHP_EOL;
    if (!empty($errors)) {
        echo "错误: " . $errors . PHP_EOL;
    }
    echo "退出码: " . $return_value . PHP_EOL;
} else {
    echo "无法创建进程" . PHP_EOL;
}
?>