# Linux 包管理器

> 不同 Linux 发行版用的包管理器不一样，核心原因就一个：软件打包格式和依赖管理方式不同。拿到一台陌生的 Linux 机器，先搞清楚它是哪个家族的，然后就知道该用什么命令装软件。

---

## 为什么会有这么多包管理器

Linux 世界有两个主流软件包格式：`.deb` 和 `.rpm`。Debian 系用前者，Red Hat 系用后者。后来 Arch 自己搞了一套，Alpine 为了精简也自己搞了一套，Gentoo 走源码编译路线又不一样。

底层打包工具和上层包管理器是两回事。`dpkg` 和 `rpm` 只管装包拆包，不管依赖。`apt` 和 `dnf` 坐在它们上面，帮你自动解决依赖、下载更新。就像 `pip` 和 `pip-tools` 的关系——一个只管装，一个帮你算依赖树。

如果你只用过 Ubuntu 的 `apt install`，换到 CentOS 上敲同样的命令会提示 command not found。所以把常见发行版的包管理命令搞清楚，换环境的时候不会懵。

---

## Debian 系（Debian / Ubuntu / Kali / Raspberry Pi OS）

底层工具是 `dpkg`，上层是 `apt`（老系统上还有 `apt-get`，功能差不多）。

### dpkg

`dpkg` 直接操作 `.deb` 文件，不处理依赖。

**安装与卸载：**

```bash
dpkg -i package.deb                        # 安装一个 deb 包
dpkg -i --force-depends package.deb        # 忽略依赖警告强行安装
dpkg -i --force-confold package.deb        # 安装时保留旧配置文件（不覆盖）
dpkg -i --force-confnew package.deb        # 安装时用新配置文件覆盖旧的
dpkg -r package_name                       # 卸载，保留配置文件
dpkg -P package_name                       # 彻底卸载（连配置文件一起删）
dpkg --configure -a                        # 修复中断的安装——偶遇"dpkg was interrupted"时用
dpkg --audit                              # 检查所有已安装包的完整性
```

**查询已安装的包：**

```bash
dpkg -l                                    # 列出所有已安装的包
dpkg -l | grep keyword                     # 名称/描述模糊搜索
dpkg -l 'linux-*'                          # 支持通配符
dpkg -s package_name                       # 查看包的详细状态（版本、依赖、描述）
dpkg -L package_name                       # 列出这个包安装了哪些文件
dpkg -S /path/to/file                      # 反向查——这个文件属于哪个包
dpkg -S /usr/bin/ssh                       # 快速判断 ssh 命令来自哪个包
dpkg --get-selections                      # 导出所有已安装包的名称和状态
dpkg --get-selections > packages.list      # 备份包列表，方便迁移系统
dpkg --set-selections < packages.list      # 批量恢复包安装状态
dpkg --get-selections | grep -v deinstall  # 只看实际已安装的（排除已标记删除的）
```

**查看未安装的 .deb 文件信息：**

```bash
dpkg -I package.deb                        # 查看 deb 文件的元信息（包名、版本、依赖）
dpkg -c package.deb                        # 列出 deb 文件里面有哪些文件（不解包）
dpkg --info package.deb                    # 同 -I，输出格式稍不同
dpkg --contents package.deb                # 同 -c
```

**比较版本号：**

```bash
dpkg --compare-versions "2.0.1" lt "2.1.0" && echo "older"   # 版本比较，脚本里用
```

### apt

日常用的基本都是 apt。下面按实际操作场景分组，把常用参数列全。

**安装：**

```bash
apt install package_name                   # 基础安装
apt install -y package_name                # 跳过确认提示（脚本必备）
apt install --no-install-recommends pkg    # 只装必须的依赖，不装"推荐"的包——省磁盘
apt install --install-suggests pkg         # 连"建议"的包一起装（极少用）
apt install --dry-run package_name         # 模拟安装，只看会装/删哪些包，不动系统
apt install -f                            # 修复损坏的依赖关系
apt install --reinstall package_name       # 重新安装（配置文件丢了的时候有用）
apt install --download-only package_name   # 只下载 deb 到 /var/cache/apt/archives/，不安装
apt install package_name=version           # 安装指定版本
apt install ./package.deb                  # 安装本地 deb 文件（自动解决依赖，比 dpkg -i 省心）
```

**更新与升级：**

```bash
apt update                                 # 刷新软件源列表（改 sources.list 后必须先跑这个）
apt list --upgradable                      # 看看有哪些包可以升级
apt list --upgradable -a                   # 列出可升级的包及所有可用版本
apt upgrade                                # 升级所有包（不删旧包、不装新依赖）
apt upgrade -y                            # 自动确认，脚本用
apt full-upgrade                           # 更彻底的升级——如果依赖冲突，会删掉旧包来迁就新版本
apt upgrade --dry-run                      # 模拟升级，看看会动哪些包
```

**卸载与清理：**

```bash
apt remove package_name                    # 卸载，保留配置文件
apt purge package_name                     # 卸载，配置文件也删掉
apt autoremove                             # 删掉不再需要的依赖（孤立的 lib 之类）
apt autoremove --purge                     # 连孤立包的配置文件一起清理
apt autoclean                              # 删除 /var/cache/apt/archives/ 里的旧版本 deb 缓存
apt clean                                  # 清空全部 deb 缓存（释放磁盘，但下次装包又要重新下载）
```

**搜索与信息：**

```bash
apt search keyword                         # 按包名和描述搜索
apt search --names-only keyword            # 只搜包名，不搜描述
apt show package_name                      # 查看包的详细信息（版本、大小、依赖、描述）
apt show -a package_name                   # 列出所有可用版本的信息
apt list --installed                       # 列出已安装的包
apt list --installed | grep keyword        # 查某个包装了没有
apt list --upgradable                      # 列出可升级的包
apt depends package_name                   # 查看包的依赖树
apt rdepends package_name                  # 反向查看——哪些包依赖了它
apt policy package_name                    # 查看包的安装状态和所有可用版本的优先级
apt-cache policy package_name              # 同上，老写法，输出更详细
```

**锁定包版本（防止升级）：**

```bash
apt-mark hold package_name                 # 锁定版本，apt upgrade 不会动它
apt-mark unhold package_name               # 解除锁定
apt-mark showhold                          # 查看所有被锁定的包
apt-mark auto package_name                 # 标记为自动安装（不再被依赖时会被 autoremove 删掉）
apt-mark manual package_name               # 标记为手动安装（不受 autoremove 影响）
apt-mark showmanual                        # 查看手动安装的包
```

**源管理：**

`/etc/apt/sources.list` 和 `/etc/apt/sources.list.d/` 下面是软件源配置。如果 `apt update` 报错，一般先去检查这两个地方的源地址有没有写错。

```bash
# 查看当前使用的源
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/

# 添加外部源（以 Docker 为例）
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list

# 添加 PPA（仅 Ubuntu，个人维护的第三方源）
add-apt-repository ppa:user/name
add-apt-repository --remove ppa:user/name   # 移除 PPA
```

### apt 和 apt-get 的区别

`apt` 是后来出的，把 `apt-get` 和 `apt-cache` 的常用命令合并到了一起，输出加了进度条，看着舒服点。写脚本的时候还是推荐用 `apt-get`，因为它的输出格式更稳定，不会随便改。功能上两个都能完成同样的任务。

---

## Red Hat 系（RHEL / CentOS / Fedora / Rocky / Alma）

底层是 `rpm`，上层是 `dnf`（Fedora 22+ 和 RHEL 8+ 用 dnf，老系统用 `yum`）。

### rpm

和 `dpkg` 一样，`rpm` 直接操作 `.rpm` 文件，不管依赖。

**安装与卸载：**

```bash
rpm -ivh package.rpm                       # 安装（i=install, v=verbose, h=显示进度条）
rpm -Uvh package.rpm                       # 升级安装——如果没装过就安装，装过就升级
rpm -Fvh package.rpm                       # 仅升级——已装过的才更新，没装过的跳过
rpm -ivh --test package.rpm                # 模拟安装，检查依赖冲突但不实际写入
rpm -ivh --nodeps package.rpm              # 忽略依赖强行安装（不推荐，但偶尔有用）
rpm -ivh --force package.rpm               # 强制覆盖已安装的文件
rpm -ivh --replacepkgs package.rpm         # 重新安装已装过的包
rpm -ivh --prefix=/opt/custom package.rpm  # 安装到自定义路径（仅支持 relocatable 的包）
rpm -e package_name                        # 卸载
rpm -e --test package_name                 # 模拟卸载，看会有什么依赖报错
rpm -e --nodeps package_name               # 忽略依赖强制卸载
```

**查询已安装的包：**

```bash
rpm -qa                                    # 列出所有已安装的包
rpm -qa | grep keyword                     # 模糊搜索
rpm -qa --last                             # 按安装时间排序，最近装的排前面
rpm -qi package_name                       # 查看包信息（版本、描述、安装时间）
rpm -ql package_name                       # 列出包安装的所有文件
rpm -qc package_name                       # 只列出配置文件（如 nginx.conf）
rpm -qd package_name                       # 只列出文档文件（man page、README）
rpm -qf /path/to/file                      # 反向查——这个文件属于哪个包
rpm -q --changelog package_name            # 查看包的更新日志
rpm -q --requires package_name             # 查看包依赖了哪些东西
rpm -q --provides package_name             # 查看这个包提供了哪些能力
rpm -q --scripts package_name              # 查看包的安装/卸载脚本（pre/post scripts）
rpm -q --configfiles package_name          # 查看包会安装哪些配置文件
rpm -q --dump package_name                 # 列出所有文件的详细信息（路径、权限、MD5）
rpm --verify package_name                  # 验证包安装后的文件是否被修改（对比 MD5、权限）
rpm --verify --nomtime package_name        # 同上，但不检查修改时间（很多人会改 mtime）
rpm -Va                                    # 验证所有已安装包的完整性
```

**查看未安装的 .rpm 文件信息：**

```bash
rpm -qpi package.rpm                       # 查看 rpm 文件的包信息
rpm -qpl package.rpm                       # 列出 rpm 文件里的内容
```

### dnf

`dnf` 是 `yum` 的继任者，依赖解析更快，API 更干净。RHEL 8 / CentOS 8 开始默认用 `dnf`，但为了兼容，敲 `yum` 也会被重定向到 `dnf`。

**安装：**

```bash
dnf install package_name                   # 安装
dnf install -y package_name                # 跳过确认（脚本用）
dnf install --nogpgcheck package_name      # 跳过 GPG 签名检查（非官方源偶尔需要）
dnf install --downloadonly package_name    # 只下载 rpm 到缓存目录，不安装
dnf install --downloaddir=./pkgs pkg       # 下载 rpm 到指定目录
dnf install package_name-version           # 安装指定版本
dnf install ./package.rpm                  # 安装本地 rpm 文件（会自动解决依赖）
dnf reinstall package_name                 # 重新安装（配置文件丢了或被改坏了）
dnf downgrade package_name                 # 降级到上一个可用版本
```

**更新与升级：**

```bash
dnf check-update                           # 检查有哪些包可以升级
dnf update                                 # 升级所有包
dnf update -y                             # 跳过确认
dnf update --security                     # 只安装安全更新
dnf update --exclude=kernel*              # 排除某些包不升级
dnf update package_name                   # 只升级指定包
dnf updateinfo list                       # 查看可用的安全公告
dnf upgrade                                # 同 update，Fedora 下 upgrade 可处理过时依赖
```

**卸载与清理：**

```bash
dnf remove package_name                    # 卸载
dnf remove --noautoremove package_name     # 只卸载本包，不级联删依赖
dnf autoremove                             # 删掉没用的依赖
dnf clean all                             # 清空所有缓存（下载的 rpm、元数据）
dnf clean packages                        # 只清 rpm 包缓存
dnf clean metadata                        # 只清元数据缓存
dnf makecache                             # 重新生成缓存（换源后跑一下）
```

**搜索与信息：**

```bash
dnf search keyword                         # 按包名和描述搜索
dnf search --name keyword                 # 只搜包名
dnf info package_name                      # 查看包详细信息
dnf list installed                         # 列出已安装
dnf list available                         # 列出所有可安装的
dnf list --recent                          # 列出最近添加的包（小于 7 天）
dnf provides /path/to/file                 # 反向查——哪个包提供了这个文件
dnf provides */bin/ssh                     # 查找哪个包提供了 ssh 命令
dnf repoquery --deplist package_name       # 查看包的依赖关系
dnf repoquery --whatrequires package_name  # 反向查——哪些包依赖了它
dnf history                                # 查看 dnf 操作历史（安装/卸载/升级记录）
dnf history info 42                        # 查看第 42 次操作的具体内容
dnf history undo 42                        # 撤销第 42 次操作（回滚神器）
```

**软件组管理：**

```bash
dnf group list                             # 列出所有软件组
dnf group list --hidden                    # 含隐藏的软件组
dnf group info "Development Tools"         # 查看软件组包含哪些包
dnf groupinstall "Development Tools"       # 安装整组软件
dnf groupinstall -y "Server with GUI"     # 跳过确认
dnf groupremove "Development Tools"        # 卸载整组
```

**源管理：**

```bash
dnf repolist                               # 列出已启用的软件源
dnf repolist all                           # 列出所有源（含禁用的）
dnf repolist -v                            # 查看每个源的详细信息（URL、包数量）
dnf --enablerepo=epel install pkg          # 临时启用某个源来安装
dnf --disablerepo=base install pkg         # 临时禁用某个源
dnf config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo             # 新增一个源
dnf config-manager --enable epel           # 永久启用某个源
dnf config-manager --disable epel          # 永久禁用某个源
```

### yum 换源

国内用 CentOS 官方源慢得离谱，一般都换成阿里云或者清华的镜像源。

```bash
# 备份原有源
cp /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak

# 下载阿里云镜像源（以 CentOS 7 为例）
wget -O /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo

# 刷新缓存
yum makecache
yum repolist                               # 确认源已生效
```

### EPEL 源

EPEL（Extra Packages for Enterprise Linux）是 Red Hat 官方维护的额外软件源，很多常用软件（nginx、htop、fish shell）在官方源里没有，在 EPEL 里有。

```bash
dnf install -y epel-release                # RHEL 8+ / CentOS 8+
yum install -y epel-release                # RHEL 7 / CentOS 7

# CentOS 7 也可以手动装
rpm -ivh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# 确认 EPEL 已启用
dnf repolist | grep epel
```

---

## Arch 系（Arch Linux / Manjaro / EndeavourOS）

Arch 用 `pacman`，设计哲学是简单直接，一个命令搞定所有事。Arch 还有一个 AUR（Arch User Repository），上面几乎有所有你能想到的软件，由社区维护。

### pacman

**安装：**

```bash
pacman -S package_name                     # 安装
pacman -S --noconfirm package_name         # 跳过确认提示（脚本用）
pacman -S --needed package_name            # 如果已装过就跳过
pacman -S --needed --noconfirm git base-devel  # 脚本里最常见的组合
pacman -S --ignore=kernel* package_name    # 忽略某些依赖的升级冲突
pacman -S package1 package2                # 一次装多个
pacman -U package.pkg.tar.zst              # 安装本地包
pacman -Sw package_name                    # 只下载包不安装（-w = download only）
```

**更新与升级：**

```bash
pacman -Syu                                # 全面升级（-Sy 刷新数据库，-u 升级）
pacman -Syu --noconfirm                    # 跳过确认
pacman -Syu --ignore=linux                 # 排除内核升级（有些驱动依赖特定内核版本）
pacman -Syyu                               # 强制刷新数据库（即使本地看起来是最新的）
pacman -Syuu                               # 允许降级（如果远程版本比本地旧也换过去）
pacman -Syu --overwrite '/boot/*'          # 允许覆盖指定路径的文件（冲突时用）
```

**卸载：**

```bash
pacman -R package_name                     # 卸载，保留依赖
pacman -Rs package_name                    # 卸载 + 删除不再被其他包使用的依赖
pacman -Rns package_name                   # 卸载 + 删依赖 + 删配置文件（最常用的卸载方式）
pacman -Rdd package_name                   # 强制卸载，跳过所有依赖检查（极度危险）
pacman -Rsc package_name                   # 级联卸载——依赖此包的其他包也一并删除
```

**搜索与信息：**

```bash
pacman -Ss keyword                         # 搜索远程仓库（包名和描述）
pacman -Qs keyword                         # 搜索本地已安装的包
pacman -Qi package_name                    # 查看本地已安装包的详细信息
pacman -Si package_name                    # 查看远程仓库包的详细信息
pacman -Ql package_name                    # 列出这个包安装了哪些文件
pacman -Qo /path/to/file                   # 反向查——这个文件属于哪个本地包
pacman -Fy                                  # 同步文件数据库（用 -F 搜文件前得先跑一次这个）
pacman -F keyword                          # 按文件名搜索远程仓库（例如 pacman -F /usr/bin/ssh）
pacman -Fl package_name                    # 列出远程包包含哪些文件（不下载）
pacman -Q                                  # 列出所有已安装的包
pacman -Qe                                 # 只列出手动安装的包
pacman -Qd                                 # 只列出作为依赖安装的包
pacman -Qm                                 # 只列出不在官方仓库的包（AUR 或手动装的）
pacman -Qt                                 # 只列出未被任何包依赖的孤立包
pacman -Qdtq                               # 仅输出孤立包名（配合管道删除）——q 是 quiet，只出包名
pacman -Q > pkglist.txt                    # 导出已安装包列表（迁移用）
pacman -S - < pkglist.txt                  # 从列表批量安装（-S - 从 stdin 读包名）
```

**缓存清理：**

```bash
pacman -Sc                                 # 清理未安装包的缓存（保留当前版本）
pacman -Scc                                # 清理全部缓存（释放磁盘，但无法降级）
paccache -r                                # 保留最近 3 个版本，删更早的（需要 pacman-contrib 包）
paccache -rk 1                             # 只保留最近 1 个版本
paccache -d                                # 模拟运行——看看会删哪些
du -sh /var/cache/pacman/pkg/              # 先看看缓存占了多大
```

**数据库操作：**

```bash
pacman -Dk                                 # 检查依赖完整性
sudo pacman -D --asdeps package_name       # 把一个包标记为"依赖安装"（会被 Rs 级联删除）
sudo pacman -D --asexplicit package_name   # 标记为"手动安装"（不会被 Rs 删掉）
```

pacman 的命令选项用大写字母，和 apt/dnf 的风格不太一样。刚开始容易忘，多敲几次就记住了。

### AUR 和 yay

AUR 里的包是社区用户上传的 PKGBUILD 脚本，不是预编译的二进制。你得手动 `git clone` 然后 `makepkg -si` 编译安装。嫌麻烦的话装个 AUR 助手，`yay` 用得最多。

```bash
# 安装 yay（需要先装 git 和 base-devel）
sudo pacman -S --needed --noconfirm git base-devel
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si --noconfirm                    # -s 自动装依赖，-i 编译完自动安装

# 日常使用——语法和 pacman 几乎一样
yay -S package_name                        # 搜索并安装（AUR + 官方仓库都搜）
yay -S --noconfirm package_name            # 跳过所有确认（编译问是否看 PKGBUILD 也跳过）
yay -Syu                                   # 全面升级（官方仓库 + AUR 包一起升）
yay -Sua                                   # 只升级 AUR 包
yay -Ss keyword                            # 搜索
yay -Si package_name                       # 查看包信息
yay -Rs package_name                       # 卸载+清理依赖
yay -Rns package_name                      # 卸载+清理依赖+删配置
yay -Yc                                    # 清理 AUR 构建缓存
yay -Ps                                    # 显示系统统计（装了多少包、AUR 包几个）
yay --editmenu                             # 升级时显示 diff 菜单（可以看 PKGBUILD 变更）
```

**其他 AUR 助手：**
`paru` 是 Rust 重写版 yay，功能差不多。`pamac` 是 Manjaro 自带的图形化+命令行合一的包管理器。

---

## openSUSE 系

openSUSE 用 `zypper`，底层也是 rpm 格式，但上层包装了自己的逻辑。zypper 有个独有的功能：安装某个包后如果反悔了，可以回滚到安装前的快照（依赖 btrfs 和 snapper）。

```bash
# 更新
zypper refresh                             # 刷新软件源（同 apt update）
zypper ref                                 # 缩写
zypper update                              # 升级所有包
zypper up                                  # 缩写
zypper update -y                          # 跳过确认
zypper dup                                 # 发行版升级（大版本迁移，如 15.4→15.5）
zypper dup --from repo-name               # 从指定源升级

# 安装
zypper install package_name                # 安装
zypper in package_name                     # 缩写
zypper install -y package_name             # 跳过确认
zypper install --no-recommends pkg         # 不装推荐的依赖
zypper install --download-only pkg         # 只下载不安装
zypper install --force pkg                 # 强制重新安装
zypper install package-version             # 安装指定版本

# 卸载
zypper remove package_name                 # 卸载
zypper rm package_name                     # 缩写
zypper remove --clean-deps package_name    # 卸载时连带清理不再需要的依赖

# 搜索与信息
zypper search keyword                      # 搜索
zypper se keyword                          # 缩写
zypper se --details keyword                # 搜索并显示详细信息
zypper se --installed-only keyword         # 只搜已安装的
zypper se --provides /path/to/file         # 反向查——哪个包提供了这个文件
zypper info package_name                   # 查看包详细信息
zypper if package_name                     # 缩写
zypper patches                             # 查看可用补丁
zypper list-updates                        # 列出可更新的包

# 源管理
zypper repos                               # 列出所有源
zypper lr                                  # 缩写
zypper lr -d                               # 详细信息（含 URL 和优先级）
zypper addrepo URL alias                   # 添加源
zypper ar URL alias                        # 缩写
zypper removerepo alias                    # 移除源
zypper modifyrepo --enable alias           # 启用源
zypper modifyrepo --disable alias          # 禁用源
zypper modifyrepo --priority 10 alias      # 设置源优先级（数字越小优先级越高）

# 包锁定
zypper addlock package_name                # 锁定包版本
zypper removelock package_name             # 解除锁定
zypper locks                               # 查看所有已锁定的包

# 进程检查（更新后检查哪些进程还在用旧文件）
zypper ps                                  # 显示哪些运行中的进程在用已删除/更新的文件
zypper ps -s                               # 简短格式
```

### opi

openSUSE 有一个类似 AUR 的社区源叫 OBS（Open Build Service）。`opi` 工具可以方便地从 OBS 搜索并安装软件。

```bash
sudo zypper install opi                    # 先装 opi
opi package_name                           # 从 OBS 搜索并安装
opi -n package_name                        # 非交互模式
```

---

## Alpine Linux

Alpine 为了极简，不用 glibc 而用 musl libc，包管理用 `apk`。Docker 镜像里经常见到它——`alpine` 镜像只有 5MB 左右。`apk` 这个工具本身就很小，执行速度很快。

```bash
# 更新
apk update                                 # 刷新索引
apk upgrade                                # 升级所有包
apk upgrade --available                    # 即使本地已是最新也强制检查升级

# 安装
apk add package_name                       # 安装
apk add --no-cache package_name            # 安装时不缓存（Dockerfile 里必用，减镜像体积）
apk add -u package_name                    # 如果已装就升级到最新
apk add package1 package2                  # 一次装多个
apk add --virtual .build-deps gcc make     # 创建虚拟包分组——方便批量卸载构建依赖
apk del .build-deps                        # 卸载整个虚拟包分组（构建完成后的清理步骤）
apk add package_name=version               # 安装指定版本

# 卸载
apk del package_name                       # 卸载
apk del package1 package2                  # 批量卸载

# 搜索与信息
apk search keyword                         # 搜索
apk search -v keyword                      # 搜并显示版本号
apk search -d keyword                      # 搜描述（默认只搜包名）
apk info package_name                      # 查看包信息
apk info -a package_name                   # 列出所有可用版本
apk info -L package_name                   # 列出包安装的文件
apk info -r package_name                   # 反向查——哪些包依赖了它
apk info --who-owns /path/to/file          # 反向查——这个文件属于哪个包
apk info -v                                # 列出所有已安装的包及版本
apk list --installed                       # 列出已安装
apk policy package_name                    # 查看包的仓库来源和版本策略

# 缓存管理
apk cache clean                            # 清空包缓存（释放磁盘）
apk cache download                         # 只下载包到缓存
apk cache -v sync                          # 清理不在索引中的旧缓存
```

**Dockerfile 中 Alpine 的经典写法：**

```dockerfile
FROM alpine:3.20
RUN apk add --no-cache python3 py3-pip
# --no-cache 省掉 /var/cache/apk 下的缓存，减小镜像体积
# 不需要再跑 apk update，因为 --no-cache 会自动 fetch 最新索引

# 如果你需要编译点什么，用虚拟包分组
RUN apk add --no-cache --virtual .build-deps gcc musl-dev make \
    && make \
    && apk del .build-deps
# 构建完成就把编译工具链删干净，镜像里不留多余的
```

---

## Gentoo 系

Gentoo 走源码编译路线，包管理器叫 `portage`，日常用 `emerge` 命令。装一个软件 = 下载源码 + 本地编译 + 安装，好处是你可以精确控制编译选项（USE flags），坏处是装个大软件可能等半小时。

```bash
# 同步包树
emerge --sync                              # 更新 portage 树
emerge-webrsync                            # 首次用全量抓包树（不用 git pull）

# 安装
emerge package_name                        # 安装
emerge -pv package_name                    # 模拟安装——看会拉进什么依赖、启用哪些 USE flag（常用！）
emerge -av package_name                    # 模拟 + 确认提示（-a=ask, -v=verbose，推荐日常用）
emerge --oneshot package_name              # 安装但不记录到 world 集（当依赖用的包）
emerge --fetchonly package_name            # 只下载源码不编译
emerge package_name=version                # 安装指定版本

# 卸载
emerge --unmerge package_name              # 卸载
emerge --depclean                          # 清理不再被依赖的孤立包
emerge --depclean -pv                      # 模拟——看看会删哪些，再决定要不要真删

# 升级
emerge -uD world                           # 升级整个系统（-u=update, -D=deep 递归检查依赖）
emerge -uDN world                          # 加 -N=--newuse，如果 USE flag 变了就重新编译
emerge -uDNav world                        # 再加 -a=ask 确认，-v=verbose 详细输出
emerge -uD --with-bdeps=y @world          # 连构建依赖一起升级
emerge -e world                            # 完全重建所有包（-e=empty-tree，彻底重装）

# 搜索与信息
emerge --search keyword                    # 按包名搜索
emerge --searchdesc keyword                # 按描述搜索（更慢但更全）
emerge -s keyword                          # 同上，缩写
equery list package_name                   # 查看包安装了哪些文件（需要 gentoolkit）
equery files package_name                  # 同上
equery depends package_name                # 反向查——哪些包依赖了它
equery uses package_name                   # 查看包有哪些 USE flag
equery size package_name                   # 查看包的磁盘占用
eix keyword                                # 快速搜索（需要安装 eix 工具，比 emerge --search 快得多）
eix -c keyword                             # 简洁输出模式

# USE flag 管理
# USE flag 定义在 /etc/portage/make.conf 和 /etc/portage/package.use/
# 修改后影响后续编译行为
emerge --info package_name                 # 查看包的实际 USE flag 状态
ufed                                       # 交互式 USE flag 管理器（需要 gentoolkit）
euse -a                                    # 查看所有的全局 USE flag 描述
euse -i flag                               # 查看某个 flag 的描述

# 配置更新（升级后处理 ._cfg0000_ 配置文件）
dispatch-conf                              # 交互式合并新旧配置（推荐）
etc-update                                 # 同上，界面更老派
find /etc -name '._cfg*'                   # 手动找到需要合并的配置文件

# 关键字（ACCEPT_KEYWORDS）——允许安装不稳定分支的包
# 放在 /etc/portage/package.accept_keywords/ 目录下
echo "=dev-lang/python-3.12.1 ~amd64" >> /etc/portage/package.accept_keywords/python
# ~amd64 表示接受 testing 分支，** 表示接受所有（包括 masked）
```

**portage 目录结构概览：**

```
/etc/portage/
  make.conf           # 全局配置——USE flag、CFLAGS、MAKEOPTS(-j 并行编译数)
  package.use/        # 按包设置 USE flag
  package.accept_keywords/   # 接受非稳定包
  package.mask/       # 禁止安装特定版本
  package.unmask/     # 允许被系统禁掉的包
  repos.conf/         # 软件源配置
  sets/               # 自定义包集合
```

---

## 常用操作对照表

| 操作 | Debian (apt) | RHEL (dnf) | Arch (pacman) | Alpine (apk) |
|------|-------------|-----------|--------------|-------------|
| 刷新源 | `apt update` | `dnf makecache` | `pacman -Sy` | `apk update` |
| 升级系统 | `apt upgrade` | `dnf update` | `pacman -Syu` | `apk upgrade` |
| 安装 | `apt install pkg` | `dnf install pkg` | `pacman -S pkg` | `apk add pkg` |
| 跳过确认 | `apt install -y pkg` | `dnf install -y pkg` | `pacman -S --noconfirm pkg` | `apk add --no-cache pkg` |
| 安装本地包 | `apt install ./pkg.deb` | `dnf install ./pkg.rpm` | `pacman -U pkg.pkg.tar.zst` | N/A |
| 卸载 | `apt remove pkg` | `dnf remove pkg` | `pacman -R pkg` | `apk del pkg` |
| 彻底卸载 | `apt purge pkg` | `dnf remove pkg` | `pacman -Rns pkg` | `apk del pkg` |
| 搜索 | `apt search kw` | `dnf search kw` | `pacman -Ss kw` | `apk search kw` |
| 查看信息 | `apt show pkg` | `dnf info pkg` | `pacman -Si pkg` | `apk info pkg` |
| 列出已安装 | `apt list --installed` | `dnf list installed` | `pacman -Q` | `apk info -v` |
| 文件归属 | `dpkg -S /path` | `rpm -qf /path` | `pacman -Qo /path` | `apk info --who-owns /path` |
| 列出包文件 | `dpkg -L pkg` | `rpm -ql pkg` | `pacman -Ql pkg` | `apk info -L pkg` |
| 清理无用依赖 | `apt autoremove` | `dnf autoremove` | `pacman -Rns $(pacman -Qdtq)` | `apk del pkg` (手动) |
| 清理缓存 | `apt clean` | `dnf clean all` | `pacman -Scc` | `apk cache clean` |
| 锁定版本 | `apt-mark hold pkg` | `dnf versionlock add pkg` | 编辑 `/etc/pacman.conf` IgnorePkg | `apk add pkg=1.0` (钉住版本) |

## 拿到陌生机器怎么判断

进终端后按顺序试这几个命令：

```bash
cat /etc/os-release                        # 看发行版 ID 和 ID_LIKE，最可靠
which apt && echo "Debian family"
which dnf && echo "RHEL family (modern)"
which yum && echo "RHEL family (legacy)"
which pacman && echo "Arch family"
which zypper && echo "openSUSE"
which apk && echo "Alpine"
which emerge && echo "Gentoo"
```

`/etc/os-release` 是 systemd 的标准文件，所有现代 Linux 发行版都有，里面的 `ID` 和 `ID_LIKE` 字段直接告诉你这是哪个家族的。
