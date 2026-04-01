```
# 1. 尝试自动获取IP
dhclient -r && dhclient ens33

# 2. 查看结果
ip addr show ens33

# 3. 检查网络服务
systemctl status NetworkManager

# 4. 测试网关连通性（如果有IP的话）
ping -c 2 192.168.1.1
```