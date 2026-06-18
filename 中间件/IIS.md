# IIS (Internet Information Services)

> IIS 是微软 Windows 专有的 Web 服务器，与 Windows Server 深度集成。支持 HTTP/HTTPS、FTP、SMTP 等协议，通过图形界面或 PowerShell 管理。**IIS 不原生支持 Linux**，在 Linux 上建议使用 Nginx 或 Apache 替代。

---

## 查看发行版信息

```bash
# Linux 环境用（IIS 不运行在 Linux 上）
cat /etc/os-release          # 推荐
lsb_release -a
hostnamectl

# Windows 环境用
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
# 或
[System.Environment]::OSVersion.VersionString        # PowerShell
```

---

## 重要说明：IIS 与 Linux

IIS 是 Windows 操作系统组件，**无法在 Linux 上安装或运行**。如果你在 Linux 上搭建 Web 服务，请参考：

| 需求 | Linux 方案 | 参考文件 |
|------|-----------|---------|
| 静态网站 / 虚拟主机 | Apache / Nginx | [[Apache]], [[Nginx]] |
| 反向代理 | Nginx | [[Nginx]] |
| ASP.NET 应用 | Nginx + Kestrel 反向代理 | [[Nginx]] |
| FTP 服务 | vsftpd / ProFTPD | — |

---

## Windows 上安装 IIS

### PowerShell（推荐）

```powershell
# 以管理员身份运行，安装默认 IIS 组件
Install-WindowsFeature -Name Web-Server -IncludeManagementTools

# 或带 ASP.NET 支持
Install-WindowsFeature -Name Web-Server, Web-Asp-Net45 -IncludeManagementTools
```

### 控制面板安装

```
控制面板 → 程序和功能 → 启用或关闭 Windows 功能 → Internet Information Services
```

### 查看已安装的 IIS 功能

```powershell
Get-WindowsFeature -Name Web-* | Where-Object Installed
```

---

## 服务管理

### PowerShell

```powershell
# 启动
Start-Service W3SVC
# 或
iisreset /start

# 停止
Stop-Service W3SVC
# 或
iisreset /stop

# 重启（等于 stop + start，会断开所有连接）
iisreset

# 查看状态
Get-Service W3SVC
```

### CMD

```cmd
iisreset /start
iisreset /stop
iisreset /restart
iisreset /status
```

---

## 默认目录

| 内容 | 路径 |
|------|------|
| 网站根目录 | `C:\inetpub\wwwroot\` |
| 日志目录 | `C:\inetpub\logs\LogFiles\` |
| 配置文件目录 | `C:\Windows\System32\inetsrv\config\` |
| 主配置文件 | `C:\Windows\System32\inetsrv\config\applicationHost.config` |
| IIS 可执行文件 | `C:\Windows\System32\inetsrv\` |
| FTP 根目录（如安装） | `C:\inetpub\ftproot\` |

> `applicationHost.config` 是 IIS 的核心配置 XML 文件，管理所有站点、应用程序池和全局设置。不建议直接编辑，用 IIS Manager 或 PowerShell 修改更安全。

---

## 站点管理

### 创建站点（PowerShell）

```powershell
# 创建网站目录
New-Item -Path "C:\inetpub\wwwroot\mysite" -ItemType Directory

# 创建站点
New-IISSite -Name "MySite" -PhysicalPath "C:\inetpub\wwwroot\mysite" -BindingInformation "*:80:mysite.local"

# 创建应用程序池
New-WebAppPool -Name "MyAppPool"

# 将站点绑定到应用程序池
Set-ItemProperty -Path "IIS:\Sites\MySite" -Name ApplicationPool -Value "MyAppPool"
```

### 站点操作（PowerShell）

```powershell
# 列出所有站点
Get-IISSite

# 列出所有应用程序池
Get-IISAppPool

# 停止站点
Stop-IISSite -Name "MySite"

# 启动站点
Start-IISSite -Name "MySite"

# 删除站点
Remove-IISSite -Name "MySite" -Confirm:$false

# 回收应用程序池
Restart-WebAppPool -Name "MyAppPool"
```

### 绑定管理

```powershell
# 添加 HTTPS 绑定
New-IISSiteBinding -Name "MySite" -BindingInformation "*:443:mysite.local" -Protocol https -CertificateThumbprint "xxxx"

# 查看站点绑定
Get-IISSiteBinding -Name "MySite"
```

---

## 常用命令速查

```powershell
# === IIS 管理（PowerShell）===

# 查看所有站点
Get-IISSite

# 查看站点详情
Get-IISSite -Name "Default Web Site"

# 查看正在运行的 worker process
Get-IISWorkerProcess

# 查看当前请求
Get-IISRequest

# 模块管理
Get-WebGlobalModule                    # 列出全局模块

# 查看日志位置
Get-WebConfigurationProperty -Filter "system.applicationHost/sites/siteDefaults/logFile" -Name directory

# === IIS 管理（CMD）===

# 列出所有站点
%windir%\system32\inetsrv\appcmd list sites

# 列出应用程序池
%windir%\system32\inetsrv\appcmd list apppool

# 创建站点
%windir%\system32\inetsrv\appcmd add site /name:MySite /bindings:"http/*:80:" /physicalPath:"C:\inetpub\wwwroot\mysite"

# 删除站点
%windir%\system32\inetsrv\appcmd delete site "MySite"
```

---

## 防火墙（Windows）

```powershell
# 允许 HTTP
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# 允许 HTTPS
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# 或 IIS 安装时自动创建的规则，查看：
Get-NetFirewallRule | Where-Object DisplayName -like "*World Wide Web*"
```

---

## 常见问题

**端口 80 被占用：**

```powershell
# 查看谁占用了 80 端口
netstat -ano | findstr :80
# 或
Get-NetTCPConnection -LocalPort 80
```

**IIS 不启动：**

```powershell
# 查看事件日志
Get-EventLog -LogName System -Source "Service Control Manager" -Newest 20 | Where-Object Message -like "*W3SVC*"

# 检查配置是否损坏
%windir%\system32\inetsrv\appcmd list config
```

**权限问题（500 错误）：**

```
检查应用程序池标识（Application Pool Identity）对网站目录是否有读取权限。
默认标识：IIS AppPool\<PoolName>
路径：C:\inetpub\wwwroot\<yoursite>
```

---

## Linux 替代方案对照

| IIS 功能 | Linux 等效方案 |
|----------|---------------|
| 静态文件服务 | Nginx / Apache |
| ASP.NET | Nginx + Kestrel (反向代理) |
| .htaccess 目录覆写 | Apache .htaccess |
| IIS Manager GUI | Cockpit (Web 管理面板) / 手动编辑配置 |
| 应用程序池 | systemd service 或 Docker 容器隔离 |
| FTP 服务 | vsftpd, ProFTPD |
| Windows 集成认证 | Kerberos + Apache mod_auth_kerb |
| IIS 日志 | Nginx/Apache 自带日志，或 rsyslog 集中管理 |
