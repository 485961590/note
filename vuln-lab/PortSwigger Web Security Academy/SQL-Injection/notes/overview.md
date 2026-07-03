# SQLi-Labs 关卡总览

SQLi-Labs 是经典的 SQL 注入靶场，共 65 个关卡（Less-1 到 Less-65），按注入类型和难度递增组织。

## 关卡分类

| 序号 | 分类 | 关卡 | 核心学习点 |
|------|------|------|-----------|
| 1 | GET 基础注入 | Less 1-10 | 四种闭合方式 x 三种注入技术（联合/报错/盲注） |
| 2 | POST/Header 注入 | Less 11-22 | POST 参数、User-Agent、Referer、Cookie 注入点 |
| 3 | WAF/过滤绕过 | Less 23-31 | 注释过滤、关键字过滤、空格过滤、HPP |
| 4 | 宽字节注入 | Less 32-37 | GBK 编码 + addslashes/mysql_real_escape_string 绕过 |
| 5 | 堆叠查询 | Less 38-45 | Stacked Queries（; 分隔多语句） |
| 6 | ORDER BY 注入 | Less 46-53 | ORDER BY 子句后的注入点利用 |
| 7 | 挑战关卡 | Less 54-65 | 随机表名 + 请求次数限制下的快速注入 |

## 四种闭合方式

所有注入的基础，贯穿全部 65 关：

```
类型 A: 数字型          id=1          （无需引号闭合）
类型 B: 单引号字符型     id='1'        （需闭合 '）
类型 C: 双引号字符型     id="1"        （需闭合 "）
类型 D: 括号变体         id=('1')      （需闭合括号 + 引号）
```

## 三种注入技术

| 技术 | sqlmap 参数 | 前提条件 | 速度 | 隐蔽性 |
|------|-----------|---------|------|--------|
| 联合查询 (UNION) | `--technique=U` | 有回显位 | 快 | 低 |
| 报错注入 (Error) | `--technique=E` | 有错误回显 | 快 | 低 |
| 布尔盲注 (Boolean) | `--technique=B` | 页面有 True/False 差异 | 慢 | 中 |
| 时间盲注 (Time) | `--technique=T` | 无任何回显差异 | 极慢 | 高 |

## 闭合方式对应表（快速查阅）

| Less | 方法 | 闭合方式 | 注入技术 |
|------|------|---------|---------|
| 1 | GET | `'id'` | UNION |
| 2 | GET | `id` | UNION |
| 3 | GET | `('id')` | UNION |
| 4 | GET | `("id")` | UNION |
| 5 | GET | `'id'` | Error (Double) |
| 6 | GET | `"id"` | Error (Double) |
| 7 | GET | `(('id'))` | UNION + prefix |
| 8 | GET | `'id'` | Boolean |
| 9 | GET | `'id'` | Time |
| 10 | GET | `"id"` | Time |
| 11 | POST | `'uname'` | UNION |
| 12 | POST | `("uname")` | UNION |
| 13 | POST | `('uname')` | Error (Double) |
| 14 | POST | `"uname"` | Error (Double) |
| 15 | POST | `'uname'` | Boolean |
| 16 | POST | `("uname")` | Boolean |
| 17 | POST | UPDATE 语句 | Error |
| 18 | POST | User-Agent 头 | UNION |
| 19 | POST | Referer 头 | UNION |
| 20 | POST | Cookie | UNION |
| 21 | POST | Cookie (Base64) | UNION |
| 22 | POST | Cookie (Base64+双引号) | UNION |
| 23-31 | 混合 | 见 WAF 绕过分类 | 混合 |
| 32-37 | 混合 | 见宽字节分类 | 混合 |
| 38-45 | 混合 | 见堆叠查询分类 | 混合 |
| 46-53 | GET | `sort` 参数 | 混合 |
| 54-65 | 混合 | 随机表名 | 混合 |

## 脚本使用说明

```bash
# 1. 修改脚本中的 TARGET 变量指向你的靶机
# 2. 单个分类的命令从 scripts/*.md 文件中复制执行
# 3. 或使用 run_all.md 中的一键脚本（复制保存为 run_all.sh 后执行）
# 4. 结果查看
ls results/Less-1/
```

## 相关文档

- [sqlmap 完整参考手册](../../Tools/sqlmap.md) — 本靶场使用的所有 sqlmap 参数速查
- [注入类型详解](injection-types.md) — 每种注入的原理分析
- [靶场搭建指南](setup-guide.md) — Docker/手动搭建 SQLi-Labs
