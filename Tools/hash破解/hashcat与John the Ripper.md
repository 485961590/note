# hashcat 与 John the Ripper

## 概述

John the Ripper (JtR) 和 hashcat 是两款主流的密码破解工具。实际使用中，两者常配合使用：用 JtR 的 `*2john` 系列工具从目标文件中提取 hash，再用 hashcat 进行高速破解。

---

## John the Ripper (Jumbo)

### 简介

John the Ripper 是一个快速的密码破解工具，jumbo 版本扩展了数百种 hash 和加密类型的支持。

Windows 下常用发行版：`john-1.9.0-jumbo-1-win64`

### 核心用法

```bash
# 基础破解（自动检测 hash 类型，使用默认模式顺序）
john passwd

# 指定字典 + 规则变形
john --wordlist=password.lst --rules passwd

# 查看已破解的密码
john --show passwd

# 恢复上次中断的会话
john --restore
```

### *2john 系列工具（提取 hash）

jumbo 版本自带的 `*2john` 工具用于从各类文件中提取 hash，生成 JtR 可识别的格式，后续可转入 hashcat 破解。

| 工具 | 用途 |
|---|---|
| `zip2john.exe` | 从 ZIP 压缩包提取 hash |
| `rar2john.exe` | 从 RAR 压缩包提取 hash |
| `7z2john.exe` | 从 7z 压缩包提取 hash |
| `office2john.exe` | 从 MS Office 文档提取 hash |
| `pdf2john.exe` | 从 PDF 文件提取 hash |
| `keepass2john.exe` | 从 KeePass 数据库提取 hash |
| `ssh2john.exe` | 从 SSH 私钥提取 hash |
| `dmg2john.exe` | 从 macOS DMG 镜像提取 hash |
| `bitlocker2john.exe` | 从 BitLocker 加密卷提取 hash |

#### 使用示例

```powershell
# 从 ZIP 包提取 hash，保存到文件
zip2john.exe target.zip > zip_hash.txt

# 从 RAR 包提取 hash
rar2john.exe target.rar > rar_hash.txt
```

提取出的 hash 格式通常为：

```
target.zip:$pkzip2$3*2*1*0*8*24*...*$/pkzip2$
```

---

## hashcat

### 简介

hashcat 号称世界上最快的密码破解工具，支持 CPU 和 GPU 加速，支持 300+ 种 hash 类型。

### 核心参数

| 参数        | 说明                               |
| --------- | -------------------------------- |
| `-m <数字>` | 指定 hash 类型也就是hash加密方式（必需）        |
| `-a <数字>` | 指定攻击模式，默认为 0（字典攻击）               |
| `-d <数字>` | 指定设备（GPU/CPU），如 `-d 1` 使用第一块 GPU |
| `-o <文件>` | 输出已破解密码到文件                       |
| `-w <数字>` | 工作负载配置文件 (1-4)，越大越快但越占资源         |
| `-O`      | 优化内核（仅限密码长度 <= 32 的场景）           |
| `--force` | 忽略警告强制执行                         |
| `--show`  | 显示已破解的密码                         |
获取hash值后复制前几个值然后去https://hashcat.net/wiki/doku.php?id=example_hashes网站进行对比得到hashcat -m的参数
#### 攻击模式 `-a`

| 值   | 模式                      | 说明                                                       |
| --- | ----------------------- | -------------------------------------------------------- |
| `0` | Straight / 字典攻击         | 默认模式，逐行读取字典文件（kali默认字典路径/usr/share/wordlist/rockyou.txt） |
| `1` | Combination             | 两个字典的组合                                                  |
| `3` | Brute-force / 掩码攻击      | 遍历所有可能组合                                                 |
| `6` | Hybrid: wordlist + mask | 字典 + 掩码后缀                                                |
| `7` | Hybrid: mask + wordlist | 掩码前缀 + 字典                                                |
| `9` | Association             | 使用关联攻击                                                   |

### 常用 hash 类型 `-m`

| 值 | hash 类型 |
|---|---|
| `0` | MD5 |
| `100` | SHA1 |
| `1400` | SHA2-256 |
| `1700` | SHA2-512 |
| `1000` | NTLM |
| `3000` | LM |
| `3200` | bcrypt, Blowfish (Unix) |
| `1800` | sha512crypt (Unix) |
| `500` | md5crypt (Unix) |
| `11600` | 7-Zip |
| `12500` | RAR3-hp |
| `13000` | RAR5 |
| `13600` | WinZip / ZIP |
| `17200` | PKZIP (Compressed) |
| `17210` | PKZIP (Uncompressed) |
| `17220` | PKZIP (Compressed Multi-Volume) |
| `17225` | PKZIP (Mixed Multi-File) |
| `17230` | PKZIP (Mixed Uncompressed) |
| `22000` | WPA-PBKDF2-PMKID+EAPOL |
| `22001` | WPA-PMK-PMKID+EAPOL |
| `13400` | KeePass 1/2 |
| `13711` | VeraCrypt HMAC-SHA256 |
| `13721` | VeraCrypt HMAC-SHA512 |

> hashcat 全部支持类型：`hashcat --help`

### 基本使用

```bash
# 字典攻击：破解 NTLM hash
hashcat -m 1000 -a 0 'hash值或含hash值的文件' wordlist.txt

# 指定 GPU 设备并输出结果
hashcat -m 1000 -a 0 -d 1 -o cracked.txt hash.txt wordlist.txt

# 掩码攻击（暴力破解 8 位纯数字）
hashcat -m 0 -a 3 hash.txt ?d?d?d?d?d?d?d?d

# 查看已破解结果
hashcat -m 1000 --show hash.txt

# 列出可用的 GPU/CPU 设备
hashcat -I
```

---

## 典型工作流：破解压缩包密码

### 步骤一：用 JtR 提取 hash

```powershell
# Windows 下使用 john-1.9.0-jumbo-1-win64
cd john-1.9.0-jumbo-1-win64\run

# ZIP 包
zip2john.exe D:\target.zip > D:\zip_hash.txt

# RAR 包
rar2john.exe D:\target.rar > D:\rar_hash.txt

# 7z 包
7z2john.exe D:\target.7z > D:\7z_hash.txt
```

### 步骤二：分析 hash 类型，确定 hashcat -m 值

打开提取出的 hash 文件，查看前缀：

| hash 前缀（部分） | 类型 | hashcat -m |
|---|---|---|
| `$pkzip2$...` | PKZIP 压缩 | `17200` 或 `17210` |
| `$pkzip$...` | WinZip | `13600` |
| `$rar5$...` | RAR5 | `13000` |
| `$rar3$...` | RAR3-hp | `12500` |
| `$7z$...` | 7-Zip | `11600` |

> 不确定类型时，可将 hash 提交到 [hashcat.net](https://hashcat.net/wiki/doku.php?id=example_hashes) 或 [hashes.com](https://hashes.com/en/tools/hash_identifier) 在线识别。

### 步骤三：用 hashcat 破解

```bash
# 字典攻击（默认 -a 0）
hashcat -m 17200 -a 0 zip_hash.txt rockyou.txt

# 指定 GPU + 优化
hashcat -m 17200 -a 0 -d 1 -w 4 -O -o result.txt zip_hash.txt rockyou.txt

# 掩码攻击（尝试 6 位数字密码）
hashcat -m 17200 -a 3 zip_hash.txt ?d?d?d?d?d?d
```

### 步骤四：查看结果

```bash
hashcat -m 17200 --show zip_hash.txt
```

---

## Kali Linux 中的对应工具

Kali 预装了 JtR (jumbo) 和 hashcat，命令名略有不同：

```bash
# Kali 中 *2john 工具的命令名风格
zip2john target.zip > hash.txt
rar2john target.rar > hash.txt
7z2john target.7z > hash.txt

# 或通过 john 直接调用
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# hashcat 用法一致
hashcat -m 17200 hash.txt /usr/share/wordlists/rockyou.txt
```

---

## 常用字典

| 字典                   | 说明                                                     |
| -------------------- | ------------------------------------------------------ |
| `rockyou.txt`        | 经典泄露密码合集（Kali 内置路径：`/usr/share/wordlists/rockyou.txt`） |
| `SecLists`           | GitHub 上最大的安全字典集                                       |
| `hashcat` 自带 `dict/` | 安装目录下的示例字典                                             |

---

## 常用掩码字符（-a 3 掩码攻击）

| 掩码 | 含义 |
|---|---|
| `?l` | 小写字母 a-z |
| `?u` | 大写字母 A-Z |
| `?d` | 数字 0-9 |
| `?s` | 特殊字符 |
| `?a` | 所有可打印字符 (?l + ?u + ?d + ?s) |
| `?b` | 0x00 - 0xff |

自定义字符集：`-1 ?l?d ?1?1?1?1` 表示由小写字母和数字组成的 4 位密码。

---

## 参考资料

- [[中网信安/Hashcat密码破解.pdf]]
