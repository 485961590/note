# Git 使用笔记

> Git 是分布式版本控制系统——记录每次修改、自由切换版本、多人并行协作。

---

## 三个区域

理解 Git 首先要理解三个区域：

```
工作目录                    暂存区                     本地仓库
(Working Dir)  --add-->  (Staging)  --commit-->  (Repository)
    │                        │                        │
    └────────────────────────┴────────────────────────┘
                     直接 commit -a 跳过暂存
```

| 区域   | 说明        | 对应操作         |
| ---- | --------- | ------------ |
| 工作目录 | 你正在编辑的文件  | 写代码、改文件      |
| 暂存区  | 准备提交的快照   | `git add`    |
| 本地仓库 | 提交历史的永久记录 | `git commit` |

---

## 安装与初始配置

### 安装

```bash
# Ubuntu / Debian
sudo apt install git

# CentOS / RHEL
sudo dnf install git

# macOS
brew install git
```

### 用户信息（必配）

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### 常用配置

```bash
# 查看所有配置
git config --list

# 设置默认分支名为 main
git config --global init.defaultBranch main

# 设置默认编辑器
git config --global core.editor "vim"

# 启用颜色输出
git config --global color.ui auto

# 设置换行符处理（Windows 下推荐）
git config --global core.autocrlf true    # Windows
git config --global core.autocrlf input   # Linux/macOS

# 设置别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.lg "log --oneline --graph --all"
```

配置文件位置：
- 全局：`~/.gitconfig`
- 项目级：`.git/config`

---

## 基础操作

### 创建仓库

```bash
# 在当前目录初始化
git init

# 克隆远程仓库
git clone https://github.com/user/repo.git
git clone git@github.com:user/repo.git          # SSH 方式
git clone -b branch-name <url>                  # 克隆指定分支
```

### 提交代码

```bash
# 查看文件状态
git status
git status -s                                    # 简短格式

# 将文件加入暂存区
git add file.txt
git add .                                        # 添加当前目录所有更改
git add -A                                       # 添加整个仓库所有更改

# 提交
git commit -m "修复登录页面的空指针异常"
git commit -am "跳过暂存区直接提交"                # 仅对已跟踪文件生效

# 修改上一次提交（未 push 时）
git commit --amend -m "新的提交信息"
git commit --amend --no-edit                      # 追加内容但不改信息
```

### 查看历史

```bash
# 查看提交日志
git log
git log --oneline                                # 一行一提交
git log --oneline --graph --all                  # 图形化分支树
git log -p -2                                    # 最近两次提交的 diff
git log --since="2026-06-01"                     # 时间范围
git log --author="name"                          # 按作者筛选
git log --grep="关键词"                            # 按提交信息搜索
git log -S "代码片段"                              # 按代码变更内容搜索

# 查看某次提交的详情
git show <commit-id>
git show HEAD                                    # 最新提交

# 查看谁修改了文件的每一行
git blame file.txt
git blame -L 10,20 file.txt                      # 只看第 10-20 行
```

### 查看差异

```bash
# 工作区 vs 暂存区
git diff

# 暂存区 vs 最新提交
git diff --staged
git diff --cached

# 工作区 vs 最新提交
git diff HEAD

# 两个提交之间
git diff <commit1> <commit2>

# 只看某文件的差异
git diff file.txt
```

---

## 分支管理

分支是 Git 最强大的特性——在独立线路上开发，不影响主线。

```bash
# 查看分支
git branch                  # 本地分支
git branch -a               # 含远程分支
git branch -v               # 含最后提交信息

# 创建分支
git branch feature-login
git checkout -b feature-login         # 创建并切换
git switch -c feature-login           # 同上（Git 2.23+，推荐）

# 切换分支
git checkout main
git switch main                       # 推荐（语义更清晰）

# 删除分支
git branch -d feature-login           # 安全删除（已合并）
git branch -D feature-login           # 强制删除（未合并也删）

# 重命名分支
git branch -m old-name new-name
```

### 合并（merge）

```bash
# 将 feature 分支合入当前分支
git checkout main
git merge feature-login

# 如果产生冲突，解决后
git add .
git commit                        # 或者 git merge --continue

# 取消合并
git merge --abort
```

### 变基（rebase）

把当前分支的提交"搬"到目标分支最新提交之后，保持历史线性：

```bash
# 将当前分支变基到 main
git checkout feature-login
git rebase main

# 冲突时
# 解决冲突 → git add . → git rebase --continue
# 跳过 → git rebase --skip
# 放弃 → git rebase --abort

# 交互式 rebase（合并、排序、修改提交）
git rebase -i HEAD~3              # 整理最近 3 次提交
```

**merge vs rebase：**

| | merge | rebase |
|---|---|---|
| 历史 | 保留分支拓扑（有合并节点） | 线性历史（更干净） |
| 安全性 | 高（不改变已有提交） | 改变了提交 hash |
| 适用 | 公共分支合入 | 个人分支整理后合入 |

> **原则：** 永远不要 rebase 已经 push 到远程的公共分支。

---

## 远程协作

```bash
# 查看远程仓库
git remote
git remote -v                       # 含 URL

# 添加远程仓库
git remote add origin https://github.com/user/repo.git

# 修改远程仓库 URL
git remote set-url origin git@github.com:user/repo.git

# 删除远程仓库
git remote remove origin
```

### 推送与拉取

```bash
# 推送当前分支到远程
git push origin main

# 首次推送并设置上游
git push -u origin main
# 之后只需 git push

# 拉取并合并（fetch + merge）
git pull

# 拉取并变基（fetch + rebase，推荐）
git pull --rebase

# 仅拉取不合并
git fetch origin

# 推送所有标签
git push --tags

# 强制推送（警告：覆盖远程历史，谨慎使用）
git push --force-with-lease          # 比 --force 安全
```

### Pull Request 流程

```
1. fork 原仓库到自己的账号
2. clone 自己 fork 的仓库
3. 创建新分支做修改
4. push 到自己仓库
5. 在 GitHub/GitLab 上发起 Pull Request
6. 代码评审 → 修改 → 合并
```

---

## 撤销与回退

### 工作区撤销

```bash
# 丢弃工作区单个文件的修改
git restore file.txt
git checkout -- file.txt             # 旧写法

# 丢弃工作区所有修改
git restore .
```

### 暂存区撤销

```bash
# 把文件从暂存区撤回到工作区（保留修改）
git restore --staged file.txt
git reset HEAD file.txt              # 旧写法

# 撤销所有暂存
git reset HEAD
```

### 提交撤销

```bash
# 撤销最近一次提交，修改保留在工作区
git reset --soft HEAD~1

# 撤销最近一次提交，修改保留在工作区（未暂存）
git reset --mixed HEAD~1             # 默认行为

# 撤销最近一次提交，修改全部丢弃（警告：不可逆）
git reset --hard HEAD~1

# 撤销最近 N 次提交
git reset --soft HEAD~3
```

### revert（安全撤销）

`revert` 创建一个新提交来"反向操作"，不修改历史，适合已 push 的提交：

```bash
# 撤销某次提交（生成一个新提交）
git revert <commit-id>

# 撤销一段连续的提交
git revert <oldest>..<newest>
```

**reset vs revert：**

| | reset | revert |
|---|---|---|
| 原理 | 移动 HEAD 指针，"抹掉"提交 | 创建新提交，内容是反向操作 |
| 历史 | 改变历史 | 保留完整历史 |
| 已 push 的提交 | 不建议 | 安全 |
| 适用 | 本地未 push 的提交 | 已 push 的提交 |

---

## 暂存（Stash）

临时保存当前修改，切换去做别的事，之后再恢复：

```bash
# 暂存当前修改
git stash
git stash save "描述信息"

# 查看暂存列表
git stash list

# 恢复最近一次暂存（不删除 stash 记录）
git stash apply

# 恢复最近一次暂存（删除 stash 记录）
git stash pop

# 恢复指定暂存
git stash apply stash@{2}

# 删除指定暂存
git stash drop stash@{1}

# 清空所有暂存
git stash clear

# 暂存所有文件（含未跟踪的）
git stash -u
```

典型场景：你在 feature 分支上写到一半，突然需要切到 main 修个紧急 bug：

```bash
git stash                    # 暂存手头工作
git checkout main
# 修 bug → commit → push
git checkout feature
git stash pop                # 恢复之前的工作
```

---

## 标签（Tag）

为提交打一个永久标记，常用于标记版本号：

```bash
# 创建轻量标签
git tag v1.0.0

# 创建附注标签（推荐，含作者、日期、说明）
git tag -a v1.0.0 -m "第一个正式版本"

# 为历史提交打标签
git tag -a v0.9.0 <commit-id> -m "公测版本"

# 查看标签
git tag
git tag -l "v1.*"                     # 通配符过滤
git show v1.0.0                       # 标签详情

# 推送标签
git push origin v1.0.0                # 推送单个
git push --tags                       # 推送全部

# 删除标签
git tag -d v1.0.0                     # 本地删除
git push origin --delete v1.0.0       # 远程删除
```

---

## .gitignore

告诉 Git 忽略哪些文件不纳入版本控制：

```bash
# .gitignore 示例
# 注释用 # 开头

# 忽略特定文件
secret.key
.env

# 忽略目录
node_modules/
dist/
__pycache__/

# 通配符
*.log
*.tmp
temp-*

# 但跟踪某特定文件（! 取反）
!important.log

# 忽略目录下所有，但保留目录结构
logs/*
!logs/.gitkeep
```

常用模板参考 [github.com/github/gitignore](https://github.com/github/gitignore)。

---

## .gitkeep

Git 不跟踪空目录。如果想让空目录纳入版本控制，在里面放一个 `.gitkeep` 文件：

```bash
mkdir logs
touch logs/.gitkeep
```

---

## 常用场景速查

### 场景 1：提交错了分支

```bash
# 当前在错误分支，已 commit
git log --oneline              # 记下要保留的 commit id
git checkout 正确分支
git cherry-pick <commit-id>    # 把提交复制过来
git checkout 错误分支
git reset --hard HEAD~1        # 把错误分支上的提交撤销
```

### 场景 2：合并多个零碎提交

```bash
git rebase -i HEAD~4
# 编辑器中将第 2-4 个 pick 改为 squash 或 s
# 保存后会让你编辑合并后的提交信息
```

### 场景 3：某次 commit 后所有测试都挂了，定位引入问题的提交

```bash
git bisect start
git bisect bad                 # 当前版本有问题
git bisect good <正常版本>
# Git 会自动二分切换版本，每次你验证后标记
git bisect good                # 或 git bisect bad
# 最终定位到引入问题的提交
git bisect reset               # 结束二分查找
```

### 场景 4：临时想切分支但当前修改不想 commit

```bash
git stash -u                  # 暂存含未跟踪的文件
# 干别的事...
git stash pop                 # 回来继续
```

### 场景 5：回退已经 push 的提交

```bash
# 方式一：revert（推荐，安全）
git revert HEAD
git push

# 方式二：reset + force push（警告：影响协作者）
git reset --hard HEAD~1
git push --force-with-lease
```

### 场景 6：把某分支的单个 commit 复制到当前分支

```bash
git cherry-pick <commit-id>
# 冲突时解决后
git cherry-pick --continue
```

### 场景 7：误删分支恢复

```bash
# 找到被删分支的最后 commit id
git reflog
# 恢复
git checkout -b 分支名 <commit-id>
```

### 场景 8：本地误删文件，从 Git 恢复

```bash
git restore file.txt
# 或从指定提交恢复
git checkout <commit-id> -- file.txt
```

---

## 提交信息规范

好的提交信息让历史可读：

```
<类型>: <简短描述>

<详细描述（可选）>

<关联 issue（可选）>
```

**类型前缀：**

| 前缀 | 含义 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 文档变更 |
| `style` | 格式调整（不影响代码逻辑） |
| `refactor` | 重构 |
| `test` | 添加或修改测试 |
| `chore` | 构建或辅助工具变更 |

示例：

```bash
git commit -m "feat: 添加密码重置功能"
git commit -m "fix: 修复登录超时后未正确跳转的问题"
```

---

## SSH 密钥配置

```bash
# 生成密钥
ssh-keygen -t ed25519 -C "your@email.com"
# 或传统 RSA
ssh-keygen -t rsa -b 4096 -C "your@email.com"

# 查看公钥，添加到 GitHub/GitLab 的 SSH Keys 设置中
cat ~/.ssh/id_ed25519.pub

# 测试连接
ssh -T git@github.com
```

---

## 快速参考

| 需求 | 命令 |
|------|------|
| 初始化仓库 | `git init` |
| 克隆仓库 | `git clone <url>` |
| 查看状态 | `git status` |
| 暂存文件 | `git add <file>` |
| 提交 | `git commit -m "信息"` |
| 查看日志 | `git log --oneline --graph` |
| 创建分支 | `git switch -c <分支名>` |
| 切换分支 | `git switch <分支名>` |
| 合并分支 | `git merge <分支名>` |
| 推送到远程 | `git push` / `git push -u origin <分支>` |
| 拉取更新 | `git pull --rebase` |
| 暂存工作 | `git stash` / `git stash pop` |
| 撤销提交（本地） | `git reset --soft HEAD~1` |
| 撤销提交（远程） | `git revert <commit>` |
| 打标签 | `git tag -a v1.0 -m "版本"` |
| 查看文件差异 | `git diff` |

---

## 参考

- [Git 官方文档](https://git-scm.com/doc)
- [Pro Git 中文版](https://git-scm.com/book/zh/v2)
- [GitHub Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
