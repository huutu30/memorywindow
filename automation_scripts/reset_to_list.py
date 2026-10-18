import sys
import time
import uiautomator2 as u2

sys.stdout.reconfigure(encoding='utf-8')
d = u2.connect()
print("Back to list...")
for _ in range(3):
    if d(descriptionContains="Chưa tư vấn").exists:
        print("At list now!")
        break
    d.press("back")
    time.sleep(1)
print("Done.")
