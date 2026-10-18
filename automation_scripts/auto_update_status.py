import os
import sys
import time
import random
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

CDP_PORT = 9223

# Danh sách 5 cấu hình trạng thái & chi tiết tương ứng để Random
STATUS_OPTIONS = [
    {
        "name": "Đã có SĐT Chưa liên lạc được",
        "status": "Đã có SĐT Chưa liên lạc được",
        "detail": "KH không nghe máy/từ chối cuộc gọi"
    },
    {
        "name": "Đã có SĐT Chưa xác định kết quả",
        "status": "Đã có SĐT Chưa xác định kết quả",
        "detail": "Khách suy nghĩ"
    },
    {
        "name": "Đã có SĐT Liên lạc được nhưng Chưa TV",
        "status": "Đã có SĐT Liên lạc được nhưng Chưa TV",
        "detail": "KH đang bận, hẹn gọi lại sau"
    },
    {
        "name": "Không thành công",
        "status": "Không thành công",
        "detail": "Khu vực không có hạ tầng"
    },
    {
        "name": "Không cần hỗ trợ",
        "status": "Không cần hỗ trợ",
        "detail": "Đã sử dụng dịch vụ đang tư vấn của FPT"
    }
]

def connect_to_portal(playwright, max_attempts=10):
    for attempt in range(max_attempts):
        try:
            browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
            context = browser.contexts[0]
            page = next((t for t in context.pages if "portal-sop.fpt.vn" in t.url), None)
            if page:
                print(f"✅ Đã kết nối tab Portal: {page.title()} ({page.url})")
                return browser, page
        except Exception:
            pass
        print(f"⏳ Đang kết nối tới Chrome cổng {CDP_PORT} (lần {attempt + 1}/{max_attempts})...")
        time.sleep(2)
    raise Exception(f"Không thể kết nối Chrome cổng {CDP_PORT}. Vui lòng kiểm tra lại trình duyệt.")

def pick_dropdown_item(page, select_locator, target_text, timeout=4000):
    """
    Click mở dropdown và chọn mục target_text (hỗ trợ cuộn ảo Virtual List của Ant Design và tự phục hồi)
    """
    try:
        if not select_locator.is_visible(timeout=timeout):
            return False
        select_locator.click(timeout=2000)
    except Exception:
        try:
            select_locator.evaluate("el => el.click()")
        except Exception:
            return False
    page.wait_for_timeout(300)

    # Lấy dropdown mở mới nhất
    dd_locator = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)")
    try:
        dd_locator.last.wait_for(state="visible", timeout=timeout)
    except Exception:
        return False

    dd = dd_locator.last

    # 1. Thử tìm và click ngay nếu mục đang hiển thị trên màn hình
    opt = dd.locator(".ant-select-item-option").filter(has_text=target_text)
    if opt.count() > 0 and opt.first.is_visible():
        try:
            opt.first.click()
        except Exception:
            opt.first.evaluate("el => el.click()")
        return True

    # 2. Nếu chưa thấy, cuộn chuột ảo trong dropdown để tìm
    dd_box = dd.bounding_box()
    if dd_box:
        page.mouse.move(dd_box['x'] + dd_box['width'] / 2, dd_box['y'] + dd_box['height'] / 2)
        
        # Cuộn xuống
        for _ in range(8):
            page.mouse.wheel(0, 180)
            page.wait_for_timeout(150)
            opt = dd.locator(".ant-select-item-option").filter(has_text=target_text)
            if opt.count() > 0 and opt.first.is_visible():
                try:
                    opt.first.click()
                except Exception:
                    opt.first.evaluate("el => el.click()")
                return True

        # Cuộn ngược lên nếu bị trôi
        for _ in range(8):
            page.mouse.wheel(0, -180)
            page.wait_for_timeout(150)
            opt = dd.locator(".ant-select-item-option").filter(has_text=target_text)
            if opt.count() > 0 and opt.first.is_visible():
                try:
                    opt.first.click()
                except Exception:
                    opt.first.evaluate("el => el.click()")
                return True

    return False

def update_single_lead(page, row_el, index):
    """
    Xử lý cập nhật 1 khách hàng an toàn tuyệt đối:
    1. Lấy thông tin Tên + SĐT
    2. Click vào badge 'Đã có SĐT Chưa liên hệ'
    3. Random 1 trong 5 cấu hình trạng thái
    4. Chọn Tình trạng & chờ Chi tiết mở khóa -> Chọn Chi tiết tương ứng
    5. Bấm nút 'Lưu kết quả'
    """
    try:
        try:
            cus_info = row_el.locator("td").nth(1).inner_text().strip().replace('\n', ' - ')
        except Exception:
            cus_info = f"Khách hàng #{index + 1}"

        # Random 1 trong 5 trạng thái
        choice = random.choice(STATUS_OPTIONS)
        target_status = choice["status"]
        target_detail = choice["detail"]

        print(f"\n👉 [{index + 1}] Đang xử lý: {cus_info}")
        print(f"   🎲 Chọn Random: '{target_status}' -> '{target_detail}'")

        # Đóng bất kỳ modal hoặc popover cũ nào đang treo
        try:
            old_modals = page.locator(".ant-modal:visible")
            if old_modals.count() > 0:
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
        except Exception:
            pass

        # Tìm badge tình trạng trên dòng (linh hoạt với mọi class hash)
        badge = row_el.locator("[class*='status_badge']:has-text('Đã có SĐT Chưa liên hệ'), span:has-text('Đã có SĐT Chưa liên hệ')")
        if badge.count() == 0 or not badge.first.is_visible():
            print("   ⚠️ Không tìm thấy nút trạng thái 'Đã có SĐT Chưa liên hệ' ở dòng này.")
            return False

        # Click badge để mở modal
        badge.first.click(timeout=3000)
        
        # Chờ modal xuất hiện
        modal = page.locator(".ant-modal:visible:has-text('Kết quả tư vấn'), .ant-modal:has-text('Kết quả tư vấn')").last
        try:
            modal.wait_for(state="visible", timeout=4000)
        except Exception:
            print("   ⚠️ Modal 'Kết quả tư vấn' không xuất hiện sau khi click.")
            return False

        page.wait_for_timeout(300)

        # 1. Chọn 'Tình trạng'
        tinh_trang_select = modal.locator(".ant-form-item:has(label:has-text('Tình trạng')) .ant-select, .ant-select").first
        try:
            tinh_trang_select.wait_for(state="visible", timeout=4000)
        except Exception:
            print("   ⚠️ Không thấy ô chọn 'Tình trạng'. Đóng modal...")
            cancel_btn = modal.locator("button:has-text('Hủy'), .ant-modal-close")
            if cancel_btn.count() > 0:
                cancel_btn.first.click()
            return False

        ok_status = pick_dropdown_item(page, tinh_trang_select, target_status)
        if not ok_status:
            print(f"   ⚠️ Không tìm thấy lựa chọn tình trạng '{target_status}'.")
            cancel_btn = modal.locator("button:has-text('Hủy'), .ant-modal-close")
            if cancel_btn.count() > 0:
                cancel_btn.first.click()
            return False

        # 2. CHỜ Ô 'CHI TIẾT' ĐƯỢC MỞ KHÓA
        ct_enabled = modal.locator(".ant-form-item:has(label:has-text('Chi tiết')) .ant-select:not(.ant-select-disabled)")
        try:
            ct_enabled.wait_for(state="visible", timeout=5000)
        except Exception:
            print("   ⚠️ Ô 'Chi tiết' chưa được mở khóa sau khi chọn tình trạng.")
            cancel_btn = modal.locator("button:has-text('Hủy'), .ant-modal-close")
            if cancel_btn.count() > 0:
                cancel_btn.first.click()
            return False

        # 3. Chọn 'Chi tiết'
        ok_detail = pick_dropdown_item(page, ct_enabled, target_detail)
        if not ok_detail:
            print(f"   ⚠️ Không tìm thấy lựa chọn chi tiết '{target_detail}'.")
            cancel_btn = modal.locator("button:has-text('Hủy'), .ant-modal-close")
            if cancel_btn.count() > 0:
                cancel_btn.first.click()
            return False

        page.wait_for_timeout(800)

        # 4. Bấm 'Lưu kết quả'
        save_btn = modal.locator("button:has-text('Lưu kết quả'), button:has-text('Lưu')").last
        save_btn.click(timeout=3000)

        # Chờ modal đóng lại và table nạp lại dữ liệu
        try:
            modal.wait_for(state="hidden", timeout=5000)
        except Exception:
            close_btn = modal.locator(".ant-modal-close, button:has-text('Hủy')")
            if close_btn.count() > 0:
                close_btn.first.click()
        
        print(f"   ✅ Đã Lưu kết quả thành công!")
        # Nghỉ để table cập nhật badge mới
        page.wait_for_timeout(800)
        return True

    except Exception as e:
        print(f"   ⚠️ Lỗi khi cập nhật dòng này: {e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False

def run():
    print("=" * 65)
    print("🤖 TOOL TỰ ĐỘNG CẬP NHẬT TRẠNG THÁI KHÁCH HÀNG (RANDOM 5 TRẠNG THÁI)")
    print("📋 Danh sách 5 cấu hình Random:")
    for idx, opt in enumerate(STATUS_OPTIONS, 1):
        print(f"   {idx}. {opt['status']}  -->  {opt['detail']}")
    print("=" * 65)

    with sync_playwright() as p:
        browser, page = connect_to_portal(p)

        print("\nTùy chọn chế độ chạy:")
        print("  [Enter] : Chạy tự động toàn bộ danh sách (qua tất cả các trang)")
        print("  [1]     : Chỉ chạy thử nghiệm ĐÚNG 1 khách hàng đầu tiên rồi dừng")
        print("  [p]     : Chỉ chạy hết TRANG HIỆN TẠI rồi dừng (không tự sang trang)")
        
        if "--auto" in sys.argv or "-y" in sys.argv:
            print("\n🚀 [CHẾ ĐỘ TỰ ĐỘNG] Tự động bắt đầu cập nhật toàn bộ sau 1 giây...")
            time.sleep(1)
            mode = ""
        else:
            mode = input("\n👉 Nhập lựa chọn của bạn (Nhấn Enter để chạy toàn bộ): ").strip().lower()

        total_processed = 0

        while True:
            # Lấy thông tin trang hiện tại
            current_page_num = page.evaluate("""() => {
                const active = document.querySelector('.ant-pagination-item-active');
                return active ? active.innerText.trim() : '1';
            }""")
            print(f"\n==================== ĐANG Ở TRANG {current_page_num} ====================")

            # Lấy danh sách các dòng cần xử lý còn lại trên trang
            while True:
                # Tìm các dòng có trạng thái 'Đã có SĐT Chưa liên hệ' (hỗ trợ mọi class name hash)
                target_rows = page.locator("tr.ant-table-row").filter(
                    has=page.locator("[class*='status_badge']:has-text('Đã có SĐT Chưa liên hệ'), span:has-text('Đã có SĐT Chưa liên hệ')")
                )
                count = target_rows.count()

                if count == 0:
                    print(f"🏁 Đã xử lý xong toàn bộ danh sách ở Trang {current_page_num}!")
                    break

                # Luôn lấy dòng đầu tiên đang còn trạng thái này
                row_el = target_rows.first
                success = update_single_lead(page, row_el, total_processed)
                if success:
                    total_processed += 1

                if mode == '1':
                    print("\n🛑 Chế độ thử nghiệm 1 khách hàng đã hoàn thành!")
                    return

                # Nghỉ ngắn giữa các khách hàng
                time.sleep(1.0)

            if mode == 'p':
                print("\n🛑 Đã xử lý xong trang hiện tại theo yêu cầu!")
                break

            # Kiểm tra xem còn trang tiếp theo không
            next_page_btn = page.locator("li.ant-pagination-next:not(.ant-pagination-disabled)")
            if next_page_btn.count() > 0 and next_page_btn.is_visible():
                print(f"\n🔄 Đang chuyển sang trang tiếp theo...")
                next_page_btn.click()
                # Chờ trang mới nạp xong
                page.wait_for_timeout(2000)
                # Kiểm tra số trang mới
                new_page_num = page.evaluate("""() => {
                    const active = document.querySelector('.ant-pagination-item-active');
                    return active ? active.innerText.trim() : '1';
                }""")
                if new_page_num == current_page_num:
                    print("⚠️ Đã bấm chuyển trang nhưng số trang không đổi. Kết thúc.")
                    break
            else:
                print("\n🏁 Đã đến trang cuối cùng, không còn trang kế tiếp.")
                break

        print("\n" + "=" * 65)
        print(f"🎉 HOÀN THÀNH TẤT CẢ! Tổng số khách hàng đã cập nhật: {total_processed}")
        print("=" * 65)

if __name__ == "__main__":
    run()
