# 06. Kiến Trúc Hệ Thống Tự Động Hóa (Thư Mục `cache`)

> **Tài liệu tổng hợp toàn bộ các script, cổng kết nối trình duyệt, luồng xử lý và dữ liệu vận hành trong thư mục `c:\Users\hp\Desktop\cache`.**

---

## 1. Tổng Quan Kiến Trúc Thư Mục `cache`

Thư mục `cache` là trung tâm tự động hóa (Automation Center) phục vụ:
- Tiếp nhận, xử lý và cập nhật thông tin khách hàng viễn thông trên cổng nội bộ FPT SOP.
- Tự động hóa tương tác trình duyệt thông qua Chrome Remote Debugging (CDP / Playwright).
- Tự động hóa giả lập Android (LDPlayer qua ADB / UIAutomator).
- Chăm sóc và gửi tin nhắn Zalo Web tự động.
- Quét, lọc và phân tách danh sách số điện thoại khách hàng tiềm năng.

---

## 2. Bản Đồ Các Công Cụ Chính (Automation Scripts)

| Tên Script | Mục đích & Chức năng | Cổng / Môi trường |
| :--- | :--- | :--- |
| **`pipeline.py`** | Điều phối toàn diện: Chạy `type.py` tạo hội thoại ➔ Chạy `run.py` điền địa chỉ ➔ Hẹn giờ tắt máy an toàn sau 10 phút. | Kết hợp 9222 & 9223 |
| **`type.py`** | Tự động tạo hội thoại mới với khách hàng trên web tương tác. Nhận tham số `--target` (ví dụ: 800 hội thoại). | Chrome cổng `9223` |
| **`run.py`** | Điền thông tin địa chỉ chi tiết cho các cuộc hội thoại trên hệ thống Portal SOP. Hỗ trợ cờ `--reset`, `--target`, `--shutdown`. | Chrome cổng `9222` |
| **`auto_campaign.py`** | Tự động hóa sao chép chiến dịch mới nhất, quản lý tình trạng "đang gửi", gán mã hợp đồng. | Chrome cổng `9222` |
| **`auto_update_status.py`** | Tự động cập nhật trạng thái danh sách hội thoại khách hàng, có điều chỉnh độ trễ xử lý. | Chrome cổng `9222` |
| **`auto_lookup_sop.py`** | Tra cứu tự động thông tin số điện thoại khách hàng trên Portal SOP. | Chrome cổng `9222` |
| **`fpl.py`** | Tự động hóa thao tác trên giả lập Android **LDPlayer** (chuyển đổi tài khoản, xử lý popup, đọc XML hierarchy). | LDPlayer qua ADB |
| **`zalo_sender.py`** | Gửi tin nhắn Zalo Web theo danh bạ, tự động spin content tránh trùng lặp, lọc bỏ khách hàng cũ. | Chrome cổng `9222` |
| **`tach_sdt.py`** | Tiện ích lọc, làm sạch và chuẩn hóa danh sách số điện thoại từ các file dữ liệu thô. | Python CLI |

---

## 3. Các Tệp Dữ Liệu Quan Trọng (Data Files)

- **`mahopdong.txt` / `mahopdong_backup.txt`**: Danh sách mã hợp đồng phục vụ việc tạo chiến dịch tự động.
- **`sdt_da_dung.txt`**: Danh sách các số điện thoại đã sử dụng để tránh quét hoặc gửi trùng lặp.
- **`sodaloc.txt` / `sdtfpt.txt`**: Dữ liệu số điện thoại đã được lọc sạch chuẩn định dạng.
- **`processed_history.json`**: Bộ nhớ theo dõi tiến trình xử lý chi tiết theo từng phiên chạy.
- **`khach_hang.txt`**: Danh sách tên hoặc từ khóa khách hàng hiện hữu để bot Zalo tự động bỏ qua.
- **`danh_sach_ban_be.json`**: Bộ nhớ cache danh bạ bạn bè được trích xuất từ Zalo Web.

---

## 4. Các Quy Chuẩn & Lưu Ý Sống Còn Khi Viết Code Trong `cache`

### 1. Chuẩn Hóa UTF-8 Cho Console Windows
PowerShell Windows mặc định hay bị lỗi font khi in ký tự tiếng Việt có dấu. Mọi script Python mới phải luôn có:
```python
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
```

### 2. Hai Cửa Sổ Chrome Riêng Biệt (Port 9222 & 9223)
- **Cổng 9222**: Cửa sổ Chrome dành cho Portal Quản trị / SOP FPT / Zalo Web.
- **Cổng 9223**: Cửa sổ Chrome dành cho Web khách hàng / Bot tương tác ngoài.
- Tuyệt đối không nhầm lẫn giữa 2 cổng kết nối khi gọi CDP hoặc Playwright connect.

### 3. Cơ Chế Tắt Máy An Toàn (Safe Shutdown)
Khi hoàn thành toàn bộ mục tiêu (ví dụ 800 hội thoại), lệnh tắt máy được gọi là:
```python
os.system("shutdown /s /t 600") # Chờ đúng 10 phút (600 giây)
```
Phải luôn có hướng dẫn hủy lệnh hiển thị rõ ràng trên màn hình:
```powershell
shutdown /a
```

### 4. Cơ Chế Chống Khóa Tài Khoản (Anti-Ban)
- Luôn hỗ trợ cờ `DRY_RUN = True` để kiểm thử logic trước khi click gửi thật.
- Giãn cách an toàn (Human Delay): 25 - 45 giây giữa các lượt gửi.
- Không bóc tách tên riêng bừa bãi; dùng kỹ thuật spin content đa tầng (lời chào + hook + offer + CTA + emoji ngẫu nhiên) để đảm bảo không có 2 tin nhắn nào trùng hash.
