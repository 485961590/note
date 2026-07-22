import os
import re

txt_dir = r"E:\note\考研\PPT\txt"
output_file = r"E:\note\考研\PPT\生物医学工程基础教案-完整整理.md"

files = [
    "1-ch1-绪论-生物医学工程基础教案    2018-9.txt",
    "2-ch2-生物力学-生物医学工程基础教案-58a33c99f705cc17552709dd.txt",
    "3-ch3-生物材料-生物医学工程基础教案.txt",
    "4-ch4-人工器官-生物医学工程基础教案   2018-9.txt",
    "5-ch5-生物传感器-生物医学工程基础教案2018-11.txt",
    "6-ch7-图像处理 空间域增强.txt",
    "7-ch7-医学成像.txt"
]

chapter_titles = [
    "第一章 绪论",
    "第二章 生物力学",
    "第三章 生物材料",
    "第四章 人工器官",
    "第五章 生物医学传感器基础",
    "第七章 医学图像处理（空间域增强）",
    "第七章 医学成像"
]

lines_out = []
lines_out.append("# 西南交通大学《生物医学工程基础》教案 — 完整整理\n")
lines_out.append("> 主讲教师：陈俊英（ch1-ch5）、常向荣（ch7 医学成像）\n")
lines_out.append("> 教材：《生物医学工程基础》讲义，陈俊英编，西南交通大学，2006年\n")
lines_out.append("> 教案年份：2018-2019\n")
lines_out.append("> 本文档由 PPT 教案提取文本整理而成，保留原始内容结构\n")
lines_out.append("\n---\n\n")

# TOC
lines_out.append("## 目录\n\n")
for title in chapter_titles:
    lines_out.append(f"- [{title}](#{title.replace(' ', '-').replace('（', '(').replace('）', ')')})\n")
lines_out.append("\n---\n\n")

for i, (fname, ctitle) in enumerate(zip(files, chapter_titles)):
    fpath = os.path.join(txt_dir, fname)
    if not os.path.exists(fpath):
        lines_out.append(f"\n# {ctitle}\n\n> [文件未找到]\n\n---\n\n")
        continue

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines_out.append(f"\n# {ctitle}\n\n")

    for raw_line in content.split('\n'):
        line = raw_line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip slide markers like "--- Slide 1 ---"
        if '--- Slide' in line:
            continue

        # Skip pure numbers (slide number artifacts)
        if re.match(r'^\d{1,3}$', line):
            continue

        # Skip date stamps
        if line == '2026-07-19':
            continue

        # Clean up control characters
        cleaned = line
        # Replace vertical tab with pipe
        cleaned = cleaned.replace('\x0b', ' | ')
        # Replace form feed
        cleaned = cleaned.replace('\x0c', '')
        # Remove other control chars except newlines
        cleaned = re.sub(r'[\x00-\x08\x0e-\x1f\x7f-\x9f]', '', cleaned)

        # Check if it's a section header
        if re.match(r'^§\s*\d', cleaned) or re.match(r'^第[一二三四五六七八九十]章', cleaned):
            lines_out.append(f"\n### {cleaned}\n\n")
        elif re.match(r'^[一二三四五六七八九十]、', cleaned):
            lines_out.append(f"\n#### {cleaned}\n\n")
        elif re.match(r'^\d+[、.]', cleaned):
            lines_out.append(f"\n**{cleaned}**\n\n")
        elif cleaned.startswith('作业') or cleaned.startswith('作业：'):
            lines_out.append(f"\n> **{cleaned}**\n\n")
        else:
            lines_out.append(f"{cleaned}\n")

    lines_out.append("\n---\n\n")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(''.join(lines_out))

print(f"Done: {len(lines_out)} lines written to:")
print(output_file)
print(f"File size: {os.path.getsize(output_file)} bytes")
