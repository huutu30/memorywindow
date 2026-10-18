import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    page = browser.contexts[0].pages[0]
    print('Current URL:', page.url)

    # 1. Reset: Go to list page and click Copy
    list_url = "https://portal-sop.fpt.vn/settings/chien-dich/gui-tin-nhan/mega-push-campaign"
    print("Navigating to list URL...")
    page.goto(list_url)
    time.sleep(2)
    
    # Click copy button
    print("Clicking Copy button...")
    page.evaluate("""() => {
        const rows = document.querySelectorAll('tbody tr');
        for (let r of rows) {
            const btn = r.querySelector('td:last-child button');
            if (btn) { btn.click(); break; }
        }
    }""")
    time.sleep(2.5)
    print("Now on Step 1 URL:", page.url)

    # Click Tiếp tục on Step 1
    print("Clicking Step 1 Tiếp tục...")
    page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const nextBtn = btns.find(b => b.innerText.trim() === 'Tiếp tục');
        if (nextBtn) nextBtn.click();
    }""")
    time.sleep(2.5)
    print("Now on Step 2...")

    # Click Tiếp tục on Step 2
    print("Clicking Step 2 Tiếp tục...")
    page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const nextBtn = btns.find(b => b.innerText.trim() === 'Tiếp tục');
        if (nextBtn) nextBtn.click();
    }""")
    time.sleep(2.5)
    print("Now on Step 3...")

    # Test Ctrl+A and Ctrl+V via clipboard
    test_phones = ["0348641317", "0705566812", "0899709561"]
    phones_str = "\n".join(test_phones)
    
    # Read 60 numbers from sodaloc.txt
    with open("sodaloc.txt", "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()][:60]
    phones_str = "\n".join(lines) + "\n"
    
    # 1. Click editor
    editor = page.locator('div[data-lexical-editor="true"], .input-f_yAjs').first
    editor.click()
    time.sleep(0.5)
    
    # 2. Delete existing tag(s)
    page.keyboard.press("End")
    time.sleep(0.2)
    for _ in range(5):
        page.keyboard.press("Backspace")
        time.sleep(0.05)
    
    time.sleep(0.3)
    
    # 3. Insert all 60 phone numbers at once
    print(f"Inserting {len(lines)} phone numbers...")
    page.keyboard.insert_text(phones_str)
    time.sleep(1.5)
    
    # 4. Count tags created
    tag_count = editor.evaluate("el => el.querySelectorAll('span.tag-MwVpt7, span[class*=\"tag\"]').length")
    print(f"\n🎉 Successfully created {tag_count} phone tags in Lexical editor!")
    
    # 5. Click Tiếp tục to Step 4
    page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const nextBtn = btns.find(b => b.innerText.trim() === 'Tiếp tục');
        if (nextBtn) nextBtn.click();
    }""")
    time.sleep(2)
    print("Reached Step 4 successfully! URL:", page.url)











