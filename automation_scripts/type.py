import sys
import random
import time
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ==================== CẤU HÌNH (CONFIGURATION) ====================
# Từ khóa mặc định để tìm tab trình duyệt phù hợp. Nếu không tìm thấy, hệ thống
# sẽ tự động lấy tab hiện đang hoạt động trên màn hình của bạn.
TARGET_TAB_KEYWORD = "fptlapmang" 

# Trang đích mặc định. URL này sẽ được ghi đè động dựa theo trang Web mà bạn đang mở trong Chrome.
TARGET_URL = "https://fptlapmang.id.vn/"

# Cổng debug CDP của Chrome (cần khởi chạy Chrome trước với cờ --remote-debugging-port=9222)
CDP_URL = "http://127.0.0.1:9222"

# Thời gian chờ mặc định (mili-giây)
TIMEOUT = 10000 

# Các khoảng trễ để thao tác tự nhiên và tối ưu tốc độ cao (giây)
DELAY_FILL = 0.1
DELAY_IN_BETWEEN = 0.2

# Tự động đóng tab cũ và mở tab mới sau mỗi N hội thoại để giải phóng 100% RAM và chống chậm
RECYCLE_TAB_EVERY = 50

# Mục tiêu số lượng hội thoại cần tạo (đạt mốc này sẽ tự động hoàn thành và dừng script)
TARGET_GOAL = 180
for _i, _arg in enumerate(sys.argv):
    if _arg == "--target" and _i + 1 < len(sys.argv) and sys.argv[_i + 1].isdigit():
        TARGET_GOAL = int(sys.argv[_i + 1])
# ==================================================================

# --- KHỞI TẠO NGUỒN DỮ LIỆU TIẾNG VIỆT NGẪU NHIÊN ---
HỌ_LIST = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
TÊN_ĐỆM_LIST = ["Văn", "Thị", "Minh", "Anh", "Đức", "Duy", "Ngọc", "Bảo", "Hữu", "Khánh", "Thanh", "Mỹ", "Quốc", "Tấn"]
TÊN_LIST = ["Anh", "Bình", "Cường", "Dũng", "Đạt", "Giang", "Hải", "Hùng", "Huy", "Linh", "Nam", "Phong", "Quân", "Sơn", "Tuấn", "Vy", "Phương", "Thảo", "Hương", "Trang", "Yến", "Tú", "Khải", "Tâm"]

SĐT_ĐẦU_SỐ = ["090", "091", "098", "097", "096", "035", "036", "037", "038", "077", "078", "079", "086", "088", "089", "056", "058"]

# Bản đồ địa chỉ phân cấp chuẩn xác theo tỉnh/thành -> quận/huyện -> tên đường phù hợp thực tế
ADDRESS_TEMPLATES = {
    "Hồ Chí Minh": {
        "districts": [
            {
                "name": "Quận 1",
                "streets": ["Lê Lợi", "Nguyễn Huệ", "Đồng Khởi", "Hai Bà Trưng", "Lê Thánh Tôn", "Lý Tự Trọng"]
            },
            {
                "name": "Quận 3",
                "streets": ["Cách Mạng Tháng Tám", "Nguyễn Đình Chiểu", "Điện Biên Phủ", "Lê Quý Đôn", "Nam Kỳ Khởi Nghĩa"]
            },
            {
                "name": "Quận 10",
                "streets": ["Ba Tháng Hai", "Tô Hiến Thành", "Sư Vạn Hạnh", "Cách Mạng Tháng Tám", "Lý Thường Kiệt"]
            },
            {
                "name": "Quận Bình Thạnh",
                "streets": ["Bạch Đằng", "Điện Biên Phủ", "Xô Viết Nghệ Tĩnh", "Phan Đăng Lưu", "Lê Quang Định"]
            },
            {
                "name": "Quận Gò Vấp",
                "streets": ["Quang Trung", "Nguyễn Oanh", "Phan Văn Trị", "Lê Đức Thọ", "Thống Nhất"]
            },
            {
                "name": "Huyện Hóc Môn",
                "streets": ["Lý Thường Kiệt", "Song Hành", "Tô Ký", "Đặng Thúc Vịnh", "Bùi Công Trừng"]
            },
            {
                "name": "Huyện Bình Chánh",
                "streets": ["Quốc Lộ 1A", "Nguyễn Văn Linh", "Đinh Đức Thiện", "Phạm Hùng", "Trần Đại Nghĩa"]
            }
        ]
    },
    "Hà Nội": {
        "districts": [
            {
                "name": "Quận Hoàn Kiếm",
                "streets": ["Đinh Tiên Hoàng", "Tràng Tiền", "Lý Thái Tổ", "Hàng Bạc", "Hàng Gai", "Hàng Đào"]
            },
            {
                "name": "Quận Đống Đa",
                "streets": ["Nguyễn Lương Bằng", "Xã Đàn", "Chùa Bộc", "Tây Sơn", "Tôn Đức Thắng", "Đê La Thành"]
            },
            {
                "name": "Quận Cầu Giấy",
                "streets": ["Xuân Thủy", "Cầu Giấy", "Duy Tân", "Trần Thái Tông", "Nguyễn Phong Sắc"]
            },
            {
                "name": "Quận Tây Hồ",
                "streets": ["Lạc Long Quân", "Thụy Khuê", "Yên Phụ", "Hoàng Hoa Thám", "Xuân La"]
            },
            {
                "name": "Quận Ba Đình",
                "streets": ["Kim Mã", "Đội Cấn", "Giảng Võ", "Liễu Giai", "Hoàng Diệu"]
            }
        ]
    },
    "Đà Nẵng": {
        "districts": [
            {
                "name": "Quận Hải Châu",
                "streets": ["Bạch Đằng", "Trần Phú", "Trần Hưng Đạo", "Nguyễn Văn Linh", "Lê Duẩn"]
            },
            {
                "name": "Quận Thanh Khê",
                "streets": ["Điện Biên Phủ", "Hùng Vương", "Trần Cao Vân", "Nguyễn Tất Thành"]
            },
            {
                "name": "Quận Sơn Trà",
                "streets": ["Võ Nguyên Giáp", "Phạm Văn Đồng", "Ngô Quyền", "Lê Đức Thọ"]
            }
        ]
    },
    "Cần Thơ": {
        "districts": [
            {
                "name": "Quận Ninh Kiều",
                "streets": ["Đại Lộ Hòa Bình", "Hai Bà Trưng", "30 Tháng 4", "Mậu Thân", "Nguyễn Việt Hồng"]
            },
            {
                "name": "Quận Cái Răng",
                "streets": ["Võ Nguyên Giáp", "Phạm Hùng", "Lý Thái Tổ", "Trần Hưng Đạo"]
            }
        ]
    },
    "Bình Dương": {
        "districts": [
            {
                "name": "Thành phố Thủ Dầu Một",
                "streets": ["Đại Lộ Bình Dương", "Yersin", "Chùa Hội Khánh", "Phú Lợi", "Lê Hồng Phong"]
            },
            {
                "name": "Thành phố Thuận An",
                "streets": ["Cách Mạng Tháng Tám", "DT743", "Nguyễn Trãi", "Phan Đình Phùng"]
            }
        ]
    },
    "Đồng Nai": {
        "districts": [
            {
                "name": "Thành phố Biên Hòa",
                "streets": ["Phạm Văn Thuận", "Nguyễn Ái Quốc", "Võ Thị Sáu", "Đồng Khởi", "Bùi Văn Hòa"]
            }
        ]
    },
    "Long An": {
        "districts": [
            {
                "name": "Thành phố Tân An",
                "streets": ["Hùng Vương", "Quốc Lộ 1A", "Trần Phong Sắc", "Nguyễn Huệ", "Châu Thị Kim"]
            }
        ]
    }
}

def generate_random_data():
    ho = random.choice(HỌ_LIST)
    dem = random.choice(TÊN_ĐỆM_LIST)
    ten = random.choice(TÊN_LIST)
    ho_va_ten = f"{ho} {dem} {ten}"
    
    sdt = random.choice(SĐT_ĐẦU_SỐ) + "".join(random.choices("0123456789", k=7))
    
    # Lấy ngẫu nhiên một tỉnh từ bản đồ
    tinh = random.choice(list(ADDRESS_TEMPLATES.keys()))
    # Lấy ngẫu nhiên một quận/huyện thuộc tỉnh đó
    quan_huyen_list = ADDRESS_TEMPLATES[tinh]["districts"]
    quan_huyen_data = random.choice(quan_huyen_list)
    quan_huyen = quan_huyen_data["name"]
    # Lấy ngẫu nhiên một tuyến đường thuộc quận/huyện đó
    duong = random.choice(quan_huyen_data["streets"])
    so_nha = random.randint(1, 350)
    
    dia_chi = f"{so_nha} Đường {duong}, {quan_huyen}, {tinh}"
    return ho_va_ten, sdt, dia_chi

# --- HÀM TÌM PHẦN TỬ TRONG TRANG CHÍNH & TẤT CẢ IFRAMES ---
def find_element(page, selectors_list, timeout=1000):
    """
    Tìm phần tử dựa trên một danh sách các CSS selector có thể trùng khớp.
    Tự động duyệt qua cả trang chính và các frame/iframe bên trong.
    """
    for selector in selectors_list:
        try:
            loc = page.locator(selector).first
            if loc.is_visible(timeout=timeout):
                return loc
        except Exception:
            pass
        
        for frame in page.frames:
            try:
                loc = frame.locator(selector).first
                if loc.is_visible(timeout=timeout):
                    return loc
            except Exception:
                continue
                
    return None

def click_element_by_text(page, tagName, text, timeout=2000):
    """
    Tìm và click một phần tử theo Tên thẻ (tag name) và chứa đoạn văn bản (text).
    Tự động hỗ trợ cả trang chính lẫn iframes.
    """
    xpath_selector = f"//{tagName}[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
    
    try:
        loc = page.locator(xpath_selector).first
        if loc.is_visible(timeout=timeout):
            loc.click()
            return True
    except Exception:
        pass
        
    for frame in page.frames:
        try:
            loc = frame.locator(xpath_selector).first
            if loc.is_visible(timeout=timeout):
                loc.click()
                return True
        except Exception:
            continue
    return False

def get_dialogue_frame(page):
    """
    Lấy iframe chứa giao diện hội thoại và form đăng ký.
    Hỗ trợ linh hoạt cả #livechat-sop lẫn #sop-livechat-wrapper và các iframe động.
    """
    candidates = [
        "#livechat-sop > iframe:not([width='88px'])",
        "#sop-livechat-wrapper iframe",
        "#livechat-sop iframe",
        "iframe:not([width='88px'])",
    ]
    for sel in candidates:
        try:
            f = page.frame_locator(sel).first
            if f.locator("input, .anticon-more, button").first.is_visible(timeout=200):
                return f
        except Exception:
            continue
    return page.frame_locator("#livechat-sop > iframe, #sop-livechat-wrapper iframe").first

def open_chat_widget(page):
    """
    Kích hoạt và mở widget chat bằng nhiều chiến lược phối hợp:
    1. Kiểm tra nếu form hoặc hội thoại đã mở -> trả về ngay.
    2. Click trực tiếp qua evaluate vào nút chat bên trong document của iframe 88px.
    3. Click vật lý bằng tọa độ chuột vào tâm bong bóng chat.
    4. Thử lại liên tục mỗi 300ms cho đến khi form mở, không bao giờ bỏ qua khi widget đã hiện.
    """
    start = time.time()
    while time.time() - start < 8.0:
        # Kiểm tra xem biểu mẫu đã xuất hiện chưa
        for f_sel in ["#livechat-sop > iframe:not([width='88px'])", "#sop-livechat-wrapper iframe", "iframe:not([width='88px'])"]:
            try:
                frame = page.frame_locator(f_sel).first
                if frame.locator("input").first.is_visible(timeout=100) or frame.locator(".anticon-more").first.is_visible(timeout=100):
                    return True
            except Exception:
                pass

        # Tìm kiếm launcher
        launcher_loc = page.locator("#livechat-sop [class*='live-chat-wrapper'], #livechat-sop iframe[width='88px'], iframe[width='88px'], iframe[height='88px']").first
        if launcher_loc.is_visible(timeout=150):
            # A. Click trực tiếp vào phần tử bên trong iframe launcher qua JavaScript
            try:
                page.evaluate("""() => {
                    const ifr = document.querySelector("#livechat-sop iframe[width='88px'], iframe[width='88px']");
                    if (ifr && ifr.contentDocument) {
                        const target = ifr.contentDocument.querySelector("[class*='chat-box'], [class*='show-button'], [class*='glow'], svg, .frame-content div");
                        if (target) {
                            target.click();
                            target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        }
                    }
                }""")
            except Exception:
                pass
            
            # B. Click vật lý bằng tọa độ chuột vào tâm bong bóng chat (x: ~52px, y: ~664px)
            try:
                box = launcher_loc.bounding_box()
                if box:
                    cx = box['x'] + (box['width'] / 2 if box['width'] <= 88 else 44)
                    cy = box['y'] + (75 if box['height'] > 100 else box['height'] / 2)
                    page.mouse.click(cx, cy)
            except Exception:
                pass
        else:
            # Cuộn nhẹ kích hoạt nếu widget chưa kịp tải
            try:
                page.mouse.wheel(0, 200)
            except Exception:
                pass

        time.sleep(0.3)

    return False

def navigate_fresh(context, page, url):
    """
    Xóa cookies, local storage và session storage, sau đó tải lại trang
    với wait_until='domcontentloaded' để tăng tốc độ gấp 3-4 lần so với networkidle.
    """
    try:
        context.clear_cookies()
    except Exception:
        pass
        
    try:
        # Xóa storage ngay trên trang trước khi tải lại
        page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e){} }")
        try:
            element_handle = page.locator('#sop-livechat-wrapper iframe').element_handle(timeout=300)
            if element_handle:
                frame = element_handle.content_frame()
                if frame:
                    frame.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e){} }")
        except Exception:
            pass
            
        # Tải trang nhanh 1 lần duy nhất
        page.goto(url, wait_until="domcontentloaded", timeout=12000)
    except Exception as load_err:
        try:
            page.reload(wait_until="domcontentloaded", timeout=12000)
        except Exception:
            pass

def close_active_dialogue(dialogue_frame, three_dots):
    """
    Tự động nhấp ba chấm -> Kết thúc hội thoại -> Đóng cuộc trò chuyện.
    Sử dụng auto-wait thay cho time.sleep cứng để thao tác đóng diễn ra trong tích tắc.
    """
    try:
        if three_dots.is_visible(timeout=1500):
            three_dots.click()
            
            # Chọn mục Kết thúc hội thoại (NFC/NFD)
            end_chat = dialogue_frame.locator("[class*='popover'] p, [class*='popover'] div, p:has-text('Kết thúc'), p:has-text('Kết thúc'), span:has-text('Kết thúc'), span:has-text('Kết thúc')").first
            end_chat.wait_for(state="visible", timeout=3000)
            end_chat.click()
            
            # Chọn nút Đóng (NFC/NFD)
            close_btn = dialogue_frame.locator("button:has-text('Đóng'), button:has-text('Đóng'), .ant-modal-confirm-btns button:last-child, .ant-btn-primary, button[class*='primary']").first
            close_btn.wait_for(state="visible", timeout=3000)
            close_btn.click()
            time.sleep(0.3)
            return True
    except Exception as err:
        print(f"   (Lỗi khi thực hiện đóng hội thoại: {err})")
    return False

# --- QUY TRÌNH CHẠY CHÍNH ---
def run():
    global TARGET_URL
    with sync_playwright() as p:
        print(f"Đang kết nối tới trình duyệt tại {CDP_URL}...")
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"KHÔNG THỂ KẾT NỐI TRÌNH DUYỆT! Hãy chắc chắn bạn đã mở Chrome với cổng debug 9222.")
            print(f"Chi tiết lỗi: {e}")
            return
            
        context = browser.contexts[0]
        
        # 1. Tìm tab trình duyệt hoạt động
        page = None
        if TARGET_TAB_KEYWORD:
            page = next((tab for tab in context.pages if TARGET_TAB_KEYWORD.lower() in tab.url.lower() or TARGET_TAB_KEYWORD.lower() in tab.title().lower()), None)
        
        # Nếu không tìm thấy bằng keyword, tự động nhận diện tab đang mở URL bất kỳ không phải trang trắng
        if page is None:
            page = next((tab for tab in context.pages if tab.url.startswith("http")), None)
            
        if page is None and context.pages:
            page = context.pages[0]

        if page is None:
            print("Không tìm thấy bất kỳ tab trình duyệt nào đang mở! Hãy mở Chrome trước.")
            return
            
        # Ghi đè TARGET_URL hoạt động động theo tab hiện tại để tương thích mọi máy
        current_url = page.url
        if current_url.startswith("http"):
            TARGET_URL = current_url
            print(f"-> Nhận diện URL mục tiêu từ trình duyệt: {TARGET_URL}")
            
        # Tự động từ chối (Block) quyền Geolocation qua CDP
        try:
            cdp_client = context.new_cdp_session(page)
            cdp_client.send("Browser.setPermission", {
                "permission": {
                    "name": "geolocation"
                },
                "setting": "denied",
                "origin": TARGET_URL
            })
            print("-> Đã tự động TỪ CHỐI (Block) quyền Location qua CDP để tắt popup hỏi của trình duyệt.")
        except Exception as perm_err:
            print(f"-> Không thể tự động từ chối quyền location qua CDP: {perm_err}")
            
        # Làm sạch session ban đầu và tải trang
        navigate_fresh(context, page, TARGET_URL)
            
        print(f"Đã kết nối thành công tới tab: '{page.title()}' ({page.url})")
        if "--auto" in sys.argv or "-y" in sys.argv:
            print("🚀 [CHẾ ĐỘ TỰ ĐỘNG TREO MÁY] Tự động bắt đầu tạo hội thoại sau 1 giây...")
            time.sleep(1)
        else:
            input("Nhấn ENTER trong Terminal này để BẮT ĐẦU chạy tự động...")
        
        loop_count = 0
        success_count = 0
        start_time = time.time()
        
        while success_count < TARGET_GOAL:
            loop_count += 1
            elapsed = time.time() - start_time
            avg_speed = (elapsed / success_count) if success_count > 0 else 0
            remaining_chats = TARGET_GOAL - success_count
            eta_seconds = remaining_chats * avg_speed if success_count > 0 else 0
            eta_str = f"{int(eta_seconds // 3600)}h {int((eta_seconds % 3600) // 60)}m" if success_count > 0 else "Đang tính..."
            
            print(f"\n===== [VÒNG {loop_count} | TIẾN ĐỘ: {success_count}/{TARGET_GOAL}] =====")
            if success_count > 0:
                print(f"⏱️ Tốc độ TB: {avg_speed:.1f}s/cuộc | Dự kiến hoàn thành sau: {eta_str}")
            
            # Tạo dữ liệu ngẫu nhiên
            name, phone, address = generate_random_data()
            print(f"-> Dữ liệu: {name} | {phone} | {address}")
            
            try:
                dialogue_frame = get_dialogue_frame(page)
                three_dots = dialogue_frame.locator(".anticon-more, [aria-label='more'], button:has(.anticon-more)").first
                name_field = dialogue_frame.locator("input[placeholder*='tên'], input[placeholder*='Tên'], input[placeholder*='name']").first
                
                # 1. Kiểm tra nhanh: CHỈ đóng nếu là hội thoại cũ (đã kết nối chat, không có ô nhập tên)
                if not name_field.is_visible(timeout=200) and three_dots.is_visible(timeout=300):
                    print("-> Phát hiện hội thoại cũ đang mở. Đóng ngay...")
                    close_active_dialogue(dialogue_frame, three_dots)
                    navigate_fresh(context, page, TARGET_URL)
                    continue
                
                # 2. Mở widget chat siêu ổn định (click liên tục cả JS lẫn tọa độ chuột tới khi mở)
                opened = open_chat_widget(page)
                if not opened:
                    raise Exception("Không thể mở widget chat sau 8 giây thử lại.")
                
                # Lấy lại dialogue frame chính xác khi đã mở
                dialogue_frame = get_dialogue_frame(page)
                three_dots = dialogue_frame.locator(".anticon-more, [aria-label='more'], button:has(.anticon-more)").first
                name_field = dialogue_frame.locator("input[placeholder*='tên'], input[placeholder*='Tên'], input[placeholder*='name'], input").first
                
                # Nếu vô tình vào thẳng màn hình chat cũ (không có form nhập tên mà có nút 3 chấm)
                if not name_field.is_visible(timeout=300) and three_dots.is_visible(timeout=500):
                    print("-> Vào thẳng hội thoại cũ, tiến hành đóng...")
                    close_active_dialogue(dialogue_frame, three_dots)
                    navigate_fresh(context, page, TARGET_URL)
                    continue
                
                # Đợi ô nhập họ tên sẵn sàng
                name_field.wait_for(state="visible", timeout=4000)
                
                # 3. Điền thông tin nhanh
                name_field = dialogue_frame.locator("input[placeholder*='tên'], input[placeholder*='Tên'], input[placeholder*='name']").first
                if not name_field.is_visible(timeout=200):
                    name_field = dialogue_frame.locator("input").nth(0)
                name_field.fill(name)
                time.sleep(DELAY_FILL)
                
                phone_field = dialogue_frame.locator("input[placeholder*='thoại'], input[placeholder*='phone']").first
                if not phone_field.is_visible(timeout=200):
                    phone_field = dialogue_frame.locator("input").nth(1)
                phone_field.fill(phone)
                time.sleep(DELAY_FILL)
                
                address_field = dialogue_frame.locator("input[placeholder*='chỉ'], input[placeholder*='address']").first
                if not address_field.is_visible(timeout=200):
                    address_field = dialogue_frame.locator("input").nth(2)
                address_field.fill(address)
                time.sleep(DELAY_FILL)
                
                # 4. Click Bắt đầu
                submit_btn = dialogue_frame.locator(
                    "button:has-text('Bắt đầu'), button:has-text('Bắt đầu'), " 
                    "button:has-text('Bắt đầu chat'), button:has-text('Gửi'), "
                    "button:has-text('Đăng ký'), button:has-text('Start'), "
                    "button:has-text('Submit'), [type='submit'], .ant-btn-primary"
                ).first
                
                if not submit_btn.is_visible(timeout=300):
                    submit_btn = dialogue_frame.get_by_text("Bắt đầu").first
                
                submit_btn.click(timeout=4000)
                
                # 5. Chờ hội thoại kết nối thành công (form đăng ký gửi đi và ẩn)
                try:
                    name_field.wait_for(state="hidden", timeout=10000)
                except Exception:
                    time.sleep(1.0)
                success_count += 1
                print(f"-> [THÀNH CÔNG] Đã kích hoạt hội thoại #{success_count}!")
                
                # 6. Đóng hội thoại ngay
                close_active_dialogue(dialogue_frame, three_dots)
                
                # 7. Kiểm tra làm mới tab định kỳ (mỗi 50 hội thoại) để giải phóng triệt để RAM
                if success_count > 0 and success_count % RECYCLE_TAB_EVERY == 0:
                    print(f"\n🔄 Đạt mốc {success_count} hội thoại! Đang tái tạo tab mới để giải phóng 100% RAM...")
                    try:
                        old_page = page
                        page = context.new_page()
                        try:
                            old_page.close()
                        except Exception:
                            pass
                        try:
                            cdp = context.new_cdp_session(page)
                            cdp.send("Browser.setPermission", {
                                "permission": {"name": "geolocation"},
                                "setting": "denied",
                                "origin": TARGET_URL
                            })
                        except Exception:
                            pass
                        navigate_fresh(context, page, TARGET_URL)
                        print("-> Đã mở tab mới tinh! Bộ nhớ được xả sạch, tốc độ phục hồi tối đa.")
                    except Exception as rec_err:
                        print(f"-> Lỗi khi làm mới tab: {rec_err}")
                        navigate_fresh(context, page, TARGET_URL)
                else:
                    # Tải lại trang nhanh để chuẩn bị vòng tiếp theo
                    navigate_fresh(context, page, TARGET_URL)
                
            except Exception as e:
                print(f"[!] LỖI tại vòng {loop_count}: {e}")
                print(f"-> Tải lại {TARGET_URL} để tiếp tục...")
                try:
                    navigate_fresh(context, page, TARGET_URL)
                except Exception:
                    pass
        
        print(f"\n🎉 ĐÃ HOÀN THÀNH MỤC TIÊU {TARGET_GOAL} HỘI THOẠI TRONG {int((time.time() - start_time) / 60)} PHÚT!")

if __name__ == "__main__":
    run()
