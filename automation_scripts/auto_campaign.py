import os
import sys
import time
import datetime
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

CDP_URL = "http://127.0.0.1:9222"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PAGES_CONFIG = {
    "1": {"name": "A Sóc F P T", "prefix": "asoc"},
    "2": {"name": "Tú Lắp Wifi F P T", "prefix": "tulap"},
    "3": {"name": "Chuyên Lắp Đặt Mạng F P T", "prefix": "mangfpt"},
    "4": {"name": "Anh Tứ F P T", "prefix": "anhtu"},
    "5": {"name": "An Thy F P T", "prefix": "anthy"},
    "6": {"name": "Bảo Anh F P T", "prefix": "baoanh"},
    "7": {"name": "Lắp Mạng Wifi F P T", "prefix": "lapmang"},
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_tomorrow_date():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    return tomorrow

def load_phones(file_path):
    if not os.path.isabs(file_path):
        file_path = os.path.join(BASE_DIR, file_path)
    
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file: {file_path}")
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def remove_used_phones_from_file(file_path, used_phones):
    """Tự động cắt bỏ các số đã chạy thành công khỏi file nguồn"""
    if not os.path.isabs(file_path):
        file_path = os.path.join(BASE_DIR, file_path)
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, "r", encoding="utf-8") as f:
        current_phones = [line.strip() for line in f if line.strip()]
    
    used_set = set(used_phones)
    remaining = [p for p in current_phones if p not in used_set]
    
    with open(file_path, "w", encoding="utf-8") as f:
        for p in remaining:
            f.write(p + "\n")
    return len(remaining)

def log_used_phones(camp_name, target_page, date_disp, phones):
    """Ghi nhật ký lịch sử các số đã dùng theo từng chiến dịch để tra cứu/đối soát"""
    log_file = os.path.join(BASE_DIR, "sdt_da_dung.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n# ============================================================\n")
        f.write(f"# CHIẾN DỊCH: {camp_name} | TRANG: {target_page} | NGÀY GỬI: {date_disp}\n")
        f.write(f"# THỜI GIAN TẠO: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | TỔNG SỐ: {len(phones)} SĐT\n")
        f.write(f"# ============================================================\n")
        for p in phones:
            f.write(p + "\n")

def interactive_menu():
    print("=" * 60)
    print("      🚀 CÔNG CỤ TỰ ĐỘNG TẠO CHIẾN DỊCH MEGA PUSH")
    print("=" * 60)
    
    # 1. Chọn Trang
    print("\n[?] Chọn Trang bạn muốn chạy chiến dịch:")
    for key, cfg in PAGES_CONFIG.items():
        print(f"  [{key}] {cfg['name']} (Tiền tố gợi ý: {cfg['prefix']})")
    custom_choice = str(len(PAGES_CONFIG) + 1)
    print(f"  [{custom_choice}] Tùy chỉnh tên trang khác...")
    
    choice = input(f"\n👉 Nhập lựa chọn [1-{custom_choice}] (Mặc định: 1): ").strip() or "1"
    if choice in PAGES_CONFIG:
        target_page_name = PAGES_CONFIG[choice]["name"]
        default_prefix = PAGES_CONFIG[choice]["prefix"]
    else:
        target_page_name = input("👉 Nhập tên hiển thị của Trang: ").strip()
        default_prefix = input("👉 Nhập tiền tố viết tắt: ").strip() or "camp"

    # 2. Tiền tố tên chiến dịch
    custom_prefix = input(f"\n[?] Tiền tố tên chiến dịch (Enter để lấy '{default_prefix}'): ").strip()
    prefix = custom_prefix if custom_prefix else default_prefix

    # 3. Ngày bắt đầu
    tomorrow = get_tomorrow_date()
    tomorrow_str = tomorrow.strftime("%d/%m")
    start_date_str = input(f"\n[?] Ngày bắt đầu gửi [DD/MM] (Enter để lấy ngày mai {tomorrow_str}): ").strip()
    if not start_date_str:
        start_date_str = tomorrow_str

    try:
        parts = [int(p) for p in start_date_str.replace("-", "/").split("/")]
        day, month = parts[0], parts[1]
        year = tomorrow.year if len(parts) < 3 else parts[2]
        start_date = datetime.date(year, month, day)
    except Exception:
        print("⚠️ Ngày nhập không hợp lệ, tự động dùng ngày mai.")
        start_date = tomorrow

    # 4. Số lượng ngày / chiến dịch
    num_days_str = input("\n[?] Số ngày muốn tạo liên tiếp (Enter để lấy 5 ngày): ").strip()
    num_days = int(num_days_str) if num_days_str.isdigit() else 5

    # 5. File số điện thoại
    default_phone_file = "sodaloc.txt"
    if not os.path.exists(os.path.join(BASE_DIR, default_phone_file)):
        txt_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".txt")]
        if txt_files:
            default_phone_file = txt_files[0]
            
    phone_file = input(f"\n[?] File chứa danh sách SĐT (Enter để lấy '{default_phone_file}'): ").strip()
    if not phone_file:
        phone_file = default_phone_file

    # 6. Số lượng SĐT mỗi chiến dịch
    limit_str = input("\n[?] Số lượng SĐT cho mỗi chiến dịch (Enter để lấy 150): ").strip()
    limit = int(limit_str) if limit_str.isdigit() else 150

    # Đọc danh sách số điện thoại
    all_phones = load_phones(phone_file)
    total_needed = num_days * limit
    print(f"\n📊 Tổng số SĐT hiện có trong '{phone_file}': {len(all_phones)} số.")
    if len(all_phones) < total_needed:
        print(f"⚠️ Cảnh báo: Cần {total_needed} số ({num_days} x {limit}), nhưng file chỉ còn {len(all_phones)} số.")
    
    # Tạo danh sách chiến dịch dự kiến
    campaigns = []
    current_date = start_date
    phone_idx = 0
    for i in range(num_days):
        d_str = f"{current_date.day}-{current_date.month}"
        c_name = f"{prefix} {d_str}"
        batch_phones = all_phones[phone_idx : phone_idx + limit]
        phone_idx += limit
        campaigns.append({
            "name": c_name,
            "target_page": target_page_name,
            "date": current_date,
            "date_display": current_date.strftime("%d/%m/%Y"),
            "date_iso": current_date.strftime("%Y-%m-%d"),
            "phones": batch_phones,
            "limit": limit,
            "phone_file": phone_file
        })
        current_date += datetime.timedelta(days=1)

    print("\n" + "=" * 60)
    print("📋 XÁC NHẬN DANH SÁCH CHIẾN DỊCH SẼ TẠO:")
    print("=" * 60)
    print(f"  • Trang đích: {target_page_name}")
    print(f"  • Hạn mức: {limit} số/ngày")
    print(f"  • Khung giờ gửi: 07:00 - 20:00 (Gửi một lần)")
    print(f"  • File SĐT nguồn: {phone_file} (sẽ tự động trừ bớt khi tạo xong)")
    print(f"  • File lưu lịch sử: sdt_da_dung.txt")
    print(f"  • Tổng số chiến dịch: {len(campaigns)}")
    print("-" * 60)
    for idx, c in enumerate(campaigns, start=1):
        print(f"  {idx:2d}. Tên: {c['name']:<18} | Ngày gửi: {c['date_display']} | SĐT: {len(c['phones'])} số")
    print("=" * 60)

    confirm = input("\n👉 Bấm [Enter] để BẮT ĐẦU CHẠY (hoặc gõ 'q' để hủy): ").strip().lower()
    if confirm == 'q':
        print("🛑 Đã hủy thao tác.")
        sys.exit(0)

    return campaigns

def create_single_campaign(page, camp_info):
    c_name = camp_info["name"]
    target_page = camp_info["target_page"]
    phones = camp_info["phones"]
    limit_val = str(camp_info.get("limit", 60))
    target_date_iso = camp_info["date_iso"]
    target_date_disp = camp_info["date_display"]

    print(f"\n🚀 ĐANG TẠO CHIẾN DỊCH: '{c_name}' (Ngày gửi: {target_date_disp})...")

    # 1. Đảm bảo đang ở trang danh sách chiến dịch
    list_url = "https://portal-sop.fpt.vn/settings/chien-dich/gui-tin-nhan/mega-push-campaign"
    if list_url not in page.url or "sao-chep" in page.url or "tao-moi" in page.url:
        print("  🔄 Đang quay lại trang danh sách chiến dịch...")
        page.goto(list_url, timeout=15000)
        time.sleep(2)

    page.wait_for_load_state("domcontentloaded")
    time.sleep(1.5)

    # 2. Bấm nút Copy ở dòng chiến dịch mới nhất (chấp nhận mọi tình trạng kể cả 'Đang gửi')
    print("  📋 Bấm nút Sao chép chiến dịch mới nhất...")
    copied = page.evaluate("""() => {
        const rows = Array.from(document.querySelectorAll('tbody tr.ant-table-row, tbody tr'));
        for (let r of rows) {
            const lastTd = r.querySelector('td:last-child');
            if (!lastTd) continue;
            const btns = Array.from(lastTd.querySelectorAll('button'));
            if (btns.length > 0) {
                // Nút đầu tiên trong cột hành động là nút Sao chép
                btns[0].click();
                return true;
            }
        }
        return false;
    }""")
    
    if not copied:
        raise Exception("Không tìm thấy nút sao chép ở danh sách chiến dịch")

    # Chờ form sao chép xuất hiện
    time.sleep(2.5)

    # 3. BƯỚC 1: KHỞI TẠO
    print("  ⚙️ [Bước 1/4] Thiết lập Khởi tạo (Bật kích hoạt, Đổi tên, Chọn trang)...")
    
    # Bật kích hoạt bằng JavaScript
    page.evaluate("""() => {
        const switches = Array.from(document.querySelectorAll('.ant-switch, #activate'));
        const sw = switches.find(s => s.offsetParent !== null) || switches[0];
        if (sw && sw.getAttribute('aria-checked') === 'false') {
            sw.click();
        }
    }""")
    time.sleep(0.3)

    # Nhập tên chiến dịch (chọn ô visible)
    name_inp = page.locator('#name:visible, input[placeholder*="chiến dịch"]:visible').first
    if name_inp.count() > 0:
        name_inp.click()
        name_inp.fill(c_name)
        time.sleep(0.3)

    # Mở dropdown Chọn Trang đích (chọn ô visible)
    page.locator(".select-HmbrOo .ant-select-selector:visible, .ant-select-selector:visible").first.click()
    time.sleep(0.8)

    # Chọn đúng trang và bỏ chọn các trang khác
    page.evaluate("""(targetName) => {
        const drop = document.querySelector('.ant-select-dropdown:not(.ant-select-dropdown-hidden)');
        if (!drop) return;
        
        const rows = drop.querySelectorAll('.fanpage_option-S1Jyb_');
        rows.forEach(r => {
            if (r.querySelector('.select_all-ujhhjm') || r.querySelector('.fp_select_all-cjT2XM')) return; // Bỏ qua tiêu đề nhóm
            
            const text = r.innerText.trim();
            const chkBox = r.querySelector('.ant-checkbox-input') || r.querySelector('input[type="checkbox"]');
            const isChecked = r.querySelector('.ant-checkbox-checked') !== null;
            
            const matches = text.toLowerCase().includes(targetName.toLowerCase().trim());
            if (matches) {
                if (!isChecked && chkBox) chkBox.click();
            } else {
                if (isChecked && chkBox) chkBox.click();
            }
        });
    }""", target_page)
    time.sleep(0.5)

    # Đóng dropdown
    page.keyboard.press("Escape")
    time.sleep(0.5)

    # Bấm Tiếp tục sang Bước 2 (Nội dung)
    page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const nextBtn = btns.find(b => b.innerText.trim() === 'Tiếp tục');
        if (nextBtn) nextBtn.click();
    }""")
    time.sleep(2.0)

    # 4. BƯỚC 2: NỘI DUNG
    print("  💬 [Bước 2/4] Kiểm tra Nội dung và bấm Tiếp tục...")
    page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const nextBtn = btns.find(b => b.innerText.trim() === 'Tiếp tục');
        if (nextBtn) nextBtn.click();
    }""")
    time.sleep(2.0)

    # 5. BƯỚC 3: ĐỐI TƯỢNG NHẬN TIN NHẮN (DÁN SĐT)
    print(f"  📱 [Bước 3/4] Dán {len(phones)} số điện thoại...")
    
    # Tìm ô Lexical Editor
    editor = page.locator('div[data-lexical-editor="true"], .input-f_yAjs, div[contenteditable="true"]').first
    if editor.count() > 0:
        editor.click()
        time.sleep(0.3)
        # Xóa sạch toàn bộ các thẻ SĐT cũ
        page.keyboard.press("Control+A")
        time.sleep(0.1)
        page.keyboard.press("Backspace")
        time.sleep(0.2)
        
        # Nhập toàn bộ danh sách SĐT mới
        phones_str = "\n".join(phones) + "\n"
        page.keyboard.insert_text(phones_str)
        time.sleep(1.5)
        
        try:
            tag_count = editor.evaluate("el => el.querySelectorAll('span.tag-MwVpt7, span[class*=\"tag\"]').length")
            print(f"  ✅ Đã nạp thành công {tag_count} số điện thoại vào chiến dịch!")
        except Exception:
            print(f"  ✅ Đã nạp {len(phones)} số điện thoại!")
    else:
        print("  ⚠️ Dùng ô input/textarea dự phòng...")
        page.locator("textarea, input[type='text']").first.fill("\n".join(phones))
        time.sleep(1.0)

    # Bấm Tiếp tục sang Bước 4 (Lịch gửi)
    page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const nextBtn = btns.find(b => b.innerText.trim() === 'Tiếp tục');
        if (nextBtn) nextBtn.click();
    }""")
    time.sleep(2.0)

    # 6. BƯỚC 4: LỊCH GỬI TỰ ĐỘNG & HẠN MỨC
    print(f"  🎯 [Bước 4/4] Thiết lập hạn mức {limit_val} số/ngày & Giờ gửi 07:00 - 20:00 & Ngày {target_date_disp}...")

    # Chọn hạn mức SĐT/ngày (nếu có sẵn 30, 60, 90, 120, 150 thì tick chọn, nếu giá trị khác thì chọn 'Khác' và nhập vào ô)
    standard_limits = ["30", "60", "90", "120", "150"]
    if limit_val in standard_limits:
        page.evaluate("""(val) => {
            const r = document.querySelector(`input[type="radio"][value="${val}"]`);
            if (r) {
                r.click();
                r.closest('.ant-radio-wrapper')?.click();
            }
        }""", limit_val)
        time.sleep(0.3)
    else:
        # Chọn mục 'Khác'
        page.evaluate("""() => {
            const rOther = document.querySelector('input[type="radio"][value="other"]');
            if (rOther) {
                rOther.click();
                rOther.closest('.ant-radio-wrapper')?.click();
            }
        }""")
        time.sleep(0.5)
        # Nhập số lượng vào ô hạn mức tùy chỉnh (#daily_quota_custom)
        custom_inp = page.locator("#daily_quota_custom, input[id*='daily_quota'], .ant-input-number-input").first
        if custom_inp.count() > 0:
            custom_inp.click()
            custom_inp.fill(limit_val)
            time.sleep(0.3)
            print(f"  🔢 Đã nhập hạn mức tùy chỉnh: {limit_val} số/ngày vào ô 'Khác'")
        else:
            page.evaluate("""(val) => {
                const inp = document.querySelector('#daily_quota_custom') || document.querySelector('.ant-input-number-input');
                if (inp) {
                    inp.value = val;
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", limit_val)
            time.sleep(0.3)

    # Chỉnh giờ bắt đầu thành 07:00 (Click thật vào ô giờ bắt đầu để mở dropdown timepicker)
    try:
        page.locator("#allowed_sending_time:visible, #allowed_sending_time").first.click()
        time.sleep(0.8)
        
        # Chọn giờ 07 và bấm OK
        page.evaluate("""() => {
            const drop = document.querySelector('.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)');
            if (!drop) return;
            
            const col0 = drop.querySelectorAll('.ant-picker-time-panel-column')[0];
            if (col0) {
                const cells = Array.from(col0.querySelectorAll('.ant-picker-time-panel-cell'));
                const c07 = cells.find(c => c.innerText.trim() === '07');
                if (c07) {
                    (c07.querySelector('.ant-picker-time-panel-cell-inner') || c07).click();
                }
            }
            
            const okBtn = drop.querySelector('.ant-picker-ok button') || Array.from(drop.querySelectorAll('button')).find(b => b.innerText.trim() === 'OK');
            if (okBtn) okBtn.click();
        }""")
        time.sleep(0.5)
    except Exception as e:
        print(f"  ⚠️ Lưu ý chỉnh giờ: {e}")

    # Chọn radio "Gửi một lần"
    page.evaluate("""() => {
        const onceRadio = document.querySelector('input[value="once"]') || Array.from(document.querySelectorAll('.ant-radio-wrapper')).find(r => r.innerText.includes('Gửi một lần'));
        if (onceRadio) {
            onceRadio.click();
            onceRadio.closest('.ant-radio-wrapper')?.click();
        }
    }""")
    time.sleep(0.8)

    # Mở datepicker ngày gửi và chọn đúng ngày
    try:
        page.locator("#once_date:visible, #once_date").first.click()
        time.sleep(0.8)

        date_clicked = page.evaluate("""(targetIso) => {
            const parts = targetIso.split('-').map(Number);
            const targetYear = parts[0];
            const targetMonth = parts[1];
            const targetDay = parts[2];

            const drop = document.querySelector('.ant-picker-dropdown:not(.ant-picker-dropdown-hidden)');
            if (!drop) return false;

            const nextBtn = drop.querySelector('.ant-picker-header-next-btn');
            const prevBtn = drop.querySelector('.ant-picker-header-prev-btn');

            // Chuyển tháng bằng nút mũi tên '>' (next) hoặc '<' (prev)
            for (let step = 0; step < 24; step++) {
                const monthBtn = drop.querySelector('.ant-picker-month-btn');
                const yearBtn = drop.querySelector('.ant-picker-year-btn');
                if (!monthBtn || !yearBtn) break;

                // Lấy chính xác số tháng và năm từ nút riêng biệt (ví dụ: 'Tháng 10' -> 10, '2026' -> 2026)
                const curMonth = parseInt(monthBtn.innerText.replace(/\\D/g, ''), 10);
                const curYear = parseInt(yearBtn.innerText.replace(/\\D/g, ''), 10);

                if (isNaN(curMonth) || isNaN(curYear)) break;

                const curTotal = curYear * 12 + curMonth;
                const targetTotal = targetYear * 12 + targetMonth;

                if (curTotal < targetTotal) {
                    if (nextBtn) nextBtn.click();
                    else break;
                } else if (curTotal > targetTotal) {
                    if (prevBtn) prevBtn.click();
                    else break;
                } else {
                    // Đã đúng tháng và năm
                    break;
                }
            }

            // Sau khi đã ở đúng tháng, chọn ngày trong tháng (chỉ chọn ô active .ant-picker-cell-in-view)
            const inViewCells = Array.from(drop.querySelectorAll('.ant-picker-cell-in-view'));
            const targetCell = inViewCells.find(c => c.innerText.trim() === String(targetDay));
            if (targetCell) {
                (targetCell.querySelector('.ant-picker-cell-inner') || targetCell).click();
                return true;
            }
            return false;
        }""", target_date_iso)

        if not date_clicked:
            day_num = str(int(target_date_iso.split("-")[2]))
            page.locator(f".ant-picker-dropdown:visible .ant-picker-cell-in-view:has-text('{day_num}')").first.click(timeout=3000)

        time.sleep(0.5)
        print(f"  📅 Đã chọn ngày gửi: {target_date_disp}")
    except Exception as e:
        print(f"  ⚠️ Lưu ý chọn ngày: {e}")

    time.sleep(0.8)

    # 7. BẤM LƯU CHIẾN DỊCH
    print("  💾 Bấm nút [LƯU] hoàn tất...")
    page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const saveBtn = btns.find(b => b.innerText.trim() === 'Lưu' || (b.innerText.includes('Lưu') && !b.innerText.includes('nháp')));
        if (saveBtn) saveBtn.click();
    }""")

    # Chờ hoàn tất và quay lại danh sách
    time.sleep(3.5)
    print(f"  ✅ ĐÃ TẠO THÀNH CÔNG: {c_name}!")

    # 8. Ghi nhận lịch sử & tự động trừ số khỏi file nguồn
    phone_file = camp_info.get("phone_file", "sodaloc.txt")
    log_used_phones(c_name, target_page, target_date_disp, phones)
    remaining_count = remove_used_phones_from_file(phone_file, phones)
    print(f"  📝 Đã lưu {len(phones)} số vào 'sdt_da_dung.txt' & tự động trừ khỏi '{phone_file}' (Còn lại: {remaining_count} số).")

def main():
    campaigns = interactive_menu()

    print("\n🔌 Đang kết nối tới trình duyệt Chrome (Port 9222)...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"\n❌ Lỗi kết nối tới Chrome trên cổng 9222!")
            print(f"Chi tiết: {e}")
            print("\n👉 Hãy đảm bảo bạn đã mở Chrome với flag: --remote-debugging-port=9222")
            input("\nBấm Enter để thoát...")
            return

        contexts = browser.contexts
        if not contexts or not contexts[0].pages:
            print("❌ Không tìm thấy tab nào đang mở trên Chrome.")
            return

        # Tìm page của Sale Platform
        target_page = None
        for pg in contexts[0].pages:
            if "mega-push-campaign" in pg.url or "fpt.vn" in pg.url:
                target_page = pg
                break
        
        if not target_page:
            target_page = contexts[0].pages[0]

        print(f"✅ Đã kết nối tab: {target_page.title()}")

        success_count = 0
        for idx, camp in enumerate(campaigns, start=1):
            print(f"\n[{idx}/{len(campaigns)}] =====================================")
            try:
                create_single_campaign(target_page, camp)
                success_count += 1
            except Exception as ex:
                print(f"  ❌ Lỗi khi tạo chiến dịch '{camp['name']}': {ex}")
                time.sleep(2)

        print("\n" + "=" * 60)
        print(f"🎉 ĐÃ HOÀN TẤT! Tạo thành công {success_count}/{len(campaigns)} chiến dịch.")
        print("=" * 60)
        input("\n👉 Bấm Enter để kết thúc...")

if __name__ == "__main__":
    main()
