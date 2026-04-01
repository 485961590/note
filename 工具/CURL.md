## 基本语法

```
curl [选项] [URL]
```

## 常用操作

### 1. 基本请求

```
curl http://example.com                    # GET请求
curl -X POST http://example.com            # POST请求
curl -X PUT http://example.com             # PUT请求
curl -X DELETE http://example.com          # DELETE请求
```

### 2. 下载文件

```
curl -O http://example.com/file.txt        # 保存为原文件名
curl -o newname.txt http://example.com/file.txt  # 指定保存文件名
```

### 3. 提交数据

```
curl -d "name=value" http://example.com    # POST表单数据
curl -d @data.json http://example.com      # POST JSON文件
curl -F "file=@test.txt" http://example.com # 文件上传
```

### 4. 设置请求头

```
curl -H "Content-Type: application/json" http://example.com
curl -H "Authorization: Bearer token" http://example.com
```

### 5. 认证

```
curl -u username:password http://example.com  # 基本认证
curl --cookie "name=value" http://example.com # 设置cookie
```

### 6. 输出控制

```
curl -s http://example.com                 # 静默模式（不显示进度）
curl -v http://example.com                 # 详细输出
curl -i http://example.com                 # 包含响应头
```

## 实用示例

```
# 测试命令执行
curl "http://target.com/?cmd=ls"
curl "http://target.com/?cmd=cat%20*"
curl "http://target.com/?cmd=pwd"

# 带输出详细信息
curl -v "http://target.com/?cmd=ls"
```

### 安全使用curl

```
# 先查看内容再决定是否执行
curl http://example.com/script.sh > check_script.sh
cat check_script.sh  # 检查内容
bash check_script.sh # 确认安全后执行

# 或直接查看不保存
curl http://example.com/script.sh | less
```

### 高级用法

```
# 跟随重定向
curl -L http://example.com

# 限速下载
curl --limit-rate 100k http://example.com/file.zip

# 断点续传
curl -C - -O http://example.com/largefile.zip

# 测试API
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"value"}' http://api.example.com/endpoint
```