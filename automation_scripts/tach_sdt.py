import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(BASE_DIR, "mahopdong.txt")
OUTPUT = os.path.join(BASE_DIR, "sodaloc.txt")

with open(INPUT, 'r', encoding='utf-8') as f:
    lines = f.readlines()

phones = []
for line in lines:
    m = re.search(r'->\s*(0\d{9})', line.strip())
    if m:
        phones.append(m.group(1))

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(phones) + '\n')

print(f"✅ Đã tách {len(phones)} số điện thoại vào file sodaloc.txt")
