def judge(c):
    """判断字符是否不是字母或数字"""
    return not c.isalnum()


def find_xor_parts(shell):
    """为输入字符串找到两个非字母数字的异或部分"""
    result1 = ""
    result2 = ""

    for char in shell:
        found = False
        for x in range(33, 127):
            char_x = chr(x)
            if judge(char_x):  # x不包含数字字母
                for y in range(33, 127):
                    char_y = chr(y)
                    if judge(char_y):  # y不包含数字字母
                        if chr(ord(char_x) ^ ord(char_y)) == char:
                            result1 += char_x
                            result2 += char_y
                            found = True
                            break
                if found:
                    break
        if not found:
            result1 += "?"
            result2 += "?"

    return result1, result2


# 使用示例
if __name__ == "__main__":
    shell = "_POST"
    part1, part2 = find_xor_parts(shell)
    print(f"输入: {shell}")
    print(f"第一部分: {part1}")
    print(f"第二部分: {part2}")

    # 示例2：验证功能
    print("\n验证:")
    for a, b, expected in zip(part1, part2, shell):
        result = chr(ord(a) ^ ord(b))
        print(f"  {a} ^ {b} = {result} ({'正确' if result == expected else '错误'})")
