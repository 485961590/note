# RLO 反转后缀 + 自解压程序钓鱼

## 概述

利用 Unicode RLO (RIGHT-TO-LEFT OVERRIDE, U+202E) 控制字符反转文件名显示方向，配合 WinRAR 自解压程序和图标替换，将 `.exe` 木马伪装为文档/图片等无害文件类型。

## 完整流程

```
CS 生成木马(.exe) → WinRAR 打包自解压(.exe) → 更换图标(.ico) → RLO 反转后缀伪装 → 投递
```

---

## 一、图标生成

使用 PIL 将任意 PNG 图片转换为 .ico 格式（支持多尺寸）：

```python
from PIL import Image

img = Image.open('hacker.png')

# 创建包含多个尺寸的 .ico 文件
sizes = [(16, 16), (32, 32), (48, 48)]
img.save('hacker.ico', format='ICO', sizes=sizes)
```

标准 Windows 图标尺寸为 16x16、32x32、48x48，建议全部包含以保证在不同视图下的显示效果。

---

## 二、WinRAR 自解压程序配置

### 关键设置

| 选项 | 设置 | 说明 |
|------|------|------|
| Setup program | 木马文件 + 诱饵文件 | 解压后自动执行，同时打开诱饵避免起疑 |
| General → Save as | 默认 SFX 名称 | 后续用 RLO 伪装 |
| Modes → Silent mode | Hide all | 静默解压，不显示窗口 |
| Modes → Overwrite mode | Overwrite all files | 覆盖已有文件 |
| Update | Extract and replace files | 解压并替换 |

### 常用解压路径

- `%TEMP%` — 临时目录，不易察觉
- `%APPDATA%` — 应用数据目录

### 更换图标

在 WinRAR 自解压选项 → "Text and icon" → "Load SFX icon from the file" 中选择生成好的 `.ico` 文件。

---

## 三、RLO 文件名伪装

### RLO 原理

U+202E (RIGHT-TO-LEFT OVERRIDE) 强制将其后的字符按从右到左顺序显示。利用这一特性，可以将 `.exe` 扩展名在视觉上隐藏到文件名中间，而显示为其他扩展名。

### PowerShell 操作

```powershell
$rlo = [char]0x202E

# 示例：将 payload.exe 重命名，使视觉显示为 payloadexe.pdf
Rename-Item "payload.exe" "payload${rlo}fdp.exe"
```

### 命名建议

| 实际文件名 | 视觉显示 | 伪装类型 |
|-----------|---------|---------|
| `resume` + RLO + `cod.exe` | `resumeexe.doc` | Word 文档 |
| `invoice` + RLO + `fdp.exe` | `invoiceexe.pdf` | PDF 文件 |
| `salary` + RLO + `slx.exe` | `salaryexe.xls` | Excel 表格 |
| `photo` + RLO + `gpj.exe` | `photoexe.jpg` | 图片 |

建议使用 PDF/DOC/XLS 等文档类后缀，因为收到"文件"比收到"图片"更合理，降低目标怀疑。

---

## 四、其他可用 Unicode 控制字符

| 字符 | Unicode | 作用 |
|------|---------|------|
| RLO | U+202E | 强制从右到左显示（最常用） |
| LRO | U+202D | 强制从左到右显示 |
| PDF | U+202C | 结束 RLO/LRO 的影响范围 |
| RLI | U+2067 | 从右到左隔离 |
| LRI | U+2066 | 从左到右隔离 |

---

## 五、注意事项

1. **免杀**：CS 默认 payload 和自解压程序都可能被 Defender 查杀，投递前在目标系统环境下测试
2. **右键菜单**：文件名右键 "插入 Unicode 控制字符" 来自 Windows 复杂脚本语言支持，未安装时可用 PowerShell 替代
3. **诱饵文件**：自解压时同时释放并打开一个正常文档/图片，降低目标警觉
4. **红队合规**：仅在授权渗透测试范围内使用
