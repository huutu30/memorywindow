import sys
from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')

tree = etree.parse('hierarchy.xml')
for node in tree.xpath('//*[@text or @content-desc]'):
    txt = node.get('text', '')
    desc = node.get('content-desc', '')
    cls = node.get('class', '')
    bounds = node.get('bounds', '')
    if txt or desc:
        print(f"[{cls}] text='{txt}' desc='{desc}' bounds={bounds}")
