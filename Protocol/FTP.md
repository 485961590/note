**FTP（File Transfer Protocol）本质上是一个不安全的协议**，所有数据（包括用户名、密码、文件内容）都是**明文传输**的。

# FTP可以进行远程连接，可以执行的操作是：
## 基础导航命令
```
pwd                     # 显示当前远程目录
ls                      # 列出当前目录内容（简化版）
dir                     # 列出当前目录内容（详细信息，类似 ls -l）
cd /path                # 切换远程目录
cdup                    # 返回上级目录（等同于 cd ..）
lcd /local/path         # 切换本地目录（important！）
```
## 文件下载命令
 ```
get filename              # 下载单个文件到本地当前目录
get filename localname    # 下载并重命名
mget *.txt                # 下载多个文件（通配符）
recv filename             # 同 get
 ```
## 文件管理命令
```
put filename              # 上传单个文件
put localfile remotefile  # 上传并重命名
mput *.txt                # 上传多个文件
send filename             # 同 put
```
## 文件管理命令
```
delete filename           # 删除远程文件
rmdir dirname             # 删除远程空目录
mkdir dirname             # 创建远程目录
rename oldname newname    # 重命名远程文件
chmod 755 filename        # 修改远程文件权限（需服务器支持）
size filename             # 查看文件大小
status                    # 显示当前状态
```