import re
import sys
import io
import os
import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

# Đảm bảo in tiếng Việt chuẩn trên Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ==============================================================================
# CẤU HÌNH HỆ THỐNG (SETTINGS)
# ==============================================================================
CDP_URL = "http://127.0.0.1:9222"

# CHẾ ĐỘ CHẠY THỬ (DRY_RUN):
# True:  Chỉ quét danh bạ, tạo tin nhắn ngẫu nhiên và in ra màn hình xem trước (KHÔNG GỬI THẬT).
# False: GỬI THẬT vào tin nhắn Zalo của từng người.
DRY_RUN = True

# GIỚI HẠN SỐ LƯỢNG GỬI MỖI ĐỢT:
# Nên để từ 15 đến 25 người/lần để tránh bị Zalo đánh dấu bất thường.
BATCH_LIMIT = 20

# THỜI GIAN NGHỈ GIỮA 2 LẦN GỬI (GIÂY):
# Giãn cách ngẫu nhiên từ DELAY_MIN đến DELAY_MAX giây (mô phỏng người thật thao tác)
DELAY_MIN = 25
DELAY_MAX = 45

# TỰ ĐỘNG DÙNG LẠI DANH BẠ ĐÃ QUÉT (Tiết kiệm thời gian, không cần cuộn lại mỗi lần chạy):
# True:  Nếu đã có file 'danh_sach_ban_be.json' thì dùng luôn.
# False: Bắt buộc quét lại toàn bộ từ Zalo Web.
USE_CACHED_FRIENDS = True

# ĐƯỜNG DẪN CÁC FILE DỮ LIỆU
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_KHACH_HANG = os.path.join(BASE_DIR, "khach_hang.txt")
FILE_SENT_HISTORY = os.path.join(BASE_DIR, "sent_history.json")
FILE_ALL_FRIENDS = os.path.join(BASE_DIR, "danh_sach_ban_be.json")
FILE_PREVIEW = os.path.join(BASE_DIR, "preview_messages.txt")


# ==============================================================================
# BỘ SINH TIN NHẮN NGẪU NHIÊN ĐA TẦNG (COMBINATORIAL GENERATOR)
# ==============================================================================
GREETINGS = [
    "Dạ em chào anh/chị ạ",
    "Em chào anh/chị nhé",
    "Dạ em chào anh/chị",
    "Chào anh/chị ạ",
    "Dạ bên em chào anh/chị ạ",
    "Em chào anh/chị nha",
    "Chúc anh/chị một ngày làm việc vui vẻ ạ",
    "Dạ bên em kính chào anh/chị",
    "Em chào anh/chị ạ",
]

HOOKS = [
    "hôm nay bên em đang có đợt ưu đãi lắp mạng và lắp wifi",
    "hiện bên em có chương trình trợ giá chuyển mạng hoặc lắp wifi mới",
    "bên em vừa ra mắt chương trình ưu đãi lắp mạng tốc độ cao",
    "đợt này bên em có voucher gửi tặng khách đăng ký lắp wifi",
    "nhân dịp này bên em có chương trình khuyến mãi lắp mạng mới",
    "hôm nay bên em có ưu đãi riêng cho khách chuyển mạng hoặc lắp wifi",
    "hiện tại bên em đang có đợt giảm giá ưu tiên khi đăng ký lắp mạng",
    "bên em đang áp dụng chương trình trợ giá lắp wifi gia đình",
]

OFFERS = [
    "giảm trực tiếp từ 100k đến 200k ạ",
    "hỗ trợ voucher giảm ngay 100k - 200k khi lắp mạng",
    "giảm 100k - 200k khi anh/chị lắp wifi mới hoặc chuyển mạng",
    "ưu đãi chiết khấu từ 100 đến 200 ngàn vào phí hòa mạng",
    "được giảm nóng 100k - 200k tiền mặt",
    "tặng ưu đãi giảm 100k - 200k cước phí",
    "hỗ trợ mức giảm hấp dẫn từ 100k đến 200k",
]

def get_random_cta():
    """Tạo câu kêu gọi hành động tự nhiên, không lộ số điện thoại để chống Zalo quét."""
    ctas = [
        "Anh/chị quan tâm nhắn lại em tư vấn chi tiết nha.",
        "Nếu anh/chị có nhu cầu cứ nhắn lại em hỗ trợ liền nhé!",
        "Anh/chị cần thông tin chi tiết cứ nhắn lại em nha.",
        "Anh/chị cần xem qua chi tiết nhắn em gửi thông tin ạ!",
        "Nếu cần hỗ trợ anh/chị cứ phản hồi em tư vấn nhiệt tình nha.",
        "Anh/chị có nhu cầu nhắn em hỗ trợ ngay nhé!",
        "Anh/chị quan tâm thì nhắn lại em gửi ưu đãi nhé.",
        "Có gì cần tư vấn thêm anh/chị cứ nhắn lại em nhé!",
    ]
    return random.choice(ctas)

EMOJIS = ["✨", "🎁", "🌟", "🍀", "💐", "😊", "👍", "📩", "🌿", ""]

def format_sentence_casing(text):
    """Đảm bảo chữ cái đầu câu và chữ cái sau các dấu chấm (. ! ?) luôn được viết hoa chuẩn mực."""
    text = text.strip()
    if not text:
        return text

    # 1. Viết hoa ký tự đầu tiên của đoạn văn
    text = text[0].upper() + text[1:]

    # 2. Viết hoa sau các dấu ngắt câu: . hoặc ! hoặc ? kèm khoảng trắng
    def capitalize_match(match):
        punct_and_spaces = match.group(1)
        next_char = match.group(2)
        return punct_and_spaces + next_char.upper()

    pattern = r'([.!?]\s+)([a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ])'
    text = re.sub(pattern, capitalize_match, text)
    return text

def generate_random_message():
    """Tạo ra 1 tin nhắn hoàn toàn ngẫu nhiên từ tổ hợp các vế mà không bị lặp từ và chuẩn viết hoa."""
    g = random.choice(GREETINGS).strip()
    h = random.choice(HOOKS).strip()
    o = random.choice(OFFERS).strip()
    c = get_random_cta().strip()
    e = random.choice(EMOJIS).strip()
    
    # 4 cấu trúc câu tự nhiên, lịch sự
    templates = [
        f"{g}! {h.capitalize()}, {o}. {c}",
        f"{g}, {h}, {o}. {c}",
        f"{g}! Đợt này bên em có chính sách {o}. {c}",
        f"{g}. {h.capitalize()}, được {o}. {c}",
    ]
    selected = random.choice(templates)
    
    # Chuẩn hóa viết hoa đầu câu và sau dấu ngắt câu
    selected = format_sentence_casing(selected)
    
    if e:
        selected = f"{selected} {e}"
    return selected


# ==============================================================================
# HÀM XỬ LÝ DANH SÁCH KHÁCH HÀNG & LỊCH SỬ GỬI
# ==============================================================================
def load_khach_hang_list():
    """Đọc danh sách từ khóa/tên khách hàng cần bỏ qua."""
    if not os.path.exists(FILE_KHACH_HANG):
        with open(FILE_KHACH_HANG, "w", encoding="utf-8") as f:
            f.write("# Danh sách tên hoặc từ khóa Zalo khách hàng cần BỎ QUA\n")
        return []

    excludes = []
    with open(FILE_KHACH_HANG, "r", encoding="utf-8") as f:
        for line in f:
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("#"):
                excludes.append(cleaned.lower())
    return excludes

def is_khach_hang(name, excludes):
    """Kiểm tra tên bạn bè có trùng hoặc chứa từ khóa khách hàng không."""
    name_lower = name.lower()
    for ex in excludes:
        if ex in name_lower:
            return True, ex
    return False, None

def load_sent_history():
    """Đọc lịch sử những người đã được gửi tin."""
    if not os.path.exists(FILE_SENT_HISTORY):
        return {}
    try:
        with open(FILE_SENT_HISTORY, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_sent_history(name, message):
    """Lưu lịch sử gửi thành công."""
    history = load_sent_history()
    history[name] = {
        "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    }
    with open(FILE_SENT_HISTORY, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ==============================================================================
# CRAWLER: QUÉT TOÀN BỘ DANH SÁCH BẠN BÈ TỪ ZALO WEB
# ==============================================================================
def scan_all_friends(page, use_cache=True):
    """Duyệt danh bạ bạn bè hoặc nạp từ file cache nếu có."""
    if use_cache and os.path.exists(FILE_ALL_FRIENDS):
        try:
            with open(FILE_ALL_FRIENDS, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if cached and len(cached) > 0:
                    print(f"📦 Đã nạp {len(cached)} bạn bè từ bộ nhớ cache ({FILE_ALL_FRIENDS})")
                    return cached
        except Exception:
            pass

    print("\n🔍 Đang mở Danh bạ -> Danh sách bạn bè trên Zalo Web...")
    
    # 1. Bấm vào icon Danh bạ trên thanh menu trái
    contact_tab_btn = page.query_selector('div[title="Danh bạ"], div.leftbar-tab:has(.lb-tab-title:has-text("Danh bạ"))')
    if contact_tab_btn:
        contact_tab_btn.click()
        time.sleep(0.5)
        
    # 2. Bấm vào sub-menu "Danh sách bạn bè"
    ds_bb = page.query_selector('.menu-item:has-text("Danh sách bạn bè")')
    if ds_bb:
        ds_bb.click()
        time.sleep(0.8)

    # 3. Cuộn lên đầu trang trước
    page.mouse.move(700, 350)
    time.sleep(0.2)
    for _ in range(12):
        page.mouse.wheel(0, -1000)
        time.sleep(0.08)
    time.sleep(0.5)

    print("📜 Đang cuộn quét danh sách bạn bè...")
    all_friends = []
    seen = set()
    no_new_count = 0

    for step in range(40):
        current_names = page.evaluate("""() => {
            const items = document.querySelectorAll('.contact-item-v2-wrapper .name');
            return Array.from(items).map(el => el.innerText.trim()).filter(Boolean);
        }""")

        new_found = 0
        for name in current_names:
            if name not in seen:
                seen.add(name)
                all_friends.append(name)
                new_found += 1

        if new_found == 0:
            no_new_count += 1
            if no_new_count >= 5:
                break
        else:
            no_new_count = 0

        # Cuộn chuột xuống
        page.mouse.wheel(0, 550)
        time.sleep(0.35)

    print(f"✅ Đã quét thành công tổng cộng: {len(all_friends)} bạn bè.")
    with open(FILE_ALL_FRIENDS, "w", encoding="utf-8") as f:
        json.dump(all_friends, f, ensure_ascii=False, indent=2)

    return all_friends


# ==============================================================================
# HÀM KIỂM TRA CẢNH BÁO BẢO VỆ TÀI KHOẢN (ANTI-BAN DETECTOR)
# ==============================================================================
def check_zalo_warning(page):
    """Phát hiện popup cảnh báo thao tác nhanh hoặc Captcha của Zalo."""
    return page.evaluate("""() => {
        const modals = Array.from(document.querySelectorAll('.zl-modal, .popover-v2, [class*="modal"], [class*="dialog"]'));
        for (const m of modals) {
            const t = (m.innerText || '').toLowerCase();
            if (t.includes('thao tác quá nhanh') || t.includes('tạm thời bị khóa') || t.includes('xác thực') || t.includes('captcha') || t.includes('báo xấu')) {
                return m.innerText.replace(/\\n+/g, ' ');
            }
        }
        return null;
    }""")


# ==============================================================================
# HÀM GỬI TIN NHẮN TỚI 1 BẠN BÈ
# ==============================================================================
def send_message_to_friend(page, friend_name, message, dry_run=True):
    """Tìm bạn bè qua thanh tìm kiếm, mở khung chat và gửi tin nhắn."""
    print(f"\n👤 Đang xử lý: [{friend_name}]")

    # Kiểm tra cảnh báo bất thường trước khi thực hiện
    alert = check_zalo_warning(page)
    if alert:
        print(f"🚨 CẢNH BÁO TỪ ZALO PHÁT HIỆN: {alert}")
        print("🛑 DỪNG TỰ ĐỘNG ĐỂ BẢO VỆ TÀI KHOẢN!")
        return "STOP"

    # 1. Tìm qua thanh tìm kiếm
    search_input = page.query_selector('#contact-search-input')
    if not search_input:
        print("❌ Không tìm thấy ô tìm kiếm (#contact-search-input)!")
        return False

    search_input.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    time.sleep(0.2)
    
    # Gõ tên bạn bè vào ô tìm kiếm
    page.keyboard.type(friend_name, delay=25)
    time.sleep(1.2)

    # 2. Tìm kết quả trong danh sách kết quả tìm kiếm
    first_res = page.query_selector('.conv-item')
    if not first_res:
        print(f"⚠️ Không tìm thấy hội thoại cho [{friend_name}]. Bỏ qua.")
        search_input.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        return False

    first_res.click()
    time.sleep(1.2)

    # Xóa nội dung tìm kiếm
    search_input.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    time.sleep(0.4)

    # 3. Kiểm tra ô nhập tin nhắn #richInput
    chat_input = page.query_selector('#richInput')
    if not chat_input:
        print(f"⚠️ Không mở được ô nhập tin nhắn với [{friend_name}] (có thể là tài khoản hệ thống hoặc bị chặn).")
        return False

    print(f"💬 Nội dung tin nhắn:")
    print(f"   \"{message}\"")

    if dry_run:
        print("🔎 [DRY-RUN] Chế độ xem trước: KHÔNG gửi thật.")
        return True

    # 4. GỬI THẬT: Focus vào ô nhập liệu và chèn tin nhắn chính xác
    chat_input.click()
    time.sleep(0.3)
    
    # Dùng insert_text để gửi tiếng Việt có dấu chuẩn 100%, không bị lỗi bộ gõ IME
    page.keyboard.insert_text(message)
    time.sleep(0.8)

    # Bấm Enter để gửi
    page.keyboard.press("Enter")
    time.sleep(1.2)

    # Kiểm tra xem tin nhắn đã bay đi chưa (khung nhập đã trống)
    current_val = page.evaluate("() => document.querySelector('#richInput')?.innerText?.trim() || ''")
    if current_val:
        # Nếu chưa bay đi, thử bấm nút gửi chính thức
        send_btn = page.query_selector('[data-id="btn_Chat_Send"], .fa-send, [title*="Gửi"]')
        if send_btn:
            send_btn.click()
            time.sleep(1.0)

    # Kiểm tra lại xem có popup cảnh báo spam sau khi bấm gửi không
    alert_after = check_zalo_warning(page)
    if alert_after:
        print(f"🚨 CẢNH BÁO TỪ ZALO SAU KHI GỬI: {alert_after}")
        print("🛑 DỪNG TỰ ĐỘNG ĐỂ BẢO VỆ TÀI KHOẢN!")
        return "STOP"

    print(f"🚀 [ĐÃ GỬI THÀNH CÔNG] tới [{friend_name}]!")
    save_sent_history(friend_name, message)
    return True


# ==============================================================================
# HÀM CHÍNH (MAIN ORCHESTRATOR)
# ==============================================================================
def main():
    print("=" * 65)
    print("🤖 ZALO REMIND AUTO-SENDER (PLAYWRIGHT CDP 9222)")
    print(f"⚙️  Chế độ: {'[DRY_RUN - XEM TRƯỚC / KHÔNG GỬI]' if DRY_RUN else '[THỰC THI - GỬI TIN THẬT]'}")
    print(f"🎯 Giới hạn lượt này: tối đa {BATCH_LIMIT} người")
    print(f"⏱️  Độ trễ giãn cách: {DELAY_MIN} - {DELAY_MAX} giây/người")
    print("=" * 65)

    # 1. Đọc danh sách loại trừ & lịch sử
    khach_hang_excludes = load_khach_hang_list()
    sent_history = load_sent_history()
    print(f"📋 Số từ khóa/tên Khách hàng cần bỏ qua: {len(khach_hang_excludes)}")
    print(f"📜 Số người đã được gửi trong lịch sử: {len(sent_history)}")

    # 2. Kết nối tới Chrome
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"\n❌ Không thể kết nối tới Chrome cổng {CDP_URL}!")
            print("👉 Vui lòng đảm bảo Chrome đã được bật sẵn cờ: --remote-debugging-port=9222")
            print(f"Chi tiết lỗi: {e}")
            return

        pages = browser.contexts[0].pages
        zalo_page = next((pg for pg in pages if "chat.zalo.me" in pg.url), None)
        if not zalo_page:
            print("❌ Không tìm thấy tab Zalo Web (chat.zalo.me) trong Chrome!")
            return

        print(f"🌐 Đã kết nối Zalo tab: {zalo_page.title()}")

        # 3. Lấy danh sách bạn bè
        friends_list = scan_all_friends(zalo_page)
        if not friends_list:
            print("❌ Không lấy được danh sách bạn bè nào!")
            return

        # 4. Lọc và chuẩn bị danh sách gửi
        eligible_queue = []
        skipped_customers = []
        skipped_already_sent = []

        for name in friends_list:
            is_kh, kw = is_khach_hang(name, khach_hang_excludes)
            if is_kh:
                skipped_customers.append((name, kw))
                continue
            if name in sent_history:
                skipped_already_sent.append(name)
                continue
            eligible_queue.append(name)

        print("\n" + "=" * 65)
        print("📊 THỐNG KÊ DANH SÁCH:")
        print(f" • Tổng số bạn bè: {len(friends_list)}")
        print(f" • Bỏ qua (Đã là Khách hàng trong khach_hang.txt): {len(skipped_customers)}")
        print(f" • Bỏ qua (Đã gửi trước đó trong sent_history.json): {len(skipped_already_sent)}")
        print(f" • Sẵn sàng để gửi tin nhắn: {len(eligible_queue)}")
        print("=" * 65)

        if skipped_customers:
            print(f"💡 Một số khách hàng được phát hiện và bỏ qua:")
            for name, kw in skipped_customers[:5]:
                print(f"   [BỎ QUA] {name} (khớp từ khóa: '{kw}')")

        # 5. Giới hạn số lượng gửi lượt này
        targets_for_this_batch = eligible_queue[:BATCH_LIMIT]
        print(f"\n🚀 Sẽ xử lý {len(targets_for_this_batch)} người trong lượt chạy này...")

        if DRY_RUN:
            # Ghi file preview_messages.txt để user kiểm tra thoải mái
            with open(FILE_PREVIEW, "w", encoding="utf-8") as pf:
                pf.write(f"=== DANH SÁCH XEM TRƯỚC TIN NHẮN TẠO NGẪU NHIÊN ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n\n")
                for idx, friend in enumerate(targets_for_this_batch, 1):
                    msg = generate_random_message()
                    pf.write(f"[{idx}/{len(targets_for_this_batch)}] Gửi tới: {friend}\n")
                    pf.write(f"Nội dung: {msg}\n")
                    pf.write("-" * 50 + "\n")

            print(f"\n📄 Đã xuất bản xem trước tin nhắn vào: {FILE_PREVIEW}")

        # 6. Bắt đầu vòng lặp gửi tin
        sent_count = 0
        for idx, friend in enumerate(targets_for_this_batch, 1):
            msg = generate_random_message()
            print(f"\n[{idx}/{len(targets_for_this_batch)}] ------------------------------")
            success = send_message_to_friend(zalo_page, friend, msg, dry_run=DRY_RUN)
            
            if success:
                sent_count += 1

            # Giãn cách an toàn giữa các tin nhắn
            if idx < len(targets_for_this_batch):
                if not DRY_RUN:
                    wait_time = random.uniform(DELAY_MIN, DELAY_MAX)
                    print(f"⏳ Nghỉ an toàn {wait_time:.1f} giây trước khi gửi người tiếp theo...")
                    time.sleep(wait_time)
                else:
                    time.sleep(0.5)

        print("\n" + "=" * 65)
        print(f"🎉 HOÀN THÀNH LƯỢT CHẠY! Đã xử lý: {sent_count}/{len(targets_for_this_batch)}")
        if DRY_RUN:
            print("👉 Bạn vừa chạy ở chế độ DRY_RUN (Xem trước).")
            print("👉 Hãy mở file 'preview_messages.txt' và 'khach_hang.txt' để kiểm tra.")
            print("👉 Khi bạn đã ưng ý, đổi `DRY_RUN = False` trong file 'zalo_sender.py' để gửi thật!")
        print("=" * 65)

if __name__ == "__main__":
    main()
