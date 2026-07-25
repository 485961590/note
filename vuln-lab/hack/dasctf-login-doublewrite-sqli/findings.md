# Findings — dasctf-http-challenge

## Target
http://23f036b60c9b61df4c2bf85c.http-ctf2.dasctf.com:80

## Flag Captured
- **CTF2{ec2b64-9988-4362-8b08-69c4b6f33a68}** — from b4bsql table, row id=8 (username: flag)

## Exploitation Path
1. **Recon** — Login page at check.php (GET: username, password), PHP 7.3.11, OpenResty, MariaDB
2. **SQLi Discovery** — Single quote injection revealed MariaDB errors; `admin'#` bypassed authentication
3. **Filter Bypass** — Keyword filter (OR, AND, BY, UNION, SELECT) bypassed with double-write technique
4. **Database Enumeration** — UNION SELECT extracted database name (geek), tables (b4bsql, geekuser), and columns
5. **Data Extraction** — Dumped b4bsql table revealing the flag

## Unexploited Vulnerabilities
- MySQL root@localhost access (potential for file read/write if FILE privilege is available)
- Admin MD5 hash (70951dbf907a9a021de25996fc5a02c9) — not cracked in this session
