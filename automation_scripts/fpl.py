import os
import sys
import time
import re
from lxml import etree
import uiautomator2 as u2

# Cấu hình UTF-8 cho console Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

OUTPUT_FILE = "fpl.txt"

def log(msg):
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

def ensure_output_file():
    saved_phones = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip()
                    if p:
                        saved_phones.add(p)
        except Exception:
            pass
    return saved_phones

def save_phone(phone, saved_phones):
    if not phone:
        return False
    if phone in saved_phones:
        log(f"⚠️ SĐT {phone} đã có trong danh sách.")
        return False

    try:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"{phone}\n")
    except Exception as e:
        log(f"Lỗi ghi {OUTPUT_FILE}: {e}")

    saved_phones.add(phone)
    log(f"💾 ĐÃ LƯU SĐT: {phone} -> {OUTPUT_FILE}")
    return True

def parse_hierarchy(d):
    """Lấy xml hierarchy để quét danh sách khách hàng"""
    try:
        xml_str = d.dump_hierarchy()
        return etree.fromstring(xml_str.encode('utf-8'))
    except Exception:
        return None

def parse_bounds(bounds_str):
    m = re.findall(r'\d+', bounds_str)
    if len(m) >= 4:
        return tuple(map(int, m[:4]))
    return None

def click_kxd_customer(d, tree):
    """
    Tìm item khách hàng có chữ KXĐ trong danh sách và click
    """
    nodes = tree.xpath('//*[contains(@content-desc, "KXĐ") or contains(@text, "KXĐ")]')
    for node in nodes:
        desc = node.attrib.get('content-desc', '')
        text = node.attrib.get('text', '')
        label = desc if desc else text
        
        if "KXĐ" not in label:
            continue
            
        bounds_str = node.attrib.get('bounds', '')
        b = parse_bounds(bounds_str)
        if not b:
            continue
            
        x1, y1, x2, y2 = b
        
        # Bỏ qua nếu nằm ở vùng header / tabs trên
        if y1 < 350:
            continue
            
        # Nếu item nằm quá sát mép dưới, cuộn nhẹ lên
        if y2 > 1200:
            log(f"Khách KXĐ ở sát mép dưới ({y1}-{y2}), cuộn nhẹ lên...")
            d.swipe(360, 950, 360, 750, duration=0.25)
            time.sleep(0.8)
            tree_new = parse_hierarchy(d)
            if tree_new is None:
                return False
            return click_kxd_customer(d, tree_new)
            
        click_x = (x1 + x2) // 2
        click_y = (y1 + y2) // 2
        log(f"🎯 Bấm vào khách '{label.strip()}' tại [{x1},{y1}]...")
        d.click(click_x, click_y)
        return True
        
    return False

def extract_phone_number(d):
    """Trích xuất SĐT từ màn hình chi tiết"""
    time.sleep(0.8)
    
    # 1. Thử qua selector u2
    try:
        el = d(descriptionMatches=r".*Số điện thoại\s*\n?\s*[0-9+]{9,12}.*")
        if el.exists:
            desc = el.info.get('contentDescription', '')
            m = re.search(r'Số điện thoại\s*\n?\s*([0-9+]{9,12})', desc)
            if m:
                return m.group(1).strip()
    except Exception:
        pass

    # 2. Quét toàn bộ hierarchy
    tree = parse_hierarchy(d)
    if tree is not None:
        for node in tree.xpath('//*[@content-desc or @text]'):
            content = (node.attrib.get('content-desc') or '') + " " + (node.attrib.get('text') or '')
            m = re.search(r'Số điện thoại\s*\n?\s*([0-9+]{9,12})', content)
            if m:
                return m.group(1).strip()
        for node in tree.xpath('//*[@content-desc or @text]'):
            content = (node.attrib.get('content-desc') or '') + " " + (node.attrib.get('text') or '')
            m = re.search(r'(0[3|5|7|8|9]\d{8})', content)
            if m:
                return m.group(1).strip()
    return None

def open_consultation_form(d):
    """
    Cuộn xuống để thấy 'Lịch sử tư vấn' và bấm nút thêm (+) ở góc phải.
    Xử lý cả trường hợp đã có hoặc chưa có lịch sử tư vấn trước đó.
    """
    log("📜 Cuộn xuống tìm 'Lịch sử tư vấn'...")
    d.swipe(360, 850, 360, 450, duration=0.3)
    time.sleep(0.8)

    el = d(descriptionContains="Lịch sử tư vấn")
    if not el.exists:
        d.swipe(360, 800, 360, 500, duration=0.25)
        time.sleep(0.6)
        el = d(descriptionContains="Lịch sử tư vấn")

    if el.exists:
        info = el.info
        b = info.get('bounds')
        click_x = b['right'] - 40
        click_y = (b['top'] + b['bottom']) // 2
        log(f"👉 Bấm vào icon thêm tư vấn (+) tại ({click_x}, {click_y})...")
        d.click(click_x, click_y)
        return click_x, click_y
    else:
        log("Thử bấm vào vùng Lịch sử tư vấn tại (653, 780)...")
        d.click(653, 780)
        return 653, 780

def fill_consultation_and_confirm(d, retry_coords=(653, 780)):
    """
    Điền form Cập nhật kết quả tư vấn:
    - Tình trạng tư vấn: Gọi lại sau
    - Kết quả tư vấn: KH đang bận, hẹn gọi lại sau
    - Xác nhận
    """
    log("⏳ Chờ mở form 'Cập nhật kết quả tư vấn'...")
    form_opened = d(descriptionContains="Tình trạng tư vấn").wait(timeout=4.0)
    
    if not form_opened:
        log("Chưa thấy form, thử bấm lại icon thêm (+)...")
        d.click(retry_coords[0], retry_coords[1])
        form_opened = d(descriptionContains="Tình trạng tư vấn").wait(timeout=3.0)
        
    if not form_opened:
        log("❌ Không mở được form tư vấn!")
        return False

    # 1. Chọn Tình trạng tư vấn: Gọi lại sau
    log("🔽 Mở dropdown 'Tình trạng tư vấn'...")
    d(descriptionContains="Tình trạng tư vấn").click()
    time.sleep(0.6)
    
    log("👉 Chọn 'Gọi lại sau'...")
    opt_status = d(description="Gọi lại sau")
    if opt_status.wait(timeout=2.0):
        opt_status.click()
    else:
        node = d.xpath('//*[contains(@content-desc, "Gọi lại sau")]')
        if node.exists:
            node.click()
        else:
            log("❌ Không tìm thấy mục 'Gọi lại sau'!")
            return False
    time.sleep(0.6)

    # 2. Chọn Kết quả tư vấn: KH đang bận, hẹn gọi lại sau
    log("🔽 Mở dropdown 'Kết quả tư vấn'...")
    d(descriptionContains="Kết quả tư vấn").click()
    time.sleep(0.6)
    
    log("👉 Chọn 'KH đang bận, hẹn gọi lại sau'...")
    opt_result = d(descriptionContains="KH đang bận")
    if opt_result.wait(timeout=2.0):
        opt_result.click()
    else:
        node = d.xpath('//*[contains(@content-desc, "KH đang bận")]')
        if node.exists:
            node.click()
        else:
            log("❌ Không tìm thấy mục 'KH đang bận, hẹn gọi lại sau'!")
            return False
    time.sleep(0.6)

    # 3. Bấm nút Xác nhận
    log("✅ Bấm 'Xác nhận' cập nhật...")
    confirm_btn = d(description="Xác nhận")
    if confirm_btn.exists:
        confirm_btn.click()
    else:
        d.click(360, 1205)
    time.sleep(1.2)

    # 4. Xử lý popup Thông báo Cập nhật thành công
    handle_popup_after_confirm(d)
    return True

def handle_popup_after_confirm(d):
    """Chờ và đóng popup Thông báo Cập nhật thành công"""
    for _ in range(6):
        time.sleep(0.5)
        btns = d(description="Xác nhận")
        if btns.exists:
            log("📢 Đã thấy popup thông báo. Bấm 'Xác nhận' đóng popup...")
            btns.click()
            time.sleep(0.8)
            return True
    return False

def enter_khtn_from_home(d):
    """Nhận diện và bấm vào Khách hàng tiềm năng nếu đang ở màn hình chính SOP"""
    # 1. Tìm qua text
    btn = d(text="Khách hàng tiềm năng")
    if not btn.exists:
        btn = d(textContains="Khách hàng")
    if not btn.exists:
        btn = d(descriptionContains="Khách hàng tiềm năng")
    if not btn.exists:
        btn = d(descriptionContains="Khách hàng")

    if btn.exists:
        log("📱 Phát hiện đang ở Trang chủ SOP, bấm vào 'Khách hàng tiềm năng'...")
        btn.click()
        time.sleep(2.0)
        return True

    # 2. Kiểm tra nếu có các icon đặc trưng của màn hình chính (Đơn hàng, Tập điểm, Trang chủ)
    if d(text="Đơn hàng").exists or d(text="Tập điểm").exists or d(text="Tính năng ưa thích").exists or d(description="Trang chủ").exists:
        log("📱 Đang ở Trang chủ SOP, click tọa độ nút Khách hàng tiềm năng (276, 878)...")
        d.click(276, 878)
        time.sleep(2.0)
        return True

    return False

def back_to_customer_list(d):
    """
    Bấm Back an toàn để quay về màn hình danh sách ban đầu (Chưa tư vấn).
    Nếu lỡ back ra màn hình chính của SOP thì tự động bấm vào lại 'Khách hàng tiềm năng'.
    """
    log("🔙 Quay lại danh sách KH tiềm năng...")
    for attempt in range(4):
        # 1. Nếu đã về tới tab danh sách Chưa tư vấn -> Xong
        if d(descriptionContains="Chưa tư vấn").exists:
            log("✅ Đã về màn hình danh sách.")
            return True

        # 2. Nếu lỡ rơi ra Trang chủ màn hình chính SOP -> Tự động vào lại Khách hàng tiềm năng
        if enter_khtn_from_home(d):
            if d(descriptionContains="Chưa tư vấn").wait(timeout=3.0):
                log("✅ Đã vào lại màn hình danh sách từ Trang chủ.")
                return True

        log(f"Bấm phím Back (lần {attempt + 1})...")
        d.press("back")
        time.sleep(1.0)

    # Kiểm tra lần cuối sau khi thoát vòng lặp
    if d(descriptionContains="Chưa tư vấn").exists:
        return True
    return enter_khtn_from_home(d)

def check_and_enter_khtn(d):
    """Kiểm tra nếu đang ở trang chủ thì bấm vào Khách hàng tiềm năng"""
    if d(descriptionContains="Chưa tư vấn").exists:
        log("✅ Đang ở sẵn danh sách 'KH tiềm năng'.")
        return True
    return enter_khtn_from_home(d)

def main():
    print("=" * 60)
    print("     TOOL FPL - TỰ ĐỘNG XỬ LÝ KHÁCH HÀNG TIỀM NĂNG")
    print("=" * 60)
    
    saved_phones = ensure_output_file()
    log(f"Đã có {len(saved_phones)} SĐT trong file lưu trữ.")
    
    log("Đang kết nối giả lập qua uiautomator2...")
    try:
        d = u2.connect()
        info = d.info
        log(f"✅ Đã kết nối: {info.get('productName', 'Android')} ({info.get('displayWidth')}x{info.get('displayHeight')})")
    except Exception as e:
        log(f"❌ Lỗi kết nối giả lập: {e}")
        return

    # Vào danh sách nếu đang ở ngoài Trang chủ
    check_and_enter_khtn(d)

    consecutive_no_kxd = 0
    MAX_NO_KXD_SWIPES = 8
    processed_count = 0

    while True:
        try:
            # Luôn đảm bảo đang ở màn hình danh sách Chưa tư vấn
            if not d(descriptionContains="Chưa tư vấn").exists:
                # Nếu ở Trang chủ thì vào lại
                if not enter_khtn_from_home(d):
                    back_to_customer_list(d)
                time.sleep(1.0)

            tree = parse_hierarchy(d)
            if tree is None:
                time.sleep(0.8)
                continue

            # Tìm và click vào khách có chữ KXĐ
            clicked = click_kxd_customer(d, tree)
            
            if clicked:
                consecutive_no_kxd = 0
                time.sleep(1.0)
                
                # 1. Trích xuất số điện thoại
                phone = extract_phone_number(d)
                if phone:
                    log(f"📞 Tìm thấy SĐT: {phone}")
                else:
                    log("⚠️ Chưa đọc được SĐT ở trang này!")
                    
                # 2. Cuộn xuống và mở form thêm tư vấn (nút + ở dòng Lịch sử tư vấn)
                coords = open_consultation_form(d)
                
                # 3. Điền form tư vấn và Xác nhận
                ok = fill_consultation_and_confirm(d, retry_coords=coords)
                
                if ok:
                    # Chỉ lưu SĐT khi đã cập nhật tư vấn thành công lên hệ thống
                    if phone:
                        save_phone(phone, saved_phones)
                    processed_count += 1
                    log(f"🎉 ĐÃ XỬ LÝ XONG KHÁCH #{processed_count} (Tổng: {len(saved_phones)} SĐT)")
                else:
                    log("⚠️ Không hoàn thành form, quay lại danh sách...")
                    
                # 4. Trở ra danh sách ban đầu (tự xử lý nếu lỡ văng ra Trang chủ)
                back_to_customer_list(d)
                time.sleep(1.0)
                
            else:
                consecutive_no_kxd += 1
                log(f"Không thấy khách KXĐ trên màn hình. Đang cuộn xuống tìm tiếp ({consecutive_no_kxd}/{MAX_NO_KXD_SWIPES})...")
                d.swipe(360, 950, 360, 450, duration=0.3)
                time.sleep(1.2)
                
                if consecutive_no_kxd >= MAX_NO_KXD_SWIPES:
                    log("🏁 Đã duyệt hết danh sách!")
                    print("=" * 60)
                    print(f"Hoàn thành! Đã xử lý {processed_count} khách trong phiên này.")
                    print(f"Tổng số SĐT trong file: {len(saved_phones)}")
                    print("=" * 60)
                    break

        except KeyboardInterrupt:
            log("🛑 Người dùng bấm dừng tool.")
            break
        except Exception as e:
            log(f"⚠️ Có lỗi xảy ra: {e}")
            time.sleep(1.5)
            back_to_customer_list(d)

if __name__ == "__main__":
    main()
