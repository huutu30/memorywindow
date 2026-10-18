import sys
import uiautomator2 as u2

sys.stdout.reconfigure(encoding='utf-8')
d = u2.connect()
el = d(descriptionContains="Lịch sử tư vấn")
if el.exists:
    print("Bounds of 'Lịch sử tư vấn':", el.info.get('bounds'))
