升级 Shell 为完全交互式 TTY 终端可以整理为固定的**三步标准化流程**：
### **完全交互式 TTY 升级法**
**第一步：派生伪终端（靶机上执行）**
根据靶机环境选择任一脚本语言运行：
- **Python 2/3**：        
```bash
python -c 'import pty; pty.spawn("/bin/bash")'
```

- **Script（无 Python 时备选）**：

```bash
script -qc /bin/bash /dev/null
```
- **第二步：挂起并配置本地 Terminal（本地 Kali 上执行）**
1. 按下 **`Ctrl + Z`** 将当前 Shell 挂起到后台。
2. 在本地 Kali 终端中直接输入并回车：
```bash
stty raw -echo; fg
```
3. 再次按 **`Enter`** 键恢复界面（若页面无显示或错乱可输入 `reset` 并按回车）。
- **第三步：补全环境变量与分辨率（靶机上执行）**
```bash
export TERM=xterm
export SHELL=bash
```
_(可选)_ 设置终端行列大小以适配本地窗口（先在本地执行 `stty size` 查看行宽）：
```bash
stty rows 60 cols 230
```