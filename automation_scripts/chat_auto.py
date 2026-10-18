import random
import time
from playwright.sync_api import sync_playwright

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

# Các khoảng trễ để thao tác tự nhiên hơn (giây)
DELAY_FILL = 0.5
DELAY_IN_BETWEEN = 1.0
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

def click_bottom_left_launcher(page):
    """
    Tự động quét các phần tử ở vùng góc dưới cùng bên trái (bottom-left) của trình duyệt.
    Xác định và nhấp vào biểu tượng chat/SOP chat launcher.
    """
    click_script = """
    () => {
        const findLauncher = (doc) => {
            const elements = doc.querySelectorAll('*');
            let candidate = null;
            const vh = window.innerHeight;
            for (const el of elements) {
                try {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    if (rect.width > 20 && rect.height > 20 && 
                        style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0) {
                        
                        if (rect.left >= 0 && rect.left < 180 && rect.bottom > vh - 180) {
                            if (el.tagName !== 'BODY' && el.tagName !== 'HTML' && el.tagName !== 'MAIN' && el.tagName !== 'IFRAME') {
                                if (!candidate || (rect.width * rect.height < candidate.getBoundingClientRect().width * candidate.getBoundingClientRect().height)) {
                                    candidate = el;
                                }
                            }
                        }
                    }
                } catch(e) {}
            }
            return candidate;
        };
        
        const launcher = findLauncher(document);
        if (launcher) {
            launcher.click();
            return true;
        }
        return false;
    }
    """
    try:
        if page.evaluate(click_script):
            return True
    except Exception:
        pass
        
    for frame in page.frames:
        try:
            if frame.evaluate(click_script):
                return True
        except Exception:
            continue
            
    return False

def navigate_fresh(context, page, url):
    """
    Xóa cookies, local storage và session storage của trang chính lẫn iframe chat (nếu có),
    sau đó tải trang để đảm bảo widget chat được reset hoàn toàn mỗi lần chạy.
    """
    print(f"-> Đang làm sạch bộ nhớ & cookies cho trang {url}...")
    try:
        context.clear_cookies()
    except Exception as e:
        print(f"   (Lưu ý: Không thể xoá cookies: {e})")
        
    try:
        page.goto(url)
        page.wait_for_load_state("networkidle")
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        
        # Thử dọn dẹp thêm bộ nhớ trong iframe chat của SOP nếu đang tải
        try:
            element_handle = page.locator('#sop-livechat-wrapper iframe').element_handle(timeout=1000)
            if element_handle:
                frame = element_handle.content_frame()
                if frame:
                    frame.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
                    print("-> Đã xoá bộ nhớ đệm (localStorage) trong iframe chat.")
        except Exception:
            pass
            
        page.goto(url)
        page.wait_for_load_state("networkidle")
    except Exception as load_err:
        print(f"   (Lưu ý: Lỗi trong quá trình reset/load trang: {load_err})")

def close_active_dialogue(dialogue_frame, three_dots):
    """
    Tự động nhấp ba chấm -> Kết thúc hội thoại -> Đóng cuộc trò chuyện.
    Hỗ trợ cả Unicode NFC và NFD, giải quyết độ trễ hiển thị bằng Playwright auto-wait.
    """
    try:
        if three_dots.is_visible(timeout=3000):
            print("-> Nhấp nút 3 chấm để hiển thị menu...")
            three_dots.click()
            time.sleep(1.0)
            
            # Chọn mục Kết thúc hội thoại (NFC/NFD) qua class popover hoặc text
            print("-> Tìm và nhấp 'Kết thúc hội thoại'...")
            end_chat = dialogue_frame.locator("[class*='popover'] p, [class*='popover'] div, p:has-text('Kết thúc'), p:has-text('Kết thúc'), span:has-text('Kết thúc'), span:has-text('Kết thúc')").first
            end_chat.click(timeout=8000)
            time.sleep(1.0)
            
            # Chọn nút Đóng (NFC/NFD), hoặc nút chính trong Modal confirm
            print("-> Tìm và nhấp xác nhận 'Đóng'...")
            close_btn = dialogue_frame.locator("button:has-text('Đóng'), button:has-text('Đóng'), .ant-modal-confirm-btns button:last-child, .ant-btn-primary, button[class*='primary']").first
            close_btn.click(timeout=8000)
            print("-> Đã gửi lệnh click đóng cuộc trò chuyện.")
            time.sleep(2.0)
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
        input("Nhấn ENTER trong Terminal này để BẮT ĐẦU chạy tự động...")
        
        loop_count = 0
        while True:
            loop_count += 1
            print(f"\n===== [VÒNG LẶP THỨ {loop_count}] =====")
            
            # Tạo dữ liệu ngẫu nhiên
            name, phone, address = generate_random_data()
            print(f"Dữ liệu ngẫu nhiên:")
            print(f" - Họ và tên : {name}")
            print(f" - SĐT       : {phone}")
            print(f" - Địa chỉ   : {address}")
            
            try:
                # 1. Kiểm tra trạng thái hiện tại của widget
                dialogue_frame = page.frame_locator('#sop-livechat-wrapper iframe')
                three_dots = dialogue_frame.locator(".anticon-more, header button, div[class*='header'] button").first
                
                # Kiểm tra xem có hội thoại cũ nào đang hoạt động không để đóng trước khi chạy vòng mới
                if three_dots.is_visible(timeout=3000):
                    print("-> Phát hiện hội thoại cũ đang mở. Đóng hội thoại để bắt đầu lượt mới...")
                    close_active_dialogue(dialogue_frame, three_dots)
                    navigate_fresh(context, page, TARGET_URL)
                    continue
                
                 # 2. Cuộn trang và chờ widget hiển thị
                print("-> Đang thực hiện cuộn trang (scroll) để kích hoạt hiển thị widget...")
                try:
                    page.evaluate("window.scrollTo(0, 500)")
                    time.sleep(0.3)
                    page.evaluate("window.scrollTo(0, 1000)")
                    time.sleep(0.3)
                    page.evaluate("window.scrollTo(0, 0)")
                except Exception as scroll_err:
                    print(f"   (Lưu ý: Không thể scroll trang: {scroll_err})")
                
                # Chờ 7 giây và cuộn nhẹ liên tục để kích hoạt lazy loading
                print("-> Chờ 7 giây và cuộn trang liên tục để kích hoạt hiển thị widget...")
                for i in range(7):
                    try:
                        y_pos = 650 if (i % 2 == 0) else 150
                        page.evaluate(f"window.scrollTo(0, {y_pos})")
                    except Exception:
                        pass
                    time.sleep(1.0)
                
                try:
                    page.evaluate("window.scrollTo(0, 0)")
                except Exception:
                    pass
                
                name_input = dialogue_frame.locator("input").first
                
                if not name_input.is_visible(timeout=3000):
                    print("-> Không thấy biểu mẫu đăng ký, đang tìm kiếm launcher...")
                    launcher = None
                    for frame_sel in ['iframe[width="88px"]', 'iframe[height="88px"]']:
                        try:
                            candidate = page.frame_locator(frame_sel).locator(".frame-content, body, div[class*='glow']").first
                            candidate.wait_for(state="visible", timeout=3000)
                            launcher = candidate
                            break
                        except:
                            pass
                    
                    if launcher:
                        print("-> Đã tìm thấy launcher. Đang click...")
                        launcher.click()
                        time.sleep(3.0) 
                    else:
                        print("-> Không tìm thấy launcher bằng frame locator. Thử cuộn lại lần nữa...")
                        try:
                            page.evaluate("window.scrollTo(0, 800)")
                            time.sleep(1.5)
                            page.evaluate("window.scrollTo(0, 0)")
                            time.sleep(1.5)
                        except Exception:
                            pass
                        
                        # Quét lại launcher sau khi cuộn thêm
                        for frame_sel in ['iframe[width="88px"]', 'iframe[height="88px"]']:
                            try:
                                candidate = page.frame_locator(frame_sel).locator(".frame-content, body, div[class*='glow']").first
                                if candidate.is_visible(timeout=2000):
                                    launcher = candidate
                                    break
                            except:
                                pass
                        
                        if launcher:
                            print("-> Đã tìm thấy launcher ở lượt cuộn phụ. Đang click...")
                            launcher.click()
                            time.sleep(3.0)
                        else:
                            print("-> Vẫn không tìm thấy launcher bằng frame locator.")
                else:
                    print("-> Biểu mẫu đăng ký đã hiển thị sẵn.")
 
                # Nhắm vào input đầu tiên để đảm bảo nó xuất hiện
                try:
                    name_input.wait_for(state="visible", timeout=8000)
                except Exception:
                    # Kiểm tra lại xem có tình cờ vào thẳng màn hình hội thoại sau khi click launcher không
                    if three_dots.is_visible(timeout=2000):
                        print("-> Trực tiếp mở vào hội thoại cũ, tiến hành đóng...")
                        close_active_dialogue(dialogue_frame, three_dots)
                        navigate_fresh(context, page, TARGET_URL)
                        continue
                    raise Exception("Không tìm thấy hoặc không thể mở biểu mẫu đăng ký (ô Họ và tên không xuất hiện)")

                # 3. Điền thông tin Họ và tên
                name_input = dialogue_frame.locator("input[placeholder*='tên'], input[placeholder*='Tên'], input[placeholder*='name']").first
                if not name_input.is_visible(timeout=1000):
                    name_input = dialogue_frame.locator("input").nth(0)
                
                print("-> Điền Họ tên...")
                name_input.fill(name)
                time.sleep(DELAY_FILL)
                    
                # 4. Điền Số điện thoại
                phone_input = dialogue_frame.locator("input[placeholder*='thoại'], input[placeholder*='phone']").first
                if not phone_input.is_visible(timeout=1000):
                    phone_input = dialogue_frame.locator("input").nth(1)
                
                print("-> Điền SĐT...")
                phone_input.fill(phone)
                time.sleep(DELAY_FILL)
 
                # 5. Điền Địa chỉ
                address_input = dialogue_frame.locator("input[placeholder*='chỉ'], input[placeholder*='address']").first
                if not address_input.is_visible(timeout=1000):
                    address_input = dialogue_frame.locator("input").nth(2)
                
                print("-> Điền Địa chỉ...")
                address_input.fill(address)
                time.sleep(DELAY_FILL)
 
                # 6. Click nút "Bắt đầu" (Bộ lọc nhiều lớp tối ưu hóa đa website)
                submit_btn = dialogue_frame.locator(
                    "button:has-text('Bắt đầu'), button:has-text('Bắt đầu'), " 
                    "button:has-text('Bắt đầu chat'), button:has-text('Gửi'), "
                    "button:has-text('Đăng ký'), button:has-text('Start'), "
                    "button:has-text('Submit'), [type='submit'], .ant-btn-primary"
                ).first
                
                if not submit_btn.is_visible(timeout=1000):
                    submit_btn = dialogue_frame.get_by_text("Bắt đầu").first
                if not submit_btn.is_visible(timeout=500):
                    submit_btn = dialogue_frame.get_by_text("Bắt đầu").first 
                
                print("-> Click nút Bắt đầu...")
                submit_btn.click(timeout=8000)
                
                # Chờ màn hình hội thoại hiển thị
                print("-> Đang chờ màn hình hội thoại tải...")
                three_dots.wait_for(state="visible", timeout=15000)
                time.sleep(1.0)
                
                # 7. Đóng hội thoại sau khi hoàn thành đăng ký
                close_active_dialogue(dialogue_frame, three_dots)
                
                # 8. Điều hướng trực tiếp lại trang đích để chạy tiếp vòng sau
                navigate_fresh(context, page, TARGET_URL)
                
            except Exception as e:
                print(f"[!] LỖI tại vòng {loop_count}: {e}")
                print(f"Đang điều hướng lại {TARGET_URL} để thử lại vòng sau...")
                try:
                    navigate_fresh(context, page, TARGET_URL)
                except Exception:
                    pass

if __name__ == "__main__":
    run()
