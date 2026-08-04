# arp-scan

> 局域网(L2)主机发现工具，通过发送 ARP 请求探测网段内存活主机，并识别厂商
> 项目地址: https://github.com/royhills/arp-scan

---

## 工作原理

向目标网段内每个 IP 发送 ARP 请求，收到 ARP 响应的即为主机。返回的内容包括 IP、MAC 地址，并自动通过 OUI 库匹配网卡厂商。

- 工作在二层(L2)，只对**同一局域网/同一网段**有效，无法穿透路由器扫描跨网段主机
- 比 ICMP 探测(ping)更可靠：即使主机屏蔽了 ICMP，ARP 响应通常也会返回
- 需要 root 权限（构造原始 ARP 包）
- 输出会附带厂商信息，方便识别设备类型（路由器、手机、摄像头等）

**合规性**：ARP 探测仅作用于本地网段，属于内网信息收集行为，请仅在自己有权测试的网络中使用。

---

## 安装

```bash
# Kali / Debian
sudo apt install arp-scan

# 源码编译
git clone https://github.com/royhills/arp-scan.git
cd arp-scan && autoreconf -fi && ./configure && make && sudo make install

# Windows（可选）
# 官方提供 Windows 构建版，需先安装 Npcap 驱动
# 下载地址见项目 Releases 页面
```

---

## 基本用法

```bash
# 扫描本地网段（根据网卡配置自动生成地址）
sudo arp-scan --local

# 指定网段扫描
sudo arp-scan 192.168.1.0/24

# 指定网卡接口（推荐，源 MAC 取自该网卡）
sudo arp-scan -I eth0 192.168.1.0/24

# 扫描一个范围
sudo arp-scan 192.168.1.100-192.168.1.200
```

---

## 常用参数

| 参数 | 作用 |
|------|------|
| `-l, --local` | 扫描本地网段（自动获取网卡配置的网段） |
| `-I, --interface` | 指定网卡接口，如 `-I eth0`、`-I wlan0` |
| `-R, --retry` | 重试次数，默认 2 |
| `-t, --timeout` | 每包超时时间（毫秒），默认 100 |
| `-r, --random` | 随机化扫描顺序，降低被 IDS 检测的概率 |
| `-s, --srcaddr` | 指定源 IP |
| `-v` | 详细输出 |
| `--ouifile` | 指定 OUI 厂商数据库文件 |
| `--interface` | 显示扫描使用的网卡信息 |
| `--duplicates` | 显示重复的响应 |

---

## 使用示例

### 主机发现

```bash
# 扫描本地网段
sudo arp-scan -l

# 输出示例
# 192.168.1.1    00:0c:29:xx:xx:xx  VMware, Inc.
# 192.168.1.10   5c:8d:4e:xx:xx:xx  Xiaomi Communications Co Ltd
# 192.168.1.20   f0:9f:c2:xx:xx:xx  TP-Link Technologies Co.,Ltd.
```

### 识别设备类型

厂商列直接显示网卡制造商，可据此判断设备：
- TP-Link / Xiaomi / HUAWEI → 路由器、智能家居设备
- VMware / QEMU / Oracle VirtualBox → 虚拟机
- Apple → iPhone/Mac
- Raspberry Pi Foundation → 树莓派

### 与 nmap 结合

```bash
# 先用 arp-scan 找存活主机，再交给 nmap 做端口扫描
sudo arp-scan -l | awk '{print $1}' | grep -E '^[0-9.]+$' | nmap -iL -
```

### 指定网卡

```bash
# 多网卡时明确指定接口，避免扫错网段
sudo arp-scan -I wlan0 --local
```

---

## 注意事项

- **必须 root**：普通用户无法构造原始 ARP 包，会报错
- **仅限本网段**：ARP 请求不会跨路由器转发，跨网段请用 nmap 等三层工具
- **接口参数很重要**：不指定 `-I` 时默认使用路由表主接口，可能不是目标网卡
- **虚拟网卡干扰**：VMware/VirtualBox 的虚拟网卡会响应探测，注意区分
- **重复响应**：虚拟机或配置了多 IP 的主机可能返回多条记录，可用 `--duplicates` 观察
