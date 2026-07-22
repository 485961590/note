# Findings — 8.140.206.93 (CISP-PTE SQL Injection)

## Summary

**Flag:** `123`
**Method:** Boolean-based blind SQL injection via load_file('/home/key')
**Time to solve:** ~1 hour (mostly debugging filter bypasses)

## Target Profile

- Apache 2.4.7 + PHP 5.5.9 + MySQL (LAMP stack)
- CISP-PTE certification exam challenge
- Goal: Read /home/key via SQL injection

## Vulnerabilities Found

### 1. SQL Injection (CRITICAL — Exploited)
- **Location:** GET parameter `id` on `/vulnerabilities/fu1.php`
- **Query template:** `select * from article where id= ('INPUT')`
- **Filters:** `union` keyword removal (case-insensitive), space removal
- **Bypasses:** `uniunionon` (nested keyword), `%09` (tab), `#` (comment)
- **Exploited via:** Boolean-based blind injection with `load_file('/home/key')`
- **Result:** Flag `123` extracted

### 2. Exposed .git Repository (HIGH)
- **Location:** http://8.140.206.93:81/.git/
- **Impact:** Source code disclosure (index.php, phpinfo.php)
- **Key finding:** `mysql_connect('localhost', 'root')` with NO password
- **Not exploited:** Upstream repo only contained base files; challenge files not committed

### 3. Information Disclosure (MEDIUM)
- **phpinfo.php:** Accessible (HTTP 200), reveals full PHP configuration
- **SQL query display:** The executed SQL is shown on the page, aiding injection debugging

### 4. MySQL root with no password (HIGH)
- **Found in:** index.php source from .git
- **Impact:** Full database access, LOAD_FILE capability
- **Exploited indirectly:** Used LOAD_FILE() to read /home/key

## Exploitation Path

1. Recon: nmap + whatweb + curl -> identified LAMP stack, SQLi challenge
2. Source review: .git repo -> mysql_connect root no password
3. Manual injection: Discovered filter bypasses (uniunionon + tab + #)
4. Boolean oracle: Confirmed load_file('/home/key') works
5. Blind extraction: Extracted file length (4) and characters ('1','2','3','\n')
6. Flag: `123`

## Dead Ends

- **UNION SELECT:** Attempted multiple column counts (2-12) with all bypasses active. SQL syntax confirmed correct but card never displayed injected values. Likely column count mismatch with article table.
- **-- comment:** Broken by space filter. Required switching to `#`.

## Remaining Attack Surface (Unexploited)

- phpinfo.php — full PHP configuration available
- MySQL root access — full database dump possible
- Directory enumeration not performed (no wordlist selected)
