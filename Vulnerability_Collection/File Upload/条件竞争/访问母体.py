import requests

url = "http://192.168.245.151:8006/upload/mom.php.7z"
while True:
    html = requests.get(url)
    if html.status_code == 200:
        print("OK")
        break
    else:
        print("NO")
