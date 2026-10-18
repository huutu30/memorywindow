import os
import sys
import json
import time
import re
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

CDP_PORT = 9222
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_label_history.json")

TARGET_COUNT = 800
for _i, _arg in enumerate(sys.argv):
    if _arg == "--target" and _i + 1 < len(sys.argv) and sys.argv[_i + 1].isdigit():
        TARGET_COUNT = int(sys.argv[_i + 1])

AUTO_SHUTDOWN = "--shutdown" in sys.argv
SHUTDOWN_COUNTDOWN = 600
for _i, _arg in enumerate(sys.argv):
    if _arg == "--countdown" and _i + 1 < len(sys.argv) and sys.argv[_i + 1].isdigit():
        SHUTDOWN_COUNTDOWN = int(sys.argv[_i + 1])

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"processed_ids": [], "processed_names": [], "total_count": 0, "contracts_found": 0, "labels_added": 0}

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Không thể lưu lịch sử: {e}")

def mark_chat_processed(history, room_id, name, result_type):
    key = f"{name}_{room_id}" if room_id else name
    if key not in history["processed_ids"]:
        history["processed_ids"].append(key)
        history["processed_names"].append(name)
        history["total_count"] += 1
        if result_type == "CONTRACT":
            history["contracts_found"] = history.get("contracts_found", 0) + 1
        elif result_type == "LABEL_ADDED":
            history["labels_added"] = history.get("labels_added", 0) + 1
        save_history(history)

def is_chat_processed(history, room_id, name):
    key = f"{name}_{room_id}" if room_id else name
    return key in history["processed_ids"] or name in history["processed_names"]

def scroll_chat_list_to_load_more(page):
    """Cuộn danh sách hội thoại để nạp thêm hội thoại mới từ server"""
    prev_count = page.locator("li[class*='lists-chat-']").count()
    for _ in range(3):
        try:
            page.evaluate("""() => {
                const first = document.querySelector("li[class*='lists-chat-']");
                if (first) {
                    let p = first.parentElement;
                    while (p && p !== document.body) {
                        const st = window.getComputedStyle(p);
                        if (p.scrollHeight > p.clientHeight && (st.overflowY === 'auto' || st.overflowY === 'scroll')) {
                            p.scrollTop = p.scrollHeight;
                            break;
                        }
                        p = p.parentElement;
                    }
                }
                const view = document.querySelector(".view-S88vge") || document.querySelector("[class*='view-']");
                if (view) {
                    view.scrollTop = view.scrollHeight;
                }
            }""")
        except Exception:
            pass

        try:
            last_li = page.locator("li[class*='lists-chat-']").last
            if last_li.is_visible():
                last_li.scroll_into_view_if_needed(timeout=1500)
        except Exception:
            pass

        try:
            page.mouse.wheel(0, 300)
        except Exception:
            pass

        page.wait_for_timeout(1200)
        new_count = page.locator("li[class*='lists-chat-']").count()
        if new_count > prev_count:
            return new_count
    return prev_count

def connect_to_portal(playwright, max_attempts=15):
    for attempt in range(max_attempts):
        try:
            browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
            context = browser.contexts[0]
            page = next((t for t in context.pages if "portal-sop.fpt.vn" in t.url), None)
            if page:
                print(f"✅ Đã kết nối tới tab Portal (cổng {CDP_PORT}): {page.title()}")
                return browser, page
        except Exception:
            pass
        print(f"⏳ Đang chờ kết nối tới Chrome cổng {CDP_PORT} (Thử lại {attempt + 1}/{max_attempts})...")
        time.sleep(2)
    raise Exception(f"Không thể kết nối tới tab portal-sop.fpt.vn trên cổng {CDP_PORT}.")

def process_single_chat(page, chat_item, chat_index):
    """
    Xử lý đúng 1 hội thoại:
    1. Click mở hội thoại
    2. Bấm 'Tra cứu Tạo SR' và click nút Tra cứu
    3. Nhận diện có hợp đồng hay không
    4. Nếu chưa có hợp đồng: Về tab Thông tin, gắn nhãn 'Chưa dùng mạng nào', Lưu
    Trả về: (status: str, room_id: str, chat_name: str)
    """
    try:
        chat_text = chat_item.inner_text()
        chat_name = chat_text.split('\n')[0].strip()
    except Exception:
        chat_name = f"Hội thoại #{chat_index + 1}"

    print(f"\n{'=' * 55}")
    print(f"👉 [#{chat_index + 1}] Bắt đầu xử lý: {chat_name}")
    print(f"{'=' * 55}")

    # 1. Click mở hội thoại
    try:
        chat_item.evaluate("el => el.click()")
    except Exception:
        chat_item.click(force=True, timeout=2000)
    page.wait_for_timeout(1200)

    room_id = page.url.split("/t/")[-1].split("?")[0] if "/t/" in page.url else ""

    # 2. Bấm tab 'Tra cứu Tạo SR'
    cus_tab = page.locator("[id*='tab-cus360'], .ant-tabs-tab:has-text('Tra cứu')")
    if cus_tab.count() == 0 or not cus_tab.first.is_visible():
        print("⚠️ Không thấy tab 'Tra cứu Tạo SR'.")
        return "ERROR_NO_TAB", room_id, chat_name

    cus_tab.first.click()
    page.wait_for_timeout(800)

    # 3. Bấm nút Tra cứu nếu có
    tra_cuu_btn = page.locator("button:has-text('Tra cứu')")
    if tra_cuu_btn.count() > 0 and tra_cuu_btn.first.is_visible():
        print("   🔍 Bấm nút 'Tra cứu'...")
        tra_cuu_btn.first.click()
        # Chờ kết quả tra cứu nạp xong
        page.wait_for_timeout(2500)
    else:
        # Đã tra cứu sẵn trước đó
        page.wait_for_timeout(600)

    # 4. Kiểm tra có hợp đồng hay không (Kiểm tra trong iframe cus360)
    # Vì toàn bộ kết quả tra cứu HĐ được nhúng trong iframe cus360.fpt.vn
    cus_frame = None
    for _ in range(8):
        cus_frame = next((f for f in page.frames if "cus360.fpt.vn" in f.url), None)
        if cus_frame:
            break
        page.wait_for_timeout(400)

    has_contract = False
    contract_snippet = ""

    if cus_frame:
        # Chờ iframe nạp xong dữ liệu
        for _ in range(6):
            try:
                frame_text = cus_frame.evaluate("() => document.body ? document.body.innerText.trim() : ''")
                if "Không có hợp đồng" in frame_text:
                    has_contract = False
                    break
                elif "Danh sách hợp đồng" in frame_text:
                    # Nếu có 'Danh sách hợp đồng' và không có 'Không có hợp đồng' -> ĐÃ CÓ HỢP ĐỒNG!
                    has_contract = True
                    lines = [line.strip() for line in frame_text.split('\n') if line.strip() and line.strip() != "Danh sách hợp đồng"]
                    contract_snippet = " | ".join(lines[:3]) if lines else "Đã tìm thấy HĐ"
                    break
            except Exception:
                pass
            page.wait_for_timeout(500)
    else:
        # Dự phòng kiểm tra nếu hiển thị ngoài frame
        panel_text = page.evaluate('''() => {
            const sider = document.querySelector('.sider-m1Q2FR') || document.querySelector('[id*="panel-cus360"]') || document.body;
            return sider ? sider.innerText : '';
        }''')
        if "Không có hợp đồng" in panel_text:
            has_contract = False
        elif "Danh sách hợp đồng" in panel_text and not ("Không có hợp đồng" in panel_text):
            has_contract = True

    if has_contract:
        print(f"✅ [ĐÃ CÓ HỢP ĐỒNG] Khách '{chat_name}' ĐÃ CÓ HỢP ĐỒNG ({contract_snippet}) -> BỎ QUA, KHÔNG GẮN NHÃN!")
        return "CONTRACT", room_id, chat_name

    print(f"⚠️ [CHƯA CÓ HỢP ĐỒNG] Khách '{chat_name}' chưa có hợp đồng -> Chuyển về gắn nhãn...")

    # 5. Quay lại tab 'Thông tin'
    info_tab = page.locator("[id*='tab-info']")
    if info_tab.count() > 0:
        info_tab.first.click()
        page.wait_for_timeout(800)

    # Kiểm tra xem khách đã được gắn nhãn 'Chưa dùng mạng nào' từ trước chưa
    already_tagged = page.locator(".ant-card:has(.ant-card-head-title:has-text('Nhãn')) div:has-text('Chưa dùng mạng nào'), .name-cx50Qx:has-text('Chưa dùng mạng nào')")
    if already_tagged.count() > 0 and already_tagged.first.is_visible():
        print("ℹ️ Đã có sẵn nhãn 'Chưa dùng mạng nào' -> Hoàn tất, không cần gắn lại.")
        return "LABEL_ADDED", room_id, chat_name

    # 6. Bấm Gắn nhãn
    gan_nhan = page.locator("span:has-text('Gắn nhãn'), span:has-text('Gán nhãn')")
    if gan_nhan.count() > 0 and gan_nhan.first.is_visible():
        print("   🏷️ Bấm 'Gắn nhãn'...")
        gan_nhan.first.click()
        page.wait_for_timeout(600)

    # 7. Bấm vào ô input nhãn
    nhan_card = page.locator(".ant-card:has(.ant-card-head-title:has-text('Nhãn'))")
    nhan_input = nhan_card.locator("input")
    if nhan_input.count() > 0 and nhan_input.first.is_visible():
        print("   🖱️ Bấm vào ô nhập nhãn...")
        nhan_input.first.click()
        page.wait_for_timeout(700)

    # 8. Chọn 'Chưa dùng mạng nào'
    target = page.locator(".item-MBRHM6").filter(has_text="Chưa dùng mạng nào")
    if target.count() > 0:
        print("   ⭐ Chọn nhãn 'Chưa dùng mạng nào'...")
        target.first.click()
        page.wait_for_timeout(500)
    else:
        print("   ⚠️ Không tìm thấy nhãn 'Chưa dùng mạng nào' trong danh sách gợi ý.")

    # 9. Bấm Lưu
    save_btn = nhan_card.locator("button:has-text('Lưu')")
    if save_btn.count() > 0 and save_btn.first.is_visible():
        print("   💾 Bấm nút 'Lưu'...")
        save_btn.first.click()
        page.wait_for_timeout(1000)
        print(f"🎉 Gắn nhãn 'Chưa dùng mạng nào' cho '{chat_name}' thành công!")
        return "LABEL_ADDED", room_id, chat_name
    else:
        print("⚠️ Không thấy nút Lưu nhãn.")
        return "SAVE_FAILED", room_id, chat_name

def trigger_auto_shutdown(total_count):
    print("\n" + "=" * 65)
    print(f"🎉 ĐÃ HOÀN THÀNH MỤC TIÊU: {total_count}/{TARGET_COUNT} HỘI THOẠI!")
    print("=" * 65)
    if AUTO_SHUTDOWN:
        mins = SHUTDOWN_COUNTDOWN // 60
        print(f"🛑 [TỰ ĐỘNG TẮT MÁY] Máy sẽ tắt sau {mins} phút ({SHUTDOWN_COUNTDOWN}s)...")
        time.sleep(2)
        os.system(f"shutdown /s /t {SHUTDOWN_COUNTDOWN}")

def run():
    history = load_history()

    with sync_playwright() as p:
        browser, page = connect_to_portal(p)

        print("\n" + "=" * 65)
        print("🤖 TOOL TỰ ĐỘNG TRA CỨU HỢP ĐỒNG & GẮN NHÃN PORTAL SOP")
        print(f"📊 Đã xử lý trước đó: {history['total_count']} hội thoại")
        print(f"   - Đã có hợp đồng (bỏ qua): {history.get('contracts_found', 0)}")
        print(f"   - Chưa có hợp đồng (đã gắn nhãn): {history.get('labels_added', 0)}")
        print(f"🎯 Mục tiêu: {TARGET_COUNT} hội thoại ({'Tự động tắt máy' if AUTO_SHUTDOWN else 'Không tắt máy'})")
        print("=" * 65)
        print("Tùy chọn chạy:")
        print("  [Enter] : Chạy tự động liên tục toàn bộ danh sách")
        print("  [1]     : Chỉ xử lý 1 hội thoại đang mở hiện tại rồi dừng")
        print("  [s]     : Chế độ thủ công (click hội thoại bất kỳ trên web rồi bấm Enter)")
        print("  [r]     : Làm mới lịch sử đã lưu để chạy lại từ đầu")
        print("  [Số]    : Bắt đầu từ số thứ tự cụ thể (VD: 1, 10, 25...)")

        if "--auto" in sys.argv or "-y" in sys.argv:
            print("\n🚀 Tự động bắt đầu chạy sau 1 giây...")
            time.sleep(1)
            user_choice = ""
        else:
            user_choice = input("\n👉 Nhập lựa chọn của bạn (Nhấn Enter để chạy tự động): ").strip()

        if user_choice.lower() == 'r':
            confirm = input("Bạn có chắc muốn làm mới lịch sử? (y/n): ").strip().lower()
            if confirm == 'y':
                history = {"processed_ids": [], "processed_names": [], "total_count": 0, "contracts_found": 0, "labels_added": 0}
                save_history(history)
                print("🧹 Đã làm mới lịch sử.")
            user_choice = ""

        # Chế độ thủ công
        if user_choice.lower() == 's':
            print("\n>>> ĐÃ BẬT CHẾ ĐỘ THỦ CÔNG <<<")
            print("Click hội thoại bất kỳ trên web, sau đó bấm Enter để xử lý. Gõ 'q' để thoát.")
            while True:
                cmd = input("\n[Thủ công] Bấm Enter để xử lý (hoặc 'q' để thoát): ").strip().lower()
                if cmd == 'q':
                    break
                active_item = page.locator("li[class*='lists-chat-'][class*='active']")
                if active_item.count() == 0:
                    active_item = page.locator("li[class*='lists-chat-']").first
                res, r_id, name = process_single_chat(page, active_item, 0)
                if res in ["CONTRACT", "LABEL_ADDED"]:
                    mark_chat_processed(history, r_id, name, res)
            return

        # Chế độ 1 hội thoại
        if user_choice == '1':
            print("\n--- Đang xử lý đúng 1 hội thoại đang chọn ---")
            active_item = page.locator("li[class*='lists-chat-'][class*='active']")
            if active_item.count() == 0:
                active_item = page.locator("li[class*='lists-chat-']").first
            res, r_id, name = process_single_chat(page, active_item, 0)
            if res in ["CONTRACT", "LABEL_ADDED"]:
                mark_chat_processed(history, r_id, name, res)
            print("Hoàn tất!")
            return

        start_index = 0
        if user_choice.isdigit():
            start_index = max(0, int(user_choice) - 1)

        print(f"\n>>> BẮT ĐẦU CHẠY TỰ ĐỘNG TỪ HỘI THOẠI #{start_index + 1} <<<")

        curr_index = start_index
        no_more_chats_count = 0

        while True:
            try:
                if history["total_count"] >= TARGET_COUNT:
                    trigger_auto_shutdown(history["total_count"])
                    break

                chats = page.locator("li[class*='lists-chat-']")
                total = chats.count()

                if curr_index >= total:
                    print(f"\n🔄 Đang ở cuối danh sách ({total} hội thoại). Đang cuộn nạp thêm...")
                    new_total = scroll_chat_list_to_load_more(page)
                    if new_total > total:
                        chats = page.locator("li[class*='lists-chat-']")
                        total = new_total
                        no_more_chats_count = 0
                    else:
                        no_more_chats_count += 1
                        if no_more_chats_count < 5:
                            print(f"⏳ Đang đợi mạng tải thêm (Lần {no_more_chats_count}/5)...")
                            time.sleep(2)
                            continue
                        else:
                            print("🏁 Đã duyệt hết toàn bộ hội thoại hiện có trên hệ thống!")
                            break

                chat_item = chats.nth(curr_index)
                try:
                    chat_text = chat_item.inner_text()
                    chat_name = chat_text.split('\n')[0].strip()
                except Exception:
                    chat_name = f"Chat_{curr_index}"

                # Kiểm tra nếu đã xử lý trước đó
                # (để lướt qua nhanh các hội thoại đã xong nếu chạy lại)
                if is_chat_processed(history, "", chat_name):
                    print(f"⏩ [Bỏ qua] Hội thoại #{curr_index + 1}: '{chat_name}' đã được xử lý trước đó.")
                    curr_index += 1
                    continue

                res, r_id, name = process_single_chat(page, chat_item, curr_index)
                if res in ["CONTRACT", "LABEL_ADDED"]:
                    mark_chat_processed(history, r_id, name, res)

                curr_index += 1
                time.sleep(0.5)

            except KeyboardInterrupt:
                print("\n🛑 Người dùng đã dừng chương trình.")
                break
            except Exception as e:
                print(f"⚠️ Lỗi phát sinh tại hội thoại #{curr_index + 1}: {e}")
                curr_index += 1
                time.sleep(1)

        print("\n" + "=" * 65)
        print("🏁 KẾT THÚC PHIÊN LÀM VIỆC")
        print(f"📊 Tổng số hội thoại đã xử lý: {history['total_count']}")
        print(f"   - Có hợp đồng: {history.get('contracts_found', 0)}")
        print(f"   - Đã gắn nhãn 'Chưa dùng mạng nào': {history.get('labels_added', 0)}")
        print("=" * 65)

if __name__ == "__main__":
    run()
