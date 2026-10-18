import sys
import os
import time
import re
import uiautomator2 as u2
from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "mahopdong.txt")
BACKUP_PATH = os.path.join(BASE_DIR, "mahopdong_backup.txt")

# --- CẤU HÌNH TỐC ĐỘ VÀ NGHỈ GIẢI LAO ---
PACE_SECONDS = 2.0      # Tốc độ chuẩn cho mỗi mã (5 giây)
BATCH_SIZE = 100         # Cứ sau bao nhiêu mã thì tạm nghỉ (30 mã)
BREAK_DURATION = 3     # Thời gian nghỉ giải lao (60 giây). Đặt = 0 nếu muốn chạy liên tục không nghỉ.

def connect_device():
    print("🔌 Đang kết nối tới giả lập LDPlayer...")
    try:
        d = u2.connect("127.0.0.1:5555")
    except Exception:
        d = u2.connect()
    print(f"✅ Đã kết nối thiết bị: {d.serial}")
    return d

def lookup_contract(d, contract_code):
    """
    Tra cứu 1 mã hợp đồng trên app SOP.
    Trả về: (tên_khách_hàng, số_điện_thoại) hoặc (None, None) nếu không tìm thấy.
    """
    edit = d(className="android.widget.EditText")
    if not edit.exists(timeout=5):
        print("⚠️ Không tìm thấy ô nhập liệu! Đang thử click lại...")
        # Thử tìm ô EditText bất kỳ
        return None, None
    
    # 1. Nhập mã hợp đồng
    edit.click()
    edit.clear_text()
    edit.set_text(contract_code)
    time.sleep(0.3)
    
    # 2. Bấm phím Enter để tìm kiếm
    d.press("enter")
    
    # 3. Lắng nghe và đọc kết quả (chờ tối đa 4 giây)
    phone = None
    name = None
    start_time = time.time()
    
    while time.time() - start_time < 4.0:
        try:
            xml = d.dump_hierarchy()
            tree = etree.fromstring(xml.encode('utf-8'))
            
            # Lấy tất cả text của TextView trên màn hình
            all_texts = tree.xpath('//node[@class="android.widget.TextView"]/@text')
            
            for i, t in enumerate(all_texts):
                # Format hiển thị thường là: " | 0339770708, 079185008264 | ..." hoặc "0339770708"
                m = re.search(r'\|\s*(0\d{9})', t)
                if not m:
                    m = re.search(r'\b(0\d{9})\b', t)
                
                if m and contract_code in t:
                    phone = m.group(1)
                    # Node ngay trước đó thường là Họ Tên khách hàng (in hoa)
                    if i > 0:
                        candidate_name = all_texts[i-1].strip()
                        if candidate_name not in ["Khách hàng", "Tạo SR", "Số hợp đồng", "Tìm kiếm theo", "Nội dung yêu cầu"]:
                            name = candidate_name
                    break
                elif m:
                    phone = m.group(1)
            
            if phone:
                break
        except Exception:
            pass
        time.sleep(0.4)
        
    return name, phone

def main():
    if not os.path.exists(FILE_PATH):
        print(f"❌ Không tìm thấy file {FILE_PATH}")
        return

    # Kết nối LDPlayer
    d = connect_device()

    # Đọc các dòng từ file
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Sao lưu 1 bản trước khi chạy
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"💾 Đã tạo file sao lưu tại: {BACKUP_PATH}")

    total = len(lines)
    print(f"📋 Tổng số dòng cần xử lý: {total}\n" + "="*50)

    updated_count = 0
    
    for idx, line in enumerate(lines):
        raw_line = line.strip()
        if not raw_line:
            continue
        
        # Tách mã hợp đồng từ đầu dòng (hỗ trợ mọi tỉnh thành: SGA, BDA, CMA, LAA, DTA...)
        match = re.match(r'^([A-Za-z0-9]+)', raw_line)
        if not match:
            continue
        
        code = match.group(1).upper()
        
        # Nếu dòng đã có số điện thoại thật (ví dụ: -> 0348641317), bỏ qua không tra lại
        has_real_phone = re.search(r'->\s*(0\d{9})', raw_line)
        if has_real_phone:
            print(f"[{idx+1}/{total}] ⏩ {code} đã có SĐT: {has_real_phone.group(1)} (Bỏ qua)")
            continue

        start_code_time = time.time()
        print(f"[{idx+1}/{total}] 🔍 Đang tra cứu mã: {code} ...", end=" ", flush=True)
        name, phone = lookup_contract(d, code)
        
        if phone:
            print(f"✅ Tìm thấy: {phone} ({name or 'N/A'})")
            lines[idx] = f"{code} -> {phone}\n"
            updated_count += 1
        else:
            print("❌ Không tìm thấy kết quả")
            lines[idx] = f"{code} -> Không tìm thấy\n"

        # Ghi đè cập nhật ngay lập tức vào file (không sợ bị mất tiến độ nếu dừng giữa chừng)
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        # Đảm bảo tốc độ đúng chuẩn PACE_SECONDS (5 giây / 1 mã hợp đồng)
        elapsed = time.time() - start_code_time
        sleep_time = max(0.5, PACE_SECONDS - elapsed)
        time.sleep(sleep_time)

        # Cơ chế nghỉ giải lao sau mỗi BATCH_SIZE mã (để an toàn cho tài khoản)
        if BREAK_DURATION > 0 and (idx + 1) < total and (updated_count % BATCH_SIZE == 0) and updated_count > 0:
            print(f"\n☕ [Nghỉ giải lao] Đã tra cứu {updated_count} mã. Tạm nghỉ {BREAK_DURATION}s để an toàn cho tài khoản...")
            time.sleep(BREAK_DURATION)
            print("🚀 Tiếp tục tra cứu đợt tiếp theo...\n")

    print("="*50)
    print(f"🎉 Hoàn thành! Đã cập nhật thành công {updated_count}/{total} mã hợp đồng vào file: mahopdong.txt")

if __name__ == "__main__":
    main()
