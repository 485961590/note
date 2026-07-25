# Findings — DASCTF SQL Blind Injection

## Summary

**Flag:** `Ohhh.you.fInd.the.flag.read.on..br..ohhh...` (501 chars, repeating pattern)
**Table:** `Flaaaaag.fl4gawsl`
**Method:** Boolean-based blind SQLi with WAF bypass
**Key techniques:** `SELECT(`, `FROM(subquery)x`, `WHERE(`, `)regexp(` — parentheses replace spaces

## Target Profile

- OpenResty + PHP 7.3.11 + MariaDB 10.3.18
- Database: `geek`, user: `root@localhost`
- Tables: `F1naI1y` (search messages), `Flaaaaag` (flag data)

## Vulnerabilities Found

### 1. SQL Injection (boolean-based blind) — EXPLOITED
- **Location:** `search.php?id=`
- **Context:** Numeric (no quotes needed)
- **Oracle:** `id=2-(condition)` — TRUE="NO! Not this!", FALSE="yingyingying~"
- **WAF Bypass:** `keyword(` instead of `keyword ` for SELECT, FROM, WHERE, substr

### 2. Information Disclosure
- phpinfo accessible, database credentials exposed in source

### 3. WAF Blacklist Bypass
- Multiple techniques found: parentheses substitution, Unicode whitespace, REGEXP subquery pattern

## Exploitation Path

1. Boolean oracle: `id=2-(1=1)` -> TRUE, `id=2-(1=0)` -> FALSE
2. Extract `database()=geek`, `version()=10.3.18-MariaDB`, `user()=root@localhost`
3. Enumerate tables via information_schema: `F1naI1y,Flaaaaag`
4. Enumerate columns: `Flaaaaag` has `id,fl4gawsl`
5. REGEXP prefix extraction: `(subquery)regexp('^prefix')` to read flag character by character
6. Flag: 501-char repeating message from row 3

## Key WAF Bypasses

| Technique | Works? | Notes |
|-----------|--------|-------|
| `SELECT(` | YES | Parenthesis after keyword |
| `FROM(SELECT(...))x` | YES | Nested subquery with alias |
| `substr(` | YES | Function call bypass |
| `WHERE(` | YES | Same as SELECT |
| `)regexp(` | YES | REGEXP after closing paren |
| `AND(` | NO | WAF catches AND even with paren |
| Unicode spaces | YES | U+2008/2009/200A/200B/3000 bypass WAF but MariaDB rejects them |
