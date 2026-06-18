# CentOS 7 配置网络

适用于 CentOS 7 虚拟机（NAT/桥接模式）手动获取 IP 的常用命令。

```bash
# 1. 释放旧租约并重新获取 IP
dhclient -r && dhclient ens33

# 2. 查看当前 IP 地址
ip addr show ens33

# 3. 检查网络管理服务状态
systemctl status NetworkManager

# 4. 测试网关连通性（有 IP 后执行）
ping -c 2 192.168.1.1
```